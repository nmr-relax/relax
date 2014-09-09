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

# Python module imports.
from copy import deepcopy
from collections import OrderedDict
from datetime import datetime
from glob import glob
from os import F_OK, access, getcwd, sep
from numpy import asarray, std
import sys
from warnings import warn

# relax module imports.
import dep_check
from lib.io import extract_data, get_file_path, sort_filenames, write_data
from lib.text.sectioning import section, subsection, subtitle, title
from lib.warnings import RelaxWarning
from pipe_control.mol_res_spin import display_spin, generate_spin_string, return_spin, spin_loop
from pipe_control import pipes
from prompt.interpreter import Interpreter
from specific_analyses.relax_disp.data import generate_r20_key, has_exponential_exp_type, is_r1_optimised, loop_exp_frq_offset, loop_exp_frq_offset_point, return_param_key_from_data, spin_loop
from specific_analyses.relax_disp.variables import MODEL_NOREX, MODEL_PARAMS, MODEL_R2EFF, PARAMS_R20
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
            self.set_self(key='insignificance', value=1.0)

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


    def set_base_cpmg(self, glob_ini=None, force=False):
        """ Setup base information, but do not load intensity. """

        # Define model
        method = 'setup'
        model = 'setup'
        analysis = 'setup'

        # Check previous, and get the pipe name.
        found, pipe_name, resfile, path = self.check_previous_result(method=method, model=model, analysis=analysis, glob_ini='setup', bundle='setup')

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
                peaks_folder = getattr(self, key)['peaks_folder']

                # Define glop pattern for peak files.
                peaks_glob_pat = '%s*%.ser' % (glob_ini, self.method)

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


    def set_intensity_and_error(self, pipe_name, glob_ini=None):
        # Read the intensity per spectrum id and set the RMSD error.

        # Switch to the pipe.
        if pipes.cdp_name() != pipe_name:
            self.interpreter.pipe.switch(pipe_name)

        # Loop over spectrometer frequencies.
        for i, sfrq in enumerate(self.sfrqs):
            # Access the key in self.
            key = DIC_KEY_FORMAT % (sfrq)

            # Get the spectrum ids.
            spectrum_ids = cdp.dic_spectrum_ids[key]

            # Get the folder for peak files.
            peaks_folder = getattr(self, key)['peaks_folder']

            # Define glop pattern for peak files.
            peaks_glob_pat = '%s*%.ser' % (glob_ini, self.method)

            # Get the file list.
            peaks_file_list = glob(peaks_folder + sep + peaks_glob_pat)

            # Sort the file list Alphanumeric.
            peaks_file_list = sort_filenames(filenames=peaks_file_list)

            # There should only be one peak file.
            for peaks_file in peaks_file_list:
                self.interpreter.spectrum.read_intensities(file=peaks_file, spectrum_id=spectrum_ids, int_method=self.int_method, int_col=range(len(spectrum_ids)))

            # Get the folder for rmsd files.
            rmsd_folder = getattr(self, key)['rmsd_folder']

            # Define glop pattern for rmsd files.
            rmsd_glob_pat = '%s*%.rmsd' % (glob_ini, self.method)

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


    def do_spectrum_error_analysis(self, pipe_name):
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


    def set_int(self, methods=None, list_glob_ini=None, force=False):
        """Call both the setup of data and the error analysis"""

        # Define model
        model = 'setup'
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
                    # Create the data pipe, by copying setup pipe.
                    self.interpreter.pipe.copy(pipe_from=self.base_setup_pipe_name, pipe_to=pipe_name, bundle_to=self.method)
                    self.interpreter.pipe.switch(pipe_name)

                    # Call set intensity.
                    self.set_intensity_and_error(pipe_name=pipe_name, glob_ini=glob_ini)

                    # Call error analysis.
                    self.do_spectrum_error_analysis(pipe_name=pipe_name)

                    # Save results, and store the current settings dic to pipe.
                    cdp.settings = self.settings
                    self.interpreter.results.write(file=resfile, dir=path, force=force)


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
                        self.set_int(methods=[method], list_glob_ini=[glob_ini])

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


    def r20_from_min_r2eff(self, spin_id=None, methods=None, model=None, model_from=None, analysis=None, analysis_from=None, list_glob_ini=None, force=False):
        """Will set the grid R20 values from the minimum R2eff values through the r20_from_min_r2eff user function.
        This will speed up the grid search with a factor GRID_INC^(Nr_spec_freq). For a CPMG experiment with two fields and standard GRID_INC=21, the speed-up is a factor 441."""

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

                if found and not force:
                    file_path = get_file_path(file_name=resfile, dir=path)
                    text = "The file '%s' already exists.  Set the force flag to True to overwrite." % (file_path)
                    warn(RelaxWarning(text))
                else:
                    self.interpreter.results.write(file=resfile, dir=path, force=force)


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
                found, pipe_name, resfile, path = self.check_previous_result(method=self.method, model=model, analysis=analysis, glob_ini=glob_ini, bundle=self.method)

                if not found:
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


        # Switch to the pipe.
        if pipes.cdp_name() != pipe_name:
            self.interpreter.pipe.switch(pipe_name)

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


    def col_r2eff(self, method=None, list_glob_ini=None):

        # Loop over the glob ini:
        res_dic = {}
        res_dic['method'] = method
        for glob_ini in list_glob_ini:
            # Store under glob_ini
            res_dic[str(glob_ini)] = {}

            # Get the pipe name for R2eff values.
            pipe_name = self.name_pipe(method=method, model=MODEL_R2EFF, analysis='int', glob_ini=glob_ini)

            # Check if pipe exists, or else calculate.
            if not pipes.has_pipe(pipe_name):
                self.calc_r2eff(methods=[method], list_glob_ini=[glob_ini])

            if pipes.get_pipe() != pipe_name:
                self.interpreter.pipe.switch(pipe_name)

            # Results dictionary.
            res_dic[str(glob_ini)] = {}
            res_dic[str(glob_ini)]['r2eff'] = {}
            res_dic[str(glob_ini)]['r2eff_err'] = {}
            spin_point_r2eff_list = []
            spin_point_r2eff_err_list = []

            # Loop over the spins.
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
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


    def get_r2eff_stat_dic(self, list_r2eff_dics=None, list_glob_ini=None):

        # Loop over the result dictionaries:
        res_dic = {}
        for i, r2eff_dic in enumerate(list_r2eff_dics):
            # Let the reference dic be initial dic
            r2eff_dic_ref = list_r2eff_dics[0]
            method_ref = r2eff_dic_ref['method']
            res_dic['method_ref'] = method_ref

            # Let the reference R2eff array be the initial glob.
            r2eff_arr_ref = r2eff_dic_ref[str(list_glob_ini[0])]['r2eff_arr']
            res_dic['r2eff_arr_ref'] = r2eff_arr_ref

            # Get the current method
            method_cur = r2eff_dic['method']
            res_dic[method_cur] = {}
            res_dic[method_cur]['method'] = method_cur
            res_dic[method_cur]['glob_ini'] = []
            res_dic[method_cur]['r2eff_norm_std'] = []

            # Now loop over glob_ini:
            for glob_ini in list_glob_ini:
                # Get the array, if it exists.
                if str(glob_ini) not in r2eff_dic:
                    continue

                r2eff_arr = r2eff_dic[str(glob_ini)]['r2eff_arr']

                # Make a normalised R2eff array according to reference.
                # This require that all number of points are equal.
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
                res_dic[method_cur]['glob_ini'].append(glob_ini)

                # Store to result dic.
                res_dic[method_cur][str(glob_ini)] = {}
                res_dic[method_cur][str(glob_ini)]['r2eff_arr'] = r2eff_arr
                res_dic[method_cur][str(glob_ini)]['r2eff_norm_arr'] = r2eff_norm_arr
                res_dic[method_cur][str(glob_ini)]['r2eff_norm_std'] = r2eff_norm_std
                res_dic[method_cur]['r2eff_norm_std'].append(r2eff_norm_std)

                res_dic[method_cur][str(glob_ini)]['r2eff_diff_norm_arr'] = r2eff_diff_norm_arr
                res_dic[method_cur][str(glob_ini)]['r2eff_diff_norm_std'] = r2eff_diff_norm_std


            res_dic[method_cur]['glob_ini'] = asarray(res_dic[method_cur]['glob_ini'])
            res_dic[method_cur]['r2eff_norm_std'] = asarray(res_dic[method_cur]['r2eff_norm_std'])


        return res_dic


    def plot_r2eff_stat(self, r2eff_stat_dic=None, methods=[], list_glob_ini=[], show=False):

        # Loop over the methods.

        # Define figure
        #fig = plt.figure(figsize=(12, 12))
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        #ax2 = ax1.twinx()

        for method in methods:
            if method not in r2eff_stat_dic:
                continue

            if not dep_check.matplotlib_module:
                continue


            x = r2eff_stat_dic[method]['glob_ini']
            y = r2eff_stat_dic[method]['r2eff_norm_std']

            ax1.plot(x, y, label='%s'%method)

        #ax1.legend(loc='upper left', shadow=True)
        ax1.legend(loc='upper left', shadow=True, prop = fontP)
        ax1.set_xlabel('NI')
        ax1.set_ylabel(r'$\sigma ( R_{2,\mathrm{eff}} )$')
        fig.gca().set_xticks(x)
        fig.gca().invert_xaxis()
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


