###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing all of the RelaxError objects."""


# Python module imports.
from re import match
import time
from types import ClassType

# Global variables.
relax = None
Debug = False



# Base class for all errors.
############################

class BaseError(Exception):
    def __str__(self):
        return ("RelaxError: " + self.text + "\n")


    def save_state(self):
        """Function for saving the program state."""

        # Dummy function.
        if not relax:
            return

        # Append the date and time to the save file.
        now = time.localtime()
        file_name = "relax_state_%i%02i%02i_%02i%02i%02i" % (now[0], now[2], now[1], now[3], now[4], now[5])

        # Save the program state.
        relax.interpreter._State.save(file_name)



# Standard errors.
##################

class RelaxError(BaseError):
    def __init__(self, text):
        self.text = text
        if Debug:
            self.save_state()


# Fault.
########

class RelaxFault(BaseError):
    def __init__(self):
        self.text = "Impossible to be here, please re-run relax with the '--debug' flag and summit a bug report at https://gna.org/projects/relax/."
        self.save_state()


# Code implementation errors.
#############################

# Not implemented yet.
class RelaxImplementError(BaseError):
    def __init__(self):
        self.text = "This function has not yet been implemented."


# Program errors.
#################

# Cannot locate the program.
class RelaxProgError(BaseError):
    def __init__(self, name):
        self.text = "The program " + `name` + " cannot be found."
        if Debug:
            self.save_state()


# The binary executable file does not exist (full path has been given!).
class RelaxMissingBinaryError(BaseError):
    def __init__(self, name):
        self.text = "The binary executable file " + `name` + " does not exist."
        if Debug:
            self.save_state()


# The binary executable file is not executable.
class RelaxNonExecError(BaseError):
    def __init__(self, name):
        self.text = "The binary executable file " + `name` + " is not executable."
        if Debug:
            self.save_state()


# The binary executable file is not located within the system path.
class RelaxNoInPathError(BaseError):
    def __init__(self, name):
        self.text = "The binary executable file " + `name` + " is not located within the system path."
        if Debug:
            self.save_state()


# Program execution failure.
class RelaxProgFailError(BaseError):
    def __init__(self, name):
        self.text = "Execution of the program " + name + " has failed."
        if Debug:
            self.save_state()


# PDB errors.
#############

# PDB data corresponding to the data pipe already exists.
class RelaxPdbError(BaseError):
    def __init__(self, pipe=None):
        if pipe != None:
            self.text = "PDB data corresponding to the data pipe " + `pipe` + " already exists."
        else:
            self.text = "PDB data already exists."
        if Debug:
            self.save_state()

# No PDB loaded.
class RelaxNoPdbError(BaseError):
    def __init__(self, pipe=None):
        if pipe != None:
            self.text = "No PDB file has been loaded for the data pipe " + `pipe` + "."
        else:
            self.text = "No PDB file has been loaded."
        if Debug:
            self.save_state()

# Loading error.
class RelaxPdbLoadError(BaseError):
    def __init__(self, name):
        self.text = "The PDB file " + `name` + " could not be loaded properly, no molecular chains could be extracted."
        if Debug:
            self.save_state()

# No unit vectors.
class RelaxNoVectorsError(BaseError):
    def __init__(self, pipe):
        self.text = "The unit XH bond vectors for the data pipe " + `pipe` + " have not been calculated."
        if Debug:
            self.save_state()

# No chains within the PDB file.
class RelaxNoPdbChainError(BaseError):
    def __init__(self):
        self.text = "No peptide or nucleotide chains can be found within the PDB file."
        if Debug:
            self.save_state()


# Nuclear errors.
#################

# Nucleus not set.
class RelaxNucleusError(BaseError):
    def __init__(self):
        self.text = "The type of nucleus has not yet been set."
        if Debug:
            self.save_state()

# Spin type not set.
class RelaxSpinTypeError(BaseError):
    def __init__(self):
        self.text = "The spin type has not yet been set.  Please use the value.set() user function to set the heteronucleus type."
        if Debug:
            self.save_state()

# Proton type not set.
class RelaxProtonTypeError(BaseError):
    def __init__(self):
        self.text = "The type of proton attached to the spin has not yet been set.  Please use the value.set() user function to set the proton type."
        if Debug:
            self.save_state()


# Argument errors.
##################

# Invalid argument.
class RelaxInvalidError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " is invalid."
        if Debug:
            self.save_state()

