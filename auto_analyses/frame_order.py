###############################################################################
#                                                                             #
# Copyright (C) 2011-2014 Edward d'Auvergne                                   #
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
"""The full frame order analysis.


The nested model parameter copying protocol
===========================================

To allow the analysis to complete in under 1,000,000 years, the trick of copying parameters from simpler nested models is used in this auto-analysis.  The protocol is split into four categories for the average domain position, the pivot point, the motional eigenframe and the parameters of ordering.  These use the fact that the free rotor and torsionless models are the two extrema of the models where the torsion angle is restricted, whereby sigma_max is pi and 0 respectively.
"""


# Python module imports.
from numpy import float64, zeros
from os import F_OK, access, getcwd, sep
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.arg_check import is_float, is_int, is_str
from lib.errors import RelaxError
from lib.frame_order.conversions import convert_axis_alpha_to_spherical
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.io import open_write_file
from lib.order.order_parameters import iso_cone_theta_to_S
from lib.text.sectioning import section, subsection, title
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control.pipes import get_pipe
from pipe_control.structure.mass import pipe_centre_of_mass
from prompt.interpreter import Interpreter
from specific_analyses.frame_order.data import generate_pivot
from specific_analyses.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_LIST_FREE_ROTORS, MODEL_LIST_ISO_CONE, MODEL_LIST_NONREDUNDANT, MODEL_LIST_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from status import Status; status = Status()


