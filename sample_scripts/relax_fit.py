###############################################################################
#                                                                             #
# Copyright (C) 2004,2006-2008,2017 Edward d'Auvergne                         #
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

"""Script for relaxation curve fitting."""


# Python module imports.
from time import asctime, localtime

# relax module imports.
from auto_analyses.relax_fit import Relax_fit


# Create the data pipe.
pipe_bundle = "rx (%s)" % asctime(localtime())
pipe.create(pipe_name='rx', pipe_type='relax_fit', bundle=pipe_bundle)

# Load the backbone amide and tryptophan indole 15N spins from a PDB file.
structure.read_pdb('Ap4Aase_new_3.pdb')
structure.load_spins(spin_id='@N')
structure.load_spins(spin_id='@NE1')

# Spectrum names.
names = [
    'T2_ncyc1_ave',
    'T2_ncyc1b_ave',
    'T2_ncyc2_ave',
    'T2_ncyc4_ave',
    'T2_ncyc4b_ave',
    'T2_ncyc6_ave',
    'T2_ncyc9_ave',
    'T2_ncyc9b_ave',
    'T2_ncyc11_ave',
    'T2_ncyc11b_ave'
]

# Relaxation times (in seconds).
times = [
    0.0176,
    0.0176,
    0.0352,
    0.0704,
    0.0704,
    0.1056,
    0.1584,
    0.1584,
    0.1936,
    0.1936
]

# Loop over the spectra.
for i in range(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.list', spectrum_id=names[i], int_method='height')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Specify the duplicated spectra.
spectrum.replicated(spectrum_ids=['T2_ncyc1_ave', 'T2_ncyc1b_ave'])
spectrum.replicated(spectrum_ids=['T2_ncyc4_ave', 'T2_ncyc4b_ave'])
spectrum.replicated(spectrum_ids=['T2_ncyc9_ave', 'T2_ncyc9b_ave'])
spectrum.replicated(spectrum_ids=['T2_ncyc11_ave', 'T2_ncyc11b_ave'])

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
deselect.read(file='unresolved', res_num_col=1)

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Execute the auto-analysis.
Relax_fit(pipe_name='rx', pipe_bundle=pipe_bundle, file_root='rx', results_dir='.', grid_inc=11, mc_sim_num=50, view_plots=True)
