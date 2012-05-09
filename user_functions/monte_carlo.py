###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing the Monte Carlo simulation 'monte_carlo' user function data."""

# relax module imports.
from generic_fns import monte_carlo
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# Generic description document, used in all user functions.
monte_carlo_desc = ["Monte Carlo Simulation Overview", """
For proper error analysis using Monte Carlo simulations, a sequence of function calls is required for running the various simulation components.  The steps necessary for implementing Monte Carlo simulations are:

1.  The measured data set together with the corresponding error set should be loaded into relax.

2.  Either minimisation is used to optimise the parameters of the chosen model, or a calculation is run.

3.  To initialise and turn on Monte Carlo simulations, the number of simulations, n, needs to be set.

4.  The simulation data needs to be created either by back calculation from the fully minimised model parameters from step 2 or by direct calculation when values are calculated rather than minimised.  The error set is used to randomise each simulation data set by assuming Gaussian errors.  This creates a synthetic data set for each Monte Carlo simulation.

5.  Prior to minimisation of the parameters of each simulation, initial parameter estimates are required.  These are taken as the optimised model parameters.  An alternative is to use a grid search for each simulation to generate initial estimates, however this is extremely computationally expensive.  For the case where values are calculated rather than minimised, this step should be skipped (although the results will be unaffected if this is accidentally run).

6.  Each simulation requires minimisation or calculation.  The same techniques as used in step 2, excluding the grid search when minimising, should be used for the simulations.

7.  Failed simulations are removed using the techniques of model elimination.

8.  The model parameter errors are calculated from the distribution of simulation parameters.


Monte Carlo simulations can be turned on or off using functions within this class.  Once the function for setting up simulations has been called, simulations will be turned on.  The effect of having simulations turned on is that the functions used for minimisation (grid search, minimise, etc) or calculation will only affect the simulation parameters and not the model parameters.  By subsequently turning simulations off using the appropriate function, the functions used in minimisation will affect the model parameters and not the simulation parameters.


An example for model-free analysis using the prompt UI mode which includes only the functions required for implementing the above steps is:

relax> grid_search(inc=11)                                       # Step 2.
relax> minimise('newton')                                        # Step 2.
relax> monte_carlo.setup(number=500)                             # Step 3.
relax> monte_carlo.create_data(method='back_calc')               # Step 4.
relax> monte_carlo.initial_values()                              # Step 5.
relax> minimise('newton')                                        # Step 6.
relax> eliminate()                                               # Step 7.
relax> monte_carlo.error_analysis()                              # Step 8.

An example for reduced spectral density mapping is:

relax> calc()                                                    # Step 2.
relax> monte_carlo.setup(number=500)                             # Step 3.
relax> monte_carlo.create_data(method='back_calc')               # Step 4.
relax> calc()                                                    # Step 6.
relax> monte_carlo.error_analysis()                              # Step 8.
"""]


# The user function class.
uf_class = uf_info.add_class('monte_carlo')
uf_class.title = "Class containing the functions for Monte Carlo and related simulations."
uf_class.menu_text = "&monte_carlo"
uf_class.gui_icon = "oxygen.actions.roll-relax-blue"


# The monte_carlo.create_data user function.
uf = uf_info.add_uf('monte_carlo.create_data')
uf.title = "Create the Monte Carlo simulation data."
uf.title_short = "Data creation."
uf.add_keyarg(
    name = "method",
    default = "back_calc",
    py_type = "str",
    desc_short = "method",
    desc = "The simulation method.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["Monte Carlo", "Bootstrapping"],
    wiz_combo_data = ["back_calc", "direct"],
    wiz_read_only = True
)
uf.desc = """
The method can either be set to back calculation (Monte Carlo) or direct (bootstrapping), the choice of which determines the simulation type.  If the values or parameters are calculated rather than minimised, this option will have no effect.  Errors should only be propagated via Monte Carlo simulations if errors have been measured. 

For error analysis, the method argument should be set to back calculation which will result in proper Monte Carlo simulations.  The data used for each simulation is back calculated from the minimised model parameters and is randomised using Gaussian noise where the standard deviation is from the original error set.  When the method is set to back calculation, this function should only be called after the model is fully minimised.

The simulation type can be changed by setting the method argument to direct.  This will result in bootstrapping simulations which cannot be used in error analysis (and which are no longer Monte Carlo simulations).  However, these simulations are required for certain model selection techniques (see the documentation for the model selection user function for details), and can be used for other purposes.  Rather than the data being back calculated from the fitted model parameters, the data is generated by taking the original data and randomising using Gaussian noise with the standard deviations set to the original error set.
"""
uf.additional = [monte_carlo_desc]
uf.backend = monte_carlo.create_data
uf.menu_text = "&create_data"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False


