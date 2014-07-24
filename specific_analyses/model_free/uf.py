###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The model-free analysis user functions."""

# Python module imports.
from re import match

# relax module imports.
from lib.errors import RelaxError, RelaxFuncSetupError, RelaxNoSequenceError, RelaxTensorError
from pipe_control import pipes
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
import specific_analyses
from specific_analyses.model_free.api import Model_free
from specific_analyses.model_free.model import model_map
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container

# The API object.
api_model_free = Model_free()


# Classic style documentation.
classic_style_doc = Desc_container("Model-free classic style")
classic_style_doc.add_paragraph("Creator:  Edward d'Auvergne")
classic_style_doc.add_paragraph("Argument string:  \"classic\"")
classic_style_doc.add_paragraph("Description:  The classic style draws the backbone of a protein in a cylindrical bond style.  Rather than colouring the amino acids to which the NH bond belongs, the three covalent bonds of the peptide bond from Ca to Ca in which the NH bond is located are coloured.  Deselected residues are shown as black lines.")
classic_style_doc.add_paragraph("Supported data types:")
table = uf_tables.add_table(label="table: model-free macro classic style", caption="The model-free classic style for mapping model spin specific data onto 3D molecular structures using either PyMOL or Molmol.", caption_short="The model-free classic style for PyMOL and Molmol data mapping.")
table.add_headings(["Data type", "String", "Description"])
table.add_row(["S2.", "'s2'", "The standard model-free order parameter, equal to S2f.S2s for the two timescale models.  The default colour gradient starts at 'yellow' and ends at 'red'."])
table.add_row(["S2f.", "'s2f'", "The order parameter of the faster of two internal motions.  Residues which are described by model-free models m1 to m4, the single timescale models, are illustrated as white neon bonds.  The default colour gradient is the same as that for the S2 data type."])
table.add_row(["S2s.", "'s2s'", "The order parameter of the slower of two internal motions.  This functions exactly as S2f except that S2s is plotted instead."])
table.add_row(["Amplitude of fast motions.", "'amp_fast'", "Model independent display of the amplite of fast motions.  For residues described by model-free models m5 to m8, the value plotted is that of S2f.  However, for residues described by models m1 to m4, what is shown is dependent on the timescale of the motions.  This is because these single timescale models can, at times, be perfect approximations to the more complex two timescale models.  Hence if te is less than 200 ps, S2 is plotted.  Otherwise the peptide bond is coloured white.  The default colour gradient  is the same as that for S2."])
table.add_row(["Amplitude of slow motions.", "'amp_slow'", "Model independent display of the amplite of slow motions, arbitrarily defined as motions slower than 200 ps.  For residues described by model-free models m5 to m8, the order parameter S2 is plotted if ts > 200 ps.  For models m1 to m4, S2 is plotted if te > 200 ps.  The default colour gradient is the same as that for S2."])
table.add_row(["te.", "'te'", "The correlation time, te.  The default colour gradient starts at 'turquoise' and ends at 'blue'."])
table.add_row(["tf.", "'tf'", "The correlation time, tf.  The default colour gradient is the same as that of te."])
table.add_row(["ts.", "'ts'", "The correlation time, ts.  The default colour gradient starts at 'blue' and ends at 'black'."])
table.add_row(["Timescale of fast motions", "'time_fast'", "Model independent display of the timescale of fast motions.  For models m5 to m8, only the parameter tf is plotted.  For models m2 and m4, the parameter te is plotted only if it is less than 200 ps.  All other residues are assumed to have a correlation time of zero.  The default colour gradient is the same as that of te."])
table.add_row(["Timescale of slow motions", "'time_slow'", "Model independent display of the timescale of slow motions.  For models m5 to m8, only the parameter ts is plotted.  For models m2 and m4, the parameter te is plotted only if it is greater than 200 ps.  All other residues are coloured white.  The default colour gradient is the same as that of ts."])
table.add_row(["Chemical exchange", "'rex'", "The chemical exchange, Rex.  Residues which experience no chemical exchange are coloured white.  The default colour gradient starts at 'yellow' and finishes at 'red'."])
classic_style_doc.add_table(table.label)

