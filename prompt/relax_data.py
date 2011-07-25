###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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
"""Module containing the 'relax_data' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns import relax_data
from relax_errors import RelaxError


class Relax_data(User_fn_class):
    """Class for manipulating R1, R2, and NOE relaxation data."""

    def back_calc(self, ri_id=None, ri_type=None, frq=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.back_calc("
            text = text + "ri_id=" + repr(ri_id)
            text = text + ", ri_type=" + repr(ri_type)
            text = text + ", frq=" + repr(frq) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation ID string', can_be_none=True)
        arg_check.is_str(ri_type, 'relaxation type', can_be_none=True)
        arg_check.is_num(frq, 'frequency', can_be_none=True)

        # Execute the functional code.
        relax_data.back_calc(ri_id=ri_id, ri_type=ri_type, frq=frq)

    # The function doc info.
    back_calc._doc_title = "Back calculate the relaxation data at the given frequency."
    back_calc._doc_title_short = "Relaxation data back calculation."
    back_calc._doc_args = [
        ["ri_id", "The relaxation data ID string."],
        ["ri_type", "The relaxation data type, ie 'R1', 'R2', or 'NOE'."],
        ["frq", "The spectrometer frequency in Hz."]
    ]
    back_calc._doc_desc = """
        This allows relaxation data of the given type and frequency to be back calculated from the model parameter values.
        """
    _build_doc(back_calc)


    def copy(self, pipe_from=None, pipe_to=None, ri_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", ri_id=" + repr(ri_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)
        arg_check.is_str(ri_id, 'relaxation data ID string', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        relax_data.copy(pipe_from=pipe_from, pipe_to=pipe_to, ri_id=ri_id)

    # The function doc info.
    copy._doc_title = "Copy relaxation data from one pipe to another."
    copy._doc_title_short = "Relaxation data copying."
    copy._doc_args = [
        ["pipe_from", "The name of the pipe to copy the relaxation data from."],
        ["pipe_to", "The name of the pipe to copy the relaxation data to."],
        ["ri_id", "The relaxation data ID string."]
    ]
    copy._doc_desc = """
        This will copy relaxation data from one data pipe to another.  If the relaxation ID data string is not given then all relaxation data will be copied, otherwise only a specific data set will be copied.
        """
    copy._doc_examples = """
        To copy all relaxation data from pipe 'm1' to pipe 'm9', type one of:

        relax> relax_data.copy('m1', 'm9')
        relax> relax_data.copy(pipe_from='m1', pipe_to='m9')
        relax> relax_data.copy('m1', 'm9', None)
        relax> relax_data.copy(pipe_from='m1', pipe_to='m9', ri_id=None)

        To copy only the NOE relaxation data with the ID string of 'NOE_800' from 'm3' to 'm6', type
        one of:

        relax> relax_data.copy('m3', 'm6', 'NOE_800')
        relax> relax_data.copy(pipe_from='m3', pipe_to='m6', ri_id='NOE_800')
        """
    _build_doc(copy)


    def delete(self, ri_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.delete("
            text = text + "ri_id=" + repr(ri_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation data ID string')

        # Execute the functional code.
        relax_data.delete(ri_id=ri_id)

    # The function doc info.
    delete._doc_title = "Delete the data corresponding to the relaxation data ID string."
    delete._doc_title_short = "Relaxation data deletion."
    delete._doc_args = [
        ["ri_id", "The relaxation data ID string."]
    ]
    delete._doc_desc = """
        The relaxation data corresponding to the given relaxation data ID string will be removed from the current data pipe.
        """
    delete._doc_examples = """
        To delete the relaxation data corresponding to the ID 'NOE_600', type:

        relax> relax_data.delete('NOE_600')
        """
    _build_doc(delete)


    def display(self, ri_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.display("
            text = text + "ri_id=" + repr(ri_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation data ID string')

        # Execute the functional code.
        relax_data.display(ri_id=ri_id)

    # The function doc info.
    display._doc_title = "Display the data corresponding to the relaxation data ID string."
    display._doc_title_short = "Displaying relaxation data."
    display._doc_args = [
        ["ri_id", "The relaxation data ID string."]
    ]
    display._doc_examples = """
        To display the NOE relaxation data at 600 MHz with the ID string 'NOE_600', type:

        relax> relax_data.display('NOE_600')
        """
    _build_doc(display)


    def peak_intensity_type(self, ri_id=None, type=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.peak_intensity_type("
            text = text + "ri_id=" + repr(ri_id)
            text = text + ", type=" + repr(type) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation data ID string')
        arg_check.is_str(type, 'peak intensity type')

        # Execute the functional code.
        relax_data.peak_intensity_type(ri_id=ri_id, type=type)

    # The function doc info.
    peak_intensity_type._doc_title = "Specify the type of peak intensity measurement used - i.e. height or volume."
    peak_intensity_type._doc_title_short = "Setting peak intensity type."
    peak_intensity_type._doc_args = [
        ["ri_id", "The relaxation data ID string."],
        ["type", "The peak intensity type."]
    ]
    peak_intensity_type._doc_desc = """
        This is essential for BMRB data deposition.  It is used to specify whether peak heights or peak volumes were measured.  The two currently allowed values for the type argument are 'height' and 'volume'.
        """
    _build_doc(peak_intensity_type)


    def read(self, ri_id=None, ri_type=None, frq=None, file=None, dir=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.read("
            text = text + "ri_id=" + repr(ri_id)
            text = text + ", ri_type=" + repr(ri_type)
            text = text + ", frq=" + repr(frq)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spin_id_col=" + repr(spin_id_col)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", data_col=" + repr(data_col)
            text = text + ", error_col=" + repr(error_col)
            text = text + ", sep=" + repr(sep)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation ID string')
        arg_check.is_str(ri_type, 'relaxation type')
        arg_check.is_num(frq, 'frequency')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(spin_id_col, 'spin ID string column', can_be_none=True)
        arg_check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        arg_check.is_int(res_num_col, 'residue number column', can_be_none=True)
        arg_check.is_int(res_name_col, 'residue name column', can_be_none=True)
        arg_check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        arg_check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        arg_check.is_int(data_col, 'data column')
        arg_check.is_int(error_col, 'error column')
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        relax_data.read(ri_id=ri_id, ri_type=ri_type, frq=frq, file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep, spin_id=spin_id)

    # The function doc info.
    read._doc_title = "Read R1, R2, or NOE relaxation data from a file."
    read._doc_title_short = "Reading relaxation data from file."
    read._doc_args = [
        ["ri_id", "The relaxation data ID string.  This must be a unique identifier."],
        ["ri_type", "The relaxation data type, i.e. 'R1', 'R2', or 'NOE'."],
        ["frq", "The spectrometer frequency in Hz."],
        ["file", "The name of the file containing the relaxation data."],
        ["dir", "The directory where the file is located."],
        ["spin_id_col", "The spin ID string column (an alternative to the mol, res, and spin name and number columns)."],
        ["mol_name_col", "The molecule name column (alternative to the spin_id_col)."],
        ["res_num_col", "The residue number column (alternative to the spin_id_col)."],
        ["res_name_col", "The residue name column (alternative to the spin_id_col)."],
        ["spin_num_col", "The spin number column (alternative to the spin_id_col)."],
        ["spin_name_col", "The spin name column (alternative to the spin_id_col)."],
        ["data_col", "The relaxation data column."],
        ["error_col", "The experimental error column."],
        ["sep", "The column separator (the default is white space)."],
        ["spin_id", "The spin ID string to restrict the loading of data to certain spin subsets."]
    ]
    read._doc_desc = """
        The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number, residue name, spin number and/or spin name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID string can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.
        """
    read._doc_examples = """
        The following commands will read the protein NOE relaxation data collected at 600 MHz out of
        a file called 'noe.600.out' where the residue numbers, residue names, data, errors are in
        the first, second, third, and forth columns respectively.

        relax> relax_data.read('NOE_600', 'NOE', 599.7 * 1e6, 'noe.600.out', res_num_col=1,
                               res_name_col=2, data_col=3, error_col=4)
        relax> relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0 * 1e6, file='noe.600.out',
                               res_num_col=1, res_name_col=2, data_col=3, error_col=4)


        The following commands will read the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> relax_data.read('R2_800', 'R2', 8.0 * 1e8, 'r2.out', res_num_col=2, res_name_col=3,
                               data_col=5, error_col=6, sep=',')
        relax> relax_data.read(ri_id='R2_800', ri_type='R2', frq=8.0*1e8, file='r2.out',
                               res_num_col=2, res_name_col=3, data_col=5, error_col=6, sep=',')


        The following commands will read the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> relax_data.read('R1_300', 'R1', 300.1 * 1e6, 'r1.out', sep='%')
        """
    _build_doc(read)


    def temp_calibration(self, ri_id=None, method=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.temp_calibration("
            text = text + "ri_id=" + repr(ri_id)
            text = text + ", method=" + repr(method) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation data ID string')
        arg_check.is_str(method, 'temperature calibration method')

        # Execute the functional code.
        relax_data.temp_calibration(ri_id=ri_id, method=method)

    # The function doc info.
    temp_calibration._doc_title = "Specify the temperature calibration method used."
    temp_calibration._doc_title_short = "Setting temperature calibration method."
    temp_calibration._doc_args = [
        ["ri_id", "The relaxation data ID string."],
        ["method", "The calibration method."]
    ]
    temp_calibration._doc_desc = """
        This is essential for BMRB data deposition.  The currently allowed methods are:

            'methanol',
            'monoethylene glycol',
            'no calibration applied'.

        Other strings will be accepted if supplied.
        """
    _build_doc(temp_calibration)


    def temp_control(self, ri_id=None, method=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.temp_control("
            text = text + "ri_id=" + repr(ri_id)
            text = text + ", method=" + repr(method) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation data ID string')
        arg_check.is_str(method, 'temperature control method')

        # Execute the functional code.
        relax_data.temp_control(ri_id=ri_id, method=method)

    # The function doc info.
    temp_control._doc_title = "Specify the temperature control method used."
    temp_control._doc_title_short = "Setting temperature control method."
    temp_control._doc_args = [
        ["ri_id", "The relaxation data ID string."],
        ["method", "The control method."]
    ]
    temp_control._doc_desc = """
        This is essential for BMRB data deposition.  The currently allowed methods are:

            'single scan interleaving',
            'temperature compensation block',
            'single scan interleaving and temperature compensation block',
            'single fid interleaving',
            'single experiment interleaving',
            'no temperature control applied'.
        """
    _build_doc(temp_control)


    def write(self, ri_id=None, file=None, dir=None, bc=False, force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_data.write("
            text = text + "ri_id=" + repr(ri_id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", bc=" + repr(bc)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ri_id, 'relaxation data ID string')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(bc, 'back calculated data flag')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        relax_data.write(ri_id=ri_id, file=file, dir=dir, bc=bc, force=force)

    # The function doc info.
    write._doc_title = "Write relaxation data to a file."
    write._doc_title_short = "Relaxation data writing."
    write._doc_args = [
        ["ri_id", "The relaxation data ID string."],
        ["file", "The name of the file."],
        ["dir", "The directory name."],
        ["bc", "A flag which if True will cause the back calculated relaxation data to be written to file rather than the actual data."],
        ["force", "A flag which if True will cause the file to be overwritten."]
    ]
    write._doc_desc = """
        If no directory name is given, the file will be placed in the current working directory.  The relaxation data ID string is required for selecting which relaxation data to write to file.
        """
    _build_doc(write)
