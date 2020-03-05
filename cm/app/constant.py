# -*- coding: utf-8 -*-

CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'


#CELERY_BROKER_URL = 'amqp://admin:mypass@localhost:5672/'
CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'CM - Wind potential'
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE' # Do no change this value
RPC_Q = 'rpc_queue_CM_compute' # Do no change this value
CM_ID = 13
PORT_LOCAL = int('500' + str(CM_ID))
PORT_DOCKER = 80
#TODO:**********************************************************
CELERY_BROKER_URL = CELERY_BROKER_URL_DOCKER
PORT = PORT_DOCKER
#TODO:**********************************************************
TRANFER_PROTOCOLE ='http://'


INPUTS_CALCULATION_MODULE = [
    {'input_name': 'Wind Hub Setup costs (all inclusive) price [Euro/kWp]',
     'input_type': 'input',
     'input_parameter_name': 'setup_costs',
     'input_value': 2000,
     'input_priority': 0,
     'input_unit': 'Euro/kWp',
     'input_min': 0.0,
     'input_max': 10000,
     'cm_id': CM_ID
     },
    {'input_name': 'Distance among wind hubs [m]',
     'input_type': 'input',
     'input_priority': 0,
     'input_parameter_name': 'res_hub',
     'input_value': 1000,
     'input_unit': ' ',
     'input_min': 0,
     'input_max': 5000,
     'cm_id': CM_ID
     },
    {'input_name': 'Peak power [kW]',
     'input_type': 'input',
     'input_parameter_name': 'peak_power',
     'input_value': 800,
     'input_priority': 1,
     'input_unit': 'kW',
     'input_min': 0,
     'input_max': 5000,
     'cm_id': CM_ID
     },
    {'input_name': 'Height [m]',
     'input_type': 'input',
     'input_parameter_name': 'height',
     'input_value': 80,
     'input_priority': 1,
     'input_unit': 'm',
     'input_min': 0,
     'input_max': 250,
     'cm_id': CM_ID
     },
    {'input_name': 'Maintenance and operation costs [% of the setup cost]',
     'input_type': 'input',
     'input_parameter_name': 'maintenance_percentage',
     'input_value': 2,
     'input_priority': 0,
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
    "category": "Supply",
    "cm_name": CM_NAME,
    "layers_needed": [
       "output_wind_speed"   # kWh/m²/year
    ],
    "type_layer_needed": [
       {"type": "output_wind_speed",
        "description": "Availale areas that are suitable to install a wind turbine"}
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