# Model elimination documentation.
eliminate_doc = []
eliminate_doc.append(Desc_container("Local tm model elimination rule"))
eliminate_doc[-1].add_paragraph("The local tm, in some cases, may exceed the value expected for a global correlation time. Generally the tm value will be stuck at the upper limit defined for the parameter.  These models are eliminated using the rule:")
eliminate_doc[-1].add_verbatim("    tm >= c")
eliminate_doc[-1].add_paragraph("The default value of c is 50 ns, although this can be overridden by supplying the value (in seconds) as the first element of the args tuple.")
eliminate_doc.append(Desc_container("Internal correlation times {te, tf, ts} model elimination rules"))
eliminate_doc[-1].add_paragraph("These parameters may experience the same problem as the local tm in that the model fails and the parameter value is stuck at the upper limit.  These parameters are constrained using the formula (te, tf, ts <= 2tm).  These failed models are eliminated using the rule:")
eliminate_doc[-1].add_verbatim("    te, tf, ts >= c . tm.")
eliminate_doc[-1].add_paragraph("The default value of c is 1.5.  Because of round-off errors and the constraint algorithm, setting c to 2 will result in no models being eliminated as the minimised parameters will always be less than 2tm.  The value can be changed by supplying the value as the second element of the tuple.")
eliminate_doc.append(Desc_container("Arguments"))
eliminate_doc[-1].add_paragraph("The 'args' argument must be a tuple of length 2, the elements of which must be numbers.  For example, to eliminate models which have a local tm value greater than 25 ns and models with internal correlation times greater than 1.5 times tm, set 'args' to (25 * 1e-9, 1.5).")


