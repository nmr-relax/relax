# Python module imports.
from re import search
import sys

# Add the path to the relax base directory.
sys.path.append(sys.path[0])
sys.path[0] = '../..'

# relax module imports.
from prompt.interpreter import Interpreter


class Dummy_class:
    def __init__(self):
        # Some dummy data structures.
        self.script_file = None
        self.intro_string = ''
        self.dummy_mode = 1

        # Start the interpreter!
        self.interpreter = Interpreter(self)
        self.interpreter.run()

        # Get the names of the data structures.
        names = sorted(self.local.keys())

        # Alphabetically sort the names of the data structures.

        # Alphabetically sort the names of the data structures.
        for name in names:
            # Skip the name if it is in the blacklist.
            blacklist = ['Numeric', 'Scientific', 'intro_off', 'intro_on', 'pi', 'script']
            if name in blacklist:
                continue

            # Get the object.
            object = self.local[name]

            # Determine if the structure is user function containing class.
            if hasattr(object, '__relax_help__'):
                # Get the names of the data structures.
                names2 = sorted(dir(object))

                # Alphabetically sort the names of the data structures.
                for name2 in names2:
                    # Skip names begining with an underscore.
                    if search('^_', name2):
                        continue

                    # Get the object.
                    object2 = getattr(object, name2)

                    # Skip the object if there is no docstring.
                    if not hasattr(object2, '__doc__') or not object2.__doc__:
                        continue

                    # Printout.
                    print(name + '.' + name2)

                # Done.
                continue

            # Skip the object if there is no docstring.
            if not hasattr(object, '__doc__') or not object.__doc__:
                continue

            # Print the name.
            print(name)

# Exec.
Dummy_class()
