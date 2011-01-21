# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()

pipe.create('a', 'mf')
cdp.nest = []
path = status.install_path + sep + 'test_suite' + sep + 'system_tests' + sep + 'scripts' + sep + 'nested_scripting' + sep
script(path + 'sub.py')
script(path + 'c.py')
script(path + 'd.py')
