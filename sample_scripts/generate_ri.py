# Script for generating synthetic relaxation data.


def back_calc(run):
    """Function for back calculating the relaxation data."""

    relax_data.back_calc(run, ri_label='NOE', frq_label='600', frq=600e6)
    relax_data.back_calc(run, ri_label='R1', frq_label='600', frq=600e6)
    relax_data.back_calc(run, ri_label='R2', frq_label='600', frq=600e6)
    relax_data.back_calc(run, ri_label='NOE', frq_label='500', frq=500e6)
    relax_data.back_calc(run, ri_label='R1', frq_label='500', frq=500e6)
    relax_data.back_calc(run, ri_label='R2', frq_label='500', frq=500e6)


def errors(run):
    """Function for generating relaxation data errors."""

    # Loop over the sequence.
    for i in xrange(len(self.relax.data.res[run])):
        # Loop over the relaxation data.
        for j in xrange(len(self.relax.data.res[run][i].relax_data)):
            # Alias.
            data = self.relax.data.res[run][i]

            # 600 MHz NOE.
            if data.ri_labels[j] == 'NOE' and data.frq_labels[data.remap_table[j]] == '600':
                data.relax_error[j] = 0.04

            # 500 MHz NOE.
            elif data.ri_labels[j] == 'NOE' and data.frq_labels[data.remap_table[j]] == '500':
                data.relax_error[j] = 0.05

            # All other data.
            else:
                data.relax_error[j] = data.relax_data[j] * 0.02


def write(run):
    """Function for writing the relaxation data to file."""

    relax_data.write(run, ri_label='NOE', frq_label='600', file='noe.600.out', force=1)
    relax_data.write(run, ri_label='R1', frq_label='600', file='r1.600.out', force=1)
    relax_data.write(run, ri_label='R2', frq_label='600', file='r2.600.out', force=1)
    relax_data.write(run, ri_label='NOE', frq_label='500', file='noe.500.out', force=1)
    relax_data.write(run, ri_label='R1', frq_label='500', file='r1.500.out', force=1)
    relax_data.write(run, ri_label='R2', frq_label='500', file='r2.500.out', force=1)


# Create the run
run = 'test'
run.create(run, 'mf')

# Set the nucleus type to nitrogen.
nuclei('N')

# Set the diffusion tensor to isotropic with tm set to 10 ns.
diffusion_tensor.set(run, 10e-9)

# Generate the sequence from the PDB file.
pdb(run, 'test.pdb')

# Set the CSA and bond lengths.
value.set(run, value=-170e-6, data_type='CSA')
value.set(run, value=1.02e-10, data_type='r')

# Set the model-free parameters.
value.set(run, value=0.8, data_type='S2')
value.set(run, value=20e-12, data_type='te')

# Select model-free model m2.
model_free.select_model(run, model='m2')

# Back calculate the relaxation data.
back_calc(run)

# Generate the errors.
errors(run)

# Write the relaxation data to file.
results.write(run)