# Argument not in the list.
class RelaxArgNotInListError(BaseError):
    def __init__(self, name, value, list):
        self.text = "The " + name + " argument " + `value` + " is neither "
        for i in xrange(len(list)-1):
            self.text = self.text + `list[i]` + ', '
        self.text = self.text + 'nor ' + `list[-1]` + "."
        if Debug:
            self.save_state()

# Boolean - the values True and False.
class RelaxBoolError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " boolean argument " + `value` + " must either be True or False."
        if Debug:
            self.save_state()

# Binary - integers 0 and 1.
class RelaxBinError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be the integer 0 or 1."
        if Debug:
            self.save_state()

# Float.
class RelaxFloatError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be a floating point number."
        if Debug:
            self.save_state()

# Number.
class RelaxNumError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be a number."
        if Debug:
            self.save_state()

# Function.
class RelaxFunctionError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be a function."
        if Debug:
            self.save_state()

# Integer.
class RelaxIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be an integer."
        if Debug:
            self.save_state()

# Integer or list of integers.
class RelaxIntListIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be an integer or an array of integers."
        if Debug:
            self.save_state()

# Integer or string.
class RelaxIntStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be an integer or a string."
        if Debug:
            self.save_state()

# String or file descriptor.
class RelaxStrFileError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a string or a file descriptor."
        if Debug:
            self.save_state()

# Length of the list.
class RelaxLenError(BaseError):
    def __init__(self, name, len):
        self.text = "The " + name + " argument must be of length " + `len` + "."
        if Debug:
            self.save_state()

# List.
class RelaxListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be an array."
        if Debug:
            self.save_state()

# List of floating point numbers.
class RelaxListFloatError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be an array of floating point numbers."
        if Debug:
            self.save_state()

# List of floating point numbers or strings.
class RelaxListFloatStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be an array of floating point numbers or strings."
        if Debug:
            self.save_state()

# List of integers.
class RelaxListIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be an array of integers."
        if Debug:
            self.save_state()

# List of numbers.
class RelaxListNumError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be an array of numbers."
        if Debug:
            self.save_state()

# List of strings.
class RelaxListStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be an array of strings."
        if Debug:
            self.save_state()

# Tuple.
class RelaxTupleError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be a tuple."
        if Debug:
            self.save_state()

# Tuple or number.
class RelaxNumTupleError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a number or tuple of numbers."
        if Debug:
            self.save_state()

# None.
class RelaxNoneError(BaseError):
    def __init__(self, name):
        self.text = "The " + name + " argument has not been supplied."
        if Debug:
            self.save_state()

# None or float.
class RelaxNoneFloatError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a floating point number or None."
        if Debug:
            self.save_state()

# None, float, or list.
class RelaxNoneFloatListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a floating point number, a list, or None."
        if Debug:
            self.save_state()

# None, float, str, or list.
class RelaxNoneFloatStrListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a floating point number, a string, a list, or None."
        if Debug:
            self.save_state()

# None or integer.
class RelaxNoneIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be an integer or None."
        if Debug:
            self.save_state()

# None, integer, or string.
class RelaxNoneIntStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be an integer, a string, or None."
        if Debug:
            self.save_state()

# None or list.
class RelaxNoneListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be an array or None."
        if Debug:
            self.save_state()

# None or list of strings.
class RelaxNoneListstrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be an array of strings or None."
        if Debug:
            self.save_state()

# None or number.
class RelaxNoneNumError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a number or None."
        if Debug:
            self.save_state()

# None or string.
class RelaxNoneStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a string or None."
        if Debug:
            self.save_state()

# None, string, or list.
class RelaxNoneStrListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a string or None."
        if Debug:
            self.save_state()

# None or tuple.
class RelaxNoneTupleError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be a tuple or None."
        if Debug:
            self.save_state()

# String.
class RelaxStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must be a string."
        if Debug:
            self.save_state()

# String or list of strings.
class RelaxStrListStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " must either be an string or an array of strings."
        if Debug:
            self.save_state()


# Sequence errors.
##################

# No sequence loaded.
class RelaxNoSequenceError(BaseError):
    def __init__(self):
        self.text = "The sequence data does not exist."
        if Debug:
            self.save_state()

# The sequence already exists.
class RelaxSequenceError(BaseError):
    def __init__(self, pipe=None):
        if pipe == None:
            self.text = "The sequence data already exists."
        else:
            self.text = "The sequence data for the data pipe " + `pipe` + " already exists."
        if Debug:
            self.save_state()

# The two sequences are different.
class RelaxDiffSeqError(BaseError):
    def __init__(self, pipe1, pipe2):
        self.text = "The sequences for the data pipes " + `pipe1` + " and " + `pipe2` + " are not the same."
        if Debug:
            self.save_state()

