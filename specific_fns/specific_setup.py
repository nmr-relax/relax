###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
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


from re import match


class Specific_setup:
    def __init__(self, relax):
        """Class for equation type specific function setup."""

        self.relax = relax


    def get_string(self, function_type):
        """Function for returning a string corresponding to the function type."""

        # Initialise.
        string = "this analysis"

        # NOE calculation.
        if function_type == 'noe':
            string = "NOE calculations"

        # Relaxation curve fitting.
        if function_type == 'relax_fit':
            string = "relaxation curve fitting"

        # Reduced spectral density mapping.
        if function_type == 'jw':
            string = "reduced spectral density mapping"

        # Model-free analysis.
        if function_type == 'mf':
            string = "Model-free analysis"

        # Model-free analysis.
        if function_type == 'mf_csa':
            string = "Model-free csa analysis"

        # Hybrid models.
        if function_type == 'hybrid':
            string = "hybrid models"

        return string


    def setup(self, eqi, function_type, raise_error=1):
        """Setup function."""

        # Initialise.
        self.eqi = eqi
        function = None

        # Get the function.
        try:
            # NOE calculation.
            if function_type == 'noe':
                function = self.noe()

            # Relaxation curve fitting.
            if function_type == 'relax_fit':
                function = self.relax_fit()

            # Reduced spectral density mapping.
            if function_type == 'jw':
                function = self.jw_funcs()

            # Model-free analysis.
            if function_type == 'mf':
                function = self.mf_funcs()

            # Model-free analysis.
            if function_type == 'mf_csa':
                function = self.mf_csa_funcs()

            # Hybrid models.
            if function_type == 'hybrid':
                function = self.hybrid_funcs()

        # Catch all errors.
        except:
            function = None

        # Raise an error if the function doesn't exist.
        if raise_error and function == None:
            # Some debugging output.
            if Debug:
                print "Function type: " + `function_type`
                print "Eqi: " + `self.eqi`

            # Raise the error.
            raise RelaxFuncSetupError, self.get_string(function_type)

        # Return the function.
        return function


    def hybrid_funcs(self):
        """Hybrid model specific functions."""

        # Duplicate data function.
        if self.eqi == 'duplicate_data':
            return self.relax.specific.hybrid.duplicate_data

        # Model statistics.
        if self.eqi == 'model_stats':
            return self.relax.specific.hybrid.model_statistics

        # Number of instances.
        if self.eqi == 'num_instances':
            return self.relax.specific.hybrid.num_instances

        # Skip function.
        if self.eqi == 'skip_function':
            return self.relax.specific.hybrid.skip_function


    def jw_funcs(self):
        """Reduced spectral density mapping specific functions."""

        # Calculate function.
        if self.eqi == 'calculate':
            return self.relax.specific.jw_mapping.calculate

        # Copy function.
        if self.eqi == 'copy':
            return self.relax.specific.jw_mapping.copy

        # Create Monte Carlo data function (same as data returning function).
        if self.eqi == 'create_mc_data':
            return self.relax.specific.jw_mapping.return_data

        # Number of instances.
        if self.eqi == 'num_instances':
            return self.relax.specific.jw_mapping.num_instances

        # Overfit deselect.
        if self.eqi == 'overfit_deselect':
            return self.relax.specific.jw_mapping.overfit_deselect

        # Pack Monte Carlo simulation data function.
        if self.eqi == 'pack_sim_data':
            return self.relax.specific.jw_mapping.sim_pack_data

        # Data returning function.
        if self.eqi == 'return_data':
            return self.relax.specific.jw_mapping.return_data

        # Data or parameter name returning function.
        if self.eqi == 'return_data_name':
            return self.relax.specific.jw_mapping.return_data_name

        # Factor of conversion between different parameter units returning function.
        if self.eqi == 'return_conversion_factor':
            return self.relax.specific.jw_mapping.return_conversion_factor

        # Data error returning function.
        if self.eqi == 'return_error':
            return self.relax.specific.jw_mapping.return_error

        # Grace string returning function.
        if self.eqi == 'return_grace_string':
            return self.relax.specific.jw_mapping.return_grace_string

        # Simulation parameter array returning function.
        if self.eqi == 'return_sim_param':
            return self.relax.specific.jw_mapping.sim_return_param

        # Simulation parameter array returning function.
        if self.eqi == 'return_selected_sim':
            return self.relax.specific.jw_mapping.sim_return_selected

        # String of the external parameter units returning function.
        if self.eqi == 'return_units':
            return self.relax.specific.jw_mapping.return_units

        # Value and error returning function.
        if self.eqi == 'return_value':
            return self.relax.specific.jw_mapping.return_value

        # Set function.
        if self.eqi == 'set':
            return self.relax.specific.jw_mapping.set

        # Set error function.
        if self.eqi == 'set_error':
            return self.relax.specific.jw_mapping.set_error

        # Set error function.
        if self.eqi == 'set_selected_sim':
            return self.relax.specific.jw_mapping.set_selected_sim

        # Write results function (Columnar format).
        if self.eqi == 'write_columnar_results':
            return self.relax.specific.jw_mapping.write_columnar_results


    def mf_funcs(self):
        """Model-free analysis specific functions."""

        # Back-calculate function.
        if self.eqi == 'back_calc':
            return self.relax.specific.model_free.back_calc

        # Calculate function.
        if self.eqi == 'calculate':
            return self.relax.specific.model_free.calculate

        # Copy function.
        if self.eqi == 'copy':
            return self.relax.specific.model_free.copy

        # Create Monte Carlo data function.
        if self.eqi == 'create_mc_data':
            return self.relax.specific.model_free.create_mc_data

        # Duplicate data function.
        if self.eqi == 'duplicate_data':
            return self.relax.specific.model_free.duplicate_data

        # Eliminate models.
        if self.eqi == 'eliminate':
            return self.relax.specific.model_free.eliminate

        # Grid search function.
        if self.eqi == 'grid_search':
            return self.relax.specific.model_free.grid_search

        # Initial Monte Carlo parameter value search function.
        if self.eqi == 'init_sim_values':
            return self.relax.specific.model_free.sim_init_values

        # Map bounds function.
        if self.eqi == 'map_bounds':
            return self.relax.specific.model_free.map_bounds

        # Minimise function.
        if self.eqi == 'minimise':
            return self.relax.specific.model_free.minimise

        # Model statistics.
        if self.eqi == 'model_stats':
            return self.relax.specific.model_free.model_statistics

        # Molmol macro creation.
        if self.eqi == 'molmol_macro':
            return self.relax.specific.model_free.molmol.macro

        # Number of instances.
        if self.eqi == 'num_instances':
            return self.relax.specific.model_free.num_instances

        # Overfit deselect.
        if self.eqi == 'overfit_deselect':
            return self.relax.specific.model_free.overfit_deselect

        # Pack Monte Carlo simulation data function.
        if self.eqi == 'pack_sim_data':
            return self.relax.specific.model_free.sim_pack_data

        # Parameter names function.
        if self.eqi == 'param_names':
            return self.relax.specific.model_free.get_param_names

        # Parameter values function.
        if self.eqi == 'param_values':
            return self.relax.specific.model_free.get_param_values

        # Read results file function (Columnar format).
        if self.eqi == 'read_columnar_results':
            return self.relax.specific.model_free.read_columnar_results

        # Read results file function (XML format).
        #if self.eqi == 'read_xml_results':
        #    return self.relax.specific.model_free.read_xml_results

        # Data returning function.
        if self.eqi == 'return_data':
            return self.relax.specific.model_free.return_data

        # Data or parameter name returning function.
        if self.eqi == 'return_data_name':
            return self.relax.specific.model_free.return_data_name

        # Data error returning function.
        if self.eqi == 'return_error':
            return self.relax.specific.model_free.return_error

        # Factor of conversion between different parameter units returning function.
        if self.eqi == 'return_conversion_factor':
            return self.relax.specific.model_free.return_conversion_factor

        # Grace string returning function.
        if self.eqi == 'return_grace_string':
            return self.relax.specific.model_free.return_grace_string

        # Selected simulation array returning function.
        if self.eqi == 'return_selected_sim':
            return self.relax.specific.model_free.sim_return_selected

        # Simulation chi-squared array returning function.
        if self.eqi == 'return_sim_chi2':
            return self.relax.specific.model_free.sim_return_chi2

        # Simulation parameter array returning function.
        if self.eqi == 'return_sim_param':
            return self.relax.specific.model_free.sim_return_param

        # String of the external parameter units returning function.
        if self.eqi == 'return_units':
            return self.relax.specific.model_free.return_units

        # Value and error returning function.
        if self.eqi == 'return_value':
            return self.relax.specific.model_free.return_value

        # Set function.
        if self.eqi == 'set':
            return self.relax.specific.model_free.set

        # Set error function.
        if self.eqi == 'set_error':
            return self.relax.specific.model_free.set_error

        # Set the selected simulations array.
        if self.eqi == 'set_selected_sim':
            return self.relax.specific.model_free.set_selected_sim

        # Skip function.
        if self.eqi == 'skip_function':
            return self.relax.specific.model_free.skip_function

        # Unselect function.
        if self.eqi == 'unselect':
            return self.relax.specific.model_free.unselect

        # Write results function (Columnar format).
        if self.eqi == 'write_columnar_results':
            return self.relax.specific.model_free.write_columnar_results

        # Write results function (XML format).
        #if self.eqi == 'write_xml_results':
        #    return self.relax.specific.model_free.write_xml_results


    def mf_csa_funcs(self):
        """Model-free analysis specific functions."""

        # Back-calculate function.
        if self.eqi == 'back_calc':
            return self.relax.specific.model_free_csa.back_calc

        # Calculate function.
        if self.eqi == 'calculate':
            return self.relax.specific.model_free_csa.calculate

        # Copy function.
        if self.eqi == 'copy':
            return self.relax.specific.model_free_csa.copy

        # Create Monte Carlo data function.
        if self.eqi == 'create_mc_data':
            return self.relax.specific.model_free_csa.create_mc_data

        # Duplicate data function.
        if self.eqi == 'duplicate_data':
            return self.relax.specific.model_free_csa.duplicate_data

        # Eliminate models.
        if self.eqi == 'eliminate':
            return self.relax.specific.model_free_csa.eliminate

        # Grid search function.
        if self.eqi == 'grid_search':
            return self.relax.specific.model_free_csa.grid_search

        # Initial Monte Carlo parameter value search function.
        if self.eqi == 'init_sim_values':
            return self.relax.specific.model_free_csa.sim_init_values

        # Map bounds function.
        if self.eqi == 'map_bounds':
            return self.relax.specific.model_free_csa.map_bounds

        # Minimise function.
        if self.eqi == 'minimise':
            return self.relax.specific.model_free_csa.minimise

        # Model statistics.
        if self.eqi == 'model_stats':
            return self.relax.specific.model_free_csa.model_statistics

        # Molmol macro creation.
        if self.eqi == 'molmol_macro':
            return self.relax.specific.model_free_csa.molmol.macro

        # Number of instances.
        if self.eqi == 'num_instances':
            return self.relax.specific.model_free_csa.num_instances

        # Overfit deselect.
        if self.eqi == 'overfit_deselect':
            return self.relax.specific.model_free_csa.overfit_deselect

        # Pack Monte Carlo simulation data function.
        if self.eqi == 'pack_sim_data':
            return self.relax.specific.model_free_csa.sim_pack_data

        # Parameter names function.
        if self.eqi == 'param_names':
            return self.relax.specific.model_free_csa.get_param_names

        # Parameter values function.
        if self.eqi == 'param_values':
            return self.relax.specific.model_free_csa.get_param_values

        # Read results file function (Columnar format).
        if self.eqi == 'read_columnar_results':
            return self.relax.specific.model_free_csa.read_columnar_results

        # Read results file function (XML format).
        #if self.eqi == 'read_xml_results':
        #    return self.relax.specific.model_free_csa.read_xml_results

        # Data returning function.
        if self.eqi == 'return_data':
            return self.relax.specific.model_free_csa.return_data

        # Data or parameter name returning function.
        if self.eqi == 'return_data_name':
            return self.relax.specific.model_free_csa.return_data_name

        # Data error returning function.
        if self.eqi == 'return_error':
            return self.relax.specific.model_free_csa.return_error

        # Factor of conversion between different parameter units returning function.
        if self.eqi == 'return_conversion_factor':
            return self.relax.specific.model_free_csa.return_conversion_factor

        # Grace string returning function.
        if self.eqi == 'return_grace_string':
            return self.relax.specific.model_free_csa.return_grace_string

        # Selected simulation array returning function.
        if self.eqi == 'return_selected_sim':
            return self.relax.specific.model_free_csa.sim_return_selected

        # Simulation chi-squared array returning function.
        if self.eqi == 'return_sim_chi2':
            return self.relax.specific.model_free_csa.sim_return_chi2

        # Simulation parameter array returning function.
        if self.eqi == 'return_sim_param':
            return self.relax.specific.model_free_csa.sim_return_param

        # String of the external parameter units returning function.
        if self.eqi == 'return_units':
            return self.relax.specific.model_free_csa.return_units

        # Value and error returning function.
        if self.eqi == 'return_value':
            return self.relax.specific.model_free_csa.return_value

        # Set function.
        if self.eqi == 'set':
            return self.relax.specific.model_free_csa.set

        # Set error function.
        if self.eqi == 'set_error':
            return self.relax.specific.model_free_csa.set_error

        # Set the selected simulations array.
        if self.eqi == 'set_selected_sim':
            return self.relax.specific.model_free_csa.set_selected_sim

        # Skip function.
        if self.eqi == 'skip_function':
            return self.relax.specific.model_free_csa.skip_function

        # Unselect function.
        if self.eqi == 'unselect':
            return self.relax.specific.model_free_csa.unselect

        # Write results function (Columnar format).
        if self.eqi == 'write_columnar_results':
            return self.relax.specific.model_free_csa.write_columnar_results

        # Write results function (XML format).
        #if self.eqi == 'write_xml_results':
        #    return self.relax.specific.model_free_csa.write_xml_results


    def noe(self):
        """NOE calculation functions."""

        # Calculate function.
        if self.eqi == 'calculate':
            return self.relax.specific.noe.calculate

        # Overfit deselect.
        if self.eqi == 'overfit_deselect':
            return self.relax.specific.noe.overfit_deselect

        # Read results file function (Columnar format).
        if self.eqi == 'read_columnar_results':
            return self.relax.specific.noe.read_columnar_results

        # Factor of conversion between different parameter units returning function.
        if self.eqi == 'return_conversion_factor':
            return self.relax.specific.noe.return_conversion_factor

        # Grace string returning function.
        if self.eqi == 'return_grace_string':
            return self.relax.specific.noe.return_grace_string

        # Value and error returning function.
        if self.eqi == 'return_value':
            return self.relax.specific.noe.return_value

        # String of the external parameter units returning function.
        if self.eqi == 'return_units':
            return self.relax.specific.noe.return_units

        # Write results function (Columnar format).
        if self.eqi == 'write_columnar_results':
            return self.relax.specific.noe.write_columnar_results


    def relax_fit(self):
        """Relaxation curve fitting functions."""

        # Create Monte Carlo data function.
        if self.eqi == 'create_mc_data':
            return self.relax.specific.relax_fit.create_mc_data

        # Grid search function.
        if self.eqi == 'grid_search':
            return self.relax.specific.relax_fit.grid_search

        # Initial Monte Carlo parameter value search function.
        if self.eqi == 'init_sim_values':
            return self.relax.specific.relax_fit.sim_init_values

        # Minimise function.
        if self.eqi == 'minimise':
            return self.relax.specific.relax_fit.minimise

        # Number of instances.
        if self.eqi == 'num_instances':
            return self.relax.specific.relax_fit.num_instances

        # Overfit deselect.
        if self.eqi == 'overfit_deselect':
            return self.relax.specific.relax_fit.overfit_deselect

        # Pack Monte Carlo simulation data function.
        if self.eqi == 'pack_sim_data':
            return self.relax.specific.relax_fit.sim_pack_data

        # Factor of conversion between different parameter units returning function.
        if self.eqi == 'return_conversion_factor':
            return self.relax.specific.relax_fit.return_conversion_factor

        # Data returning function.
        if self.eqi == 'return_data':
            return self.relax.specific.relax_fit.return_data

        # Data or parameter name returning function.
        if self.eqi == 'return_data_name':
            return self.relax.specific.relax_fit.return_data_name

        # Data error returning function.
        if self.eqi == 'return_error':
            return self.relax.specific.relax_fit.return_error

        # Grace string returning function.
        if self.eqi == 'return_grace_string':
            return self.relax.specific.relax_fit.return_grace_string

        # Selected simulation array returning function.
        if self.eqi == 'return_selected_sim':
            return self.relax.specific.relax_fit.sim_return_selected

        # Simulation parameter array returning function.
        if self.eqi == 'return_sim_param':
            return self.relax.specific.relax_fit.sim_return_param

        # Value and error returning function.
        if self.eqi == 'return_value':
            return self.relax.specific.relax_fit.return_value

        # String of the external parameter units returning function.
        if self.eqi == 'return_units':
            return self.relax.specific.relax_fit.return_units

        # Set function.
        if self.eqi == 'set':
            return self.relax.specific.relax_fit.set
        
        # Set error function.
        if self.eqi == 'set_error':
            return self.relax.specific.relax_fit.set_error

        # Set the selected simulations array.
        if self.eqi == 'set_selected_sim':
            return self.relax.specific.relax_fit.set_selected_sim
