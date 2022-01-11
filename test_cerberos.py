from collections import OrderedDict as OD
from cerberus import Validator
import warnings
print("[WARNING] Filtering out warnings at the moment")
warnings.filterwarnings("ignore")


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

#      print("[DEBUG]:", self._config, dep_rules, self.document)


schema = {'a': {'allowed': [1, 2]},
          'b': {'check_with': 'values_dependent',
                'allowed_values_dependencies': {'a': {frozenset([1]): ['b_a1']},
                                                'a': {frozenset([2]): ['b_a2']}}
               }
         }


v = MyValidator(schema)
doc = {'a': 2, 'b': 'b_a2'}
print("Testing:", doc)
print(v.validate(doc))
assert not v.errors

print()
doc = {'a': 2, 'b': 'b_a1'}
print("Testing:", doc)
print(v.validate(doc))
assert v.errors == {'b': ["Value for 'b' is forbidden by schema."]}
print(v.errors)
