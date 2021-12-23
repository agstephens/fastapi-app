import os
import datetime

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
import requests
import json

app = FastAPI()

origins = [
  "http://localhost:3000",
  "http://localhost:8999",
  "http://192.168.50.70:3000",
  "http://192.168.50.70:8999"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def now():
    return datetime.datetime.now().isoformat().split(".")[0]

@app.get('/')
def index():
    return {'key': 'value'}



class JsonDB:

  model_props = ["id"]
  
  def __init__(self, filepath):

    self.file = filepath
    if not os.path.isfile(self.file):
      open(self.file, 'w').write('{"db": []}')
  
  def delete(self, _id):
    db = self._load()
    filtered = [rec for rec in db if rec['id'] != int(_id)]
    self._save(filtered)

  def add(self, content):
    db = self._load()

    if len(db) == 0:
      next_id = 1
    else:
      next_id = db[-1]['id'] + 1

    rec = {"id": next_id}
    for prop in self.model_props:
      if prop != "id":
        rec[prop] = getattr(content, prop)
    # rec = {"id": next_id, 
    #        "name": todo.name, 
    #        "description": todo.description,
    #        "complete": todo.complete,
    #        "updated": todo.updated
    #        }

    db.append(rec)
    self._save(db)
    return rec

  def get_all(self):
    return self._load()

  def get(self, _id):
    db = self._load()
    try:
      rec = [rec for rec in db if rec['id'] == int(_id)][0]
      return rec
    except:
      return None

  def update(self, _id, content):

    db = self._load()
    resp = None

    for rec in db:
      if rec["id"] == _id:

         for prop in self.model_props:
           if prop == "id": continue
           elif prop == "updated":
             rec[prop] = now()
           else:
             rec[prop] = content[prop]
         resp = rec 
   
    self._save(db) 
    return resp

  def _load(self):
    db = json.load(open(self.file))["db"]
    return db

  def _save(self, recs):
    db = {"db": recs}
    with open(self.file, "w") as writer:
      json.dump(db, writer)

    return True






# Todo models and API
class TodoDB(JsonDB):
  model_props = ["id", "name", "description", "people", "orgs", "groups", "complete",  "updated"]


class Todo(BaseModel):
    name: str
    description: str
    people: List[str] = Field(default_factory=list)
    orgs: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    complete: bool
    updated: str = Field(default_factory=now)


@app.get('/todos')
def get_todos():
    results = todo_db.get_all()
    return results

@app.get('/todos/{todo_id}')
def get_todo(todo_id: int):
    return todo_db.get(todo_id)

@app.put('/todos/{todo_id}')
def update_todo(todo_id: int, todo: Todo):
    rec = todo_db.get(todo_id)
    rec.update(todo.dict())
    return todo_db.update(todo_id, rec)

@app.post('/todos')
def create_todo(todo: Todo):
    rec = todo_db.add(todo)
    return rec

@app.delete('/todos/{todo_id}')
def delete_todo(todo_id: int):
    todo_db.delete(todo_id)
    return {}


# Person models and API
class PersonDB(JsonDB):
  model_props = ["id", "name", "org"]

class Person(BaseModel):
    name: str
    description: str
    org: int = Field(default_factory=1)


@app.get('/people')
def get_persons():
    results = person_db.get_all()
    return results

@app.get('/people/{person_id}')
def get_person(person_id: int):
    return person_db.get(person_id)

@app.put('/people/{person_id}')
def update_person(person_id: int, person: Person):
    rec = person_db.get(person_id)
    rec.update(person.dict())
    return person_db.update(person_id, rec)

@app.post('/people')
def create_person(person: Person):
    rec = person_db.add(person)
    return rec

@app.delete('/people/{person_id}')
def delete_person(person_id: int):
    person_db.delete(person_id)
    return {}


RecordPlan = {"Org": "name id", 
"Group": [["Person", "Person"], ["Org", "Org"], "id"]}


# Create the DBs
dbdir = "dbs"
if not os.path.isdir(dbdir):
  os.makedirs(dbdir)


todo_db = TodoDB(f'{dbdir}/todo_db.json')
person_db = PersonDB(f'{dbdir}/person_db.json')