def create_model(model=None, equation=None, params=None, spin_id=None):
    """Function for creating a custom model-free model.

    @param model:       The name of the model.
    @type model:        str
    @param equation:    The equation type to use.  The 3 allowed types are:  'mf_orig' for the original model-free equations with parameters {s2, te}; 'mf_ext' for the extended model-free equations with parameters {s2f, tf, s2, ts}; and 'mf_ext2' for the extended model-free equations with parameters {s2f, tf, s2s, ts}.
    @type equation:     str
    @param params:      A list of the parameters to include in the model.  The allowed parameter names includes those for the equation type as well as chemical exchange 'rex', the bond length 'r', and the chemical shift anisotropy 'csa'.
    @type params:       list of str
    @param spin_id:     The spin identification string.
    @type spin_id:      str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the pipe type is 'mf'.
    function_type = pipes.get_type()
    if function_type != 'mf':
        raise RelaxFuncSetupError(specific_analyses.get_string(function_type))

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Check the validity of the model-free equation type.
    valid_types = ['mf_orig', 'mf_ext', 'mf_ext2']
    if not equation in valid_types:
        raise RelaxError("The model-free equation type argument " + repr(equation) + " is invalid and should be one of " + repr(valid_types) + ".")

    # Check the validity of the parameter array.
    s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
    for i in range(len(params)):
        # Invalid parameter flag.
        invalid_param = 0

        # S2.
        if params[i] == 's2':
            # Does the array contain more than one instance of S2.
            if s2:
                invalid_param = 1
            s2 = 1

            # Does the array contain S2s.
            s2s_flag = 0
            for j in range(len(params)):
                if params[j] == 's2s':
                    s2s_flag = 1
            if s2s_flag:
                invalid_param = 1

        # te.
        elif params[i] == 'te':
            # Does the array contain more than one instance of te and has the extended model-free formula been selected.
            if equation == 'mf_ext' or te:
                invalid_param = 1
            te = 1

            # Does the array contain the parameter S2.
            s2_flag = 0
            for j in range(len(params)):
                if params[j] == 's2':
                    s2_flag = 1
            if not s2_flag:
                invalid_param = 1

        # S2f.
        elif params[i] == 's2f':
            # Does the array contain more than one instance of S2f and has the original model-free formula been selected.
            if equation == 'mf_orig' or s2f:
                invalid_param = 1
            s2f = 1

        # S2s.
        elif params[i] == 's2s':
            # Does the array contain more than one instance of S2s and has the original model-free formula been selected.
            if equation == 'mf_orig' or s2s:
                invalid_param = 1
            s2s = 1

        # tf.
        elif params[i] == 'tf':
            # Does the array contain more than one instance of tf and has the original model-free formula been selected.
            if equation == 'mf_orig' or tf:
                invalid_param = 1
            tf = 1

            # Does the array contain the parameter S2f.
            s2f_flag = 0
            for j in range(len(params)):
                if params[j] == 's2f':
                    s2f_flag = 1
            if not s2f_flag:
                invalid_param = 1

        # ts.
        elif params[i] == 'ts':
            # Does the array contain more than one instance of ts and has the original model-free formula been selected.
            if equation == 'mf_orig' or ts:
                invalid_param = 1
            ts = 1

            # Does the array contain the parameter S2 or S2s.
            flag = 0
            for j in range(len(params)):
                if params[j] == 's2' or params[j] == 's2f':
                    flag = 1
            if not flag:
                invalid_param = 1

        # Rex.
        elif params[i] == 'rex':
            if rex:
                invalid_param = 1
            rex = 1

        # Interatomic distances.
        elif params[i] == 'r':
            if r:
                invalid_param = 1
            r = 1

        # CSA.
        elif params[i] == 'csa':
            if csa:
                invalid_param = 1
            csa = 1

        # Unknown parameter.
        else:
            raise RelaxError("The parameter " + params[i] + " is not supported.")

        # The invalid parameter flag is set.
        if invalid_param:
            raise RelaxError("The parameter array " + repr(params) + " contains an invalid combination of parameters.")

    # Set up the model.
    model_setup(model, equation, params, spin_id)


def delete():
    """Delete all the model-free data."""

    # Test if the current pipe exists.
    pipes.test()

    # Test if the pipe type is set to 'mf'.
    function_type = pipes.get_type()
    if function_type != 'mf':
        raise RelaxFuncSetupError(specific_analyses.setup.get_string(function_type))

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Get all data structure names.
    names = api_model_free.data_names(scope='spin')

    # Loop over the spins.
    for spin in spin_loop():
        # Loop through the data structure names.
        for name in names:
            # Skip the data structure if it does not exist.
            if not hasattr(spin, name):
                continue

            # Delete the data.
            delattr(spin, name)


def model_setup(model=None, equation=None, params=None, spin_id=None):
    """Function for updating various data structures depending on the model selected.

    @param model:       The name of the model.
    @type model:        str
    @param equation:    The equation type to use.  The 3 allowed types are:  'mf_orig' for the original model-free equations with parameters {s2, te}; 'mf_ext' for the extended model-free equations with parameters {s2f, tf, s2, ts}; and 'mf_ext2' for the extended model-free equations with parameters {s2f, tf, s2s, ts}.
    @type equation:     str
    @param params:      A list of the parameters to include in the model.  The allowed parameter names includes those for the equation type as well as chemical exchange 'rex', the bond length 'r', and the chemical shift anisotropy 'csa'.
    @type params:       list of str
    @param spin_id:     The spin identification string.
    @type spin_id:      str
    """

    # Test that no diffusion tensor exists if local tm is a parameter in the model.
    if params:
        for param in params:
            if param == 'local_tm' and hasattr(pipes.get_pipe(), 'diff_tensor'):
                raise RelaxTensorError('diffusion')

    # Loop over the sequence.
    for spin, spin_id in spin_loop(spin_id, return_id=True):
        # Initialise the data structures (if needed).
        api_model_free.data_init(spin_id)

        # Model-free model, equation, and parameter types.
        spin.model = model
        spin.equation = equation
        spin.params = params


def remove_tm(spin_id=None):
    """Remove local tm from the set of model-free parameters for the given spins.

    @param spin_id: The spin identification string.
    @type spin_id:  str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the pipe type is 'mf'.
    function_type = pipes.get_type()
    if function_type != 'mf':
        raise RelaxFuncSetupError(specific_analyses.get_string(function_type))

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Loop over the spins.
    for spin in spin_loop(spin_id):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Test if a local tm parameter exists.
        if not hasattr(spin, 'params') or not 'local_tm' in spin.params:
            continue

        # Remove tm.
        spin.params.remove('local_tm')

        # Model name.
        if match('^tm', spin.model):
            spin.model = spin.model[1:]

        # Delete the local tm variable.
        del spin.local_tm

        # Set all the minimisation stats to None.
        spin.chi2 = None
        spin.iter = None
        spin.f_count = None
        spin.g_count = None
        spin.h_count = None
        spin.warning = None

    # Set the global minimisation stats to None.
    cdp.chi2 = None
    cdp.iter = None
    cdp.f_count = None
    cdp.g_count = None
    cdp.h_count = None
    cdp.warning = None


def select_model(model=None, spin_id=None):
    """Function for the selection of a preset model-free model.

    @param model:   The name of the model.
    @type model:    str
    @param spin_id: The spin identification string.
    @type spin_id:  str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the pipe type is 'mf'.
    function_type = pipes.get_type()
    if function_type != 'mf':
        raise RelaxFuncSetupError(specific_analyses.get_string(function_type))

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Obtain the model info.
    equation, params = model_map(model)

    # Set up the model.
    model_setup(model, equation, params, spin_id)
