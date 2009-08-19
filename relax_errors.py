###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
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
try:
    from bz2 import BZ2File
    bz2 = True
except ImportError:
    bz2 = False
from cPickle import dump
from re import match
from sys import stderr
import time
from types import ClassType

# Global variables.
Debug = False


def save_state():
    """Save the program state, for debugging purposes."""

    # relax data store singleton import.  Must be done here!
    try:
        from data import Relax_data_store; ds = Relax_data_store()

    # Ok, this is not relax so don't do anything!
    except ImportError:
        return

    # Append the date and time to the save file.
    now = time.localtime()
    file_name = "relax_state_%i%02i%02i_%02i%02i%02i" % (now[0], now[2], now[1], now[3], now[4], now[5])

    # Open the file for writing.
    if bz2:
        stderr.write("\n\nStoring the relax state in the file '%s.bz2'.\n\n\n" % file_name)
        file = BZ2File(file_name+'.bz2', 'w')
    else:
        stderr.write("\n\nStoring the relax state in the file '%s'.\n\n\n" % file_name)
        file = open(file_name, 'w')

    # Pickle the data class and write it to file
    dump(ds, file, 1)

    # Close the file.
    file.close()


# Base class for all errors.
############################

class BaseError(Exception):
    def __str__(self):
        # Save the state if debugging is turned on.
        if Debug:
            save_state()

        # Modify the error message to include 'RelaxError' at the start.
        return ("RelaxError: " + self.text + "\n")


# Standard errors.
##################

class RelaxError(BaseError):
    def __init__(self, text):
        self.text = text


# Fault.
########

class RelaxFault(BaseError):
    def __init__(self):
        self.text = "Impossible to be here, please re-run relax with the '--debug' flag and summit a bug report at https://gna.org/projects/relax/."

    def __str__(self):
        # Save the program state, no matter what.
        save_state()

        # Modify the error message to include 'RelaxError' at the start.
        return ("RelaxError: " + self.text + "\n")


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
        self.text = "The program " + repr(name) + " cannot be found."


# The binary executable file does not exist (full path has been given!).
class RelaxMissingBinaryError(BaseError):
    def __init__(self, name):
        self.text = "The binary executable file " + repr(name) + " does not exist."


# The binary executable file is not executable.
class RelaxNonExecError(BaseError):
    def __init__(self, name):
        self.text = "The binary executable file " + repr(name) + " is not executable."


# The binary executable file is not located within the system path.
class RelaxNoInPathError(BaseError):
    def __init__(self, name):
        self.text = "The binary executable file " + repr(name) + " is not located within the system path."


# Program execution failure.
class RelaxProgFailError(BaseError):
    def __init__(self, name):
        self.text = "Execution of the program " + name + " has failed."


# PDB errors.
#############

# PDB data corresponding to the data pipe already exists.
class RelaxPdbError(BaseError):
    def __init__(self, pipe=None):
        if pipe != None:
            self.text = "PDB data corresponding to the data pipe " + repr(pipe) + " already exists."
        else:
            self.text = "PDB data already exists."

# No PDB loaded.
class RelaxNoPdbError(BaseError):
    def __init__(self, pipe=None):
        if pipe != None:
            self.text = "No PDB file has been loaded for the data pipe " + repr(pipe) + "."
        else:
            self.text = "No PDB file has been loaded."

# Loading error.
class RelaxPdbLoadError(BaseError):
    def __init__(self, name):
        self.text = "The PDB file " + repr(name) + " could not be loaded properly, no molecular chains could be extracted."

# No unit vectors.
class RelaxNoVectorsError(BaseError):
    def __init__(self, pipe):
        self.text = "The unit XH bond vectors for the data pipe " + repr(pipe) + " have not been calculated."

# No chains within the PDB file.
class RelaxNoPdbChainError(BaseError):
    def __init__(self):
        self.text = "No peptide or nucleotide chains can be found within the PDB file."


# Nuclear errors.
#################

# Nucleus not set.
class RelaxNucleusError(BaseError):
    def __init__(self):
        self.text = "The type of nucleus has not yet been set."

# Spin type not set.
class RelaxSpinTypeError(BaseError):
    def __init__(self):
        self.text = "The spin type has not yet been set.  Please use the value.set() user function to set the heteronucleus type."

# Proton type not set.
class RelaxProtonTypeError(BaseError):
    def __init__(self):
        self.text = "The type of proton attached to the spin has not yet been set.  Please use the value.set() user function to set the proton type."


