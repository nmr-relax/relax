###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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

"""Script for performing a full relaxation dispersion analysis using off-resonance R1rho-type data."""


# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff', 'DPL94', 'TP02', 'NS R1rho 2-site']

# The grid search size (the number of increments per dimension).
GRID_INC = 21

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 500

# The model selection technique to use.
MODSEL = 'AIC'


# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = 'r1rho_off_res_tp02'

# Load the sequence.
sequence.read('fake_sequence.in', res_num_col=1, res_name_col=2)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Set the isotope information.
spin.isotope(isotope='15N')

# The spectral data - spectrum ID, peak list file name, spin-lock field strength (Hz), the spin-lock offset (ppm), the relaxation time (s), spectrometer frequency (Hz), and experimental error (RMSD of the base plane noise for each spectrum).
data = [
    ['ref_500MHz',       'ref_500MHz.list',     ,   None, 110.0, 0.1, 500e6, 200000.0]
    ['nu_1000.0_500MHz', 'nu_1000.0_500MHz.list', 1000.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_1500.0_500MHz', 'nu_1500.0_500MHz.list', 1500.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_2000.0_500MHz', 'nu_2000.0_500MHz.list', 2000.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_2500.0_500MHz', 'nu_2500.0_500MHz.list', 2500.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_3000.0_500MHz', 'nu_3000.0_500MHz.list', 3000.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_3500.0_500MHz', 'nu_3500.0_500MHz.list', 3500.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_4000.0_500MHz', 'nu_4000.0_500MHz.list', 4000.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_4500.0_500MHz', 'nu_4500.0_500MHz.list', 4500.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_5000.0_500MHz', 'nu_5000.0_500MHz.list', 5000.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_5500.0_500MHz', 'nu_5500.0_500MHz.list', 5500.0, 110.0, 0.1, 500e6, 200000.0]
    ['nu_6000.0_500MHz', 'nu_6000.0_500MHz.list', 6000.0, 110.0, 0.1, 500e6, 200000.0]
    ['ref_800MHz',       'ref_800MHz.list',     ,   None, 110.0, 0.1, 800e6, 200000.0]
    ['nu_1000.0_800MHz', 'nu_1000.0_800MHz.list', 1000.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_1500.0_800MHz', 'nu_1500.0_800MHz.list', 1500.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_2000.0_800MHz', 'nu_2000.0_800MHz.list', 2000.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_2500.0_800MHz', 'nu_2500.0_800MHz.list', 2500.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_3000.0_800MHz', 'nu_3000.0_800MHz.list', 3000.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_3500.0_800MHz', 'nu_3500.0_800MHz.list', 3500.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_4000.0_800MHz', 'nu_4000.0_800MHz.list', 4000.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_4500.0_800MHz', 'nu_4500.0_800MHz.list', 4500.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_5000.0_800MHz', 'nu_5000.0_800MHz.list', 5000.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_5500.0_800MHz', 'nu_5500.0_800MHz.list', 5500.0, 110.0, 0.1, 800e6, 200000.0]
    ['nu_6000.0_800MHz', 'nu_6000.0_800MHz.list', 6000.0, 110.0, 0.1, 800e6, 200000.0]
]

# Loop over the spectra.
for id, file, field, offset, relax_time, H_frq, rmsd in data:
    # Load the peak intensities and set the errors.
    spectrum.read_intensities(file=file, dir=data_path, spectrum_id=id, int_method='height')
    spectrum.baseplane_rmsd(spectrum_id=id, error=error)

    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='R1rho')

    # Set the relaxation dispersion spin-lock field strength (nu1).
    relax_disp.spin_lock_field(spectrum_id=id, field=field)

    # Set the spin-lock offset.
    relax_disp.spin_lock_offset(spectrum_id=id, offset=offset)

    # Set the relaxation times (in s).
    relax_disp.relax_time(spectrum_id=id, time=relax_time)

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=id, frq=H_frq)

# Load the R1 data.
relax_data.read(ri_id='500MHz', ri_type='R1', frq=500e6, file='R1_500MHz.out', dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
relax_data.read(ri_id='800MHz', ri_type='R1', frq=800e6, file='R1_800MHz.out', dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Clustering.
relax_disp.cluster(cluster_id='cluster', spin_id=':1-50')

# Read the chemical shift data.
chemical_shift.read(file='ref_500MHz.list', dir=data_path)

# Deselect unresolved spins.
deselect.read(file='unresolved', dir='500_MHz', res_num_col=1)
deselect.read(file='unresolved', dir='800_MHz', res_num_col=1)



# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)
