###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
"""The minimisation user function definitions."""

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control import minimise
from user_functions.data import Uf_info, Uf_tables; uf_info = Uf_info(); uf_tables = Uf_tables()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('minimise')
uf_class.title = "Class for setting parameter values."
uf_class.menu_text = "&minimise"
uf_class.gui_icon = "relax.rosenbrock"


# The minimise.calculate user function.
uf = uf_info.add_uf('minimise.calculate')
uf.title = "Calculate the model parameters or the current target function value."
uf.title_short = "Model parameter or target function value calculation."
uf.display = True
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The operation of this user function is two-fold and depends on whether the solution for the models of the current analysis are found by direct calculation or by optimisation.  The dual operations are:")
uf.desc[-1].add_item_list_element("Direct calculation models", "For these models, the parameters will be directly calculated from the base data.  This will be the exact solution and the user function will store the parameter values.  The grid search and optimisation user functions are not implemented for this analysis type.")
uf.desc[-1].add_item_list_element("Optimised models", "This will call the target function normally used for optimisation for each model using the current parameter values.  This can be used to manually find the chi-squared value for different parameter values.  The parameter values will not be affected.")
uf.backend = minimise.calc
uf.menu_text = "&calculate"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_size = (900, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'minimise.png'


# The minimise.execute user function.
uf = uf_info.add_uf('minimise.execute')
uf.title = "Perform an optimisation."
uf.title_short = "Minimisation."
uf.display = True
uf.add_keyarg(
    name = "min_algor",
    default = "newton",
    py_type = "str",
    desc_short = "minimisation algorithm",
    desc = "The optimisation algorithm to use.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "Back-and-forth coordinate descent",
        "Steepest descent",
        "Quasi-Newton BFGS",
        "Newton",
        "Newton-CG",
        "Cauchy point",
        "Dogleg",
        "CG-Steihaug",
        "Exact trust region",
        "Fletcher-Reeves",
        "Polak-Ribiere",
        "Polak-Ribiere +",
        "Hestenes-Stiefel",
        "Simplex",
        "Levenberg-Marquardt",
        "Simulated Annealing"
    ],
    wiz_combo_data = [
        "cd",
        "sd",
        "bfgs",
        "newton",
        "ncg",
        "cauchy",
        "dogleg",
        "steihaug",
        "exact",
        "fr",
        "pr",
        "pr+",
        "hs",
        "simplex",
        "lm",
        "sa"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "line_search",
    py_type = "str",
    desc_short = "line search algorithm",
    desc = "The line search algorithm which will only be used in combination with the line search and conjugate gradient methods.  This will default to the More and Thuente line search.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "Backtracking",
        "Nocedal and Wright interpolation",
        "Nocedal and Wright for the Wolfe conditions",
        "More and Thuente",
        "No line search"
    ],
    wiz_combo_data = [
        "back",
        "nwi",
        "nww",
        "mt",
        "no line"
    ],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "hessian_mod",
    py_type = "str",
    desc_short = "hessian modification",
    desc = "The Hessian modification.  This will only be used in the algorithms which use the Hessian, and defaults to Gill, Murray, and Wright modified Cholesky algorithm.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "Unmodified Hessian",
        "Eigenvalue modification",
        "Cholesky with added multiple of the identity",
        "The Gill, Murray, and Wright modified Cholesky algorithm",
        "The Schnabel and Eskow 1999 algorithm"
    ],
    wiz_combo_data = [
        "no hessian mod",
        "eigen",
        "chol",
        "gmw",
        "se99"
    ],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "hessian_type",
    py_type = "str",
    desc_short = "hessian type",
    desc = "The Hessian type.  This will only be used in a few trust region algorithms, and defaults to BFGS.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "Quasi-Newton BFGS",
        "Newton"
    ],
    wiz_combo_data = [
        "bfgs",
        "newton"
    ],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "func_tol",
    default = 1e-25,
    py_type = "num",
    desc_short = "function tolerance",
    desc = "The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.  The default value is 1e-25."
)
uf.add_keyarg(
    name = "grad_tol",
    py_type = "num",
    desc_short = "gradient tolerance",
    desc = "The gradient tolerance.  Minimisation is terminated if the current gradient value is less than the tolerance.  The default value is None.",
    can_be_none = True
)
uf.add_keyarg(
    name = "max_iter",
    default = 10000000,
    py_type = "int",
    min = 1,
    max = 1000000000,
    desc_short = "maximum number of iterations",
    desc = "The maximum number of iterations.  The default value is 1e7."
)
uf.add_keyarg(
    name = "constraints",
    default = True,
    py_type = "bool",
    desc_short = "constraints flag",
    desc = "A boolean flag specifying whether the parameters should be constrained.  The default is to turn constraints on (constraints=True)."
)
uf.add_keyarg(
    name = "scaling",
    default = True,
    py_type = "bool",
    desc_short = "diagonal scaling flag",
    desc = "The diagonal scaling boolean flag.  The default that scaling is on (scaling=True)."
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will perform an optimisation starting from the current parameter values.  This is only suitable for data pipe types which have target functions and hence support optimisation.")
# Diagonal scaling.
uf.desc.append(Desc_container("Diagonal scaling"))
uf.desc[-1].add_paragraph("Diagonal scaling is the transformation of parameter values such that each value has a similar order of magnitude.  Certain minimisation techniques, for example the trust region methods, perform extremely poorly with badly scaled problems.  In addition, methods which are insensitive to scaling such as Newton minimisation may still benefit due to the minimisation of round off errors.")
uf.desc[-1].add_paragraph("In Model-free analysis for example, if S2 = 0.5, te = 200 ps, and Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18].  Rex is divided by (2 * pi * 600,000,000)**2 to make it field strength independent.  The scaling vector for this model may be something like [1.0, 1e-9, 1/(2 * pi * 6e8)**2].  By dividing the unscaled parameter vector by the scaling vector the scaled parameter vector is [0.5, 0.2, 15.0].  To revert to the original unscaled parameter vector, the scaled parameter vector and scaling vector are multiplied.")
# Minimisation algorithms.
uf.desc.append(Desc_container("Minimisation algorithms"))
uf.desc[-1].add_paragraph("A minimisation function is selected if the minimisation algorithm matches a certain pattern.  Because the python regular expression 'match' statement is used, various strings can be supplied to select the same minimisation algorithm.  Below is a list of the minimisation algorithms available together with the corresponding patterns.")
uf.desc[-1].add_paragraph("This is a short description of python regular expression, for more information, see the regular expression syntax section of the Python Library Reference.  Some of the regular expression syntax used in this function is:")
uf.desc[-1].add_item_list_element("'[]'", "A sequence or set of characters to match to a single character.  For example, '[Nn]ewton' will match both 'Newton' and 'newton'.")
uf.desc[-1].add_item_list_element("'^'", "Match the start of the string.")
uf.desc[-1].add_item_list_element("'$'", "Match the end of the string.  For example, '^[Ll][Mm]$' will match 'lm' and 'LM' but will not match if characters are placed either before or after these strings.")
uf.desc[-1].add_paragraph("To select a minimisation algorithm, use a string which matches one of the following patterns given in the tables.")
uf.desc[-1].add_paragraph("Unconstrained line search methods:")
table = uf_tables.add_table(label="table: min - line search", caption="Minimisation algorithms -- unconstrained line search methods.")
table.add_headings(["Minimisation algorithm", "Patterns"])
table.add_row(["Back-and-forth coordinate descent", "'^[Cc][Dd]$' or '^[Cc]oordinate[ _-][Dd]escent$'"])
table.add_row(["Steepest descent", "'^[Ss][Dd]$' or '^[Ss]teepest[ _-][Dd]escent$'"])
table.add_row(["Quasi-Newton BFGS", "'^[Bb][Ff][Gg][Ss]$'"])
table.add_row(["Newton", "'^[Nn]ewton$'"])
table.add_row(["Newton-CG", "'^[Nn]ewton[ _-][Cc][Gg]$' or '^[Nn][Cc][Gg]$'"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("Unconstrained trust-region methods:")
table = uf_tables.add_table(label="table: min - trust-region", caption="Minimisation algorithms -- unconstrained trust-region methods.")
table.add_headings(["Minimisation algorithm", "Patterns"])
table.add_row(["Cauchy point", "'^[Cc]auchy'"])
table.add_row(["Dogleg", "'^[Dd]ogleg'"])
table.add_row(["CG-Steihaug", "'^[Cc][Gg][-_ ][Ss]teihaug' or '^[Ss]teihaug'"])
table.add_row(["Exact trust region", "'^[Ee]xact'"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("Unconstrained conjugate gradient methods:")
table = uf_tables.add_table(label="table: min - conjugate gradient", caption="Minimisation algorithms -- unconstrained conjugate gradient methods.")
table.add_headings(["Minimisation algorithm", "Patterns"])
table.add_row(["Fletcher-Reeves", "'^[Ff][Rr]$' or '^[Ff]letcher[-_ ][Rr]eeves$'"])
table.add_row(["Polak-Ribiere", "'^[Pp][Rr]$' or '^[Pp]olak[-_ ][Rr]ibiere$'"])
table.add_row(["Polak-Ribiere +", "'^[Pp][Rr]\+$' or '^[Pp]olak[-_ ][Rr]ibiere\+$'"])
table.add_row(["Hestenes-Stiefel", "'^[Hh][Ss]$' or '^[Hh]estenes[-_ ][Ss]tiefel$'"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("Miscellaneous unconstrained methods:")
table = uf_tables.add_table(label="table: min - misc", caption="Minimisation algorithms -- miscellaneous unconstrained methods.")
table.add_headings(["Minimisation algorithm", "Patterns"])
table.add_row(["Simplex", "'^[Ss]implex$'"])
table.add_row(["Levenberg-Marquardt", "'^[Ll][Mm]$' or '^[Ll]evenburg-[Mm]arquardt$'"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("Global minimisation methods:")
table = uf_tables.add_table(label="table: min - global", caption="Minimisation algorithms -- global minimisation methods.")
table.add_headings(["Minimisation algorithm", "Patterns"])
table.add_row(["Simulated Annealing", "'^[Ss][Aa]$' or '^[Ss]imulated [Aa]nnealing$'"])
uf.desc[-1].add_table(table.label)
# Minimisation options.
uf.desc.append(Desc_container("Minimisation options"))
uf.desc[-1].add_paragraph("The minimisation options can be given in any order.")
uf.desc[-1].add_paragraph("Line search algorithms.  These are used in the line search methods and the conjugate gradient methods.  The default is the Backtracking line search.  The algorithms are:")
table = uf_tables.add_table(label="table: min sub-algor - line search", caption="Minimisation sub-algorithms -- line search algorithms.")
table.add_headings(["Line search algorithm", "Patterns"])
table.add_row(["Backtracking line search", "'^[Bb]ack'"])
table.add_row(["Nocedal and Wright interpolation based line search", "'^[Nn][Ww][Ii]' or '^[Nn]ocedal[ _][Ww]right[ _][Ii]nt'"])
table.add_row(["Nocedal and Wright line search for the Wolfe conditions", "'^[Nn][Ww][Ww]' or '^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe'"])
table.add_row(["More and Thuente line search", "'^[Mm][Tt]' or '^[Mm]ore[ _][Tt]huente$'"])
table.add_row(["No line search", "'^[Nn]o [Ll]ine [Ss]earch$'"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("Hessian modifications.  These are used in the Newton, Dogleg, and Exact trust region algorithms:")
table = uf_tables.add_table(label="table: min sub-algor - Hessian mod", caption="Minimisation sub-algorithms -- Hessian modifications.")
table.add_headings(["Hessian modification", "Patterns"])
table.add_row(["Unmodified Hessian", "'^[Nn]o [Hh]essian [Mm]od'"])
table.add_row(["Eigenvalue modification", "'^[Ee]igen'"])
table.add_row(["Cholesky with added multiple of the identity", "'^[Cc]hol'"])
table.add_row(["The Gill, Murray, and Wright modified Cholesky algorithm", "'^[Gg][Mm][Ww]$'"])
table.add_row(["The Schnabel and Eskow 1999 algorithm", "'^[Ss][Ee]99'"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("Hessian type, these are used in a few of the trust region methods including the Dogleg and Exact trust region algorithms.  In these cases, when the Hessian type is set to Newton, a Hessian modification can also be supplied as above.  The default Hessian type is Newton, and the default Hessian modification when Newton is selected is the GMW algorithm:")
table = uf_tables.add_table(label="table: min sub-algor - Hessian type", caption="Minimisation sub-algorithms -- Hessian type.")
table.add_headings(["Hessian type", "Patterns"])
table.add_row(["Quasi-Newton BFGS", "'^[Bb][Ff][Gg][Ss]$'"])
table.add_row(["Newton", "'^[Nn]ewton$'"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("For Newton minimisation, the default line search algorithm is the More and Thuente line search, while the default Hessian modification is the GMW algorithm.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To apply Newton minimisation together with the GMW81 Hessian modification algorithm, the More and Thuente line search algorithm, a function tolerance of 1e-25, no gradient tolerance, a maximum of 10,000,000 iterations, constraints turned on to limit parameter values, and have normal printout, type any combination of:")
uf.desc[-1].add_prompt("relax> minimise.execute('newton')")
uf.desc[-1].add_prompt("relax> minimise.execute('Newton')")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', 'gmw')")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', 'mt')")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', 'gmw', 'mt')")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', 'mt', 'gmw')")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', func_tol=1e-25)")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', func_tol=1e-25, grad_tol=None)")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', max_iter=1e7)")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', constraints=True, max_iter=1e7)")
uf.desc[-1].add_prompt("relax> minimise.execute('newton', verbosity=1)")
uf.desc[-1].add_paragraph("To use constrained Simplex minimisation with a maximum of 5000 iterations, type:")
uf.desc[-1].add_prompt("relax> minimise.execute('simplex', constraints=True, max_iter=5000)")
uf.backend = minimise.minimise
uf.menu_text = "&execute"
uf.gui_icon = "relax.rosenbrock"
uf.wizard_height_desc = 300
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'minimise.png'


# The minimise.grid_search user function.
uf = uf_info.add_uf('minimise.grid_search')
uf.title = "Perform a grid search to find an initial non-biased parameter set for optimisation."
uf.title_short = "Grid search optimisation."
uf.display = True
uf.add_keyarg(
    name = "lower",
    py_type = "num_list",
    desc_short = "lower bounds",
    desc = "An array of the lower bound parameter values for the grid search.  The length of the array should be equal to the number of parameters in the model.",
    can_be_none = True
)
uf.add_keyarg(
    name = "upper",
    py_type = "num_list",
    desc_short = "upper bounds",
    desc = "An array of the upper bound parameter values for the grid search.  The length of the array should be equal to the number of parameters in the model.",
    can_be_none = True
)
uf.add_keyarg(
    name = "inc",
    default = 21,
    py_type = "int_or_int_list",
    desc_short = "incrementation value",
    desc = "The number of increments to search over.  If a single integer is given then the number of increments will be equal in all dimensions.  Different numbers of increments in each direction can be set if 'inc' is set to an array of integers of length equal to the number of parameters.",
    none_elements = False
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1."
)
uf.add_keyarg(
    name = "constraints",
    default = True,
    py_type = "bool",
    desc_short = "constraints flag",
    desc = "A boolean flag specifying whether the parameters should be constrained.  The default is to turn constraints on (constraints=True)."
)
uf.add_keyarg(
    name = "skip_preset",
    default = True,
    py_type = "bool",
    desc_short = "skip preset parameter flag",
    desc = "This argument, when True, allows any parameter which already has a value set to be skipped in the grid search."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The optimisation of a mathematical model normally consists of two parts - a coarse grid search across the parameter space to find an initial set of parameter values followed by the use of a high precision optimisation algorithm to exactly find the local or global solution.  The grid search is an essential tool as it allows a non-biased initial optimisation position to be found.  It avoids the statistical bias and preconditioning introduced by using a self chosen initial parameter set.  The high computational cost of the grid search is almost always favourable to the statistical bias of a user defined starting position.")
uf.desc[-1].add_paragraph("The region of the parameter space that the grid search covers is defined by the lower and upper grid bounds.  These will generally default to the entire parameter space except for when the parameter is non-bounded, for example a 3D position in the PDB space.  This user function will print out the grid bounds used and, if the default bounds are deemed to be insufficient, then the lower, upper or both bounds can supplied.  This only works if all active models have the same parameters.  The coarseness or fineness of the grid is defined by the number of increments to search across between the bounds.  For an alternative to using large numbers of increments, see the zooming grid search.")
uf.desc[-1].add_paragraph("It is possible to decrease the dimensionality of the grid search, and hence drop the computational cost by orders of magnitude, if certain parameter values are know a priori.  For example if the values are determined via a different experiment.  Such parameters can be set with the value setting user function.  Then, when the skip preset flag is set, these parameters will be skipped in the grid search.  This feature should not be abused and statistical bias should be avoided at all cost.")
uf.backend = minimise.grid_search
uf.menu_text = "&grid_search"
uf.gui_icon = "relax.grid_search"
uf.wizard_height_desc = 370
uf.wizard_size = (1000, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'minimise.png'


# The minimise.grid_zoom user function.
uf = uf_info.add_uf('minimise.grid_zoom')
uf.title = "Activate the zooming grid search by setting the zoom level."
uf.title_short = "Zooming grid search activation."
uf.add_keyarg(
    name = "level",
    default = 0,
    py_type = "num",
    desc_short = "zoom level",
    desc = "The zooming grid search level.  This can be any number, positive or negative."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The optimisation of a mathematical model normally consists of two parts - a coarse grid search to find an initial set of parameter values followed by the use of a high precision optimisation algorithm to exactly find the local or global solution.  But in certain situations, for example where a parallelised grid search is advantageous, a finer grid may be desired.  The zooming grid search provides a more efficient alternative to simply increasing the number of increments used in the initial grid search.  Note that in most situations, standard optimisation algorithms will be by far computationally less expensive.")
uf.desc[-1].add_paragraph("The zooming grid search can be activated via this user function.  After setting the desired zoom level, the original grid search user function should be called again.  The zoom level is used to decrease the total area of the grid search.  The grid width for each dimension of the parameter space will be divided by 2**zoom_level.  So a level of 1 will halve all dimensions, a level of 2 will quarter the widths, a level of 3 will be an eighth of the widths, etc.")
uf.desc[-1].add_paragraph("The zooming algorithm proceeds as follows.  The new zoomed grid will be centred at the current parameter values.  However if the new grid is outside of the bounds of the original grid, the entire grid will be translated so that it lies entirely within the original bounds.  This is to avoid grid points lying within undefined regions of the space.  An exception is when the zoom factor is negative, hence the new grid will be larger than the original.")
uf.desc[-1].add_paragraph("An example of using the zooming grid search is to first perform a standard initial grid search, then set the zoom level to 1 and perform a second grid search.  Continue for zoom levels 2, 3, etc. until the desired fineness is obtained.  Note that convergence is not guaranteed - as the zoom level is increased to infinity, the parameter values do not necessarily converge to the local minimum.  Therefore performing standard optimisation is recommended after completing a zooming grid search. ")
uf.backend = minimise.grid_zoom
uf.menu_text = "&grid_zoom"
uf.gui_icon = "oxygen.actions.zoom-in"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'minimise.png'
