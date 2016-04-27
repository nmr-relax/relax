###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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

"""Script for performing a full relaxation dispersion analysis using CPMG-type data.

This uses Dr. Flemming Hansen's data from http://dx.doi.org/10.1021/jp074793o.

This is here to test the ./sample_scripts/relax_disp/cpmg_analysis.py sample script.  The differences between the two files should be minimal.
"""

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff']

# The grid search size (the number of increments per dimension).
GRID_INC = 3

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3

# A flag which if True will activate Monte Carlo simulations for all models.  Note this will hugely increase the computation time.
MC_SIM_ALL_MODELS = False

# The directory of results of an earlier analysis without clustering.
PRE_RUN_DIR = None

# The model selection technique to use.
MODSEL = 'AIC'

# The flag for only using numeric models in the final model selection.
NUMERIC_ONLY = False

# The R2eff/R1rho value in rad/s by which to judge insignificance.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.
INSIGNIFICANCE = 1.0

# Set up the data pipe.
#######################

# The results directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = None

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_24601_R2eff_missing_data'

# Load the sequence.
#molecule.create(mol_name='CKIRD', mol_type='protein')
sequence.read('fake_sequence.in', dir=data_path, res_num_col=1, res_name_col=2)
molecule.name(name='CKIRD');

# Name the spins so they can be matched to the assignments, and the isotope for field strength scaling.
spin.name(name='N')
spin.isotope(isotope='15N')

