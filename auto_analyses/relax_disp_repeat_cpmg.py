###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The automatic relaxation dispersion protocol for repeated data for CPMG.

U{task #7826<https://gna.org/task/index.php?78266>}, Write an python class for the repeated analysis of dispersion data.
"""

# Dependencies.
import dep_check

# Python module imports.
from copy import deepcopy
from datetime import datetime
from glob import glob
from os import F_OK, access, getcwd, sep
from numpy import any, asarray, arange, concatenate, max, mean, min, sqrt, std, sum
if dep_check.scipy_module:
    from scipy.stats import pearsonr
import sys
from warnings import warn

# relax module imports.
import dep_check
from lib.dispersion.variables import MODEL_NOREX, MODEL_PARAMS, MODEL_R2EFF, PARAMS_R20
from lib.io import extract_data, get_file_path, open_write_file, sort_filenames, write_data
from lib.text.sectioning import section, subsection, subtitle, title
from lib.warnings import RelaxWarning
from pipe_control.mol_res_spin import display_spin, generate_spin_string, return_spin, spin_loop
from pipe_control import pipes
from prompt.interpreter import Interpreter
from specific_analyses.relax_disp.data import generate_r20_key, has_exponential_exp_type, is_r1_optimised, loop_exp_frq_offset, loop_exp_frq_offset_point, return_param_key_from_data
from status import Status; status = Status()

if dep_check.matplotlib_module:
    import pylab as plt
    from matplotlib.font_manager import FontProperties
    fontP = FontProperties()
    fontP.set_size('small')


# Define sfrq key to dic.
DIC_KEY_FORMAT = "%.8f"


class Relax_disp_rep:

    """The relaxation dispersion analysis for repeated data."""

    # Some class variables.
    opt_func_tol = 1e-25
    opt_max_iterations = int(1e7)


    def __init__(self, settings):
        """Perform a repeated dispersion analysis for settings given."""

        # Store settings.
        self.settings = settings

        # Unpack settings from dictionary to self.
        for setting, value in self.settings.iteritems():
            setattr(self, setting, value)

        if 'pipe_type' not in self.settings:
            self.set_self(key='pipe_type', value='relax_disp')

        if 'time' not in self.settings:
            self.set_self(key='time', value=datetime.now().strftime('%Y_%m_%d_%H_%M'))

        # No results directory, so default to the current directory.
        if 'results_dir' not in self.settings:
            self.set_self(key='results_dir', value=getcwd() + sep + 'results' + sep + self.time )

        # Standard Monte-Carlo simulations.
        if 'mc_sim_num' not in self.settings:
            self.set_self(key='mc_sim_num', value=40)

        # Standard Monte-Carlo simulations for exponential fit. '-1' is getting R2eff err from Co-variance.
        if 'exp_mc_sim_num' not in self.settings:
            self.set_self(key='exp_mc_sim_num', value=-1)

        # Standard Monte-Carlo simulations for exponential fit. '-1' is getting R2eff err from Co-variance.
        if 'modsel' not in self.settings:
            self.set_self(key='modsel', value='AIC')

        # The R2eff/R1rho value in rad/s by which to judge insignificance.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.
        if 'insignificance' not in self.settings:
            self.set_self(key='insignificance', value=0.0)

        # A flag which if True will activate R1 parameter fitting via relax_disp.r1_fit for the models that support it.
        # If False, then the relax_disp.r1_fit user function will not be called.
        if 'r1_fit' not in self.settings:
            self.set_self(key='r1_fit', value=False)

        # The minimisation algorithm.
        if 'min_algor' not in self.settings:
            self.set_self(key='min_algor', value='simplex')

        # The constraints settings.
        if 'constraints' not in self.settings:
            self.set_self(key='constraints', value=True)

        # The base setup.
        if 'base_setup_pipe_name' not in self.settings:
            base_setup_pipe_name = self.name_pipe(method='setup', model='setup', analysis='setup', glob_ini='setup')
            self.set_self(key='base_setup_pipe_name', value=base_setup_pipe_name)

        # Start interpreter.
        self.interpreter_start()


    def set_base_cpmg(self, method=None, glob_ini=None, force=False):
        """ Setup base information, but do not load intensity. """

        # Define model
        model = 'setup'
        analysis = 'setup'

        # Check previous, and get the pipe name.
        found, pipe_name, resfile, path = self.check_previous_result(method='setup', model=model, analysis=analysis, glob_ini='setup', bundle='setup')

        # If found, then pass, else calculate it.
        if found:
            pass
        else:
            # Create the data pipe.
            self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=self.pipe_type, bundle=None)

            # Loop over frequency, store spectrum ids.
            dic_spectrum_ids = {}
            dic_spectrum_ids_replicates = {}
            for i, sfrq in enumerate(self.sfrqs):
                # Access the key in self.
                key = DIC_KEY_FORMAT % (sfrq)

                # Loop over cpmg_frqs.
                cpmg_frqs = getattr(self, key)['cpmg_frqs']

                # Get the folder for peak files.
                peaks_folder = getattr(self, key)['peaks_folder'] + sep + method

                # Define glop pattern for peak files.
                peaks_glob_pat = '%s_%s.ser' % (glob_ini, method)

                # Get the file list.
                peaks_file_list = glob(peaks_folder + sep + peaks_glob_pat)

                # Sort the file list Alphanumeric.
                peaks_file_list = sort_filenames(filenames=peaks_file_list)

                # Create the spins.
                for peaks_file in peaks_file_list:
                    self.interpreter.spectrum.read_spins(file=peaks_file, dir=None)

                # Collect data keys.
                dic_spectrum_ids[key] = []
                for j, cpmg_frq in enumerate(cpmg_frqs):
                    # Define the key.
                    data_key = return_param_key_from_data(exp_type=self.exp_type, frq=sfrq, point=cpmg_frq)
                    spectrum_id = data_key + '_%i'%j

                    # Store data key
                    dic_spectrum_ids[key].append(spectrum_id)

                    # Set the current experiment type.
                    self.interpreter.relax_disp.exp_type(spectrum_id=spectrum_id, exp_type=self.exp_type)

                    # Set the relaxation dispersion CPMG frequencies.
                    if cpmg_frq == 0.0:
                        cpmg_frq = None
                    self.interpreter.relax_disp.cpmg_setup(spectrum_id=spectrum_id, cpmg_frq=cpmg_frq)

                    # Relaxation dispersion CPMG constant time delay T (in s).
                    time_T2 = getattr(self, key)['time_T2']
                    self.interpreter.relax_disp.relax_time(spectrum_id=spectrum_id, time=time_T2)

                    # Set the NMR field strength of the spectrum.
                    self.interpreter.spectrometer.frequency(id=spectrum_id, frq=sfrq, units=self.sfrq_unit)

                # Get the list of duplications
                list_dub = self.get_dublicates(dic_spectrum_ids[key], cpmg_frqs)

                # Store to dic
                dic_spectrum_ids_replicates[key] = list_dub

            # Store to current data pipe.
            cdp.dic_spectrum_ids = dic_spectrum_ids
            cdp.dic_spectrum_ids_replicates = dic_spectrum_ids_replicates

            # Name the isotope for field strength scaling.
            self.interpreter.spin.isotope(isotope=self.isotope)

            # Finally store the pipe name and save the setup pipe.
            self.interpreter.results.write(file=resfile, dir=path, force=force)


    def set_intensity_and_error(self, pipe_name, glob_ini=None, set_rmsd=None):
        # Read the intensity per spectrum id and set the RMSD error.

        # Switch to the pipe.
        if pipes.cdp_name() != pipe_name:
            self.interpreter.pipe.switch(pipe_name)

        # Loop over spectrometer frequencies.
        finished = len(self.sfrqs) * [False]
        for i, sfrq in enumerate(self.sfrqs):
            # Access the key in self.
            key = DIC_KEY_FORMAT % (sfrq)

            # Get the spectrum ids.
            spectrum_ids = cdp.dic_spectrum_ids[key]

            # Get the folder for peak files.
            peaks_folder = getattr(self, key)['peaks_folder'] + sep + self.method

            # Define glop pattern for peak files.
            peaks_glob_pat = '%s_%s.ser' % (glob_ini, self.method)

            # Get the file list.
            peaks_file_list = glob(peaks_folder + sep + peaks_glob_pat)

            # Sort the file list Alphanumeric.
            peaks_file_list = sort_filenames(filenames=peaks_file_list)

            # If there is no peak list, then continue.
            if len(peaks_file_list) == 0:
                finished[i] = False
                continue

            # There should only be one peak file.
            for peaks_file in peaks_file_list:
                self.interpreter.spectrum.read_intensities(file=peaks_file, spectrum_id=spectrum_ids, int_method=self.int_method, int_col=range(len(spectrum_ids)))

            if set_rmsd:
                # Get the folder for rmsd files.
                rmsd_folder = getattr(self, key)['rmsd_folder']

                # Define glop pattern for rmsd files.
                rmsd_glob_pat = '%s_*_%s.rmsd' % (glob_ini, self.method)

                # Get the file list.
                rmsd_file_list = glob(rmsd_folder + sep + rmsd_glob_pat)

                # Sort the file list Alphanumeric.
                rmsd_file_list = sort_filenames(filenames=rmsd_file_list)

                # Loop over spectrum ids
                for j, spectrum_id in enumerate(spectrum_ids):
                    # Set the peak intensity errors, as defined as the baseplane RMSD.
                    rmsd_file = rmsd_file_list[j]

                    # Extract rmsd from line 0, and column 0.
                    rmsd = float(extract_data(file=rmsd_file)[0][0])
                    self.interpreter.spectrum.baseplane_rmsd(error=rmsd, spectrum_id=spectrum_id)

            finished[i] = True

        return all(finished)


    def do_spectrum_error_analysis(self, pipe_name, set_rep=None):
        """Do spectrum error analysis, where both replicates per spectrometer frequency and subset is taken into consideration."""


        # Switch to the pipe.
        if pipes.cdp_name() != pipe_name:
            self.interpreter.pipe.switch(pipe_name)

        # Loop over spectrometer frequencies.
        for i, sfrq in enumerate(self.sfrqs):
            # Access the key in self.
            key = DIC_KEY_FORMAT % (sfrq)

            # Printout.
            section(file=sys.stdout, text="Error analysis for pipe='%s' and sfr:%3.2f"%(pipe_name, sfrq), prespace=2)

            # Get the spectrum ids.
            spectrum_ids = cdp.dic_spectrum_ids[key]

            if set_rep:
                # Get the spectrum ids replicates.
                spectrum_ids_replicates = cdp.dic_spectrum_ids_replicates[key]

                # Check if there are any replicates.
                for replicate in spectrum_ids_replicates:
                    spectrum_id, rep_list = replicate

                    # If there is a replicated list, specify it.
                    if len(rep_list) > 0:
                        # Define the replicates.
                        self.interpreter.spectrum.replicated(spectrum_ids=rep_list)

            # Run the error analysis on the subset.
            self.interpreter.spectrum.error_analysis(subset=spectrum_ids)


    def set_int(self, methods=None, list_glob_ini=None, set_rmsd=True, set_rep=False, force=False):
        """Call both the setup of data and the error analysis"""

        # Define model
        model = 'setup'
        analysis = 'int'

        # Loop over the methods.
        finished = len(methods) * [False]
        for i, method in enumerate(methods):
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    calculate = True
                    finished[i] = False
                elif found:
                    calculate = False
                    finished[i] = True

                if calculate:
                    # Create the data pipe, by copying setup pipe.
                    self.interpreter.pipe.copy(pipe_from=self.base_setup_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                    # Call set intensity.
                    finished_int = self.set_intensity_and_error(pipe_name=pipe_name, glob_ini=glob_ini, set_rmsd=set_rmsd)

                    if finished_int:
                        # Call error analysis.
                        self.do_spectrum_error_analysis(pipe_name=pipe_name, set_rep=set_rep)

                        # Save results, and store the current settings dic to pipe.
                        cdp.settings = self.settings
                        self.interpreter.results.write(file=resfile, dir=path, force=force)

                        finished[i] = True

                    else:
                        pipe_name = pipes.cdp_name()
                        self.interpreter.pipe.delete(pipe_name=pipe_name)

        return all(finished)


    def calc_r2eff(self, methods=None, list_glob_ini=None, force=False):
        """Method to calculate R2eff or read previous results."""

        model = MODEL_R2EFF
        analysis = 'int'

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    calculate = True
                elif found:
                    calculate = False

                if calculate:
                    # Create the data pipe by copying the intensity pipe, then switching to it.
                    # If not intensity pipe name pipe exists, then calculate it.
                    intensity_pipe_name = self.name_pipe(method=self.method, model='setup', analysis='int', glob_ini=glob_ini)

                    if not pipes.has_pipe(intensity_pipe_name):
                        finished = self.set_int(methods=[method], list_glob_ini=[glob_ini])
                        if not finished:
                            continue

                    self.interpreter.pipe.copy(pipe_from=intensity_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                    # Select the model.
                    self.interpreter.relax_disp.select_model(model)

                    # Print
                    subtitle(file=sys.stdout, text="The '%s' model for pipe='%s'" % (model, pipe_name), prespace=3)

                    # Calculate the R2eff values for the fixed relaxation time period data types.
                    if model == MODEL_R2EFF and not has_exponential_exp_type():
                        self.interpreter.minimise.calculate()

                    # Save results, and store the current settings dic to pipe.
                    cdp.settings = self.settings
                    self.interpreter.results.write(file=resfile, dir=path, force=force)


    def deselect_all(self, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Method to deselect all spins for a pipe."""

        # Set default
        if model_from == None:
            model_from = model
        if analysis_from == None:
            analysis_from = analysis

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    # If previous pipe not found, then create it.
                    model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis=analysis_from, glob_ini=glob_ini)

                    # Copy pipe and switch.
                    self.interpreter.pipe.copy(pipe_from=model_from_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                # Print
                subtitle(file=sys.stdout, text="Deselect all spins for pipe='%s'" % (pipe_name), prespace=3)

                # Deselect spins.
                self.interpreter.deselect.all()

                # Save results, and store the current settings dic to pipe.
                cdp.settings = self.settings

                if found and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)

                # Show selected spins
                self.interpreter.spin.display()


    def select_spin(self, spin_id=None, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Method to select spins for a pipe."""

        # Set default
        if model_from == None:
            model_from = model
        if analysis_from == None:
            analysis_from = analysis

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    # If previous pipe not found, then create it.
                    model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis=analysis_from, glob_ini=glob_ini)

                    # Copy pipe and switch.
                    self.interpreter.pipe.copy(pipe_from=model_from_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                # Print
                subtitle(file=sys.stdout, text="Select spins '%s' for pipe='%s'" % (spin_id, pipe_name), prespace=3)

                # Select spins.
                self.interpreter.select.spin(spin_id=spin_id)

                # Save results, and store the current settings dic to pipe.
                cdp.settings = self.settings

                if found and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)

                # Show selected spins
                self.interpreter.spin.display()


    def value_set(self, spin_id=None, val=None, param=None, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Use value.set on all pipes."""

        # Set default
        if model_from == None:
            model_from = model
        if analysis_from == None:
            analysis_from = analysis

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    # If previous pipe not found, then create it.
                    model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis=analysis_from, glob_ini=glob_ini)

                    # Copy pipe and switch.
                    self.interpreter.pipe.copy(pipe_from=model_from_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                # Print
                subtitle(file=sys.stdout, text="For param '%s' set value '%3.2f' for pipe='%s'" % (param, val, pipe_name), prespace=3)

                # Select the model.
                self.interpreter.relax_disp.select_model(model)

                # Set value
                self.interpreter.value.set(val=val, param=param, spin_id=spin_id)

                # Save results, and store the current settings dic to pipe.
                cdp.settings = self.settings

                if found and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)

                # Print for pipe name
                self.spin_display_params(pipe_name=pipe_name)


    def r20_from_min_r2eff(self, spin_id=None, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Will set the grid R20 values from the minimum R2eff values through the r20_from_min_r2eff user function.
        This will speed up the grid search with a factor GRID_INC^(Nr_spec_freq). For a CPMG experiment with two fields and standard GRID_INC = 21, the speed-up is a factor 441.
        """

        # Set default
        if model_from == None:
            model_from = model
        if analysis_from == None:
            analysis_from = analysis

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    # If previous pipe not found, then create it.
                    model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis=analysis_from, glob_ini=glob_ini)

                    # Copy pipe and switch.
                    self.interpreter.pipe.copy(pipe_from=model_from_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                # Print
                subtitle(file=sys.stdout, text="Set grid r20 for pipe='%s'" % (pipe_name), prespace=3)

                # Select the model.
                self.interpreter.relax_disp.select_model(model)

                # Set r20 from min r2eff.
                self.interpreter.relax_disp.r20_from_min_r2eff(force=True)

                # Save results, and store the current settings dic to pipe.
                cdp.settings = self.settings

                if found and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)

                # Print for pipe name
                self.spin_display_params(pipe_name=pipe_name)


    def minimise_grid_search(self, inc=11, verbosity=0, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Use value.set on all pipes."""

        # Set default
        if model_from == None:
            model_from = model
        if analysis_from == None:
            analysis_from = analysis

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                # Try from analysis
                if not found:
                    # Check previous, and get the pipe name.
                    found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis_from, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    # If previous pipe not found, then create it.
                    model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis=analysis_from, glob_ini=glob_ini)

                    # Check if pipe exists. If not, try the R2eff pipe.
                    if not pipes.has_pipe(model_from_pipe_name):
                        model_from_pipe_name = self.name_pipe(method=self.method, model=MODEL_R2EFF, analysis='int', glob_ini=glob_ini)

                    # If not the R2eff pipe exist, then calculate it.
                    if not pipes.has_pipe(model_from_pipe_name):
                        self.calc_r2eff(methods=[self.method], list_glob_ini=[glob_ini])

                    # Copy pipe and switch.
                    self.interpreter.pipe.copy(pipe_from=model_from_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                # Select the model.
                self.interpreter.relax_disp.select_model(model)

                # Deselect insignificant spins.
                if model not in [MODEL_R2EFF, MODEL_NOREX]:
                    self.interpreter.relax_disp.insignificance(level=self.insignificance)

                # Print
                subtitle(file=sys.stdout, text="Grid search for pipe='%s'" % (pipe_name), prespace=3)

                # Grid search.
                if inc:
                    self.interpreter.minimise.grid_search(inc=inc, verbosity=verbosity, constraints=self.constraints, skip_preset=True)

                # Default values.
                else:
                    # The standard parameters.
                    for param in MODEL_PARAMS[model]:
                        self.interpreter.value.set(param=param, index=None, force=False)

                    # The optional R1 parameter.
                    if is_r1_optimised(model=model):
                        self.interpreter.value.set(param='r1', index=None)


                # Save results, and store the current settings dic to pipe.
                cdp.settings = self.settings

                # Define new pipe names.
                pipe_name = self.name_pipe(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini)
                resfile = pipe_name.replace(" ", "_")
                model_path = model.replace(" ", "_")
                path = self.results_dir+sep+model_path

                if found and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)

                # Print for pipe name
                self.spin_display_params(pipe_name=pipe_name)


    def cluster_spins(self, spin_id=None, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Method to select spins for a pipe."""

        # Set default
        if model_from == None:
            model_from = model
        if analysis_from == None:
            analysis_from = analysis

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
                    # If previous pipe not found, then create it.
                    model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis=analysis_from, glob_ini=glob_ini)

                    # Copy pipe and switch.
                    self.interpreter.pipe.copy(pipe_from=model_from_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                # Print
                subtitle(file=sys.stdout, text="Cluster spins '%s' for pipe='%s'" % (spin_id, pipe_name), prespace=3)

                # Select spins.
                self.interpreter.relax_disp.cluster(cluster_id='sel', spin_id=spin_id)

                # Save results, and store the current settings dic to pipe.
                cdp.settings = self.settings

                if found and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)

            # print clustered spins
            print("Clustered spins are:", cdp.clustering)


    def minimise_execute(self, verbosity=1, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Use value.set on all pipes."""

        # Set default
        if model_from == None:
            model_from = model
        if analysis_from == None:
            analysis_from = analysis

        # Loop over the methods.
        for method in methods:
            # Change the self key.
            self.set_self(key='method', value=method)

            # Loop over the glob ini:
            for glob_ini in list_glob_ini:
                # Check previous, and get the pipe name.
                found_pipe, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                # Try from analysis
                if not found_pipe:
                    # Check previous, and get the pipe name.
                    found_analysis, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis_from, glob_ini=glob_ini, bundle=self.method)

                if not (found_pipe or found_analysis):
                    # If previous pipe not found, then create it.
                    model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis=analysis_from, glob_ini=glob_ini)

                    # Check if pipe exists. If not, try grid pipe.
                    if not pipes.has_pipe(model_from_pipe_name):
                        model_from_pipe_name = self.name_pipe(method=self.method, model=model_from, analysis='grid', glob_ini=glob_ini)

                    # Copy pipe and switch.
                    self.interpreter.pipe.copy(pipe_from=model_from_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                # Select the model.
                self.interpreter.relax_disp.select_model(model)

                # Print
                subtitle(file=sys.stdout, text="Minimise for pipe='%s'" % (pipe_name), prespace=3)

                # Do the minimisation.
                self.interpreter.minimise.execute(min_algor=self.min_algor, func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=self.constraints, scaling=True, verbosity=verbosity)

                # Save results, and store the current settings dic to pipe.
                cdp.settings = self.settings

                # Define new pipe names.
                pipe_name = self.name_pipe(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini)
                resfile = pipe_name.replace(" ", "_")
                model_path = model.replace(" ", "_")
                path = self.results_dir+sep+model_path

                if found_pipe and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)

                # Print for pipe name
                self.spin_display_params(pipe_name=pipe_name)


    def name_pipe(self, method, model, analysis, glob_ini, clusterid=None):
        """Generate a unique name for the data pipe.

        @param prefix:  The prefix of the data pipe name.
        @type prefix:   str
        """

        # Cluster group is none, set to standard free spins.
        # cdp.clustering['free spins']
        if clusterid == None:
            clusterid = 'free spins'

        # The unique pipe name.
        name = "%s - %s - %s - %s - %s" % (method, model, analysis, glob_ini, clusterid)

        # Replace name with underscore.
        name = name.replace(" ", "_")

        # Return the name.
        return name


    def check_previous_result(self, method=None, model=None, analysis=None, glob_ini=None, clusterid=None, bundle=None):

        # Define if found and loaded
        found = False
        if bundle == None:
            bundle = self.pipe_bundle

        # Define the pipe name.
        pipe_name = self.name_pipe(method=method, model=model, analysis=analysis, glob_ini=glob_ini, clusterid=clusterid)

        # The results directory path.
        model_path = model.replace(" ", "_")
        path = self.results_dir+sep+model_path

        # The result file.
        resfile = pipe_name.replace(" ", "_")

        # First check if the pipe already exists. Then switch to it.
        if pipes.has_pipe(pipe_name):
            print("Detected the presence of previous '%s' pipe - switching to it." % pipe_name)
            self.interpreter.pipe.switch(pipe_name)
            found = True

        else:
            # Check that results do not already exist - i.e. a previous run was interrupted.
            path1 = get_file_path(file_name=resfile, dir=path)
            path2 = path1 + '.bz2'
            path3 = path1 + '.gz'

            #print("Path to R2eff file is: %s"%path1)
            if access(path1, F_OK) or access(path2, F_OK) or access(path2, F_OK):
                # Printout.
                print("Detected the presence of results files for the '%s' pipe - loading these instead of performing optimisation for a second time." % pipe_name)

                # Create a data new pipe and switch to it.
                self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=self.pipe_type, bundle=bundle)
                self.interpreter.pipe.switch(pipe_name)

                # Load the results.
                self.interpreter.results.read(file=resfile, dir=path)

                # Set found to True
                found = True

        return found, pipe_name, resfile, path


    def spin_display_params(self, spin_id=None, pipe_name=None):
        """Display parameters for model in pipe."""


        # First check if the pipe already exists. Then switch to it.
        if pipes.has_pipe(pipe_name):
            # Switch to the pipe.
            if pipes.cdp_name() != pipe_name:
                print("Detected the presence of previous '%s' pipe - switching to it." % pipe_name)
                self.interpreter.pipe.switch(pipe_name)

        else:
            # The result file.
            pipe_name_split = pipe_name.split("_-_")
            method = pipe_name_split[0]
            model = pipe_name_split[1]
            analysis = pipe_name_split[2]
            bundle = method

            model_path = model.replace(" ", "_")
            path = self.results_dir+sep+model_path
            # The result file.
            resfile = pipe_name.replace(" ", "_")

            # Check that results do not already exist - i.e. a previous run was interrupted.
            path1 = get_file_path(file_name=resfile, dir=path)
            path2 = path1 + '.bz2'
            path3 = path1 + '.gz'

            #print("Path to R2eff file is: %s"%path1)
            if access(path1, F_OK) or access(path2, F_OK) or access(path2, F_OK):
                # Printout.
                print("Detected the presence of results files for the '%s' pipe - loading these instead of performing optimisation for a second time." % pipe_name)

                # Create a data new pipe and switch to it.
                self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=self.pipe_type, bundle=bundle)
                self.interpreter.pipe.switch(pipe_name)

                # Load the results.
                self.interpreter.results.read(file=resfile, dir=path)

                # Set found to True
                found = True


        # Start dic.
        my_dic = {}
        spin_id_list = []

        # Define data list.
        data = []

        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(selection=spin_id, full_info=True, return_id=True, skip_desel=True):
            # Add key to dic.
            my_dic[spin_id] = {}
            # Store id, for ordering.
            spin_id_list.append(spin_id)

            # Add list to data.
            cur_data_list = [repr(mol_name), repr(resi), repr(resn), repr(cur_spin.num), repr(cur_spin.name), spin_id]

            # Get the parameters fitted in the model.
            params = cur_spin.params
            my_dic[spin_id]['params'] = params
            my_dic[spin_id]['params_err'] = []

            # Loop over params.
            for i, param in enumerate(params):
                # Set the param error name
                param_err = param + '_err'
                my_dic[spin_id]['params_err'].append(param_err)

                # If param in PARAMS_R20, values are stored in with parameter key.
                param_key_list = []
                if param in PARAMS_R20:
                    # Loop over frq key.
                    for exp_type, frq, offset, ei, mi, oi, in loop_exp_frq_offset(return_indices=True):
                        # Get the parameter key.
                        param_key = generate_r20_key(exp_type=exp_type, frq=frq)
                        param_key_list.append(param_key)
                        my_dic[spin_id]['param_key_list'] = param_key_list
                        my_dic[spin_id][param] = {}

                        # Get the Value.
                        if len(getattr(cur_spin, param)) == 0:
                            param_val = None
                        else:
                            param_val = deepcopy(getattr(cur_spin, param)[param_key])
                        my_dic[spin_id][param][param_key] = param_val

                        # Add information to data.
                        if param_val == None:
                            cur_data_list.append("%s"%param_val)
                        else:
                            cur_data_list.append("%3.3f"%param_val)

                else:
                    # Get the value.
                    param_val = deepcopy(getattr(cur_spin, param))
                    my_dic[spin_id][param] = param_val

                    # Add information to data.
                    if param_val == None:
                        cur_data_list.append("%s"%param_val)
                    else:
                        cur_data_list.append("%.3f"%param_val)

            # Add data.
            data.append(cur_data_list)

        # Collect header from spin 0.
        cur_spin_id = spin_id_list[0]
        cur_spin_params = my_dic[cur_spin_id]['params']
        cur_param_keys = my_dic[cur_spin_id]['param_key_list']

        # Define header.
        param_header = ["Molecule", "Res number", "Res name", "Spin number", "Spin name", "Spin id"]

        # Loop over params, add to header.
        for param in cur_spin_params:
            if param in PARAMS_R20:
                for param_key in cur_param_keys:
                    # Take the second last part of key.
                    cur_key = "%3.1f" % float(param_key.split()[-2])
                    hstring = "%s_%s" % (param, cur_key)
                    param_header.append(hstring)
            else:
                hstring = "%s" % (param)
                param_header.append(hstring)

        write_data(out=sys.stdout, headings=param_header, data=data)


    def get_dublicates(self, spectrum_ids, cpmg_frqs):
        """Method which return a list of tubles, where each tuble is a spectrum id and a list of spectrum ids which are replicated"""

        # Get the dublicates.
        dublicates = map(lambda val: (val, [i for i in xrange(len(cpmg_frqs)) if cpmg_frqs[i] == val]), cpmg_frqs)

        # Loop over the list of the mapping of cpmg frequency and duplications.
        list_dub_mapping = []
        for i, dub in enumerate(dublicates):
            # Get current spectum id.
            cur_spectrum_id = spectrum_ids[i]

            # Get the tuple of cpmg frequency and indexes of duplications.
            cpmg_frq, list_index_occur = dub

            # Collect mapping of index to id.
            id_list = []
            if len(list_index_occur) > 1:
                for list_index in list_index_occur:
                    id_list.append(spectrum_ids[list_index])

            # Store to list
            list_dub_mapping.append((cur_spectrum_id, id_list))

        return list_dub_mapping


    def col_int(self, method=None, list_glob_ini=None, selection=None):

        # Loop over the glob ini:
        res_dic = {}
        res_dic['method'] = method
        res_dic['selection'] = selection
        for glob_ini in list_glob_ini:
            # Get the pipe name for peak_intensity values.
            pipe_name = self.name_pipe(method=method, model='setup', analysis='int', glob_ini=glob_ini)

            # Check if pipe exists, or else calculate.
            if not pipes.has_pipe(pipe_name):
                self.set_int(methods=[method], list_glob_ini=[glob_ini])

            if pipes.cdp_name() != pipe_name and pipes.has_pipe(pipe_name):
                self.interpreter.pipe.switch(pipe_name)

            elif pipes.has_pipe(pipe_name) == False:
                continue

            # Results dictionary.
            res_dic[str(glob_ini)] = {}
            res_dic[str(glob_ini)]['peak_intensity'] = {}
            res_dic[str(glob_ini)]['peak_intensity_err'] = {}
            spin_point_peak_intensity_list = []
            spin_point_peak_intensity_err_list = []

            # Loop over the spins.
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(selection=selection, full_info=True, return_id=True, skip_desel=True):
                # Make spin dic.
                res_dic[str(glob_ini)]['peak_intensity'][spin_id] = {}
                res_dic[str(glob_ini)]['peak_intensity_err'][spin_id] = {}

                # Loop over spectrum_ids.
                for s_id in cdp.spectrum_ids:
                    # Check for bad data has skipped peak_intensity points
                    if s_id in cur_spin.peak_intensity:
                        peak_intensity_point = cur_spin.peak_intensity[s_id]
                        peak_intensity_err_point = cur_spin.peak_intensity_err[s_id]

                        res_dic[str(glob_ini)]['peak_intensity'][spin_id][s_id] = peak_intensity_point
                        res_dic[str(glob_ini)]['peak_intensity_err'][spin_id][s_id] = peak_intensity_err_point
                        spin_point_peak_intensity_list.append(peak_intensity_point)
                        spin_point_peak_intensity_err_list.append(peak_intensity_err_point)

            res_dic[str(glob_ini)]['peak_intensity_arr'] = asarray(spin_point_peak_intensity_list)
            res_dic[str(glob_ini)]['peak_intensity_err_arr'] = asarray(spin_point_peak_intensity_err_list)

        return res_dic


    def plot_int_corr(self, corr_data, show=False, write_stats=False):

        # Define figure.
        # Nr of columns is number of datasets.
        nr_cols = len(corr_data)
        # Nr of rows, is 2. With and without scaling.
        nr_rows = 4

        # Define figure
        fig, axises = plt.subplots(nrows=nr_rows, ncols=nr_cols)
        fig.suptitle('Correlation plot')

        # axises is a tuple with number of elements corresponding to number of rows.
        # Each sub-tuple contains axis for each column.

        # For writing out stats.
        data_dic = {}

        # Loop over the rows.
        for i, row_axises in enumerate(axises):
            # Loop over the columns.
            for j, ax in enumerate(row_axises) :
                # Extract from lists.
                data, methods, glob_inis = corr_data[j]
                data_x, data_y = data
                method_x, method_y = methods
                glob_ini_x, glob_ini_y = glob_inis

                x = data_x[str(glob_ini_x)]['peak_intensity_arr']
                x_err = data_x[str(glob_ini_x)]['peak_intensity_err_arr']
                np = len(x)

                y = data_y[str(glob_ini_y)]['peak_intensity_arr']
                y_err = data_y[str(glob_ini_y)]['peak_intensity_err_arr']

                # If row 1.
                if i == 0:
                    # Add to data dic.
                    method_xy_NI = "int_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                    data_dic[method_xy_NI] = []

                    ax.plot(x, x, 'o', label='%s vs. %s' % (method_x, method_x))
                    ax.plot(x, y, '.', label='%s vs. %s' % (method_y, method_x) )

                    np = len(y)
                    ax.set_title(r'$I$' + ' for %s %i vs. %s %i. np=%i' % (method_y, glob_ini_y, method_x, glob_ini_x, np), fontsize=10)
                    ax.legend(loc='upper center', shadow=True, prop=fontP)
                    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
                    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
                    ax.set_xlabel(r'$I$')
                    ax.set_ylabel(r'$I$')

                    # Calculate straight line.
                    # Linear a, with no intercept.
                    a = sum(x * y) / sum(x**2)
                    min_x = min(x)
                    max_x =  max(x)
                    step_x = (max_x - min_x) / np
                    x_arange = arange(min_x, max_x, step_x)
                    y_arange = a * x_arange

                    # Add to data.
                    for k, x_k in enumerate(x):
                        y_k = y[k]
                        x_arange_k = x_arange[k]
                        y_arange_k = y_arange[k]
                        data_dic[method_xy_NI].append(["%3.5f"%x_k, "%3.5f"%y_k, "%3.5f"%x_arange_k, "%3.5f"%y_arange_k])

                # Scale intensity
                if i == 1:

                    x_norm = x / x.max()
                    y_norm = y / y.max()

                    ax.plot(x_norm, x_norm, 'o', label='%s vs. %s' % (method_x, method_x))
                    ax.plot(x_norm, y_norm, '.', label='%s vs. %s' % (method_y, method_x))

                    np = len(y_norm)
                    ax.set_title('Normalised intensity for %s %i vs. %s %i. np=%i' % (method_y, glob_ini_y, method_x, glob_ini_x, np), fontsize=10)
                    ax.legend(loc='upper center', shadow=True, prop = fontP)
                    ax.set_xlabel(r'$\mathrm{Norm.} I$')
                    ax.set_ylabel(r'$\mathrm{Norm.} I$')


                # Error.
                if i == 2:
                    # Add to data dic.
                    method_xy_NI = "int_err_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                    data_dic[method_xy_NI] = []

                    ax.plot(x_err, x_err, 'o', label='%s vs. %s' % (method_x, method_x))
                    ax.plot(x_err, y_err, '.', label='%s vs. %s' % (method_y, method_x))

                    np = len(y_err)
                    ax.set_title(r'$\sigma(I)$' + ' for %s %i vs. %s %i. np=%i' % (method_y, glob_ini_y, method_x, glob_ini_x, np), fontsize=10)
                    ax.legend(loc='upper center', shadow=True, prop = fontP)
                    ax.set_xlabel(r'$\sigma(I)$')
                    ax.set_ylabel(r'$\sigma(I)$')

                    # Calculate straight line.
                    # Linear a, with no intercept.
                    a = sum(x_err * y_err) / sum(x_err**2)
                    min_x = min(x_err)
                    max_x =  max(x_err)
                    step_x = (max_x - min_x) / np
                    x_err_arange = arange(min_x, max_x, step_x)
                    y_err_arange = a * x_err_arange

                    # Add to data.
                    for k, x_err_k in enumerate(x_err):
                        y_err_k = y_err[k]
                        x_err_arange_k = x_err_arange[k]
                        y_err_arange_k = y_err_arange[k]
                        data_dic[method_xy_NI].append(["%3.5f"%x_err_k, "%3.5f"%y_err_k, "%3.5f"%x_err_arange_k, "%3.5f"%y_err_arange_k])


                # Intensity to error.
                if i == 3:

                    x_to_x_err = x / x_err
                    y_to_y_err = y / y_err

                    ax.plot(x_to_x_err, x_to_x_err, 'o', label='%s vs. %s' % (method_x, method_x))
                    ax.plot(x_to_x_err, y_to_y_err, '.', label='%s vs. %s' % (method_y, method_x))

                    np = len(y_to_y_err)
                    ax.set_title(r'$I/\sigma(I)$' + ' for %s %i vs. %s %i. np=%i' % (method_y, glob_ini_y, method_x, glob_ini_x, np), fontsize=10)
                    ax.legend(loc='upper center', shadow=True, prop = fontP)
                    ax.set_xlabel(r'$I/\sigma(I)$')
                    ax.set_ylabel(r'$I/\sigma(I)$')

            plt.tight_layout()

        # Loop over columns for writing data.
        # Write to file.
        if write_stats:
            # Re-order the data.
            headings_all = []
            method_xy_NI_all = []
            # Loop over the columns.
            for j in range(nr_cols):
                headings_j = []
                method_xy_NI_j = []
                # Loop over rows
                for i in range(nr_rows):
                    # Extract from lists.
                    data, methods, glob_inis = corr_data[j]
                    method_x, method_y = methods
                    glob_ini_x, glob_ini_y = glob_inis

                    # If row 1.
                    if i == 0:
                        # Add to headings.
                        method_x_NI = "int_%s%s" % (method_x, glob_ini_x)
                        method_y_NI = "int_%s%s" % (method_y, glob_ini_y)
                        method_x_NI_lin = "int_lin_%s%s" % (method_x, glob_ini_x)
                        method_y_NI_lin = "int_lin_%s%s" % (method_y, glob_ini_y)
                        headings_j = headings_j + [method_x_NI, method_y_NI, method_x_NI_lin, method_y_NI_lin]

                        method_xy_NI = "int_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                        method_xy_NI_j.append(method_xy_NI)

                    # Error.
                    if i == 2:
                        # Add to headings
                        method_x_NI = "int_err_%s%s" % (method_x, glob_ini_x)
                        method_y_NI = "int_err_%s%s" % (method_y, glob_ini_y)
                        method_x_NI_lin = "int_err_lin_%s%s" % (method_x, glob_ini_x)
                        method_y_NI_lin = "int_err_lin_%s%s" % (method_y, glob_ini_y)
                        headings_j = headings_j + [method_x_NI, method_y_NI, method_x_NI_lin, method_y_NI_lin]

                        method_xy_NI = "int_err_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                        method_xy_NI_j.append(method_xy_NI)

                headings_all.append(headings_j)
                method_xy_NI_all.append(method_xy_NI_j)

            # Loop over the columns.
            for j, headings_j in enumerate(headings_all):
                method_xy_NI_j = method_xy_NI_all[j]

                data_w = []
                data_int = data_dic[method_xy_NI_j[0]]
                data_int_err = data_dic[method_xy_NI_j[1]]

                for k, data_int_k in enumerate(data_int):
                    data_int_err_k = data_int_err[k]
                    data_w.append(data_int_k + data_int_err_k)

                # Define file name.
                data, methods, glob_inis = corr_data[j]
                data_x, data_y = data
                method_x, method_y = methods
                glob_ini_x, glob_ini_y = glob_inis
                np = len(data_int)

                # Get the spin selection for correlation.
                selection = data_x['selection']

                file_name_ini = 'int_corr_%s_%s_%s_%s_NP_%i' % (method_x, glob_ini_x, method_y, glob_ini_y, np)
                if selection == None:
                    file_name_ini = file_name_ini + '_all'
                else:
                    file_name_ini = file_name_ini + '_sel'

                file_name = file_name_ini + '.txt'
                path = self.results_dir

                # save figure
                # Write png.
                png_file_name = file_name_ini + '.png'
                png_file_path = get_file_path(file_name=png_file_name, dir=path)
                plt.savefig(png_file_path, bbox_inches='tight')

                # Write file
                file_obj, file_path = open_write_file(file_name=file_name, dir=path, force=True, compress_type=0, verbosity=1, return_path=True)

                # Write data.
                write_data(out=file_obj, headings=headings_j, data=data_w)

                # Close file.
                file_obj.close()

        if show:
            plt.show()


    def get_int_stat_dic(self, list_int_dics=None, list_glob_ini=None):

        # Loop over the result dictionaries:
        res_dic = {}
        for i, int_dic in enumerate(list_int_dics):
            # Let the reference dic be initial dic
            int_dic_ref = list_int_dics[0]
            method_ref = int_dic_ref['method']
            res_dic['method_ref'] = method_ref
            glob_ini_ref = list_glob_ini[0]
            res_dic['glob_ini_ref'] = str(glob_ini_ref)
            selection = int_dic_ref['selection']
            res_dic['selection'] = selection

            # Let the reference int array be the initial glob.
            int_arr_ref = int_dic_ref[str(glob_ini_ref)]['peak_intensity_arr']
            res_dic['int_arr_ref'] = int_arr_ref
            int_err_arr_ref = int_dic_ref[str(glob_ini_ref)]['peak_intensity_err_arr']
            res_dic['int_err_arr_ref'] = int_err_arr_ref

            # Get the current method
            method_cur = int_dic['method']
            res_dic[method_cur] = {}
            res_dic[method_cur]['method'] = method_cur
            res_dic[method_cur]['sampling_sparseness'] = []
            res_dic[method_cur]['glob_ini'] = []
            res_dic[method_cur]['int_norm_std'] = []

            # Other stats.
            res_dic[method_cur]['r_xy_int'] = []
            res_dic[method_cur]['a_int'] = []
            res_dic[method_cur]['r_xy_int_err'] = []
            res_dic[method_cur]['a_int_err'] = []

            # Now loop over glob_ini:
            for glob_ini in list_glob_ini:
                # Get the array, if it exists.
                if str(glob_ini) not in int_dic:
                    continue

                # Get the data.
                int_arr = int_dic[str(glob_ini)]['peak_intensity_arr']
                int_err_arr = int_dic[str(glob_ini)]['peak_intensity_err_arr']

                # This require that all number of points are equal.
                # If they are not of same length, then dont even bother to continue.
                if len(int_arr) != len(int_arr_ref):
                    continue

                # Store x
                sampling_sparseness = float(glob_ini) / float(glob_ini_ref) * 100.
                res_dic[method_cur]['sampling_sparseness'].append(sampling_sparseness)
                res_dic[method_cur]['glob_ini'].append(glob_ini)

                # Store to result dic.
                res_dic[method_cur][str(glob_ini)] = {}
                res_dic[method_cur][str(glob_ini)]['sampling_sparseness'] = sampling_sparseness
                res_dic[method_cur][str(glob_ini)]['int_arr'] = int_arr
                res_dic[method_cur][str(glob_ini)]['int_err_arr'] = int_err_arr

                # Calculate sample correlation coefficient, measure of goodness-of-fit of linear regression
                # Without intercept.
                x = int_arr_ref
                y = int_arr

                a_int = sum(x*y) / sum(x**2)
                r_xy_int = sum(x*y) / sqrt(sum(x**2) * sum(y**2))

                x = int_err_arr_ref
                y = int_err_arr
                a_int_err = sum(x*y) / sum(x**2)
                r_xy_int_err = sum(x*y) / sqrt(sum(x**2) * sum(y**2))

                print(method_ref, method_cur, sampling_sparseness, glob_ini, r_xy_int**2, a_int, r_xy_int_err**2, a_int_err)

                # Store to result dic.
                res_dic[method_cur][str(glob_ini)]['r_xy_int'] = r_xy_int
                res_dic[method_cur]['r_xy_int'].append(r_xy_int)
                res_dic[method_cur][str(glob_ini)]['a_int'] = a_int
                res_dic[method_cur]['a_int'].append(a_int)

                res_dic[method_cur][str(glob_ini)]['r_xy_int_err'] = r_xy_int_err
                res_dic[method_cur]['r_xy_int_err'].append(r_xy_int_err)
                res_dic[method_cur][str(glob_ini)]['a_int_err'] = a_int_err
                res_dic[method_cur]['a_int_err'].append(a_int_err)

            res_dic[method_cur]['sampling_sparseness'] = asarray(res_dic[method_cur]['sampling_sparseness'])
            res_dic[method_cur]['glob_ini'] = asarray(res_dic[method_cur]['glob_ini'])

            res_dic[method_cur]['r_xy_int'] = asarray(res_dic[method_cur]['r_xy_int'])
            res_dic[method_cur]['a_int'] = asarray(res_dic[method_cur]['a_int'])
            res_dic[method_cur]['r_xy_int_err'] = asarray(res_dic[method_cur]['r_xy_int_err'])
            res_dic[method_cur]['a_int_err'] = asarray(res_dic[method_cur]['a_int_err'])

        return res_dic


    def plot_int_stat(self, int_stat_dic=None, methods=[], list_glob_ini=[], show=False, write_stats=False):

        # Define figure
        fig, axises = plt.subplots(nrows=2, ncols=1)
        fig.suptitle('Stats per NI')
        ax1, ax2 = axises

        # Catch min and max values for all methods.
        min_a = 1.0
        max_a = 0.0

        min_r_xy2 = 1.0
        max_r_xy2 = 0.0

        # Prepare header for writing.
        selection = int_stat_dic['selection']

        # For writing out stats.
        headings = []
        data_dic = {}
        data_dic_methods = []
        i_max = 0

        for method in methods:
            if method not in int_stat_dic:
                continue

            # Use NI as x.
            NI = int_stat_dic[method]['glob_ini']
            # Use sampling_sparseness as x.
            SS = int_stat_dic[method]['sampling_sparseness']

            # Add to headings.
            headings = headings + ['method', 'SS', 'NI', 'slope_int', 'rxy2_int', 'slope_int_err', 'rxy2_int_err']

            # Get stats.
            # Linear regression slope, without intercept
            a_int = int_stat_dic[method]['a_int']

            if max(a_int) > max_a:
                max_a = max(a_int)
            if min(a_int) < min_a:
                min_a = min(a_int)

            # sample correlation coefficient, without intercept
            r_xy_int = int_stat_dic[method]['r_xy_int']
            r_xy_int2 = r_xy_int**2

            if max(r_xy_int2) > max_r_xy2:
                max_r_xy2 = max(r_xy_int2)
            if min(r_xy_int2) < min_r_xy2:
                min_r_xy2 = min(r_xy_int2)

            # For just the int values
            a_int_err = int_stat_dic[method]['a_int_err']
            r_xy_int_err = int_stat_dic[method]['r_xy_int_err']
            r_xy_int_err2 = r_xy_int_err**2

            # Add to data.
            data_dic[method] = {}
            data_dic_methods.append(method)
            for i, NI_i in enumerate(NI):
                SS_i = SS[i]
                a_int_i = a_int[i]
                r_xy_int2_i = r_xy_int2[i]
                a_int_err_i = a_int_err[i]
                r_xy_int_err2_i = r_xy_int_err2[i]
                data_dic[method][str(i)] = ["%3.5f"%SS_i, "%i"%NI_i, "%3.5f"%a_int_i, "%3.5f"%r_xy_int2_i, "%3.5f"%a_int_err_i, "%3.5f"%r_xy_int_err2_i]
                if i > i_max:
                    i_max = i

            t = ax1.plot(SS, a_int, ".--", label='%s slope int'%method)
            color = t[0].get_color()
            ax1.plot(SS, a_int_err, ".-", label='%s slope  int_err'%method, color=color)

            t = ax2.plot(SS, r_xy_int2, "o--", label='%s r2 int'%method)
            color = t[0].get_color()
            ax2.plot(SS, r_xy_int_err2, "o-", label='%s r2 int_err'%method, color=color)

        # Loop over methods for writing data.
        data = []

        for i in range(0, i_max+1):
            data_i = []
            for method in data_dic_methods:
                data_dic_m = data_dic[method]
                # Loop over all possible data points.
                if str(i) in data_dic_m:
                    data_i = data_i + [method] + data_dic_m[str(i)]
                else:
                    data_i = data_i + [method] + ["0", "0", "0", "0", "0", "0"]

            data.append(data_i)

        # Set legends.
        ax1.legend(loc='lower left', shadow=True, prop = fontP)
        #ax1.set_xlabel('NI')
        ax1.set_xlabel('SS')
        #ax1.set_ylabel(r'$\sigma ( R_{2,\mathrm{eff}} )$')
        ax1.set_ylabel('Linear regression slope, without intercept')
        #ax1.set_xticks(NI)
        #ax1.set_xticks(SS)
        ax1.set_ylim(min_a*0.95, max_a*1.05)
        ax1.invert_xaxis()

        ax2.legend(loc='lower right', shadow=True, prop = fontP)
        ax2.set_ylabel('Sample correlation ' + r'$r_{xy}^2$')
        #ax2.set_xticks(NI)
        #ax2.set_xticks(SS)
        ax2.set_ylim(min_r_xy2*0.95, max_r_xy2*1.05)
        ax2.invert_xaxis()

        # Determine filename.
        if selection == None:
            file_name_ini = 'int_stat_all'
        else:
            file_name_ini = 'int_stat_sel'

        # Write png.
        png_file_name = file_name_ini + '.png'
        png_file_path = get_file_path(file_name=png_file_name, dir=self.results_dir)

        # Write to file.
        if write_stats:
            # save figure
            plt.savefig(png_file_path, bbox_inches='tight')

            file_name = file_name_ini + '.txt'
            path = self.results_dir
            file_obj, file_path = open_write_file(file_name=file_name, dir=path, force=True, compress_type=0, verbosity=1, return_path=True)

            # Write data.
            write_data(out=file_obj, headings=headings, data=data)

            # Close file.
            file_obj.close()

        # Plot data.
        if show:
            plt.show()


    def col_r2eff(self, method=None, list_glob_ini=None, selection=None):

        # Loop over the glob ini:
        res_dic = {}
        res_dic['method'] = method
        res_dic['selection'] = selection
        for glob_ini in list_glob_ini:
            # Get the pipe name for R2eff values.
            pipe_name = self.name_pipe(method=method, model=MODEL_R2EFF, analysis='int', glob_ini=glob_ini)

            # Check if pipe exists, or else calculate.
            if not pipes.has_pipe(pipe_name):
                self.calc_r2eff(methods=[method], list_glob_ini=[glob_ini])

            if pipes.cdp_name() != pipe_name and pipes.has_pipe(pipe_name):
                self.interpreter.pipe.switch(pipe_name)

            elif pipes.has_pipe(pipe_name) == False:
                continue

            # Results dictionary.
            res_dic[str(glob_ini)] = {}
            res_dic[str(glob_ini)]['r2eff'] = {}
            res_dic[str(glob_ini)]['r2eff_err'] = {}
            spin_point_r2eff_list = []
            spin_point_r2eff_err_list = []

            # Loop over the spins.
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(selection=selection, full_info=True, return_id=True, skip_desel=True):
                # Make spin dic.
                res_dic[str(glob_ini)]['r2eff'][spin_id] = {}
                res_dic[str(glob_ini)]['r2eff_err'][spin_id] = {}

                # Loop over the R2eff points
                for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
                    # Define the key.
                    data_key = return_param_key_from_data(exp_type=self.exp_type, frq=frq, offset=offset, point=point)

                    # Check for bad data has skipped r2eff points
                    if data_key in cur_spin.r2eff:
                        r2eff_point = cur_spin.r2eff[data_key]
                        r2eff_err_point = cur_spin.r2eff_err[data_key]

                        res_dic[str(glob_ini)]['r2eff'][spin_id][data_key] = r2eff_point
                        res_dic[str(glob_ini)]['r2eff_err'][spin_id][data_key] = r2eff_err_point
                        spin_point_r2eff_list.append(r2eff_point)
                        spin_point_r2eff_err_list.append(r2eff_err_point)

            res_dic[str(glob_ini)]['r2eff_arr'] = asarray(spin_point_r2eff_list)
            res_dic[str(glob_ini)]['r2eff_err_arr'] = asarray(spin_point_r2eff_err_list)

        return res_dic


    def plot_r2eff_corr(self, corr_data, show=False, write_stats=False):

        # Define figure.
        # Nr of columns is number of datasets.
        nr_cols = len(corr_data)
        # Nr of rows, is 2. With and without scaling.
        nr_rows = 2

        # Define figure
        fig, axises = plt.subplots(nrows=nr_rows, ncols=nr_cols)
        fig.suptitle('Correlation plot')

        # axises is a tuple with number of elements corresponding to number of rows.
        # Each sub-tuple contains axis for each column.

        # For writing out stats.
        data_dic = {}

        # Loop over the rows.
        for i, row_axises in enumerate(axises):
            # Loop over the columns.
            for j, ax in enumerate(row_axises):
                # Extract from lists.
                data, methods, glob_inis = corr_data[j]
                data_x, data_y = data
                method_x, method_y = methods
                glob_ini_x, glob_ini_y = glob_inis

                x = data_x[str(glob_ini_x)]['r2eff_arr']
                x_err = data_x[str(glob_ini_x)]['r2eff_err_arr']
                np = len(x)

                y = data_y[str(glob_ini_y)]['r2eff_arr']
                y_err = data_y[str(glob_ini_y)]['r2eff_err_arr']

                # If row 1.
                if i == 0:
                    # Add to data dic.
                    method_xy_NI = "r2eff_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                    data_dic[method_xy_NI] = []

                    # Calculate straight line.
                    # Linear a, with no intercept.
                    a = sum(x * y) / sum(x**2)
                    min_x = min(x)
                    max_x =  max(x)
                    step_x = (max_x - min_x) / np
                    x_arange = arange(min_x, max_x, step_x)
                    y_arange = a * x_arange

                    ax.plot(x, x, 'o', label='%s vs. %s' % (method_x, method_x))
                    ax.plot(x_arange, x_arange, 'b--')
                    if len(x) != len(y):
                        print(len(x), len(y))
                    ax.plot(x, y, '.', label='%s vs. %s' % (method_y, method_x) )
                    ax.plot(x_arange, y_arange, 'g--')

                    ax.set_title(r'$R_{2,\mathrm{eff}}$' + ' for %s %i vs. %s %i. np=%i' % (method_y, glob_ini_y, method_x, glob_ini_x, np), fontsize=10)
                    ax.legend(loc='upper left', shadow=True, prop = fontP)
                    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
                    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
                    ax.set_xlabel(r'$R_{2,\mathrm{eff}}$')
                    ax.set_ylabel(r'$R_{2,\mathrm{eff}}$')

                    # Add to data.
                    for k, x_k in enumerate(x):
                        y_k = y[k]
                        x_arange_k = x_arange[k]
                        y_arange_k = y_arange[k]
                        data_dic[method_xy_NI].append(["%3.5f"%x_k, "%3.5f"%y_k, "%3.5f"%x_arange_k, "%3.5f"%y_arange_k])

                # R2eff to error.
                if i == 1:
                    # Add to data dic.
                    method_xy_NI = "r2eff_to_err_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                    data_dic[method_xy_NI] = []

                    x_to_x_err = x / x_err
                    y_to_y_err = y / y_err

                    # Calculate straight line.
                    # Linear a, with no intercept.
                    a = sum(x_to_x_err * y_to_y_err) / sum(x_to_x_err**2)
                    min_x = min(x_to_x_err)
                    max_x =  max(x_to_x_err)
                    step_x = (max_x - min_x) / np
                    x_to_x_err_arange = arange(min_x, max_x, step_x)
                    y_to_x_err_arange = a * x_to_x_err_arange

                    ax.plot(x_to_x_err, x_to_x_err, 'o', label='%s vs. %s' % (method_x, method_x))
                    ax.plot(x_to_x_err_arange, x_to_x_err_arange, 'b--')
                    ax.plot(x_to_x_err, y_to_y_err, '.', label='%s vs. %s' % (method_y, method_x) )
                    ax.plot(x_to_x_err_arange, y_to_x_err_arange, 'g--')

                    ax.set_title(r'$R_{2,\mathrm{eff}}/\sigma(R_{2,\mathrm{eff}})$' + ' for %s %i vs. %s %i. np=%i' % (method_y, glob_ini_y, method_x, glob_ini_x, np), fontsize=10)
                    ax.legend(loc='upper left', shadow=True, prop = fontP)
                    ax.set_xlabel(r'$R_{2,\mathrm{eff}}/\sigma(R_{2,\mathrm{eff}})$')
                    ax.set_ylabel(r'$R_{2,\mathrm{eff}}/\sigma(R_{2,\mathrm{eff}})$')

                    # Add to data.
                    for k, x_to_x_err_k in enumerate(x_to_x_err):
                        y_to_y_err_k = y_to_y_err[k]
                        x_to_x_err_arange_k = x_to_x_err_arange[k]
                        y_to_x_err_arange_k = y_to_x_err_arange[k]
                        data_dic[method_xy_NI].append(["%3.5f"%x_to_x_err_k, "%3.5f"%y_to_y_err_k, "%3.5f"%x_to_x_err_arange_k, "%3.5f"%y_to_x_err_arange_k])


        plt.tight_layout()

        # Loop over columns for writing data.
        # Write to file.
        if write_stats:
            # Re-order the data.
            headings_all = []
            method_xy_NI_all = []
            # Loop over the columns.
            for j in range(nr_cols):
                headings_j = []
                method_xy_NI_j = []
                # Loop over rows
                for i in range(nr_rows):
                    # Extract from lists.
                    data, methods, glob_inis = corr_data[j]
                    method_x, method_y = methods
                    glob_ini_x, glob_ini_y = glob_inis

                    # If row 1.
                    if i == 0:
                        # Add to headings.
                        method_x_NI = "r2eff_%s%s" % (method_x, glob_ini_x)
                        method_y_NI = "r2eff_%s%s" % (method_y, glob_ini_y)
                        method_x_NI_lin = "r2eff_lin_%s%s" % (method_x, glob_ini_x)
                        method_y_NI_lin = "r2eff_lin_%s%s" % (method_y, glob_ini_y)
                        headings_j = headings_j + [method_x_NI, method_y_NI, method_x_NI_lin, method_y_NI_lin]

                        method_xy_NI = "r2eff_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                        method_xy_NI_j.append(method_xy_NI)

                    # R2eff to error.
                    if i == 1:
                        # Add to headings
                        method_x_NI = "r2eff_to_err_%s%s" % (method_x, glob_ini_x)
                        method_y_NI = "r2eff_to_err_%s%s" % (method_y, glob_ini_y)
                        method_x_NI_lin = "r2eff_to_err_lin_%s%s" % (method_x, glob_ini_x)
                        method_y_NI_lin = "r2eff_to_err_lin_%s%s" % (method_y, glob_ini_y)
                        headings_j = headings_j + [method_x_NI, method_y_NI, method_x_NI_lin, method_y_NI_lin]

                        method_xy_NI = "r2eff_to_err_%s%s_%s%s" % (method_x, glob_ini_x, method_y, glob_ini_y)
                        method_xy_NI_j.append(method_xy_NI)

                headings_all.append(headings_j)
                method_xy_NI_all.append(method_xy_NI_j)

            # Loop over the columns.
            for j, headings_j in enumerate(headings_all):
                method_xy_NI_j = method_xy_NI_all[j]

                data_w = []
                data_r2eff = data_dic[method_xy_NI_j[0]]
                data_r2eff_to_err = data_dic[method_xy_NI_j[1]]

                for k, data_r2eff_k in enumerate(data_r2eff):
                    data_r2eff_to_err_k = data_r2eff_to_err[k]
                    data_w.append(data_r2eff_k + data_r2eff_to_err_k)

                # Define file name.
                data, methods, glob_inis = corr_data[j]
                data_x, data_y = data
                method_x, method_y = methods
                glob_ini_x, glob_ini_y = glob_inis
                np = len(data_r2eff)

                # Get the spin selection for correlation.
                selection = data_x['selection']

                file_name_ini = 'r2eff_corr_%s_%s_%s_%s_NP_%i' % (method_x, glob_ini_x, method_y, glob_ini_y, np)
                if selection == None:
                    file_name_ini = file_name_ini + '_all'
                else:
                    file_name_ini = file_name_ini + '_sel'

                file_name = file_name_ini + '.txt'
                path = self.results_dir

                # save figure
                # Write png.
                png_file_name = file_name_ini + '.png'
                png_file_path = get_file_path(file_name=png_file_name, dir=path)
                plt.savefig(png_file_path, bbox_inches='tight')

                # Write file
                file_obj, file_path = open_write_file(file_name=file_name, dir=path, force=True, compress_type=0, verbosity=1, return_path=True)

                # Write data.
                write_data(out=file_obj, headings=headings_j, data=data_w)

                # Close file.
                file_obj.close()

        if show:
            plt.show()


    def get_r2eff_stat_dic(self, list_r2eff_dics=None, list_glob_ini=None):

        # Loop over the result dictionaries:
        res_dic = {}
        for i, r2eff_dic in enumerate(list_r2eff_dics):
            # Let the reference dic be initial dic
            r2eff_dic_ref = list_r2eff_dics[0]
            method_ref = r2eff_dic_ref['method']
            res_dic['method_ref'] = method_ref
            glob_ini_ref = list_glob_ini[0]
            res_dic['glob_ini_ref'] = str(glob_ini_ref)
            selection = r2eff_dic_ref['selection']
            res_dic['selection'] = selection

            # Let the reference R2eff array be the initial glob.
            r2eff_arr_ref = r2eff_dic_ref[str(glob_ini_ref)]['r2eff_arr']
            res_dic['r2eff_arr_ref'] = r2eff_arr_ref
            r2eff_err_arr_ref = r2eff_dic_ref[str(glob_ini_ref)]['r2eff_err_arr']
            res_dic['r2eff_err_arr_ref'] = r2eff_err_arr_ref

            # Get the current method
            method_cur = r2eff_dic['method']
            res_dic[method_cur] = {}
            res_dic[method_cur]['method'] = method_cur
            res_dic[method_cur]['sampling_sparseness'] = []
            res_dic[method_cur]['glob_ini'] = []
            res_dic[method_cur]['r2eff_norm_std'] = []

            # Other stats.
            res_dic[method_cur]['pearsons_correlation_coefficient'] = []
            res_dic[method_cur]['two_tailed_p_value'] = []
            res_dic[method_cur]['r_xy'] = []
            res_dic[method_cur]['a'] = []
            res_dic[method_cur]['r_xy_2'] = []
            res_dic[method_cur]['a_2'] = []
            res_dic[method_cur]['r_xy_int'] = []
            res_dic[method_cur]['a_int'] = []
            res_dic[method_cur]['b_int'] = []

            # Now loop over glob_ini:
            for glob_ini in list_glob_ini:
                # Get the array, if it exists.
                if str(glob_ini) not in r2eff_dic:
                    continue

                # Get the data.
                r2eff_arr = r2eff_dic[str(glob_ini)]['r2eff_arr']
                r2eff_err_arr = r2eff_dic[str(glob_ini)]['r2eff_err_arr']

                # Make a normalised R2eff array according to reference.
                # This require that all number of points are equal.
                # If they are not of same length, then dont even bother to continue.
                if len(r2eff_arr) != len(r2eff_arr_ref):
                    continue

                # Get the normalised array.
                r2eff_norm_arr = r2eff_arr/r2eff_arr_ref

                # Calculate the standard deviation
                r2eff_norm_std = std(r2eff_norm_arr, ddof=1)

                # Get the diff, then norm
                r2eff_diff_norm_arr = (r2eff_arr - r2eff_arr_ref) / r2eff_arr_ref
                r2eff_diff_norm_std = std(r2eff_diff_norm_arr, ddof=1)

                # Store x
                sampling_sparseness = float(glob_ini) / float(glob_ini_ref) * 100.
                res_dic[method_cur]['sampling_sparseness'].append(sampling_sparseness)
                res_dic[method_cur]['glob_ini'].append(glob_ini)

                # Store to result dic.
                res_dic[method_cur][str(glob_ini)] = {}
                res_dic[method_cur][str(glob_ini)]['sampling_sparseness'] = sampling_sparseness
                res_dic[method_cur][str(glob_ini)]['r2eff_arr'] = r2eff_arr
                res_dic[method_cur][str(glob_ini)]['r2eff_norm_arr'] = r2eff_norm_arr
                res_dic[method_cur][str(glob_ini)]['r2eff_norm_std'] = r2eff_norm_std
                res_dic[method_cur]['r2eff_norm_std'].append(r2eff_norm_std)

                res_dic[method_cur][str(glob_ini)]['r2eff_diff_norm_arr'] = r2eff_diff_norm_arr
                res_dic[method_cur][str(glob_ini)]['r2eff_diff_norm_std'] = r2eff_diff_norm_std

                ### Calculate for value over error.

                # Calculate the R2eff versus R2eff error.
                r2eff_vs_err_ref = r2eff_arr_ref / r2eff_err_arr_ref
                r2eff_vs_err = r2eff_arr / r2eff_err_arr

                # Get the statistics from scipy.
                pearsons_correlation_coefficient, two_tailed_p_value = pearsonr(r2eff_vs_err_ref, r2eff_vs_err)

                # With intercept at axis.
                # Calculate sample correlation coefficient, measure of goodness-of-fit of linear regression
                x = r2eff_vs_err_ref
                x_m = mean(x)
                y = r2eff_vs_err
                y_m = mean(r2eff_vs_err)

                # Solve by linear least squares. f(x) = a*x + b.
                n = len(y)
                a_int = (sum(x*y) - 1./n * sum(x) * sum(y) ) / ( sum(x**2) - 1./n * (sum(x))**2 )
                b_int = 1./n * sum(y) - a_int * 1./n * sum(x)

                r_xy_int = sum( (x - x_m)*(y - y_m) ) / sqrt( sum((x - x_m)**2) * sum((y - y_m)**2) )

                # Without intercept.
                a = sum(x*y) / sum(x**2)
                r_xy = sum(x*y) / sqrt(sum(x**2) * sum(y**2))

                # Without intercept for just R2eff.
                x_2 = r2eff_arr_ref
                y_2 = r2eff_arr
                a_2 = sum(x_2*y_2) / sum(x_2**2)
                r_xy_2 = sum(x_2*y_2) / sqrt(sum(x_2**2) * sum(y_2**2))

                #print(method_ref, method_cur, sampling_sparseness, glob_ini, pearsons_correlation_coefficient, r_xy**2, a, r_xy_int**2, a_int, b_int)
                print(method_ref, method_cur, sampling_sparseness, glob_ini, pearsons_correlation_coefficient, r_xy**2, a, r_xy_2**2, a_2)

                # Store to result dic.
                res_dic[method_cur][str(glob_ini)]['pearsons_correlation_coefficient'] = pearsons_correlation_coefficient
                res_dic[method_cur]['pearsons_correlation_coefficient'].append(pearsons_correlation_coefficient)
                res_dic[method_cur][str(glob_ini)]['two_tailed_p_value'] = two_tailed_p_value
                res_dic[method_cur]['two_tailed_p_value'].append(two_tailed_p_value)
                res_dic[method_cur][str(glob_ini)]['r_xy'] = r_xy
                res_dic[method_cur]['r_xy'].append(r_xy)
                res_dic[method_cur][str(glob_ini)]['a'] = a
                res_dic[method_cur]['a'].append(a)

                res_dic[method_cur][str(glob_ini)]['r_xy_2'] = r_xy_2
                res_dic[method_cur]['r_xy_2'].append(r_xy_2)
                res_dic[method_cur][str(glob_ini)]['a_2'] = a_2
                res_dic[method_cur]['a_2'].append(a_2)

                res_dic[method_cur][str(glob_ini)]['r_xy_int'] = r_xy_int
                res_dic[method_cur]['r_xy_int'].append(r_xy_int)
                res_dic[method_cur][str(glob_ini)]['a_int'] = a_int
                res_dic[method_cur]['a_int'].append(a_int)
                res_dic[method_cur][str(glob_ini)]['b_int'] = b_int
                res_dic[method_cur]['b_int'].append(b_int)

            res_dic[method_cur]['sampling_sparseness'] = asarray(res_dic[method_cur]['sampling_sparseness'])
            res_dic[method_cur]['glob_ini'] = asarray(res_dic[method_cur]['glob_ini'])
            res_dic[method_cur]['r2eff_norm_std'] = asarray(res_dic[method_cur]['r2eff_norm_std'])

            res_dic[method_cur]['pearsons_correlation_coefficient'] = asarray(res_dic[method_cur]['pearsons_correlation_coefficient'])
            res_dic[method_cur]['two_tailed_p_value'] = asarray(res_dic[method_cur]['two_tailed_p_value'])
            res_dic[method_cur]['r_xy'] = asarray(res_dic[method_cur]['r_xy'])
            res_dic[method_cur]['a'] = asarray(res_dic[method_cur]['a'])
            res_dic[method_cur]['r_xy_2'] = asarray(res_dic[method_cur]['r_xy_2'])
            res_dic[method_cur]['a_2'] = asarray(res_dic[method_cur]['a_2'])
            res_dic[method_cur]['r_xy_int'] = asarray(res_dic[method_cur]['r_xy_int'])
            res_dic[method_cur]['a_int'] = asarray(res_dic[method_cur]['a_int'])
            res_dic[method_cur]['b_int'] = asarray(res_dic[method_cur]['b_int'])

        return res_dic


    def plot_r2eff_stat(self, r2eff_stat_dic=None, methods=[], list_glob_ini=[], show=False, write_stats=False):

        # Define figure
        fig, axises = plt.subplots(nrows=2, ncols=1)
        fig.suptitle('Stats per NI')
        ax1, ax2 = axises

        # Catch min and max values for all methods.
        min_a = 1.0
        max_a = 0.0

        min_r_xy2 = 1.0
        max_r_xy2 = 0.0

        # Prepare header for writing.
        selection = r2eff_stat_dic['selection']

        # For writing out stats.
        headings = []
        data_dic = {}
        data_dic_methods = []
        i_max = 0

        for method in methods:
            if method not in r2eff_stat_dic:
                continue

            # Use NI as x.
            NI = r2eff_stat_dic[method]['glob_ini']
            # Use sampling_sparseness as x.
            SS = r2eff_stat_dic[method]['sampling_sparseness']

            # Add to headings.
            headings = headings + ['method', 'SS', 'NI', 'slope_r2eff', 'rxy2_r2eff', 'slope_r2eff_vs_err', 'rxy2_r2eff_vs_err']

            # Get stats.
            # Linear regression slope, without intercept
            a = r2eff_stat_dic[method]['a']

            if max(a) > max_a:
                max_a = max(a)
            if min(a) < min_a:
                min_a = min(a)

            # sample correlation coefficient, without intercept
            r_xy = r2eff_stat_dic[method]['r_xy']
            r_xy2 = r_xy**2

            if max(r_xy2) > max_r_xy2:
                max_r_xy2 = max(r_xy2)
            if min(r_xy2) < min_r_xy2:
                min_r_xy2 = min(r_xy2)

            # For just the R2eff values
            a_r2eff = r2eff_stat_dic[method]['a_2']
            r_xy_r2eff = r2eff_stat_dic[method]['r_xy_2']
            r_xy_r2eff2 = r_xy_r2eff**2

            # Add to data.
            data_dic[method] = {}
            data_dic_methods.append(method)
            for i, NI_i in enumerate(NI):
                SS_i = SS[i]
                a_i = a[i]
                r_xy2_i = r_xy2[i]
                a_r2eff_i = a_r2eff[i]
                r_xy_r2eff2_i = r_xy_r2eff2[i]
                data_dic[method][str(i)] = ["%3.5f"%SS_i, "%i"%NI_i, "%3.5f"%a_r2eff_i, "%3.5f"%r_xy_r2eff2_i, "%3.5f"%a_i, "%3.5f"%r_xy2_i]
                if i > i_max:
                    i_max = i

            #ax1.plot(NI, a, ".-", label='%s LR'%method)
            #ax2.plot(NI, r_xy2, "o--", label='%s SC'%method)
            t = ax1.plot(SS, a_r2eff, ".--", label='%s slope R2eff'%method)
            color = t[0].get_color()
            ax1.plot(SS, a, ".-", label='%s slope'%method, color=color)

            t = ax2.plot(SS, r_xy_r2eff2, "o--", label='%s r2 R2eff'%method)
            color = t[0].get_color()
            ax2.plot(SS, r_xy2, "o-", label='%s r2'%method, color=color)

        # Loop over methods for writing data.
        data = []

        for i in range(0, i_max+1):
            data_i = []
            for method in data_dic_methods:
                data_dic_m = data_dic[method]
                # Loop over all possible data points.
                if str(i) in data_dic_m:
                    data_i = data_i + [method] + data_dic_m[str(i)]
                else:
                    data_i = data_i + [method] + ["0", "0", "0", "0", "0", "0"]

            data.append(data_i)

        # Set legends.
        ax1.legend(loc='lower left', shadow=True, prop = fontP)
        #ax1.set_xlabel('NI')
        ax1.set_xlabel('SS')
        #ax1.set_ylabel(r'$\sigma ( R_{2,\mathrm{eff}} )$')
        ax1.set_ylabel('Linear regression slope, without intercept')
        #ax1.set_xticks(NI)
        #ax1.set_xticks(SS)
        ax1.set_ylim(min_a*0.95, max_a*1.05)
        ax1.invert_xaxis()

        ax2.legend(loc='lower right', shadow=True, prop = fontP)
        ax2.set_ylabel('Sample correlation ' + r'$r_{xy}^2$')
        #ax2.set_xticks(NI)
        #ax2.set_xticks(SS)
        ax2.set_ylim(min_r_xy2*0.95, max_r_xy2*1.05)
        ax2.invert_xaxis()

        # Determine filename.
        if selection == None:
            file_name_ini = 'r2eff_stat_all'
        else:
            file_name_ini = 'r2eff_stat_sel'

        # Write png.
        png_file_name = file_name_ini + '.png'
        png_file_path = get_file_path(file_name=png_file_name, dir=self.results_dir)

        # Write to file.
        if write_stats:
            # save figure
            plt.savefig(png_file_path, bbox_inches='tight')

            file_name = file_name_ini + '.txt'
            path = self.results_dir
            file_obj, file_path = open_write_file(file_name=file_name, dir=path, force=True, compress_type=0, verbosity=1, return_path=True)

            # Write data.
            write_data(out=file_obj, headings=headings, data=data)

            # Close file.
            file_obj.close()

        # Plot data.
        if show:
            plt.show()


    def col_min(self, method=None, model=None, analysis=None, list_glob_ini=None, selection=None):

        # Loop over the glob ini:
        res_dic = {}
        res_dic['method'] = method
        res_dic['selection'] = selection
        res_dic['analysis'] = analysis

        for glob_ini in list_glob_ini:
            # Check previous, and get the pipe name.
            found, pipe_name, resfile, path = self.check_previous_result(method=method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=method)

            if pipes.cdp_name() != pipe_name:
                self.interpreter.pipe.switch(pipe_name)

            # Results dictionary.
            res_dic[str(glob_ini)] = {}
            res_dic[str(glob_ini)]['params'] = {}

            # Detect which params are in use.
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(selection=selection, full_info=True, return_id=True, skip_desel=True):
                params_list = cur_spin.params

                # Store to dic.
                res_dic[str(glob_ini)]['params']['params_list'] = params_list

                # Store individual.
                for param in params_list:
                    # Store in list.
                    res_dic[str(glob_ini)]['params'][param] = []
                    res_dic[str(glob_ini)]['params'][param+'_resi'] = []

                    # Prepare to store individual per spin.
                    res_dic[str(glob_ini)][param] = {}

                # Break after first round.
                break

            # Loop over the spins.
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(selection=selection, full_info=True, return_id=True, skip_desel=True):
                # Loop over params
                for param in params_list:

                    # Make spin dic.
                    res_dic[str(glob_ini)][param][spin_id] = {}

                    # If param in PARAMS_R20, values are stored in with parameter key.
                    param_key_list = []
                    if param in PARAMS_R20:
                        # Loop over frq key.
                        for exp_type, frq, offset, ei, mi, oi, in loop_exp_frq_offset(return_indices=True):
                            # Get the parameter key.
                            param_key = generate_r20_key(exp_type=exp_type, frq=frq)
                            param_key_list.append(param_key)
                            res_dic[str(glob_ini)][param][spin_id]['param_key_list'] = param_key_list

                            # Get the Value.
                            param_val = deepcopy(getattr(cur_spin, param)[param_key])
                            # Store in list and per spin.
                            res_dic[str(glob_ini)]['params'][param].append(param_val)
                            res_dic[str(glob_ini)][param][spin_id][param_key] = param_val

                            res_dic[str(glob_ini)]['params'][param+'_resi'].append("%i_%3.0f"%(resi, frq/1E6))

                    else:
                        # Get the value.
                        param_val = deepcopy(getattr(cur_spin, param))
                        # Store in list and per spin.
                        res_dic[str(glob_ini)]['params'][param].append(param_val)
                        res_dic[str(glob_ini)][param][spin_id][param_key] = param_val

                        res_dic[str(glob_ini)]['params'][param+'_resi'].append("%i"%(resi))

            # Print
            subtitle(file=sys.stdout, text="The minimised valus for '%s' model for pipe='%s at %s'" % (model, pipe_name, glob_ini), prespace=3)

            # Convert to numpy array.
            for param in params_list:
                res_dic[str(glob_ini)]['params'][param] = asarray(res_dic[str(glob_ini)]['params'][param])
                param_vals_str = " ".join(format(x, "2.3f") for x in res_dic[str(glob_ini)]['params'][param])
                print(param, param_vals_str)

        return res_dic


    def plot_min_corr(self, corr_data, show=False, write_stats=False):
        # Define figure.
        # Nr of columns is number of datasets.
        nr_cols = len(corr_data)
        # Nr of rows, is the number of parameters.
        data_xy_0, methods_0, glob_inis_0 = corr_data[0]
        glob_ini_0 = glob_inis_0[0]
        params_list = data_xy_0[0][str(glob_ini_0)]['params']['params_list']
        nr_rows = len(params_list)
        analysis = data_xy_0[0]['analysis']

        # Define figure
        fig, axises = plt.subplots(nrows=nr_rows, ncols=nr_cols)
        fig.suptitle('Correlation plot')

        # axises is a tuple with number of elements corresponding to number of rows.
        # Each sub-tuple contains axis for each column.

        # For writing out stats.
        data_dic = {}

        # Loop over the rows.
        for i, row_axises in enumerate(axises):
            param = params_list[i]

            # Loop over the columns.
            for j, ax in enumerate(row_axises):
                # Extract from lists.
                data, methods, glob_inis = corr_data[j]
                data_x, data_y = data
                method_x, method_y = methods
                glob_ini_x, glob_ini_y = glob_inis

                x = data_x[str(glob_ini_x)]['params'][param]
                y = data_y[str(glob_ini_y)]['params'][param]
                # Relative uncertainty / fractional uncertainty / precision
                precision = abs(y-x) / ((x+y)/2)
                # Count outliers. Value differ more than than the value itself. 
                precision_outlier = precision > 1.00
                #precision_outlier = precision > 0.020
                precision_outlier_nr = sum(precision_outlier)
                resis = data_x[str(glob_ini_x)]['params'][param+'_resi']
                resi_outlier_arr = asarray(resis)[precision_outlier]
                resi_outlier_arr_str = ":"+','.join(str(e) for e in resi_outlier_arr)

                np = len(y)

                # Linear a, with no intercept.
                a = sum(x * y) / sum(x**2)
                min_xy = min(concatenate((x, y)))
                max_xy = max(concatenate((x, y)))

                dx = (max_xy - min_xy) / np
                x_arange = arange(min_xy, max_xy + dx, dx)
                y_arange = a * x_arange

                ax.plot(x, x, 'o', label='%s vs. %s' % (method_x, method_x))
                ax.plot(x, y, '.', label='%s vs. %s' % (method_y, method_x) )

                #x_label = '%s'%param
                y_label = '%s'%param

                #ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)

                ax.set_title('For %s %i vs. %s %i. np=%i' % (method_y, glob_ini_y, method_x, glob_ini_x, np), fontsize=10)
                ax.legend(loc='upper left', shadow=True, prop=fontP)

                # kex has values in 1000 area.
                if param == 'kex':
                    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
                    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

                ## If r2 or dw parameter, do a straight line:
                #if param in PARAMS_R20 + ['dw']:

                #    ax.plot(x_arange, x_arange, 'b--')
                #    ax.plot(x_arange, y_arange, 'g--')

                # Do a straight line for all.
                ax.plot(x_arange, x_arange, 'b--')
                ax.plot(x_arange, y_arange, 'g--')

                # Store to data dic
                method_xy_NI = "%s_%s_%s%s_%s%s" % (analysis, param, method_x, glob_ini_x, method_y, glob_ini_y)
                data_dic[method_xy_NI] = []

                # Add to data.
                for k, x_k in enumerate(x):
                    y_k = y[k]
                    x_arange_k = x_arange[k]
                    y_arange_k = y_arange[k]
                    precision_k = precision[k]
                    resi_k = resis[k]

                    data_dic[method_xy_NI].append(["%3.5f"%x_k, "%3.5f"%y_k, "%3.5f"%x_arange_k, "%3.5f"%y_arange_k, "%3.5f"%precision_k, "%s"%resi_k, "%i"%precision_outlier_nr, "%s"%resi_outlier_arr_str])

        plt.tight_layout()

        # Loop over columns for writing data.
        # Write to file.
        if write_stats:
            # Re-order the data.
            headings_all = []
            method_xy_NI_all = []
            # Loop over the columns.
            for j in range(nr_cols):
                headings_j = []
                method_xy_NI_j = []
                # Loop over rows
                for i in range(nr_rows):
                    # Extract from lists.
                    data, methods, glob_inis = corr_data[j]
                    method_x, method_y = methods
                    glob_ini_x, glob_ini_y = glob_inis
                    param = params_list[i]

                    # Add to headings
                    method_x_NI = "%s_%s_%s%s" % (analysis, param, method_x, glob_ini_x)
                    method_y_NI = "%s_%s_%s%s" % (analysis, param, method_y, glob_ini_y)
                    method_x_NI_lin = "%s_%s_lin_%s%s" % (analysis, param, method_x, glob_ini_x)
                    method_y_NI_lin = "%s_%s_lin_%s%s" % (analysis, param, method_y, glob_ini_y)
                    headings_j = headings_j + [method_x_NI, method_y_NI, method_x_NI_lin, method_y_NI_lin, "abs_diff_frac", "resi", "outlier_nr", "outlier_resi"]

                    method_xy_NI = "%s_%s_%s%s_%s%s" % (analysis, param, method_x, glob_ini_x, method_y, glob_ini_y)
                    method_xy_NI_j.append(method_xy_NI)

                headings_all.append(headings_j)
                method_xy_NI_all.append(method_xy_NI_j)

            # Loop over the columns.
            for j, headings_j in enumerate(headings_all):
                method_xy_NI_j = method_xy_NI_all[j]

                data_w = []
                method_xy_NI_r2 = method_xy_NI_j[0]
                data_r2 = data_dic[method_xy_NI_r2]

                # Loop over the rows of data.
                for k, data_r2_k in enumerate(data_r2):
                    data_row = data_r2_k
                    # Loop over the columns.
                    for method_xy_NI in method_xy_NI_j[1:]:
                        data_param = data_dic[method_xy_NI]

                        try:
                            data_param_row = data_param[k]
                        except IndexError:
                            data_param_row = len(data_param[0]) * ['0.0']
                            data_param_row[-1] = ':'

                        data_row = data_row + data_param_row

                    data_w.append(data_row)

                # Define file name.
                data, methods, glob_inis = corr_data[j]
                data_x, data_y = data
                method_x, method_y = methods
                glob_ini_x, glob_ini_y = glob_inis

                # Get the spin selection for correlation.
                selection = data_x['selection']

                file_name_ini = '%s_%s_%s_%s_%s' % (analysis, method_x, glob_ini_x, method_y, glob_ini_y)
                if selection == None:
                    file_name_ini = file_name_ini + '_all'
                else:
                    file_name_ini = file_name_ini + '_sel'

                file_name = file_name_ini + '.txt'
                path = self.results_dir

                # save figure
                # Write png.
                png_file_name = file_name_ini + '.png'
                png_file_path = get_file_path(file_name=png_file_name, dir=path)
                plt.savefig(png_file_path, bbox_inches='tight')

                # Write file
                file_obj, file_path = open_write_file(file_name=file_name, dir=path, force=True, compress_type=0, verbosity=1, return_path=True)

                # Write data.
                write_data(out=file_obj, headings=headings_j, data=data_w)

                # Close file.
                file_obj.close()

        if show:
            plt.show()


    def get_min_stat_dic(self, list_r2eff_dics=None, list_glob_ini=None):

        # Loop over the result dictionaries:
        res_dic = {}
        for i, min_dic in enumerate(list_r2eff_dics):
            # Let the reference dic be initial dic
            min_dic_ref = list_r2eff_dics[0]
            method_ref = min_dic_ref['method']
            res_dic['method_ref'] = method_ref
            glob_ini_ref = list_glob_ini[0]
            res_dic['glob_ini_ref'] = str(glob_ini_ref)
            selection = min_dic_ref['selection']
            res_dic['selection'] = selection
            params_list = min_dic_ref[str(glob_ini_ref)]['params']['params_list']
            res_dic['params_list'] = params_list
            analysis = min_dic_ref['analysis']
            res_dic['analysis'] = analysis

            # Get the current method
            method_cur = min_dic['method']
            res_dic[method_cur] = {}

            # Loop over params
            for j, param in enumerate(params_list):
                res_dic[param] = {}

                # Let the reference param array be the initial glob.
                param_arr_ref = min_dic_ref[str(glob_ini_ref)]['params'][param]
                res_dic[param]['param_arr_ref'] = param_arr_ref

                res_dic[method_cur][param] = {}
                res_dic[method_cur][param]['method'] = method_cur
                res_dic[method_cur][param]['sampling_sparseness'] = []
                res_dic[method_cur][param]['glob_ini'] = []

                # Other stats.
                res_dic[method_cur][param]['r_xy'] = []
                res_dic[method_cur][param]['a'] = []
                res_dic[method_cur][param]['precision_outlier_nr'] = []
                res_dic[method_cur][param]['resi_outlier'] = []

                # Now loop over glob_ini:
                for glob_ini in list_glob_ini:
                    # Get the array, if it exists.
                    if str(glob_ini) not in min_dic:
                        continue

                    # Get the data.
                    param_arr = min_dic[str(glob_ini)]['params'][param]
                    resis = min_dic[str(glob_ini)]['params'][param+'_resi']

                    # This require that all number of points are equal.
                    # If they are not of same length, then dont even bother to continue.
                    if len(param_arr) != len(param_arr_ref):
                        continue

                    # Store x
                    sampling_sparseness = float(glob_ini) / float(glob_ini_ref) * 100.
                    res_dic[method_cur][param]['sampling_sparseness'].append(sampling_sparseness)
                    res_dic[method_cur][param]['glob_ini'].append(glob_ini)

                    # Store to result dic.
                    res_dic[method_cur][param][str(glob_ini)] = {}
                    res_dic[method_cur][param][str(glob_ini)]['sampling_sparseness'] = sampling_sparseness
                    res_dic[method_cur][param][str(glob_ini)]['param_arr'] = param_arr

                    # With intercept at axis.
                    # Calculate sample correlation coefficient, measure of goodness-of-fit of linear regression
                    x = param_arr_ref
                    x_m = mean(x)
                    y = param_arr
                    y_m = mean(y)

                    # Without intercept.
                    a = sum(x*y) / sum(x**2)
                    r_xy = sum(x*y) / sqrt(sum(x**2) * sum(y**2))

                    # Relative uncertainty / fractional uncertainty / precision
                    precision = abs(y-x) / ((x+y)/2)
                    # Count outliers. Value differ more than than the value itself. 
                    precision_outlier = precision > 1.00
                    #precision_outlier = precision > 0.02
                    precision_outlier_nr = sum(precision_outlier)

                    resi_outlier_arr = asarray(resis)[precision_outlier]
                    resi_outlier_arr_str = ":"+','.join(str(e) for e in resi_outlier_arr)

                    print(param, method_ref, method_cur, sampling_sparseness, glob_ini, r_xy**2, a, precision_outlier_nr, resi_outlier_arr_str)

                    # Store to result dic.
                    res_dic[method_cur][param][str(glob_ini)]['r_xy'] = r_xy
                    res_dic[method_cur][param]['r_xy'].append(r_xy)
                    res_dic[method_cur][param][str(glob_ini)]['a'] = a
                    res_dic[method_cur][param]['a'].append(a)
                    res_dic[method_cur][param][str(glob_ini)]['precision_outlier_nr'] = precision_outlier_nr
                    res_dic[method_cur][param]['precision_outlier_nr'].append(precision_outlier_nr)
                    res_dic[method_cur][param]['resi_outlier'].append(resi_outlier_arr_str)

                res_dic[method_cur][param]['sampling_sparseness'] = asarray(res_dic[method_cur][param]['sampling_sparseness'])
                res_dic[method_cur][param]['glob_ini'] = asarray(res_dic[method_cur][param]['glob_ini'])

                res_dic[method_cur][param]['r_xy'] = asarray(res_dic[method_cur][param]['r_xy'])
                res_dic[method_cur][param]['a'] = asarray(res_dic[method_cur][param]['a'])
                res_dic[method_cur][param]['precision_outlier_nr'] = asarray(res_dic[method_cur][param]['precision_outlier_nr'])
                res_dic[method_cur][param]['resi_outlier'] = asarray(res_dic[method_cur][param]['resi_outlier'])

        return res_dic


    def plot_min_stat(self, min_stat_dic=None, methods=[], list_glob_ini=[], show=False, write_stats=False):

        # Catch min and max values for all methods.
        min_a = 1.0
        max_a = 0.0

        min_r_xy2 = 1.0
        max_r_xy2 = 0.0

        # Prepare header for writing.
        selection = min_stat_dic['selection']
        params_list = min_stat_dic['params_list']
        analysis = min_stat_dic['analysis']

        # For writing out stats.
        headings = []
        data_dic = {}
        data_dic_methods = []

        i_max = 0

        for method in methods:
            if method not in min_stat_dic:
                continue

            # Define figure
            fig, axises = plt.subplots(nrows=len(params_list), ncols=1)
            fig.suptitle('Stats per NI %s' % method)

            # Loop over params
            data_dic[method] = {}
            data_dic_methods.append(method)

            for j, param in enumerate(params_list):
                data_dic[method][param] = {}

                # Use NI as x.
                NI = min_stat_dic[method][param]['glob_ini']

                # Use sampling_sparseness as x.
                SS = min_stat_dic[method][param]['sampling_sparseness']

                # Add to headings.
                headings = headings + ['method_%s'%param, 'SS', 'NI', 'slope', 'rxy2', 'outlier_nr', 'resi_outlier']

                # Get stats.
                # Linear regression slope, without intercept
                a = min_stat_dic[method][param]['a']

                if max(a) > max_a:
                    max_a = max(a)
                if min(a) < min_a:
                    min_a = min(a)

                # sample correlation coefficient, without intercept
                r_xy = min_stat_dic[method][param]['r_xy']
                r_xy2 = r_xy**2

                if max(r_xy2) > max_r_xy2:
                    max_r_xy2 = max(r_xy2)
                if min(r_xy2) < min_r_xy2:
                    min_r_xy2 = min(r_xy2)

                # Get the precision_outlier_nr, where values change more than the value itself.
                precision_outlier_nr = min_stat_dic[method][param]['precision_outlier_nr']
                resi_outlier = min_stat_dic[method][param]['resi_outlier']

                # Add to data.
                for i, NI_i in enumerate(NI):
                    SS_i = SS[i]
                    a_i = a[i]
                    r_xy2_i = r_xy2[i]
                    precision_outlier_nr_i = precision_outlier_nr[i]
                    resi_outlier_i = resi_outlier[i]
                    data_dic[method][param][str(i)] = ["%3.5f"%SS_i, "%i"%NI_i, "%3.5f"%a_i, "%3.5f"%r_xy2_i, "%i"%precision_outlier_nr_i, "%s"%resi_outlier_i]
                    if i > i_max:
                        i_max = i

                ax = axises[j]
                ax.plot(SS, a, ".-", label='%s_%s_a' % (method, param) )
                ax.plot(SS, r_xy2, "o--", label='%s_%s_r_xy2' % (method, param) )
                ax.legend(loc='lower left', shadow=True, prop = fontP)
                ax.set_xlabel('SS')
                ax.invert_xaxis()
                #ax.set_ylim(min_a*0.95, max_a*1.05)


        # Loop over methods for writing data.
        data = []

        # Loop over all lines.
        for i in range(0, i_max+1):
            data_i = []
            for method in data_dic_methods:
                data_dic_m = data_dic[method]
                # Loop over all params
                for j, param in enumerate(params_list):
                    # Loop over all possible data points.
                    if str(i) in data_dic_m[param]:
                        data_i = data_i + ["%s_%s" % (method, param)] + data_dic_m[param][str(i)]
                    else:
                        data_i = data_i + ["%s_%s" % (method, param)] + ["0", "0", "0", "0", "0", ":"]

            data.append(data_i)

        # Determine filename.
        if selection == None:
            file_name_ini = '%s_stat_all' % analysis
        else:
            file_name_ini = '%s_stat_sel' % analysis

        # Write png.
        png_file_name = file_name_ini + '.png'
        png_file_path = get_file_path(file_name=png_file_name, dir=self.results_dir)

        # Write to file.
        if write_stats:
            # save figure
            plt.savefig(png_file_path, bbox_inches='tight')

            file_name = file_name_ini + '.txt'
            path = self.results_dir
            file_obj, file_path = open_write_file(file_name=file_name, dir=path, force=True, compress_type=0, verbosity=1, return_path=True)

            # Write data.
            write_data(out=file_obj, headings=headings, data=data)

            # Close file.
            file_obj.close()

        # Plot data.
        if show:
            plt.show()


    def interpreter_start(self):
        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)


    def set_self(self, key, value):
        """Store to self and settings dictionary"""

        # Store to dic.
        self.settings[key] = value

        # Store to self.
        setattr(self, key, value)


    def lock_start(self):
        # Execution lock.
        status.exec_lock.acquire(self.pipe_bundle, mode='auto-analysis')


    def lock_stop(self):
        # Execution lock.
        status.exec_lock.release()


    def status_start(self):
        # Set up the analysis status object.
        status.init_auto_analysis(self.pipe_bundle, type='relax_disp')
        status.current_analysis = self.pipe_bundle


    def status_stop(self):
        # Change status.
        status.auto_analysis[self.pipe_bundle].fin = True
        status.current_analysis = None


