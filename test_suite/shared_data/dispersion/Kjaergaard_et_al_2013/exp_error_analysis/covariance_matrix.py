# Check the R2eff and I0 errors using the covariance technique.

# Python module imports.
from os import chdir, getcwd, pardir, sep


# Setup.
cwd = getcwd()
chdir(pardir)
script('1_setup_r1rho.py')
chdir(cwd)

# Peak intensity error analysis.
spectrum.error_analysis()

# Only select a few spins for speed.
deselect.all()
select.spin(":5-10")

# The model.
relax_disp.select_model('R2eff')

# Optimisation.
minimise.grid_search(inc=11)
minimise.execute('newton', constraints=False)

# Error analysis.
relax_disp.r2eff_err_estimate(chi2_jacobian=True)

# Write out the values.
value.write(param='r2eff', file='r2eff_covar.txt', force=True)
value.write(param='i0', file='i0_covar.txt', force=True)

# Save the state.
state.save('covar_errors', force=True)

