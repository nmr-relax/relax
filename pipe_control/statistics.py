###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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
"""Module for handling statistics."""

# relax module imports.
from pipe_control.pipes import check_pipe
from specific_analyses.api import return_api


def model_statistics():
    """Calculate and store the model statistics."""

    # Checks.
    check_pipe()

    # The specific analysis API object.
    api = return_api()

    # Calculate the chi2.
    print("Calculating the chi-squared value for the current parameter values.")
    api.calculate()

    # Loop over the base models.
    print("\nStoring the model statistics.")
    for model_info in api.model_loop():
        # Printout.
        api.print_model_title(model_info)

        # Get the model statistics.
        k, n, chi2 = api.model_statistics(model_info)

        # The model container.
        container = api.get_model_container(model_info)

        # Store the values.
        container.chi2 = chi2
        container.num_params = k
        container.num_data_points = n
