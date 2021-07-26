from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI()

MOLES_API = "http://api.catalogue.ceda.ac.uk/api/v2"
LIMIT = 10

ob_map = {
    "dataset": ("observation", "uuid,title,result_field", "&publicationState__in=citable,published"),
    "collection": ("observationcollection", "uuid,title", ""),
    "project": ("project", "uuid,title", "")
}
class Dataset(BaseModel):
    uuid: str
    title: str
    datapath: str

@app.get('/ceda/catalogue/')
def index():
    return "Here is the MOLES search api..."

def search_ceda_cat(ob_type, qs):
    ob_name, fields, extras = ob_map[ob_type]
    url = f"{MOLES_API}/{ob_name}s/?fields={fields}&limit={LIMIT}{extras}"
    if qs:
        url = f"{url}&{qs}"

    r = requests.get(url)
    return r.json()["results"]

@app.get('/ceda/catalogue/datasets')
def get_datasets(datapath: Optional[str] = None):
    results = []
    qs = ""

    if datapath:
        qs = f"result_field__dataPath__icontains={datapath}"

    for dset in search_ceda_cat("dataset", qs):
        res = {"uuid": dset["uuid"], "title": dset["title"], "datapath": dset["result_field"]["dataPath"]}
        results.append(res)
    return results

# @app.get('/cities/{city_id}')
# def get_city(city_id: int):
#     return db[city_id-1]

# @app.post('/cities')
# def create_city(city: City):
#     db.append(city.dict())
#     return db[-1]

# @app.delete('/cities/{city_id}')
# def delete_city(city_id: int):
#     db.pop(city_id-1)
#     return {}