# The monte_carlo.error_analysis user function.
uf = uf_info.add_uf('monte_carlo.error_analysis')
uf.title = "Calculate parameter errors from the Monte Carlo simulations."
uf.title_short = "Error calculation."
uf.add_keyarg(
    name = "prune",
    default = 0.0,
    py_type = "num",
    desc_short = "pruning quantity",
    desc = "Legacy argument corresponding to 'trim' in Art Palmer's Modelfree program.  The default value of 0.0 corresponds to no pruning of the data."
)
uf.desc = """
Parameter errors are calculated as the standard deviation of the distribution of parameter values.  This function should never be used if parameter values are obtained by minimisation and the simulation data are generated using the method 'direct'.  The reason is because only true Monte Carlo simulations can give the true parameter errors.

The prune argument is legacy code which corresponds to the 'trim' option in Art Palmer's Modelfree program.  To remove failed simulations, the eliminate function should be used prior to this function.  Eliminating the simulations specifically identifies and removes the failed simulations whereas the prune argument will only, in a few cases, positively identify failed simulations but only if severe parameter limits have been imposed.  Most failed models will pass through the pruning process and hence cause a catastrophic increase in the parameter errors.  If the argument must be used, the following must be taken into account. If the values or parameters are calculated rather than minimised, the prune argument must be set to zero.  The value of this argument is proportional to the number of simulations removed prior to error calculation.  If prune is set to 0.0, all simulations are used for calculating errors, whereas a value of 1.0 excludes all data.  In almost all cases prune must be set to zero, any value greater than zero will result in an underestimation of the error values.  If a value is supplied, the lower and upper tails of the distribution of chi-squared values will be excluded from the error calculation.
"""
uf.additional = [monte_carlo_desc]
uf.backend = monte_carlo.error_analysis
uf.menu_text = "&error_analysis"
uf.wizard_height_desc = 650
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False


# The monte_carlo.initial_values user function.
uf = uf_info.add_uf('monte_carlo.initial_values')
uf.title = "Set the initial simulation parameter values."
uf.title_short = "Initial value setting."
uf.desc = """
This only effects where minimisation occurs and can therefore be skipped if the values or parameters are calculated rather than minimised.  However, if accidentally run in this case, the results will be unaffected.  It should only be called after the model or run is fully minimised.  Once called, the functions 'grid_search' and 'minimise' will only effect the simulations and not the model parameters.

The initial values of the parameters for each simulation is set to the minimised parameters of the model.  A grid search can be undertaken for each simulation instead, although this is computationally expensive and unnecessary.  The minimisation function should be executed for a second time after running this function.
"""
uf.additional = [monte_carlo_desc]
uf.backend = monte_carlo.initial_values
uf.menu_text = "&initial_values"
uf.wizard_height_desc = 650
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False


# The monte_carlo.off user function.
uf = uf_info.add_uf('monte_carlo.off')
uf.title = "Turn the Monte Carlo simulations off."""
uf.title_short = "Simulations off."""
uf.desc = """
This will turn off the Monte Carlo simulations so that subsequent optimisation will operate directly on the model parameters and not on the simulations.
"""
uf.additional = [monte_carlo_desc]
uf.backend = monte_carlo.off
uf.menu_text = "o&ff"
uf.wizard_height_desc = 650
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False


# The monte_carlo.on user function.
uf = uf_info.add_uf('monte_carlo.on')
uf.title = "Turn the Monte Carlo simulations on."""
uf.title_short = "Simulations on."""
uf.desc = """
This will turn on the Monte Carlo simulations so that subsequent optimisation will operate on the simulations rather than on the real model parameters.
"""
uf.additional = [monte_carlo_desc]
uf.backend = monte_carlo.on
uf.menu_text = "o&n"
uf.wizard_height_desc = 650
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False


# The monte_carlo.setup user function.
uf = uf_info.add_uf('monte_carlo.setup')
uf.title = "Set up the Monte Carlo simulations."
uf.title_short = "Simulation setup."
uf.add_keyarg(
    name = "number",
    default = 500,
    py_type = "int",
    min = 3,
    max = 100000,
    desc_short = "number of Monte Carlo simulations",
    desc = "The number of Monte Carlo simulations."
)
uf.desc = """
This must be called prior to any of the other Monte Carlo functions.  The effect is that the number of simulations will be set and that simulations will be turned on.
"""
uf.additional = [monte_carlo_desc]
uf.backend = monte_carlo.setup
uf.menu_text = "&setup"
uf.wizard_height_desc = 600
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False
