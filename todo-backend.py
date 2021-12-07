import os
import datetime

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

class JsonDB:
  def __init__(self, filepath):
    self.file = filepath
    if not os.path.isfile(self.file):
      open(self.file, 'w').write('{"db": []}')
  
  def delete(self, _id):
    db = self._load()
    filtered = [rec for rec in db if rec['id'] != int(_id)]
    self._save(filtered)

  def add(self, todo):
    db = self._load()

    if len(db) == 0:
      next_id = 1
    else:
      next_id = db[-1]['id'] + 1

    rec = {"id": next_id, 
           "name": todo.name, 
           "description": todo.description,
           "complete": todo.complete,
           "updated": todo.updated
           }
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

  def update(self, _id, updated_rec):
    db = self._load()
    resp = None

    for rec in db:
      if rec["id"] == _id:
         for prop in ("name", "description", "complete"):
             rec[prop] = updated_rec[prop]

         rec["updated"] = now()
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
   
db = JsonDB('./db.json')


def now():
    return datetime.datetime.now().isoformat().split(".")[0]

class Todo(BaseModel):
    name: str
    description: str
    complete: bool
    updated: str = Field(default_factory=now)


@app.get('/')
def index():
    return {'key': 'value'}

@app.get('/todos')
def get_todos():
    results = db.get_all()
    return results

@app.get('/todos/{todo_id}')
def get_todo(todo_id: int):
    return db.get(todo_id)

@app.put('/todos/{todo_id}')
def update_todo(todo_id: int, todo: Todo):
    rec = db.get(todo_id)
    rec.update(todo.dict())
    return db.update(todo_id, rec)

@app.post('/todos')
def create_todo(todo: Todo):
    rec = db.add(todo)
    return rec

@app.delete('/todos/{todo_id}')
def delete_todo(todo_id: int):
    db.delete(todo_id)
    return {}

