# Script for generating relaxation data for the 400 bond vectors in 'sphere.pdb'.
# Each vector will have the model-free parameter values of S2 = 0.8, te = 20 ns, Rex = 0 1/s.
# The diffusion tensor is isotropic with a correlation time of 10 ns.

# Create the run
name = 'sphere'
create_run(name, 'mf')

# Set the nucleus type to nitrogen.
nuclei('N')

# Set the diffusion tensor to isotropic with tm set to 10 ns.
diffusion_tensor.set(name, 10e-9)

# Generate the sequence from the PDB file.
pdb(name, 'sphere.pdb')

# Set the CSA and bond lengths.
value.set(name, value=-170e-6, data_type='CSA')
value.set(name, value=1.02e-10, data_type='r')

# Set the model-free parameters.
value.set(name, value=0.8, data_type='S2')
value.set(name, value=20e-12, data_type='te')

# Select model-free model m2.
model_free.select_model(name, model='m2')

# Back calculate the relaxation data.
relax_data.back_calc(name, ri_label='NOE', frq_label='600', frq=600e6)
relax_data.back_calc(name, ri_label='R1', frq_label='600', frq=600e6)
relax_data.back_calc(name, ri_label='R2', frq_label='600', frq=600e6)
relax_data.back_calc(name, ri_label='NOE', frq_label='500', frq=500e6)
relax_data.back_calc(name, ri_label='R1', frq_label='500', frq=500e6)
relax_data.back_calc(name, ri_label='R2', frq_label='500', frq=500e6)

# Generate the errors.
for i in xrange(len(self.relax.data.res[name])):
    # Loop over the relaxation data.
    for j in xrange(len(self.relax.data.res[name][i].relax_data)):
        # Alias.
        data = self.relax.data.res[name][i]

        # 600 MHz NOE.
        if data.ri_labels[j] == 'NOE' and data.frq_labels[data.remap_table[j]] == '600':
            data.relax_error[j] = 0.04

        # 500 MHz NOE.
        elif data.ri_labels[j] == 'NOE' and data.frq_labels[data.remap_table[j]] == '500':
            data.relax_error[j] = 0.05

        # All other data.
        else:
            data.relax_error[j] = data.relax_data[j] * 0.02

# Write the relaxation data to file.
relax_data.write(name, ri_label='NOE', frq_label='600', file='noe.600.out', force=1)
relax_data.write(name, ri_label='R1', frq_label='600', file='r1.600.out', force=1)
relax_data.write(name, ri_label='R2', frq_label='600', file='r2.600.out', force=1)
relax_data.write(name, ri_label='NOE', frq_label='500', file='noe.500.out', force=1)
relax_data.write(name, ri_label='R1', frq_label='500', file='r1.500.out', force=1)
relax_data.write(name, ri_label='R2', frq_label='500', file='r2.500.out', force=1)
