#from typing import List
import json
from collections import OrderedDict as OD

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

#from pydantic import BaseModel, Field
#import requests
#import json
#from cerberus import Validator


from meta_wps_validator import schema, MetaWPSValidator as Validator


app = FastAPI()
ports = [3001, 8998]
hosts = ["localhost", "192.168.50.70"]

origins = [f"http://{host}:{port}" for host in hosts for port in ports]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#schema = OD({'paramA': {'allowed': ['a1', 'a2', 'a3']}, 'paramB': {'allowed': ['b1', 'b2']}}) 
#schema = {'a': {'allowed': [1, 2]},
#          'b': {'dependencies': ['a'],
#                'check_with': 'values_dependent',
#                'allowed_values_dependencies': {'a': {(1,): ['b_a1']},
#                                                'a': {(2,): ['b_a2']}} } }

v = Validator(schema) 


def transform_schema(selections=None, schema=schema):
    if not selections: selections = {}

    d = OD()
    for key, value in schema.items():
        if 'allowed' in value:
            selected = selections.get(key, None)

            if selected:
                d[key] = selected
            else:
                d[key] = value['allowed']
        else:
            break

    print("Transformed to:", d)
    return d
 

@app.get('/')
def index():
    return "Use /meta-wps endpoint with posted inputs JSON."


@app.get('/meta-wps')
def meta_wps_get():
    return transform_schema(schema)


@app.post('/meta-wps')
async def meta_wps(request: Request):
    inputs = await request.json()
    print("[POST] received", inputs)
    return validate_inputs(inputs)


def validate_inputs(inputs):
    result = {"result": v.validate(inputs), 
              "errors": v.errors,
              "options": transform_schema(inputs)}
    print("RETURNING:", result)
    return json.dumps(result, indent = 4) 