class Frame_order_analysis:
    """The frame order auto-analysis protocol."""

    def __init__(self, data_pipe_full=None, data_pipe_subset=None, pipe_bundle=None, results_dir=None, opt_rigid=None, opt_subset=None, opt_full=None, opt_mc=None, mc_sim_num=500, models=MODEL_LIST_NONREDUNDANT, brownian_step_size=2.0, brownian_snapshot=10, brownian_total=1000):
        """Perform the full frame order analysis.

        @param data_pipe_full:          The name of the data pipe containing all of the RDC and PCS data.
        @type data_pipe_full:           str
        @param data_pipe_subset:        The name of the data pipe containing all of the RDC data but only a small subset of ~5 PCS points.
        @type data_pipe_subset:         str
        @keyword pipe_bundle:           The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:              str
        @keyword results_dir:           The directory where files are saved in.
        @type results_dir:              str
        @keyword opt_rigid:             The grid search, zooming grid search and minimisation settings object for the rigid frame order model.
        @type opt_rigid:                Optimisation_settings instance
        @keyword opt_subset:            The grid search, zooming grid search and minimisation settings object for optimisation of all models, excluding the rigid model, for the PCS data subset.
        @type opt_subset:               Optimisation_settings instance
        @keyword opt_full:              The grid search, zooming grid search and minimisation settings object for optimisation of all models, excluding the rigid model, for the full data set.
        @type opt_full:                 Optimisation_settings instance
        @keyword opt_mc:                The grid search, zooming grid search and minimisation settings object for optimisation of the Monte Carlo simulations.  Any grid search settings will be ignored, as only the minimise.execute user function is run for the simulations.  And only the settings for the first iteration of the object will be accessed and used - iterative optimisation will be ignored.
        @type opt_mc:                   Optimisation_settings instance
        @keyword mc_sim_num:            The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:               int
        @keyword models:                The frame order models to use in the analysis.  The 'rigid' model must be included as this is essential for the analysis.
        @type models:                   list of str
        @keyword brownian_step_size:    The step_size argument for the pseudo-Brownian dynamics simulation frame_order.simulate user function.
        @type brownian_step_size:       float
        @keyword brownian_snapshot:     The snapshot argument for the pseudo-Brownian dynamics simulation frame_order.simulate user function.
        @type brownian_snapshot:        int
        @keyword brownian_total:        The total argument for the pseudo-Brownian dynamics simulation frame_order.simulate user function.
        @type brownian_total:           int
        """

        # Execution lock.
        status.exec_lock.acquire(pipe_bundle, mode='auto-analysis')

        # Execute the full protocol.
        try:
            # Initial printout.
            title(file=sys.stdout, text="Frame order auto-analysis", prespace=7)

            # Store the args.
            self.data_pipe_full = data_pipe_full
            self.data_pipe_subset = data_pipe_subset
            self.pipe_bundle = pipe_bundle
            self.opt_rigid = opt_rigid
            self.opt_subset = opt_subset
            self.opt_full = opt_full
            self.opt_mc = opt_mc
            self.mc_sim_num = mc_sim_num
            self.brownian_step_size = brownian_step_size
            self.brownian_snapshot = brownian_snapshot
            self.brownian_total = brownian_total

            # Re-order the models to enable the parameter nesting protocol.
            self.models = self.reorder_models(models)

            # A dictionary and list of the data pipe names.
            self.pipe_name_dict = {}
            self.pipe_name_list = []

            # Project directory (i.e. directory containing the model-free model results and the newly generated files)
            if results_dir:
                self.results_dir = results_dir + sep
            else:
                self.results_dir = getcwd() + sep

            # Data checks.
            self.check_vars()

            # Load the interpreter.
            self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
            self.interpreter.populate_self()
            self.interpreter.on(verbose=False)

            # Output the starting time.
            self.interpreter.time()

            # The nested model optimisation protocol.
            self.nested_models()

            # The final results does not already exist.
            if not self.read_results(model='final', pipe_name='final'):
                # Model selection.
                self.interpreter.model_selection(method='AIC', modsel_pipe='final', pipes=self.pipe_name_list)

                # The numerical optimisation settings.
                opt = self.opt_mc
                self.sobol_setup(opt.get_min_sobol_info(0))

                # Monte Carlo simulations.
                self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
                self.interpreter.monte_carlo.create_data()
                self.interpreter.monte_carlo.initial_values()
                self.interpreter.minimise.execute(opt.get_min_algor(0), func_tol=opt.get_min_func_tol(0), max_iter=opt.get_min_max_iter(0))
                self.interpreter.eliminate()
                self.interpreter.monte_carlo.error_analysis()

                # Finish.
                self.interpreter.results.write(file='results', dir=self.results_dir+'final', force=True)

            # Output the finishing time.
            self.interpreter.time()

            # Visualisation of the final results.
            self.visualisation(model='final')

        # Clean up.
        finally:
            # Finish and unlock execution.
            status.exec_lock.release()

        # Save the final program state.
        self.interpreter.state.save('final_state', dir=self.results_dir, force=True)


    def axis_permutation_analysis(self, model=None):
        """Handle the two local minima in the pseudo-elliptic models.

        This involves creating a new data pipe for the pseudo-elliptic models, permuting the motional parameters, and performing an optimisation.  This will explore the second minimum.


        @keyword model:     The frame order model to visualise.  This should match the model of the current data pipe, unless the special value of 'final' is used to indicate the visualisation of the final results.
        @type model:        str
        """

        # Nothing to do.
        if model not in MODEL_LIST_ISO_CONE + MODEL_LIST_PSEUDO_ELLIPSE:
            return

        # The permutations.
        perms = ['A']
        if model in MODEL_LIST_PSEUDO_ELLIPSE:
            perms.append('B')

        # Loop over all permutations.
        for perm in perms:
            # The title printout.
            title = model[0].upper() + model[1:]
            text = "Axis permutation '%s' of the %s frame order model" % (perm, title)
            section(file=sys.stdout, text=text, prespace=5)

            # Output the model staring time.
            self.interpreter.time()

            # A new model name.
            perm_model = "%s permutation %s" % (model, perm)

            # The data pipe name.
            self.pipe_name_dict[perm_model] = '%s permutation %s - %s' % (title, perm, self.pipe_bundle)
            self.pipe_name_list.append(self.pipe_name_dict[perm_model])

            # The results file already exists, so read its contents instead.
            if self.read_results(model=perm_model, pipe_name=self.pipe_name_dict[perm_model]):
                # Re-perform model elimination just in case.
                self.interpreter.eliminate()

                # The PDB representation of the model and visualisation script (in case this was not completed correctly).
                self.visualisation(model=perm_model)

                # Jump to the next permutation.
                continue

            # Copy the data pipe, and add it to the list so it is included in the model selection.
            self.interpreter.pipe.copy(pipe_from=self.pipe_name_dict[model], pipe_to=self.pipe_name_dict[perm_model])

            # Switch to the new pipe.
            self.interpreter.pipe.switch(pipe_name=self.pipe_name_dict[perm_model])

            # Permute the axes.
            self.interpreter.frame_order.permute_axes(permutation=perm)

            # Minimise with only the last optimisation settings (for the full data set).
            opt = self.opt_full
            for i in opt.loop_min():
                pass

            # The numerical optimisation settings.
            self.sobol_setup(opt.get_min_sobol_info(i))

            # Perform the optimisation.
            self.interpreter.minimise.execute(min_algor=opt.get_min_algor(i), func_tol=opt.get_min_func_tol(i), max_iter=opt.get_min_max_iter(i))

            # Results printout.
            self.print_results()

            # Model elimination.
            self.interpreter.eliminate()

            # Save the results.
            self.interpreter.results.write(dir=self.model_directory(perm_model), force=True)

            # The PDB representation of the model and visualisation script.
            self.visualisation(model=perm_model)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe bundle.
        if not isinstance(self.pipe_bundle, str):
            raise RelaxError("The pipe bundle name '%s' is invalid." % self.pipe_bundle)

        # Minimisation variables.
        if not isinstance(self.mc_sim_num, int):
            raise RelaxError("The mc_sim_num user variable '%s' is incorrectly set.  It should be an integer." % self.mc_sim_num)


    def custom_grid_incs(self, model, inc=None):
        """Set up a customised grid search increment number for each model.

        @param model:   The frame order model.
        @type model:    str
        @keyword inc:   The number of grid search increments to use for each dimension.
        @type inc:      int
        @return:        The list of increment values.
        @rtype:         list of int and None
        """

        # Initialise the structure.
        incs = []

        # The pivot parameters.
        if hasattr(cdp, 'pivot_fixed') and not cdp.pivot_fixed:
            # Optimise the pivot for the rotor model.
            if model == MODEL_ROTOR:
                incs += [inc, inc, inc]

            # Otherwise use preset values (copied from other models).
            else:
                incs += [None, None, None]

        # The 2nd pivot point parameters - the minimum inter rotor axis distance.
        if model in [MODEL_DOUBLE_ROTOR]:
            incs += [inc]

        # The average domain position parameters.
        if model == MODEL_FREE_ROTOR:
            incs += [inc, inc, inc, inc, inc]
        elif model in [MODEL_ISO_CONE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]:
            incs += [None, None, None, None, None]
        else:
            incs += [None, None, None, None, None, None]

        # The motional eigenframe and order parameters - the rotor model.
        if model == MODEL_ROTOR:
            incs += [inc, inc]

        # The motional eigenframe and order parameters - the free rotor model.
        if model == MODEL_FREE_ROTOR:
            incs += [None]

        # The motional eigenframe and order parameters - the torsionless isotropic cone model.
        if model == MODEL_ISO_CONE_TORSIONLESS:
            incs += [None, None, None]

        # The motional eigenframe and order parameters - the free rotor isotropic cone model.
        if model == MODEL_ISO_CONE_FREE_ROTOR:
            incs += [None, None, None]

        # The motional eigenframe and order parameters - the isotropic cone model.
        if model == MODEL_ISO_CONE:
            incs += [None, None, inc, None]

        # The motional eigenframe and order parameters - the torsionless pseudo-elliptic cone model.
        if model == MODEL_PSEUDO_ELLIPSE_TORSIONLESS:
            incs += [None, None, None, None, None]

        # The motional eigenframe and order parameters - the free rotor pseudo-elliptic cone model.
        if model == MODEL_PSEUDO_ELLIPSE_FREE_ROTOR:
            incs += [None, None, None, None, None]

        # The motional eigenframe and order parameters - the pseudo-elliptic cone model.
        if model == MODEL_PSEUDO_ELLIPSE:
            incs += [inc, inc, inc, None, inc, None]

        # The motional eigenframe and order parameters - the double rotor model.
        if model == MODEL_DOUBLE_ROTOR:
            incs += [None, None, None, inc, inc]

        # Return the increment list.
        return incs


    def model_directory(self, model):
        """Return the directory to be used for the model.

        @param model:   The frame order model.
        @type model:    str
        """

        # Convert the model name.
        dir = model.replace(' ', '_')
        dir = dir.replace(',', '')

        # Return the full path.
        return self.results_dir + dir


    def nested_params_ave_dom_pos(self, model):
        """Copy the average domain parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_RIGID, MODEL_FREE_ROTOR]:
            # Printout.
            print("No nesting of the average domain position parameters for the '%s' model." % model)

            # Exit.
            return

        # The average position from the rigid model.
        if model not in MODEL_LIST_FREE_ROTORS:
            # Printout.
            print("Obtaining the average position from the rigid model.")

            # Get the rigid data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_RIGID])

            # Copy the average position parameters from the rigid model.
            cdp.ave_pos_x = pipe.ave_pos_x
            cdp.ave_pos_y = pipe.ave_pos_y
            cdp.ave_pos_z = pipe.ave_pos_z
            cdp.ave_pos_alpha = pipe.ave_pos_alpha
            cdp.ave_pos_beta = pipe.ave_pos_beta
            cdp.ave_pos_gamma = pipe.ave_pos_gamma

        # The average position from the free rotor model.
        else:
            # Printout.
            print("Obtaining the average position from the free rotor model.")

            # Get the free rotor data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_FREE_ROTOR])

            # Copy the average position parameters from the free rotor model.
            cdp.ave_pos_x = pipe.ave_pos_x
            cdp.ave_pos_y = pipe.ave_pos_y
            cdp.ave_pos_z = pipe.ave_pos_z
            cdp.ave_pos_beta = pipe.ave_pos_beta
            cdp.ave_pos_gamma = pipe.ave_pos_gamma


    def nested_params_eigenframe(self, model):
        """Copy the eigenframe parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_ROTOR, MODEL_PSEUDO_ELLIPSE]:
            # Printout.
            print("No nesting of the eigenframe parameters for the '%s' model." % model)

            # Exit.
            return

        # The cone axis from the rotor model.
        if model in [MODEL_FREE_ROTOR, MODEL_ISO_CONE]:
            # Printout.
            print("Obtaining the cone axis from the rotor model.")

            # Get the rotor data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ROTOR])

            # The cone axis as the axis alpha angle.
            if model == MODEL_FREE_ROTOR:
                cdp.axis_alpha = pipe.axis_alpha

            # The cone axis from the axis alpha angle to spherical angles.
            if model == MODEL_ISO_CONE:
                cdp.axis_theta, cdp.axis_phi = convert_axis_alpha_to_spherical(alpha=pipe.axis_alpha, pivot=generate_pivot(order=1, pipe_name=self.pipe_name_dict[MODEL_ROTOR]), point=pipe_centre_of_mass(verbosity=0))

        # The cone axis from the isotropic cone model.
        elif model in [MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS]:
            # Printout.
            print("Obtaining the cone axis from the isotropic cone model.")

            # Get the iso cone data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ISO_CONE])

            # Copy the cone axis parameters.
            cdp.axis_theta = pipe.axis_theta
            cdp.axis_phi = pipe.axis_phi

        # The full eigenframe from the pseudo-ellipse model.
        elif model in [MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_DOUBLE_ROTOR]:
            # Printout.
            print("Obtaining the full eigenframe from the pseudo-ellipse model.")

            # Get the pseudo-ellipse data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_PSEUDO_ELLIPSE])

            # Copy the three Euler angles.
            cdp.eigen_alpha = pipe.eigen_alpha
            cdp.eigen_beta = pipe.eigen_beta
            cdp.eigen_gamma = pipe.eigen_gamma


    def nested_params_order(self, model):
        """Copy the order parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_ROTOR, MODEL_DOUBLE_ROTOR]:
            # Printout.
            print("No nesting of the order parameters for the '%s' model." % model)

            # Exit.
            return

        # The cone angle from the isotropic cone model.
        if model in [MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_ISO_CONE_FREE_ROTOR]:
            # Get the iso cone data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ISO_CONE])

            # Copy the cone angle directly.
            if model == MODEL_ISO_CONE_TORSIONLESS:
                print("Obtaining the cone angle from the isotropic cone model.")
                cdp.cone_theta = pipe.cone_theta

            # Copy as the X cone angle.
            elif model == MODEL_PSEUDO_ELLIPSE:
                print("Obtaining the cone X angle from the isotropic cone model.")
                cdp.cone_theta_x = pipe.cone_theta

            # Convert to the order parameter S.
            elif model == MODEL_ISO_CONE_FREE_ROTOR:
                print("Obtaining the cone order parameter from the isotropic cone model.")
                cdp.cone_s1 = iso_cone_theta_to_S(pipe.cone_theta)

        # The X and Y cone angles from the pseudo-ellipse model.
        elif model in [MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]:
            # Printout.
            print("Obtaining the cone X and Y angles from the pseudo-ellipse model.")

            # Get the pseudo-ellipse data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_PSEUDO_ELLIPSE])

            # Copy the cone axis.
            cdp.cone_theta_x = pipe.cone_theta_x
            cdp.cone_theta_y = pipe.cone_theta_y


        # The torsion from the rotor model.
        if model in [MODEL_ISO_CONE, MODEL_PSEUDO_ELLIPSE]:
            # Printout.
            print("Obtaining the torsion angle from the rotor model.")

            # Get the rotor data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ROTOR])

            # Copy the cone axis.
            cdp.cone_sigma_max = pipe.cone_sigma_max


    def nested_params_pivot(self, model):
        """Copy the pivot parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_ROTOR]:
            # Printout.
            print("No nesting of the pivot parameters for the '%s' model." % model)

            # Exit.
            return

        # The pivot from the rotor model.
        print("Obtaining the pivot point from the rotor model.")

        # Get the iso cone data pipe.
        pipe = get_pipe(self.pipe_name_dict[MODEL_ROTOR])

        # Copy the pivot parameters.
        cdp.pivot_x = pipe.pivot_x
        cdp.pivot_y = pipe.pivot_y
        cdp.pivot_z = pipe.pivot_z


    def nested_models(self):
        """Protocol for the nested optimisation of the frame order models."""

        # First optimise the rigid model using all data.
        self.optimise_rigid()

        # Iteratively optimise the frame order models.
        for model in self.models:
            # Skip the already optimised rigid model.
            if model == MODEL_RIGID:
                continue

            # The model title.
            title = model[0].upper() + model[1:]

            # Printout.
            section(file=sys.stdout, text="%s frame order model"%title, prespace=5)

            # Output the model staring time.
            self.interpreter.time()

            # The data pipe name.
            self.pipe_name_dict[model] = '%s - %s' % (title, self.pipe_bundle)
            self.pipe_name_list.append(self.pipe_name_dict[model])

            # The results file already exists, so read its contents instead.
            if self.read_results(model=model, pipe_name=self.pipe_name_dict[model]):
                # Re-perform model elimination just in case.
                self.interpreter.eliminate()

                # The PDB representation of the model and visualisation script (in case this was not completed correctly).
                self.visualisation(model=model)

                # Perform the axis permutation analysis.
                self.axis_permutation_analysis(model=model)

                # Skip to the next model.
                continue

            # Create the data pipe using the full data set, and switch to it.
            self.interpreter.pipe.copy(self.data_pipe_subset, self.pipe_name_dict[model], bundle_to=self.pipe_bundle)
            self.interpreter.pipe.switch(self.pipe_name_dict[model])

            # Select the Frame Order model.
            self.interpreter.frame_order.select_model(model=model)

            # Copy nested parameters.
            subsection(file=sys.stdout, text="Parameter nesting.")
            self.nested_params_ave_dom_pos(model)
            self.nested_params_eigenframe(model)
            self.nested_params_pivot(model)
            self.nested_params_order(model)

            # Zooming grid search.
            opt = self.opt_subset
            for i in opt.loop_grid():
                # Set the zooming grid search level.
                zoom = opt.get_grid_zoom_level(i)
                if zoom != None:
                    self.interpreter.minimise.grid_zoom(level=zoom)

