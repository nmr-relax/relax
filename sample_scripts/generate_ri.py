# Script for generating synthetic relaxation data.

# relax module imports.
from generic.selection import spin_loop


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


# Create the run
pipe.create('test', 'mf')

# Set the nucleus type to nitrogen.
value.set('15N', 'heteronucleus')

# Set the diffusion tensor to isotropic with tm set to 10 ns.
diffusion_tensor.init(10e-9)

# Add a residue.
sequence.add(1, 'ALA')

# Set the CSA and bond lengths.
value.set(value=-172e-6, param='CSA')
value.set(value=1.02e-10, param='r')

# Set the model-free parameters.
value.set(value=0.8, param='S2')
value.set(value=20e-12, param='te')

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
