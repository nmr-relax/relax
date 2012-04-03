###############################################################################
#                                                                             #
# Copyright (C) 2004-2010 Edward d'Auvergne                                   #
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

"""Script for black-box model-free analysis.

This script is designed for those who appreciate black-boxes or those who appreciate complex code.  Importantly data at multiple magnetic field strengths is essential for this analysis.  The script will need to be heavily tailored to the molecule in question by changing the variables just below this documentation.  If you would like to change how model-free analysis is performed, the code in the class Main can be changed as needed.  For a description of object-oriented coding in python using classes, functions/methods, self, etc., see the python tutorial.

If you have obtained this script without the program relax, please visit http://www.nmr-relax.com.


References
==========

The model-free optimisation methodology herein is that of:

    d'Auvergne, E. J. and Gooley, P. R. (2008b). Optimisation of NMR dynamic models II. A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor. J. Biomol. NMR, 40(2), 121-133

Other references for features of this script include model-free model selection using Akaike's Information Criterion:

    d'Auvergne, E. J. and Gooley, P. R. (2003). The use of model selection in the model-free analysis of protein dynamics. J. Biomol. NMR, 25(1), 25-39.

The elimination of failed model-free models and Monte Carlo simulations:

    d'Auvergne, E. J. and Gooley, P. R. (2006). Model-free model elimination: A new step in the model-free dynamic analysis of NMR relaxation data. J. Biomol. NMR, 35(2), 117-135.

Significant model-free optimisation improvements:

    d'Auvergne, E. J. and Gooley, P. R. (2008a). Optimisation of NMR dynamic models I. Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces. J. Biomol. NMR, 40(2), 107-109.

Rather than searching for the lowest chi-squared value, this script searches for the model with the lowest AIC criterion.  This complex multi-universe, multi-dimensional search is formulated using set theory as the universal solution:

    d'Auvergne, E. J. and Gooley, P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. 3(7), 483-494.

The basic three references for the original and extended model-free theories are:

    Lipari, G. and Szabo, A. (1982a). Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules I. Theory and range of validity. J. Am. Chem. Soc., 104(17), 4546-4559.

    Lipari, G. and Szabo, A. (1982b). Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules II. Analysis of experimental results. J. Am. Chem. Soc., 104(17), 4559-4570.

    Clore, G. M., Szabo, A., Bax, A., Kay, L. E., Driscoll, P. C., and Gronenborn, A.M. (1990). Deviations from the simple 2-parameter model-free approach to the interpretation of N-15 nuclear magnetic-relaxation of proteins. J. Am. Chem. Soc., 112(12), 4989-4991.


How to use this script
======================

The value of the variable DIFF_MODEL will determine the behaviour of this script.  The five diffusion models used in this script are:

    Model I   (MI)   - Local tm.
    Model II  (MII)  - Sphere.
    Model III (MIII) - Prolate spheroid.
    Model IV  (MIV)  - Oblate spheroid.
    Model V   (MV)   - Ellipsoid.

Model I must be optimised prior to any of the other diffusion models, while the Models II to V can be optimised in any order.  To select the various models, set the variable DIFF_MODEL to the following strings:

    MI   - 'local_tm'
    MII  - 'sphere'
    MIII - 'prolate'
    MIV  - 'oblate'
    MV   - 'ellipsoid'

This approach has the advantage of eliminating the need for an initial estimate of a global diffusion tensor and removing all the problems associated with the initial estimate.

It is important that the number of parameters in a model does not exceed the number of relaxation data sets for that spin.  If this is the case, the list of models in the MF_MODELS and LOCAL_TM_MODELS variables will need to be trimmed.


Model I - Local tm
~~~~~~~~~~~~~~~~~~

This will optimise the diffusion model whereby all spin of the molecule have a local tm value, i.e. there is no global diffusion tensor.  This model needs to be optimised prior to optimising any of the other diffusion models.  Each spin is fitted to the multiple model-free models separately, where the parameter tm is included in each model.

AIC model selection is used to select the models for each spin.


Model II - Sphere
~~~~~~~~~~~~~~~~~

This will optimise the isotropic diffusion model.  Multiple steps are required, an initial optimisation of the diffusion tensor, followed by a repetitive optimisation until convergence of the diffusion tensor.  Each of these steps requires this script to be rerun. For the initial optimisation, which will be placed in the directory './sphere/init/', the following steps are used:

The model-free models and parameter values for each spin are set to those of diffusion model MI.

The local tm parameter is removed from the models.

The model-free parameters are fixed and a global spherical diffusion tensor is minimised.


For the repetitive optimisation, each minimisation is named from 'round_1' onwards.  The initial 'round_1' optimisation will extract the diffusion tensor from the results file in './sphere/init/', and the results will be placed in the directory './sphere/round_1/'.  Each successive round will take the diffusion tensor from the previous round.  The following steps are used:

The global diffusion tensor is fixed and the multiple model-free models are fitted to each spin.

AIC model selection is used to select the models for each spin.

All model-free and diffusion parameters are allowed to vary and a global optimisation of all parameters is carried out.


Model III - Prolate spheroid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da >= 0 is used.  The base directory containing all the results is './prolate/'.


Model IV - Oblate spheroid
~~~~~~~~~~~~~~~~~~~~~~~~~~

The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da <= 0 is used.  The base directory containing all the results is './oblate/'.


Model V - Ellipsoid
~~~~~~~~~~~~~~~~~~~

The methods used are identical to those of diffusion model MII, except that a fully anisotropic diffusion tensor is used (also known as rhombic or asymmetric diffusion).  The base directory is './ellipsoid/'.



Final run
~~~~~~~~~

Once all the diffusion models have converged, the final run can be executed.  This is done by setting the variable DIFF_MODEL to 'final'.  This consists of two steps, diffusion tensor model selection, and Monte Carlo simulations.  Firstly AIC model selection is used to select between the diffusion tensor models.  Monte Carlo simulations are then run solely on this selected diffusion model.  Minimisation of the model is bypassed as it is assumed that the model is already fully optimised (if this is not the case the final run is not yet appropriate).

The final black-box model-free results will be placed in the file 'final/results'.
"""

