import __builtin__
from re import match
from types import ClassType


class RelaxErrors:
    def __init__(self):
        """Class for placing all the errors below into __builtin__"""

        # Loop over all objects in 'self'.
        for name in dir(self):
            # Get the object.
            object = getattr(self, name)

            # Skip over all non error class objects.
            if type(object) != ClassType or not match('Relax', name):
                continue

            # Place the exceptions into __builtin__
            __builtin__.__setattr__(name, object)

            # Tuple of all the errors.
            if hasattr(__builtin__, 'AllRelaxErrors'):
                __builtin__.AllRelaxErrors = __builtin__.AllRelaxErrors, object
            else:
                __builtin__.AllRelaxErrors = object,


    # Base class for all errors.
    ############################

    class BaseError(Exception):
        def __str__(self):
            return ("RelaxError: " + self.text + "\n")


    # Standard errors.
    ##################

    class RelaxError(BaseError):
        def __init__(self, text):
            self.text = text


    # Type errors.
    ##############

    # Binary - integers 0 and 1.
    class RelaxBinError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be the integer 0 or 1."

    # Float.
    class RelaxFloatError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be a floating point number."

    # Function.
    class RelaxFunctionError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be a function."

    # Integer.
    class RelaxIntError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be an integer."

    # Integer or list of integers.
    class RelaxIntListIntError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be an integer or an array of integers."

    # Length of the list.
    class RelaxLenError(BaseError):
        def __init__(self, name, len):
            self.text = "The " + name + " argument must be of length " + `len` + "."

    # List.
    class RelaxListError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be an array."

    # List of floating point numbers.
    class RelaxListFloatError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be an array of floating point numbers."

    # List of integers.
    class RelaxListIntError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be an array of integers."

    # List of numbers.
    class RelaxListNumError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be an array of numbers."

    # List of strings.
    class RelaxListStrError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be an array of strings."

    # None.
    class RelaxNoneError(BaseError):
        def __init__(self, name):
            self.text = "The " + name + " argument has not been supplied."

    # None or Float.
    class RelaxNoneFloatError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a floating point number or None."

    # None or list.
    class RelaxNoneListError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be an array or None."

    # None or number.
    class RelaxNoneNumError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a number or None."

    # None or string.
    class RelaxNoneStrError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a string or None."

    # String.
    class RelaxStrError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be a string."


    # Sequence errors.
    ##################

    # No sequence loaded.
    class RelaxSequenceError(BaseError):
        def __init__(self):
            self.text = "Sequence data has not been loaded."

    # Cannot find the residue in the sequence.
    class RelaxNoResError(BaseError):
        def __init__(self, number, name=None):
            if name == None:
                self.text = "The residue " + `number` + " cannot be found in the sequence."
            else:
                self.text = "The residue " + `number` + " " + name + " cannot be found in the sequence."


    # File errors.
    ##############

    # No file.
    class RelaxFileError(BaseError):
        def __init__(self, name, file_name):
            if name == None:
                self.text = "The file " + `file_name` + " does not exist."
            else:
                self.text = "The " + name + " file " + `file_name` + " does not exist."

    # No data in file.
    class RelaxFileEmptyError(BaseError):
        def __init__(self):
            self.text = "The file contains no data."

    # Overwrite file.
    class RelaxFileOverwriteError(BaseError):
        def __init__(self, file_name, flag):
            self.text = "The file " + `file_name` + " already exists.  Set the " + flag + " to 1 to overwrite."


    # Run errors.
    #############

    # No run.
    class RelaxRunError(BaseError):
        def __init__(self, run):
            self.text = "The run " + `run` + " does not exist."
