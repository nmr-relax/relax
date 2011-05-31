###############################################################################
#                                                                             #
# Copyright (C) 2005-2008 Edward d'Auvergne                                   #
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

"""Script for creating a grace plot of 'S2' vs 'te'."""


# Create the run.
name = 'm4'
pipe.create(name, 'mf')

# Load the data.
results.read(name)

# Grace plot.
grace.write(name, x_data_type='s2', y_data_type='te', plot_data='sim', file='s2_te.agr', force=True)

# View the plot.
grace.view(file='s2_te.agr')
