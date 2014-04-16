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
"""The model-free analysis parameter functions."""

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError, RelaxNoTensorError
from pipe_control import diffusion_tensor
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop


def determine_model_type():
    """Determine the global model type.

    @return:    The name of the model type, which will be one of 'all', 'diff', 'mf', or 'local_tm'.  If all parameters are fixed (and no spins selected), None is returned.
    @rtype:     str or None
    """

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # If there is a local tm, fail if not all residues have a local tm parameter.
    local_tm = False
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # No params.
        if not hasattr(spin, 'params') or not spin.params:
            continue

        # Local tm.
        if not local_tm and 'local_tm' in spin.params:
            local_tm = True

        # Inconsistencies.
        elif local_tm and not 'local_tm' in spin.params:
            raise RelaxError("All spins must either have a local tm parameter or not.")

    # Check if any model-free parameters are allowed to vary.
    mf_all_fixed = True
    mf_all_deselected = True
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # At least one spin is selected.
        mf_all_deselected = False

        # Test the fixed flag.
        if not hasattr(spin, 'fixed'):
            mf_all_fixed = False
            break
        if not spin.fixed:
            mf_all_fixed = False
            break

    # No spins selected?!?
    if mf_all_deselected:
        # All parameters fixed!
        if not hasattr(cdp, 'diff_tensor') or cdp.diff_tensor.fixed:
            return None

        return 'diff'

    # Local tm.
    if local_tm:
        return 'local_tm'

    # Test if the diffusion tensor data is loaded.
    if not diffusion_tensor.diff_data_exists():
        # Catch when the local tm value is set but not in the parameter list.
        for spin in spin_loop():
            if hasattr(spin, 'local_tm') and spin.local_tm != None and not 'local_tm' in spin.params:
                raise RelaxError("The local tm value is set but not located in the model parameter list.")

        # Normal error.
        raise RelaxNoTensorError('diffusion')

    # 'diff' model type.
    if mf_all_fixed:
        # All parameters fixed!
        if cdp.diff_tensor.fixed:
            return None

        return 'diff'

    # 'mf' model type.
    if cdp.diff_tensor.fixed:
        return 'mf'

    # 'all' model type.
    else:
        return 'all'


