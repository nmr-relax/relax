# Check the R2eff and I0 errors from a large number of Monte Carlo simulations.

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
monte_carlo.setup(number=10000)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise.execute('newton', constraints=False)
monte_carlo.error_analysis()

# Write out the values.
value.write(param='r2eff', file='r2eff_mc.txt', force=True)
value.write(param='i0', file='i0_mc.txt', force=True)

# Save the state.
state.save('mc_errors', force=True)
