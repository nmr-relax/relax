# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()

path = status.install_path + sep + 'test_suite' + sep + 'system_tests' + sep + 'scripts' + sep + 'nested_scripting' + sep
script(path + 'a.py')
script(path + 'b.py')
