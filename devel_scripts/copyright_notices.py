#! /usr/bin/env python3

###############################################################################
#                                                                             #
# Copyright (C) 2017 Edward d'Auvergne                                        #
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

"""Recursively check all files for FSF copyright notice compliance.

This standard is from https://www.gnu.org/prep/maintain/html_node/Copyright-Notices.html, and
reproduced here for a permanent record:

6.5 Copyright Notices
=====================

You should maintain a proper copyright notice and a license notice in each nontrivial file in the
package. (Any file more than ten lines long is nontrivial for this purpose.) This includes header
files and interface definitions for building or running the program, documentation files, and any
supporting files. If a file has been explicitly placed in the public domain, then instead of a
copyright notice, it should have a notice saying explicitly that it is in the public domain.

Even image files and sound files should contain copyright notices and license notices, if their
format permits. Some formats do not have room for textual annotations; for these files, state the
copyright and copying permissions in a README file in the same directory.

Change log files should have a copyright notice and license notice at the end, since new material is
added at the beginning but the end remains the end.

When a file is automatically generated from some other file in the distribution, it is useful for
the automatic procedure to copy the copyright notice and permission notice of the file it is
generated from, if possible. Alternatively, put a notice at the beginning saying which file it is
generated from.

A copyright notice looks like this:

Copyright (C) year1, year2, year3 copyright-holder

The word 'Copyright' must always be in English, by international convention.

The copyright-holder may be the Free Software Foundation, Inc., or someone else; you should know who
is the copyright holder for your package.

Replace the '(C)' with a C-in-a-circle symbol if it is available. For example, use '@copyright{}' in
a Texinfo file. However, stick with parenthesized 'C' unless you know that C-in-a-circle will work.
For example, a program's standard --version message should use parenthesized 'C' by default, though
message translations may use C-in-a-circle in locales where that symbol is known to work.
Alternatively, the '(C)' or C-in-a-circle can be omitted entirely; the word 'Copyright' suffices.

To update the list of year numbers, add each year in which you have made nontrivial changes to the
package. (Here we assume you're using a publicly accessible revision control server, so that every
revision installed is also immediately and automatically published.) When you add the new year, it
is not required to keep track of which files have seen significant changes in the new year and which
have not. It is recommended and simpler to add the new year to all files in the package, and be done
with it for the rest of the year.

Don't delete old year numbers, though; they are significant since they indicate when older versions
might theoretically go into the public domain, if the movie companies don't continue buying laws to
further extend copyright. If you copy a file into the package from some other program, keep the
copyright years that come with the file.

You can use a range ('2008-2010') instead of listing individual years ('2008, 2009, 2010') if and
only if: 1) every year in the range, inclusive, really is a "copyrightable" year that would be
listed individually; and 2) you make an explicit statement in a README file about this usage.

For files which are regularly copied from another project (such as 'gnulib'), leave the copyright
notice as it is in the original.

The copyright statement may be split across multiple lines, both in source files and in any
generated output. This often happens for files with a long history, having many different years of
publication.

For an FSF-copyrighted package, if you have followed the procedures to obtain legal papers, each
file should have just one copyright holder: the Free Software Foundation, Inc. You should edit the
file's copyright notice to list that name and only that name.

But if contributors are not all assigning their copyrights to a single copyright holder, it can
easily happen that one file has several copyright holders. Each contributor of nontrivial text is a
copyright holder.

In that case, you should always include a copyright notice in the name of main copyright holder of
the file. You can also include copyright notices for other copyright holders as well, and this is a
good idea for those who have contributed a large amount and for those who specifically ask for
notices in their names. (Sometimes the license on code that you copy in may require preserving
certain copyright notices.) But you don't have to include a notice for everyone who contributed to
the file (which would be rather inconvenient).

Sometimes a program has an overall copyright notice that refers to the whole program. It might be in
the README file, or it might be displayed when the program starts up. This copyright notice should
mention the year of completion of the most recent major version; it can mention years of completion
of previous major versions, but that is optional.
"""

# Python module imports.
from datetime import date, datetime
import mimetypes
from os import getcwd, path, sep, walk
from re import search
from subprocess import PIPE, Popen
import sys

# Modify the module path.
sys.path.append('.')

# relax module imports.
from lib.io import open_read_file


# The significant number of new lines of code added.
SIG_CODE = 8

# The repository checkout copies, to allow for repository migrations, ordered by date from oldest to newest.
# The data consists of:
#       0 - The repository path.
#       1 - The repository type (either "svn" or "git").
#       2 - The start date.
#       3 - The end date.
#       4 - The optional HEAD directory for svn.
REPOS = [
    ["/data/relax/gna/repository_backup/git_migration/svn_cleanup_co", "svn", 2001, 2016, "trunk"],
    [".", "git", 2001, 2050, None],    # Overlapping with the original svn repository to pull in non-tracked svn branch merges.
]

# The committer name translation table.
COMMITTERS = {
    "Michael Bieri": "Michael Bieri",
    "Edward d'Auvergne": "Edward d'Auvergne",
    "Troels Emtekær Linnet": "Troels E. Linnet",
    "Chris MacRaild": "Chris MacRaild",
    "Sébastien Morin": "Sebastien Morin",
    "Han Sun": "Han Sun",
    "Gary Thompson": "Gary Thompson",
}

# The svn committer name translation table.
SVN_COMMITTERS = {
    "michaelbieri": "Michael Bieri",
    "bugman": "Edward d'Auvergne",
    "edward": "Edward d'Auvergne",
    "root": "Edward d'Auvergne",
    "tlinnet": "Troels Emtekær Linnet",
    "macraild": "Chris MacRaild",
    "semor": "Sébastien Morin",
    "han87": "Han Sun",
    "varioustoxins": "Gary Thompson",
}

# Alternative names for the committers.
COMMITTER_ALT = {
    "Troels Schwartz-Linnet": "Troels E. Linnet",
}

# Blacklisted files.
BLACKLISTED_FILES = [
    '.gitignore',                                               # Trivial file list.
    'docs/COPYING',                                             # The original GPLv3 licence text.
    'docs/html/clean',                                          # Trivial script.
    'docs/latex/gpl-3.0.tex',                                   # The original GPLv3 licence text.
    'docs/latex/nth.sty',                                       # Public domain.
    'docs/latex/relax_version.tex',                             # Single line auto-generated file.
    'docs/latex/frame_order/compile_param_nesting',             # Trivial script.
    'graphics/analyses/model_free/2I5O_trunc.pdb',              # Public domain.
    'graphics/misc/Rosenbrock_function/generate.py',            # Public domain.
    'graphics/relax_icons/png/chemical_shift/doc.aux',          # One line.
    'graphics/relax_icons/png/chemical_shift/doc.log',          # LaTex log file.
    'graphics/relax_icons/png/frq/doc.aux',                     # One line.
    'graphics/relax_icons/png/frq/doc.log',                     # LaTex log file.
    'graphics/relax_icons/png/jw_mapping/doc.aux',              # One line.
    'graphics/relax_icons/png/jw_mapping/doc.log',              # LaTex log file.
    'graphics/relax_icons/png/model_free/mf.aux',               # One line.
    'graphics/relax_icons/png/model_free/mf.log',               # LaTex log file.
    'graphics/wizards/structure/2JK4.pdb.gz',                   # Public domain.
]

# Directories to skip.
DIR_SKIP = [
    'extern/numdifftools',                                      # External packages distributed with relax.
    'extern/sobol',                                             # External packages distributed with relax.
    'graphics/oxygen_icons',                                    # External source, copyright documented as much as possible.
]