# Cannot find the residue in the sequence.
class RelaxNoResError(BaseError):
    def __init__(self, number, name=None):
        if name == None:
            self.text = "The residue '" + `number` + "' cannot be found in the sequence."
        else:
            self.text = "The residue '" + `number` + " " + name + "' cannot be found in the sequence."
        if Debug:
            self.save_state()

# Cannot find the spin in the sequence.
class RelaxNoSpinError(BaseError):
    def __init__(self, id):
        self.text = "The spin " + `id` + " does not exist."
        if Debug:
            self.save_state()

# The sequence data is not valid.
class RelaxInvalidSeqError(BaseError):
    def __init__(self, line):
        self.text = "The line " + `line` + " of the sequence data is invalid."
        if Debug:
            self.save_state()

# The spins have not been loaded
class RelaxSpinsNotLoadedError(BaseError):
    def __init__(self, spin_id):
        self.text = "The spin information for the spin " + `spin_id` + " has not yet been loaded, please use the structure.load_spins() user function."
        if Debug:
            self.save_state()




# Relaxation data errors.
#########################

# No relaxation data.
class RelaxNoRiError(BaseError):
    def __init__(self, ri_label, frq_label):
        self.text = "Relaxation data corresponding to ri_label = " + `ri_label` + " and frq_label = " + `frq_label` + " does not exist."
        if Debug:
            self.save_state()

# Relaxation data already exists.
class RelaxRiError(BaseError):
    def __init__(self, ri_label, frq_label):
        self.text = "Relaxation data corresponding to ri_label = " + `ri_label` + " and frq_label = " + `frq_label` + " already exists."
        if Debug:
            self.save_state()


# Model-free errors.
####################

# Model-free data already exists.
class RelaxMfError(BaseError):
    def __init__(self, pipe):
        self.text = "Model-free data corresponding to the data pipe " + `pipe` + " already exists."
        if Debug:
            self.save_state()


# Tensor errors.
################

# Tensor data corresponding to the data pipe already exists.
class RelaxTensorError(BaseError):
    def __init__(self, tensor_type):
        self.text = "The " + tensor_type + " tensor data already exists."
        if Debug:
            self.save_state()

# No tensor data exists.
class RelaxNoTensorError(BaseError):
    def __init__(self, tensor_type, tensor_label=None):
        if not tensor_label:
            self.text = "No " + tensor_type + " tensor data exists."
        else:
            self.text = "No " + tensor_type + " tensor data exists for the tensor " + `tensor_label` + "."
        if Debug:
            self.save_state()


# File errors.
##############

# No directory.
class RelaxDirError(BaseError):
    def __init__(self, name, dir):
        if name == None:
            self.text = "The directory " + `dir` + " does not exist."
        else:
            self.text = "The " + name + " directory " + `dir` + " does not exist."
        if Debug:
            self.save_state()

# No file.
class RelaxFileError(BaseError):
    def __init__(self, name, file_name=None):
        if file_name == None:
            self.text = "The file " + `name` + " does not exist."
        else:
            self.text = "The " + name + " file " + `file_name` + " does not exist."
        if Debug:
            self.save_state()

# No data in file.
class RelaxFileEmptyError(BaseError):
    def __init__(self):
        self.text = "The file contains no data."
        if Debug:
            self.save_state()

# Overwrite file.
class RelaxFileOverwriteError(BaseError):
    def __init__(self, file_name, flag):
        self.text = "The file " + `file_name` + " already exists.  Set the " + flag + " to 1 to overwrite."
        if Debug:
            self.save_state()

# Invalid data format.
class RelaxInvalidDataError(BaseError):
    def __init__(self):
        self.text = "The format of the data is invalid."
        if Debug:
            self.save_state()


# Data pipe errors.
###################

# The data pipe already exists.
class RelaxPipeError(BaseError):
    def __init__(self, pipe):
        self.text = "The data pipe " + `pipe` + " already exists."
        if Debug:
            self.save_state()

# No data pipe exists.
class RelaxNoPipeError(BaseError):
    def __init__(self, pipe=None):
        if pipe != None:
            self.text = "The data pipe " + `pipe` + " has not been created yet."
        else:
            self.text = "No data pipes currently exist.  Please use the pipe.create() user function first."
        if Debug:
            self.save_state()


# Spin-Residue-Molecule errors.
###############################

