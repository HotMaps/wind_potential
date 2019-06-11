# -*- coding: utf-8 -*-

CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'


#CELERY_BROKER_URL = 'amqp://admin:mypass@localhost:5672/'
CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'Solar PV potential'
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE' # Do no change this value
RPC_Q = 'rpc_queue_CM_compute' # Do no change this value
CM_ID = 4
PORT_LOCAL = int('500' + str(CM_ID))
PORT_DOCKER = 80
#TODO:**********************************************************
CELERY_BROKER_URL = CELERY_BROKER_URL_DOCKER
PORT = PORT_DOCKER
#TODO:**********************************************************
TRANFER_PROTOCOLE ='http://'


INPUTS_CALCULATION_MODULE = [
    {'input_name': 'Suitable area for wind energy production [% of available area]',
     'input_type': 'input',
     'input_parameter_name': 'reduction_factor',
     'input_value': 100,
     'input_priority': 0,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 100,
     'cm_id': CM_ID
     },
    {'input_name': 'Wind energy target of the region if available',
     'input_type': 'input',
     'input_parameter_name': 'target',
     'input_value': 0,
     'input_priority': 0,
     'input_unit': 'GWh',
     'input_min': 0,
     'input_max': 10000000000000,
     'cm_id': CM_ID
     },
    {'input_name': 'Wind Hub Setup costs (all inclusive) price [currency/kWp]',
     'input_type': 'input',
     'input_parameter_name': 'setup_costs',
     'input_value': 2000,
     'input_priority': 1,
     'input_unit': 'currency/kWp',
     'input_min': 0.0,
     'input_max': 10000,
     'cm_id': CM_ID
     },
    {'input_name': 'Distance among wind hubs [m]',
     'input_type': 'input',
     'input_priority': 0,
     'input_parameter_name': 'res_hub',
     'input_value': 500,
     'input_unit': ' ',
     'input_min': 0,
     'input_max': 5000,
     'cm_id': CM_ID
     },
    {'input_name': 'Average height per plant [kW_p]',
     'input_type': 'input',
     'input_parameter_name': 'height',
     'input_value': 50,
     'input_priority': 1,
     'input_unit': 'kW',
     'input_min': 0,
     'input_max': 150,
     'cm_id': CM_ID
     },
    {'input_name': 'Efficiency of the system',
     'input_type': 'input',
     'input_parameter_name': 'efficiency',
     'input_value': 0.75,
     'input_priority': 1,
     'input_unit': ' ',
     'input_min': 0,
     'input_max': 1,
     'cm_id': CM_ID
     },
    {'input_name': 'Swept area [m]',
     'input_type': 'input',
     'input_parameter_name': 'swept_area',
     'input_value': 1810,
     'input_priority': 5000,
     'input_unit': ' ',
     'input_min': 0,
     'input_max': 1,
     'cm_id': CM_ID
     },
    {'input_name': 'Peak power [kW]',
     'input_type': 'input',
     'input_parameter_name': 'peak_power',
     'input_value': 800,
     'input_priority': 5000,
     'input_unit': ' ',
     'input_min': 0,
     'input_max': 1,
     'cm_id': CM_ID
     },
    {'input_name': 'Maintenance and operation costs [% of the setup cost]',
     'input_type': 'input',
     'input_parameter_name': 'maintenance_percentage',
     'input_value': 2,
     'input_priority': 1,
     'input_unit': '%',
     'input_min': 0.0,
     'input_max': 100,
     'cm_id': CM_ID
     },
    {'input_name': 'Financing years [year]',
     'input_type': 'input',
     'input_parameter_name': 'financing_years',
     'input_value': 20,
     'input_priority': 1,
     'input_unit': 'year',
     'input_min': 0.0,
     'input_max': 40,
     'cm_id': CM_ID
     },
    {'input_name': 'Discount rate [%]',
     'input_type': 'input',
     'input_parameter_name': 'discount_rate',
     'input_value': 4.0,
     'input_priority': 1,
     'input_unit': '%',
     'input_min': 0,
     'input_max': 100,
     'cm_id': CM_ID
     }
]


SIGNATURE = {
    "category": "Wind energy potential",
    "cm_name": CM_NAME,
    "layers_needed": [
        "climate_wind_speed", "wind_50m"   # kWh/m²/year
    ],
    "type_layer_needed": [
        "speed", "area"
    ],
    "cm_url": "Do not add something",
    "cm_description": "This computation aims to compute the wind"
                      "energy potential and the financial feasibility of"
                      "a selected area."
                      "The code is on Hotmaps Github group and has"
                      " been developed by EURAC",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
