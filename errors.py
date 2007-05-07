###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
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
import time
import warnings
import inspect



# The RelaxError system.
########################

class RelaxErrors:
    def __init__(self, relax):
        """Class for placing all the errors below into __builtin__"""

        # Loop over all objects in 'self'.
        for name in dir(self):
            # Get the object.
            object = getattr(self, name)

            # Skip over all non error class objects.
            if not (isinstance(object, ClassType) or isinstance(object, type(type))) or not match('Relax', name):
                continue

            # Add the top level relax class:
            setattr(object, '_relax', relax)

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


        def save_state(self):
            """Function for saving the program state."""

            now = time.localtime()
            file_name = "relax_state_%i%02i%02i_%02i%02i%02i" % (now[0], now[2], now[1], now[3], now[4], now[5])
            self._relax.interpreter._State.save(file_name)


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

    # PDB data corresponding to the run already exists.
    class RelaxPdbError(BaseError):
        def __init__(self, run):
            self.text = "PDB data corresponding to the run " + `run` + " already exists."
            if Debug:
                self.save_state()

    # No PDB loaded.
    class RelaxNoPdbError(BaseError):
        def __init__(self, run):
            self.text = "No PDB file has been loaded for the run " + `run` + "."
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
        def __init__(self, run):
            self.text = "The unit XH bond vectors for the run " + `run` + " have not been calculated."
            if Debug:
                self.save_state()

    # PDB data corresponding to the run already exists.
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

    # Integer or string
    class RelaxIntStrError(BaseError):
        def __init__(self, name, value):
            self.text = "The " + name + " argument " + `value` + " must either be an integer or a string."
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
        def __init__(self, run):
            self.text = "The sequence data for the run " + `run` + " does not exist."
            if Debug:
                self.save_state()

    # The sequence already exists.
    class RelaxSequenceError(BaseError):
        def __init__(self, run):
            self.text = "The sequence data for the run " + `run` + " already exists."
            if Debug:
                self.save_state()

    # The two sequences are different.
    class RelaxDiffSeqError(BaseError):
        def __init__(self, run1, run2):
            self.text = "The sequences for the runs " + `run1` + " and " + `run2` + " are not the same."
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
        def __init__(self, run):
            self.text = "Model-free data corresponding to the run " + `run` + " already exists."
            if Debug:
                self.save_state()


    # Tensor errors.
    ################

    # Diffusion tensor data corresponding to the run already exists.
    class RelaxTensorError(BaseError):
        def __init__(self, run):
            self.text = "Diffusion tensor data corresponding to the run " + `run` + " already exists."
            if Debug:
                self.save_state()

    # No diffusion tensor data loaded.
    class RelaxNoTensorError(BaseError):
        def __init__(self, run):
            self.text = "No diffusion tensor data is loaded for the run " + `run` + "."
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


    # Run errors.
    #############

    # Run already exists.
    class RelaxRunError(BaseError):
        def __init__(self, run):
            self.text = "The run " + `run` + " already exists."
            if Debug:
                self.save_state()

    # No run.
    class RelaxNoRunError(BaseError):
        def __init__(self, run):
            self.text = "The run " + `run` + " has not been created yet."
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
        def __init__(self, run):
            self.text = "The models corresponding to the run " + `run` + " have not been setup."
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

    # Value already exists.
    class RelaxValueError(BaseError):
        def __init__(self, data_type, run):
            self.text = "The data type " + `data_type` + " already exists for " + `run` + "."
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
            if param_type:
                self.text = "The " + param_type + " parameter " + `name` + " is unknown."
            else:
                self.text = "The parameter " + `name` + " is unknown."
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
        def __init__(self, run):
            self.text = "Simulations for the run " + `run` + " have not been setup."
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



# The RelaxWarning system.
##########################

class RelaxWarnings:
    def __init__(self):
        """Class for placing all the warnings below into __builtin__"""

        # Loop over all objects in 'self'.
        for name in dir(self):
            # Get the object.
            object = getattr(self, name)

            # Skip over all non-warning class objects.
            if not (isinstance(object, ClassType) or isinstance(object, type(type))) or not match('Relax', name):
                continue

            # Place the warnings into __builtin__
            __builtin__.__setattr__(name, object)

            # Tuple of all the warnings.
            if hasattr(__builtin__, 'AllRelaxWarnings'):
                __builtin__.AllRelaxWarnings = __builtin__.AllRelaxWarnings, object
            else:
                __builtin__.AllRelaxWarnings = object,

        # Format warning messages.
        warnings.formatwarning = self.format

        # Set warning filters.
        if Pedantic:
            warnings.filterwarnings('error', category=self.BaseWarning)
        else:
            warnings.filterwarnings('always', category=self.BaseWarning)


    def format(self, message, category, filename, lineno):
        """ Replacement for warnings.formatwarning to customise output format."""

        # Add the text 'RelaxWarning: ' to the start of the warning message.
        if issubclass(category, self.BaseWarning):
            message = "RelaxWarning: %s\n\n" % message

        # Print stack-trace in debug mode.
        if Debug:
            tb = ""
            for frame in inspect.stack()[4:]:
                file = frame[1]
                lineNo = frame[2]
                func = frame[3]
                tb_frame = '  File "%s", line %i, in %s\n' % (file, lineNo, func)
                try:
                    context = frame[4][frame[5]]
                except TypeError:
                    pass
                else:
                    tb_frame = '%s    %s\n' % (tb_frame, context.strip())
                tb = tb_frame + tb
            tb = "Traceback (most recent call last):\n%s" % tb
            message = tb + message

        # Return the warning message.
        return message


    # Base class for all warnings.
    ##############################

    class BaseWarning(Warning, RelaxErrors.BaseError):
        def __str__(self):
            return self.text


    # Standard warnings.
    ####################

    class RelaxWarning(BaseWarning):
        def __init__(self, text):
            self.text = text


    # PDB warnings.
    ###############

    # Zero length XH bond vector.
    class RelaxZeroVectorWarning(BaseWarning):
        def __init__(self, res):
            self.text = "The XH bond vector for residue " + `res` + " is of zero length."


    # The atom is missing from the PDB file.
    class RelaxNoAtomWarning(BaseWarning):
        def __init__(self, atom, res):
            self.text = "The atom %s could not be found for residue %i" % (atom, res)


    # The PDB file is missing.
    class RelaxNoPDBFileWarning(BaseWarning):
        def __init__(self, file):
            self.text = "The PDB file %s cannot be found, no structures will be loaded." % file
