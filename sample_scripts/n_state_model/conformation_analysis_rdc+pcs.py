###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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

"""Script for determining populations for lactose conformations using RDCs and PCSs.

The reference for this script is:

    Erdelyi, M., d'Auvergne, E. J., Navarro-Vazquez, A., Leonov, A. and Griesinger, C. (2011).  Dynamics of the glycosidic bond.  Conformational space of lactose.  Manuscript in preparation.
"""


# Python imports.
from os import getcwd, listdir
from re import search

# relax imports.
from data import Relax_data_store; ds = Relax_data_store()
from specific_fns.setup import n_state_model_obj


# Create the data pipe.
pipe.create('lactose', 'N-state')

# Load the structures.
files = listdir(getcwd())
num = 1
for file in files:
    print file
    if search('.pdb$', file):
        structure.read_pdb(file=file, parser='internal', set_model_num=num, set_mol_name='conf')
        num += 1
NUM_STR = num - 1

# Load the sequence information.
structure.load_spins(spin_id=':900@C*', ave_pos=False)
structure.load_spins(spin_id=':900@H*', ave_pos=False)

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
deselect.spin(spin_id=':900@H6')
deselect.spin(spin_id=':900@H7')
deselect.spin(spin_id=':900@H17')
deselect.spin(spin_id=':900@H18')

# Load the CH vectors for the C atoms.
structure.vectors(spin_id='@C*', attached='H*', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.10 * 1e-10, 'bond_length', spin_id="@C*")
value.set('13C', 'heteronucleus', spin_id="@C*")
value.set('1H', 'proton', spin_id="@C*")

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er', 'Yb', 'Eu']

# Load the RDCs and PCSs.
for i in xrange(len(align_list)):
    # The RDC.
    rdc.read(align_id=align_list[i], file='rdc_Series1_G.txt', dir='../../../align_data', mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=i+3, error_col=None)
    rdc.read(align_id=align_list[i], file='rdc_err_measured.txt', dir='../../../align_data', mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=None, error_col=i+3)
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
    temperature(id=align_list[i], temp=298)

    # The frequency.
    frq.set(id=align_list[i], frq=900.015 * 1e6)

# Tag.
######

# Create a data pipe for the aligned tag structures.
pipe.create('tag', 'N-state')

# Load all the tag structures.
NUM_TAG = 1000
for i in range(NUM_TAG):
    structure.read_pdb(file='LactoseMCMM4_'+`i+1`, dir='../../../structures/tag_1000/080704_MCMM4_aligned-forEd1000', parser='internal', set_model_num=i+1, set_mol_name='tag')

# Load the lanthanide atoms.
structure.load_spins(spin_id=':4@C1', combine_models=False, ave_pos=False)

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
for j in xrange(NUM_STR):
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
        print "%16.10f %s" % (cdp.probs[i], cdp.structure.structural_data[i].mol[0].file_name)
