"""Optimise the SQ data in relax.

To run this, type:

$ rm -f optimise_sq.log; ../../../../../relax --tee optimise_sq.log optimise_sq.py
"""

# Load the program state.
state.load('sq_state')

# Copy the data to a new pipe.
pipe_name = 'MMQ 1H+15N SQ'
pipe.copy('R2eff', pipe_name)
pipe.switch(pipe_name)

# Change the model.
relax_disp.select_model('MQ NS CPMG 2-site')

# Manually set the parameter values.
spin_H = cdp.mol[0].res[0].spin[0]
spin_H.r2 = [6.779626, 7.089813, 5.610770]
spin_H.pA = 0.947960
spin_H.kex = 408.394
spin_H.dw = 4.369907
spin_H.dwH = -0.267240
spin_N = cdp.mol[0].res[0].spin[1]
spin_N.r2 = [8.412998, 8.847946, 10.329567]
spin_N.pA = 0.947960
spin_N.kex = 408.394
spin_N.dw = 4.369907
spin_N.dwH = -0.267240

# Optimisation.
minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()
minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)
monte_carlo.error_analysis()

# Save the results.
state.save('state', dir='sq', compress_type=1, force=True)