def model_map(model):
    """Return the equation name and parameter list corresponding to the given model.

    @param model:   The model-free model.
    @type model:    str
    @return:        The equation type (either 'mf_orig' or 'mf_ext') and the model-free parameter list corresponding to the model.
    @rtype:         str, list
    """

    # Block 1.
    if model == 'm0':
        equation = 'mf_orig'
        params = []
    elif model == 'm1':
        equation = 'mf_orig'
        params = ['s2']
    elif model == 'm2':
        equation = 'mf_orig'
        params = ['s2', 'te']
    elif model == 'm3':
        equation = 'mf_orig'
        params = ['s2', 'rex']
    elif model == 'm4':
        equation = 'mf_orig'
        params = ['s2', 'te', 'rex']
    elif model == 'm5':
        equation = 'mf_ext'
        params = ['s2f', 's2', 'ts']
    elif model == 'm6':
        equation = 'mf_ext'
        params = ['s2f', 'tf', 's2', 'ts']
    elif model == 'm7':
        equation = 'mf_ext'
        params = ['s2f', 's2', 'ts', 'rex']
    elif model == 'm8':
        equation = 'mf_ext'
        params = ['s2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm9':
        equation = 'mf_orig'
        params = ['rex']

    # Block 2.
    elif model == 'm10':
        equation = 'mf_orig'
        params = ['csa']
    elif model == 'm11':
        equation = 'mf_orig'
        params = ['csa', 's2']
    elif model == 'm12':
        equation = 'mf_orig'
        params = ['csa', 's2', 'te']
    elif model == 'm13':
        equation = 'mf_orig'
        params = ['csa', 's2', 'rex']
    elif model == 'm14':
        equation = 'mf_orig'
        params = ['csa', 's2', 'te', 'rex']
    elif model == 'm15':
        equation = 'mf_ext'
        params = ['csa', 's2f', 's2', 'ts']
    elif model == 'm16':
        equation = 'mf_ext'
        params = ['csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'm17':
        equation = 'mf_ext'
        params = ['csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'm18':
        equation = 'mf_ext'
        params = ['csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm19':
        equation = 'mf_orig'
        params = ['csa', 'rex']

    # Block 3.
    elif model == 'm20':
        equation = 'mf_orig'
        params = ['r']
    elif model == 'm21':
        equation = 'mf_orig'
        params = ['r', 's2']
    elif model == 'm22':
        equation = 'mf_orig'
        params = ['r', 's2', 'te']
    elif model == 'm23':
        equation = 'mf_orig'
        params = ['r', 's2', 'rex']
    elif model == 'm24':
        equation = 'mf_orig'
        params = ['r', 's2', 'te', 'rex']
    elif model == 'm25':
        equation = 'mf_ext'
        params = ['r', 's2f', 's2', 'ts']
    elif model == 'm26':
        equation = 'mf_ext'
        params = ['r', 's2f', 'tf', 's2', 'ts']
    elif model == 'm27':
        equation = 'mf_ext'
        params = ['r', 's2f', 's2', 'ts', 'rex']
    elif model == 'm28':
        equation = 'mf_ext'
        params = ['r', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm29':
        equation = 'mf_orig'
        params = ['r', 'rex']

    # Block 4.
    elif model == 'm30':
        equation = 'mf_orig'
        params = ['r', 'csa']
    elif model == 'm31':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2']
    elif model == 'm32':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2', 'te']
    elif model == 'm33':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2', 'rex']
    elif model == 'm34':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2', 'te', 'rex']
    elif model == 'm35':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 's2', 'ts']
    elif model == 'm36':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'm37':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'm38':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm39':
        equation = 'mf_orig'
        params = ['r', 'csa', 'rex']


    # Preset models with local correlation time.
    ############################################

    # Block 1.
    elif model == 'tm0':
        equation = 'mf_orig'
        params = ['local_tm']
    elif model == 'tm1':
        equation = 'mf_orig'
        params = ['local_tm', 's2']
    elif model == 'tm2':
        equation = 'mf_orig'
        params = ['local_tm', 's2', 'te']
    elif model == 'tm3':
        equation = 'mf_orig'
        params = ['local_tm', 's2', 'rex']
    elif model == 'tm4':
        equation = 'mf_orig'
        params = ['local_tm', 's2', 'te', 'rex']
    elif model == 'tm5':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 's2', 'ts']
    elif model == 'tm6':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm7':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm8':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm9':
        equation = 'mf_orig'
        params = ['local_tm', 'rex']

    # Block 2.
    elif model == 'tm10':
        equation = 'mf_orig'
        params = ['local_tm', 'csa']
    elif model == 'tm11':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2']
    elif model == 'tm12':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2', 'te']
    elif model == 'tm13':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2', 'rex']
    elif model == 'tm14':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2', 'te', 'rex']
    elif model == 'tm15':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 's2', 'ts']
    elif model == 'tm16':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm17':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm18':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm19':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 'rex']

    # Block 3.
    elif model == 'tm20':
        equation = 'mf_orig'
        params = ['local_tm', 'r']
    elif model == 'tm21':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2']
    elif model == 'tm22':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2', 'te']
    elif model == 'tm23':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2', 'rex']
    elif model == 'tm24':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2', 'te', 'rex']
    elif model == 'tm25':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 's2', 'ts']
    elif model == 'tm26':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm27':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm28':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm29':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'rex']

    # Block 4.
    elif model == 'tm30':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa']
    elif model == 'tm31':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2']
    elif model == 'tm32':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2', 'te']
    elif model == 'tm33':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2', 'rex']
    elif model == 'tm34':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2', 'te', 'rex']
    elif model == 'tm35':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 's2', 'ts']
    elif model == 'tm36':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm37':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm38':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm39':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 'rex']

    # Invalid model.
    else:
        raise RelaxError("The model '%s' is invalid." % model)

    # Return the values.
    return equation, params