# This is a small test script by Sebastian Morin.

# Python module imports.
from os import getcwd, listdir, sep
from re import search
from string import lower

# relax module imports.
from auto_analyses.dauvergne_protocol import dAuvergne_protocol


# User variables.
#################

# The diffusion model.
DIFF_MODEL = 'prolate'

# The model-free models (do not change these unless absolutely necessary).
MF_MODELS = ['m1', 'm8']
LOCAL_TM_MODELS = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']

# The PDB file (set this to None if no structure is available).
PDB_FILE = 'struc.pdb'

# The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
SEQ_ARGS = ['seq.seq', None, None, 1, 2, None, 3, None]

# The heteronucleus atom name corresponding to that of the PDB file (used if the spin name is not in the sequence data).
HET_NAME = 'N'

# The relaxation data (data type, frequency label, frequency, file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col, sep).  These are the arguments to the relax_data.read() user function, please see the documentation for that function for more information.
RELAX_DATA = [['R1',  '800', 799.737 * 1e6, 'R1-800',  None, None, 1, 2, None, None, 3, 4, None],
              ['NOE',  '800', 799.737 * 1e6, 'noe-800', None, None, 1, 2, None, None, 3, 4, None],
              ['R1',  '600', 599.737 * 1e6, 'R1-600',  None, None, 1, 2, None, None, 3, 4, None],
              ['R2',  '600', 599.737 * 1e6, 'R2-600',  None, None, 1, 2, None, None, 3, 4, None],
              ['NOE', '600', 599.737 * 1e6, 'noe-600', None, None, 1, 2, None, None, 3, 4, None],
              ['R1',  '500', 499.719 * 1e6, 'R1-500',  None, None, 1, 2, None, None, 3, 4, None],
              ['R2',  '500', 499.719 * 1e6, 'R2-500',  None, None, 1, 2, None, None, 3, 4, None],
              ['NOE', '500', 499.719 * 1e6, 'noe-500', None, None, 1, 2, None, None, 3, 4, None]
]

# The file containing the list of unresolved spins to exclude from the analysis (set this to None if no spin is to be excluded).
UNRES = None

# A file containing a list of spins which can be dynamically excluded at any point within the analysis (when set to None, this variable is not used).
EXCLUDE = None

# The bond length, CSA values, heteronucleus type, and proton type.
BOND_LENGTH = 1.02 * 1e-10
CSA = -200 * 1e-6
HETNUC = '15N'
PROTON = '1H'

# The grid search size (the number of increments per dimension).
GRID_INC = 5

# The optimisation technique.
MIN_ALGOR = 'newton'

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 500

# Automatic looping over all rounds until convergence (must be a boolean value of True or False).
CONV_LOOP = False


# Execution (do not change!).
dAuvergne_protocol(diff_model=DIFF_MODEL, mf_models=MF_MODELS, local_tm_models=LOCAL_TM_MODELS, pdb_file=PDB_FILE, seq_args=SEQ_ARGS, het_name=HET_NAME, relax_data=RELAX_DATA, unres=UNRES, exclude=EXCLUDE, bond_length=BOND_LENGTH, csa=CSA, hetnuc=HETNUC, proton=PROTON, grid_inc=GRID_INC, min_algor=MIN_ALGOR, mc_num=MC_NUM, conv_loop=CONV_LOOP)
