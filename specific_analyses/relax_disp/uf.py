###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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
"""The relaxation dispersion API object."""

# relax module imports.
from lib.dispersion.variables import MODEL_DESC, MODEL_LIST_FULL, MODEL_PARAMS, MODEL_R2EFF
from lib.errors import RelaxError
from pipe_control.mol_res_spin import check_mol_res_spin_data, spin_loop
from pipe_control.pipes import check_pipe
from specific_analyses.relax_disp.api import Relax_disp
from specific_analyses.relax_disp.checks import check_c_modules, check_exp_type, check_pipe_type
from specific_analyses.relax_disp.data import get_curve_type


# The API object.
api_relax_disp = Relax_disp()


def cluster(cluster_id=None, spin_id=None):
    """Define spin clustering.

    @keyword cluster_id:    The cluster ID string.
    @type cluster_id:       str
    @keyword spin_id:       The spin ID string for the spin or group of spins to add to the cluster.
    @type spin_id:          str
    """

    # Initialise.
    if not hasattr(cdp, 'clustering'):
        # Create the dictionary.
        cdp.clustering = {}
        cdp.clustering['free spins'] = []

        # Add all spin IDs to the cluster.
        for spin, id in spin_loop(return_id=True):
            cdp.clustering['free spins'].append(id)

    # Add the key.
    if cluster_id not in cdp.clustering:
        cdp.clustering[cluster_id] = []

    # Loop over the spins to add to the cluster.
    for spin, id in spin_loop(selection=spin_id, return_id=True):
        # First remove the ID from all clusters.
        for key in cdp.clustering.keys():
            if id in cdp.clustering[key]:
                cdp.clustering[key].pop(cdp.clustering[key].index(id))

        # Then add the ID to the cluster.
        cdp.clustering[cluster_id].append(id)

    # Clean up - delete any empty clusters (except the free spins).
    clean = []
    for key in cdp.clustering.keys():
        if key == 'free spins':
            continue
        if cdp.clustering[key] == []:
            clean.append(key)
    for key in clean:
        cdp.clustering.pop(key)


def cluster_ids():
    """Return the current list of cluster ID strings.

    @return:    The list of cluster IDs.
    @rtype:     list of str
    """

    # Initialise.
    ids = ['free spins']

    # Add the defined IDs.
    if hasattr(cdp, 'clustering'):
        for key in list(cdp.clustering.keys()):
            if key not in ids:
                ids.append(key)

    # Return the IDs.
    return ids


def model_setup(model, params):
    """Update various model specific data structures.

    @param model:   The relaxation dispersion curve type.
    @type model:    str
    @param params:  A list consisting of the model parameters.
    @type params:   list of str
    """

    # The model group.
    if model == MODEL_R2EFF:
        cdp.model_type = 'R2eff'
    else:
        cdp.model_type = 'disp'

    # Loop over the sequence.
    for spin, spin_id in spin_loop(skip_desel=True, return_id=True):
        # The model and parameter names.
        spin.model = model
        spin.params = params

        # Initialise the data structures (if needed).
        api_relax_disp.data_init(spin_id)


def r1_fit(fit=True):
    """Set the R1 optimisation flag.

    @keyword fit:   The R1 optimisation flag.
    @type fit:      bool
    """

    # Simply store the value for later use.
    cdp.r1_fit = fit


def select_model(model=MODEL_R2EFF):
    """Set up the model for the relaxation dispersion analysis.

    @keyword model: The relaxation dispersion analysis type.
    @type model:    str
    """

    # Data checks.
    check_pipe()
    check_pipe_type()
    check_mol_res_spin_data()
    check_exp_type()

    # The curve type.
    curve_type = get_curve_type()
    if model == MODEL_R2EFF and curve_type == 'exponential':
        check_c_modules()

    # Invalid model.
    if model not in MODEL_DESC:
        raise RelaxError("The model '%s' must be one of %s." % (model, MODEL_LIST_FULL))

    # R2eff/R1rho model.
    if model == MODEL_R2EFF:
        if curve_type == 'exponential':
            params = ['r2eff', 'i0']
        else:
            params = ['r2eff']

    # All other models.
    else:
        params = MODEL_PARAMS[model]

    # Printout.
    print(MODEL_DESC[model])

    # Set up the model.
    model_setup(model, params)
