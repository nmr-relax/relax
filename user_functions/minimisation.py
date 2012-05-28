###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""The minimisation user function definitions."""

# Python module imports.
from string import split

# relax module imports.
from generic_fns import minimise
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The calc user function.
uf = uf_info.add_uf('calc')
uf.title = "Calculate the function value."
uf.title_short = "Function value calculation."
uf.display = True
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1."
)
uf.desc = """
This will call the target function for the analysis type associated with the current data pipe using the current parameter values.  This can be used to find, for example, the chi-squared value for different parameter values.
"""
uf.backend = minimise.calc
uf.menu_text = "&calc"
uf.gui_icon = "relax.minimise"
uf.wizard_image = WIZARD_IMAGE_PATH + 'minimise.png'


# The grid_search user function.
uf = uf_info.add_uf('grid_search')
uf.title = "Perform a grid search."
uf.title_short = "Grid search."
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
    desc = "The number of increments to search over.  If a single integer is given then the number of increments will be equal in all dimensions.  Different numbers of increments in each direction can be set if 'inc' is set to an array of integers of length equal to the number of parameters."
)

uf.add_keyarg(
    name = "constraints",
    default = True,
    py_type = "bool",
    desc_short = "constraints flag",
    desc = "A boolean flag specifying whether the parameters should be constrained.  The default is to turn constraints on (constraints=True)."
)

uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1."
)
uf.desc = """
This will perform a grid search across the parameter space.
"""
uf.backend = minimise.grid_search
uf.menu_text = "&grid_search"
uf.gui_icon = "relax.grid_search"
uf.wizard_size = (800, 500)


