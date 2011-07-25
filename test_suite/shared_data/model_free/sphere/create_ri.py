###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
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

"""Script for generating relaxation data for the bond vectors in 'sphere.pdb'.

Each vector will have the model-free parameter values of S2 = 0.8, te = 20 ns, Rex = 0 1/s.  The diffusion tensor is isotropic with a correlation time of 10 ns.
"""

# relax module imports.
from generic_fns.mol_res_spin import spin_loop


# Create the data pipe.
pipe.create('sphere', 'mf')

# Load a PDB file.
structure.read_pdb('sphere.pdb')

# Load the backbone amide nitrogen spins from the structure.
structure.load_spins(spin_id='@N')

# Load the NH vectors.
structure.vectors(spin_id='@N', attached='H', ave=False)

# Set the diffusion tensor to isotropic with tm set to 10 ns.
diffusion_tensor.init(10e-9)

# Set the CSA and bond lengths.
value.set(val=-172e-6, param='CSA')
value.set(val=1.02e-10, param='r')
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Set the model-free parameters.
value.set(val=0.8, param='S2')
value.set(val=20e-12, param='te')

# Select model-free model m2.
model_free.select_model(model='m2')

# Back calculate the relaxation data.
relax_data.back_calc(ri_id='NOE_600', ri_type='600', frq=600e6)
relax_data.back_calc(ri_id='R1_600',  ri_type='600', frq=600e6)
relax_data.back_calc(ri_id='R2_600',  ri_type='600', frq=600e6)
relax_data.back_calc(ri_id='NOE_500', ri_type='500', frq=500e6)
relax_data.back_calc(ri_id='R1_500',  ri_type='500', frq=500e6)
relax_data.back_calc(ri_id='R2_500',  ri_type='500', frq=500e6)

# Generate the errors.
for spin in spin_loop():
    # Loop over the relaxation data.
    for ri_id in cdp.ri_ids:
        # 600 MHz NOE.
        if ri_id == 'NOE_600':
            spin.ri_data_err[ri_id] = 0.04

        # 500 MHz NOE.
        elif ri_id == 'NOE_500':
            spin.ri_data_err[ri_id] = 0.05

        # All other data.
        else:
            spin.ri_data_err[ri_id] = spin.ri_data[ri_id] * 0.02

# Write the relaxation data to file.
relax_data.write(ri_id='NOE_600', ri_type='NOE', file='noe.600.out', force=True)
relax_data.write(ri_id='R1_600',  ri_type='R1',  file='r1.600.out', force=True)
relax_data.write(ri_id='R2_600',  ri_type='R2',  file='r2.600.out', force=True)
relax_data.write(ri_id='NOE_500', ri_type='NOE', file='noe.500.out', force=True)
relax_data.write(ri_id='R1_500',  ri_type='R1',  file='r1.500.out', force=True)
relax_data.write(ri_id='R2_500',  ri_type='R2',  file='r2.500.out', force=True)