# Add some new mimetypes.
mimetypes.add_type('application/gromacs', '.trr')
mimetypes.add_type('application/octet-stream', '.icns')
mimetypes.add_type('application/pymol', '.pse')
mimetypes.add_type('image/xcf', '.xcf')

# Binary mimetypes.
BINARY_MIMETYPES = [
    'application/gromacs',
    'application/octet-stream',
    'application/pdf',
    'application/pymol',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/vnd.microsoft.icon',
    'image/xcf',
    'application/x-dvi',
]

# Binary files (for those without a mimetype or extension).
BINARY_FILES = [
]

# Real starting dates (to handle incorrect git copying histories).
START_DATE = {
    'auto_analyses/__init__.py': [2004, "Edward d'Auvergne"],
    'auto_analyses/relax_disp.py': [2013, "Edward d'Auvergne"],
    'data_store/exp_info.py': [2009, "Edward d'Auvergne"],
    'data_store/gui.py': [2010, "Edward d'Auvergne"],
    'docs/__init__.py': [2004, "Edward d'Auvergne"],
    'docs/devel/README': [2017, "Edward d'Auvergne"],
    'docs/devel/svn2git_migration/dups.py': [2017, "Edward d'Auvergne"],
    'docs/devel/svn2git_migration/gitsvn_conversion.sh': [2017, "Edward d'Auvergne"],
    'docs/html/icons/README': [2017, "Edward d'Auvergne"],
    'docs/latex/__init__.py': [2004, "Edward d'Auvergne"],
    'docs/latex/licence.tex': [2005, "Edward d'Auvergne"],
    'extern/__init__.py': [2011, "Edward d'Auvergne"],
    'graphics/__init__.py': [2012, "Edward d'Auvergne"],
    'graphics/analyses/consistency_testing/README': [2017, "Edward d'Auvergne"],
    'graphics/analyses/dispersion/README': [2017, "Edward d'Auvergne"],
    'graphics/analyses/model_free/README': [2017, "Edward d'Auvergne"],
    'graphics/analyses/model_free/ellipsoid.pdb': [2011, "Edward d'Auvergne"],
    'graphics/misc/n_state_model/README': [2017, "Edward d'Auvergne"],
    'graphics/misc/pymol/README': [2017, "Edward d'Auvergne"],
    'graphics/misc/Rosenbrock_function/README': [2017, "Edward d'Auvergne"],
    'graphics/relax_icons/png/README': [2017, "Edward d'Auvergne"],
    'graphics/relax_icons/png/chemical_shift/README': [2017, "Edward d'Auvergne"],
    'graphics/relax_icons/png/frq/README': [2017, "Edward d'Auvergne"],
    'graphics/relax_icons/png/jw_mapping/README': [2017, "Edward d'Auvergne"],
    'graphics/relax_icons/png/model_free/README': [2017, "Edward d'Auvergne"],
    'graphics/relax_icons/svg/j_coupling.svg': [2013, "Edward d'Auvergne"],
    'graphics/screenshots/noe_analysis/README': [2017, "Edward d'Auvergne"],
    'graphics/screenshots/r1_analysis/README': [2017, "Edward d'Auvergne"],
    'graphics/screenshots/spin_viewer/README': [2017, "Edward d'Auvergne"],
    'graphics/wizards/dipole_pair/README': [2017, "Edward d'Auvergne"],
    'graphics/wizards/j_coupling.svg': [2013, "Edward d'Auvergne"],
    'graphics/wizards/molmol/README': [2017, "Edward d'Auvergne"],
    'graphics/wizards/pymol/README': [2017, "Edward d'Auvergne"],
    'graphics/wizards/spectrum/README': [2017, "Edward d'Auvergne"],
    'graphics/wizards/structure/README': [2017, "Edward d'Auvergne"],
    'graphics/wizards/value/README': [2017, "Edward d'Auvergne"],
}

# Additional copyrights that are not present in the git log.
ADDITIONAL_COPYRIGHT = {
    'docs/html/icons/contents.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/crossref.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/footnote.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/index.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/next_g.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/next.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/prev_g.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/prev.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/up_g.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/html/icons/up.png': ["Copyright (C) 1993 Nikos Drakos"],
    'docs/latex/relax.bst' : ["Copyright (C) 1988, all rights reserved."],
}

# False positives (copyright notices in files to ignore, as they are not in the git log).
FALSE_POS = {
    'graphics/wizards/oxygen-icon-weather-snow-scattered-night.png': ["Copyright (C) 2007 Nuno Pinheiro <nuno@oxygen-icons.org>", "Copyright (C) 2007 David Vignoni <david@icon-king.com>", "Copyright (C) 2007 David Miller <miller@oxygen-icons.org>", "Copyright (C) 2007 Johann Ollivier Lapeyre <johann@oxygen-icons.org>", "Copyright (C) 2007 Kenneth Wimer <kwwii@bootsplash.org>", "Copyright (C) 2007 Riccardo Iaconelli <riccardo@oxygen-icons.org>"],
    'graphics/wizards/object-locked-unlocked.png': ["Copyright (C) 2007 Nuno Pinheiro <nuno@oxygen-icons.org>", "Copyright (C) 2007 David Vignoni <david@icon-king.com>", "Copyright (C) 2007 David Miller <miller@oxygen-icons.org>", "Copyright (C) 2007 Johann Ollivier Lapeyre <johann@oxygen-icons.org>", "Copyright (C) 2007 Kenneth Wimer <kwwii@bootsplash.org>", "Copyright (C) 2007 Riccardo Iaconelli <riccardo@oxygen-icons.org>"],
    'graphics/wizards/oxygen-icon-weather-clear.png': ["Copyright (C) 2007 Nuno Pinheiro <nuno@oxygen-icons.org>", "Copyright (C) 2007 David Vignoni <david@icon-king.com>", "Copyright (C) 2007 David Miller <miller@oxygen-icons.org>", "Copyright (C) 2007 Johann Ollivier Lapeyre <johann@oxygen-icons.org>", "Copyright (C) 2007 Kenneth Wimer <kwwii@bootsplash.org>", "Copyright (C) 2007 Riccardo Iaconelli <riccardo@oxygen-icons.org>"],
    'graphics/wizards/dipole_pair/VectorFieldPlot.py': ["Copyright (C) 2010 Geek3"]
}

# False negatives (significant git log commits which do not imply copyright ownership).
FALSE_NEG = {
    'docs/html/icons/contents.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/crossref.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/footnote.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/index.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/next_g.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/next.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/prev_g.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/prev.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/up_g.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'docs/html/icons/up.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'graphics/analyses/consistency_testing_100x47.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'graphics/analyses/consistency_testing_200x94.png': ["Copyright (C) 2011 Edward d'Auvergne"],
    'graphics/wizards/oxygen-icon-weather-snow-scattered-night.png': ["Copyright (C) 2012 Edward d'Auvergne"],
    'graphics/wizards/object-locked-unlocked.png': ["Copyright (C) 2012 Edward d'Auvergne"],
    'graphics/wizards/oxygen-icon-weather-clear.png': ["Copyright (C) 2012 Edward d'Auvergne"],
}

