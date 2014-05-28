###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Variables for the wxPython file selector wildcard filters."""


# Grace wildcards.
WILDCARD_GRACE_ALL = \
    "Grace files (*.agr)|*.agr;*.AGR|"+\
    "Gzipped Grace files (*.agr.gz)|*.agr.gz;*.AGR.gz;*.AGR.GZ|"+\
    "All files (*)|*"

# MOLMOL wildcards.
WILDCARD_MOLMOL_MACRO = "Molmol macro files (*.pml)|*.pml;*.PML"

# PyMOL wildcards.
WILDCARD_PYMOL_MACRO = "PyMOL macro files (*.pml)|*.pml;*.PML"

# relax script, results and save files.
WILDCARD_RELAX_RESULT = \
    "Bzipped relax results files (*.bz2)|*.bz2;*.BZ2|"+\
    "Gzipped relax results files (*.gz)|*.gz;*.GZ|"+\
    "Uncompressed relax results files (*)|*"
WILDCARD_RELAX_SAVE = \
    "Bzipped relax state files (*.bz2)|*.bz2;*.BZ2|"+\
    "Gzipped relax state files (*.gz)|*.gz;*.GZ|"+\
    "Uncompressed relax state files (*)|*"
WILDCARD_RELAX_SCRIPT = "relax scripts (*.py)|*.py;*.PY"

# Spectral data.
WILDCARD_SPECTRUM_PEAKLIST = \
    "Sparky peak lists (*.list)|*.list;*.LIST|"+\
    "XEasy peak lists (*.text)|*.text;*.TEXT|"+\
    "NMRView peak lists (*.xpk)|*.xpk;*.XPK|"+\
    "NMRPipe seriesTab peak lists (*.ser)|*.ser;*.SER|"+\
    "All files (*)|*"

# 3D structure related wildcards.
WILDCARD_STRUCT_GAUSSIAN_ALL = \
    "Gaussian log files (*.log)|*.log;*.LOG|"+\
    "Bzipped Gaussian log files (*.log.bz2)|*.log.bz2;*.LOG.bz2;*.LOG.BZ2|"+\
    "Gzipped Gaussian log files (*.log.gz)|*.log.gz;*.LOG.gz;*.LOG.GZ|"+\
    "All files (*)|*"
WILDCARD_STRUCT_PDB = \
    "PDB files (*.pdb)|*.pdb;*.PDB|"+\
    "All files (*)|*"
WILDCARD_STRUCT_PDB_ALL = \
    "PDB files (*.pdb)|*.pdb;*.PDB|"+\
    "Bzipped PDB files (*.pdb.bz2)|*.pdb.bz2;*.PDB.bz2;*.PDB.BZ2|"+\
    "Gzipped PDB files (*.pdb.gz)|*.pdb.gz;*.PDB.gz;*.PDB.GZ|"+\
    "All files (*)|*"
WILDCARD_STRUCT_XYZ_ALL = \
    "XYZ files (*.xyz)|*.xyz;*.XYZ|"+\
    "Bzipped XYZ files (*.xyz.bz2)|*.xyz.bz2;*.XYZ.bz2;*.XYZ.BZ2|"+\
    "Gzipped XYZ files (*.xyz.gz)|*.xyz.gz;*.XYZ.gz;*.XYZ.GZ|"+\
    "All files (*)|*"