data = [
['60_111.11_0_1.in', '60/60_111.11_0_1.in', 111.11, 600.1206736, 0, 1],
['60_111.11_0.018_1.in', '60/60_111.11_0.018_1.in', 111.11, 600.1206736, 0.018, 1],
['60_111.11_0.036_1.in', '60/60_111.11_0.036_1.in', 111.11, 600.1206736, 0.036, 1],
['60_166.67_0_1.in', '60/60_166.67_0_1.in', 166.67, 600.1206736, 0, 1],
['60_166.67_0.024_1.in', '60/60_166.67_0.024_1.in', 166.67, 600.1206736, 0.024, 1],
['60_166.67_0.036_1.in', '60/60_166.67_0.036_1.in', 166.67, 600.1206736, 0.036, 1],
['60_222.22_0_1.in', '60/60_222.22_0_1.in', 222.22, 600.1206736, 0, 1],
['60_222.22_0.027_1.in', '60/60_222.22_0.027_1.in', 222.22, 600.1206736, 0.027, 1],
['60_222.22_0.036_1.in', '60/60_222.22_0.036_1.in', 222.22, 600.1206736, 0.036, 1],
['60_277.78_0_1.in', '60/60_277.78_0_1.in', 277.78, 600.1206736, 0, 1],
['60_277.78_0.0216_1.in', '60/60_277.78_0.0216_1.in', 277.78, 600.1206736, 0.0216, 1],
['60_277.78_0.036_1.in', '60/60_277.78_0.036_1.in', 277.78, 600.1206736, 0.036, 1],
['60_333.33_0_1.in', '60/60_333.33_0_1.in', 333.33, 600.1206736, 0, 1],
['60_333.33_0.024_1.in', '60/60_333.33_0.024_1.in', 333.33, 600.1206736, 0.024, 1],
['60_333.33_0.036_1.in', '60/60_333.33_0.036_1.in', 333.33, 600.1206736, 0.036, 1],
['60_388.89_0_1.in', '60/60_388.89_0_1.in', 388.89, 600.1206736, 0, 1],
['60_388.89_0.0205714_1.in', '60/60_388.89_0.0205714_1.in', 388.89, 600.1206736, 0.0205714, 1],
['60_388.89_0.036_1.in', '60/60_388.89_0.036_1.in', 388.89, 600.1206736, 0.036, 1],
['60_444.44_0_1.in', '60/60_444.44_0_1.in', 444.44, 600.1206736, 0, 1],
['60_444.44_0.0225_1.in', '60/60_444.44_0.0225_1.in', 444.44, 600.1206736, 0.0225, 1],
['60_444.44_0.036_1.in', '60/60_444.44_0.036_1.in', 444.44, 600.1206736, 0.036, 1],
['60_500_0_1.in', '60/60_500_0_1.in', 500, 600.1206736, 0, 1],
['60_500_0.024_1.in', '60/60_500_0.024_1.in', 500, 600.1206736, 0.024, 1],
['60_500_0.036_1.in', '60/60_500_0.036_1.in', 500, 600.1206736, 0.036, 1],
['60_555.56_0_1.in', '60/60_555.56_0_1.in', 555.56, 600.1206736, 0, 1],
['60_555.56_0.0216_1.in', '60/60_555.56_0.0216_1.in', 555.56, 600.1206736, 0.0216, 1],
['60_555.56_0.036_1.in', '60/60_555.56_0.036_1.in', 555.56, 600.1206736, 0.036, 1],
['60_611.11_0_1.in', '60/60_611.11_0_1.in', 611.11, 600.1206736, 0, 1],
['60_611.11_0.0229091_1.in', '60/60_611.11_0.0229091_1.in', 611.11, 600.1206736, 0.0229091, 1],
['60_611.11_0.036_1.in', '60/60_611.11_0.036_1.in', 611.11, 600.1206736, 0.036, 1],
['60_666.67_0_1.in', '60/60_666.67_0_1.in', 666.67, 600.1206736, 0, 1],
['60_666.67_0.024_1.in', '60/60_666.67_0.024_1.in', 666.67, 600.1206736, 0.024, 1],
['60_666.67_0.036_1.in', '60/60_666.67_0.036_1.in', 666.67, 600.1206736, 0.036, 1],
['60_722.22_0_1.in', '60/60_722.22_0_1.in', 722.22, 600.1206736, 0, 1],
['60_722.22_0.0249231_1.in', '60/60_722.22_0.0249231_1.in', 722.22, 600.1206736, 0.0249231, 1],
['60_722.22_0.036_1.in', '60/60_722.22_0.036_1.in', 722.22, 600.1206736, 0.036, 1],
['60_777.78_0_1.in', '60/60_777.78_0_1.in', 777.78, 600.1206736, 0, 1],
['60_777.78_0.0231429_1.in', '60/60_777.78_0.0231429_1.in', 777.78, 600.1206736, 0.0231429, 1],
['60_777.78_0.036_1.in', '60/60_777.78_0.036_1.in', 777.78, 600.1206736, 0.036, 1],
['60_833.33_0_1.in', '60/60_833.33_0_1.in', 833.33, 600.1206736, 0, 1],
['60_833.33_0.024_1.in', '60/60_833.33_0.024_1.in', 833.33, 600.1206736, 0.024, 1],
['60_833.33_0.036_1.in', '60/60_833.33_0.036_1.in', 833.33, 600.1206736, 0.036, 1],
['60_888.89_0_1.in', '60/60_888.89_0_1.in', 888.89, 600.1206736, 0, 1],
['60_888.89_0.0225_1.in', '60/60_888.89_0.0225_1.in', 888.89, 600.1206736, 0.0225, 1],
['60_888.89_0.036_1.in', '60/60_888.89_0.036_1.in', 888.89, 600.1206736, 0.036, 1],
['60_944.44_0_1.in', '60/60_944.44_0_1.in', 944.44, 600.1206736, 0, 1],
['60_944.44_0.0232941_1.in', '60/60_944.44_0.0232941_1.in', 944.44, 600.1206736, 0.0232941, 1],
['60_944.44_0.036_1.in', '60/60_944.44_0.036_1.in', 944.44, 600.1206736, 0.036, 1],
['60_1000_0_1.in', '60/60_1000_0_1.in', 1000, 600.1206736, 0, 1],
['60_1000_0.024_1.in', '60/60_1000_0.024_1.in', 1000, 600.1206736, 0.024, 1],
['60_1000_0.036_1.in', '60/60_1000_0.036_1.in', 1000, 600.1206736, 0.036, 1],
['96_222.22_0_6.in', '96/96_222.22_0_6.in', 222.22, 950.4444488, 0, 6],
['96_222.22_0.009_6.in', '96/96_222.22_0.009_6.in', 222.22, 950.4444488, 0.009, 6],
['96_222.22_0.018_6.in', '96/96_222.22_0.018_6.in', 222.22, 950.4444488, 0.018, 6],
['96_444.44_0_6.in', '96/96_444.44_0_6.in', 444.44, 950.4444488, 0, 6],
['96_444.44_0.009_6.in', '96/96_444.44_0.009_6.in', 444.44, 950.4444488, 0.009, 6],
['96_444.44_0.018_6.in', '96/96_444.44_0.018_6.in', 444.44, 950.4444488, 0.018, 6],
['96_666.67_0_6.in', '96/96_666.67_0_6.in', 666.67, 950.4444488, 0, 6],
['96_666.67_0.009_6.in', '96/96_666.67_0.009_6.in', 666.67, 950.4444488, 0.009, 6],
['96_666.67_0.018_6.in', '96/96_666.67_0.018_6.in', 666.67, 950.4444488, 0.018, 6],
['96_888.89_0_6.in', '96/96_888.89_0_6.in', 888.89, 950.4444488, 0, 6],
['96_888.89_0.009_6.in', '96/96_888.89_0.009_6.in', 888.89, 950.4444488, 0.009, 6],
['96_888.89_0.018_6.in', '96/96_888.89_0.018_6.in', 888.89, 950.4444488, 0.018, 6],
['96_1111.11_0_6.in', '96/96_1111.11_0_6.in', 1111.11, 950.4444488, 0, 6],
['96_1111.11_0.009_6.in', '96/96_1111.11_0.009_6.in', 1111.11, 950.4444488, 0.009, 6],
['96_1111.11_0.018_6.in', '96/96_1111.11_0.018_6.in', 1111.11, 950.4444488, 0.018, 6],
['96_1333.33_0_6.in', '96/96_1333.33_0_6.in', 1333.33, 950.4444488, 0, 6],
['96_1333.33_0.009_6.in', '96/96_1333.33_0.009_6.in', 1333.33, 950.4444488, 0.009, 6],
['96_1333.33_0.018_6.in', '96/96_1333.33_0.018_6.in', 1333.33, 950.4444488, 0.018, 6],
['96_1555.56_0_6.in', '96/96_1555.56_0_6.in', 1555.56, 950.4444488, 0, 6],
['96_1555.56_0.009_6.in', '96/96_1555.56_0.009_6.in', 1555.56, 950.4444488, 0.009, 6],
['96_1555.56_0.018_6.in', '96/96_1555.56_0.018_6.in', 1555.56, 950.4444488, 0.018, 6],
['96_1777.78_0_6.in', '96/96_1777.78_0_6.in', 1777.78, 950.4444488, 0, 6],
['96_1777.78_0.009_6.in', '96/96_1777.78_0.009_6.in', 1777.78, 950.4444488, 0.009, 6],
['96_1777.78_0.018_6.in', '96/96_1777.78_0.018_6.in', 1777.78, 950.4444488, 0.018, 6],
['96_2000_0_6.in', '96/96_2000_0_6.in', 2000, 950.4444488, 0, 6],
['96_2000_0.009_6.in', '96/96_2000_0.009_6.in', 2000, 950.4444488, 0.009, 6],
['96_2000_0.018_6.in', '96/96_2000_0.018_6.in', 2000, 950.4444488, 0.018, 6],
]

# Loop over the spectra.
for id, file, cpmg_frq, H_frq, delay, ndat in data:

    # Load the peak intensities.
    spectrum.read_intensities(file=file, dir=data_path, spectrum_id=id, int_method='height', res_num_col=1, int_col=2)

    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='SQ CPMG')

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.cpmg_setup(spectrum_id=id, cpmg_frq=cpmg_frq)

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=id, frq=H_frq*1e6)

    # Relaxation dispersion CPMG constant time delay T (in s).
    relax_disp.relax_time(spectrum_id=id, time=delay)

# set each spectrum noise RMSD
    if ndat == 1:
	spectrum.baseplane_rmsd(error=24000, spectrum_id=id, spin_id=None)
    elif ndat == 6:
	spectrum.baseplane_rmsd(error=65000, spectrum_id=id, spin_id=None)

# Peak intensity error analysis.
spectrum.error_analysis_per_field()

# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=ds.tmpdir, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL, pre_run_dir=PRE_RUN_DIR, insignificance=INSIGNIFICANCE, numeric_only=NUMERIC_ONLY, mc_sim_all_models=MC_SIM_ALL_MODELS)
