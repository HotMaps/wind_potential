import tempfile
import unittest
from app import create_app
import os.path
from shutil import copyfile
from .test_client import TestClient
from app.constant import INPUTS_CALCULATION_MODULE
import matplotlib.pyplot as plt
from pint import UnitRegistry
import resutils.output as ro

UPLOAD_DIRECTORY = os.path.join(tempfile.gettempdir(), "hotmaps", "cm_files_uploaded")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)

ureg = UnitRegistry()


def load_input():
    """
    Load the input values in the file constant.py

    :return a dictionary with the imput values
    """
    inputs_parameter = {}
    for inp in INPUTS_CALCULATION_MODULE:
        inputs_parameter[inp["input_parameter_name"]] = inp["input_value"]
    return inputs_parameter


def load_raster(area):
    """
    Load the raster file for testing
    :param area: raster file with available area
    :param speed: raster file with wind speed

    :return a dictionary with the raster file paths
    """
    raster_file_path = os.path.join("tests/data", area)
    save_path_area = os.path.join(UPLOAD_DIRECTORY, area)
    copyfile(raster_file_path, save_path_area)
    inputs_raster_selection = {}
    inputs_raster_selection["output_wind_speed"] = save_path_area
    return inputs_raster_selection


def modify_input(inputs_parameter, **kwargs):
    """
    Modify the dictionary of input parameter

    :return a dictionary with input file modified
    """
    for key, value in kwargs.items():
        inputs_parameter[key] = value
    return inputs_parameter


def test_graph(graph):
    """
    Print a graph with matplot lib by reading the dictionary with graph info
    """
    for n, g in enumerate(graph):
        graph_file_path = os.path.join("tests/data", "plot{}.png".format(n))
        # simulate copy from HTAPI to CM
        x = [i for i in range(0, len(g["data"]["labels"]))]
        # TODO loop in datasets to plot more lines
        y = [float(i) for i in g["data"]["datasets"][0]["data"]]
        fig, ax = plt.subplots()
        ax.plot(x, y, label=g["data"]["datasets"][0]["label"])
        ax.set_xlabel(g["xLabel"])
        ax.set_ylabel(g["yLabel"])
        ax.set_xticks(x)
        ax.set_xticklabels(g["data"]["labels"], rotation=90)
        ax.grid(True)
        fig.tight_layout()
        fig.savefig(graph_file_path)
        plt.clf()


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(os.environ.get("FLASK_CONFIG", "development"))
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app)

    def tearDown(self):

        self.ctx.pop()

    def test_compute(self):
        """
        Test of the default values from app.constat by
        1) asserting the production per platn between 5 and 15 kWh/day
        2) asserting the value of lcoe between 0.02 and 0.2 euro/kWh
        """
        inputs_raster_selection = load_raster("area_for_test.tif")
        inputs_parameter_selection = load_input()
        # register the calculation module a
        payload = {
            "inputs_raster_selection": inputs_raster_selection,
            "inputs_vector_selection": [],
            "inputs_parameter_selection": inputs_parameter_selection,
        }

        rv, json = self.client.post("computation-module/compute/", data=payload)
        # 0) print graphs
        test_graph(json["result"]["graphics"])
        # 1) assert that the production is beetween a reasonable range of kWh/day per plant
        e_plant = ro.production_per_plant(json, "Wind")
        e_plant.ito(ureg.kilowatt_hour / ureg.year)
        self.assertGreaterEqual(e_plant.magnitude, 50000)
        self.assertLessEqual(e_plant.magnitude, 6000000)
        # 2) assert that the value of lcoe is between 0.02 and 0.2 euro/kWh
        lcoe, unit = ro.search(
            json["result"]["indicator"], "Levelized Cost of Wind Energy"
        )
        self.assertGreaterEqual(lcoe, 0.02)
        self.assertLessEqual(lcoe, 0.2)
        self.assertTrue(rv.status_code == 200)


#
#    def test_raster(self):
#        """
#        Test the output raster
#        1) the consistent between input file and output file in the case
#        of using the total surface of the buildings
#        """
#        inputs_raster_selection = load_raster("raster_for_test.tif",
#                                              "area_for_test.tif")
#        inputs_parameter_selection = load_input()
#        inputs_parameter_selection = modify_input(inputs_parameter_selection,
#                                                  reduction_factor=100)
#        # register the calculation module a
#        payload = {"inputs_raster_selection": inputs_raster_selection,
#                   "inputs_parameter_selection": inputs_parameter_selection}
#
#        rv, json = self.client.post('computation-module/compute/',
#                                    data=payload)
#
#        # 1) the consistent between input file and output file in the case
#        # of using the total surface of the buildings
#        path_output = json['result']['raster_layers'][0]['path']
#        ds = gdal.Open(path_output)
#        raster_out = np.array(ds.GetRasterBand(1).ReadAsArray())
#        ds = gdal.Open(inputs_raster_selection["solar_optimal_total"])
#        raster_in = np.array(ds.GetRasterBand(1).ReadAsArray())
#        error = diff_raster(raster_in, raster_out)
#        self.assertLessEqual(error, 0.01)
#
#    def test_noresults(self):
#        """
#        Test the message when no output file are produced
#        """
#        inputs_raster_selection = load_raster("raster_for_test.tif",
#                                              "area_for_test.tif")
#        inputs_parameter_selection = load_input()
#        inputs_parameter_selection = modify_input(inputs_parameter_selection,
#                                                  roof_use_factor=0.1)
#        # register the calculation module a
#        payload = {"inputs_raster_selection": inputs_raster_selection,
#                   "inputs_parameter_selection": inputs_parameter_selection}
#
#        rv, json = self.client.post('computation-module/compute/',
#                                    data=payload)
#        self.assertTrue(rv.status_code == 200)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
