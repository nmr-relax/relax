###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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

# Script for relaxation curve fitting.
######################################


# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# Load the backbone amide 15N spins from a PDB file.
structure.read_pdb('Ap4Aase_new_3.pdb')
structure.load_spins(spin_id='@N')

# Load the peak intensities.
relax_fit.read(file='T2_ncyc1.list', relax_time=0.0176)
relax_fit.read(file='T2_ncyc1b.list', relax_time=0.0176)
relax_fit.read(file='T2_ncyc2.list', relax_time=0.0352)
relax_fit.read(file='T2_ncyc4.list', relax_time=0.0704)
relax_fit.read(file='T2_ncyc4b.list', relax_time=0.0704)
relax_fit.read(file='T2_ncyc6.list', relax_time=0.1056)
relax_fit.read(file='T2_ncyc9.list', relax_time=0.1584)
relax_fit.read(file='T2_ncyc9b.list', relax_time=0.1584)
relax_fit.read(file='T2_ncyc11.list', relax_time=0.1936)
relax_fit.read(file='T2_ncyc11b.list', relax_time=0.1936)

# Calculate the peak intensity averages and the standard deviation of all spectra.
relax_fit.mean_and_error()

# Deselect unresolved residues.
deselect.read(file='unresolved')

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', scaling=False, constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=500)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', scaling=False, constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='rx.out', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='chi2.agr', force=True)    # Minimised chi-squared value.
grace.write(y_data_type='i0', file='i0.agr', force=True)    # Initial peak intensity.
grace.write(y_data_type='rx', file='rx.agr', force=True)    # Relaxation rate.
grace.write(x_data_type='relax_times', y_data_type='ave_int', file='intensities.agr', force=True)    # Average peak intensities.
grace.write(x_data_type='relax_times', y_data_type='ave_int', norm=1, file='intensities_norm.agr', force=True)    # Average peak intensities (normalised).

# Display the Grace plots.
grace.view(file='chi2.agr')
grace.view(file='i0.agr')
grace.view(file='rx.agr')
grace.view(file='intensities.agr')
grace.view(file='intensities_norm.agr')

# Save the program state.
state.save(file='rx.save', force=True)
