###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
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
"""The Lipari-Szabo model-free analysis API object."""


# Python module imports.
import bmrblib
from copy import deepcopy
from math import pi
from minfx.grid import grid_split
from numpy import array, dot, float64, int32, zeros
from numpy.linalg import inv
from re import match, search
import string
import sys
from types import MethodType
from warnings import warn

# relax module imports.
from lib.arg_check import is_num_list, is_str_list
from lib.errors import RelaxError, RelaxFault, RelaxNoModelError, RelaxNoSequenceError, RelaxNoTensorError
from lib.float import isInf
from lib.physical_constants import h_bar, mu0, return_gyromagnetic_ratio
from lib.text.sectioning import subsection
from lib.warnings import RelaxDeselectWarning, RelaxWarning
from multi import Processor_box
from pipe_control import diffusion_tensor, interatomic, mol_res_spin, pipes, relax_data, sequence
from pipe_control.bmrb import list_sample_conditions
from pipe_control.exp_info import bmrb_write_citations, bmrb_write_methods, bmrb_write_software
from pipe_control.interatomic import return_interatom_list
from pipe_control.mol_res_spin import count_spins, exists_mol_res_spin_data, find_index, get_molecule_names, return_spin, return_spin_from_index, return_spin_indices, spin_loop
from pipe_control.minimise import reset_min_stats
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.model_free.bmrb import sf_csa_read, sf_model_free_read, to_bmrb_model
from specific_analyses.model_free.data import compare_objects
from specific_analyses.model_free.molmol import Molmol
from specific_analyses.model_free.model import determine_model_type
from specific_analyses.model_free.parameters import are_mf_params_set, assemble_param_names, assemble_param_vector, linear_constraints
from specific_analyses.model_free.optimisation import MF_grid_command, MF_memo, MF_minimise_command, minimise_data_setup, relax_data_opt_structs
from specific_analyses.model_free.parameter_object import Model_free_params
from specific_analyses.model_free.pymol import Pymol
from target_functions.mf import Mf


