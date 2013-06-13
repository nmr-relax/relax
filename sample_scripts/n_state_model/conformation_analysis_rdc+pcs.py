###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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

"""Script for determining populations for lactose conformations using RDCs and PCSs.

The reference for this script is:

    Erdelyi, M., d'Auvergne E., Navarro-Vazquez, A., Leonov, A., and Griesinger, C. (2011) Dynamics of the Glycosidic Bond: Conformational Space of Lactose. Chemistry-A European Journal, 17(34), 9368-9376 (http://dx.doi.org/10.1002/chem.201100854).

This should be used in combination with the local_min_search.py sample script.
"""


# Python imports.
from os import getcwd, listdir
from re import search

# relax imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from specific_analyses.setup import n_state_model_obj


# Create the data pipe.
pipe.create('lactose', 'N-state')

# Load all PDB structures from the current directory.
files = listdir(getcwd())
num = 1
for file in files:
    print(file)
    if search('.pdb$', file):
        structure.read_pdb(file=file, set_model_num=num, set_mol_name='conf')
        num += 1
NUM_STR = num - 1

# Set up the 13C and 1H spins information.
structure.load_spins(spin_id=':900@C*', ave_pos=False)
structure.load_spins(spin_id=':900@H*', ave_pos=False)
spin.isotope(isotope='13C', spin_id='@C*')
spin.isotope(isotope='1H', spin_id='@H*')

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1='@C*', spin_id2='@H*', direct_bond=True)
interatom.set_dist(spin_id1='@C*', spin_id2='@H*', ave_dist=1.10 * 1e-10)
interatom.unit_vectors(ave=False)

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
deselect.spin(spin_id=':900@H6')
deselect.spin(spin_id=':900@H7')
deselect.spin(spin_id=':900@H17')
deselect.spin(spin_id=':900@H18')

# Deselect the CH2 bonds.
deselect.interatom(spin_id1=':900@C6', spin_id2=':900@H6')
deselect.interatom(spin_id1=':900@C6', spin_id2=':900@H7')
deselect.interatom(spin_id1=':900@C12', spin_id2=':900@H17')
deselect.interatom(spin_id1=':900@C12', spin_id2=':900@H18')

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er', 'Yb', 'Eu']

# Load the RDCs and PCSs.
for i in range(len(align_list)):
    # The RDC.
    rdc.read(align_id=align_list[i], file='rdc_Series1_G.txt', dir='../../../align_data', spin_id1_col=1, spin_id2_col=2, data_col=i+3, error_col=None)
    rdc.read(align_id=align_list[i], file='rdc_err_measured.txt', dir='../../../align_data', spin_id1_col=1, spin_id2_col=2, data_col=None, error_col=i+3)
    rdc.display(align_id=align_list[i])

    # The PCS.
    pcs.read(align_id=align_list[i], file='pcs_Series1_G.txt', dir='../../../align_data', mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=i+2, error_col=None)
    pcs.read(align_id=align_list[i], file='pcs_err_measured+rcsa.txt', dir='../../../align_data', mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=None, error_col=i+2)
    pcs.display(align_id=align_list[i])

    # The weights.
    rdc.weight(align_id=align_list[i], spin_id=None)
    pcs.weight(align_id=align_list[i], spin_id='@C*')
    pcs.weight(align_id=align_list[i], spin_id='@H*')

    # The temperature.
    spectrometer.temperature(id=align_list[i], temp=298)

    # The frequency.
    spectrometer.frequency(id=align_list[i], frq=900.015 * 1e6)

# Tag.
######

# Create a data pipe for the aligned tag structures.
pipe.create('tag', 'N-state')

# Load all the tag structures.
NUM_TAG = 1000
for i in range(NUM_TAG):
    structure.read_pdb(file='LactoseMCMM4_'+`i+1`, dir='../../../structures/tag_1000/080704_MCMM4_aligned-forEd1000', set_model_num=i+1, set_mol_name='tag')

# Load the lanthanide atoms.
structure.load_spins(spin_id=':4@C1', ave_pos=False)

# Switch back to the main analysis data pipe.
pipe.switch('lactose')

# Calculate the paramagnetic centre (from the structures in the 'tag' data pipe).
paramag.centre(atom_id=':4@C1', pipe='tag')


# Fixed model.
##############

# Set up the model.
n_state_model.select_model(model='fixed')

# Minimisation.
minimise('newton')

# Calculate the AIC value.
k, n, chi2 = n_state_model_obj.model_statistics()
ds[ds.current_pipe].aic = chi2 + 2.0*k

# Write out a results file.
results.write('results_fixed_rdc+pcs', dir=None, force=True)


# Population model.
###################

# Set up the model.
n_state_model.select_model(model='population')

# Set to equal probabilities.
for j in range(NUM_STR):
    value.set(1.0/NUM_STR, 'p'+`j`)

# Minimisation.
minimise('bfgs', constraints=True)

# Calculate the AIC value.
k, n, chi2 = n_state_model_obj.model_statistics()
ds[ds.current_pipe].aic = chi2 + 2.0*k

# Write out a results file.
results.write('results_population_rdc+pcs', dir=None, force=True)

# Show the tensors.
align_tensor.display()

# Show the populations.
for i in range(len(cdp.structure.structural_data)):
    if abs(cdp.probs[i]) > 1e-7:
        print("%16.10f %s" % (cdp.probs[i], cdp.structure.structural_data[i].mol[0].file_name))
