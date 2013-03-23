###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""Module containing the OpenDX 3D space isosurface mapping class."""


# Python module imports.
from numpy import float64, zeros

# relax module imports.
from pipe_control import pipes
from pipe_control import value
from pipe_control.opendx.base_map import Base_Map


class Iso3D(Base_Map):
    """OpenDX 3D space isosurface mapping class."""

    def map_text(self, map_file):
        """Function for creating the text of a 3D map."""

        # Initialise.
        values = zeros(3, float64)
        percent = 0.0
        percent_inc = 100.0 / (self.inc + 1.0)**(self.n - 1.0)
        print("%-10s%8.3f%-1s" % ("Progress:", percent, "%"))

        # Fix the diffusion tensor.
        unfix = False
        if hasattr(cdp, 'diff_tensor') and not cdp.diff_tensor.fixed:
            cdp.diff_tensor.fixed = True
            unfix = True

        # Initial value of the first parameter.
        values[0] = self.bounds[0, 0]

        # The model identifier.

        # Loop over the first parameter.
        for i in range((self.inc + 1)):
            # Initial value of the second parameter.
            values[1] = self.bounds[1, 0]

            # Loop over the second parameter.
            for j in range((self.inc + 1)):
                # Initial value of the third parameter.
                values[2] = self.bounds[2, 0]

                # Loop over the third parameter.
                for k in range((self.inc + 1)):
                    # Set the parameter values.
                    if self.spin_id:
                        value.set(val=values, param=self.params, spin_id=self.spin_id, force=True)
                    else:
                        value.set(val=values, param=self.params, force=True)

                    # Calculate the function values.
                    if self.spin_id:
                        self.calculate(spin_id=self.spin_id, verbosity=0)
                    else:
                        self.calculate(verbosity=0)

                    # Get the minimisation statistics for the model.
                    if self.spin_id:
                        k, n, chi2 = self.model_stats(spin_id=self.spin_id)
                    else:
                        k, n, chi2 = self.model_stats(model_info=0)

                    # Set maximum value to 1e20 to stop the OpenDX server connection from breaking.
                    if chi2 > 1e20:
                        map_file.write("%30f\n" % 1e20)
                    else:
                        map_file.write("%30f\n" % chi2)

                    # Increment the value of the third parameter.
                    values[2] = values[2] + self.step_size[2]

                # Progress incrementation and printout.
                percent = percent + percent_inc
                print("%-10s%8.3f%-8s%-8g" % ("Progress:", percent, "%,  " + repr(values) + ",  f(x): ", chi2))

                # Increment the value of the second parameter.
                values[1] = values[1] + self.step_size[1]

            # Increment the value of the first parameter.
            values[0] = values[0] + self.step_size[0]

        # Unfix the diffusion tensor.
        if unfix:
            cdp.diff_tensor.fixed = False
