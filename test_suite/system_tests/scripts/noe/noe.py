###############################################################################
#                                                                             #
# Copyright (C) 2008,2014 Edward d'Auvergne                                   #
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
"""Script for calculating NOEs."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Create the NOE data pipe.
pipe.create('NOE', 'noe')

# Load the sequence.
sequence.read(file='Ap4Aase.seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Add the Trp 40 indole spin.
spin.create(res_num=40, spin_name='NE1')

# Load the reference spectrum and saturated spectrum peak intensities.
spectrum.read_intensities(file='ref_ave.list', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='ref_ave')
spectrum.read_intensities(file='sat_ave.list', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='sat_ave')

# Set the spectrum types.
noe.spectrum_type('ref', 'ref_ave')
noe.spectrum_type('sat', 'sat_ave')

# Set the errors.
spectrum.baseplane_rmsd(error=3600, spectrum_id='ref_ave')
spectrum.baseplane_rmsd(error=3000, spectrum_id='sat_ave')

# Individual residue errors.
spectrum.baseplane_rmsd(error=122000, spectrum_id='ref_ave', spin_id=":5")
spectrum.baseplane_rmsd(error=8500, spectrum_id='sat_ave', spin_id=":5")

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved residues.
deselect.read(file='unresolved', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting', res_num_col=1)

# Calculate the NOEs.
minimise.calculate()

# Save the NOEs.
value.write(param='noe', file='devnull', force=True)

# Create grace files.
grace.write(y_data_type='peak_intensity', file='intensities.agr', dir=ds.tmpdir, force=True)
grace.write(y_data_type='noe', file='noe.agr', dir=ds.tmpdir, force=True)

# Write the results.
results.write(file='devnull', dir=None, force=True)

# Save the program state.
state.save('devnull', force=True)
