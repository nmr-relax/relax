# Python module imports.
from re import search

# relax module imports.
from prompt.interpreter import Interpreter


# Initialise the interpreter!
interpreter = Interpreter(self)

# Get the names of the data structures.
names = sorted(interpreter._locals.keys())

# Alphabetically sort the names of the data structures.
for name in names:
    # Skip the name if it is in the blacklist.
    blacklist = ['pi', 'script']
    if name in blacklist:
        continue

    # Get the object.
    object = interpreter._locals[name]

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
