import unittest
from werkzeug.exceptions import NotFound
from app import create_app
import os.path
from shutil import copyfile
from .test_client import TestClient
UPLOAD_DIRECTORY = '/var/hotmaps/cm_files_uploaded'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)


<<<<<<< HEAD
def load_input():
    """
    Load the input values in the file constant.py

    :return a dictionary with the imput values
    """
    inputs_parameter = {}
    for inp in INPUTS_CALCULATION_MODULE:
        inputs_parameter[inp['input_parameter_name']] = inp['input_value']
    return inputs_parameter


def load_raster(area, speed):
    """
    Load the raster file for testing
    :param area: raster file with available area
    :param speed: raster file with wind speed

    :return a dictionary with the raster file paths
    """
    raster_file_path = os.path.join('tests/data', speed)
    save_path_speed = os.path.join(UPLOAD_DIRECTORY, speed)
    copyfile(raster_file_path, save_path_speed)
    inputs_raster_selection = {}
    raster_file_path = os.path.join('tests/data', area)
    save_path_area = os.path.join(UPLOAD_DIRECTORY, area)
    copyfile(raster_file_path, save_path_area)
    inputs_raster_selection = {}
    inputs_raster_selection["climate_wind_speed"] = save_path_speed
    inputs_raster_selection["wind_50m"] = save_path_area
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
        graph_file_path = os.path.join('tests/data', 'plot{}.png'.format(n))
        # simulate copy from HTAPI to CM
        x = [i for i in range(0, len(g['data']['labels']))]
        # TODO loop in datasets to plot more lines
        y = [int(i) for i in g['data']['datasets'][0]['data']]
        plt.plot(x, y, label=g['data']['datasets'][0]['label'])
        plt.xlabel(g['xLabel'])
        plt.ylabel(g['yLabel'])
        plt.xticks(rotation=90)
        ax = plt.gca()
        axes = plt.axes()
        axes.set_xticks(x)
        ax.set_xticklabels(g['data']['labels'])
#        locs, labels = plt.xticks()
#        plt.xticks(locs, g['data']['labels'])
        plt.savefig(graph_file_path)
        plt.clf()


=======
>>>>>>> parent of 1fb9394... first test
class TestAPI(unittest.TestCase):


    def setUp(self):
        self.app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app,)

    def tearDown(self):

        self.ctx.pop()


    def test_compute(self):
        raster_file_path = 'tests/data/raster_for_test.tif'
        # simulate copy from HTAPI to CM
        save_path = UPLOAD_DIRECTORY+"/raster_for_test.tif"
        copyfile(raster_file_path, save_path)

        inputs_raster_selection = {}
        inputs_parameter_selection = {}
        inputs_vector_selection = {}
        inputs_raster_selection["heat_tot_curr_density"]  = save_path
        inputs_vector_selection["heating_technologies_eu28"]  = {}
        inputs_parameter_selection["reduction_factor"] = 2

        # register the calculation module a
        payload = {"inputs_raster_selection": inputs_raster_selection,
                   "inputs_parameter_selection": inputs_parameter_selection,
                   "inputs_vector_selection": inputs_vector_selection}


        rv, json = self.client.post('computation-module/compute/', data=payload)

        self.assertTrue(rv.status_code == 200)