<<<<<<< .working
            # Grid search.
            incs = self.custom_grid_incs(model)
            self.interpreter.grid_search(inc=incs)
=======
                # The numerical optimisation settings.
                self.sobol_setup(opt.get_grid_sobol_info(i))
>>>>>>> .merge-right.r24836

                # Set up the custom grid increments.
                incs = self.custom_grid_incs(model, inc=opt.get_grid_inc(i))

                # Perform the grid search.
                self.interpreter.minimise.grid_search(inc=incs)

            # Minimise (for the PCS data subset and full RDC set).
<<<<<<< .working
            for i in range(len(self.num_int_pts_subset)):
                self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_subset[i])
                self.interpreter.minimise(self.min_algor, func_tol=self.func_tol_subset[i])
=======
            for i in opt.loop_min():
                # The numerical optimisation settings.
                self.sobol_setup(opt.get_min_sobol_info(i))
>>>>>>> .merge-right.r24836

                # Perform the optimisation.
                self.interpreter.minimise.execute(min_algor=opt.get_min_algor(i), func_tol=opt.get_min_func_tol(i), max_iter=opt.get_min_max_iter(i))

            # Copy the PCS data.
            self.interpreter.pcs.copy(pipe_from=self.data_pipe_full, pipe_to=self.pipe_name_dict[model])

            # Reset the selection status.
            for spin, spin_id in spin_loop(return_id=True, skip_desel=False):
                # Get the spin from the original pipe.
                spin_orig = return_spin(spin_id=spin_id, pipe=self.data_pipe_full)

                # Reset the spin selection.
                spin.select = spin_orig.select

            # Minimise (for the full data set).
