import os
import sys
from osgeo import gdal
import numpy as np
import pandas as pd
import warnings
from collections import defaultdict

# TODO:  change with try and better define the path
path = os.path.dirname(os.path.dirname
                       (os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, 'app', 'api_v1')
if path not in sys.path:
        sys.path.append(path)
from my_calculation_module_directory.energy_production import get_plants, get_profile, get_raster, get_indicators
from my_calculation_module_directory.visualization import line, reducelabels
from ..helper import generate_output_file_tif
from my_calculation_module_directory.utils import best_unit
import my_calculation_module_directory.plants as plant


set_turbine = [{'name': 'Enercon E48 800',
                'height': 50,
                'area': 1810}, ]


def get_integral_error(pl, interval):
    """
    Compute the integrale of the production profile and compute
    the error with respect to the total energy production
    obtained by the raster file
    :parameter pl: plant
    :parameter interval: step over computing the integral

    :returns: the relative error
    """
    error = abs((pl.energy_production * pl.n_plants -
                 pl.profile.sum() * interval) /
                (pl.energy_production * pl.n_plants)) * 100
    if error[0] > 5:
        message = """Difference between raster value sum and {}
                      total energy greater than {}%""".format(pl.id,
                                                              int(error))
        warnings.warn(message)
        return message


def run_source(kind, pl, data_in,
               most_suitable,
               n_plant_raster,
               irradiation_values,
               building_footprint,
               reduction_factor,
               output_suitable,
               discount_rate,
               ds):
    """
    Run the simulation and get indicators for the single source
    """
    pl.financial = plant.Financial(investement_cost=int(data_in['setup_costs']
                                                        * pl.peak_power),
                                   yearly_cost=data_in['tot_cost_year'],
                                   plant_life=data_in['financing_years'])

    result = dict()
    if most_suitable.max() > 0:
        result['raster_layers'] = get_raster(most_suitable, output_suitable,
                                             ds)
        result['indicator'] = get_indicators(kind, pl, most_suitable,
                                             n_plant_raster, discount_rate)

        # default profile

        default_profile, unit, con = best_unit(pl.profile['output'].values,
                                               'kW', no_data=0,
                                               fstat=np.median,
                                               powershift=0)

        graph = line(x=reducelabels(pl.profile.index.strftime('%d-%b %H:%M')),
                     y_labels=['{} {} profile [{}]'.format(kind,
                                                           pl.resolution[1],
                                                           unit)],
                     y_values=[default_profile], unit=unit,
                     xLabel=pl.resolution[0],
                     yLabel='{} {} profile [{}]'.format(kind,
                                                        pl.resolution[1],
                                                        unit))

        # monthly profile of energy production

        df_month = pl.profile.groupby(pd.Grouper(freq='M')).sum()
        monthly_profile, unit, con = best_unit(df_month['output'].values,
                                               'kWh', no_data=0,
                                               fstat=np.median,
                                               powershift=0)
        graph_month = line(x=df_month.index.strftime('%b'),
                           y_labels=[""""{} monthly energy
                                      production [{}]""".format(kind, unit)],
                           y_values=[monthly_profile], unit=unit,
                           xLabel="Months",
                           yLabel='{} monthly profile [{}]'.format(kind, unit))

        graphics = [graph, graph_month]

        result['graphics'] = graphics
    return result


def calculation(output_directory, inputs_raster_selection,
                inputs_parameter_selection):
    """
    Main function
    """
    # list of error messages
    # TODO: to be fixed according to CREM format
    messages = []
    # generate the output raster file
    output_suitable = generate_output_file_tif(output_directory)

    # retrieve the inputs layes
    ds = gdal.Open(inputs_raster_selection["climate_wind_speed"])
    speed = ds.ReadAsArray()
    speed = np.nan_to_num(speed)

    # retrieve the inputs layes
    ds = gdal.Open(inputs_raster_selection["wind_50m"])
    available_area = np.nan_to_num(ds.ReadAsArray())

    # retrieve the inputs all input defined in the signature
    w_in = {'res_hub':
            float(inputs_parameter_selection["res_hub"]),
            'target': float(inputs_parameter_selection["target"]),
            'setup_costs': int(inputs_parameter_selection['setup_costs']),
            'tot_cost_year':
            (float(inputs_parameter_selection['maintenance_percentage']) /
             100 * int(inputs_parameter_selection['setup_costs'])),
            'financing_years': int(inputs_parameter_selection['financing_years']),
            'efficiency': float(inputs_parameter_selection['efficiency']),
            'height': float(inputs_parameter_selection['height']),
            }

    reduction_factor = float(inputs_parameter_selection["reduction_factor"])
    discount_rate = float(inputs_parameter_selection['discount_rate'])

    # TODO: set peak power and swept area from a list of turbine
    # define a pv plant with input features
    wind_plant = plant.Wind_plant('Wind',
                                  peak_power=800,
                                  efficiency=w_in['efficiency']
                                  )
    wind_plant.swept_area = 1810
    wind_plant.area = w_in["res_hub"]*w_in["res_hub"]
    # add information to get the time profile
    ds_geo = ds.GetGeoTransform()
    wind_pixel_area = ds_geo[1] * (-ds_geo[5])
    plant_px = wind_pixel_area/(w_in['res_hub']**2)

    plant_raster, most_suitable, wind_plant = get_plants(wind_plant,
                                                         w_in['target'],
                                                         speed,
                                                         available_area,
                                                         reduction_factor,
                                                         plant_px)
    wind_plant.n_plants = plant_raster.sum()
    if wind_plant.n_plants > 0:
        wind_plant.raw = False
        wind_plant.mean = None
        wind_plant.profile = get_profile(speed, ds,
                                         most_suitable, plant_raster,
                                         wind_plant)
        messages.append(get_integral_error(wind_plant, 1))
        wind_plant.resolution = ['Hours', 'hourly']
        res = run_source('wind', wind_plant, w_in, most_suitable,
                         plant_raster,
                         speed, available_area,
                         reduction_factor, output_suitable, discount_rate,
                         ds)
    else:
        # TODO: How to manage message
        res = dict()
        warnings.warn("Not suitable pixels have been identified.")

    return res