# Disallow molecule selection.
class RelaxMolSelectDisallowError(BaseError):
    def __init__(self):
        self.text = "The selection of molecules is not allowed."
        if Debug:
            self.save_state()

# Disallow residue selection.
class RelaxResSelectDisallowError(BaseError):
    def __init__(self):
        self.text = "The selection of residues is not allowed."
        if Debug:
            self.save_state()

# Disallow spin selection.
class RelaxSpinSelectDisallowError(BaseError):
    def __init__(self):
        self.text = "The selection of spin systems is not allowed."
        if Debug:
            self.save_state()


# Setup errors.
###############

# Cannot setup the functions.
class RelaxFuncSetupError(BaseError):
    def __init__(self, string):
        self.text = "This function is not available for " + string + "."
        if Debug:
            self.save_state()

# The model has not been setup.
class RelaxNoModelError(BaseError):
    def __init__(self, name=None):
        if name != None:
            self.text = "The " + name + " model has not been setup."
        else:
            self.text = "The model has not been setup."
        if Debug:
            self.save_state()


# Regular expression errors.
############################

# Bad regular expression.
class RelaxRegExpError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + `value` + " is not valid regular expression."
        if Debug:
            self.save_state()


# Data type errors.
###################

# Parameter cannot be set.
class RelaxParamSetError(BaseError):
    def __init__(self, name, param_type=None):
        if param_type != None:
            self.text = "The " + name + " parameter, " + `param_type` + ", cannot be set."
        else:
            self.text = "The " + name + " parameter cannot be set."
        if Debug:
            self.save_state()

# Value already exists.
class RelaxValueError(BaseError):
    def __init__(self, data_type, pipe):
        self.text = "The data type " + `data_type` + " already exists for the data pipe " + `pipe` + "."
        if Debug:
            self.save_state()

# No data value.
class RelaxNoValueError(BaseError):
    def __init__(self, name):
        self.text = "The " + `name` + " value has not yet been set."
        if Debug:
            self.save_state()

# Unknown data type.
class RelaxUnknownDataTypeError(BaseError):
    def __init__(self, name):
        self.text = "The data type " + `name` + " is unknown."
        if Debug:
            self.save_state()

# Unknown parameter.
class RelaxUnknownParamError(BaseError):
    def __init__(self, name, param_type=None):
        if param_type != None:
            self.text = "The " + name + " parameter, " + `param_type` + ", is unknown."
        else:
            self.text = "The " + name + " parameter is unknown."
        if Debug:
            self.save_state()

# Unknown parameter combination.
class RelaxUnknownParamCombError(BaseError):
    def __init__(self, name, data):
        self.text = "The " + `name` + " argument " + `data` + " represents an unknown parameter combination."
        if Debug:
            self.save_state()


# Simulation errors.
####################

# No simulations.
class RelaxNoSimError(BaseError):
    def __init__(self, pipe):
        self.text = "Simulations for the data pipe " + `pipe` + " have not been setup."
        if Debug:
            self.save_state()


# Style errors.
###############

# Unknown style.
class RelaxStyleError(BaseError):
    def __init__(self, style):
        self.text = "The style " + `style` + " is unknown."
        if Debug:
            self.save_state()


# Colour errors.
################

# Invalid colour.
class RelaxInvalidColourError(BaseError):
    def __init__(self, colour):
        self.text = "The colour " + `colour` + " is invalid."
        if Debug:
            self.save_state()


# Value errors.
###############

# Infinity.
class RelaxInfError(BaseError):
    def __init__(self, name):
        self.text = "The invalid " + name + " floating point value of infinity has occurred."
        if Debug:
            self.save_state()

# NaN (Not a Number).
class RelaxNaNError(BaseError):
    def __init__(self, name):
        self.text = "The invalid " + name + " floating point value of NaN (Not a Number) has occurred."
        if Debug:
            self.save_state()



# An object of all the RelaxErrors.
###################################

# Function for setting up the AllRelaxErrors object.
def all_errors(names):
    """Function for returning all the RelaxErrors to allow the AllRelaxError object to be created."""

    # Empty list.
    list = None

    # Loop over all objects of this module.
    for name in names:
        # Get the object.
        object = globals()[name]

        # Skip over all non error class objects.
        if not (isinstance(object, ClassType) or isinstance(object, type(type))) or not match('Relax', name):
            continue

        # Tuple of all the errors.
        if list == None:
            list = object,
        else:
            list = list, object

    # Return the list of RelaxErrors
    return list

# Initialise the AllRelaxErrors structure so it can be imported.
AllRelaxErrors = all_errors(dir())
