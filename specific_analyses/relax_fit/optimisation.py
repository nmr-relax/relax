###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""The R1 and R2 exponential relaxation curve fitting optimisation functions."""

# relax module imports.
from specific_analyses.relax_fit.parameters import assemble_param_vector
from target_functions.relax_fit_wrapper import Relax_fit_opt


def back_calc(spin=None, relax_time_id=None):
    """Back-calculation of peak intensity for the given relaxation time.

    @keyword spin:              The spin container.
    @type spin:                 SpinContainer instance
    @keyword relax_time_id:     The ID string for the desired relaxation time.
    @type relax_time_id:        str
    @return:                    The peak intensity for the desired relaxation time.
    @rtype:                     float
    """

    # Create the initial parameter vector.
    param_vector = assemble_param_vector(spin=spin)

    # The keys.
    keys = list(spin.peak_intensity.keys())

    # The peak intensities and times.
    values = []
    errors = []
    times = []
    for key in keys:
        values.append(spin.peak_intensity[key])
        errors.append(spin.peak_intensity_err[key])
        times.append(cdp.relax_times[key])

    # A fake scaling matrix in a diagonalised list form.
    scaling_list = []
    for i in range(len(param_vector)):
        scaling_list.append(1.0)

    # Initialise the relaxation fit functions.
    model = Relax_fit_opt(model=spin.model, num_params=len(spin.params), values=values, errors=errors, relax_times=times, scaling_matrix=scaling_list)

    # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
    model.func(param_vector)

    # Get the data back.
    results = model.back_calc_data()

    # Return the correct peak height.
    return results[keys.index(relax_time_id)]
