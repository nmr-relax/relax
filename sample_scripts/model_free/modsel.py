###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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

"""Script for model-free model selection."""


# Set the data pipe names.
pipes = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Loop over the data pipe names.
for name in pipes:
    print(("\n\n# " + name + " #"))

    # Create the data pipe.
    pipe.create(name, 'mf')

    # Reload precalculated results from the files 'm1/results', etc.
    results.read(file='results', dir=name)

# Model elimination.
eliminate()

# Model selection.
model_selection(method='AIC', modsel_pipe='aic')

# Write the results.
state.save('save', force=True)
results.write(file='results', force=True)
