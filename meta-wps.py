#from typing import List
from collections import OrderedDict as OD

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

#from pydantic import BaseModel, Field
#import requests
#import json
from cerberus import Validator


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


schema = OD({'paramA': {'allowed': ['a1', 'a2', 'a3']},
          'paramB': {'allowed': ['b1', 'b2']}}) 

v = Validator(schema) 


def transform_schema(schema=schema):
    d = OD()
    for key, value in schema.items():
        d[key] = value['allowed']

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
    return validate_inputs(inputs)


def validate_inputs(inputs):
    result = {"result": v.validate(inputs), 
              "errors": v.errors,
              "schema": v.schema}
    return result

