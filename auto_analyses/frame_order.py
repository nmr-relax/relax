###############################################################################
#                                                                             #
# Copyright (C) 2011-2016 Edward d'Auvergne                                   #
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
"""The automated frame order analysis protocol.


Usage
=====

To use this analysis, you should import the following into your script:

    - Frame_order_analysis:  This is a Python class which contains the automated protocol.  Initialising the class will execute the full analysis.  See its documentation for all the options it accepts.
    - Optimisation_settings:  This is a Python class which is used to set up and store the optimisation settings used in the automated protocol.  This allows for grid searches, zooming grid searches, minimisation settings, quasi-random Sobol' numerical integration of the PCS, and SciPy quadratic numerical integration of the PCS to be specified.

See the sample scripts for examples of how these are used.  In addition, the following two functions provide summaries of the analysis:

    - count_sobol_points:  This function will summarize the number of quasi-random Sobol' points used in the PCS numeric integration.  The table it creates is very useful for judging the quality of the current optimisation settings.
    - summarise:  This function will summarise all of the current frame order results.

Both these functions will be called at the end of the auto-analysis.  However they can also be used in simple scripts to summarise the results as an analysis is progressing.



The nested model parameter copying protocol
===========================================

To allow the analysis to complete in under 1,000,000 years, the trick of copying parameters from simpler nested models is used in this auto-analysis.  The protocol is split into four categories for the average domain position, the pivot point, the motional eigenframe and the parameters of ordering.  These use the fact that the free rotor and torsionless models are the two extrema of the models where the torsion angle is restricted, whereby sigma_max is pi and 0 respectively.
"""


# Python module imports.
from math import pi
from numpy import float64, zeros
from os import F_OK, access, getcwd, sep
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.arg_check import is_bool, is_float, is_int, is_str
from lib.errors import RelaxError
from lib.frame_order.conversions import convert_axis_alpha_to_spherical
from lib.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_LIST, MODEL_LIST_FREE_ROTORS, MODEL_LIST_ISO_CONE, MODEL_LIST_NONREDUNDANT, MODEL_LIST_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from lib.geometry.angles import wrap_angles
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.io import open_write_file
from lib.text.sectioning import subtitle, subsubtitle, title
from lib.text.table import MULTI_COL, format_table
from pipe_control import pipes, results
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control.structure.mass import pipe_centre_of_mass
from prompt.interpreter import Interpreter
from specific_analyses.frame_order.data import generate_pivot
from specific_analyses.frame_order import optimisation
from status import Status; status = Status()



def count_sobol_points(file_name='sobol_point_count', dir=None, force=True):
    """Count the number of Sobol' points used for the PCS numerical integration.

    This function can be used while a frame order analysis is running to summarise the results.  It will create a table of the number of Sobol' points used, which can then be used to judge the quality of the integration.


    @keyword file_name:     The file to save the table into.
    @type file_name:        str
    @keyword dir:           The optional directory to place the file into.  If specified, the results files will also be searched for in this directory.
    @type dir:              None or str
    @keyword force:         A flag which if True will cause any preexisting file to be overwritten.
    @type force:            bool
    """

    # Store the current data pipe name.
    original_pipe = pipes.cdp_name()

    # The model names, titles and directories, including axis permutations.
    models = []
    model_titles = []
    dirs = []
    for model in MODEL_LIST:
        # Add the base model.
        models.append(model)
        title = model[0].upper() + model[1:]
        model_titles.append(title)
        dirs.append(model_directory(model, base_dir=dir))

        # Axis permutations.
        if model in MODEL_LIST_ISO_CONE + MODEL_LIST_PSEUDO_ELLIPSE:
            # The A permutation.
            models.append("%s permutation A" % model)
            model_titles.append(title + ' (perm A)')
            dirs.append(model_directory(models[-1], base_dir=dir))

            # The B permutation.
            if model in MODEL_LIST_PSEUDO_ELLIPSE:
                models.append("%s permutation B" % model)
                model_titles.append(title + ' (perm B)')
                dirs.append(model_directory(models[-1], base_dir=dir))

    # Loop over the models.
    count = {}
    count_total = {}
    percentage = {}
    for i in range(len(models)):
        # Skip the rigid model.
        if models[i] == MODEL_RIGID:
            continue

        # No file.
        found = False
        for ext in ['.bz2', '', 'gz']:
            file = dirs[i]+sep+'results'+ext
            if access(file, F_OK):
                found = True
                break
        if not found:
            continue

        # Create a data pipe.
        pipe_name = 'temp %s' % models[i]
        if pipes.has_pipe(pipe_name):
            pipes.delete(pipe_name)
        pipes.create(pipe_name, 'frame order')

        # Load the data.
        results.read(file='results', dir=dirs[i])

        # SciPy quadratic integration has been used.
        if hasattr(cdp, 'quad_int') and cdp.quad_int:
            count[models[i]] = 'Quad int'
            count_total[models[i]] = ''
            percentage[models[i]] = ''
            continue

        # Count the Sobol' points used.
        if not hasattr(cdp, 'sobol_points_used'):
            optimisation.count_sobol_points()
        count[models[i]] = cdp.sobol_points_used
        count_total[models[i]] = cdp.sobol_max_points
        percentage[models[i]] = "%10.3f" % (float(cdp.sobol_points_used) / float(cdp.sobol_max_points) * 100.0) + '%'

        # Delete the temporary data pipe.
        pipes.delete(pipe_name)

    # Initialise the output string.
    string = "Quasi-random Sobol' numerical PCS integration point counting:\n\n"

    # Assemble the table contents.
    headings = [["Model", "Total points", "Used points", "Percentage"]]
    contents = []
    for model in models:
        if model not in count:
            continue
        contents.append([model, count_total[model], count[model], percentage[model]])

    # Add the table to the output string.
    string += format_table(headings=headings, contents=contents)

    # Stdout output.
    sys.stdout.write("\n\n\n")
    sys.stdout.write(string)

    # Save to file.
    file = open_write_file(file_name=file_name, dir=dir, force=force)
    file.write(string)
    file.close()

    # Switch back to the original data pipe, if it exists.
    if original_pipe:
        pipes.switch(original_pipe)


