###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


    # Program errors.
    #################

    class RelaxProgError(BaseError):
        def __init__(self, name):
            self.text = "The program " + `name` + " cannot be found."

    class RelaxProgFailError(BaseError):
        def __init__(self, name):
            self.text = "Execution of the program " + name + " has failed."


    # PDB errors.
    #############

    # No PDB loaded.
    class RelaxPdbError(BaseError):
        def __init__(self, run):
            self.text = "No PDB file has been loaded for the run " + `run` + "."

    # Loading error.
    class RelaxPdbLoadError(BaseError):
        def __init__(self, name):
            self.text = "The PDB file " + `name` + " could not be loaded properly, no proteins could be extracted."

    # No unit vectors.
    class RelaxNoVectorsError(BaseError):
        def __init__(self, run):
            self.text = "The unit XH bond vectors for the run " + `run` + " have not been calculated."


    # Nuclear errors.
    #################

    # Nucleus not set.
    class RelaxNucleusError(BaseError):
        def __init__(self):
            self.text = "The type of nucleus has not yet been set."


    # Argument errors.
    ##################

    # Invalid argument.
    class RelaxInvalidError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " is invalid."

    # Binary - integers 0 and 1.
    class RelaxBinError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be the integer 0 or 1."

    # Float.
    class RelaxFloatError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be a floating point number."

    # Number.
    class RelaxNumError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be a number."

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

    # Integer or string
    class RelaxIntStrError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be an integer or a string."

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

    # Tuple.
    class RelaxTupleError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be a tuple."

    # Tuple or number.
    class RelaxNumTupleError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a number or tuple of numbers."

    # None.
    class RelaxNoneError(BaseError):
        def __init__(self, name):
            self.text = "The " + name + " argument has not been supplied."

    # None or float.
    class RelaxNoneFloatError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a floating point number or None."

    # None, float, or list.
    class RelaxNoneFloatListError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a floating point number, a list, or None."

    # None or integer.
    class RelaxNoneIntError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be an integer or None."

    # None, integer, or string.
    class RelaxNoneIntStrError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be an integer, a string, or None."

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

    # None, string, or list.
    class RelaxNoneStrListError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a string or None."

    # None or tuple.
    class RelaxNoneTupleError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be a tuple or None."

    # String.
    class RelaxStrError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must be a string."


    # Sequence errors.
    ##################

    # No sequence loaded.
    class RelaxNoSequenceError(BaseError):
        def __init__(self, run):
            self.text = "The sequence data for the run " + `run` + " has not been loaded."

    # The sequence already exists.
    class RelaxSequenceError(BaseError):
        def __init__(self, run):
            self.text = "The sequence data for the run " + `run` + " already exists."

    # The two sequences are different.
    class RelaxDiffSeqError(BaseError):
        def __init__(self, run1, run2):
            self.text = "The sequences for the runs " + `run1` + " and " + `run2` + " are not the same."

    # Cannot find the residue in the sequence.
    class RelaxNoResError(BaseError):
        def __init__(self, number, name=None):
            if name == None:
                self.text = "The residue '" + `number` + "' cannot be found in the sequence."
            else:
                self.text = "The residue '" + `number` + " " + name + "' cannot be found in the sequence."


    # Relaxation data errors.
    #########################

    # No relaxation data.
    class RelaxNoRiError(BaseError):
        def __init__(self, ri_label, frq_label):
            self.text = "Relaxation data corresponding to ri_label = " + `ri_label` + " and frq_label = " + `frq_label` + " does not exist."

    # Relaxation data already exists.
    class RelaxRiError(BaseError):
        def __init__(self, ri_label, frq_label):
            self.text = "Relaxation data corresponding to ri_label = " + `ri_label` + " and frq_label = " + `frq_label` + " already exists."


    # Model-free errors.
    ####################

    # No model-free data.
    class RelaxNoMfError(BaseError):
        def __init__(self, run):
            self.text = "Model-free data corresponding to the run " + `run` + " does not exist."

    # Model-free data already exists.
    class RelaxMfError(BaseError):
        def __init__(self, run):
            self.text = "Model-free data corresponding to the run " + `run` + " already exists."


    # Tensor errors.
    ################

    # Diffusion tensor data corresponding to the run already exists.
    class RelaxTensorError(BaseError):
        def __init__(self, run):
            self.text = "Diffusion tensor data corresponding to the run " + `run` + " already exists."

    # No diffusion tensor data loaded.
    class RelaxNoTensorError(BaseError):
        def __init__(self, run):
            self.text = "No diffusion tensor data is loaded for the run " + `run` + "."


    # File errors.
    ##############

    # No directory.
    class RelaxDirError(BaseError):
        def __init__(self, name, dir):
            if name == None:
                self.text = "The directory " + `dir` + " does not exist."
            else:
                self.text = "The " + name + " directory " + `dir` + " does not exist."

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

    # Invalid file format.
    class RelaxInvalidFileError(BaseError):
        def __init__(self, file_name):
            self.text = "The format of the file " + `file_name` + " is invalid."


    # Run errors.
    #############

    # Run already exists.
    class RelaxRunError(BaseError):
        def __init__(self, run):
            self.text = "The run " + `run` + " already exists."

    # No run.
    class RelaxNoRunError(BaseError):
        def __init__(self, run):
            self.text = "The run " + `run` + " has not been created yet."


    # Setup errors.
    ###############

    # Cannot setup the functions.
    class RelaxFuncSetupError(BaseError):
        def __init__(self, name, equation):
            self.text = "The " + `name` + " functions for the equation type " + `equation` + " cannot be setup."


    # Regular expression errors.
    ############################

    # Bad regular expression.
    class RelaxRegExpError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " is not valid regular expression."


    # Data type errors.
    ###################

    # Value already exists.
    class RelaxValueError(BaseError):
        def __init__(self, data_type, run):
            self.text = "The data type " + `data_type` + " already exists for " + `run` +"."

    # No data value.
    class RelaxNoValueError(BaseError):
        def __init__(self, name):
            self.text = "The " + `name` + " value has not yet been set."

    # Unknown parameter combination.
    class RelaxUnknownParamCombError(BaseError):
        def __init__(self, name, data):
            self.text = "The " + `name` + " argument " + `data` + " represents an unknown parameter combination."
