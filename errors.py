import __builtin__


class RelaxErrors:
    def __init__(self):
        """Class for placing all the user errors below into __builtin__"""

        # Place the exceptions into __builtin__
        __builtin__.UserError = UserError
        __builtin__.UserArgListError = UserArgListError
        __builtin__.UserArgNoneError = UserArgNoneError
        __builtin__.UserArgStrError = UserArgStrError

        # Tuple of all the errors.
        __builtin__.AllUserErrors = (UserError, UserArgListError, UserArgNoneError, UserArgStrError)


# Base class for the user errors.
######################

class BaseError(Exception):
    def __str__(self):
        return ("UserError: " + self.text + "\n")


# Standard user error.
######################

class UserError(BaseError):
    def __init__(self, text):
        self.text = text


# Argument errors.
##################

# Function.
class UserArgFunctionError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be a function."

# Integers 0 and 1.
class UserArgBinError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be either the integers 0 or 1."

# Integer.
class UserArgIntError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be an integer."

# Integer or list of integers.
class UserArgIntListIntError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be either an integer or an array of integers."

# List.
class UserArgListError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be an array."

# List of integers.
class UserArgListIntError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be an array of integers."

# List of numbers.
class UserArgListNumError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be an array of numbers."

# List of strings.
class UserArgListStrError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be an array of strings."

# None.
class UserArgNoneError(BaseError):
    def __init__(self, arg):
        self.text = "The " + arg + " argument has not been supplied."

# None or list.
class UserArgNoneListError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be either an array or None."

# None or number.
class UserArgNoneNumError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be either a number or None."

# None or string.
class UserArgNoneStrError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be either a string or None."

# String.
class UserArgStrError(BaseError):
    def __init__(self, arg, value):
        self.text = "The " + arg + " argument " + `value` + " must be a string."


# Sequence errors.
##################

# No sequence loaded.
class UserSequenceError(BaseError):
    def __init__(self):
        self.text = "Sequence data has not been loaded."

# Cannot find the residue in the sequence.
class UserNoResError(BaseError):
    def __init__(self, number):
        self.text = "The residue " + `number` + " cannot be found in the sequence."
