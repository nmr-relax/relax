###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The monte_carlo user function definitions for Monte Carlo simulations."""

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control import monte_carlo
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# Generic description document, used in all user functions.
monte_carlo_desc = Desc_container("Monte Carlo Simulation Overview")
monte_carlo_desc.add_paragraph("For proper error analysis using Monte Carlo simulations, a sequence of function calls is required for running the various simulation components.  The steps necessary for implementing Monte Carlo simulations are:")
monte_carlo_desc.add_item_list_element("1", "The measured data set together with the corresponding error set should be loaded into relax.")
monte_carlo_desc.add_item_list_element("2", "Either minimisation is used to optimise the parameters of the chosen model, or a calculation is run.")
monte_carlo_desc.add_item_list_element("3", "To initialise and turn on Monte Carlo simulations, the number of simulations, n, needs to be set.")
monte_carlo_desc.add_item_list_element("4", "The simulation data needs to be created either by back calculation from the fully minimised model parameters from step 2 or by direct calculation when values are calculated rather than minimised.  The error set is used to randomise each simulation data set by assuming Gaussian errors.  This creates a synthetic data set for each Monte Carlo simulation.")
monte_carlo_desc.add_item_list_element("5", "Prior to minimisation of the parameters of each simulation, initial parameter estimates are required.  These are taken as the optimised model parameters.  An alternative is to use a grid search for each simulation to generate initial estimates, however this is extremely computationally expensive.  For the case where values are calculated rather than minimised, this step should be skipped (although the results will be unaffected if this is accidentally run).")
monte_carlo_desc.add_item_list_element("6", "Each simulation requires minimisation or calculation.  The same techniques as used in step 2, excluding the grid search when minimising, should be used for the simulations.")
monte_carlo_desc.add_item_list_element("7", "Failed simulations are removed using the techniques of model elimination.")
monte_carlo_desc.add_item_list_element("8", "The model parameter errors are calculated from the distribution of simulation parameters.")
monte_carlo_desc.add_paragraph("Monte Carlo simulations can be turned on or off using functions within this class.  Once the function for setting up simulations has been called, simulations will be turned on.  The effect of having simulations turned on is that the functions used for minimisation (grid search, minimise, etc) or calculation will only affect the simulation parameters and not the model parameters.  By subsequently turning simulations off using the appropriate function, the functions used in minimisation will affect the model parameters and not the simulation parameters.")
monte_carlo_desc.add_paragraph("An example for model-free analysis using the prompt UI mode which includes only the functions required for implementing the above steps is:")
monte_carlo_desc.add_prompt("relax> minimise.grid_search(inc=11)                              # Step 2.")
monte_carlo_desc.add_prompt("relax> minimise.execute('newton')                                # Step 2.")
monte_carlo_desc.add_prompt("relax> monte_carlo.setup(number=500)                             # Step 3.")
monte_carlo_desc.add_prompt("relax> monte_carlo.create_data(method='back_calc')               # Step 4.")
monte_carlo_desc.add_prompt("relax> monte_carlo.initial_values()                              # Step 5.")
monte_carlo_desc.add_prompt("relax> minimise.execute('newton')                                # Step 6.")
monte_carlo_desc.add_prompt("relax> eliminate()                                               # Step 7.")
monte_carlo_desc.add_prompt("relax> monte_carlo.error_analysis()                              # Step 8.")
monte_carlo_desc.add_paragraph("An example for reduced spectral density mapping is:")
monte_carlo_desc.add_prompt("relax> minimise.calculate()                                      # Step 2.")
monte_carlo_desc.add_prompt("relax> monte_carlo.setup(number=500)                             # Step 3.")
monte_carlo_desc.add_prompt("relax> monte_carlo.create_data(method='back_calc')               # Step 4.")
monte_carlo_desc.add_prompt("relax> minimise.calculate()                                      # Step 6.")
monte_carlo_desc.add_prompt("relax> monte_carlo.error_analysis()                              # Step 8.")


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
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The method can either be set to back calculation (Monte Carlo) or direct (bootstrapping), the choice of which determines the simulation type.  If the values or parameters are calculated rather than minimised, this option will have no effect.  Errors should only be propagated via Monte Carlo simulations if errors have been measured. ")
uf.desc[-1].add_paragraph("For error analysis, the method should be set to back calculation which will result in proper Monte Carlo simulations.  The data used for each simulation is back calculated from the minimised model parameters and is randomised using Gaussian noise where the standard deviation is from the original error set.  When the method is set to back calculation, this function should only be called after the model is fully minimised.")
uf.desc[-1].add_paragraph("The simulation type can be changed by setting the method to direct.  This will result in bootstrapping simulations which cannot be used in error analysis (and which are no longer Monte Carlo simulations).  However, these simulations are required for certain model selection techniques (see the documentation for the model selection user function for details), and can be used for other purposes.  Rather than the data being back calculated from the fitted model parameters, the data is generated by taking the original data and randomising using Gaussian noise with the standard deviations set to the original error set.")
uf.desc.append(monte_carlo_desc)
uf.backend = monte_carlo.create_data
uf.menu_text = "&create_data"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'monte_carlo.png'