<<<<<<< .working
            for i in range(len(self.num_int_pts_full)):
                self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_full[i])
                self.interpreter.minimise(self.min_algor, func_tol=self.func_tol_full[i])
=======
            opt = self.opt_full
            for i in opt.loop_min():
                # The numerical optimisation settings.
                self.sobol_setup(opt.get_min_sobol_info(i))
>>>>>>> .merge-right.r24836

                # Perform the optimisation.
                self.interpreter.minimise.execute(min_algor=opt.get_min_algor(i), func_tol=opt.get_min_func_tol(i), max_iter=opt.get_min_max_iter(i))

            # Results printout.
            self.print_results()

            # Model elimination.
            self.interpreter.eliminate()

            # Save the results.
            self.interpreter.results.write(dir=self.model_directory(model), force=True)

            # The PDB representation of the model and visualisation script.
            self.visualisation(model=model)

            # Perform the axis permutation analysis.
            self.axis_permutation_analysis(model=model)


    def optimise_rigid(self):
        """Optimise the rigid frame order model.

        The Sobol' integration is not used here, so the algorithm is different to the other frame order models.
        """

        # The model.
        model = MODEL_RIGID
        title = model[0].upper() + model[1:]

        # Print out.
        section(file=sys.stdout, text="%s frame order model"%title, prespace=5)

        # Output the model staring time.
        self.interpreter.time()

        # The data pipe name.
        self.pipe_name_dict[model] = '%s - %s' % (title, self.pipe_bundle)
        self.pipe_name_list.append(self.pipe_name_dict[model])

        # The results file already exists, so read its contents instead.
        if self.read_results(model=model, pipe_name=self.pipe_name_dict[model]):
            # The PDB representation of the model and the pseudo-Brownian dynamics simulation (in case this was not completed correctly).
            self.interpreter.frame_order.pdb_model(dir=self.model_directory(model), force=True)
            self.interpreter.frame_order.simulate(dir=self.model_directory(model), step_size=self.brownian_step_size, snapshot=self.brownian_snapshot, total=self.brownian_total, force=True)

            # Nothing more to do.
            return

        # Create the data pipe using the full data set, and switch to it.
        self.interpreter.pipe.copy(self.data_pipe_full, self.pipe_name_dict[model], bundle_to=self.pipe_bundle)
        self.interpreter.pipe.switch(self.pipe_name_dict[model])

        # Select the Frame Order model.
        self.interpreter.frame_order.select_model(model=model)

        # Split zooming grid search for the translation.
        print("\n\nTranslation active - splitting the grid search and iterating.")
        self.interpreter.value.set(param='ave_pos_x', val=0.0)
        self.interpreter.value.set(param='ave_pos_y', val=0.0)
        self.interpreter.value.set(param='ave_pos_z', val=0.0)
        opt = self.opt_rigid
        for i in opt.loop_grid():
            # Set the zooming grid search level.
            zoom = opt.get_grid_zoom_level(i)
            if zoom != None:
                self.interpreter.minimise.grid_zoom(level=zoom)

            # The numerical optimisation settings.
            self.sobol_setup(opt.get_grid_sobol_info(i))

            # The number of increments.
            inc = opt.get_grid_inc(i)

            # First optimise the rotation.
            self.interpreter.minimise.grid_search(inc=[None, None, None, inc, inc, inc], skip_preset=False)

            # Then the translation.
            self.interpreter.minimise.grid_search(inc=[inc, inc, inc, None, None, None], skip_preset=False)

        # Minimise.
