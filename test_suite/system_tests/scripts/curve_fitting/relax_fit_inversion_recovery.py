###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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
from os import sep

# relax module imports.
from auto_analyses.relax_fit import Relax_fit
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing temporary directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp'

# The path to the data files.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'+sep+'bug_23244_Iinf_graph'


# Create the 'test' data pipe.
pipe.create(pipe_name='test', bundle='R1 analysis', pipe_type='relax_fit')

# Set up the sequence.
spin.create(res_num=51, spin_name='CG2')

# Load the peak intensities.
spectrum.read_intensities(file=['GB1_TR347_T1_1_1.list', 'GB1_TR347_T1_2_1.list', 'GB1_TR347_T1_3_1.list', 'GB1_TR347_T1_4_1.list', 'GB1_TR347_T1_5_1.list', 'GB1_TR347_T1_6_1.list', 'GB1_TR347_T1_7_1.list', 'GB1_TR347_T1_8_1.list', 'GB1_TR347_T1_9_1.list', 'GB1_TR347_T1_10_1.list', 'GB1_TR347_T1_11_1.list', 'GB1_TR347_T1_12_1.list', 'GB1_TR347_T1_13_1.list', 'GB1_TR347_T1_14_1.list', 'GB1_TR347_T1_15_1.list', 'GB1_TR347_T1_16_1.list', 'GB1_TR347_T1_17_1.list'], dir=DATA_PATH, spectrum_id=['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'g10', 'g11', 'g12', 'g13', 'g14', 'g15', 'g16', 'g17'], dim=1, int_method='height', int_col=None, spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, sep=None, spin_id=None, ncproc=None)

# Spectrum baseplane noise for non-duplicated spectra
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g1', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g2', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g3', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g4', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g5', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g6', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g8', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g7', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g9', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g10', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g11', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g12', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g13', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g14', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g15', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g16', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g17', spin_id=None)
spectrum.baseplane_rmsd(error=40000.0, spectrum_id='g17', spin_id=None)

# Set the relaxation times.
relax_fit.relax_time(time=0.001, spectrum_id='g1')
relax_fit.relax_time(time=0.005, spectrum_id='g2')
relax_fit.relax_time(time=0.01, spectrum_id='g3')
relax_fit.relax_time(time=0.025, spectrum_id='g4')
relax_fit.relax_time(time=0.05, spectrum_id='g5')
relax_fit.relax_time(time=0.075, spectrum_id='g6')
relax_fit.relax_time(time=0.1, spectrum_id='g7')
relax_fit.relax_time(time=0.15, spectrum_id='g8')
relax_fit.relax_time(time=0.2, spectrum_id='g9')
relax_fit.relax_time(time=0.25, spectrum_id='g10')
relax_fit.relax_time(time=0.3, spectrum_id='g11')
relax_fit.relax_time(time=0.4, spectrum_id='g12')
relax_fit.relax_time(time=0.5, spectrum_id='g13')
relax_fit.relax_time(time=0.6, spectrum_id='g14')
relax_fit.relax_time(time=0.75, spectrum_id='g15')
relax_fit.relax_time(time=0.9, spectrum_id='g16')
relax_fit.relax_time(time=1.0, spectrum_id='g17')
relax_fit.relax_time(time=1.0, spectrum_id='g17')

# Set the relaxation curve type for the inversion recovery.
relax_fit.select_model(model='inv')

# Execute the auto-analysis
Relax_fit(pipe_name='test', pipe_bundle='R1 analysis', file_root='rx', results_dir=ds.tmpdir, grid_inc=11, mc_sim_num=50, view_plots=False)
