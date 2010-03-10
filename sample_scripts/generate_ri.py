###############################################################################
#                                                                             #
# Copyright (C) 2004-2010 Edward d'Auvergne                                   #
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

"""Script for back-calculating the relaxation data."""

# relax module imports.
from generic_fns.mol_res_spin import spin_loop


def back_calc():
    """Function for back calculating the relaxation data."""

    relax_data.back_calc(ri_label='NOE', frq_label='600', frq=600e6)
    relax_data.back_calc(ri_label='R1', frq_label='600', frq=600e6)
    relax_data.back_calc(ri_label='R2', frq_label='600', frq=600e6)
    relax_data.back_calc(ri_label='NOE', frq_label='500', frq=500e6)
    relax_data.back_calc(ri_label='R1', frq_label='500', frq=500e6)
    relax_data.back_calc(ri_label='R2', frq_label='500', frq=500e6)


def errors():
    """Function for generating relaxation data errors."""

    # Loop over the sequence.
    for spin in spin_loop():
        # Loop over the relaxation data.
        for j in xrange(len(spin.relax_data)):
            # No data.
            if spin.relax_data[j] == None:
                continue

            # 600 MHz NOE.
            if spin.ri_labels[j] == 'NOE' and spin.frq_labels[spin.remap_table[j]] == '600':
                spin.relax_error[j] = 0.04

            # 500 MHz NOE.
            elif spin.ri_labels[j] == 'NOE' and spin.frq_labels[spin.remap_table[j]] == '500':
                spin.relax_error[j] = 0.05

            # All other data.
            else:
                spin.relax_error[j] = spin.relax_data[j] * 0.02


def write():
    """Function for writing the relaxation data to file."""

    relax_data.write(ri_label='NOE', frq_label='600', file='noe.600.out', force=True)
    relax_data.write(ri_label='R1', frq_label='600', file='r1.600.out', force=True)
    relax_data.write(ri_label='R2', frq_label='600', file='r2.600.out', force=True)
    relax_data.write(ri_label='NOE', frq_label='500', file='noe.500.out', force=True)
    relax_data.write(ri_label='R1', frq_label='500', file='r1.500.out', force=True)
    relax_data.write(ri_label='R2', frq_label='500', file='r2.500.out', force=True)


# Create the data pipe.
pipe.create('test', 'mf')

# Load a PDB file.
structure.read_pdb('example.pdb')

# Load the backbone amide nitrogen spins from the structure.
structure.load_spins(spin_id='@N')

# Set the spin name and then load the NH vectors.
structure.vectors(spin_id='@N', attached='H*', ave=False)

# Set the diffusion tensor in the PDB frame (Dxx, Dyy, Dzz, Dxy, Dxz, Dyz).
diffusion_tensor.init((1.340e7, 1.516e7, 1.691e7, 0.000e7, 0.000e7, 0.000e7), param_types=3)

# Set the required values.
value.set(val=-172e-6, param='CSA')
value.set(val=1.02e-10, param='r')
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')
value.set(val=0.8, param='S2')
value.set(val=20e-12, param='te')

# Select model-free model m2.
model_free.select_model(model='m2')

# Back calculate the relaxation data.
back_calc()

# Generate the errors.
errors()

# Write the data.
write()

# Write the relaxation data to file.
results.write()