# SVN revisions and git hashes to exclude.
EXCLUDE = {
    "/data/relax/gna/repository_backup/git_migration/svn_cleanup_co": [
        'r19068',   # A reversion commit.
        'r19067',   # The reverted commit.
        'r19066',   # The reverted commit.
        'r19065',   # The reverted commit.
    ],
    '.': [
        '3497eb7bdb85ea656e0f33a8b972602cc5bde6ed',    # Directory rename {gui_bieri/res/pics => gui/images}.
        '9403da5ca58d48ca56a0bc2c19da89a44efced44',    # Reversion of '6888758caa637c256837b8fce9ebb9093d1656a2'.
        '6888758caa637c256837b8fce9ebb9093d1656a2',    # Reverted by '9403da5ca58d48ca56a0bc2c19da89a44efced44'.
    ]
}

# SVN revisions and git hashes to switch authorship of (e.g. if someone commits someone else's code).
# The data consists of:
#       0 - The commit key, consisting of the first line of the commit message followed by the ISO date in brackets.
#       1 - The comitter's name.
#       2 - The real author.
AUTHOR_SWITCH = [
    ["Fixed several typo errors of \"Is it selected\"->\"It is selected\". A copy-paste error which have spreaded. (2013-10-07 13:41:55 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r21008 - 0fa89a69d265a3e39c65c7582fa48e1634db25eb
    ["Added Tollinger model TSMFK01 to sample scripts. (2013-10-07 13:41:54 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r21007 - aeae2d81602e411eb2ab38927a1f289a7ca9fd0f
    ["Added Tollinger reference. (2013-10-07 13:41:52 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r21006 - 652a1f694e1cea9de1405072870efe387212b3f6
    ["Another fix for bibtex string 'cp' instead of 'cj'. (2013-09-13 12:52:33 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r21002 - 25bb33fa1c921d8c8238b087ae2214e4a5b6b624
    ["Fix for latex bibtex string 'cp' instead of 'cj'. (2013-09-13 12:52:32 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r21001 - 67c3e1bac2faf2e3f612114c8389793f59c2210d
    ["Fix for bibtex warning 'Warning--string name \"mb\" is undefined'. (2013-09-13 12:52:30 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r21000 - 82a5c44a23bf5da1783c9b69117bc3d147b27352
    ["Fix for adding TSMFK01 to sample scripts. (2013-09-12 09:08:18 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20988 - e053ed7f9b031060a2e44dab1a8d53560158fd58
    ["Added subsection with TSMFK01 model. (2013-09-12 09:08:16 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20987 - 2acd34ca7b89836299b3388e2527126b91c08c73
    ["Added TSMFK01 to model overview table. (2013-09-12 09:08:15 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20986 - 5df428dea43b8006b36e7912d5d273da062c3ddc
    ["Added desc. item for model TSMFK01. (2013-09-12 09:08:14 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20985 - 403716ea6ddc1215e3328aa0276dec6e8d2ef989
    ["Modified headers for scripts producing analysis for data which is full or truncated. (2013-09-11 11:06:37 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20979 - 3bc5db46d827905d8758defa58d4482c2a5e5888
    ["Added systemtests for conversion of kex to k_AB/k_BA for models where kex and pA is present. (2013-09-11 11:03:45 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20978 - f731ce39a9d4bd6927660e81f560e032584619c0
    ["Fix for passing system test on windows with python 32. Precision lowered by 2 decimals. (2013-09-11 11:03:44 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20977 - 7f97c47a1a7595a9f667e8ca1215140847d26186
    ["Added system test for testing conversion to k_BA from kex and pA. (2013-09-11 11:03:43 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20976 - fd7d7afb308a6b306e9d7ac4f9810418c51e2197
    ["Added the conversion to k_BA from kex and pA. (2013-09-11 11:03:41 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20975 - 8f3909d219ee35bdf88c368b871474059ffbc9c3
    ["Fixed bug, where kex to k_AB where not possible if the model does not contain parameter 'pA'. The conversion is now skipped. (2013-09-11 11:03:40 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20974 - 82b24b0aa7100f7f6ae4c4734d7c83cbe148399c
    ["Added the conversion to k_AB from kex and pA. k_AB = kex * (1.0 - pA). (2013-09-10 12:39:51 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20966 - 77e6d3b8c1c78d9b0b7a7545e74ddb2c67d32355
    ["Optimized the target function for model TSMFK. (2013-09-10 12:39:49 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20965 - f5c8accda0254d9c277f0bfaa821b2b26806a487
    ["Added to calculate the tau_cpmg times when model is TSMFK01. (2013-09-10 12:39:47 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20964 - 347a0637cd8414c78cdb43770ccc24d808d54c77
    ["Added the write-out of 'dw' and 'k_AB' for model TSMFK01, when performing auto-analysis. (2013-09-10 12:39:44 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20963 - 766b0b157ed6a558586a58555877974eb5745c87
    ["Changed reference to Tollinger et al. instead of Tollinger/Kay. (2013-09-10 06:41:38 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20953 - 36f652d1cda77096b639f231ed0c8f4412ba3e9b
    ["Added the output from relax after analysis of all models. (2013-09-09 16:33:09 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20943 - 955c24fcc2825ca239ff8b815c9d7f9588546b1f
    ["Modified doc string for the script analysing all models for residue L61. (2013-09-09 16:33:01 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20942 - a90d59a6501bfec7dc77705c4676607e02d27fd0
    ["Added to the README file for the 1.01 M GuHCL experiment. (2013-09-09 16:32:59 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20941 - 581e3fb8d6b30d71797c60a9db692fe901c43872
    ["Added dataset experiment in 1.01 M GuHCl (guanidine hydrochloride). (2013-09-09 16:32:01 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20940 - 0caa48355d94a2f741d272e9ebd614b9986f25dd
    ["Re-run of data after movement of scripts. (2013-09-09 16:31:59 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20939 - 38f7e2a2c8cf4089ded79863d1c0d764646b74eb
    ["Changed scripts after moving data. (2013-09-09 16:31:57 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20938 - 6748094a5b18f6e53f876857e8ac196998f370f5
    ["Moved files into folder which is specific for the experiment. (2013-09-09 16:30:55 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20937 - 1616eb937851695b8a6f49df2df1850e00bbb989
    ["Modified system test after inclusion of 1M GuHCl dataset. (2013-09-09 16:30:53 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20936 - d7cfc91e1af21df6cad46fb71717d43915bdcc5f
    ["Added k_AB to parameters. (2013-09-06 15:04:31 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20910 - 6b371ec7b8157b8641ceb85f3677353ce6908c78
    ["Converted references of ka and kA to k_AB. (2013-09-06 14:12:15 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20905 - fddcf10d696fff3b43b3c72c8855bb0c7fa2958d
    ["Fixed expydoc formatting. (2013-09-06 12:42:59 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20897 - 7b60e1e808e47273001f0929a27274e0106500b5
    ["Fixed missing space typo. (2013-09-06 12:42:58 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20896 - ebf3c6980c8e145eafb2b7cc6ea1befa119f510a
    ["Modified the script for the full analysis of all models of CPMG type. (2013-09-06 11:57:01 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20893 - e3c86eeaa8dede6bc137e2043b2a08088cda5738
    ["Started a system test for model TSMFK01. (2013-09-06 11:56:59 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20892 - e596f3754824249e0975fca31989c882465abb5f
    ["Fix for the residue index in the test suite when using the truncated spin system. (2013-09-06 09:43:35 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20886 - dac6f58571441a7d9e4395b77ca5e4bea05409ee
    ["Changed the saved states to the truncated spin system. (2013-09-06 09:43:34 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20885 - 572067083b429ca6b811c783eae12b4bd885a467
    ["Changed the initialization script to use the truncated spin system. (2013-09-06 09:43:32 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20884 - ff5b94a987b520fae1edfcfce57d4924039e897f
    ["Added file which setup a truncated spin system. (2013-09-06 09:43:31 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20883 - 6baf8f7ffb5074f18cc876f0bb63f77f28efd931
    ["Added \"CR72 full\" test suite for kteilum_fmpoulsen_makke_cpmg_data. (2013-09-06 09:43:30 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20882 - b508b95f2523fe841f1af2aacd034f15264fde10
    ["Fixed values for system test: relax -s Relax_disp.test_kteilum_fmpoulsen_makke_cpmg_data_to_cr72 The test now passes. The values are compared to a relax run with 500 Monte Carlo simulations. (2013-09-06 09:43:29 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20881 - b0cc3978441b9dbce1306c262f454bc5dbe6ce3b
    ["Added the truncated test data for system test: relax -s Relax_disp.test_kteilum_fmpoulsen_makke_cpmg_data_to_cr72 (2013-09-06 08:26:42 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20878 - dc643a1cbda5f4eabd3146a66f29094ea120c0c2
    ["Fixed typo. (2013-09-06 08:26:41 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20877 - 8e6249dc3abd7d44fa0c6f5a3cf60420df1a82bb
    ["Moved the experiment type setting into per spectra settings. (2013-09-06 08:26:40 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20876 - 561fd72ef5b4a2986d06b206e1ccf0450f4e507c
    ["Fix epydoc HTML markup code. (2013-09-04 13:54:37 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20805 - 2491c3719061d50cb34469c0844e5116cbb57263
    ["Fix trailing spaces. (2013-09-04 13:54:36 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20804 - ff2cc86e13d98c209053c73cbedbbf099c96b1dc
    ["Added the first system test for model CR72 for the kteilum_fmpoulsen_makke_cpmg_data. (2013-09-04 13:27:19 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20803 - 94912f057e4825f408781785ad1a69d8b0360e36
    ["Added script files for generating a saved state file with R2eff values. (2013-09-04 13:26:24 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20802 - 6b43dc16ca55120a28e17c4f9274edb04037b0fb
    ["Modified the script file for saving of a truncated base_pipe state file. (2013-09-04 13:23:41 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20801 - ed59e318c717bc4be20011eb795a29ee91e2de2e
    ["Truncated the dataset to only one residue L61. The truncated dataset will be expanded later. (2013-09-04 13:23:07 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20800 - 32433b400d14dbe7ea9119ccc3d9ee1e0e3d98d0
    ["Added setup function for the system test of KTeilum_FMPoulsen_MAkke_2006 data. (2013-09-04 11:55:18 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20797 - a8fb612b4b60f7cc084bf089df963ce6ab9d9354
    ["Moved the ordering of the model TSMF. Ordering conventions mentioned in this post: http://article.gmane.org/gmane.science.nmr.relax.devel/4500 (2013-09-03 15:07:38 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20773 - e01a74e2f0dfb76329655377a03b1efbccc26f2f
    ["Fix for unpacking the parameters correctly. (2013-09-03 09:27:05 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20767 - 29be71687d5231d51227f70b97987384982044f7
    ["Fix for r20 should be called r20a. (2013-09-03 09:27:04 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20766 - 6f11f86697c8c81a497a64f8b7a5da4c32a7874d
    ["Renamed ka parameter to kA, to be consistent with naming conventions. (2013-09-03 09:27:03 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20765 - 0bf6ba5160ebcbec907ec4bde74aaaac322b7908
    ["Added support for the TSMFK01 model to the relax_disp.select_model user function back end. (2013-08-20 21:15:39 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20654 - 3089dbd891d5d59f5d5b36e96f72e1d13c77b6f8
    ["Fix for converting dw from ppm to rad/s. (2013-08-20 21:15:37 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20653 - 06d2a6aaf030809e178ab91a167a81bb826eae59
    ["Copyright of Sebastien Morin and Edward d'Auvergne re-inserted, since tsmfk01 is an alteration of lm63.py and m61.py in same directory. (2013-08-20 21:14:36 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20652 - 2d01aea46dbd4eedc2c300d280535442ea3180d0
    ["Added the TSMFK01 model equations to the relax library: lib/dispersion/tsmfk01.py (2013-08-18 18:23:22 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20632 - 0ec7e943fb5f2718959b1fd8e3686515302f74ab
    ["Created the TSMFK01 model target function for 2-site very-slow exchange model, range of microsecond to second time scale. (2013-08-18 18:23:12 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20631 - 2871a1a56b7d61c3c1bddd01a35b22a50ae8599e
    ["Added the TSMFK01 model to the user_functions/relax_disp.py select_model user function frontend. (2013-08-18 18:22:45 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20630 - 85a257befee0462a33fa69bc42b6ca49c7076fe7
    ["lib/dispersion/lm63.py is copied to tsmfk01.py as part of the implementation of the TSMFK01 model equation. (2013-08-18 16:15:17 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20629 - 1481f9fcfd09a8eeed697d5d76892eb964407938
    ["Added the new 'TSMFK01' model to the specific_analyses\relax_disp\variables.py module. (2013-08-18 14:01:43 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20628 - 0fb1231289b49ea9ec908c3fc2bc3801bddfc37b
    ["Fix for two spaces are used after a period in documentation. (2013-08-02 22:08:28 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20522 - 7384dcf4167e0b1a038d653dfb618d5907086973
    ["Fix for two spaces are used after a period in documentation. (2013-08-02 22:08:26 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20521 - 658ca7b73e7a2f96b4a613309ced53bcd8e8000c
    ["Fix for two spaces are used after a period in documentation. (2013-08-02 22:08:24 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20520 - c2da5e8839330c48290432de2b3291fe87731cb0
    ["Added a stub GUI describtion in the File formats, for NMRPipe seriesTab. (2013-08-02 20:07:52 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20519 - f8b0a9b0c15e9e28e948df39751d18b73a358b5e
    ["Added GUI description for when supplying 'auto' to the spectrum_id. (2013-08-02 20:07:51 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20518 - 332c2c52c191f730698e37c51ffce6f19a0f45d9
    ["Added epydoc documentation in pipe_control\spectrum.py .read() when supplying keyword 'auto'. (2013-08-02 20:07:49 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20517 - 21916108cfaf069ed64d9e773b44c8296ef0d030
    ["Moved the adding function of adding the spectrum id (and ncproc) to the relax data store. (2013-08-02 18:59:02 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20515 - 834347d2ffc5c03287a193b05848b76de3ace5f1
    ["Moved checks for matching length of spectrum IDs and intensities columns. (2013-08-02 18:59:00 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20514 - 4ad351fb23e946aa688ce56d959482742d18816e
    ["Remove from datalist where empty list starts. These are created where spins are skipped for ID = '?-?'. (2013-08-02 18:58:59 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20513 - 2526f50094f63f532d15d2fca60f09ea52641f09
    ["Made it possible to autogenerate spectrum ID's, if spectrum_id='auto'. (2013-08-02 18:58:57 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20512 - 1a38b36a4b9585260f2e9cda6154fd7f5829b73b
    ["Added check for number of supplied spectra ID's and the number of returned intensity columns. (2013-08-02 18:58:55 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20511 - 275608ee8b7990126ff0bf0764b74eb7c91d618b
    ["Added system test for reading of a multi column formatted NMRPipe seriesTab file. (2013-08-02 18:56:54 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20510 - b33bf75a135653ae76dae1d74612baf9e1fb19e9
    ["The ID of spins in seriesTab_multi.ser was not formatted correctly to SPARKY format. (2013-08-02 15:55:23 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20509 - 86a9fd5b8ce877803abcbee554e37c52e8d7c2a4
    ["Replacing a pointer-reference structure to an empty creation of list of lists. (2013-08-02 15:35:57 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20508 - 3bfaef643c82eebce19de2415dde883b2e883670
    ["Fix for unit test of nmrpipe. (2013-08-02 15:35:01 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20507 - edd8c338ce24feb1d6aa26385220434e2f630074
    ["Adding NMR seriesTab data file for a multiple column / multiple spectrum formatted file. (2013-08-02 12:00:20 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20506 - b0d9f2622263d05b2addc8c7c63c7b3309eaf10f
    ["Fix for handling reading spin of type heteronuc='NE1' and proton='HE1'. (2013-08-02 11:53:52 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20505 - ac462582c36768dad3f14992f246537c21bce280
    ["Fixed the extraction of NMRPipe seriestab data in pipe_control.spectrum.read(). (2013-08-02 11:52:16 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20504 - c48003924908e100b297ba5ab38dd7a10b354f68
    ["Modfied the intensity list to handle intensities for all spectra per spin. (2013-08-02 11:51:50 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20503 - 37d763daea0e2e815427e0e1aaec87d193b7b472
    ["Fixed wrong reference to Sparky format. (2013-08-02 11:40:28 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20502 - 95f3cc349660ed46d6144f15bb8d84991b350499
    ["Removed the flag for single_spectrum. (2013-08-02 11:39:53 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20501 - f90c252ca26eff3544fb267a87701ac57a782831
    ["Flag change added to reading of NMRPipe SeriesTab. (2013-07-22 06:49:41 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20446 - 4f2d2ca67f50eb2202961a63d1221356aeaee31b
    ["Added flag for single or multiple extraction of spectrum. (2013-07-22 06:48:21 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20445 - a9ecea1f75602f8c3f1ded14eb3d5b07c0c8f709
    ["Extraction of NMRPipe SeriesTab changed. (2013-07-22 06:47:33 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20444 - e25fb3e8507ad83ed9d163e30c22a8eb9cbedfd0
    ["Completed NMRPipe SeriesTab reader. (2013-07-22 06:37:58 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20442 - bfb1ec5dd9e19b039130db3cf15ce71bd534e65f
    ["Progress sr #3043: (https://gna.org/support/index.php?3043) - support for NMRPipe seriesTab format *.ser. (2013-07-22 06:34:04 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20440 - 86ffa9dd18f255cbc78d2e15a71ff831bd5bd2bf
    ["Progress sr #3043: (https://gna.org/support/index.php?3043) - support for NMRPipe seriesTab format *.ser. (2013-07-22 06:32:54 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20439 - 8767b75cd29ca83bba8f642e4a017b1ad82ad20f
    ["Added the script from Troels Linnet for backing up the relax wiki via FTP. (2013-07-17 11:58:11 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20350 - 1818bc2113206949aa13c38fdd5dbfb3b83a0775
    ["Imported the missing lib.software.nmrpipe module into pipe_control.spectrum. (2013-06-24 12:58:23 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20257 - 45087db216e4da7a019815af0fb1560a8c3231e1
    ["Added function destination for auto-detected NMRPipe SeriesTab format. (2013-06-24 10:29:40 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20256 - 948e4c620829430eb1eac217a967009452493660
    ["Autodetect format implemented for NMRPipe SeriesTab format implemented. (2013-06-21 18:01:06 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20251 - f9a093e6d6f63dd3accc44ef2cf6f4c4b8924750
    ["Fix for commit (http://article.gmane.org/gmane.science.nmr.relax.scm/18004). The spin naming was wrong. (2013-06-21 17:46:58 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20250 - 6c4f94357d2d081a11acb44d58dad0c24f73da97
    ["Adding a NMRPipe function file in the folder lib\software\nmrpipe.py. (2013-06-21 16:33:03 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20249 - 8ddee0172e11b02c6c7393a2e4df8c23ba9dfcbb
    ["Test function for NMRPipe SeriesTab format implemented. (2013-06-21 16:23:24 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20248 - 18c0143989ccd65bd73e157ede03ffa1911610a8
    ["Adding a test data file in NMRPipe SeriesTab format. (2013-06-21 15:28:04 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20247 - 75455e3f1430480c349c6375c38b49e3088a5537
    ["Fix for bug #20916, (https://gna.org/bugs/?20916) - Suggestion for python script for PNG/EPS/SVG conversion of grace files. (2013-06-18 15:29:16 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20196 - 57daa1453ebb3291ec812e52c0f809de61be13fc
    ["Fix for bug #20915, (https://gna.org/bugs/?20915) - Failure of Grace opening in MS Windows (2013-06-18 08:00:50 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r20187 - b9cbcced6dea6b17ee7f05999dc7a618b3219da6
    ["Added the 'test.seq' file from bug report #20873 (http://gna.org/bugs/?20873). (2013-06-06 15:06:42 +0000)",
        "Edward d'Auvergne", "Troels Emtekær Linnet"],    # r19895 - a1413d678d500467d8fdaff4db704a919d9ec483
    ["Bug fix for the color_code_noe() method. (2010-01-15 11:40:52 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10238 - 2d0bccf99aa99c0d2b2998e4b868b727fee79e81 End of adding Michael's GUI 1.00.
    ["A number of improvements to the final results analysis. (2010-01-15 10:30:17 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10237 - c090b5dd1670e2e420d9b92787d47f1ec1051bbd
    ["Removed a number of calls to wx.PySimpleApp(). (2010-01-15 10:25:21 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10236 - 76c93c006a70e96921f88b7d1dcbf34d076c73ef
    ["Simplifications to the file dialog code. (2010-01-15 10:24:40 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10235 - 280eec8f86a3c7e882203dd247b1df1aab76e271
    ["Shift of the GUI calculation code to using the relax API (rather than scripting). (2010-01-15 10:23:13 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10234 - b2746e0609846b4a94094b829e159d32da0ce576
    ["Shifted from using msgbox() to relax_run_ok() to indication proper completion of the calculation. (2010-01-15 10:17:23 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10233 - fa72615c4c659cfb9ddba688a0da2bcc3a3c291a
    ["Removed an event.Skip() call. (2010-01-15 10:04:37 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10232 - 05d33ce113973eb36a000f6234d7d6897cc89a62
    ["Expansion of exec_model_free() in preparation for rearrangements in the calc_modelfree module. (2010-01-15 10:03:40 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10231 - 86299d02dc12bef16f4d1179ec7e2de9572ceac7
    ["Modified how the r1_list and r2_list data structures are handled. (2010-01-15 09:59:06 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10230 - 8803f88adc055e1e84789255664318eda1196f1c
    ["relax execution now occurs automatically after clicking on the icon. (2010-01-15 09:54:54 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10229 - a324f08aaf4e2a3c5c2b779adbade4c8e5fa9982
    ["Expanded the print out when exiting to include references and shifted to using question(). (2010-01-15 09:51:59 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10228 - 8a53d9fcd96e32cbee9f88e239aef8def7f50837
    ["Added actions for the new menu entries. (2010-01-15 09:46:48 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10227 - c3dc5b7ca9b24d3a7b51e66cac58dff0f2f86eaf
    ["Comment improvements throughout relax_gui. (2010-01-15 09:45:55 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10226 - 13bd66b7bb6d716d3c331985d4877e87a8253ccd
    ["Added a series of global variables to be used throughout the GUI. (2010-01-15 09:32:40 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10225 - d82427c07c09ca3e259f506c13e456109f6a43dd
    ["Increased the status bar width. (2010-01-15 09:17:00 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10224 - 1026067c47e78b65d8c63ada1470c34f9b004beb
    ["Simplified the whichmodel() function (not sure what the removed wx calls did anyway). (2010-01-15 09:12:53 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10223 - cbdb7467cd555aca3634b476c09a25dcfafb52b1
    ["Improvements to how unresolved spin systems are handled. (2010-01-15 09:10:26 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10222 - 6ca187e562c490618d7c50594ae4ec36c9b0b6a9
    ["Updated the global setting dialog. (2010-01-14 18:05:43 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10221 - cbc0adf95100a37a7c9b4a3867c4bb6eab116bb2
    ["Properly introduced the import_seq(), settings(), param_file_setting() and reset_setting() methods. (2010-01-14 17:05:47 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10220 - a20e5ffb4b94d9a044f7f343bed42a9a9c45c156
    ["Reverted r10214 as the code was not placed in the correct spot! (2010-01-14 17:01:25 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10219 - 1cc1f39134858fe3f41c96bc8d328895b40cf57c
    ["Bug fix.  Incorrect whitespace was introduced in the last revision (r10217). (2010-01-14 16:46:33 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10218 - 7c7e5706472cac6b5525313ca1b945914268cc6f
    ["Changes to all the opening and saving file dialogs. (2010-01-14 16:45:18 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10217 - 977203b2644848a56ebaa6d92ac4eba0467e27f0
    ["Switched from using msgbox() to using the specific dir_message() function. (2010-01-14 16:33:36 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10216 - 5c248b83efd842e57e678f4f02729b56f063b019
    ["Switched from using diropenbox() to opendir(). (2010-01-14 16:27:17 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10215 - 647bec76129c4d3552216c79aa9e37b05704fe30
    ["Added the missing import_seq(), settings(), param_file_setting() and reset_setting() methods. (2010-01-14 15:10:02 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10214 - 5a5ce803f018eddf06141a0cbf76478f2baf7333
    ["Expansion and improvements to the menu bar of the main window. (2010-01-14 15:06:06 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10213 - 1053bac83d5d4f28be9336c5c478c7d38915dc77
    ["Clean up of the gui_bieri.res.results_analysis module (much code deletion) (2010-01-14 14:45:19 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10212 - d3bc64efa9b046c9aae36e6d325f30b4ad66715a
    ["Another import fix as this was forgotten in the last commit. (2010-01-14 14:06:48 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10211 - ed977f50ec633dd050ef070e5cc2a07c500308c5
    ["Fixes for the relaxGUI imports. (2010-01-14 13:58:33 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10210 - 240521cad444abe40f4d67ab0b32cfb8bf7e1e1d
    ["Added version information to the GUI.  This includes a GUI version of 1.00. (2010-01-14 13:47:33 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10209 - eb76464f0ac57a59ca668d4f966788366c00e76b
    ["Changed '/' to os.sep to make the Bieri GUI OS independent. (2010-01-14 10:13:05 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10206 - ed5807eb07c2189a495efd9075dcbb6a60ee1619 Start of adding Michael's GUI 1.00.
    ["Added the select_model_calc modules. (2009-12-14 13:48:05 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10093 - 55ea96c362fe1b7dab61f84b5fca38ed102f9eaf
    ["Added the filedialog and message modules. (2009-12-14 13:41:14 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r10092 - 81aab2e3b2c72692a0edab23dbeebc51c40f162e
    ["Initial commit of Michael Bieri's GUI code. (2009-11-19 09:43:44 +0000)",
        "Edward d'Auvergne", "Michael Bieri"],            # r9879  - 289d0c6a814bf7b23daed580dcbc040d4f208b9e
]


def committer_info_cleanup(file_path, committer_info):
    """Clean up the committer info data structure.

    @param file_path:       The full file path.
    @type file_path:        str
    @param committer_info:  The committer info data structure, listing the committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @type committer_info:   dict of lists of str
    """

    # Strip out incorrect dates.
    if file_path in START_DATE:
        # Add missing committers.
        if START_DATE[file_path][1] not in committer_info:
            committer_info[START_DATE[file_path][1]] = []

        # Loop over all recorded committers.
        for committer in committer_info:
            # Prune all earlier dates.
            for i in reversed(range(len(committer_info[committer]))):
                if int(committer_info[committer][i]) < START_DATE[file_path][0]:
                    committer_info[committer].pop(i)

            # Add the start date if missing.
            if START_DATE[file_path][1] == committer and not str(START_DATE[file_path][0]) in committer_info[committer]:
                committer_info[committer].append(str(START_DATE[file_path][0]))

    # Remove committers with no commits.
    prune = []
    for committer in committer_info:
        if len(committer_info[committer]) == 0:
            prune.append(committer)
    for committer in prune:
        del committer_info[committer]


def extract_copyright(file_path):
    """Pull out all the copyright notices from the given file.

    @param file_path:   The full file path.
    @type file_path:    str
    @return:            The list of current copyright notices.
    @rtype:             list of str
    """

    # Read the file data.
    file = open_read_file(file_path, verbosity=0)
    lines = file.readlines()
    file.close()

    # Loop over the file, finding the statements.
    statements = []
    for line in lines:
        if "Copyright (C)" in line:
            # Skip README file copyright notices for other files.
            if 'README' in file_path and search(": *Copyright \(C\)", line):
                continue

            # Skip copyright notices in this script.
            if 'copyright_notices.py' in file_path and search("\"", line):
                continue

            # Strip leading and trailing comment characters, and all whitespace.
            line = line.strip()
            if line[0] in ['#', '%']:
                line = line[1:]
            if line[-1] in ['#', '%']:
                line = line[:-2]
            line = line.strip()

            # Append the statement.
            statements.append(line)

    # Return the list of copyright statements.
    return statements


def extract_copyright_readme(file_name, root):
    """Try to extract copyright notice for the file from the README file.

    @param file_name:   The isolated file name to search for the copyright notice.
    @type file_name:    str
    @param root:        The file path root which should contain the README file.
    @type root:         str
    @return:            The list of current copyright notices.
    @rtype:             list of str
    """

    # Search for the README file.
    readme = root + sep + 'README'
    if not path.exists(readme):
        return []

    # Read the README file data.
    file = open(readme)
    lines = file.readlines()
    file.close()

    # Loop over the file, finding the statements.
    statements = []
    for line in lines:
        if search("^%s: " % file_name, line) and "Copyright (C)" in line:
            statements.append(line[line.index("Copyright"):].strip())

    # Return the list of copyright statements.
    return statements


def format_copyright(committer_info):
    """Convert the committer and year data structure into copyright statements.

    @param committer_info:  The committer info data structure, listing the committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @type committer_info:   dict of lists of str
    @return:                The ordered list of copyright statements.
    @rtype:                 list of str
    """

    # Init.
    statements = []

    # Loop over each committer.
    for committer in committer_info:
        # Format the year string.
        years = format_years(committer_info[committer])

        # Format the copyright statement.
        statements.append("Copyright (C) %s %s" % (years, COMMITTERS[committer]))

    # Return the list of copyright statements.
    return statements


def format_years(years):
    """Format the given list of years for the copyright string.

    @param years:   The unordered list of years.
    @type years:    list of str
    """

    # Convert the years to ints and sort the list.
    dates = []
    for i in range(len(years)):
        dates.append(int(years[i]))
    dates.sort()

    # Split the dates into ranges.
    date_ranges = [[dates[0]]]
    for i in range(1, len(dates)):
        if dates[i]-1 == date_ranges[-1][-1]:
            date_ranges[-1].append(dates[i])
        else:
            date_ranges.append([dates[i]])

    # String format the ranges.
    year_string = ''
    for i in range(len(date_ranges)):
        # Range separator required.
        if len(year_string):
            year_string += ','

        # A single year.
        if len(date_ranges[i]) == 1:
            year_string += '%s' % date_ranges[i][0]

        # A range.
        else:
            year_string += '%s-%s' % (date_ranges[i][0], date_ranges[i][-1])

    # Return the formatted string.
    return year_string


def git_log_data(file_path, repo_path=None, exclude_hashes=None, author_switch=None, committer_info=None, after=None, before=None, init=False):
    """Get the committers and years of significant commits from the git log.

    @param file_path:           The full file path to obtain the git info for.
    @type file_path:            str
    @keyword repo_path:         The path to the local copy of the git repository.
    @type repo_path:            str
    @keyword exclude_hashes:    A list of commit hashes to exclude from the search.  For example directory renames with binary files present.
    @type exclude_hashes:       list of str
    @keyword author_switch:     List of commit hashes and authors to switch the authorship of.  The first element should be the commit hash, the second the comitter, and the third the real comitter.
    @type author_switch:        list of list of str
    @keyword committer_info:    The committer info data structure, listing the committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @type committer_info:       dict of lists of str
    @keyword after:             Show commits more recent than a specific date.
    @type after:                int or None
    @keyword before:            Show commits older than a specific date.
    @type before:               int or None
    @keyword init:              A flag which if True means that the current repository is the starting repository.
    @type init:                 bool
    @return:                    The committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @rtype:                     dict of lists of str
    """

    # Date restrictions.
    after_opt = ''
    before_opt = ''
    if after:
        after_opt = '--after=%i-01-01' % after
    if before:
        before_opt = '--before=%i-12-31' % before

    # Exec.
    pipe = Popen("git log %s %s --numstat --follow --pretty='%%cn xxx %%cd xxx %%H xxx %%s' --date=iso %s/%s" % (after_opt, before_opt, repo_path, file_path), shell=True, stdout=PIPE, close_fds=False)

    # Get the data.
    lines = pipe.stdout.readlines()
    i = 0
    committer = None
    while 1:
        # Termination.
        if i >= len(lines):
            break

        # Obtain the committer and date info.
        committer, date, commit_hash, subject = lines[i].decode().split(' xxx ')
        year = date.split('-')[0]
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')

        # The next line is a committer, so skip the current line.
        if search(' xxx ', lines[i+1].decode()):
            i += 1
            continue

        # Hashes to exclude.
        if commit_hash.strip() in exclude_hashes:
            i += 3
            continue

        # The numstat info.
        newlines = lines[i+2].decode().split()[0]
        if newlines == '-':
            newlines = 1e10
        else:
            newlines = int(newlines)

        # Not significant.
        if newlines < SIG_CODE:
            i += 3
            continue

        # Skip svnmerge.py merges for svn->git migration repositories as these do not imply copyright ownership for the comitter.
        if search("^Merged revisions .* via svnmerge from", subject):
            i += 3
            continue

        # Author switch.
        commit_key = "%s (%s +0000)" % (subject.strip(), date.strftime("%Y-%m-%d %H:%M:%S"))
        for j in range(len(author_switch)):
            if author_switch[j][0] == commit_key:
                committer = author_switch[j][2]

        # Date already exists.
        if committer in committer_info and year in committer_info[committer]:
            i += 3
            continue

        # A new committer.
        if committer not in committer_info:
            committer_info[committer] = []

        # Store the info.
        committer_info[committer].append(year)

        # Increment the index.
        i += 3

    # Always include the very first commit.
    if init:
        if committer and committer not in committer_info:
            committer_info[committer] = []
        if committer and year not in committer_info[committer]:
            committer_info[committer].append(year)


def svn_log_data(file_path, repo_path=None, exclude_rev=None, author_switch=None, svn_head=None, committer_info=None, after=None, before=None, init=False):
    """Get the committers and years of significant commits from the svn log.

    @param file_path:           The full file path to obtain the git info for.
    @type file_path:            str
    @keyword repo_path:         The path to the local copy of the svn repository.
    @type repo_path:            str
    @keyword exclude_rev:       A list of revisions to exclude from the search.  For example commit reversions.
    @type exclude_rev:          list of str
    @keyword author_switch:     List of revisions and authors to switch the authorship of.  The first element should be the commit revision number (e.g. "r200"), the second the comitter, and the third the real comitter.
    @type author_switch:        list of list of str
    @keyword svn_head:          The HEAD directory, e.g. "trunk".
    @type svn_head:             str
    @keyword committer_info:    The committer info data structure, listing the committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @type committer_info:       dict of lists of str
    @keyword after:             Show commits more recent than a specific date.
    @type after:                int or None
    @keyword before:            Show commits older than a specific date.
    @type before:               int or None
    @keyword init:              A flag which if True means that the current repository is the starting repository.
    @type init:                 bool
    @return:                    The committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @rtype:                     dict of lists of str
    """

    # Date restrictions.
    date_range = ''
    if after or before:
        date_range += "-r"
    if before:
        date_range += '{%i-12-31}:' % before
    else:
        date_range += '{3000-01-01}:'
    if after:
        date_range += '{%i-01-01}' % after
    else:
        date_range += '{1000-01-01}'

    # Exec.
    pipe = Popen("svn log --diff %s %s/%s/%s" % (date_range, repo_path, svn_head, file_path), shell=True, stdout=PIPE, close_fds=False)

    # Get the data.
    lines = pipe.stdout.readlines()
    for i in range(len(lines)):
        try:
            lines[i] = lines[i].decode()[:-1]
        except UnicodeError:
            # Catch the ascii character 43 ("+").
            if lines[i][0] == 43:
                lines[i] = "+binary diff"
            else:
                lines[i] = ""
    i = 0
    committer = None
    while 1:
        # Termination.
        if i >= len(lines)-1:
            break

        # A new commit.
        if search('^------------------------------------------------------------------------', lines[i]) and lines[i+1][0] == 'r':
            # Move to the summary line.
            i += 1

            # Extract the committer and year.
            rev, svn_committer, date, length = lines[i].split(' | ')
            committer = SVN_COMMITTERS[svn_committer]
            year = date.split()[0].split('-')[0]
            date = date.split(" (")[0]
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')

            # Find the diff.
            in_diff = False
            newlines = 0
            svnmerge_py = False
            msg = ""
            msg_flag = True
            while 1:
                # Walk down the lines.
                i += 1

                # Store the first line of the commit message.
                if msg_flag and search("^[A-Za-z]", lines[i]):
                    # Store the line.
                    msg += lines[i]
                    msg_flag = False

                    # Search for additional first lines.
                    while 1:
                        # Walk down the lines.
                        i += 1

                        # Termination.
                        if not len(lines[i]):
                            break

                        # Add the line.
                        else:
                            msg += " %s" % lines[i]

                # Mark svnmerge.py merges as these do not imply copyright ownership for the comitter.
                if search("^Merged revisions .* via svnmerge from", lines[i]):
                    svnmerge_py = True

                # End of the diff.
                if i >= len(lines) or search('^------------------------------------------------------------------------', lines[i]):
                    break

                # Inside the diff.
                if search('^===================================================================', lines[i]):
                    in_diff = True
                    i += 1
                if not in_diff:
                    continue

                # Binary diff.
                if "Cannot display: file marked as a binary type." in lines[i]:
                    newlines = 1000000
                    break

                # Count the added lines.
                if len(lines[i]) and lines[i][0] == "+" and lines[i][0:3] != "+++":
                    newlines += 1

        # Not a new commit.
        else:
            i += 1
            continue

        # Revisions to exclude.
        if rev.strip() in exclude_rev:
            continue

        # No diff found.
        if not in_diff:
            continue

        # Not significant.
        if newlines < SIG_CODE:
            continue

        # Author switch.
        commit_key = "%s (%s +0000)" % (msg.strip(), date.strftime("%Y-%m-%d %H:%M:%S"))
        for j in range(len(author_switch)):
            if author_switch[j][0] == commit_key:
                committer = author_switch[j][2]

        # Date already exists.
        if committer in committer_info and year in committer_info[committer]:
            continue

        # Skip svnmerge commits.
        if svnmerge_py:
            svnmerge_py = False
            continue

        # A new committer.
        if committer not in committer_info:
            committer_info[committer] = []

        # Store the info.
        committer_info[committer].append(year)

    # Always include the very first commit.
    if init:
        if committer and committer not in committer_info:
            committer_info[committer] = []
        if committer and year not in committer_info[committer]:
            committer_info[committer].append(year)


def validate_copyright(expected_copyright, recorded_copyright):
    """Check if the expected and recorded copyrights match.

    @param expected_copyright:  The unsorted list of expected copyright notices.
    @type expected_copyright:   list of str
    @param recorded_copyright:  The unsorted list of recorded copyright notices.
    @type recorded_copyright:   list of str
    @return:                    True if the copyright notices match, False otherwise.
    @rtype:                     bool
    """

    # Sort the lists.
    expected_copyright.sort()
    recorded_copyright.sort()

    # Replace alternative names in the recorded list.
    for i in range(len(recorded_copyright)):
        for alt in COMMITTER_ALT:
            if search(alt, recorded_copyright[i]):
                recorded_copyright[i] = recorded_copyright[i].replace(alt, COMMITTER_ALT[alt])

    # Compare the lists.
    if expected_copyright == recorded_copyright:
        return True
    return False


def validate_readme(root):
    """Check the validity of the copyright notices in the README file.

    @param root:    The path which should contain the README file.
    @type root:     str
    """

    # Search for the README file.
    if root[-1] == sep:
        readme = root + 'README'
    else:
        readme = root + sep + 'README'
    if not path.exists(readme):
        return

    # Printout.
    sys.stdout.write("Validating: %s\n" % readme)

    # Read the README file data.
    file = open(readme)
    lines = file.readlines()
    file.close()

    # Loop over the file, finding the statements.
    missing = []
    for line in lines:
        if search(": *Copyright \(C\)", line):
            # Strip out the file.
            file_name = line.split(':')[0]

            # Check if the file exists.
            file_path = root + sep + file_name
            if not path.exists(file_path):
                missing.append(file_path)

    # Errors.
    if missing:
        sys.stderr.write("Missing files with copyright notices:\n")
        for i in range(len(missing)):
            sys.stderr.write("    %s\n" % missing[i])



# Execute the script.
if __name__ == '__main__':
    # The path to search.
    if len(sys.argv) == 2:
        directory = sys.argv[1]
    else:
        directory = getcwd()

    # Initial printout.
    sys.stdout.write("\nFSF copyright notice compliance checking for the directory '%s'.\n\n" % directory)
    sys.stdout.flush()

    # Walk through the current dir.
    for root, dirs, files in walk(directory):
        # Validate any copyright statements in the README file, if present.
        validate_readme(root)

        # Directory skip.
        skip = False
        for name in DIR_SKIP:
            if name in root:
                skip = True
                break
        if skip:
            continue

        # Loop over the files.
        for file_name in files:
            # Full path to the file.
            if root[-1] == sep:
                file_path = root + file_name
            else:
                file_path = root + sep + file_name

            # Strip any './' characters from the start.
            if len(file_path) >= 2 and file_path[:2] == './':
                file_path = file_path[2:]

            # Blacklisted file.
            if file_path in BLACKLISTED_FILES:
                continue

            # Check for untracked files.
            if REPOS[-1][1] == 'git':
                pipe = Popen("git ls-files %s --error-unmatch; echo $?" % file_path, shell=True, stderr=PIPE, stdout=PIPE, close_fds=False)
            else:
                pipe = Popen("svn info %s/%s/%s" % (REPOS[-1][0], REPOS[-1][4], file_path), shell=True, stderr=PIPE, stdout=PIPE, close_fds=False)
            err = pipe.stderr.readlines()
            if err:
                continue

            # Get the committer and year information from the repository logs.
            committer_info = {}
            init = True
            for repo_path, repo_type, repo_start, repo_end, repo_head in REPOS:
                if repo_type == 'git':
                    git_log_data(file_path, repo_path=repo_path, exclude_hashes=EXCLUDE[repo_path], author_switch=AUTHOR_SWITCH, committer_info=committer_info, after=repo_start, before=repo_end, init=init)
                else:
                    svn_log_data(file_path, repo_path=repo_path, exclude_rev=EXCLUDE[repo_path], author_switch=AUTHOR_SWITCH, svn_head=repo_head, committer_info=committer_info, after=repo_start, before=repo_end, init=init)
                init = False
            committer_info_cleanup(file_path, committer_info)

            # Format the data as copyright statements.
            expected_copyright = format_copyright(committer_info)

            # Determine the file type.
            type, encoding = mimetypes.guess_type(file_path)
            sys.stdout.write("Checking: %s (mimetype = '%s')\n" % (file_path, type))
            sys.stdout.flush()

            # Parse text files for the current copyright statements.
            recorded_copyright = []
            if type not in BINARY_MIMETYPES and file_path not in BINARY_FILES:
                recorded_copyright = extract_copyright(file_path)

            # Search for missing copyright notices in local README files.
            if not len(recorded_copyright):
                recorded_copyright = extract_copyright_readme(file_name, root)

            # Add any additional copyright notices.
            if file_path in ADDITIONAL_COPYRIGHT:
                for notice in ADDITIONAL_COPYRIGHT[file_path]:
                    expected_copyright.append(notice)

            # Remove false positives and negatives.
            if file_path in FALSE_POS:
                for i in range(len(FALSE_POS[file_path])):
                    for j in reversed(range(len(recorded_copyright))):
                        if FALSE_POS[file_path][i] in recorded_copyright[j]:
                            recorded_copyright.pop(j)
            if file_path in FALSE_NEG:
                for i in range(len(FALSE_NEG[file_path])):
                    for j in reversed(range(len(expected_copyright))):
                        if FALSE_NEG[file_path][i] in expected_copyright[j]:
                            expected_copyright.pop(j)

            # Validate.
            if validate_copyright(expected_copyright, recorded_copyright):
                continue

            # Failure printout.
            sys.stderr.write("File: '%s'\n" % file_path)
            sys.stderr.write("Expected non-matching copyrights:\n")
            for i in range(len(expected_copyright)):
                if expected_copyright[i] not in recorded_copyright:
                    sys.stderr.write("    %s\n" % expected_copyright[i])
            sys.stderr.write("Recorded non-matching copyrights:\n")
            for i in range(len(recorded_copyright)):
                if recorded_copyright[i] not in expected_copyright:
                    sys.stderr.write("    %s\n" % recorded_copyright[i])
            sys.stderr.write("\n")
            sys.stderr.flush()
