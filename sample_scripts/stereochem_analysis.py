"""Configuration for the stereochem_analysis.py script.

All user settings should be placed here.

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

# Stage of analysis (see the docstring above for the options).
STAGE = 5

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

# NOE file.
NOE_FILE = "noes"

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