<<<<<<< .working
        self.interpreter.minimise(self.min_algor)
=======
        for i in opt.loop_min():
            # The numerical optimisation settings.
            self.sobol_setup(opt.get_min_sobol_info(i))
>>>>>>> .merge-right.r24836

            # Perform the optimisation.
            self.interpreter.minimise.execute(min_algor=opt.get_min_algor(i), func_tol=opt.get_min_func_tol(i), max_iter=opt.get_min_max_iter(i))

        # Results printout.
        self.print_results()

        # Save the results.
        self.interpreter.results.write(dir=self.model_directory(model), force=True)

        # The PDB representation of the model and the pseudo-Brownian dynamics simulation.
        self.interpreter.frame_order.pdb_model(dir=self.model_directory(model), force=True)
        self.interpreter.frame_order.simulate(dir=self.model_directory(model), step_size=self.brownian_step_size, snapshot=self.brownian_snapshot, total=self.brownian_total, force=True)


    def print_results(self):
        """Print out the optimisation results for the current data pipe."""

        # Header.
        sys.stdout.write("\nFinal optimisation results:\n")

        # Formatting string.
        format_float = "    %-20s %20.15f\n"
        format_vect = "    %-20s %20s\n"

        # Pivot.
        sys.stdout.write("\nPivot point:\n")
        if hasattr(cdp, 'pivot_x'):
            sys.stdout.write(format_float % ('x:', cdp.pivot_x))
        if hasattr(cdp, 'pivot_y'):
            sys.stdout.write(format_float % ('y:', cdp.pivot_y))
        if hasattr(cdp, 'pivot_z'):
            sys.stdout.write(format_float % ('z:', cdp.pivot_z))

        # Average position.
        if hasattr(cdp, 'ave_pos_x') or hasattr(cdp, 'ave_pos_alpha') or hasattr(cdp, 'ave_pos_beta') or hasattr(cdp, 'ave_pos_gamma'):
            sys.stdout.write("\nAverage moving domain position:\n")
        if hasattr(cdp, 'ave_pos_x'):
            sys.stdout.write(format_float % ('x:', cdp.ave_pos_x))
        if hasattr(cdp, 'ave_pos_y'):
            sys.stdout.write(format_float % ('y:', cdp.ave_pos_y))
        if hasattr(cdp, 'ave_pos_z'):
            sys.stdout.write(format_float % ('z:', cdp.ave_pos_z))
        if hasattr(cdp, 'ave_pos_alpha'):
            sys.stdout.write(format_float % ('alpha:', cdp.ave_pos_alpha))
        if hasattr(cdp, 'ave_pos_beta'):
            sys.stdout.write(format_float % ('beta:', cdp.ave_pos_beta))
        if hasattr(cdp, 'ave_pos_gamma'):
            sys.stdout.write(format_float % ('gamma:', cdp.ave_pos_gamma))

        # Frame order eigenframe.
        if hasattr(cdp, 'eigen_alpha') or hasattr(cdp, 'eigen_beta') or hasattr(cdp, 'eigen_gamma') or hasattr(cdp, 'axis_theta') or hasattr(cdp, 'axis_phi'):
            sys.stdout.write("\nFrame order eigenframe:\n")
        if hasattr(cdp, 'eigen_alpha'):
            sys.stdout.write(format_float % ('eigen alpha:', cdp.eigen_alpha))
        if hasattr(cdp, 'eigen_beta'):
            sys.stdout.write(format_float % ('eigen beta:', cdp.eigen_beta))
        if hasattr(cdp, 'eigen_gamma'):
            sys.stdout.write(format_float % ('eigen gamma:', cdp.eigen_gamma))

        # The cone axis.
        if hasattr(cdp, 'axis_theta'):
            # The angles.
            sys.stdout.write(format_float % ('axis theta:', cdp.axis_theta))
            sys.stdout.write(format_float % ('axis phi:', cdp.axis_phi))

            # The axis.
            axis = zeros(3, float64)
            spherical_to_cartesian([1.0, cdp.axis_theta, cdp.axis_phi], axis)
            sys.stdout.write(format_vect % ('axis:', axis))

        # Frame ordering.
        if hasattr(cdp, 'cone_theta_x') or hasattr(cdp, 'cone_theta_y') or hasattr(cdp, 'cone_theta') or hasattr(cdp, 'cone_s1') or hasattr(cdp, 'cone_sigma_max'):
            sys.stdout.write("\nFrame ordering:\n")
        if hasattr(cdp, 'cone_theta_x'):
            sys.stdout.write(format_float % ('cone theta_x:', cdp.cone_theta_x))
        if hasattr(cdp, 'cone_theta_y'):
            sys.stdout.write(format_float % ('cone theta_y:', cdp.cone_theta_y))
        if hasattr(cdp, 'cone_theta'):
            sys.stdout.write(format_float % ('cone theta:', cdp.cone_theta))
        if hasattr(cdp, 'cone_s1'):
            sys.stdout.write(format_float % ('cone s1:', cdp.cone_s1))
        if hasattr(cdp, 'cone_sigma_max'):
            sys.stdout.write(format_float % ('sigma_max:', cdp.cone_sigma_max))

        # Minimisation statistics.
        if hasattr(cdp, 'chi2'):
            sys.stdout.write("\nMinimisation statistics:\n")
        if hasattr(cdp, 'chi2'):
            sys.stdout.write(format_float % ('chi2:', cdp.chi2))

        # Final spacing.
        sys.stdout.write("\n")


    def read_results(self, model=None, pipe_name=None):
        """Attempt to read old results files.

        @keyword model:     The frame order model.
        @type model:        str
        @keyword pipe_name: The name of the data pipe to use for this model.
        @type pipe_name:    str
        @return:            True if the file exists and has been read, False otherwise.
        @rtype:             bool
        """

        # The file name.
        path = self.model_directory(model) + sep + 'results.bz2'

        # The file does not exist.
        if not access(path, F_OK):
            return False

        # Create an empty data pipe.
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type='frame order')

        # Read the results file.
        self.interpreter.results.read(path)

        # Results printout.
        self.print_results()

        # Success.
        return True


    def reorder_models(self, models=None):
        """Reorder the frame order models to enable the nested parameter copying protocol.

        @keyword models:    The frame order models to be used in the auto-analysis.
        @type models:       list of str
        @return:            The reordered frame order models.
        @rtype:             list of str
        """

        # The correct order for the nesting protocol.
        order = [
            MODEL_RIGID,
            MODEL_ROTOR,
            MODEL_ISO_CONE,
            MODEL_PSEUDO_ELLIPSE,
            MODEL_ISO_CONE_TORSIONLESS,
            MODEL_PSEUDO_ELLIPSE_TORSIONLESS,
            MODEL_FREE_ROTOR,
            MODEL_ISO_CONE_FREE_ROTOR,
            MODEL_PSEUDO_ELLIPSE_FREE_ROTOR,
            MODEL_DOUBLE_ROTOR
        ]

        # Create the new list.
        new = []
        for i in range(len(order)):
            if order[i] in models:
                new.append(order[i])

        # Sanity check - the models must all be in this list.
        for i in range(len(models)):
            if models[i] not in order:
                raise RelaxError("The frame order model '%s' is unknown." % models[i])

        # Return the reordered list.
        return new


    def sobol_setup(self, info=None):
        """Correctly handle the frame_order.sobol_setup user function.

        @keyword info:  The information from the Optimisation_settings.get_*_sobol_info() function.
        @type info:     tuple of int or None
        """

        # Unpack the info.
        max_num, oversample = info

        # Nothing to do.
        if max_num == None:
            return

        # No oversampling specified.
        if oversample == None:
            self.interpreter.frame_order.sobol_setup(max_num=max_num)

        # Full setup.
        else:
            self.interpreter.frame_order.sobol_setup(max_num=max_num, oversample=oversample)


    def visualisation(self, model=None):
        """Create visual representations of the frame order results for the given model.

        This includes a PDB representation of the motions (the 'cone.pdb' file located in each model directory) together with a relax script for displaying the average domain positions together with the cone/motion representation in PyMOL (the 'pymol_display.py' file, also created in the model directory).

        @keyword model:     The frame order model to visualise.  This should match the model of the current data pipe, unless the special value of 'final' is used to indicate the visualisation of the final results.
        @type model:        str
        """

        # Sanity check.
        if model != 'final' and model.replace(' permutation A', '').replace(' permutation B', '') != cdp.model:
            raise RelaxError("The model '%s' does not match the model '%s' of the current data pipe." % (model.replace(' permuted', ''), cdp.model))

        # The PDB representation of the model and the pseudo-Brownian dynamics simulation.
        self.interpreter.frame_order.pdb_model(dir=self.model_directory(model), force=True)
        self.interpreter.frame_order.simulate(dir=self.model_directory(model), step_size=self.brownian_step_size, snapshot=self.brownian_snapshot, total=self.brownian_total, force=True)

        # Create the visualisation script.
        subsection(file=sys.stdout, text="Creating a PyMOL visualisation script.")
        script = open_write_file(file_name='pymol_display.py', dir=self.model_directory(model), force=True)

        # Add a comment for the user.
        script.write("# relax script for displaying the frame order results of this '%s' model in PyMOL.\n\n" % model)

        # The script contents.
        script.write("# PyMOL visualisation.\n")
        script.write("pymol.frame_order()\n")

        # Close the file.
        script.close()



