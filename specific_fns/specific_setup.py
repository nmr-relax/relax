###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


    def setup(self, function_type, eqi, raise_error=1):
        """Setup function."""

        # Initialise.
        self.function_type = function_type
        function = None

        # Sequence data.
        if eqi == 'seq':
            function = self.seq_funcs()

        # Diffusion tensor.
        elif eqi == 'diff':
            function = self.diff_funcs()

        # Relaxation curve fitting.
        elif eqi == 'relax_fit':
            function = self.relax_funcs()

        # Reduced spectral density mapping.
        elif eqi == 'jw':
            function = self.jw_funcs()

        # Model-free analysis.
        elif eqi == 'mf':
            function = self.mf_funcs()

        # Raise an error if the function doesn't exist.
        if raise_error:
            if function == None:
                raise RelaxFuncSetupError, (eqi, function_type)

        # Return the function.
        return function


    def diff_funcs(self):
        """Diffusion tensor specific functions."""


    def jw_funcs(self):
        """Model-free analysis specific functions."""

        # Calculate function.
        if self.function_type == 'calculate':
            return self.relax.specific.jw_mapping.calculate

        # Value and error returning function.
        if self.function_type == 'return_value':
            return self.relax.specific.jw_mapping.return_value

        # Set function.
        if self.function_type == 'set':
            return self.relax.specific.jw_mapping.set


    def mf_funcs(self):
        """Model-free analysis specific functions."""

        # Back-calculate function.
        if self.function_type == 'back_calc':
            return self.relax.specific.model_free.back_calc

        # Calculate function.
        if self.function_type == 'calculate':
            return self.relax.specific.model_free.calculate

        # Create Monte Carlo data function.
        if self.function_type == 'create_mc_data':
            return self.relax.specific.model_free.create_mc_data

        # Duplicate data function.
        if self.function_type == 'duplicate_data':
            return self.relax.specific.model_free.duplicate_data

        # Eliminate models.
        if self.function_type == 'eliminate':
            return self.relax.specific.model_free.eliminate

        # Grid search function.
        if self.function_type == 'grid_search':
            return self.relax.specific.model_free.grid_search

        # Initial Monte Carlo parameter value search function.
        if self.function_type == 'init_sim_values':
            return self.relax.specific.model_free.sim_init_values

        # Map labels.
        if self.function_type == 'map_labels':
            return self.relax.specific.model_free.map_labels

        # Map bounds function.
        if self.function_type == 'map_bounds':
            return self.relax.specific.model_free.map_bounds

        # Minimise function.
        if self.function_type == 'minimise':
            return self.relax.specific.model_free.minimise

        # Model statistics.
        if self.function_type == 'model_stats':
            return self.relax.specific.model_free.model_statistics

        # Number of instances.
        if self.function_type == 'num_instances':
            return self.relax.specific.model_free.num_instances

        # Pack Monte Carlo simulation data function.
        if self.function_type == 'pack_sim_data':
            return self.relax.specific.model_free.sim_pack_data

        # Parameter names function.
        if self.function_type == 'param_names':
            return self.relax.specific.model_free.get_param_names

        # Parameter values function.
        if self.function_type == 'param_values':
            return self.relax.specific.model_free.get_param_values

        # Read results file function (Columnar format).
        if self.function_type == 'read_columnar_results':
            return self.relax.specific.model_free.read_columnar_results

        # Read results file function (XML format).
        if self.function_type == 'read_xml_results':
            return self.relax.specific.model_free.read_xml_results

        # Data returning function.
        if self.function_type == 'return_data':
            return self.relax.specific.model_free.return_data

        # Data error returning function.
        if self.function_type == 'return_error':
            return self.relax.specific.model_free.return_error

        # Value and error returning function.
        if self.function_type == 'return_value':
            return self.relax.specific.model_free.return_value

        # Simulation chi-squared array returning function.
        if self.function_type == 'return_sim_chi2':
            return self.relax.specific.model_free.sim_return_chi2

        # Simulation parameter array returning function.
        if self.function_type == 'return_sim_param':
            return self.relax.specific.model_free.sim_return_param

        # Set function.
        if self.function_type == 'set':
            return self.relax.specific.model_free.set

        # Set error function.
        if self.function_type == 'set_error':
            return self.relax.specific.model_free.set_error

        # Skip function.
        if self.function_type == 'skip_function':
            return self.relax.specific.model_free.skip_function

        # Unselect function.
        if self.function_type == 'unselect':
            return self.relax.specific.model_free.unselect

        # Write results function (Columnar format).
        if self.function_type == 'write_columnar_results':
            return self.relax.specific.model_free.write_columnar_results

        # Write results function (XML format).
        if self.function_type == 'write_xml_results':
            return self.relax.specific.model_free.write_xml_results


    def relax_funcs(self):
        """Relaxation curve fitting functions."""

        # Value and error returning function.
        if self.function_type == 'return_value':
            return self.relax.specific.relax_data.return_value


    def seq_funcs(self):
        """Sequence specific functions."""