# The monte_carlo.error_analysis user function.
uf = uf_info.add_uf('monte_carlo.error_analysis')
uf.title = "Calculate parameter errors from the Monte Carlo simulations."
uf.title_short = "Error calculation."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Parameter errors are calculated as the standard deviation of the distribution of parameter values.  This function should never be used if parameter values are obtained by minimisation and the simulation data are generated using the method 'direct'.  The reason is because only true Monte Carlo simulations can give the true parameter errors.")
uf.desc.append(monte_carlo_desc)
uf.backend = monte_carlo.error_analysis
uf.menu_text = "&error_analysis"
uf.gui_icon = "oxygen.actions.roll-relax-blue"
uf.wizard_height_desc = 620
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'monte_carlo.png'


# The monte_carlo.initial_values user function.
uf = uf_info.add_uf('monte_carlo.initial_values')
uf.title = "Set the initial simulation parameter values."
uf.title_short = "Initial value setting."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This only effects where minimisation occurs and can therefore be skipped if the values or parameters are calculated rather than minimised.  However, if accidentally run in this case, the results will be unaffected.  It should only be called after the model or run is fully minimised.  Once called, the user functions minimise.grid_search and minimise.execute will only effect the simulations and not the model parameters.")
uf.desc[-1].add_paragraph("The initial values of the parameters for each simulation is set to the minimised parameters of the model.  A grid search can be undertaken for each simulation instead, although this is computationally expensive and unnecessary.  The minimisation function should be executed for a second time after running this function.")
uf.desc.append(monte_carlo_desc)
uf.backend = monte_carlo.initial_values
uf.menu_text = "&initial_values"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 620
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'monte_carlo.png'


# The monte_carlo.off user function.
uf = uf_info.add_uf('monte_carlo.off')
uf.title = "Turn the Monte Carlo simulations off."""
uf.title_short = "Simulations off."""
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will turn off the Monte Carlo simulations so that subsequent optimisation will operate directly on the model parameters and not on the simulations.")
uf.desc.append(monte_carlo_desc)
uf.backend = monte_carlo.off
uf.menu_text = "o&ff"
uf.gui_icon = "oxygen.actions.dialog-cancel"
uf.wizard_height_desc = 620
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'monte_carlo.png'


# The monte_carlo.on user function.
uf = uf_info.add_uf('monte_carlo.on')
uf.title = "Turn the Monte Carlo simulations on."""
uf.title_short = "Simulations on."""
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will turn on the Monte Carlo simulations so that subsequent optimisation will operate on the simulations rather than on the real model parameters.")
uf.desc.append(monte_carlo_desc)
uf.backend = monte_carlo.on
uf.menu_text = "o&n"
uf.gui_icon = "oxygen.actions.dialog-ok"
uf.wizard_height_desc = 620
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'monte_carlo.png'


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
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This must be called prior to any of the other Monte Carlo functions.  The effect is that the number of simulations will be set and that simulations will be turned on.")
uf.desc.append(monte_carlo_desc)
uf.backend = monte_carlo.setup
uf.menu_text = "&setup"
uf.gui_icon = "oxygen.actions.document-edit"
uf.wizard_height_desc = 570
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'monte_carlo.png'
