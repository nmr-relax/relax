###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""The model-free analysis BMRB functions."""

# Python module imports.
from math import pi

# relax module imports.
from lib.errors import RelaxError
from pipe_control import bmrb, mol_res_spin
from specific_analyses.model_free.model import model_map


def from_bmrb_model(name=None):
    """The model-free model name to BMRB name mapping.

    @keyword name:  The BMRB model name.
    @type name:     str
    @return:        The corresponding model-free model name.
    @rtype:         str
    """

    # The same name.
    if name in ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']:
        return name

    # Conversion of Modelfree4 (and relax) model numbers.
    if name in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        return 'm' + name

    # The BMRB to model-free model name map.
    map = {'':                         'm0',
           'S2':                       'm1',
           'S2, te':                   'm2',
           'S2, Rex':                  'm3',
           'S2, te, Rex':              'm4',
           'S2, te, S2f':              'm5',
           'S2f, S2, ts':              'm5',
           'S2f, tf, S2, ts':          'm6',
           'S2f, S2, ts, Rex':         'm7',
           'S2f, tf, S2, ts, Rex':     'm8',
           'Rex':                      'm9',
           'tm':                       'tm0',
           'tm, S2':                   'tm1',
           'tm, S2, te':               'tm2',
           'tm, S2, Rex':              'tm3',
           'tm, S2, te, Rex':          'tm4',
           'tm, S2f, S2, ts':          'tm5',
           'tm, S2f, tf, S2, ts':      'tm6',
           'tm, S2f, S2, ts, Rex':     'tm7',
           'tm, S2f, tf, S2, ts, Rex': 'tm8',
           'tm, Rex':                  'tm9'
    }

    # Loop over the dictionary.
    for item in map.items():
        # Normal match.
        if item[0] == name:
            return item[1]

        # No whitespace.
        if item[0].replace(' ', '') == name:
            return item[1]

    # Should not be here!
    if name:
        raise RelaxError("The BMRB model-free model '%s' is unknown." % name)


def sf_csa_read(star):
    """Place the CSA data from the saveframe records into the spin container.

    @param star:    The NMR-STAR dictionary object.
    @type star:     NMR_STAR instance
    """

    # Get the entities.
    for data in star.chem_shift_anisotropy.loop():
        # The number of spins.
        N = bmrb.num_spins(data)

        # No data in the saveframe.
        if N == 0:
            continue

        # The molecule names.
        mol_names = bmrb.molecule_names(data, N)

        # Loop over the spins.
        for i in range(len(data['data_ids'])):
            # Generate a spin ID.
            spin_id = mol_res_spin.generate_spin_id_unique(mol_name=mol_names[i], res_num=data['res_nums'][i], spin_name=data['atom_names'][i])

            # Obtain the spin.
            spin = mol_res_spin.return_spin(spin_id)

            # The CSA value (converted from ppm).
            setattr(spin, 'csa', data['csa'][i] * 1e-6)


