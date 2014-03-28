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
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container

# The API object.
api_model_free = Model_free()


# Default value documentation.
default_value_doc = Desc_container("Model-free default values")
table = uf_tables.add_table(label="table: mf default values", caption="Model-free default values.")
table.add_headings(["Data type", "Object name", "Value"])
table.add_row(["Local tm", "'local_tm'", "10 * 1e-9"])
table.add_row(["Order parameters S2, S2f, and S2s", "'s2', 's2f', 's2s'", "0.8"])
table.add_row(["Correlation time te", "'te'", "100 * 1e-12"])
table.add_row(["Correlation time tf", "'tf'", "10 * 1e-12"])
table.add_row(["Correlation time ts", "'ts'", "1000 * 1e-12"])
table.add_row(["Chemical exchange relaxation", "'rex'", "0.0"])
table.add_row(["CSA", "'csa'", "-172 * 1e-6"])
default_value_doc.add_table(table.label)

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

# Data name documentation.
return_data_name_doc = Desc_container("Model-free data type string matching patterns")
table = uf_tables.add_table(label="table: mf data type patterns", caption="Model-free data type string matching patterns.")
table.add_headings(["Data type", "Object name"])
table.add_row(["Local tm", "'local_tm'"])
table.add_row(["Order parameter S2", "'s2'"])
table.add_row(["Order parameter S2f", "'s2f'"])
table.add_row(["Order parameter S2s", "'s2s'"])
table.add_row(["Correlation time te", "'te'"])
table.add_row(["Correlation time tf", "'tf'"])
table.add_row(["Correlation time ts", "'ts'"])
table.add_row(["Chemical exchange", "'rex'"])
table.add_row(["CSA", "'csa'"])
return_data_name_doc.add_table(table.label)

# Parameter setting documentation.
set_doc = Desc_container("Model-free set details")
set_doc.add_paragraph("Setting a parameter value may have no effect depending on which model-free model is chosen, for example if S2f values and S2s values are set but the run corresponds to model-free model 'm4' then, because these data values are not parameters of the model, they will have no effect.")
set_doc.add_paragraph("Note that the Rex values are scaled quadratically with field strength and should be supplied as a field strength independent value.  Use the following formula to get the correct value:")
set_doc.add_verbatim("    value = rex / (2.0 * pi * frequency) ** 2")
set_doc.add_paragraph("where:")
set_doc.add_list_element("rex is the chemical exchange value for the current frequency.")
set_doc.add_list_element("pi is in the namespace of relax, ie just type 'pi'.")
set_doc.add_list_element("frequency is the proton frequency corresponding to the data.")

# Parameter writing documentation.
write_doc = Desc_container("Model-free parameter writing details")
write_doc.add_paragraph("For the model-free theory, it is assumed that Rex values are scaled quadratically with field strength.  The values will seem quite small as they will be written out as a field strength independent value.  Hence please use the following formula to convert the value to that expected for a given magnetic field strength:")
write_doc.add_verbatim("    Rex = value * (2.0 * pi * frequency) ** 2")
write_doc.add_paragraph("The frequency is that of the proton in Hertz.")


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
    for spin in spin_loop(spin_id):
        # Initialise the data structures (if needed).
        api_model_free.data_init(spin)

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
    equation, params = api_model_free._model_map(model)

    # Set up the model.
    model_setup(model, equation, params, spin_id)