# Argument errors.
##################

# Invalid argument.
class RelaxInvalidError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " is invalid."

# Argument not in the list.
class RelaxArgNotInListError(BaseError):
    def __init__(self, name, value, list):
        self.text = "The " + name + " argument " + repr(value) + " is neither "
        for i in xrange(len(list)-1):
            self.text = self.text + repr(list[i]) + ', '
        self.text = self.text + 'nor ' + repr(list[-1]) + "."

# Boolean - the values True and False.
class RelaxBoolError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " boolean argument " + repr(value) + " must either be True or False."

# Binary - integers 0 and 1.
class RelaxBinError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be the integer 0 or 1."

# Float.
class RelaxFloatError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be a floating point number."

# Number.
class RelaxNumError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be a number."

# Function.
class RelaxFunctionError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be a function."

# Integer.
class RelaxIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be an integer."

# Integer or list of integers.
class RelaxIntListIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be an integer or an array of integers."

# Integer or string.
class RelaxIntStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be an integer or a string."

# String or file descriptor.
class RelaxStrFileError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a string or a file descriptor."

# Length of the list.
class RelaxLenError(BaseError):
    def __init__(self, name, len):
        self.text = "The " + name + " argument must be of length " + repr(len) + "."

# List.
class RelaxListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be an array."

# List of floating point numbers.
class RelaxListFloatError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be an array of floating point numbers."

# List of floating point numbers or strings.
class RelaxListFloatStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be an array of floating point numbers or strings."

# List of integers.
class RelaxListIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be an array of integers."

# List of numbers.
class RelaxListNumError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be an array of numbers."

# List of strings.
class RelaxListStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be an array of strings."

# Tuple.
class RelaxTupleError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be a tuple."

# Tuple or number.
class RelaxNumTupleError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a number or tuple of numbers."

# None.
class RelaxNoneError(BaseError):
    def __init__(self, name):
        self.text = "The " + name + " argument has not been supplied."

# None or float.
class RelaxNoneFloatError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a floating point number or None."

# None, float, or list.
class RelaxNoneFloatListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a floating point number, a list, or None."

# None, float, str, or list.
class RelaxNoneFloatStrListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a floating point number, a string, a list, or None."

# None or integer.
class RelaxNoneIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be an integer or None."

# None, integer, or list of integers.
class RelaxNoneIntListIntError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be None, an integer or an array of integers."

# None, integer, or string.
class RelaxNoneIntStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be an integer, a string, or None."

# None or list.
class RelaxNoneListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be an array or None."

# None or list of strings.
class RelaxNoneListstrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be an array of strings or None."

# None or number.
class RelaxNoneNumError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a number or None."

# None or string.
class RelaxNoneStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a string or None."

# None, string, or list.
class RelaxNoneStrListError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be None, a string or a list."

# None, string, or list of strings.
class RelaxNoneStrListStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be None, a string or a list of strings."

# None or tuple.
class RelaxNoneTupleError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be a tuple or None."

# String.
class RelaxStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must be a string."

# String or list of strings.
class RelaxStrListStrError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " must either be an string or an array of strings."


# Sequence errors.
##################

# No sequence loaded.
class RelaxNoSequenceError(BaseError):
    def __init__(self, pipe=None):
        if pipe == None:
            self.text = "The sequence data does not exist."
        else:
            self.text = "The sequence data for the data pipe " + repr(pipe) + " does not exist."

# The sequence already exists.
class RelaxSequenceError(BaseError):
    def __init__(self, pipe=None):
        if pipe == None:
            self.text = "The sequence data already exists."
        else:
            self.text = "The sequence data for the data pipe " + repr(pipe) + " already exists."

# The two sequences are different.
class RelaxDiffSeqError(BaseError):
    def __init__(self, pipe1, pipe2):
        self.text = "The sequences for the data pipes " + repr(pipe1) + " and " + repr(pipe2) + " are not the same."

# The number of molecules are different.
class RelaxDiffMolNumError(BaseError):
    def __init__(self, pipe1, pipe2):
        self.text = "The number of molecules do not match between pipes '%s' and '%s'." % (pipe1, pipe2)

# The number of residues are different.
class RelaxDiffResNumError(BaseError):
    def __init__(self, pipe1, pipe2):
        self.text = "The number of residues do not match between pipes '%s' and '%s'." % (pipe1, pipe2)

