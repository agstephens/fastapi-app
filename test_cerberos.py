from collections import OrderedDict as OD
from cerberus import Validator


schema = OD({'paramA': {'allowed': ['a1', 'a2', 'a3']},
          'paramB': {'allowed': ['b1', 'b2']}}) 

#v = Validator(schema) 


def transform_schema(schema=schema):
    d = OD()
    for key, value in schema.items():
        d[key] = value['allowed']

    return d
 

ts = transform_schema(schema)


def validate_inputs(inputs, schema=schema):
    result = {"result": v.validate(inputs, schema=schema), 
              "errors": v.errors,
              "schema": v.schema}
    print(result)


def set_b(doc):
    return "HI"


def rename2(value):
    return 'dog'



s2 = OD(
 {'a': {'allowed': [1, 2], 'required': True},
  'b': {'type': 'string', 'required': True},
  'b#1': {'dependencies': {'a': [1]}, 'rename_handler': rename2, 'allowed': ['b_a1']},
  'b#2': {'dependencies': {'a': [2]}, 'rename': 'b', 'allowed': ['b_a2']}
 })

all_inputs = [
        {}, 
        {'a': 1},
        {'a': 1, 'b#1': 'b_a1'},
        {'a': 1, 'b#2': 'b_a2'},
        {'a': 1, 'b#1': 'b_a2'},
    ]
all_inputs = []

for inputs in all_inputs:
    v2 = Validator(s2)
    print(f"Testing: {inputs}") 
    n = v2.normalized(inputs) or {}
    print(f"Normalised: {n}")
    res = v2.validate(n)
    print(f"Valid? {res}")

    if not res:
        print("ERRORS", v2.errors)

    print()



print()
class MyValidator(Validator):

  def _validate_allowed_values_dependencies(self, dummy, field, value):
    # Required to avoid cerberos raising an exception with key "allowed_values_dependencies
    pass

  def _check_with_values_dependent(self, field, value):
    dep_rules = self._config['schema'][field]['allowed_values_dependencies']
    
    for ext_field, ext_dep in dep_rules.items():
        ext_field_value = self.document[ext_field]
        
        ext_dep_values, allowed_values = list(ext_dep.items())[0]
        if ext_field_value in ext_dep_values and value not in allowed_values:
            self._error(field, f"Value for '{field}' is forbidden by schema.")


    print(self._config, dep_rules, self.document)

schema = {'a': {'allowed': [1, 2]},
          'b': {'check_with': 'values_dependent'},
#                'allowed_values_dependencies': {'a': {frozenset([1]): ['b_a1']}, 
#                                                'a': {frozenset([2]): ['b_a2']}}
#               }
          'allowed_values_dependencies_a_b_1': {'default': {'a': {frozenset([1]): ['b_a1']}}}
         }

#from cerberus import rules_set_registry
#rules_set_registry.extend((('allowed_values_dependencies', {'type': 'dict'}),))

schema = {'a': {'allowed': [1, 2]},
          'b': {'check_with': 'values_dependent',
                'allowed_values_dependencies': {'a': {frozenset([1]): ['b_a1']},
                                                'a': {frozenset([2]): ['b_a2']}}
               }
         }

v = MyValidator(schema)
print(v.validate({'a': 2, 'b': 'b_a2'}))
print(v.errors)

print(v.validate({'a': 2, 'b': 'b_a1'}))
print(v.errors)