def model_directory(model, base_dir=None):
    """Return the directory to be used for the model.

    @param model:       The frame order model name.
    @type model:        str
    @keyword base_dir:  The optional base directory to prepend to the file name.
    @type base_dir:     None or str
    """

    # Convert the model name.
    dir = model.replace(' ', '_')
    dir = dir.replace(',', '')

    # Process the base directory.
    if base_dir == None:
        base_dir = ''
    elif base_dir[-1] != sep:
        base_dir += sep

    # Return the full path.
    return base_dir + dir


def summarise(file_name='summary', dir=None, force=True):
    """Summarise the frame order auto-analysis results.

    This function can be used while a frame order analysis is running to summarise the results.  It will create a table of the statistics and model parameters for all of the optimised frame order models for which results files currently exist.


    @keyword file_name:     The file to save the table into.
    @type file_name:        str
    @keyword dir:           The optional directory to place the file into.  If specified, the results files will also be searched for in this directory.
    @type dir:              None or str
    @keyword force:         A flag which if True will cause any preexisting file to be overwritten.
    @type force:            bool
    """

    # Store the current data pipe name.
    original_pipe = pipes.cdp_name()

    # The model names, titles and directories, including axis permutations.
    models = []
    model_titles = []
    dirs = []
    for model in MODEL_LIST:
        # Add the base model.
        models.append(model)
        title = model[0].upper() + model[1:]
        model_titles.append(title)
        dirs.append(model_directory(model, base_dir=dir))

        # Axis permutations.
        if model in MODEL_LIST_ISO_CONE + MODEL_LIST_PSEUDO_ELLIPSE:
            # The A permutation.
            models.append("%s permutation A" % model)
            model_titles.append(title + ' (perm A)')
            dirs.append(model_directory(models[-1], base_dir=dir))

            # The B permutation.
            if model in MODEL_LIST_PSEUDO_ELLIPSE:
                models.append("%s permutation B" % model)
                model_titles.append(title + ' (perm B)')
                dirs.append(model_directory(models[-1], base_dir=dir))

    # The analysis directory and structures.
    contents = []
    contents.append(["Analysis directory", getcwd()])
    string = format_table(contents=contents)

    # Table header.
    headings1 = []
    headings1.append(["Model", "k", "chi2", "AIC", "Motional eigenframe", MULTI_COL, MULTI_COL, "Cone half angles (deg)", MULTI_COL, MULTI_COL, MULTI_COL])
    headings1.append([None, None, None, None, "a", "b/th", "g/ph", "thx", "thy", "smax", "smax2"])

    # 2nd table header.
    headings2 = []
    headings2.append(["Model", "Average position", MULTI_COL, MULTI_COL, MULTI_COL, MULTI_COL, MULTI_COL, "Pivot point", MULTI_COL, MULTI_COL])
    headings2.append([None, "x", "y", "z", "a", "b", "g", "x", "y", "z"])

    # Loop over the models.
    contents1 = []
    contents2 = []
    for i in range(len(models)):
        # No file.
        found = False
        for ext in ['.bz2', '', 'gz']:
            file = dirs[i]+sep+'results'+ext
            if access(file, F_OK):
                found = True
                break
        if not found:
            continue

        # Create a data pipe.
        pipe_name = 'temp %s' % models[i]
        if pipes.has_pipe(pipe_name):
            pipes.delete(pipe_name)
        pipes.create(pipe_name, 'frame order')

        # Load the data.
        results.read(file='results', dir=dirs[i])

        # Number of params.
        k = len(cdp.params)

        # Format the model information.
        contents1.append([model_titles[i], k, cdp.chi2, cdp.chi2 + 2*k, None, None, None, None, None, None, None])
        contents2.append([model_titles[i], 0.0, 0.0, 0.0, None, None, None, None, None, None])

        # Eigen alpha.
        if hasattr(cdp, 'eigen_alpha') and cdp.eigen_alpha != None:
            contents1[-1][4] = cdp.eigen_alpha

        # Eigen beta.
        if hasattr(cdp, 'eigen_beta') and cdp.eigen_beta != None:
            contents1[-1][5] = cdp.eigen_beta
        elif hasattr(cdp, 'axis_theta') and cdp.axis_theta != None:
            contents1[-1][5] = cdp.axis_theta

        # Eigen gamma.
        if hasattr(cdp, 'eigen_gamma') and cdp.eigen_gamma != None:
            contents1[-1][6] = cdp.eigen_gamma
        elif hasattr(cdp, 'axis_phi') and cdp.axis_phi != None:
            contents1[-1][6] = cdp.axis_phi

        # Convert the axis alpha angle to spherical angles for comparison.
        if hasattr(cdp, 'axis_alpha') and cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR]:
            axis_theta, axis_phi = convert_axis_alpha_to_spherical(alpha=cdp.axis_alpha, pivot=generate_pivot(order=1, pipe_name=pipe_name), point=pipe_centre_of_mass(verbosity=0))
            contents1[-1][5] = wrap_angles(axis_theta, 0.0, 2.0*pi)
            contents1[-1][6] = wrap_angles(axis_phi, 0.0, 2.0*pi)

        # Order x.
        if hasattr(cdp, 'cone_theta_x') and cdp.cone_theta_x != None:
            contents1[-1][7] = cdp.cone_theta_x / 2.0 / pi * 360.0
        elif hasattr(cdp, 'cone_theta') and cdp.cone_theta != None:
            contents1[-1][7] = cdp.cone_theta / 2.0 / pi * 360.0

        # Order y.
        if hasattr(cdp, 'cone_theta_y') and cdp.cone_theta_y != None:
            contents1[-1][8] = cdp.cone_theta_y / 2.0 / pi * 360.0

        # Order torsion.
        if hasattr(cdp, 'cone_sigma_max') and cdp.cone_sigma_max != None:
            contents1[-1][9] = cdp.cone_sigma_max / 2.0 / pi * 360.0

        # Order torsion 2.
        if hasattr(cdp, 'cone_sigma_max_2') and cdp.cone_sigma_max_2 != None:
            contents1[-1][10] = cdp.cone_sigma_max_2 / 2.0 / pi * 360.0

        # The average position parameters.
        if hasattr(cdp, 'ave_pos_x') and cdp.ave_pos_x != None:
            contents2[-1][1] = cdp.ave_pos_x
        if hasattr(cdp, 'ave_pos_y') and cdp.ave_pos_y != None:
            contents2[-1][2] = cdp.ave_pos_y
        if hasattr(cdp, 'ave_pos_z') and cdp.ave_pos_z != None:
            contents2[-1][3] = cdp.ave_pos_z
        if hasattr(cdp, 'ave_pos_alpha') and cdp.ave_pos_alpha != None:
            contents2[-1][4] = cdp.ave_pos_alpha
        if hasattr(cdp, 'ave_pos_beta') and cdp.ave_pos_beta != None:
            contents2[-1][5] = cdp.ave_pos_beta
        if hasattr(cdp, 'ave_pos_gamma') and cdp.ave_pos_gamma != None:
            contents2[-1][6] = cdp.ave_pos_gamma

        # The pivot point.
        contents2[-1][7] = cdp.pivot_x
        contents2[-1][8] = cdp.pivot_y
        contents2[-1][9] = cdp.pivot_z

        # Delete the temporary data pipe.
        pipes.delete(pipe_name)

    # Add the tables.
    string += format_table(headings=headings1, contents=contents1, custom_format=[None, None, "%.2f", "%.2f", "%.3f", "%.3f", "%.3f", "%.2f", "%.2f", "%.2f", "%.2f"])
    string += format_table(headings=headings2, contents=contents2, custom_format=[None, "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f"])

    # Stdout output.
    sys.stdout.write("\n\n\n")
    sys.stdout.write(string)

    # Save to file.
    file = open_write_file(file_name=file_name, dir=dir, force=force)
    file.write(string)
    file.close()

    # Switch back to the original data pipe, if it exists.
    if original_pipe:
        pipes.switch(original_pipe)



