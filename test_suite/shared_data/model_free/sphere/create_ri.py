###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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

"""Script for generating relaxation data for the bond vectors in 'sphere.pdb'.

Each vector will have the model-free parameter values of S2 = 0.8, te = 20 ns, Rex = 0 1/s.  The diffusion tensor is isotropic with a correlation time of 10 ns.
"""

# relax module imports.
from generic_fns.mol_res_spin import spin_loop


# Create the data pipe.
pipe.create('sphere', 'mf')

# Load a PDB file.
structure.read_pdb('sphere.pdb')

# Load the backbone amide nitrogen and proton spins from the structure.
structure.load_spins(spin_id='@N')
structure.load_spins(spin_id='@H')
structure.load_spins(spin_id='@NE1')
structure.load_spins(spin_id='@HE1')
spin.isotope('15N', spin_id='@N*')
spin.isotope('1H', spin_id='@H*')

# Set the diffusion tensor to isotropic with tm set to 10 ns.
diffusion_tensor.init(10e-9)

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.define(spin_id1='@NE1', spin_id2='@HE1', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N*', spin_id2='@H*', ave_dist=1.02 * 1e-10)
dipole_pair.unit_vectors()

# Define the chemical shift relaxation interaction.
value.set(-172 * 1e-6, 'csa', spin_id='@N*')

# Set the model-free parameters.
value.set(val=0.8, param='s2')
value.set(val=20e-12, param='te')

# Select model-free model m2.
model_free.select_model(model='m2')

# Back calculate the relaxation data.
relax_data.back_calc(ri_id='NOE_900', ri_type='NOE', frq=900e6)
relax_data.back_calc(ri_id='R1_900',  ri_type='R1',  frq=900e6)
relax_data.back_calc(ri_id='R2_900',  ri_type='R2',  frq=900e6)
relax_data.back_calc(ri_id='NOE_500', ri_type='NOE', frq=500e6)
relax_data.back_calc(ri_id='R1_500',  ri_type='R1',  frq=500e6)
relax_data.back_calc(ri_id='R2_500',  ri_type='R2',  frq=500e6)

# Generate the errors.
for spin in spin_loop():
    # No relaxation data.
    if not spin.select:
        continue

    # Loop over the relaxation data.
    for ri_id in cdp.ri_ids:
        # Set up the error relaxation data structure if needed.
        if not hasattr(spin, 'ri_data_err'):
            spin.ri_data_err = {}

        # 900 MHz NOE.
        if ri_id == 'NOE_900':
            spin.ri_data_err[ri_id] = 0.04

        # 500 MHz NOE.
        elif ri_id == 'NOE_500':
            spin.ri_data_err[ri_id] = 0.05

        # All other data.
        else:
            spin.ri_data_err[ri_id] = spin.ri_data_bc[ri_id] * 0.02

# Write the relaxation data to file.
relax_data.write(ri_id='NOE_900', file='noe.900.out', bc=True, force=True)
relax_data.write(ri_id='R1_900',  file='r1.900.out',  bc=True, force=True)
relax_data.write(ri_id='R2_900',  file='r2.900.out',  bc=True, force=True)
relax_data.write(ri_id='NOE_500', file='noe.500.out', bc=True, force=True)
relax_data.write(ri_id='R1_500',  file='r1.500.out',  bc=True, force=True)
relax_data.write(ri_id='R2_500',  file='r2.500.out',  bc=True, force=True)