class Optimisation_settings:
    """A special object for storing the settings for optimisation.

    This includes grid search information, zooming grid search settings, and settings for the minimisation.
    """

    def __init__(self):
        """Set up the optimisation settings object."""

        # Initialise some private structures for the grid search.
        self._grid_count = 0
        self._grid_incs = []
        self._grid_zoom = []
        self._grid_sobol_max_points = []
        self._grid_sobol_oversample = []

        # Initialise some private structures for the minimisation.
        self._min_count = 0
        self._min_algor = []
        self._min_func_tol = []
        self._min_max_iter = []
        self._min_sobol_max_points = []
        self._min_sobol_oversample = []


    def _check_index(self, i, iter_type=None):
        """Check that the user supplied iteration index makes sense.

        @param i:           The iteration index.
        @type i:            int
        @keyword iter_type: The type of the index.  This can be either 'grid' or 'min'.
        @type iter_type:    str
        @raises RelaxError: If the iteration is invalid.
        """

        # Check the index.
        is_int(i, name='i', can_be_none=False)

        # Is the value too high?
        if iter_type == 'grid' and i >= self._grid_count:
            raise RelaxError("The iteration index %i is too high, only %i grid searches are set up." % (i, self._grid_count))
        if iter_type == 'min' and i >= self._min_count:
            raise RelaxError("The iteration index %i is too high, only %i minimisations are set up." % (i, self._min_count))


    def add_grid(self, inc=None, zoom=None, sobol_max_points=None, sobol_oversample=None):
        """Add a grid search step.

        @keyword inc:               The grid search size (the number of increments per dimension).
        @type inc:                  int
        @keyword zoom:              The grid zoom level for this grid search.
        @type zoom:                 None or int
        @keyword sobol_max_points:  The maximum number of Sobol' points for the PCS numerical integration to use in the grid search.  See the frame_order.sobol_setup user function for details.  If not supplied, then the previous value will be used.
        @type sobol_max_points:     None or int
        @keyword sobol_oversample:  The Sobol' oversampling factor.  See the frame_order.sobol_setup user function for details.
        @type sobol_oversample:     None or int
        """

        # Value checking, as this will be set up by a user.
        is_int(inc, name='inc', can_be_none=False)
        is_int(zoom, name='zoom', can_be_none=True)
        is_int(sobol_max_points, name='sobol_max_points', can_be_none=True)
        is_int(sobol_oversample, name='sobol_oversample', can_be_none=True)

        # Store the values.
        self._grid_incs.append(inc)
        self._grid_zoom.append(zoom)
        self._grid_sobol_max_points.append(sobol_max_points)
        self._grid_sobol_oversample.append(sobol_oversample)

        # Increment the count.
        self._grid_count += 1


    def add_min(self, min_algor='simplex', func_tol=1e-25, max_iter=1000000, sobol_max_points=None, sobol_oversample=None):
        """Add an optimisation step.

        @keyword min_algor:         The optimisation technique.
        @type min_algor:            str
        @keyword func_tol:          The minimisation function tolerance cutoff to terminate optimisation (see the minimise.execute user function).
        @type func_tol:             int
        @keyword max_iter:          The maximum number of iterations for the optimisation.
        @type max_iter:             int
        @keyword sobol_max_points:  The maximum number of Sobol' points for the PCS numerical integration to use in the optimisations after the grid search.  See the frame_order.sobol_setup user function for details.  If not supplied, then the previous value will be used.
        @type sobol_max_points:     None or int
        @keyword sobol_oversample:  The Sobol' oversampling factor.  See the frame_order.sobol_setup user function for details.
        @type sobol_oversample:     None or int
        """

        # Value checking, as this will be set up by a user.
        is_str(min_algor, name='min_algor', can_be_none=False)
        is_float(func_tol, name='func_tol', can_be_none=True)
        is_int(max_iter, name='max_iter', can_be_none=True)
        is_int(sobol_max_points, name='sobol_max_points', can_be_none=True)
        is_int(sobol_oversample, name='sobol_oversample', can_be_none=True)

        # Store the values.
        self._min_algor.append(min_algor)
        self._min_func_tol.append(func_tol)
        self._min_max_iter.append(max_iter)
        self._min_sobol_max_points.append(sobol_max_points)
        self._min_sobol_oversample.append(sobol_oversample)

        # Increment the count.
        self._min_count += 1


    def get_grid_inc(self, i):
        """Return the grid increments for the given iteration.

        @param i:   The grid search iteration from the loop_grid() method.
        @type i:    int
        @return:    The grid increments for the iteration.
        @rtype:     int
        """

        # Check the index.
        self._check_index(i, iter_type='grid')

        # Return the value.
        return self._grid_incs[i]


    def get_grid_sobol_info(self, i):
        """Return the number of numerical integration points and oversampling factor for the given iteration.

        @param i:   The grid search iteration from the loop_grid() method.
        @type i:    int
        @return:    The number of numerical integration points for the iteration and the oversampling factor.
        @rtype:     int, int
        """

        # Check the index.
        self._check_index(i, iter_type='grid')

        # Return the value.
        return self._grid_sobol_max_points[i], self._grid_sobol_oversample[i]


    def get_grid_zoom_level(self, i):
        """Return the grid zoom level for the given iteration.

        @param i:   The grid search iteration from the loop_grid() method.
        @type i:    int
        @return:    The grid zoom level for the iteration.
        @rtype:     None or int
        """

        # Check the index.
        self._check_index(i, iter_type='grid')

        # Return the value.
        return self._grid_zoom[i]


    def get_min_algor(self, i):
        """Return the minimisation algorithm for the given iteration.

        @param i:   The minimisation iteration from the loop_min() method.
        @type i:    int
        @return:    The minimisation algorithm for the iteration.
        @rtype:     int
        """

        # Check the index.
        self._check_index(i, iter_type='min')

        # Return the value.
        return self._min_algor[i]


    def get_min_func_tol(self, i):
        """Return the minimisation function tolerance level for the given iteration.

        @param i:   The minimisation iteration from the loop_min() method.
        @type i:    int
        @return:    The minimisation function tolerance level for the iteration.
        @rtype:     int
        """

        # Check the index.
        self._check_index(i, iter_type='min')

        # Return the value.
        return self._min_func_tol[i]


    def get_min_max_iter(self, i):
        """Return the maximum number of iterations for the optimisation for the given iteration.

        @param i:   The minimisation iteration from the loop_min() method.
        @type i:    int
        @return:    The maximum number of iterations for the optimisation for the iteration.
        @rtype:     int
        """

        # Check the index.
        self._check_index(i, iter_type='min')

        # Return the value.
        return self._min_max_iter[i]


    def get_min_sobol_info(self, i):
        """Return the number of numerical integration points and oversampling factor for the given iteration.

        @param i:   The minimisation iteration from the loop_min() method.
        @type i:    int
        @return:    The number of numerical integration points for the iteration and the oversampling factor.
        @rtype:     int, int
        """

        # Check the index.
        self._check_index(i, iter_type='min')

        # Return the value.
        return self._min_sobol_max_points[i], self._min_sobol_oversample[i]


    def loop_grid(self):
        """Generator method for looping over all grid search iterations.

        @return:    The grid search iteration.
        @rtype:     int
        """

        # Loop over the grid searches.
        for i in range(self._grid_count):
            yield i


    def loop_min(self):
        """Generator method for looping over all minimisation iterations.

        @return:    The minimisation iteration.
        @rtype:     int
        """

        # Loop over the minimisations.
        for i in range(self._min_count):
            yield i