# The number of spins are different.
class RelaxDiffSpinNumError(BaseError):
    def __init__(self, pipe1, pipe2):
        self.text = "The number of spins do not match between pipes '%s' and '%s'." % (pipe1, pipe2)

# Cannot find the residue in the sequence.
class RelaxNoResError(BaseError):
    def __init__(self, number, name=None):
        if name == None:
            self.text = "The residue '" + repr(number) + "' cannot be found in the sequence."
        else:
            self.text = "The residue '" + repr(number) + " " + name + "' cannot be found in the sequence."

# Cannot find the spin in the sequence.
class RelaxNoSpinError(BaseError):
    def __init__(self, id):
        self.text = "The spin " + repr(id) + " does not exist."

# The sequence data is not valid.
class RelaxInvalidSeqError(BaseError):
    def __init__(self, line):
        self.text = "The line " + repr(line) + " of the sequence data is invalid."

# The spins have not been loaded
class RelaxSpinsNotLoadedError(BaseError):
    def __init__(self, spin_id):
        self.text = "The spin information for the spin " + repr(spin_id) + " has not yet been loaded, please use the structure.load_spins() user function."




# Relaxation data errors.
#########################

# No relaxation data.
class RelaxNoRiError(BaseError):
    def __init__(self, ri_label, frq_label):
        self.text = "Relaxation data corresponding to ri_label = " + repr(ri_label) + " and frq_label = " + repr(frq_label) + " does not exist."

# Relaxation data already exists.
class RelaxRiError(BaseError):
    def __init__(self, ri_label, frq_label):
        self.text = "Relaxation data corresponding to ri_label = " + repr(ri_label) + " and frq_label = " + repr(frq_label) + " already exists."


# RDC and PCS data errors.
##########################

# No RDC data.
class RelaxNoRDCError(BaseError):
    def __init__(self, id):
        self.text = "RDC data corresponding to the identification string " + repr(id) + " does not exist."

# RDC data already exists.
class RelaxRDCError(BaseError):
    def __init__(self, id):
        self.text = "RDC data corresponding to the identification string " + repr(id) + " already exists."

# No PCS data.
class RelaxNoPCSError(BaseError):
    def __init__(self, id):
        self.text = "PCS data corresponding to the identification string " + repr(id) + " does not exist."

# PCS data already exists.
class RelaxPCSError(BaseError):
    def __init__(self, id):
        self.text = "PCS data corresponding to the identification string " + repr(id) + " already exists."


# Model-free errors.
####################

# Model-free data already exists.
class RelaxMfError(BaseError):
    def __init__(self, pipe):
        self.text = "Model-free data corresponding to the data pipe " + repr(pipe) + " already exists."


# Tensor errors.
################

# Tensor data corresponding to the data pipe already exists.
class RelaxTensorError(BaseError):
    def __init__(self, tensor_type):
        self.text = "The " + tensor_type + " tensor data already exists."

# No tensor data exists.
class RelaxNoTensorError(BaseError):
    def __init__(self, tensor_type, tensor_label=None):
        if not tensor_label:
            self.text = "No " + tensor_type + " tensor data exists."
        else:
            self.text = "No " + tensor_type + " tensor data exists for the tensor " + repr(tensor_label) + "."


# File errors.
##############

# No directory.
class RelaxDirError(BaseError):
    def __init__(self, name, dir):
        if name == None:
            self.text = "The directory " + repr(dir) + " does not exist."
        else:
            self.text = "The " + name + " directory " + repr(dir) + " does not exist."

# No file.
class RelaxFileError(BaseError):
    def __init__(self, name, file_name=None):
        if file_name == None:
            self.text = "The file " + repr(name) + " does not exist."
        else:
            self.text = "The " + name + " file " + repr(file_name) + " does not exist."

# No data in file.
class RelaxFileEmptyError(BaseError):
    def __init__(self):
        self.text = "The file contains no data."

# Overwrite file.
class RelaxFileOverwriteError(BaseError):
    def __init__(self, file_name, flag):
        self.text = "The file " + repr(file_name) + " already exists.  Set the " + flag + " to True to overwrite."

# Invalid data format.
class RelaxInvalidDataError(BaseError):
    def __init__(self):
        self.text = "The format of the data is invalid."


# Data pipe errors.
###################

# The data pipe already exists.
class RelaxPipeError(BaseError):
    def __init__(self, pipe):
        self.text = "The data pipe " + repr(pipe) + " already exists."

