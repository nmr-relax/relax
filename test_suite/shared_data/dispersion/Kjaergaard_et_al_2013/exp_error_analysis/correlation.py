
# relax module imports.
from pipe_control.mol_res_spin import return_spin, spin_loop


# Load the results.
pipe.create('covar', 'relax_disp')
results.read('covar_errors')
pipe.create('mc', 'relax_disp')
results.read('mc_errors')
pipe.switch('mc')

# The Grace files.
file_i0 = open('i0_correlation.agr', 'w')
file_i0.write('@target G0.S0\n@type xy\n')
file_r2eff = open('r2eff_correlation.agr', 'w')
file_r2eff.write('@target G0.S0\n@type xy\n')

# Loop over the spins.
for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
    # The covar spin.
    spin2 = return_spin(spin_id=spin_id, pipe='covar')

    # Loop over the keys.
    for key in spin.r2eff.keys():
        file_i0.write("%s %s\n" % (spin.i0_err[key], spin2.i0_err[key]))
        file_r2eff.write("%s %s\n" % (spin.r2eff_err[key], spin2.r2eff_err[key]))

# End the file.
file_i0.write('&\n')
file_r2eff.write('&\n')
