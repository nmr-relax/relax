###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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

# relax module imports.
if dep_check.bmrblib_module:
    from bmrblib.nmr_star_dict import NMR_STAR
    from bmrblib.nmr_star_dict_v3_1 import NMR_STAR_v3_1
from generic_fns import diffusion_tensor, exp_info, mol_res_spin, pipes, relax_data
from generic_fns.mol_res_spin import get_molecule_names, spin_loop
from relax_errors import RelaxError


class Bmrb:
    """Class containing methods related to BMRB STAR file reading and writing."""

    def bmrb_read(self, file_path, version='3.1'):
        """Read the model-free results from a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the NMR-STAR data object.
        if version == '3.1':
            star = NMR_STAR_v3_1('relax_model_free_results', file_path)
        else:
            star = NMR_STAR('relax_model_free_results', file_path)

        # Read the contents of the STAR formatted file.
        star.read()

        # The diffusion tensor.
        diffusion_tensor.bmrb_read(star)

        # Generate the molecule and residue containers from the entity records.
        mol_res_spin.bmrb_read(star)

        # Read the relaxation data saveframes.
        relax_data.bmrb_read(star)


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
        if version == '3.1':
            star = NMR_STAR_v3_1('relax_model_free_results', file_path)
        else:
            star = NMR_STAR('relax_model_free_results', file_path)

        # Global minimisation stats.
        global_chi2 = None
        if hasattr(cdp, 'chi2'):
            global_chi2 = cdp.chi2

        # Rex frq.
        rex_frq = cdp.frq[0]

        # The relax to BMRB model-free model name map.
        model_map = {'m0':  '',
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
            model_list.append(model_map[spin.model])

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
        star.model_free.add(global_chi2=global_chi2, software_ids=[software_id], software_labels=['relax'], entity_ids=entity_ids, res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, atom_types=element_list, isotope=isotope_list, local_tc=local_tm_list, s2=s2_list, s2f=s2f_list, s2s=s2s_list, te=te_list, tf=tf_list, ts=ts_list, rex=rex_list, local_tc_err=local_tm_err_list, s2_err=s2_err_list, s2f_err=s2f_err_list, s2s_err=s2s_err_list, te_err=te_err_list, tf_err=tf_err_list, ts_err=ts_err_list, rex_err=rex_err_list, rex_frq=rex_frq, chi2=chi2_list, model_fit=model_list)


        # Create Supergroup 8 : The structure determination saveframes.
        ###############################################################

        # Generate the diffusion tensor saveframes.
        diffusion_tensor.bmrb_write(star)


        # Write the contents to the STAR formatted file.
        star.write()