# The minimise user function.
uf = uf_info.add_uf('minimise')
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
    desc_short = "maximum number of iterations",
    desc = "The maximum number of iterations.  The default value is 1e7.",
    can_be_none = True
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
uf.desc = """
This will perform an optimisation starting from the current parameter values.  This is only suitable for data pipe types which have target functions and hence support optimisation.
"""
uf.additional = [["Diagonal scaling", """
Diagonal scaling is the transformation of parameter values such that each value has a similar order of magnitude.  Certain minimisation techniques, for example the trust region methods, perform extremely poorly with badly scaled problems.  In addition, methods which are insensitive to scaling such as Newton minimisation may still benefit due to the minimisation of round off errors.

In Model-free analysis for example, if S2 = 0.5, te = 200 ps, and Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18].  Rex is divided by (2 * pi * 600,000,000)**2 to make it field strength independent.  The scaling vector for this model may be something like [1.0, 1e-9, 1/(2 * pi * 6e8)**2].  By dividing the unscaled parameter vector by the scaling vector the scaled parameter vector is [0.5, 0.2, 15.0].  To revert to the original unscaled parameter vector, the scaled parameter vector and scaling vector are multiplied.
"""],
["Minimisation algorithms", """
A minimisation function is selected if the minimisation algorithm argument, which should be a string, matches a certain pattern.  Because the python regular expression 'match' statement is used, various strings can be supplied to select the same minimisation algorithm.  Below is a list of the minimisation algorithms available together with the corresponding patterns.

This is a short description of python regular expression, for more information, see the regular expression syntax section of the Python Library Reference.  Some of the regular expression syntax used in this function is:

    - '[]':  A sequence or set of characters to match to a single character.  For example, '[Nn]ewton' will match both 'Newton' and 'newton'.

    - '^':  Match the start of the string.

    - '$':  Match the end of the string.  For example, '^[Ll][Mm]$' will match 'lm' and 'LM' but will not match if characters are placed either before or after these strings.

To select a minimisation algorithm, set the argument to a string which matches the given pattern.


Unconstrained line search methods::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Back-and-forth coordinate descent | '^[Cc][Dd]$' or '^[Cc]oordinate[ _-][Dd]escent$'    |
    |                                   |                                                     |
    | Steepest descent                  | '^[Ss][Dd]$' or '^[Ss]teepest[ _-][Dd]escent$'      |
    |                                   |                                                     |
    | Quasi-Newton BFGS                 | '^[Bb][Ff][Gg][Ss]$'                                |
    |                                   |                                                     |
    | Newton                            | '^[Nn]ewton$'                                       |
    |                                   |                                                     |
    | Newton-CG                         | '^[Nn]ewton[ _-][Cc][Gg]$' or '^[Nn][Cc][Gg]$'      |
    |___________________________________|_____________________________________________________|


Unconstrained trust-region methods::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Cauchy point                      | '^[Cc]auchy'                                        |
    |                                   |                                                     |
    | Dogleg                            | '^[Dd]ogleg'                                        |
    |                                   |                                                     |
    | CG-Steihaug                       | '^[Cc][Gg][-_ ][Ss]teihaug' or '^[Ss]teihaug'       |
    |                                   |                                                     |
    | Exact trust region                | '^[Ee]xact'                                         |
    |___________________________________|_____________________________________________________|


Unconstrained conjugate gradient methods::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Fletcher-Reeves                   | '^[Ff][Rr]$' or '^[Ff]letcher[-_ ][Rr]eeves$'       |
    |                                   |                                                     |
    | Polak-Ribiere                     | '^[Pp][Rr]$' or '^[Pp]olak[-_ ][Rr]ibiere$'         |
    |                                   |                                                     |
    | Polak-Ribiere +                   | '^[Pp][Rr]\+$' or '^[Pp]olak[-_ ][Rr]ibiere\+$'     |
    |                                   |                                                     |
    | Hestenes-Stiefel                  | '^[Hh][Ss]$' or '^[Hh]estenes[-_ ][Ss]tiefel$'      |
    |___________________________________|_____________________________________________________|


Miscellaneous unconstrained methods::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Simplex                           | '^[Ss]implex$'                                      |
    |                                   |                                                     |
    | Levenberg-Marquardt               | '^[Ll][Mm]$' or '^[Ll]evenburg-[Mm]arquardt$'       |
    |___________________________________|_____________________________________________________|


Global minimisation methods::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Minimisation algorithm            | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Simulated Annealing               | '^[Ss][Aa]$' or '^[Ss]imulated [Aa]nnealing$'       |
    |___________________________________|_____________________________________________________|
"""],
["Minimisation options", """
The minimisation options can be given in any order.


Line search algorithms.  These are used in the line search methods and the conjugate gradient methods.  The default is the Backtracking line search.  The algorithms are::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Line search algorithm             | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Backtracking line search          | '^[Bb]ack'                                          |
    |                                   |                                                     |
    | Nocedal and Wright interpolation  | '^[Nn][Ww][Ii]' or                                  |
    | based line search                 | '^[Nn]ocedal[ _][Ww]right[ _][Ii]nt'                |
    |                                   |                                                     |
    | Nocedal and Wright line search    | '^[Nn][Ww][Ww]' or                                  |
    | for the Wolfe conditions          | '^[Nn]ocedal[ _][Ww]right[ _][Ww]olfe'              |
    |                                   |                                                     |
    | More and Thuente line search      | '^[Mm][Tt]' or '^[Mm]ore[ _][Tt]huente$'            |
    |                                   |                                                     |
    | No line search                    | '^[Nn]o [Ll]ine [Ss]earch$'                         |
    |___________________________________|_____________________________________________________|



Hessian modifications.  These are used in the Newton, Dogleg, and Exact trust region algorithms::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Hessian modification              | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Unmodified Hessian                | '^[Nn]o [Hh]essian [Mm]od'                          |
    |                                   |                                                     |
    | Eigenvalue modification           | '^[Ee]igen'                                         |
    |                                   |                                                     |
    | Cholesky with added multiple of   | '^[Cc]hol'                                          |
    | the identity                      |                                                     |
    |                                   |                                                     |
    | The Gill, Murray, and Wright      | '^[Gg][Mm][Ww]$'                                    |
    | modified Cholesky algorithm       |                                                     |
    |                                   |                                                     |
    | The Schnabel and Eskow 1999       | '^[Ss][Ee]99'                                       |
    | algorithm                         |                                                     |
    |___________________________________|_____________________________________________________|



Hessian type, these are used in a few of the trust region methods including the Dogleg and Exact trust region algorithms.  In these cases, when the Hessian type is set to Newton, a Hessian modification can also be supplied as above.  The default Hessian type is Newton, and the default Hessian modification when Newton is selected is the GMW algorithm::
    ___________________________________________________________________________________________
    |                                   |                                                     |
    | Hessian type                      | Patterns                                            |
    |___________________________________|_____________________________________________________|
    |                                   |                                                     |
    | Quasi-Newton BFGS                 | '^[Bb][Ff][Gg][Ss]$'                                |
    |                                   |                                                     |
    | Newton                            | '^[Nn]ewton$'                                       |
    |___________________________________|_____________________________________________________|


For Newton minimisation, the default line search algorithm is the More and Thuente line search, while the default Hessian modification is the GMW algorithm.
"""]
]
uf.prompt_examples = """
To apply Newton minimisation together with the GMW81 Hessian modification algorithm, the
More and Thuente line search algorithm, a function tolerance of 1e-25, no gradient
tolerance, a maximum of 10,000,000 iterations, constraints turned on to limit parameter
values, and have normal printout, type any combination of:

relax> minimise('newton')
relax> minimise('Newton')
relax> minimise('newton', 'gmw')
relax> minimise('newton', 'mt')
relax> minimise('newton', 'gmw', 'mt')
relax> minimise('newton', 'mt', 'gmw')
relax> minimise('newton', func_tol=1e-25)
relax> minimise('newton', func_tol=1e-25, grad_tol=None)
relax> minimise('newton', max_iter=1e7)
relax> minimise('newton', constraints=True, max_iter=1e7)
relax> minimise('newton', verbosity=1)

To use constrained Simplex minimisation with a maximum of 5000 iterations, type:

relax> minimise('simplex', constraints=True, max_iter=5000)
"""
uf.backend = minimise.minimise
uf.menu_text = "&minimise"
uf.gui_icon = "relax.minimise"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 900)
uf.wizard_image = WIZARD_IMAGE_PATH + 'minimise.png'