# No data pipe exists.
class RelaxNoPipeError(BaseError):
    def __init__(self, pipe=None):
        if pipe != None:
            self.text = "The data pipe " + repr(pipe) + " has not been created yet."
        else:
            self.text = "No data pipes currently exist.  Please use the pipe.create() user function first."


# Spin-Residue-Molecule errors.
###############################

# Disallow molecule selection.
class RelaxMolSelectDisallowError(BaseError):
    def __init__(self):
        self.text = "The selection of molecules is not allowed."

# Disallow residue selection.
class RelaxResSelectDisallowError(BaseError):
    def __init__(self):
        self.text = "The selection of residues is not allowed."

# Disallow spin selection.
class RelaxSpinSelectDisallowError(BaseError):
    def __init__(self):
        self.text = "The selection of spin systems is not allowed."

# The spin must be specified.
class RelaxNoSpinSpecError(BaseError):
    def __init__(self):
        self.text = "The spin system must be specified."



# Setup errors.
###############

# Cannot setup the functions.
class RelaxFuncSetupError(BaseError):
    def __init__(self, string):
        self.text = "This function is not available for " + string + "."

# The model already exists.
class RelaxModelError(BaseError):
    def __init__(self, name=None):
        if name != None:
            self.text = "The " + name + " model already exists."
        else:
            self.text = "The model already exists."


# The model has not been setup.
class RelaxNoModelError(BaseError):
    def __init__(self, name=None):
        if name != None:
            self.text = "The specific " + name + " model has not been selected or set up."
        else:
            self.text = "The specific model has not been selected or set up."


# Regular expression errors.
############################

# Bad regular expression.
class RelaxRegExpError(BaseError):
    def __init__(self, name, value):
        self.text = "The " + name + " argument " + repr(value) + " is not valid regular expression."


# Data type errors.
###################

# Parameter cannot be set.
class RelaxParamSetError(BaseError):
    def __init__(self, name, param_type=None):
        if param_type != None:
            self.text = "The " + name + " parameter, " + repr(param_type) + ", cannot be set."
        else:
            self.text = "The " + name + " parameter cannot be set."

# Value already exists.
class RelaxValueError(BaseError):
    def __init__(self, data_type, pipe=None):
        if pipe != None:
            self.text = "The data type " + repr(data_type) + " already exists for the data pipe " + repr(pipe) + "."
        else:
            self.text = "The data type " + repr(data_type) + " already exists."

# No data value.
class RelaxNoValueError(BaseError):
    def __init__(self, name):
        self.text = "The " + repr(name) + " value has not yet been set."

# Unknown data type.
class RelaxUnknownDataTypeError(BaseError):
    def __init__(self, name):
        self.text = "The data type " + repr(name) + " is unknown."

# Unknown parameter.
class RelaxUnknownParamError(BaseError):
    def __init__(self, name, param_type=None):
        if param_type != None:
            self.text = "The " + name + " parameter, " + repr(param_type) + ", is unknown."
        else:
            self.text = "The " + name + " parameter is unknown."

# Unknown parameter combination.
class RelaxUnknownParamCombError(BaseError):
    def __init__(self, name, data):
        self.text = "The " + repr(name) + " argument " + repr(data) + " represents an unknown parameter combination."


# Simulation errors.
####################

# No simulations.
class RelaxNoSimError(BaseError):
    def __init__(self, pipe=None):
        if pipe:
            self.text = "Simulations for the data pipe " + repr(pipe) + " have not been setup."
        else:
            self.text = "Simulations have not been setup."


# Style errors.
###############

# Unknown style.
class RelaxStyleError(BaseError):
    def __init__(self, style):
        self.text = "The style " + repr(style) + " is unknown."


# Colour errors.
################

# Invalid colour.
class RelaxInvalidColourError(BaseError):
    def __init__(self, colour):
        self.text = "The colour " + repr(colour) + " is invalid."


# Value errors.
###############

# Infinity.
class RelaxInfError(BaseError):
    def __init__(self, name):
        self.text = "The invalid " + name + " floating point value of infinity has occurred."

# NaN (Not a Number).
class RelaxNaNError(BaseError):
    def __init__(self, name):
        self.text = "The invalid " + name + " floating point value of NaN (Not a Number) has occurred."


# XML errors.
#############

# Cannot recreate from the XML - the structure is not empty.
class RelaxFromXMLNotEmptyError(BaseError):
    def __init__(self, name):
        self.text = "The " + name + " data structure cannot be recreated from the XML elements as the structure is not empty."



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
