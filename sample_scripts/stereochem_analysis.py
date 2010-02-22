###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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

"""Script for the determination of relative stereochemistry.

The analysis is preformed by using multiple ensembles of structures, randomly sampled from a given
set of structures.  The discrimination is performed by comparing the sets of ensembles using NOE
violations and RDC Q-factors.

This script is split into multiple stages:

    1.  The random sampling of the snapshots to generate the N ensembles (NUM_ENS, usually 10,000 to
    100,000) of M members (NUM_MODELS, usually ~10).  The original snapshot files are expected to be
    named the SNAPSHOT_DIR + CONFIG + a number from SNAPSHOT_MIN to SNAPSHOT_MAX + ".pdb", e.g.
    "snapshots/R647.pdb".  The ensembles will be placed into the "ensembles" directory.

    2.  The NOE violation analysis.

    3.  The superimposition of ensembles.  For each ensemble, Molmol is used for superimposition
    using the fit to first algorithm.  The superimposed ensembles will be placed into the
    "ensembles_superimposed" directory.  This stage is not necessary for the NOE analysis.

    4.  The RDC Q-factor analysis.

    5.  Generation of Grace graphs.
"""

# relax module imports.
from auto_analyses.stereochem_analysis import Stereochem_analysis


# Stage of analysis (see the docstring above for the options).
STAGE = 1

# Number of ensembles.
NUM_ENS = 100000

# Ensemble size.
NUM_MODELS = 10

# Configurations.
CONFIGS = ["R", "S"]

# Snapshot directories (corresponding to CONFIGS).
SNAPSHOT_DIR = ["snapshots", "snapshots"]

# Min and max number of the snapshots (corresponding to CONFIGS).
SNAPSHOT_MIN = [0, 0]
SNAPSHOT_MAX = [76, 71]

# Pseudo-atoms.
PSEUDO = [
["Q7", ["@H16", "@H17", "@H18"]],
["Q9", ["@H20", "@H21", "@H22"]],
["Q10", ["@H23", "@H24", "@H25"]]
]

# NOE info.
NOE_FILE = "noes"
NOE_NORM = 50 * 4**2    # The NOE normalisation factor (sum of all NOEs squared).

# RDC file info.
RDC_NAME = "PAN"
RDC_FILE = "pan_rdcs"
RDC_SPIN_ID_COL = 1
RDC_MOL_NAME_COL = None
RDC_RES_NUM_COL = None
RDC_RES_NAME_COL = None
RDC_SPIN_NUM_COL = None
RDC_SPIN_NAME_COL = None
RDC_DATA_COL = 2
RDC_ERROR_COL = None

# Bond length.
BOND_LENGTH = 1.117 * 1e-10

# Log file output (only for certain stages).
LOG = True

# Number of buckets for the distribution plots.
BUCKET_NUM = 200

# Distribution plot limits.
LOWER_LIM_NOE = 0.0
UPPER_LIM_NOE = 600.0
LOWER_LIM_RDC = 0.0
UPPER_LIM_RDC = 1.0


# Set up and code execution.
analysis = Stereochem_analysis(
    stage=STAGE,
    num_ens=NUM_ENS,
    num_models=NUM_MODELS,
    configs=CONFIGS,
    snapshot_dir=SNAPSHOT_DIR,
    snapshot_min=SNAPSHOT_MIN,
    snapshot_max=SNAPSHOT_MAX,
    pseudo=PSEUDO,
    noe_file=NOE_FILE,
    noe_norm=NOE_NORM,
    rdc_name=RDC_NAME,
    rdc_file=RDC_FILE,
    rdc_spin_id_col=RDC_SPIN_ID_COL,
    rdc_mol_name_col=RDC_MOL_NAME_COL,
    rdc_res_num_col=RDC_RES_NUM_COL,
    rdc_res_name_col=RDC_RES_NAME_COL,
    rdc_spin_num_col=RDC_SPIN_NUM_COL,
    rdc_spin_name_col=RDC_SPIN_NAME_COL,
    rdc_data_col=RDC_DATA_COL,
    rdc_error_col=RDC_ERROR_COL,
    bond_length=BOND_LENGTH,
    log=LOG,
    bucket_num=BUCKET_NUM,
    lower_lim_noe=LOWER_LIM_NOE,
    upper_lim_noe=UPPER_LIM_NOE,
    lower_lim_rdc=LOWER_LIM_RDC,
    upper_lim_rdc=UPPER_LIM_RDC
)
analysis.run()