class Model_free(API_base, API_common):
    """Parent class containing all the model-free specific functions."""

    # Class variable for storing the class instance (for the singleton design pattern).
    instance = None

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.return_error = self._return_error_relax_data
        self.return_value = self._return_value_general
        self.sim_pack_data = self._sim_pack_relax_data

        # Initialise the macro classes.
        self._molmol_macros = Molmol()
        self._pymol_macros = Pymol()

        # Alias the macro creation methods.
        self.pymol_macro = self._pymol_macros.create_macro
        self.molmol_macro = self._molmol_macros.create_macro

        # Place a copy of the parameter list object in the instance namespace.
        self._PARAMS = Model_free_params()


    def back_calc_ri(self, spin_index=None, ri_id=None, ri_type=None, frq=None):
        """Back-calculation of relaxation data from the model-free parameter values.

        @keyword spin_index:    The global spin index.
        @type spin_index:       int
        @keyword ri_id:         The relaxation data ID string.
        @type ri_id:            str
        @keyword ri_type:       The relaxation data type.
        @type ri_type:          str
        @keyword frq:           The field strength.
        @type frq:              float
        @return:                The back calculated relaxation data value corresponding to the index.
        @rtype:                 float
        """

        # Get the spin container.
        spin, spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)

        # Missing interatomic vectors.
        if hasattr(cdp, 'diff_tensor') and (cdp.diff_tensor.type == 'spheroid' or cdp.diff_tensor.type == 'ellipsoid'):
            interatoms = interatomic.return_interatom_list(spin_id)
            for i in range(len(interatoms)):
                # No dipolar relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # Check the unit vectors.
                if not hasattr(interatoms[i], 'vector') or interatoms[i].vector == None:
                    warn(RelaxDeselectWarning(spin_id, 'missing structural data'))
                    return

        # Execute the over-fit deselection.
        self.overfit_deselect(data_check=False, verbose=False)

        # Get the relaxation value from the minimise function.
        value = self.minimise(min_algor='back_calc', min_options=(spin_index, ri_id, ri_type, frq))

        # Return the relaxation value.
        return value


    def bmrb_read(self, file_path, version=None, sample_conditions=None):
        """Read the model-free results from a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:           The full file path.
        @type file_path:            str
        @keyword version:           The BMRB version to force the reading.
        @type version:              None or str
        @keyword sample_conditions: The sample condition label to read.  Only one sample condition can be read per data pipe.
        @type sample_conditions:    None or str
        """

        # Initialise the NMR-STAR data object.
        star = bmrblib.create_nmr_star('relax_model_free_results', file_path, version)

        # Read the contents of the STAR formatted file.
        star.read()

        # The sample conditions.
        sample_conds = list_sample_conditions(star)
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
        sf_model_free_read(star, sample_conditions=sample_conditions)

        # Read the CSA data saveframes.
        sf_csa_read(star)


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
        rex_frq = cdp.spectrometer_frq[cdp.ri_ids[0]]

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
            # Skip the protons.
            if spin.name == 'H' or (hasattr(spin, 'element') and spin.element == 'H'):
                warn(RelaxWarning("Skipping the proton spin '%s'." % spin_id))
                continue

            # Check the data for None (not allowed in BMRB!).
            if res_num == None:
                raise RelaxError("For the BMRB, the residue of spin '%s' must be numbered." % spin_id)
            if res_name == None:
                raise RelaxError("For the BMRB, the residue of spin '%s' must be named." % spin_id)
            if spin.name == None:
                raise RelaxError("For the BMRB, the spin '%s' must be named." % spin_id)
            if not hasattr(spin, 'isotope') or spin.isotope == None:
                raise RelaxError("For the BMRB, the spin isotope type of '%s' must be specified." % spin_id)
            if not hasattr(spin, 'element') or spin.element == None:
                raise RelaxError("For the BMRB, the spin element type of '%s' must be specified.  Please use the spin user function for setting the element type." % spin_id)

            # The molecule/residue/spin info.
            mol_name_list.append(mol_name)
            res_num_list.append(res_num)
            res_name_list.append(res_name)
            atom_name_list.append(spin.name)

            # CSA values.
            if hasattr(spin, 'csa'):
                csa_list.append(spin.csa * 1e6)    # In ppm.
            else:
                csa_list.append(None)

            # Interatomic distances.
            interatoms = return_interatom_list(spin_id)
            for i in range(len(interatoms)):
                # No relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # Add the interatomic distance.
                if hasattr(interatoms[i], 'r'):
                    r_list.append(interatoms[i].r)
                else:
                    r_list.append(None)

                # Stop adding.
                break

            # The nuclear isotope.
            if hasattr(spin, 'isotope'):
                isotope_list.append(int(spin.isotope.strip(string.ascii_letters)))
            else:
                isotope_list.append(None)

            # The element.
            if hasattr(spin, 'element'):
                element_list.append(spin.element)
            else:
                element_list.append(None)

            # Diffusion tensor.
            if hasattr(spin, 'local_tm'):
                local_tm_list.append(spin.local_tm)
            else:
                local_tm_list.append(None)
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
            model_list.append(to_bmrb_model(spin.model))

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
        bmrb_write_citations(star)


        # Create Supergroup 3 : The molecular assembly saveframes.
        ##########################################################

        # Generate the entity saveframe.
        mol_res_spin.bmrb_write_entity(star)


        # Create Supergroup 4:  The experimental descriptions saveframes.
        #################################################################

        # Generate the method saveframes.
        bmrb_write_methods(star)

        # Generate the software saveframe.
        software_ids, software_labels = bmrb_write_software(star)


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


    def calculate(self, spin_id=None, scaling_matrix=None, verbosity=1, sim_index=None):
        """Calculation of the model-free chi-squared value.

        @keyword spin_id:           The spin identification string.
        @type spin_id:              str
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Determine the model type.
        model_type = determine_model_type()

        # Test if diffusion tensor data exists.
        if model_type != 'local_tm' and not diffusion_tensor.diff_data_exists():
            raise RelaxNoTensorError('diffusion')

        # Test if the PDB file has been loaded.
        if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and not hasattr(cdp, 'structure'):
            raise RelaxNoPdbError

        # Loop over the spins.
        for spin, id in spin_loop(spin_id, return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if the model-free model has been setup.
            if not spin.model:
                raise RelaxNoModelError

            # Test if the nuclear isotope type has been set.
            if not hasattr(spin, 'isotope'):
                raise RelaxSpinTypeError

            # Test if the model-free parameter values exist.
            unset_param = are_mf_params_set(spin)
            if unset_param != None:
                raise RelaxNoValueError(unset_param)

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Test the interatomic data.
            interatoms = return_interatom_list(spin_id)
            for interatom in interatoms:
                # No relaxation mechanism.
                if not interatom.dipole_pair:
                    continue

                # Test if unit vectors exist.
                if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and not hasattr(interatom, 'vector'):
                    raise RelaxNoVectorsError

                # Test if multiple unit vectors exist.
                if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and hasattr(interatom, 'vector') and is_num_list(interatom.vector[0], raise_error=False):
                    raise RelaxMultiVectorError

                # The interacting spin.
                if spin_id != interatom.spin_id1:
                    spin_id2 = interatom.spin_id1
                else:
                    spin_id2 = interatom.spin_id2
                spin2 = return_spin(spin_id2)

                # Test if the nuclear isotope type has been set.
                if not hasattr(spin2, 'isotope'):
                    raise RelaxSpinTypeError

                # Test if the interatomic distance has been set.
                if not hasattr(interatom, 'r') or interatom.r == None:
                    raise RelaxNoValueError("interatomic distance", spin_id=spin_id, spin_id2=spin_id2)

            # Skip spins where there is no data or errors.
            if not hasattr(spin, 'ri_data') or not hasattr(spin, 'ri_data_err'):
                continue

            # Make sure that the errors are strictly positive numbers.
            for ri_id in cdp.ri_ids:
                # Alias.
                err = spin.ri_data_err[ri_id]

                # Checks.
                if err != None and err == 0.0:
                    raise RelaxError("Zero error for spin '%s' for the relaxation data ID '%s', minimisation not possible." % (id, ri_id))
                elif err != None and err < 0.0:
                    raise RelaxError("Negative error of %s for spin '%s' for the relaxation data ID '%s', minimisation not possible." % (err, id, ri_id))

            # Create the initial parameter vector.
            param_vector = assemble_param_vector(spin=spin, sim_index=sim_index)

            # The relaxation data optimisation structures.
            data = relax_data_opt_structs(spin, sim_index=sim_index)

            # The spin data.
            ri_data = [array(data[0])]
            ri_data_err = [array(data[1])]
            num_frq = [data[2]]
            num_ri = [data[3]]
            ri_labels = [data[4]]
            frq = [data[5]]
            remap_table = [data[6]]
            noe_r1_table = [data[7]]
            gx = [return_gyromagnetic_ratio(spin.isotope)]
            if sim_index == None:
                csa = [spin.csa]
            else:
                csa = [spin.csa_sim[sim_index]]

            # The interatomic data.
            interatoms = return_interatom_list(spin_id)
            for i in range(len(interatoms)):
                # No relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # The surrounding spins.
                if spin_id != interatoms[i].spin_id1:
                    spin_id2 = interatoms[i].spin_id1
                else:
                    spin_id2 = interatoms[i].spin_id2
                spin2 = return_spin(spin_id2)

                # The data.
                if sim_index == None:
                    r = [interatoms[i].r]
                else:
                    r = [interatoms[i].r_sim[sim_index]]

                # Vectors.
                if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                    xh_unit_vectors = [interatoms[i].vector]
                else:
                    xh_unit_vectors = [None]

                # Gyromagnetic ratios.
                gh = [return_gyromagnetic_ratio(spin2.isotope)]

            # Count the number of model-free parameters for the residue index.
            num_params = [len(spin.params)]

            # Repackage the parameter values as a local model (ignore if the diffusion tensor is not fixed).
            param_values = [assemble_param_vector(model_type='mf')]

            # Package the diffusion tensor parameters.
            if model_type == 'local_tm':
                diff_params = [spin.local_tm]
                diff_type = 'sphere'
            else:
                # Diff type.
                diff_type = cdp.diff_tensor.type

                # Spherical diffusion.
                if diff_type == 'sphere':
                    diff_params = [cdp.diff_tensor.tm]

                # Spheroidal diffusion.
                elif diff_type == 'spheroid':
                    diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.theta, cdp.diff_tensor.phi]

                # Ellipsoidal diffusion.
                elif diff_type == 'ellipsoid':
                    diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.Dr, cdp.diff_tensor.alpha, cdp.diff_tensor.beta, cdp.diff_tensor.gamma]

            # Initialise the model-free function.
            mf = Mf(init_params=param_vector, model_type='mf', diff_type=diff_type, diff_params=diff_params, num_spins=1, equations=[spin.equation], param_types=[spin.params], param_values=param_values, relax_data=ri_data, errors=ri_data_err, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=gx, gh=gh, h_bar=h_bar, mu0=mu0, num_params=num_params, vectors=xh_unit_vectors)

            # Chi-squared calculation.
            try:
                chi2 = mf.func(param_vector)
            except OverflowError:
                chi2 = 1e200

            # Global chi-squared value.
            if model_type == 'all' or model_type == 'diff':
                cdp.chi2 = cdp.chi2 + chi2
            else:
                spin.chi2 = chi2


    def create_mc_data(self, data_id=None):
        """Create the Monte Carlo Ri data.

        @keyword data_id:   The spin identification string, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Initialise the MC data structure.
        mc_data = []

        # Get the spin container and global spin index.
        spin = return_spin(data_id)
        global_index = find_index(data_id)

        # Skip deselected spins.
        if not spin.select:
            return

        # Test if the model is set, returning None to signal that the spin should be skipped.
        if not hasattr(spin, 'model') or not spin.model:
            return None

        # Loop over the relaxation data.
        for ri_id in cdp.ri_ids:
            # Back calculate the value.
            value = self.back_calc_ri(spin_index=global_index, ri_id=ri_id, ri_type=cdp.ri_type[ri_id], frq=cdp.spectrometer_frq[ri_id])

            # Append the value.
            mc_data.append(value)

        # Return the data.
        return mc_data


    def data_init(self, data, sim=False):
        """Initialise the spin specific data structures.

        @param data:    The spin ID string from the _base_data_loop_spin() method.
        @type data:     str
        @keyword sim:   The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:      bool
        """

        # Get the spin container.
        spin = return_spin(data)

        # Loop over the data structure names.
        for name in self._PARAMS.loop(scope='spin'):
            # Blacklisted data structures.
            if name in ['ri_data', 'ri_data_bc', 'ri_data_err']:
                continue

            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Set everything else initially to None or False.
            init_data = None
            if self._PARAMS.type(name) == bool:
                init_data = False
                if name == 'select':
                    init_data = True

            # If the name is not in the spin container, add it.
            if not hasattr(spin, name):
                setattr(spin, name, init_data)


    def deselect(self, sim_index=None, model_info=None):
        """Deselect models or simulations.

        @keyword sim_index:     The optional Monte Carlo simulation index.  If None, then models will be deselected, otherwise the given simulation will.
        @type sim_index:        None or int
        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Local models.
        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin.
            spin = return_spin_from_index(model_info)

            # Spin deselection.
            if sim_index == None:
                spin.select = False

            # Simulation deselection.
            else:
                spin.select_sim[sim_index] = False

        # Global models.
        else:
            # Global model deselection.
            if sim_index == None:
                raise RelaxError("Cannot deselect the global model.")

            # Simulation deselection.
            else:
                # Deselect.
                cdp.select_sim[sim_index] = False


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single model-free model.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       A flag which if True will cause info about each spin to be printed out as the sequence is generated.
        @type verbose:          bool
        """

        # Arg tests.
        if model_info == None:
            raise RelaxError("The model_info argument cannot be None.")

        # First create the pipe_to data pipe, if it doesn't exist, but don't switch to it.
        if not pipes.has_pipe(pipe_to):
            pipes.create(pipe_to, pipe_type='mf', switch=False)

        # Get the data pipes.
        dp_from = pipes.get_pipe(pipe_from)
        dp_to = pipes.get_pipe(pipe_to)

        # Duplicate all non-sequence specific data.
        for data_name in dir(dp_from):
            # Skip the container objects.
            if data_name in ['diff_tensor', 'mol', 'interatomic', 'structure', 'exp_info']:
                continue

            # Skip special objects.
            if search('^_', data_name) or data_name in list(dp_from.__class__.__dict__.keys()):
                continue

            # Get the original object.
            data_from = getattr(dp_from, data_name)

            # The data already exists.
            if hasattr(dp_to, data_name):
                # Get the object in the target pipe.
                data_to = getattr(dp_to, data_name)

                # The data must match!
                if data_from != data_to:
                    raise RelaxError("The object " + repr(data_name) + " is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                # Skip the data.
                continue

            # Duplicate the data.
            setattr(dp_to, data_name, deepcopy(data_from))

        # Diffusion tensor comparison.
        if hasattr(dp_from, 'diff_tensor'):
            # Duplicate the tensor if it doesn't exist.
            if not hasattr(dp_to, 'diff_tensor'):
                setattr(dp_to, 'diff_tensor', deepcopy(dp_from.diff_tensor))

            # Otherwise compare the objects inside the container.
            else:
                # Loop over the modifiable objects.
                for data_name in dp_from.diff_tensor._mod_attr:
                    # Get the original object.
                    data_from = None
                    if hasattr(dp_from.diff_tensor, data_name):
                        data_from = getattr(dp_from.diff_tensor, data_name)

                    # Get the target object.
                    if data_from and not hasattr(dp_to.diff_tensor, data_name):
                        raise RelaxError("The diffusion tensor object " + repr(data_name) + " of the " + repr(pipe_from) + " data pipe is not located in the " + repr(pipe_to) + " data pipe.")
                    elif data_from:
                        data_to = getattr(dp_to.diff_tensor, data_name)
                    else:
                        continue

                    # The data must match!
                    if data_from != data_to:
                        raise RelaxError("The object " + repr(data_name) + " is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

        # Structure comparison.
        if hasattr(dp_from, 'structure'):
            # Duplicate the tensor if it doesn't exist.
            if not hasattr(dp_to, 'structure'):
                setattr(dp_to, 'structure', deepcopy(dp_from.structure))

            # Otherwise compare the objects inside the container.
            else:
                # Modifiable object checks.
                compare_objects(dp_from.structure, dp_to.structure, pipe_from, pipe_to)

                # Tests for the model and molecule containers.
                if len(dp_from.structure.structural_data) != len(dp_from.structure.structural_data):
                    raise RelaxError("The number of structural models is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                # Loop over the models.
                for i in range(len(dp_from.structure.structural_data)):
                    # Alias.
                    model_from = dp_from.structure.structural_data[i]
                    model_to = dp_to.structure.structural_data[i]

                    # Model numbers.
                    if model_from.num != model_to.num:
                        raise RelaxError("The structure models are not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                    # Molecule number.
                    if len(model_from.mol) != len(model_to.mol):
                        raise RelaxError("The number of molecules is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                    # Loop over the models.
                    for mol_index in range(len(model_from.mol)):
                        # Modifiable object checks.
                        compare_objects(model_from.mol[mol_index], model_to.mol[mol_index], pipe_from, pipe_to)

        # No sequence data, so skip the rest.
        if dp_from.mol.is_empty():
            return

        # Duplicate the sequence data if it doesn't exist.
        if dp_to.mol.is_empty():
            sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to, preserve_select=True, verbose=verbose)

        # Duplicate the interatomic data if it doesn't exist.
        if dp_to.interatomic.is_empty():
            interatomic.copy(pipe_from=pipe_from, pipe_to=pipe_to, verbose=verbose)

        # Determine the model type of the original data pipe.
        pipes.switch(pipe_from)
        model_type = determine_model_type()

        # Sequence specific data.
        spin, spin_id = return_spin_from_index(model_info, pipe=pipe_from, return_spin_id=True)
        if model_type == 'mf' or (model_type == 'local_tm' and not global_stats):
            # Duplicate the spin specific data.
            for name in dir(spin):
                # Skip special objects.
                if search('^__', name):
                    continue

                # Get the object.
                obj = getattr(spin, name)

                # Skip methods.
                if isinstance(obj, MethodType):
                    continue

                # Duplicate the object.
                new_obj = deepcopy(getattr(spin, name))
                setattr(dp_to.mol[spin._mol_index].res[spin._res_index].spin[spin._spin_index], name, new_obj)

            # Duplicate the relaxation active spins which have not been copied yet.
            interatoms = interatomic.return_interatom_list(spin_id)
            for interatom in interatoms:
                # No relaxation mechanism.
                if not interatom.dipole_pair:
                    continue

                # The interacting spin.
                if spin_id != interatom.spin_id1:
                    spin_id2 = interatom.spin_id1
                else:
                    spin_id2 = interatom.spin_id2
                spin2 = return_spin(spin_id2)

                # Duplicate the spin specific data.
                mol_index, res_index, spin_index = return_spin_indices(spin_id2)
                dp_to.mol[mol_index].res[res_index].spin[spin_index] = deepcopy(spin2)

        # Other data types.
        else:
            # Duplicate all the spin specific data.
            dp_to.mol = deepcopy(dp_from.mol)


    def eliminate(self, name, value, args, sim=None, model_info=None):
        """Model-free model elimination, parameter by parameter.

        @param name:            The parameter name.
        @type name:             str
        @param value:           The parameter value.
        @type value:            float
        @param args:            The c1 and c2 elimination constant overrides.
        @type args:             None or tuple of float
        @keyword sim:           The Monte Carlo simulation index.
        @type sim:              int
        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                True if the model is to be eliminated, False otherwise.
        @rtype:                 bool
        """

        # Default values.
        c1 = 50.0 * 1e-9
        c2 = 1.5

        # Depack the arguments.
        if args != None:
            c1, c2 = args

        # Determine the model type.
        model_type = determine_model_type()

        # Can't handle this one yet!
        if model_type != 'mf' and model_type != 'local_tm':
            raise RelaxError("Elimination of the global model is not yet supported.")

        # Get the spin and it's id string.
        spin, spin_id = return_spin_from_index(model_info, return_spin_id=True)

        # Get the tm value.
        if model_type == 'local_tm':
            tm = spin.local_tm
        else:
            tm = cdp.diff_tensor.tm

        # No tm value set, so skip the tests (no elimination).
        if tm == None:
            return False

        # Local tm.
        if name == 'local_tm' and value >= c1:
            if sim == None:
                print("Data pipe '%s':  The local tm parameter of %.5g is greater than %.5g, eliminating spin system '%s'." % (pipes.cdp_name(), value, c1, spin_id))
            else:
                print("Data pipe '%s':  The local tm parameter of %.5g is greater than %.5g, eliminating simulation %i of spin system '%s'." % (pipes.cdp_name(), value, c1, sim, spin_id))
            return True

        # Internal correlation times.
        if match('t[efs]', name) and value >= c2 * tm:
            if sim == None:
                print("Data pipe '%s':  The %s value of %.5g is greater than %.5g, eliminating spin system '%s'." % (pipes.cdp_name(), name, value, c2*tm, spin_id))
            else:
                print("Data pipe '%s':  The %s value of %.5g is greater than %.5g, eliminating simulation %i of spin system '%s'." % (pipes.cdp_name(), name, value, c2*tm, sim, spin_id))
            return True

        # Accept model.
        return False


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Get the spin ids.
        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin and it's id string.
            spin, spin_id = return_spin_from_index(model_info, return_spin_id=True)
        else:
            spin_id = None

        # Assemble and return the parameter names.
        return assemble_param_names(model_type, spin_id=spin_id)


    def get_param_values(self, model_info=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Test if the model-free models have been set up.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Not setup.
            if not spin.model:
                raise RelaxNoModelError

        # Determine the model type.
        model_type = determine_model_type()

        # Set the spin container (to None if the model is global).
        if model_type == 'mf' or model_type == 'local_tm':
            spin = return_spin_from_index(model_info)
        else:
            spin = None

        # Assemble the parameter values and return them.
        return assemble_param_vector(spin=spin, sim_index=sim_index, model_type=model_type)


    def grid_search(self, lower=None, upper=None, inc=None, scaling_matrix=None, constraints=True, verbosity=1, sim_index=None):
        """The model-free grid search function.

        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:                list of lists of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:                list of lists of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.
        @type inc:                  list of lists of int
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword constraints:       If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:          bool
        @keyword verbosity:         A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to apply the grid search to.  If None, the normal model is optimised.
        @type sim_index:            int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def map_bounds(self, param, spin_id=None):
        """Create bounds for the OpenDX mapping function.

        @param param:       The name of the parameter to return the lower and upper bounds of.
        @type param:        str
        @param spin_id:     The spin identification string.
        @type spin_id:      str
        @return:            The upper and lower bounds of the parameter.
        @rtype:             list of float
        """

        # Diffusion tensor bounds.
        if self._PARAMS.scope(param) == 'global':
            return diffusion_tensor.map_bounds(param)

        # Get the spin.
        spin = return_spin(spin_id)

        # {s2, s2f, s2s}.
        if search('^s2', param):
            return [0.0, 1.0]

        # {local tm, te, tf, ts}.
        elif search('^t', param) or param == 'local_tm':
            return [0.0, 1e-8]

        # Rex.
        elif param == 'rex':
            return [0.0, 30.0 / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]])**2]

        # Interatomic distances.
        elif param == 'r':
            return [1.0 * 1e-10, 1.1 * 1e-10]

        # CSA.
        elif param == 'csa':
            return [-100 * 1e-6, -300 * 1e-6]


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling_matrix=None, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Model-free minimisation function.

        Three categories of models exist for which the approach to minimisation is different.  These
        are:

        Single spin optimisations:  The 'mf' and 'local_tm' model types which are the
        model-free parameters for single spins, optionally with a local tm parameter.  These
        models have no global parameters.

        Diffusion tensor optimisations:  The 'diff' diffusion tensor model type.  No spin
        specific parameters exist.

        Optimisation of everything:  The 'all' model type consisting of all model-free and all
        diffusion tensor parameters.


        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation. Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation. Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                list of lists of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                list of lists of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  list of lists of int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the model-free model has been setup, and that the nuclear isotope types have been set.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Not setup.
            if not spin.model:
                raise RelaxNoModelError

            # Test if the nuclear isotope type has been set.
            if not hasattr(spin, 'isotope'):
                raise RelaxSpinTypeError

        # Reset the minimisation statistics.
        if min_algor != 'back_calc':
            reset_min_stats(sim_index=sim_index)

        # Containers for the model-free data and optimisation parameters.
        data_store = Data_container()
        opt_params = Data_container()

        # Add the imported parameters.
        data_store.h_bar = h_bar
        data_store.mu0 = mu0
        opt_params.min_algor = min_algor
        opt_params.min_options = min_options
        opt_params.func_tol = func_tol
        opt_params.grad_tol = grad_tol
        opt_params.max_iterations = max_iterations

        # Add the keyword args.
        opt_params.verbosity = verbosity

        # Determine the model type.
        data_store.model_type = determine_model_type()
        if not data_store.model_type:
            return

        # Model type for the back-calculate function.
        if min_algor == 'back_calc' and data_store.model_type != 'local_tm':
            data_store.model_type = 'mf'

        # Test if diffusion tensor data exists.
        if data_store.model_type != 'local_tm' and not diffusion_tensor.diff_data_exists():
            raise RelaxNoTensorError('diffusion')

        # Tests for the PDB file and unit vectors.
        if data_store.model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
            # Test if the structure file has been loaded.
            if not hasattr(cdp, 'structure'):
                raise RelaxNoPdbError

            # Test if unit vectors exist.
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Get the interatomic data container.
                interatoms = return_interatom_list(spin_id)

                # Unit vectors.
                for i in range(len(interatoms)):
                    # No relaxation mechanism.
                    if not interatoms[i].dipole_pair:
                        continue

                    # Check for the vectors.
                    if not hasattr(interatoms[i], 'vector'):
                        raise RelaxNoVectorsError

        # Test if the model-free parameter values are set for minimising diffusion tensor parameters by themselves.
        if data_store.model_type == 'diff':
            # Loop over the sequence.
            for spin in spin_loop():
                unset_param = are_mf_params_set(spin)
                if unset_param != None:
                    raise RelaxNoValueError(unset_param)

        # Print out.
        if verbosity >= 1:
            if data_store.model_type == 'mf':
                print("Only the model-free parameters for single spins will be used.")
            elif data_store.model_type == 'local_mf':
                print("Only a local tm value together with the model-free parameters for single spins will be used.")
            elif data_store.model_type == 'diff':
                print("Only diffusion tensor parameters will be used.")
            elif data_store.model_type == 'all':
                print("The diffusion tensor parameters together with the model-free parameters for all spins will be used.")

        # Test if the CSA and interatomic distances have been set.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # CSA value.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Get the interatomic data container.
            interatoms = return_interatom_list(spin_id)

            # Interatomic distances.
            count = 0
            for i in range(len(interatoms)):
                # No relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # Check for the distances.
                if not hasattr(interatoms[i], 'r') or interatoms[i].r == None:
                    raise RelaxNoValueError("interatomic distance", spin_id=interatoms[i].spin_id1, spin_id2=interatoms[i].spin_id2)

                # Count the number of interactions.
                count += 1
            
            # Too many interactions.
            if count > 1:
                raise RelaxError("The spin '%s' has %s dipolar relaxation interactions defined, but only a maximum of one is currently supported." % (spin_id, count))

        # Number of spins, minimisation instances, and data sets for each model type.
        if data_store.model_type == 'mf' or data_store.model_type == 'local_tm':
            num_data_sets = 1
            data_store.num_spins = 1
        elif data_store.model_type == 'diff' or data_store.model_type == 'all':
            num_data_sets = count_spins(skip_desel=False)
            data_store.num_spins = count_spins()

        # Number of spins, minimisation instances, and data sets for the back-calculate function.
        if min_algor == 'back_calc':
            num_data_sets = 0
            data_store.num_spins = 1

        # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
        processor_box = Processor_box() 
        processor = processor_box.processor

        # Loop over the models.
        for index in self.model_loop():
            # Get the spin container if required.
            if data_store.model_type == 'diff' or data_store.model_type == 'all':
                spin_index = None
                spin, data_store.spin_id = None, None
            elif min_algor == 'back_calc':
                spin_index = opt_params.min_options[0]
                spin, data_store.spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)
            else:
                spin_index = index
                spin, data_store.spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)

            # Individual spin stuff.
            if spin and (data_store.model_type == 'mf' or data_store.model_type == 'local_tm') and not min_algor == 'back_calc':
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins missing relaxation data or errors.
                if not hasattr(spin, 'ri_data') or not hasattr(spin, 'ri_data_err'):
                    continue

            # Skip spins missing the dipolar interaction.
            if spin and (data_store.model_type == 'mf' or data_store.model_type == 'local_tm'):
                interatoms = return_interatom_list(data_store.spin_id)
                if not len(interatoms):
                    continue

            # Parameter vector and diagonal scaling.
            if min_algor == 'back_calc':
                # Create the initial parameter vector.
                opt_params.param_vector = assemble_param_vector(spin=spin, model_type=data_store.model_type)

                # Diagonal scaling.
                data_store.scaling_matrix = None

            else:
                # Create the initial parameter vector.
                opt_params.param_vector = assemble_param_vector(spin=spin, sim_index=sim_index)

                # The number of parameters.
                num_params = len(opt_params.param_vector)

                # Diagonal scaling.
                data_store.scaling_matrix = scaling_matrix[index]
                if data_store.scaling_matrix != None:
                    opt_params.param_vector = dot(inv(data_store.scaling_matrix), opt_params.param_vector)

            # Store the grid search options.
            opt_params.lower, opt_params.upper, opt_params.inc = None, None, None
            if lower != None:
                opt_params.lower = lower[index]
            if upper != None:
                opt_params.upper = upper[index]
            if inc != None:
                opt_params.inc = inc[index]

            # Scaling of values for the set function.
            if match('^[Ss]et', min_algor):
                opt_params.min_options = dot(inv(data_store.scaling_matrix), opt_params.min_options)

            # Linear constraints.
            if constraints:
                opt_params.A, opt_params.b = linear_constraints(num_params, model_type=data_store.model_type, spin=spin, scaling_matrix=data_store.scaling_matrix)
            else:
                opt_params.A, opt_params.b = None, None

            # Get the data for minimisation.
            minimise_data_setup(data_store, min_algor, num_data_sets, opt_params.min_options, spin=spin, sim_index=sim_index)

            # Setup the minimisation algorithm when constraints are present.
            if constraints and not match('^[Gg]rid', min_algor):
                algor = opt_params.min_options[0]
            else:
                algor = min_algor

            # Initialise the function to minimise (for back-calculation and LM minimisation).
            if min_algor == 'back_calc' or match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                mf = Mf(init_params=opt_params.param_vector, model_type=data_store.model_type, diff_type=data_store.diff_type, diff_params=data_store.diff_params, scaling_matrix=data_store.scaling_matrix, num_spins=data_store.num_spins, equations=data_store.equations, param_types=data_store.param_types, param_values=data_store.param_values, relax_data=data_store.ri_data, errors=data_store.ri_data_err, bond_length=data_store.r, csa=data_store.csa, num_frq=data_store.num_frq, frq=data_store.frq, num_ri=data_store.num_ri, remap_table=data_store.remap_table, noe_r1_table=data_store.noe_r1_table, ri_labels=data_store.ri_types, gx=data_store.gx, gh=data_store.gh, h_bar=data_store.h_bar, mu0=data_store.mu0, num_params=data_store.num_params, vectors=data_store.xh_unit_vectors)

            # Levenberg-Marquardt minimisation.
            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                # Total number of ri.
                number_ri = 0
                for k in range(len(ri_data_err)):
                    number_ri = number_ri + len(ri_data_err[k])

                # Reconstruct the error data structure.
                lm_error = zeros(number_ri, float64)
                index = 0
                for k in range(len(ri_data_err)):
                    lm_error[index:index+len(ri_data_err[k])] = ri_data_err[k]
                    index = index + len(ri_data_err[k])

                opt_params.min_options = opt_params.min_options + (mf.lm_dri, lm_error)

            # Back-calculation.
            if min_algor == 'back_calc':
                return mf.calc_ri()

            # Parallelised grid search for the diffusion parameter space.
            if match('^[Gg]rid', min_algor) and data_store.model_type == 'diff':
                # Print out.
                print("Parallelised diffusion tensor grid search.")

                # Loop over each grid subdivision.
                for subdivision in grid_split(divisions=processor.processor_size(), lower=opt_params.lower, upper=opt_params.upper, inc=opt_params.inc, verbosity=verbosity):
                    # Set the points.
                    opt_params.subdivision = subdivision

                    # Grid search initialisation.
                    command = MF_grid_command()

                    # Pass in the data and optimisation parameters.
                    command.store_data(deepcopy(data_store), deepcopy(opt_params))

                    # Set up the model-free memo and add it to the processor queue.
                    memo = MF_memo(model_free=self, model_type=data_store.model_type, spin=spin, sim_index=sim_index, scaling_matrix=data_store.scaling_matrix)
                    processor.add_to_queue(command, memo)

                # Execute the queued elements.
                processor.run_queue()

                # Exit this method.
                return

            # Normal grid search (command initialisation).
            if search('^[Gg]rid', min_algor):
                command = MF_grid_command()

            # Minimisation of all other model types (command initialisation).
            else:
                command = MF_minimise_command()

            # Pass in the data and optimisation parameters.
            command.store_data(deepcopy(data_store), deepcopy(opt_params))

            # Set up the model-free memo and add it to the processor queue.
            memo = MF_memo(model_free=self, model_type=data_store.model_type, spin=spin, sim_index=sim_index, scaling_matrix=data_store.scaling_matrix)
            processor.add_to_queue(command, memo)

        # Execute the queued elements.
        processor.run_queue()


    def model_desc(self, model_info=None):
        """Return a description of the model.

        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                The model description.
        @rtype:                 str
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global models.
        if model_type == 'all':
            return "Global model - all diffusion tensor parameters and spin specific model-free parameters."
        elif model_type == 'diff':
            return "Diffusion tensor model."

        # Spin specific model.
        else:
            # Get the spin container.
            spin, spin_id = return_spin_from_index(model_info, return_spin_id=True)

            # Return the description.
            return "Model-free model of spin '%s'." % spin_id


    def model_loop(self):
        """Generator method for looping over the models (global or local).

        If the model type is 'all' or 'diff', then this yields the single value of zero.  Otherwise
        the global spin index is yielded.


        @return:    The model index.  This index is zero for the global models or equal to the global spin
                    index (which covers the molecule, residue, and spin indices).
        @rtype:     int
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global model.
        if model_type == 'all' or model_type == 'diff':
            yield 0

        # Spin specific models.
        else:
            # Loop over the spins.
            global_index = -1
            for spin in spin_loop():
                # Increment the global spin index.
                global_index = global_index + 1

                # Yield the spin index.
                yield global_index


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword spin_id:       The spin identification string.  Either this or the instance keyword argument must be supplied.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are returned.  If None, then the appropriateness of global or local statistics is automatically determined.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of parameters (k), the number of data points (n), and the chi-squared value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Bad argument combination.
        if model_info == None and spin_id == None:
            raise RelaxError("Either the model_info or spin_id argument must be supplied.")
        elif model_info != None and spin_id != None:
            raise RelaxError("The model_info arg " + repr(model_info) + " and spin_id arg " + repr(spin_id) + " clash.  Only one should be supplied.")

        # Determine the model type.
        model_type = determine_model_type()

        # Determine if local or global statistics will be returned.
        if global_stats == None:
            if model_type in ['mf', 'local_tm']:
                global_stats = False
            else:
                global_stats = True

        # Statistics for a single residue.
        if not global_stats:
            # Get the SpinContainer.
            if spin_id:
                spin = return_spin(spin_id)
            else:
                spin = return_spin_from_index(model_info)

            # Skip deselected residues.
            if not spin.select:
                return None, None, None

            # Missing data sets.
            if not hasattr(spin, 'ri_data'):
                return None, None, None

            # Count the number of parameters.
            param_vector = assemble_param_vector(spin=spin)
            k = len(param_vector)

            # Count the number of data points.
            n = len(spin.ri_data)

            # The chi2 value.
            chi2 = spin.chi2

        # Global stats.
        elif global_stats:
            # Count the number of parameters.
            param_vector = assemble_param_vector()
            k = len(param_vector)

            # Count the number of data points.
            n = 0
            chi2 = 0
            for spin in spin_loop():
                # Skip deselected residues.
                if not spin.select:
                    continue

                # Skip residues with no relaxation data.
                if not hasattr(spin, 'ri_data') or not len(spin.ri_data):
                    continue

                n = n + len(spin.ri_data)

                # Local tm models.
                if model_type == 'local_tm':
                    chi2 = chi2 + spin.chi2

            # The chi2 value.
            if model_type != 'local_tm':
                if not hasattr(cdp, 'chi2'):
                    raise RelaxError("Global statistics are not available, most likely because the global model has not been optimised.")
                chi2 = cdp.chi2

        # Return the data.
        return k, n, chi2


    def model_type(self):
        """Return the type of the model, either being 'local' or 'global'.

        @return:            The model type, one of 'local' or 'global'.
        @rtype:             str
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global models.
        if model_type in ['all', 'diff']:
            return 'global'

        # Local models.
        else:
            return 'local'


    def num_instances(self):
        """Function for returning the number of instances.

        @return:    The number of instances used for optimisation.  Either the number of spins if
                    the local optimisations are setup ('mf' and 'local_tm'), or 1 for the global
                    models.
        @rtype:     int
        """

        # Test if sequence data exists.
        if not exists_mol_res_spin_data():
            return 0

        # Determine the model type.
        model_type = determine_model_type()

        # Sequence specific data.
        if model_type == 'mf' or model_type == 'local_tm':
            return count_spins()

        # Other data.
        elif model_type == 'diff' or model_type == 'all':
            return 1

        # Should not be here.
        else:
            raise RelaxFault


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Print out.
        if verbose:
            print("\nOver-fit spin deselection:")

        # Test if sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Is structural data required?
        need_vect = False
        if hasattr(cdp, 'diff_tensor') and (cdp.diff_tensor.type == 'spheroid' or cdp.diff_tensor.type == 'ellipsoid'):
            need_vect = True

        # Loop over the sequence.
        deselect_flag = False
        spin_count = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # The interatomic data.
            interatoms = interatomic.return_interatom_list(spin_id)

            # Loop over the interatomic data.
            dipole_relax = False
            for i in range(len(interatoms)):
                # No dipolar relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # The surrounding spins.
                if spin_id != interatoms[i].spin_id1:
                    spin_id2 = interatoms[i].spin_id1
                else:
                    spin_id2 = interatoms[i].spin_id2
                spin2 = return_spin(spin_id2)

                # Dipolar relaxation flag.
                dipole_relax = True

            # No relaxation mechanism.
            if not dipole_relax or not hasattr(spin, 'csa') or spin.csa == None:
                warn(RelaxDeselectWarning(spin_id, 'an absence of relaxation mechanisms'))
                spin.select = False
                deselect_flag = True
                continue

            # Data checks.
            if data_check:
                # The number of relaxation data points (and for infinite data).
                data_points = 0
                inf_data = False
                if hasattr(cdp, 'ri_ids') and hasattr(spin, 'ri_data'):
                    for id in cdp.ri_ids:
                        if id in spin.ri_data and spin.ri_data[id] != None:
                            data_points += 1

                            # Infinite data!
                            if isInf(spin.ri_data[id]):
                                inf_data = True

                # Infinite data.
                if inf_data:
                    warn(RelaxDeselectWarning(spin_id, 'infinite relaxation data'))
                    spin.select = False
                    deselect_flag = True
                    continue

                # Relaxation data must exist!
                if not hasattr(spin, 'ri_data'):
                    warn(RelaxDeselectWarning(spin_id, 'missing relaxation data'))
                    spin.select = False
                    deselect_flag = True
                    continue

                # Require 3 or more relaxation data points.
                elif data_points < 3:
                    warn(RelaxDeselectWarning(spin_id, 'insufficient relaxation data, 3 or more data points are required'))
                    spin.select = False
                    deselect_flag = True
                    continue

                # Require at least as many data points as params to prevent over-fitting.
                elif hasattr(spin, 'params') and spin.params and len(spin.params) > data_points:
                    warn(RelaxDeselectWarning(spin_id, 'over-fitting - more parameters than data points'))
                    spin.select = False
                    deselect_flag = True
                    continue

            # Test for structural data if required.
            for i in range(len(interatoms)):
                # No dipolar relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # Check the unit vectors.
                if need_vect:
                    if not hasattr(interatoms[i], 'vector') or interatoms[i].vector == None:
                        warn(RelaxDeselectWarning(spin_id, 'missing structural data'))
                        spin.select = False
                        deselect_flag = True
                        continue

            # Increment the spin number.
            spin_count += 1

        # No spins selected, so fail hard to prevent the user from going any further.
        if spin_count == 0:
            warn(RelaxWarning("No spins are selected therefore the optimisation or calculation cannot proceed."))

        # Final printout.
        if verbose and not deselect_flag:
            print("No spins have been deselected.")


    def print_model_title(self, prefix=None, model_info=None):
        """Print out the model title.

        @keyword prefix:        The starting text of the title.  This should be printed out first, followed by the model information text.
        @type prefix:           str
        @keyword model_info:    The model information from model_loop().
        @type model_info:       unknown
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Local models.
        if model_type == 'mf' or model_type == 'local_tm':
            spin, spin_id = return_spin_from_index(global_index=model_info, return_spin_id=True)
            text = "%sSpin '%s'" % (prefix, spin_id)

        # Global models.
        else:
            text = prefix + "Global model"

        # The printout.
        subsection(file=sys.stdout, text=text, prespace=2)


    def set_error(self, index, error, model_info=None):
        """Set the parameter errors.

        @param index:           The index of the parameter to set the errors for.
        @type index:            int
        @param error:           The error value.
        @type error:            float
        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        """

        # Parameter increment counter.
        inc = 0

        # Determine the model type.
        model_type = determine_model_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params', scope='spin')


        # Diffusion tensor parameter errors.
        ####################################

        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    cdp.diff_tensor.set(param='tm', value=error, category='err')

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    cdp.diff_tensor.set(param='tm', value=error, category='err')
                elif index == 1:
                    cdp.diff_tensor.set(param='Da', value=error, category='err')
                elif index == 2:
                    cdp.diff_tensor.set(param='theta', value=error, category='err')
                elif index == 3:
                    cdp.diff_tensor.set(param='phi', value=error, category='err')

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    cdp.diff_tensor.set(param='tm', value=error, category='err')
                elif index == 1:
                    cdp.diff_tensor.set(param='Da', value=error, category='err')
                elif index == 2:
                    cdp.diff_tensor.set(param='Dr', value=error, category='err')
                elif index == 3:
                    cdp.diff_tensor.set(param='alpha', value=error, category='err')
                elif index == 4:
                    cdp.diff_tensor.set(param='beta', value=error, category='err')
                elif index == 5:
                    cdp.diff_tensor.set(param='gamma', value=error, category='err')

                # Increment.
                inc = inc + 6


        # Model-free parameter errors for the model type 'all'.
        #######################################################

        if model_type == 'all':
            # Loop over the spins.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        setattr(spin, param + "_err", error)

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the model types 'mf' and 'local_tm'.
        ################################################################

        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip deselected residues.
            if not spin.select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    setattr(spin, param + "_err", error)

                # Increment.
                inc = inc + 1


    def set_param_values(self, param=None, value=None, index=None, spin_id=None, error=False, force=True):
        """Set the model-free parameter values.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword index:     The index for parameters which are of the list-type.  This is unused.
        @type index:        None or int
        @keyword spin_id:   The spin identification string, only used for spin specific parameters.
        @type spin_id:      None or str
        @keyword error:     A flag which if True will allow the parameter errors to be set instead of the values.
        @type error:        bool
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        is_str_list(param, 'parameter name')

        # Separate out the diffusion tensor parameters from the model-free parameters.
        diff_params = []
        diff_vals = []
        mf_params = []
        mf_vals = []
        for i in range(len(param)):
            # Diffusion tensor parameter.
            if self._PARAMS.scope(param[i]) == 'global':
                if error:
                    diff_params.append(param[i] + '_err')
                else:
                    diff_params.append(param[i])
                diff_vals.append(value[i])

            # Model-free parameter.
            else:
                mf_params.append(param[i])
                mf_vals.append(value[i])

        # Set the diffusion tensor parameters.
        if diff_params:
            diffusion_tensor.set(value=diff_vals, param=diff_params)

        # Set the model-free parameters.
        for i in range(len(mf_params)):
            # Check if it is a model-free parameter.
            if mf_params[i] not in self.data_names(set='params', scope='spin') and mf_params[i] not in self.data_names(set='generic', scope='spin'):
                raise RelaxError("The parameter '%s' is unknown.  It should be one of %s or %s" % (mf_params[i], self.data_names(set='params', scope='spin'), self.data_names(set='generic', scope='spin')))

            # The error object name.
            if error:
                mf_params[i] += '_err'

            # Set the parameter.
            for spin in spin_loop(spin_id):
                setattr(spin, mf_params[i], mf_vals[i])


    def set_selected_sim(self, select_sim, model_info=None):
        """Set all simulation selection flags.

        @param select_sim:      The selection flags.
        @type select_sim:       bool
        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global model.
        if model_type == 'all' or model_type == 'diff':
            cdp.select_sim = select_sim

        # Spin specific model.
        else:
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip if deselected.
            if not spin.select:
                return

            # Set the simulation flags.
            spin.select_sim = deepcopy(select_sim)


    def set_update(self, param, spin):
        """Function to update the other model-free parameters.

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """

        # S2f parameter.
        if param == 's2f':
            # Update S2 if S2s exists.
            if hasattr(spin, 's2s') and spin.s2s != None:
                spin.s2 = spin.s2f * spin.s2s


        # S2s parameter.
        if param == 's2s':
            # Update S2 if S2f exists.
            if hasattr(spin, 's2f') and spin.s2f != None:
                spin.s2 = spin.s2f * spin.s2s


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Determine the model type.
        model_type = determine_model_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params', scope='spin')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min', scope='spin')

        # List of diffusion tensor parameters.
        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                diff_params = ['tm']

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                diff_params = ['tm', 'Da', 'theta', 'phi']

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                diff_params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Diffusion tensor parameters and non spin specific minimisation statistics.
        if model_type == 'diff' or model_type == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(cdp.diff_tensor, sim_object_name):
                    raise RelaxError("Monte Carlo parameter values have already been set.")

            # Loop over the minimisation stats objects.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(cdp, sim_object_name):
                    raise RelaxError("Monte Carlo parameter values have already been set.")

        # Spin specific parameters.
        if model_type != 'diff':
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Loop over all the parameter names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Test if the simulation object already exists.
                    if hasattr(spin, sim_object_name):
                        raise RelaxError("Monte Carlo parameter values have already been set.")


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the global minimisation stats objects.
        for object_name in min_names:
            # Skip non-existent objects.
            if not hasattr(cdp, object_name):
                continue

            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(cdp, sim_object_name, [])

            # Get the simulation object.
            sim_object = getattr(cdp, sim_object_name)

            # Loop over the simulations.
            for j in range(cdp.sim_number):
                # Get the object.
                object = getattr(cdp, object_name)

                # Copy and append the data.
                sim_object.append(deepcopy(object))

        # Diffusion tensor parameters and non spin specific minimisation statistics.
        if model_type == 'diff' or model_type == 'all':
            # Set up the number of simulations.
            cdp.diff_tensor.set_sim_num(cdp.sim_number)

            # Loop over the parameters, setting the initial simulation values to those of the parameter value.
            for object_name in diff_params:
                for j in range(cdp.sim_number):
                    cdp.diff_tensor.set(param=object_name, value=deepcopy(getattr(cdp.diff_tensor, object_name)), category='sim', sim_index=j)

        # Spin specific parameters.
        if model_type != 'diff':
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Loop over all the data names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(spin, sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(spin, sim_object_name)

                    # Loop over the simulations.
                    for j in range(cdp.sim_number):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(spin, object_name)))

                # Loop over all the minimisation object names.
                for object_name in min_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(spin, sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(spin, sim_object_name)

                    # Loop over the simulations.
                    for j in range(cdp.sim_number):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(spin, object_name)))


    def sim_return_chi2(self, index=None, model_info=None):
        """Return the simulation chi-squared values.

        @keyword index:         The optional simulation index.
        @type index:            int
        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                The list of simulation chi-squared values.  If the index is supplied, only a single value will be returned.
        @rtype:                 list of float or float
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Single instance.
        if model_type == 'all' or model_type == 'diff':
            return cdp.chi2_sim

        # Multiple instances.
        else:
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Return the list.
            return spin.chi2_sim


    def sim_return_param(self, index, model_info=None):
        """Return the array of simulation parameter values.

        @param index:           The index of the parameter to return the array of values for.
        @type index:            int
        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                The array of simulation parameter values.
        @rtype:                 list of float
        """

        # Parameter increment counter.
        inc = 0

        # Determine the model type.
        model_type = determine_model_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params', scope='spin')


        # Diffusion tensor parameters.
        ##############################

        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    return cdp.diff_tensor.tm_sim

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    return cdp.diff_tensor.tm_sim
                elif index == 1:
                    return cdp.diff_tensor.Da_sim
                elif index == 2:
                    return cdp.diff_tensor.theta_sim
                elif index == 3:
                    return cdp.diff_tensor.phi_sim

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    return cdp.diff_tensor.tm_sim
                elif index == 1:
                    return cdp.diff_tensor.Da_sim
                elif index == 2:
                    return cdp.diff_tensor.Dr_sim
                elif index == 3:
                    return cdp.diff_tensor.alpha_sim
                elif index == 4:
                    return cdp.diff_tensor.beta_sim
                elif index == 5:
                    return cdp.diff_tensor.gamma_sim

                # Increment.
                inc = inc + 6


        # Model-free parameters for the model type 'all'.
        #################################################

        if model_type == 'all':
            # Loop over the spins.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Loop over the spin specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        return getattr(spin, param + "_sim")

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the model types 'mf' and 'local_tm'.
        ################################################################

        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip deselected spins.
            if not spin.select:
                return

            # Loop over the spin specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    return getattr(spin, param + "_sim")

                # Increment.
                inc = inc + 1


    def sim_return_selected(self, model_info=None):
        """Return the array of selected simulation flags for the spin.

        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                The array of selected simulation flags.
        @rtype:                 list of int
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Single instance.
        if model_type == 'all' or model_type == 'diff':
            return cdp.select_sim

        # Multiple instances.
        else:
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip if deselected.
            if not spin.select:
                return

            # Return the list.
            return spin.select_sim


    def skip_function(self, model_info=None):
        """Skip certain data.

        @keyword model_info:    The model information from model_loop().  This index is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                True if the data should be skipped, False otherwise.
        @rtype:                 bool
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Sequence specific data.
        if (model_type == 'mf' or model_type == 'local_tm') and not return_spin_from_index(model_info).select:
            return True

        # Don't skip.
        return False



class Data_container:
    """Empty class to be used for data storage."""