class Frame_order_analysis:
    """The frame order auto-analysis protocol."""

    # Debugging and test suite variables.
    _final_state = True

    def __init__(self, data_pipe_full=None, data_pipe_subset=None, pipe_bundle=None, results_dir=None, pre_run_dir=None, opt_rigid=None, opt_subset=None, opt_full=None, opt_mc=None, mc_sim_num=500, models=MODEL_LIST_NONREDUNDANT, brownian_step_size=2.0, brownian_snapshot=10, brownian_total=1000, dist_total=1000, dist_max_rotations=1000000, results_compress_type=1, rigid_grid_split=False, store_intermediate=True, nested_params_ave_dom_pos=True):
        """Perform the full frame order analysis.

        @param data_pipe_full:              The name of the data pipe containing all of the RDC and PCS data.
        @type data_pipe_full:               str
        @param data_pipe_subset:            The name of the data pipe containing all of the RDC data but only a small subset of ~5 PCS points.  This optional argument is used to massively speed up the analysis.
        @type data_pipe_subset:             str or None
        @keyword pipe_bundle:               The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:                  str
        @keyword results_dir:               The directory where files are saved in.
        @type results_dir:                  str
        @keyword pre_run_dir:               The optional directory containing the frame order auto-analysis results from a previous run.  If supplied, then the 'data_pipe_full', 'data_pipe_subset', and 'opt_subset' arguments will be ignored.  The results will be loaded from the results files in this directory, and then optimisation starts from there.  The model nesting algorithm will also be deactivated.
        @keyword opt_rigid:                 The grid search, zooming grid search and minimisation settings object for the rigid frame order model.
        @type pre_run_dir:                  None or str
        @type opt_rigid:                    Optimisation_settings instance
        @keyword opt_subset:                The grid search, zooming grid search and minimisation settings object for optimisation of all models, excluding the rigid model, for the PCS data subset.
        @type opt_subset:                   Optimisation_settings instance
        @keyword opt_full:                  The grid search, zooming grid search and minimisation settings object for optimisation of all models, excluding the rigid model, for the full data set.
        @type opt_full:                     Optimisation_settings instance
        @keyword opt_mc:                    The grid search, zooming grid search and minimisation settings object for optimisation of the Monte Carlo simulations.  Any grid search settings will be ignored, as only the minimise.execute user function is run for the simulations.  And only the settings for the first iteration of the object will be accessed and used - iterative optimisation will be ignored.
        @type opt_mc:                       Optimisation_settings instance
        @keyword mc_sim_num:                The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:                   int
        @keyword models:                    The frame order models to use in the analysis.  The 'rigid' model must be included as this is essential for the analysis.
        @type models:                       list of str
        @keyword brownian_step_size:        The step_size argument for the pseudo-Brownian dynamics simulation frame_order.simulate user function.
        @type brownian_step_size:           float
        @keyword brownian_snapshot:         The snapshot argument for the pseudo-Brownian dynamics simulation frame_order.simulate user function.
        @type brownian_snapshot:            int
        @keyword brownian_total:            The total argument for the pseudo-Brownian dynamics simulation frame_order.simulate user function.
        @type brownian_total:               int
        @keyword dist_total:                The total argument for the uniform distribution frame_order.distribute user function.
        @type dist_total:                   int
        @keyword dist_max_rotations:        The max_rotations argument for the uniform distribution frame_order.distribute user function.
        @type dist_max_rotations:           int
        @keyword results_compress_type:     The type of compression to use when creating the results files.  See the results.write user function for details.
        @type results_compress_type:        int
        @keyword rigid_grid_split:          A flag which if True will cause the grid search for the rigid model to be split so that the rotation is optimised first followed by the translation.  When combined with grid zooming, this can save optimisation time.  However it may result in the global minimum being missed.
        @type rigid_grid_split:             bool
        @keyword store_intermediate:        A flag which if True will cause all intermediate optimisation results to be stored in the 'intermediate_results' directory.  These can then be used for studying the optimisation settings or loaded for subsequent analyses.
        @type store_intermediate:           bool
        @keyword nested_params_ave_dom_pos: A flag which if True will cause the average domain position parameters to be taken from the rigid or free-rotor models.  If False, then these parameters will be set to zero.
        @type nested_params_ave_dom_pos:    bool
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
            self.dist_total = dist_total
            self.dist_max_rotations = dist_max_rotations
            self.results_compress_type = results_compress_type
            self.rigid_grid_split = rigid_grid_split
            self.store_intermediate = store_intermediate
            self.flag_nested_params_ave_dom_pos = nested_params_ave_dom_pos

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

            # The pre-run directory.
            self.pre_run_dir = pre_run_dir
            self.pre_run_flag = False
            if self.pre_run_dir:
                self.pre_run_dir += sep
                self.pre_run_flag = True

            # Data checks.
            self.check_vars()

            # Load the interpreter.
            self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
            self.interpreter.populate_self()
            self.interpreter.on(verbose=False)

            # Output the starting time.
            self.interpreter.system.time()

            # The nested model optimisation protocol.
            self.nested_models()

            # Printout for the final run.
            subtitle(file=sys.stdout, text="Final results")

            # The final results does not already exist.
            if not self.read_results(model='final', pipe_name='final'):
                # Model selection.
                self.interpreter.model_selection(method='AIC', modsel_pipe='final', pipes=self.pipe_name_list)

                # The numerical optimisation settings.
                opt = self.opt_mc
                self.interpreter.frame_order.quad_int(opt.get_min_quad_int(0))
                self.sobol_setup(opt.get_min_sobol_info(0))

                # Monte Carlo simulations.
                self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
                self.interpreter.monte_carlo.create_data()
                self.interpreter.monte_carlo.initial_values()
                self.interpreter.minimise.execute(opt.get_min_algor(0), func_tol=opt.get_min_func_tol(0), max_iter=opt.get_min_max_iter(0))
                self.interpreter.eliminate()
                self.interpreter.monte_carlo.error_analysis()

                # Create the output and visualisation files.
                self.results_output(model='final', dir=self.results_dir+'final', results_file=True)

            # Regenerate the output and visualisation files for the final results.
            else:
                self.results_output(model='final', dir=self.results_dir+'final', results_file=False)

            # Output the finishing time.
            self.interpreter.system.time()

            # Final title printout.
            subtitle(file=sys.stdout, text="Summaries")

            # Save the final program state.
            if self._final_state:
                self.interpreter.state.save('final_state', dir=self.results_dir, force=True)

            # Count the number of Sobol' points and create a summary file.
            count = False
            for model in self.models:
                if model != MODEL_RIGID:
                    count = True
                    break
            if count:
                count_sobol_points(dir=self.results_dir, force=True)
            summarise(dir=self.results_dir, force=True)

        # Clean up.
        finally:
            # Finish and unlock execution.
            status.exec_lock.release()


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
            subtitle(file=sys.stdout, text=text, prespace=5)

            # Output the model staring time.
            self.interpreter.system.time()

            # A new model name.
            perm_model = "%s permutation %s" % (model, perm)

            # The data pipe name.
            self.pipe_name_dict[perm_model] = '%s permutation %s - %s' % (title, perm, self.pipe_bundle)
            self.pipe_name_list.append(self.pipe_name_dict[perm_model])

            # The output directory.
            dir = model_directory(perm_model, base_dir=self.results_dir)

            # The results file already exists, so read its contents instead.
            if self.read_results(model=perm_model, pipe_name=self.pipe_name_dict[perm_model]):
                # Re-perform model elimination just in case.
                self.interpreter.eliminate()

                # Recreate the output and visualisation files (in case this was not completed correctly).
                self.results_output(model=perm_model, dir=dir, results_file=False)

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
            self.interpreter.frame_order.quad_int(opt.get_min_quad_int(i))
            self.sobol_setup(opt.get_min_sobol_info(i))

            # Perform the optimisation.
            self.interpreter.minimise.execute(min_algor=opt.get_min_algor(i), func_tol=opt.get_min_func_tol(i), max_iter=opt.get_min_max_iter(i))

            # Results printout.
            self.print_results()

            # Model elimination.
            self.interpreter.eliminate()

            # Create the output and visualisation files.
            self.results_output(model=perm_model, dir=dir, results_file=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe bundle.
        if not isinstance(self.pipe_bundle, str):
            raise RelaxError("The pipe bundle name '%s' is invalid." % self.pipe_bundle)

        # Minimisation variables.
        if not isinstance(self.mc_sim_num, int):
            raise RelaxError("The mc_sim_num user variable '%s' is incorrectly set.  It should be an integer." % self.mc_sim_num)


    def custom_grid_incs(self, model, inc=None, pivot_search=True):
        """Set up a customised grid search increment number for each model.

        @param model:           The frame order model.
        @type model:            str
        @keyword inc:           The number of grid search increments to use for each dimension.
        @type inc:              int
        @keyword pivot_search:  A flag which if False will prevent the pivot point from being included in the grid search.
        @type pivot_search:     bool
        @return:                The list of increment values.
        @rtype:                 list of int and None
        """

        # Initialise the structure.
        incs = []

        # The pivot parameters.
        if hasattr(cdp, 'pivot_fixed') and not cdp.pivot_fixed:
            # Optimise the pivot for the rotor model.
            if pivot_search and model == MODEL_ROTOR:
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


    def nested_params_ave_dom_pos(self, model):
        """Copy the average domain parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # No nesting, so set all parameters to zero.
        if not self.flag_nested_params_ave_dom_pos:
            self.interpreter.value.set(param='ave_pos_x', val=0.0)
            self.interpreter.value.set(param='ave_pos_y', val=0.0)
            self.interpreter.value.set(param='ave_pos_z', val=0.0)
            self.interpreter.value.set(param='ave_pos_alpha', val=0.0)
            self.interpreter.value.set(param='ave_pos_beta', val=0.0)
            self.interpreter.value.set(param='ave_pos_gamma', val=0.0)
            return

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
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_RIGID])

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
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_FREE_ROTOR])

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
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_ROTOR])

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
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_ISO_CONE])

            # Copy the cone axis parameters.
            cdp.axis_theta = pipe.axis_theta
            cdp.axis_phi = pipe.axis_phi

        # The full eigenframe from the pseudo-ellipse model.
        elif model in [MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_DOUBLE_ROTOR]:
            # Printout.
            print("Obtaining the full eigenframe from the pseudo-ellipse model.")

            # Get the pseudo-ellipse data pipe.
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_PSEUDO_ELLIPSE])

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
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_ISO_CONE])

            # Copy the cone angle directly.
            if model in [MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS]:
                print("Obtaining the cone angle from the isotropic cone model.")
                cdp.cone_theta = pipe.cone_theta

            # Copy as the X cone angle.
            elif model == MODEL_PSEUDO_ELLIPSE:
                print("Obtaining the cone X angle from the isotropic cone model.")
                cdp.cone_theta_x = pipe.cone_theta

        # The X and Y cone angles from the pseudo-ellipse model.
        elif model in [MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]:
            # Printout.
            print("Obtaining the cone X and Y angles from the pseudo-ellipse model.")

            # Get the pseudo-ellipse data pipe.
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_PSEUDO_ELLIPSE])

            # Copy the cone axis.
            cdp.cone_theta_x = pipe.cone_theta_x
            cdp.cone_theta_y = pipe.cone_theta_y


        # The torsion from the rotor model.
        if model in [MODEL_ISO_CONE, MODEL_PSEUDO_ELLIPSE]:
            # Printout.
            print("Obtaining the torsion angle from the rotor model.")

            # Get the rotor data pipe.
            pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_ROTOR])

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
        pipe = pipes.get_pipe(self.pipe_name_dict[MODEL_ROTOR])

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
            subtitle(file=sys.stdout, text="%s frame order model"%title, prespace=5)

            # Output the model staring time.
            self.interpreter.system.time()

            # The data pipe name.
            self.pipe_name_dict[model] = '%s - %s' % (title, self.pipe_bundle)
            self.pipe_name_list.append(self.pipe_name_dict[model])

            # The output directory.
            dir = model_directory(model, base_dir=self.results_dir)

            # The results file already exists, so read its contents instead.
            if self.read_results(model=model, pipe_name=self.pipe_name_dict[model]):
                # Re-perform model elimination just in case.
                self.interpreter.eliminate()

                # Recreate the output files (in case this was not completed correctly).
                self.results_output(model=model, dir=dir, results_file=False)

                # Perform the axis permutation analysis.
                self.axis_permutation_analysis(model=model)

                # Skip to the next model.
                continue

            # Load a pre-run results file.
            if self.pre_run_dir != None:
                self.read_results(model=model, pipe_name=self.pipe_name_dict[model], pre_run=True)

            # Otherwise use the base data pipes.
            else:
                # Create the data pipe using the full data set, and switch to it.
                if self.data_pipe_subset != None:
                    self.interpreter.pipe.copy(self.data_pipe_subset, self.pipe_name_dict[model], bundle_to=self.pipe_bundle)
                else:
                    self.interpreter.pipe.copy(self.data_pipe_full, self.pipe_name_dict[model], bundle_to=self.pipe_bundle)
                self.interpreter.pipe.switch(self.pipe_name_dict[model])

                # Select the Frame Order model.
                self.interpreter.frame_order.select_model(model=model)

                # Copy nested parameters.
                subsubtitle(file=sys.stdout, text="Parameter nesting")
                self.nested_params_ave_dom_pos(model)
                self.nested_params_eigenframe(model)
                self.nested_params_pivot(model)
                self.nested_params_order(model)

            # Optimisation using the PCS subset (skipped if a pre-run directory is supplied).
            if self.data_pipe_subset != None and self.opt_subset != None and not self.pre_run_flag:
                self.optimisation(model=model, opt=self.opt_subset, pcs_text="PCS subset", intermediate_dir='pcs_subset')

            # Operations if a subset was used, otherwise these are not needed.
            if self.data_pipe_subset != None and self.data_pipe_full != None:
                # Copy the PCS data.
                self.interpreter.pcs.copy(pipe_from=self.data_pipe_full, pipe_to=self.pipe_name_dict[model])

                # Reset the selection status.
                for spin, spin_id in spin_loop(return_id=True, skip_desel=False):
                    # Get the spin from the original pipe.
                    spin_orig = return_spin(spin_id=spin_id, pipe=self.data_pipe_full)

                    # Reset the spin selection.
                    spin.select = spin_orig.select

            # Optimisation using the full data set.
            if self.opt_full != None:
                self.optimisation(model=model, opt=self.opt_full, pcs_text="full data set", intermediate_dir='all_data')

            # Results printout.
            self.print_results()

            # Model elimination.
            self.interpreter.eliminate()

            # Create the output and visualisation files.
            self.results_output(model=model, dir=dir, results_file=True)

            # Perform the axis permutation analysis.
            self.axis_permutation_analysis(model=model)


    def optimisation(self, model=None, opt=None, pcs_text=None, intermediate_dir=None):
        """Perform the grid search and minimisation.

        @keyword model:             The frame order model to optimise.
        @type model:                str
        @keyword opt:               The grid search, zooming grid search and minimisation settings object for optimisation of all models.
        @type opt:                  Optimisation_settings instance
        @keyword pcs_text:          The text to use in the title.  This is either about the PCS subset or full data set.
        @type pcs_text:             str
        @keyword intermediate_dir:  The directory for this PCS data set for storing the intermediate results.
        @type intermediate_dir:     str
        """

        # Printout.
        subsubtitle(file=sys.stdout, text="Optimisation using the %s" % pcs_text)

        # Results directory stub for intermediate results.
        intermediate_stub = self.results_dir + sep + 'intermediate_results' + sep + intermediate_dir

        # Zooming grid search.
        for i in opt.loop_grid():
            # The intermediate results directory.
            intermediate_dir = intermediate_stub + '_grid%i' % i

            # Set the zooming grid search level.
            zoom = opt.get_grid_zoom_level(i)
            if zoom != None:
                self.interpreter.minimise.grid_zoom(level=zoom)
                intermediate_dir += '_zoom%i' % zoom

            # Set up the custom grid increments.
            incs = self.custom_grid_incs(model, inc=opt.get_grid_inc(i), pivot_search=opt.get_grid_pivot_search(i))
            intermediate_dir += '_inc%i' % opt.get_grid_inc(i)

            # The numerical optimisation settings.
            quad_int = opt.get_grid_quad_int(i)
            if quad_int:
                self.interpreter.frame_order.quad_int(True)
                intermediate_dir += '_quad_int'
            else:
                sobol_num = opt.get_grid_sobol_info(i)
                self.sobol_setup(sobol_num)
                intermediate_dir += '_sobol%i' % sobol_num[0]

            # Perform the grid search.
            self.interpreter.minimise.grid_search(inc=incs, skip_preset=False)

            # Store the intermediate results and statistics.
            if self.store_intermediate:
                self.results_output(model=model, dir=model_directory(model, base_dir=intermediate_dir), results_file=True, simulation=False)
                count_sobol_points(dir=intermediate_dir, force=True)
                summarise(dir=intermediate_dir, force=True)

        # Minimisation.
        for i in opt.loop_min():
            # The intermediate results directory.
            func_tol = opt.get_min_func_tol(i)
            max_iter = opt.get_min_max_iter(i)
            intermediate_dir = intermediate_stub + '_min%i_ftol%g_max_iter%i' % (i, func_tol, max_iter)

            # The numerical optimisation settings.
            quad_int = opt.get_min_quad_int(i)
            if quad_int:
                self.interpreter.frame_order.quad_int(True)
                intermediate_dir += '_quad_int'
            else:
                sobol_num = opt.get_min_sobol_info(i)
                self.sobol_setup(sobol_num)
                intermediate_dir += '_sobol%i' % sobol_num[0]

            # Perform the optimisation.
            self.interpreter.minimise.execute(min_algor=opt.get_min_algor(i), func_tol=func_tol, max_iter=max_iter)

            # Store the intermediate results.
            if self.store_intermediate:
                self.results_output(model=model, dir=model_directory(model, base_dir=intermediate_dir), results_file=True, simulation=False)
                count_sobol_points(dir=intermediate_dir, force=True)
                summarise(dir=intermediate_dir, force=True)


    def optimise_rigid(self):
        """Optimise the rigid frame order model.

        The Sobol' integration is not used here, so the algorithm is different to the other frame order models.
        """

        # The model.
        model = MODEL_RIGID
        title = model[0].upper() + model[1:]

        # Print out.
        subtitle(file=sys.stdout, text="%s frame order model"%title, prespace=5)

        # Output the model staring time.
        self.interpreter.system.time()

        # The data pipe name.
        self.pipe_name_dict[model] = '%s - %s' % (title, self.pipe_bundle)
        self.pipe_name_list.append(self.pipe_name_dict[model])

        # The output directory.
        dir = model_directory(model, base_dir=self.results_dir) 

        # The results file already exists, so read its contents instead.
        if self.read_results(model=model, pipe_name=self.pipe_name_dict[model]):
            # Recreate the output and visualisation files (in case this was not completed correctly).
            self.results_output(model=model, dir=dir, results_file=False)

            # Nothing more to do.
            return

        # Load a pre-run results file.
        if self.pre_run_flag:
            self.read_results(model=model, pipe_name=self.pipe_name_dict[model], pre_run=True)

        # Otherwise use the base data pipes.
        else:
            # Create the data pipe using the full data set, and switch to it.
            self.interpreter.pipe.copy(self.data_pipe_full, self.pipe_name_dict[model], bundle_to=self.pipe_bundle)
            self.interpreter.pipe.switch(self.pipe_name_dict[model])

            # Select the Frame Order model.
            self.interpreter.frame_order.select_model(model=model)

        # Optimisation.
        opt = self.opt_rigid
        if opt != None:
            # No grid search.
            if not opt.has_grid():
                # Set up the initial parameters.
                print("\n\nNo grid search, so setting the translational and rotational parameters to zero.")
                self.interpreter.value.set(param='ave_pos_x', val=0.0)
                self.interpreter.value.set(param='ave_pos_y', val=0.0)
                self.interpreter.value.set(param='ave_pos_z', val=0.0)
                self.interpreter.value.set(param='ave_pos_alpha', val=0.0)
                self.interpreter.value.set(param='ave_pos_beta', val=0.0)
                self.interpreter.value.set(param='ave_pos_gamma', val=0.0)

            # Grid search alternation.
            elif self.rigid_grid_split:
                # Split zooming grid search for the translation.
                print("\n\nTranslation active - splitting the grid search and iterating.")
                self.interpreter.value.set(param='ave_pos_x', val=0.0)
                self.interpreter.value.set(param='ave_pos_y', val=0.0)
                self.interpreter.value.set(param='ave_pos_z', val=0.0)
                for i in opt.loop_grid():
                    # Set the zooming grid search level.
                    zoom = opt.get_grid_zoom_level(i)
                    if zoom != None:
                        self.interpreter.minimise.grid_zoom(level=zoom)

                    # The numerical optimisation settings.
                    self.interpreter.frame_order.quad_int(opt.get_grid_quad_int(i))
                    self.sobol_setup(opt.get_grid_sobol_info(i))

                    # The number of increments.
                    inc = opt.get_grid_inc(i)

                    # First optimise the rotation.
                    self.interpreter.minimise.grid_search(inc=[None, None, None, inc, inc, inc], skip_preset=False)

                    # Then the translation.
                    self.interpreter.minimise.grid_search(inc=[inc, inc, inc, None, None, None], skip_preset=False)

            # Normal grid search.
            else:
                for i in opt.loop_grid():
                    # Set the zooming grid search level.
                    zoom = opt.get_grid_zoom_level(i)
                    if zoom != None:
                        self.interpreter.minimise.grid_zoom(level=zoom)

                    # The numerical optimisation settings.
                    self.interpreter.frame_order.quad_int(opt.get_grid_quad_int(i))
                    self.sobol_setup(opt.get_grid_sobol_info(i))

                    # The number of increments.
                    inc = opt.get_grid_inc(i)

                    # Grid search
                    self.interpreter.minimise.grid_search(inc=inc, skip_preset=False)

            # Minimise.
            for i in opt.loop_min():
                # The numerical optimisation settings.
                self.interpreter.frame_order.quad_int(opt.get_min_quad_int(i))
                self.sobol_setup(opt.get_min_sobol_info(i))

                # Perform the optimisation.
                self.interpreter.minimise.execute(min_algor=opt.get_min_algor(i), func_tol=opt.get_min_func_tol(i), max_iter=opt.get_min_max_iter(i))

        # Results printout.
        self.print_results()

        # Create the output and visualisation files.
        self.results_output(model=model, dir=dir, results_file=True)


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
        if hasattr(cdp, 'cone_theta_x') or hasattr(cdp, 'cone_theta_y') or hasattr(cdp, 'cone_theta') or hasattr(cdp, 'cone_sigma_max'):
            sys.stdout.write("\nFrame ordering:\n")
        if hasattr(cdp, 'cone_theta_x'):
            sys.stdout.write(format_float % ('cone theta_x:', cdp.cone_theta_x))
        if hasattr(cdp, 'cone_theta_y'):
            sys.stdout.write(format_float % ('cone theta_y:', cdp.cone_theta_y))
        if hasattr(cdp, 'cone_theta'):
            sys.stdout.write(format_float % ('cone theta:', cdp.cone_theta))
        if hasattr(cdp, 'cone_sigma_max'):
            sys.stdout.write(format_float % ('sigma_max:', cdp.cone_sigma_max))

        # Minimisation statistics.
        if hasattr(cdp, 'chi2'):
            sys.stdout.write("\nMinimisation statistics:\n")
        if hasattr(cdp, 'chi2'):
            sys.stdout.write(format_float % ('chi2:', cdp.chi2))

        # Final spacing.
        sys.stdout.write("\n")


    def read_results(self, model=None, pipe_name=None, pre_run=False):
        """Attempt to read old results files.

        @keyword model:     The frame order model.
        @type model:        str
        @keyword pipe_name: The name of the data pipe to use for this model.
        @type pipe_name:    str
        @keyword pre_run:   A flag which if True will read the results file from the pre-run directory.
        @type pre_run:      bool
        @return:            True if the file exists and has been read, False otherwise.
        @rtype:             bool
        """

        # The file name.
        base_dir = self.results_dir
        if pre_run:
            base_dir = self.pre_run_dir
        path = model_directory(model, base_dir=base_dir) + sep + 'results'

        # Loop over the compression types.
        found = False
        for ext in ['.bz2', '', 'gz']:
            # The full file name.
            full_path = path + ext

            # The file does not exist.
            if not access(full_path, F_OK):
                continue

            # Create an empty data pipe.
            self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type='frame order')

            # Read the results file.
            self.interpreter.results.read(full_path)

            # Results printout.
            self.print_results()

            # The flag.
            found = True
            break

        # Success.
        return found


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


    def results_output(self, dir=None, model=None, results_file=True, simulation=True):
        """Create visual representations of the frame order results for the given model.

        This will call the following user functions:

            - results.write to output a results file (turned off if the results_file argument is False).
            - rdc.corr_plot and pcs.corr_plot to visualise the quality of the data and fit as 2D Grace correlation plots.
            - frame_order.pdb_model to generate a PDB representation of the frame order motions.
            - frame_order.simulate to perform a pseudo-Brownian frame order dynamics simulation.

        A relax script called 'pymol_display.py' will be created for easily visualising the PDB representation from the frame_order.pdb_model user function.


        This includes a PDB representation of the motions (the 'cone.pdb' file located in each model directory) together with a relax script for displaying the average domain positions together with the cone/motion representation in PyMOL (the 'pymol_display.py' file, also created in the model directory).

        @keyword dir:           The output directory.
        @type dir:              str
        @keyword model:         The frame order model.  This should match the model of the current data pipe, unless the special value of 'final' is used to indicate the visualisation of the final results.
        @type model:            str
        @keyword results_file:  A flag which if True will cause a results file to be created via the results.write user function.
        @type results_file:     bool
        @keyword simulation:    A flag which if True will allow the pseudo-Brownian frame order dynamics simulation to be run.
        @type simulation:       bool
        """

        # Printout.
        subsubtitle(file=sys.stdout, text="Generating the results and data visualisation files")

        # Sanity check.
        if model != 'final' and model.replace(' permutation A', '').replace(' permutation B', '') != cdp.model:
            raise RelaxError("The model '%s' does not match the model '%s' of the current data pipe." % (model.replace(' permuted', ''), cdp.model))

        # The results file.
        if results_file:
            self.interpreter.results.write(dir=dir, compress_type=self.results_compress_type, force=True)

        # The RDC and PCS correlation plots.
        self.interpreter.rdc.corr_plot(dir=dir, force=True)
        self.interpreter.pcs.corr_plot(dir=dir, force=True)

        # The PDB representation of the model.
        self.interpreter.frame_order.pdb_model(dir=dir, force=True)

        # Create the visualisation script for the PDB representation.
        script = open_write_file(file_name='pymol_display.py', dir=dir, force=True)
        script.write("# relax script for displaying the frame order results of this '%s' model in PyMOL.\n\n" % model)
        script.write("# PyMOL visualisation.\n")
        script.write("pymol.frame_order()\n")
        script.close()

        # The uniform distribution of structures.
        if simulation:
            self.interpreter.frame_order.distribute(dir=dir, total=self.dist_total, max_rotations=self.dist_max_rotations, force=True)

        # The pseudo-Brownian dynamics simulation.
        if simulation:
            self.interpreter.frame_order.simulate(dir=dir, step_size=self.brownian_step_size, snapshot=self.brownian_snapshot, total=self.brownian_total, force=True)


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
        self._grid_quad_int = []
        self._grid_pivot_search = []

        # Initialise some private structures for the minimisation.
        self._min_count = 0
        self._min_algor = []
        self._min_func_tol = []
        self._min_max_iter = []
        self._min_sobol_max_points = []
        self._min_sobol_oversample = []
        self._min_quad_int = []


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


    def add_grid(self, inc=None, zoom=None, sobol_max_points=None, sobol_oversample=None, quad_int=False, pivot_search=True):
        """Add a grid search step.

        @keyword inc:               The grid search size (the number of increments per dimension).
        @type inc:                  int
        @keyword zoom:              The grid zoom level for this grid search.
        @type zoom:                 None or int
        @keyword sobol_max_points:  The maximum number of Sobol' points for the PCS numerical integration to use in the grid search.  See the frame_order.sobol_setup user function for details.  If not supplied, then the previous value will be used.
        @type sobol_max_points:     None or int
        @keyword sobol_oversample:  The Sobol' oversampling factor.  See the frame_order.sobol_setup user function for details.
        @type sobol_oversample:     None or int
        @keyword quad_int:          The SciPy quadratic integration flag.  See the frame_order.quad_int user function for details.
        @type quad_int:             bool
        @keyword pivot_search:      A flag which if False will prevent the pivot point from being included in the grid search.
        @type pivot_search:         bool
        """

        # Value checking, as this will be set up by a user.
        is_int(inc, name='inc', can_be_none=False)
        is_int(zoom, name='zoom', can_be_none=True)
        is_int(sobol_max_points, name='sobol_max_points', can_be_none=True)
        is_int(sobol_oversample, name='sobol_oversample', can_be_none=True)
        is_bool(quad_int, name='quad_int')

        # Store the values.
        self._grid_incs.append(inc)
        self._grid_zoom.append(zoom)
        self._grid_sobol_max_points.append(sobol_max_points)
        self._grid_sobol_oversample.append(sobol_oversample)
        self._grid_quad_int.append(quad_int)
        self._grid_pivot_search.append(pivot_search)

        # Increment the count.
        self._grid_count += 1


    def add_min(self, min_algor='simplex', func_tol=1e-25, max_iter=1000000, sobol_max_points=None, sobol_oversample=None, quad_int=False):
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
        @keyword quad_int:          The SciPy quadratic integration flag.  See the frame_order.quad_int user function for details.
        @type quad_int:             bool
        """

        # Value checking, as this will be set up by a user.
        is_str(min_algor, name='min_algor', can_be_none=False)
        is_float(func_tol, name='func_tol', can_be_none=True)
        is_int(max_iter, name='max_iter', can_be_none=True)
        is_int(sobol_max_points, name='sobol_max_points', can_be_none=True)
        is_int(sobol_oversample, name='sobol_oversample', can_be_none=True)
        is_bool(quad_int, name='quad_int')

        # Store the values.
        self._min_algor.append(min_algor)
        self._min_func_tol.append(func_tol)
        self._min_max_iter.append(max_iter)
        self._min_sobol_max_points.append(sobol_max_points)
        self._min_sobol_oversample.append(sobol_oversample)
        self._min_quad_int.append(quad_int)

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


    def get_grid_pivot_search(self, i):
        """Return the pivot grid search flag.

        @param i:   The grid search iteration from the loop_grid() method.
        @type i:    int
        @return:    The pivot grid search flag.
        @rtype:     bool
        """

        # Check the index.
        self._check_index(i, iter_type='grid')

        # Return the value.
        return self._grid_pivot_search[i]


    def get_grid_quad_int(self, i):
        """Return the SciPy quadratic integration flag for the given iteration.

        @param i:   The grid search iteration from the loop_grid() method.
        @type i:    int
        @return:    The SciPy quadratic integration flag for the iteration.
        @rtype:     bool
        """

        # Check the index.
        self._check_index(i, iter_type='grid')

        # Return the value.
        return self._grid_quad_int[i]


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


    def get_min_quad_int(self, i):
        """Return the SciPy quadratic integration flag for the given iteration.

        @param i:   The minimisation iteration from the loop_min() method.
        @type i:    int
        @return:    The SciPy quadratic integration flag for the iterationor.
        @rtype:     bool
        """

        # Check the index.
        self._check_index(i, iter_type='min')

        # Return the value.
        return self._min_quad_int[i]


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


    def has_grid(self):
        """Is a grid search set up?

        @return:    True if a grid search has been set up.
        @rtype:     bool
        """

        # Grid information is present. 
        if self._grid_count > 0:
            return True

        # No grid.
        return False


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
