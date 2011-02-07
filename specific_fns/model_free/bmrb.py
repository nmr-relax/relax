###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Edward d'Auvergne                                   #
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

# Dependency check module.
import dep_check

# Python module imports.
from math import pi
from numpy import int32, zeros
import string
from warnings import warn

# relax module imports.
if dep_check.bmrblib_module:
    import bmrblib
from generic_fns import bmrb, diffusion_tensor, exp_info, mol_res_spin, pipes, relax_data
from generic_fns.mol_res_spin import get_molecule_names, spin_loop
from relax_errors import RelaxError
from relax_warnings import RelaxWarning


class Bmrb:
    """Class containing methods related to BMRB STAR file reading and writing."""

    def _bmrb_model_map(self, model_name=None, bmrb_name=None):
        """The model-free model name to BMRB name mapping.

        @return:    Either the bmrb_name or model_name corresponding to the given model_name or bmrb_name respectively.  Both args cannot be given.
        @rtype:     str
        """

        # Check.
        if model_name != None and bmrb_name != None:
            raise RelaxError, "Either the model_name or bmrb_name args can be supplied, but not both together."

        # Conversion of Modelfree4 (and relax) model numbers.
        if bmrb_name in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return 'm' + bmrb_name

        # The relax to BMRB model-free model name map.
        map = {'m0':  '',
               'm1':  'S2',
               'm2':  'S2, te',
               'm3':  'S2, Rex',
               'm4':  'S2, te, Rex',
               'm5':  'S2f, S2, ts',
               'm5':  'S2, te, S2f',
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

        # Indicies.
        if model_name:
            search_text = model_name
            search_index = 0
            return_index = 1
        else:
            search_text = bmrb_name
            search_index = 1
            return_index = 0

        # Loop over the dictionary.
        for item in map.items():
            # Normal match.
            if item[search_index] == search_text:
                return item[return_index]

            # No whitespace.
            if string.replace(item[search_index], ' ', '') == search_text:
                return item[return_index]

        # The bmrb name is the relax name!
        for item in map.items():
            if item[0] == bmrb_name:
                return bmrb_name

        # Should not be here!
        if model_name:
            raise RelaxError("The model-free model '%s' is unknown." % model_name)
        else:
            warn(RelaxWarning("The BMRB model-free model name '%s' is unknown." % model_name))


    def _sf_model_free_read(self, star, sample_conditions=None):
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
            # Store the keys.
            keys = data.keys()

            # Sample conditions do not match (remove the $ sign).
            if 'sample_cond_list_label' in keys and sample_conditions and string.replace(data['sample_cond_list_label'], '$', '') != sample_conditions:
                continue

            # Global data.
            if 'global_chi2' in keys:
                setattr(cdp, 'chi2', data['global_chi2'])

            # The number of spins.
            N = bmrb.num_spins(data)

            # No data in the saveframe.
            if N == 0:
                continue

            # The molecule names.
            mol_names = bmrb.molecule_names(data, N)

            # Missing atom names.
            if 'atom_names' not in keys or data['atom_names'] == None:
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
            if hasattr(cdp, 'frq') and len(cdp.frq):
                rex_scale = 1.0 / (2.0*pi*cdp.frq[0])**2

            # Loop over the spins.
            for i in range(N):
                # Generate a spin ID.
                spin_id = mol_res_spin.generate_spin_id(mol_name=mol_names[i], res_name=data['res_names'][i], res_num=data['res_nums'][i], spin_name=data['atom_names'][i])

                # Obtain the spin.
                spin = mol_res_spin.return_spin(spin_id)

                # No spin?!?
                if spin == None:
                    raise(RelaxError("The spin '%s' does not exist." % spin_id))

                # Loop over and set the model-free parameters.
                for j in range(len(mf_params)):
                    # No parameter.
                    if not mf_bmrb_key[j] in keys or data[mf_bmrb_key[j]] == None:
                        continue

                    # The value.
                    value = data[mf_bmrb_key[j]][i]

                    # The parameter.
                    param = mf_params[j]

                    # Change the parameter name of te to ts.
                    if param == 'te':
                        if data['s2s'] and data['s2s'][i] != None:
                            param = 'ts'

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

                    # Set the parameter.
                    setattr(spin, param, value)

                    # The error.
                    mf_bmrb_key_err = mf_bmrb_key[j] + '_err'
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
                    if mf_bmrb_key_err in keys and data[mf_bmrb_key_err] != None:
                        setattr(spin, mf_param_err, error)

                # The model.
                if data['model_fit'] != None and data['model_fit'][i] != None:
                    model = self._bmrb_model_map(bmrb_name=data['model_fit'][i])
                    setattr(spin, 'model', model)

                    # The equation and parameters.
                    equation, params = self._model_map(model)
                    setattr(spin, 'equation', equation)
                    setattr(spin, 'params', params)

                # The element.
                if'atom_types' in keys and data['atom_types'] != None:
                    setattr(spin, 'element', data['atom_types'][i])

                # Heteronucleus type.
                if'atom_types' in keys and data['atom_types'] != None and data['atom_types'][i] != None and 'isotope' in keys and data['isotope'] != None:
                    # The isotope number.
                    iso_num = data['isotope'][i]

                    # No isotope number.
                    iso_table = {'C': 13, 'N': 15}
                    if not data['isotope'][i]:
                        iso_num = iso_table[data['atom_types'][i]]

                    # Set the type.
                    setattr(spin, 'heteronuc_type', str(iso_num) + data['atom_types'][i])


    def _sf_csa_read(self, star):
        """Place the CSA data from the saveframe records into the spin container.

        @param star:    The NMR-STAR dictionary object.
        @type star:     NMR_STAR instance
        """

        # Get the entities.
        for data in star.chem_shift_anisotropy.loop():
            # Loop over the spins.
            for i in range(len(data['data_ids'])):
                # Generate a spin ID.
                spin_id = mol_res_spin.generate_spin_id(res_num=data['res_nums'][i], spin_name=data['atom_names'][i])

                # Obtain the spin.
                spin = mol_res_spin.return_spin(spin_id)

                # The CSA value (converted from ppm).
                setattr(spin, 'csa', data['csa'][i] * 1e-6)


    def bmrb_read(self, file_path, version=None, sample_conditions=None):
        """Read the model-free results from a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:           The full file path.
        @type file_path:            str
        @keyword version:           The BMRB version to force the reading.
        @type version:              None or str
        @keyword sample_conditions: The sample condition label to read.  Only one sample condition can be read per data pipe.
        @type sample_conditions:    None or str
        """

        print sample_conditions
        # Initialise the NMR-STAR data object.
        star = bmrblib.create_nmr_star('relax_model_free_results', file_path, version)

        # Read the contents of the STAR formatted file.
        star.read()

        # The sample conditions.
        sample_conds = bmrb.list_sample_conditions(star)
        if sample_conditions and sample_conditions not in sample_conds:
            raise RelaxError("The sample conditions label '%s' does not correspond to any of the labels in the file: %s" % (sample_conditions, sample_conds))
        if not sample_conditions and len(sample_conds) > 1:
            raise RelaxError("Only one of the sample conditions in %s can be loaded per relax data pipe." % sample_conds)

        # The diffusion tensor.
        diffusion_tensor.bmrb_read(star)

        # Generate the molecule and residue containers from the entity records.
        mol_res_spin.bmrb_read(star)

        # Read the relaxation data saveframes.
        relax_data.bmrb_read(star, sample_conditions=sample_conditions)

        # Read the model-free data saveframes.
        self._sf_model_free_read(star, sample_conditions=sample_conditions)

        # Read the CSA data saveframes.
        self._sf_csa_read(star)


    def bmrb_write(self, file_path, version=None):
        """Write the model-free results to a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        @keyword version:   The BMRB NMR-STAR dictionary format to output to.
        @type version:      str
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Initialise the NMR-STAR data object.
        star = bmrblib.create_nmr_star('relax_model_free_results', file_path, version)

        # Global minimisation stats.
        global_chi2 = None
        if hasattr(cdp, 'chi2'):
            global_chi2 = cdp.chi2

        # Rex frq.
        rex_frq = cdp.frq[0]

        # Initialise the spin specific data lists.
        mol_name_list = []
        res_num_list = []
        res_name_list = []
        atom_name_list = []

        csa_list = []
        r_list = []
        isotope_list = []
        element_list = []

        local_tm_list = []
        s2_list = []
        s2f_list = []
        s2s_list = []
        te_list = []
        tf_list = []
        ts_list = []
        rex_list = []

        local_tm_err_list = []
        s2_err_list = []
        s2f_err_list = []
        s2s_err_list = []
        te_err_list = []
        tf_err_list = []
        ts_err_list = []
        rex_err_list = []

        chi2_list = []
        model_list = []

        # Store the spin specific data in lists for later use.
        for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check the data for None (not allowed in BMRB!).
            if res_num == None:
                raise RelaxError("For the BMRB, the residue of spin '%s' must be numbered." % spin_id)
            if res_name == None:
                raise RelaxError("For the BMRB, the residue of spin '%s' must be named." % spin_id)
            if spin.name == None:
                raise RelaxError("For the BMRB, the spin '%s' must be named." % spin_id)
            if spin.heteronuc_type == None:
                raise RelaxError("For the BMRB, the spin isotope type of '%s' must be specified." % spin_id)
            if not hasattr(spin, 'element') or spin.element == None:
                raise RelaxError("For the BMRB, the spin element type of '%s' must be specified.  Please use the spin user function for setting the element type." % spin_id)

            # The molecule/residue/spin info.
            mol_name_list.append(mol_name)
            res_num_list.append(res_num)
            res_name_list.append(res_name)
            atom_name_list.append(spin.name)

            # Values.
            csa_list.append(spin.csa * 1e6)    # In ppm.
            r_list.append(spin.r)
            isotope_list.append(int(string.strip(spin.heteronuc_type, string.ascii_letters)))
            element_list.append(spin.element)

            # Diffusion tensor.
            local_tm_list.append(spin.local_tm)
            if hasattr(spin, 'local_tm_err'):
                local_tm_err_list.append(spin.local_tm_err)
            else:
                local_tm_err_list.append(None)

            # Model-free parameter values.
            s2_list.append(spin.s2)
            s2f_list.append(spin.s2f)
            s2s_list.append(spin.s2s)
            te_list.append(spin.te)
            tf_list.append(spin.tf)
            ts_list.append(spin.ts)
            if spin.rex == None:
                rex_list.append(None)
            else:
                rex_list.append(spin.rex / (2.0*pi*rex_frq**2))

            # Model-free parameter errors.
            params = ['s2', 's2f', 's2s', 'te', 'tf', 'ts', 'rex']
            for param in params:
                # The error list.
                err_list = locals()[param+'_err_list']

                # Append the error.
                if hasattr(spin, param+'_err'):
                    # The value.
                    val = getattr(spin, param+'_err')

                    # Scaling.
                    if param == 'rex' and val != None:
                        val = val / (2.0*pi*rex_frq**2)

                    # Append.
                    err_list.append(val)

                # Or None.
                else:
                    err_list.append(None)


            # Opt stats.
            chi2_list.append(spin.chi2)

            # Model-free model.
            model_list.append(self._bmrb_model_map(model_name=spin.model))

        # Convert the molecule names into the entity IDs.
        entity_ids = zeros(len(mol_name_list), int32)
        mol_names = get_molecule_names()
        for i in range(len(mol_name_list)):
            for j in range(len(mol_names)):
                if mol_name_list[i] == mol_names[j]:
                    entity_ids[i] = j+1


        # Create Supergroup 2 : The citations.
        ######################################

        # Generate the citations saveframe.
        exp_info.bmrb_write_citations(star)


        # Create Supergroup 3 : The molecular assembly saveframes.
        ##########################################################

        # Generate the entity saveframe.
        mol_res_spin.bmrb_write_entity(star)


        # Create Supergroup 4:  The experimental descriptions saveframes.
        #################################################################

        # Generate the method saveframes.
        exp_info.bmrb_write_methods(star)

        # Generate the software saveframe.
        software_ids, software_labels = exp_info.bmrb_write_software(star)


        # Create Supergroup 5 : The NMR parameters saveframes.
        ######################################################

        # Generate the CSA saveframe.
        star.chem_shift_anisotropy.add(entity_ids=entity_ids, res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, atom_types=element_list, isotope=isotope_list, csa=csa_list)


        # Create Supergroup 6 : The kinetic data saveframes.
        ####################################################

        # Generate the relaxation data saveframes.
        relax_data.bmrb_write(star)


        # Create Supergroup 7 : The thermodynamics saveframes.
        ######################################################

        # Get the relax software id.
        for i in range(len(software_ids)):
            if software_labels[i] == 'relax':
                software_id = software_ids[i]

        # Generate the model-free data saveframe.
        star.model_free.add(global_chi2=global_chi2, software_ids=[software_id], software_labels=['relax'], entity_ids=entity_ids, res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, atom_types=element_list, isotope=isotope_list, bond_length=r_list, local_tc=local_tm_list, s2=s2_list, s2f=s2f_list, s2s=s2s_list, te=te_list, tf=tf_list, ts=ts_list, rex=rex_list, local_tc_err=local_tm_err_list, s2_err=s2_err_list, s2f_err=s2f_err_list, s2s_err=s2s_err_list, te_err=te_err_list, tf_err=tf_err_list, ts_err=ts_err_list, rex_err=rex_err_list, rex_frq=rex_frq, chi2=chi2_list, model_fit=model_list)


        # Create Supergroup 8 : The structure determination saveframes.
        ###############################################################

        # Generate the diffusion tensor saveframes.
        diffusion_tensor.bmrb_write(star)


        # Write the contents to the STAR formatted file.
        star.write()
