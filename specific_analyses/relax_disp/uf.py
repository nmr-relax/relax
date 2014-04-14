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
from lib.errors import RelaxError
from pipe_control import pipes
from pipe_control.mol_res_spin import check_mol_res_spin_data, spin_loop
from specific_analyses.relax_disp.api import Relax_disp
from specific_analyses.relax_disp.checks import check_c_modules, check_exp_type, check_pipe_type
from specific_analyses.relax_disp.data import get_curve_type
from specific_analyses.relax_disp.variables import MODEL_LIST_FULL, MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_M61, MODEL_M61B, MODEL_MMQ_CR72, MODEL_MP05, MODEL_NOREX, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_R2EFF, MODEL_TAP03, MODEL_TP02, MODEL_TSMFK01
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


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
    for spin in spin_loop(skip_desel=True):
        # The model and parameter names.
        spin.model = model
        spin.params = params

        # Initialise the data structures (if needed).
        api_relax_disp.data_init(spin)


def select_model(model=MODEL_R2EFF):
    """Set up the model for the relaxation dispersion analysis.

    @keyword model: The relaxation dispersion analysis type.
    @type model:    str
    """

    # Data checks.
    pipes.test()
    check_pipe_type()
    check_mol_res_spin_data()
    check_exp_type()
    if model == MODEL_R2EFF:
        check_c_modules()

    # The curve type.
    curve_type = get_curve_type()

    # R2eff/R1rho model.
    if model == MODEL_R2EFF:
        print("R2eff/R1rho value and error determination.")
        if curve_type == 'exponential':
            params = ['r2eff', 'i0']
        else:
            params = ['r2eff']

    # The model for no chemical exchange relaxation.
    elif model == MODEL_NOREX:
        print("The model for no chemical exchange relaxation.")
        params = ['r2']

    # LM63 model.
    elif model == MODEL_LM63:
        print("The Luz and Meiboom (1963) 2-site fast exchange model.")
        params = ['r2', 'phi_ex', 'kex']

    # LM63 3-site model.
    elif model == MODEL_LM63_3SITE:
        print("The Luz and Meiboom (1963) 3-site fast exchange model.")
        params = ['r2', 'phi_ex_B', 'phi_ex_C', 'kB', 'kC']

    # Full CR72 model.
    elif model == MODEL_CR72_FULL:
        print("The full Carver and Richards (1972) 2-site model for all time scales.")
        params = ['r2a', 'r2b', 'pA', 'dw', 'kex']

    # Reduced CR72 model.
    elif model == MODEL_CR72:
        print("The reduced Carver and Richards (1972) 2-site model for all time scales, whereby the simplification R20A = R20B is assumed.")
        params = ['r2', 'pA', 'dw', 'kex']

    # IT99 model.
    elif model == MODEL_IT99:
        print("The Ishima and Torchia (1999) CPMG 2-site model for all time scales with pA >> pB.")
        params = ['r2', 'pA', 'dw', 'tex']

    # TSMFK01 model.
    elif model == MODEL_TSMFK01:
        print("The Tollinger et al. (2001) 2-site very-slow exchange model, range of microsecond to second time scale.")
        params = ['r2a', 'dw', 'k_AB']

    # Full NS CPMG 2-site 3D model.
    elif model == MODEL_NS_CPMG_2SITE_3D_FULL:
        print("The full numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors.")
        params = ['r2a', 'r2b', 'pA', 'dw', 'kex']

    # Reduced NS CPMG 2-site 3D model.
    elif model == MODEL_NS_CPMG_2SITE_3D:
        print("The reduced numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors, whereby the simplification R20A = R20B is assumed.")
        params = ['r2', 'pA', 'dw', 'kex']

    # NS CPMG 2-site expanded model.
    elif model == MODEL_NS_CPMG_2SITE_EXPANDED:
        print("The numerical solution for the 2-site Bloch-McConnell equations for CPMG data expanded using Maple by Nikolai Skrynnikov.")
        params = ['r2', 'pA', 'dw', 'kex']

    # Full NS CPMG 2-site star model.
    elif model == MODEL_NS_CPMG_2SITE_STAR_FULL:
        print("The full numerical solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices.")
        params = ['r2a', 'r2b', 'pA', 'dw', 'kex']

    # Reduced NS CPMG 2-site star model.
    elif model == MODEL_NS_CPMG_2SITE_STAR:
        print("The numerical reduced solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices, whereby the simplification R20A = R20B is assumed.")
        params = ['r2', 'pA', 'dw', 'kex']

    # M61 model.
    elif model == MODEL_M61:
        print("The Meiboom (1961) 2-site fast exchange model for R1rho-type experiments.")
        params = ['r2', 'phi_ex', 'kex']

    # M61 skew model.
    elif model == MODEL_M61B:
        print("The Meiboom (1961) on-resonance 2-site model with skewed populations (pA >> pB) for R1rho-type experiments.")
        params = ['r2', 'pA', 'dw', 'kex']

    # DPL94 model.
    elif model == MODEL_DPL94:
        print("The Davis, Perlman and London (1994) 2-site fast exchange model for R1rho-type experiments.")
        params = ['r2', 'phi_ex', 'kex']

    # TP02 model.
    elif model == MODEL_TP02:
        print("The Trott and Palmer (2002) off-resonance 2-site model for R1rho-type experiments.")
        params = ['r2', 'pA', 'dw', 'kex']

    # TAP03 model.
    elif model == MODEL_TAP03:
        print("The Trott, Abergel and Palmer (2003) off-resonance 2-site model for R1rho-type experiments.")
        params = ['r2', 'pA', 'dw', 'kex']

    # MP05 model.
    elif model == MODEL_MP05:
        print("The Miloushev and Palmer (2005) off-resonance 2-site model for R1rho-type experiments.")
        params = ['r2', 'pA', 'dw', 'kex']

    # Reduced NS R1rho 2-site model.
    elif model == MODEL_NS_R1RHO_2SITE:
        print("The reduced numerical solution for the 2-site Bloch-McConnell equations for R1rho data using 3D magnetisation vectors, whereby the simplification R20A = R20B is assumed.")
        params = ['r2', 'pA', 'dw', 'kex']

    # NS R1rho CPMG 3-site model.
    elif model == MODEL_NS_R1RHO_3SITE:
        print("The numerical solution for the 3-site Bloch-McConnell equations for R1rho data using 3D magnetisation vectors whereby the simplification R20A = R20B = R20C is assumed.")
        params = ['r2', 'pA', 'dw_AB', 'kex_AB', 'pB', 'dw_BC', 'kex_BC', 'kex_AC']

    # NS R1rho CPMG 3-site linearised model.
    elif model == MODEL_NS_R1RHO_3SITE_LINEAR:
        print("The numerical solution for the 3-site Bloch-McConnell equations for R1rho data using 3D magnetisation vectors linearised with kAC = kCA = 0 whereby the simplification R20A = R20B = R20C is assumed.")
        params = ['r2', 'pA', 'dw_AB', 'kex_AB', 'pB', 'dw_BC', 'kex_BC']

    # MMQ CR72 model.
    elif model == MODEL_MMQ_CR72:
        print("The Carver and Richards (1972) 2-site model for all time scales expanded for MMQ CPMG data by Korzhnev et al., 2004.")
        params = ['r2', 'pA', 'dw', 'dwH', 'kex']

    # NS MQ CPMG 2-site model.
    elif model == MODEL_NS_MMQ_2SITE:
        print("The reduced numerical solution for the 2-site Bloch-McConnell equations for MQ CPMG data using 3D magnetisation vectors, whereby the simplification R20A = R20B is assumed.")
        params = ['r2', 'pA', 'dw', 'dwH', 'kex']

    # NS MMQ CPMG 3-site model.
    elif model == MODEL_NS_MMQ_3SITE:
        print("The numerical solution for the 3-site Bloch-McConnell equations for MMQ CPMG data whereby the simplification R20A = R20B = R20C is assumed.")
        params = ['r2', 'pA', 'dw_AB', 'dwH_AB', 'kex_AB', 'pB', 'dw_BC', 'dwH_BC', 'kex_BC', 'kex_AC']

    # NS MMQ CPMG 3-site linearised model.
    elif model == MODEL_NS_MMQ_3SITE_LINEAR:
        print("The numerical solution for the 3-site Bloch-McConnell equations for MMQ CPMG data linearised with kAC = kCA = 0 whereby the simplification R20A = R20B = R20C is assumed.")
        params = ['r2', 'pA', 'dw_AB', 'dwH_AB', 'kex_AB', 'pB', 'dw_BC', 'dwH_BC', 'kex_BC']

    # Invalid model.
    else:
        raise RelaxError("The model '%s' must be one of %s." % (model, MODEL_LIST_FULL))

    # Set up the model.
    model_setup(model, params)
