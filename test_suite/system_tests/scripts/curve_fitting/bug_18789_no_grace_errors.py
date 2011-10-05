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

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Script for relaxation curve fitting.
######################################


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'

# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'+sep+'bug_18789_no_grace_errors'

# Quickly create the sequence.
residue.create(13, 'ILE')
residue.create(67, 'LEU')
spin.name(name='N')

# Spectrum names.
names = [
    '500',
    '010',
    '040',
    '420',
]

# Relaxation times (in seconds).
times = [
    0.500,
    0.010,
    0.040,
    0.420,
]

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.xpk', dir=data_path, spectrum_id=names[i], int_method='height')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])
    

spectrum.baseplane_rmsd(error=26500/1e6, spectrum_id='500', spin_id=None)
spectrum.baseplane_rmsd(error=16700/1e6, spectrum_id='010', spin_id=None)   
spectrum.baseplane_rmsd(error=18200/1e6, spectrum_id='040', spin_id=None)   
spectrum.baseplane_rmsd(error=21100/1e6, spectrum_id='420', spin_id=None)   

# Peak intensity error analysis.	 
spectrum.error_analysis()

# Deselect unresolved spins.
#deselect.read(file='unresolved')

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=3)

# Minimise.
minimise('simplex', scaling=False, constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', scaling=False, constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='rx.out', dir=ds.tmpdir, force=True)

# Create Grace plots of the data.
grace.write(y_data_type='rx', file='rx.agr', dir=ds.tmpdir, force=True)    # Relaxation rate.