def sf_model_free_read(star, sample_conditions=None):
    """Fill the spin containers with the model-free data from the saveframe records.

    @param star:                The NMR-STAR dictionary object.
    @type star:                 NMR_STAR instance
    @keyword sample_conditions: The sample condition label to read.  Only one sample condition can be read per data pipe.
    @type sample_conditions:    None or str
    """

    # The list of model-free parameters (both bmrblib names and relax names).
    mf_bmrb_key = ['bond_length', 'local_tm', 's2', 's2f', 's2s', 'te', 'tf', 'ts', 'rex', 'chi2']
    mf_params =   ['r', 'local_tm', 's2', 's2f', 's2s', 'te', 'tf', 'ts', 'rex', 'chi2']

    # Get the entities.
    for data in star.model_free.loop():
        # Sample conditions do not match (remove the $ sign).
        if 'sample_cond_list_label' in data and sample_conditions and data['sample_cond_list_label'].replace('$', '') != sample_conditions:
            continue

        # Global data.
        if 'global_chi2' in data:
            setattr(cdp, 'chi2', data['global_chi2'])

        # The number of spins.
        N = bmrb.num_spins(data)

        # No data in the saveframe.
        if N == 0:
            continue

        # The molecule names.
        mol_names = bmrb.molecule_names(data, N)

        # Missing atom names.
        if 'atom_names' not in data or data['atom_names'] == None:
            data['atom_names'] = [None] * N

        # Generate the sequence if needed.
        bmrb.generate_sequence(N, spin_names=data['atom_names'], res_nums=data['res_nums'], res_names=data['res_names'], mol_names=mol_names)

        # Correlation time scaling.
        table = {'s':   1.0,
                 'ns':  1e-9,
                 'ps':  1e-12}
        te_scale = 1.0
        if data['te_units']:
            te_scale = table[data['te_units']]

        # Fast correlation time scaling.
        if data['tf_units']:
            tf_scale = table[data['tf_units']]
        else:
            tf_scale = te_scale

        # Slow correlation time scaling.
        if data['ts_units']:
            ts_scale = table[data['ts_units']]
        else:
            ts_scale = te_scale

        # Rex scaling.
        rex_scale = 1.0
        if hasattr(cdp, 'spectrometer_frq') and len(cdp.spectrometer_frq):
            rex_scale = 1.0 / (2.0*pi*cdp.spectrometer_frq[cdp.ri_ids[0]])**2

        # Loop over the spins.
        for i in range(N):
            # Generate a spin ID.
            spin_id = mol_res_spin.generate_spin_id_unique(mol_name=mol_names[i], res_name=data['res_names'][i], res_num=data['res_nums'][i], spin_name=data['atom_names'][i])

            # Obtain the spin.
            spin = mol_res_spin.return_spin(spin_id)

            # No spin?!?
            if spin == None:
                raise RelaxError("The spin '%s' does not exist." % spin_id) 

            # Loop over and set the model-free parameters.
            for j in range(len(mf_params)):
                # The parameter.
                param = mf_params[j]

                # No parameter.
                if not mf_bmrb_key[j] in data:
                    continue

                # The parameter and its value.
                if data[mf_bmrb_key[j]] != None:
                    # The value.
                    value = data[mf_bmrb_key[j]][i]

                    # Parameter scaling.
                    if value != None:
                        if param == 'te':
                            value = value * te_scale
                        elif param == 'tf':
                            value = value * tf_scale
                        elif param == 'ts':
                            value = value * ts_scale
                        elif param == 'rex':
                            value = value * rex_scale

                # No parameter value.
                else:
                    value = None

                # Set the parameter.
                setattr(spin, param, value)

                # The error.
                mf_bmrb_key_err = mf_bmrb_key[j] + '_err'
                error = None
                if mf_bmrb_key_err in data and data[mf_bmrb_key_err] != None:
                    error = data[mf_bmrb_key_err][i]

                # Error scaling.
                if error != None:
                    if param == 'te':
                        error = error * te_scale
                    elif param == 'tf':
                        error = error * tf_scale
                    elif param == 'ts':
                        error = error * ts_scale
                    elif param == 'rex':
                        error = error * rex_scale

                # Set the error.
                mf_param_err = param + '_err'
                if mf_bmrb_key_err in data and data[mf_bmrb_key_err] != None:
                    setattr(spin, mf_param_err, error)

            # The model.
            if data['model_fit'] != None and data['model_fit'][i] != None:
                model = from_bmrb_model(data['model_fit'][i])
                setattr(spin, 'model', model)

                # The equation and parameters.
                equation, params = model_map(model)
                setattr(spin, 'equation', equation)
                setattr(spin, 'params', params)

            # Convert te values which should be ts!
            if hasattr(spin, 'model') and spin.model in ['m5', 'm6', 'm7', 'm8'] and hasattr(spin, 'te') and spin.te != None:
                # Change the parameter name of te to ts.
                spin.ts = spin.te
                if hasattr(spin, 'te_err'):
                    spin.ts_err = spin.te_err

                # Set the te and te_err values to None.
                spin.te = None
                spin.te_err = None

            # The element.
            if'atom_types' in data and data['atom_types'] != None:
                setattr(spin, 'element', data['atom_types'][i])

            # Heteronucleus type.
            if'atom_types' in data and data['atom_types'] != None and data['atom_types'][i] != None and 'isotope' in data and data['isotope'] != None:
                # The isotope number.
                iso_num = data['isotope'][i]

                # No isotope number.
                iso_table = {'C': 13, 'N': 15}
                if not data['isotope'][i]:
                    iso_num = iso_table[data['atom_types'][i]]

                # Set the type.
                setattr(spin, 'isotope', str(iso_num) + data['atom_types'][i])


def to_bmrb_model(name=None):
    """Convert the model-free model name to the BMRB name.

    @keyword name:  The model-free model name.
    @type name:     str
    @return:        The corresponding BMRB model name.
    @rtype:         str
    """

    # The relax to BMRB model-free model name map.
    map = {'m0':  '',
           'm1':  'S2',
           'm2':  'S2, te',
           'm3':  'S2, Rex',
           'm4':  'S2, te, Rex',
           'm5':  'S2f, S2, ts',
           'm6':  'S2f, tf, S2, ts',
           'm7':  'S2f, S2, ts, Rex',
           'm8':  'S2f, tf, S2, ts, Rex',
           'm9':  'Rex',
           'tm0': 'tm',
           'tm1': 'tm, S2',
           'tm2': 'tm, S2, te',
           'tm3': 'tm, S2, Rex',
           'tm4': 'tm, S2, te, Rex',
           'tm5': 'tm, S2f, S2, ts',
           'tm6': 'tm, S2f, tf, S2, ts',
           'tm7': 'tm, S2f, S2, ts, Rex',
           'tm8': 'tm, S2f, tf, S2, ts, Rex',
           'tm9': 'tm, Rex'
    }

    # No match.
    if name not in map:
        raise RelaxError("The model-free model '%s' is unknown." % name)

    # Return the BMRB model name.
    return map[name]
