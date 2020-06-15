import logging
import json
import os
import sys
from osgeo import gdal
import numpy as np
import pandas as pd
import warnings
import reslib.wind as wind
import reslib.plant as plant
import resutils.raster as rr
import resutils.output as ro
import resutils.unit as ru

# TODO:  change with try and better define the path
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(path, "app", "api_v1")
if path not in sys.path:
    sys.path.append(path)
from ..helper import generate_output_file_tif
from ..constant import CM_NAME


# set a logger
LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
logging.basicConfig(format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")

# TODO the token now is null, only 5 requests in one day,
# please set the environemnt variable with a TOKEN
# for renewable ninja
if "RES_NINJA_TOKENS" not in os.environ:
    LOGGER.warning("RES_NINJA_TOKENS environmental variable not set!")


def run_source(kind, pl, data_in, most_suitable, n_plant_raster, discount_rate):
    """
    Run the simulation and get indicators for the single source
    """
    print(
        "Financial parameters: "
        f'setup_costs={data_in["setup_costs"]} '
        f'yearly_cost={data_in["tot_cost_year"]} '
        f'plant_life={data_in["financing_years"]}'
    )
    pl.financial = plant.Financial(
        investement_cost=int(data_in["setup_costs"] * pl.peak_power),
        yearly_cost=data_in["tot_cost_year"],
        plant_life=data_in["financing_years"],
    )

    result = dict()
    if most_suitable.max() > 0:
        result["indicator"] = ro.get_indicators(
            kind, pl, most_suitable, n_plant_raster, discount_rate
        )
        print(f'indicator={json.dumps(result["indicator"])}')

        # default profile
        tot_profile = pl.prof["electricity"].values * pl.n_plants
        default_profile, unit, con = ru.best_unit(
            tot_profile, "kW", no_data=0, fstat=np.median, powershift=0
        )
        print(
            "Horuly profile "
            f"tot_profile={tot_profile} "
            f"default_profile={default_profile} "
            f"unit={unit} "
            f"con={con}"
        )

        graph = ro.line(
            x=ro.reducelabels(pl.prof.index.strftime("%d-%b %H:%M")),
            y_labels=["{} {} profile [{}]".format(kind, pl.resolution[1], unit)],
            y_values=[default_profile],
            unit=unit,
            xLabel=pl.resolution[0],
            yLabel="{} {} profile [{}]".format(kind, pl.resolution[1], unit),
        )

        # monthly profile of energy production

        df_month = pl.prof.groupby(pd.Grouper(freq="M")).sum()
        df_month["output"] = df_month["electricity"] * pl.n_plants
        monthly_profile, unit, con = ru.best_unit(
            df_month["output"].values, "kWh", no_data=0, fstat=np.median, powershift=0
        )
        print(f"monthly_profile={monthly_profile} " f"unit={unit} " f"con={con}")

        graph_month = ro.line(
            x=df_month.index.strftime("%b"),
            y_labels=[
                """"{} monthly energy
                                        production [{}]""".format(
                    kind, unit
                )
            ],
            y_values=[monthly_profile],
            unit=unit,
            xLabel="Months",
            yLabel="{} monthly profile [{}]".format(kind, unit),
        )

        graphics = [graph, graph_month]

        result["graphics"] = graphics
        print("Computed correctly!")
    return result


def calculation(output_directory, inputs_raster_selection, inputs_parameter_selection):
    """
    Main function
    """
    # list of error messages
    # TODO: to be fixed according to CREM format
    messages = []

    # retrieve the inputs all input defined in the signature
    w_in = {
        "res_hub": float(inputs_parameter_selection["res_hub"]),
        "height": float(inputs_parameter_selection["height"]),
        "setup_costs": int(inputs_parameter_selection["setup_costs"]),
        "tot_cost_year": (
            float(inputs_parameter_selection["maintenance_percentage"])
            / 100
            * int(inputs_parameter_selection["setup_costs"])
        ),
        "financing_years": int(inputs_parameter_selection["financing_years"]),
        "peak_power": float(inputs_parameter_selection["peak_power"]),
    }

    discount_rate = float(inputs_parameter_selection["discount_rate"])
    print(f"w_in={w_in}")

    # retrieve the inputs layes
    # ds = gdal.Open(inputs_raster_selection["output_wind_speed"])
    print(f"inputs_raster_selection={inputs_raster_selection}")
    print(f"inputs_raster_selection.keys()={inputs_raster_selection.keys()}")
    ds = gdal.Warp(
        "warp_test.tif",
        inputs_raster_selection["output_wind_speed"],
        outputType=gdal.GDT_Float32,
        xRes=w_in["res_hub"],
        yRes=w_in["res_hub"],
        dstNodata=0,
    )
    plant_raster = ds.ReadAsArray()
    potential = ds.ReadAsArray()
    potential = np.nan_to_num(potential)
    plant_raster = np.nan_to_num(plant_raster)
    plant_raster[plant_raster > 0] = 1
    # TODO: set peak power and swept area from a list of turbines
    wind_plant = wind.WindPlant(
        id_plant="Wind",
        peak_power=w_in["peak_power"],
        height=w_in["height"],
        model="Enercon E48 800",
    )
    wind_plant.area = w_in["res_hub"] * w_in["res_hub"]
    wind_plant.n_plants = plant_raster.sum()
    print(f"wind_plant.n_plants: {wind_plant.n_plants}")
    if wind_plant.n_plants > 0:
        wind_plant.raw = False
        wind_plant.mean = None
        wind_plant.lat, wind_plant.lon = rr.get_lat_long(ds, potential)
        wind_plant.prof = wind_plant.profile()
        wind_plant.energy_production = wind_plant.prof.sum()["electricity"]
        wind_plant.resolution = ["Hours", "hourly"]
        """
        run_source(kind, pl, data_in,
               most_suitable,
               n_plant_raster,
               discount_rate,
               )
        """
        try:
            res = run_source(
                "Wind", wind_plant, w_in, potential, plant_raster, discount_rate
            )
        except Exception as exc:
            print(f"FAILED to execute run_source function due to {exc}")
    else:
        res = dict(
            indicator=dict(
                unit="",
                name="Not suitable pixels have been identified in the area selected, please select another area",
                value=0,
            )
        )
        print("Not suitable pixels have been identified.")
    res["name"] = CM_NAME
    print("Wind computation completed!")
    return res
