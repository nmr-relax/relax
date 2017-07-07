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
from pytz import utc
from re import search
from subprocess import PIPE, Popen
import sys

# Modify the module path.
sys.path.append('.')

# relax module imports.
from lib.io import open_read_file


# Debugging modes.
DEBUG = False
DEBUG_FILE_NAME = ''

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
    "Gary S Thompson": "Gary Thompson",
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
]

# Directories to skip.
DIR_SKIP = [
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

# Stop incorrect svn history by specifying the first commit key of a file (i.e. svn copy but then a complete file replacement).
SVN_START = {
}

# Stop incorrect git history by specifying the first commit key of a misidentified file.
GIT_START = {
    "docs/devel/README":
        "FSF compliant copyright notices for all files in the documentation directory docs/devel/. (2017-07-07 09:12:47 +0200)",
    "docs/devel/svn2git_migration/dups.py":
        "Documented the svn to git repository migration. (2017-07-04 15:45:41 +0200)",
    "docs/devel/svn2git_migration/gitsvn_conversion.sh":
        "Documented the svn to git repository migration. (2017-07-04 15:45:41 +0200)",
    "docs/html/icons/README":
        "FSF compliant copyright notices for all files in the documentation directory docs/html/. (2017-07-07 11:07:40 +0200)",
    "docs/latex/__init__.py":
        "A complete shift from the make build system to the scons build system (and a bug fix). (2006-01-30 06:45:35 +0000)",
    "docs/latex/licence.tex":
        "Created the 'Licence' chapter in the manual. (2005-10-15 12:42:17 +0000)",
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
}

# Commits to exclude as a list of commit keys - the first line of the commit message followed by the ISO date in brackets.
EXCLUDE = [
    # r26537 - b792617f1685700d2c6b8445c0be6c4bed9b7646 - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - the xrange() function has been replaced by range(). (2014-11-11 16:37:03 +0000)",
    # r26536 - 1f5679337742d7910efde47e2efb5965e79ee48d - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - the spacing around commas has been fixed. (2014-11-11 16:28:08 +0000)",
    # r26535 - 42f4ddd479bf98f58541ff54244c1f61e14a9ea1 - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - the \"while 1\" construct has been replaces with \"while True\". (2014-11-11 15:51:21 +0000)",
    # r26531 - e42d086d1995b936ad550979db134a13957e2e00 - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - the filter() function in Python 3 now returns an iterator. (2014-11-11 15:37:13 +0000)",
    # r26523 - d1a81cfcf6cc024405e7e20733a2ed82cd9c7a07 - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - the execfile() function does not exist in Python 3. (2014-11-11 13:55:38 +0000)",
    # r26522 - 88ad7a3f70c2d439d74fa30882fbc5352d82fe30 - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - proper handling of the dict.items() and dict.values() functions. (2014-11-11 13:43:25 +0000)",
    # r26520 - 3e4b40da2a4de8797a54fa2c181aa3882e42c8b2 - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - elimination of all apply() calls. (2014-11-11 13:34:12 +0000)",
    # r26512 - 4c92a001fc36980f58aff7254acdaf1b52abc74e - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - replacement of all `x` with repr(x). (2014-11-11 09:43:30 +0000)",
    # r26511 - c64eb50966737265f3894d4ffe1c188280abf943 - 2to3 automated conversions.
    "Python 3 fixes via 2to3 - elimination of all map and lambda usage in relax. (2014-11-11 09:26:07 +0000)",
    # r26506 - d6d4002cc383a80c684ccc94821abd51f36245a3 - 2to3 automated conversions.
    "Python 3 fixes using 2to3 for the extern.numdifftools package. (2014-11-11 09:04:21 +0000)",
    # r26505 - a8c0b3c3c6b413d484b01c37e975851738436537 - 2to3 automated conversions.
    "Python 3 fixes using 2to3 for the extern.numdifftools package (mainly spacing fixes). (2014-11-11 09:03:19 +0000)",
    # r26502 - ab450172433405c59dbcb573e78cb99bf0f58bfb - 2to3 automated conversions.
    "Python 3 fixes throughout relax, as identified by the 2to3 script. (2014-11-11 08:19:53 +0000)",
    # r26501 - 2f09a2789a54800c7b2105818bbc1115d92d5cb1 - 2to3 automated conversions.
    "Python 3 fixes for the relax codebase. (2014-11-10 22:43:15 +0000)",
    # r25631 - cacf9d2737248d8c73fbf01551068bd6936efab5 - 2to3 automated conversions.
    "Ported r25629 from the 3.3.0 tag. (2014-09-04 14:35:35 +0000)",
    # r25629 - 318236f3a43e9632c0ecdbfa6db190c7e51c3fe3 - 2to3 automated conversions.
    "Python 3 fixes via the 2to3 compatibility script. (2014-09-04 14:31:00 +0000)",
    # r25628 - d9a77ab316518c9474f232dcfd7cb1df069665b5 - 2to3 automated conversions.
    "Ported r25627 from the 3.3.0 tag. (2014-09-04 14:25:48 +0000)",
    # r25627 - 26179f3b1f8074393c5f0b737d331efcab435d04 - 2to3 automated conversions.
    "Python 3 fixes via the 2to3 compatibility script. (2014-09-04 14:24:20 +0000)",
    # r24757 - eb0193edf9a98c5e4f290446b15203121cd57662 - 2to3 automated conversions.
    "Some Python 3 fixes as identified by the 2to3 script. (2014-07-25 15:12:32 +0000)",
    # r24756 - 92ade3b7dd895af8e3f5df3d5af2792e79ba4e6d - 2to3 automated conversions.
    "Some changes as identified by the Python 2 to 3 upgrade script /usr/bin/2to3. (2014-07-25 14:59:22 +0000)",
    # r24397 - 1611ebaa00802a02116c4876b0ea3cbaefe9be2d - 2to3 automated conversions.
    "Python 3 fixes using the 2to3 script. (2014-07-02 07:54:00 +0000)",
    # r24396 - 66c72852005730f46371496151240f0a028ff7cd - 2to3 automated conversions.
    "Python 3 fixes for the entire codebase using the 2to3 script. (2014-07-02 07:50:36 +0000)",
    # r24390 - 91d4d0984148c2a3351df0c3a8b9a0a626e5ac79 - 2to3 automated conversions.
    "General Python 3 fixes via the 2to3 script. (2014-07-02 07:37:42 +0000)",
    # r23263 - 806fa231aaf12222045311dc8d17d44cfd9cca33 - 2to3 automated conversions.
    "Python 3 fixes for all of the relax code base. (2014-05-20 16:02:55 +0000)",
    # r22816 - 89c302bba91132115ca23e213b59a894e21db539 - 2to3 automated conversions.
    "Python 3 fixes throughout the codebase. (2014-04-22 15:49:39 +0000)",
    # r21155 - a6af21049e0cbe825c9609ede890cab76269ed99 - 2to3 automated conversions.
    "A number of Python 3 fixes. (2013-10-17 09:09:48 +0000)",
    # r20785 - d4372c6612d94f2957df246b30ae0e69f9bd73a3 - 2to3 automated conversions.
    "Python 3 fixes. (2013-09-04 07:29:14 +0000)",
    # r20291 - 521787f4e4cefb4a1d7e343d873c75d617a88585 - 2to3 automated conversions.
    "Spacing fixes for the lib.dispersion.ns_2site_star module as determined by the 2to3 program. (2013-07-15 08:03:08 +0000)",
    # r19926 - 8cee1be0ce60f6e6356e2cca58eddb322117721f - 2to3 automated conversions.
    "Python 3 fixes. (2013-06-06 21:19:36 +0000)",
    # r19079 - 1e3e93331a17e1bc34bf5c491e9fd48727de0f2e.
    "Renamed the generic_fns package to pipe_control. (2013-03-23 19:25:55 +0000)",
    # r19028 - 5b8fb0ffdc9ee7e37c75fb067f155496ea733ccb.
    "Renamed the data package to data_store. (2013-03-22 23:25:25 +0000)",
    # r19026 - fa10d72942af42e328ee0952f841f1d78fbe5c66.
    "Renamed the maths_fns package to target_functions. (2013-03-22 23:00:31 +0000)",
    # r19025 - e4d289130c47e9b7cde3e4d4bcedf90a11543212.
    "Copyright updates which should have gone into r19024. (2013-03-22 22:51:05 +0000)",
    # r19024 - 44ac4a86559d295788a0f48815546cfa51bbed21.
    "Renamed the specific_fns package to specific_analyses. (2013-03-22 22:32:08 +0000)",
    # r18804 - 43a4e4daa855bfe80a748cd8cefdfab4e5e638e7 - 2to3 automated conversions.
    "Python 3 updates for the frame_order_testing branch. (2013-03-12 16:30:51 +0000)",
    # r18795 - 253b93e88e45a1dece6e84785dba4ec400a3a592 - 2to3 automated conversions.
    "Python 3 updates and fixes. (2013-03-12 13:27:01 +0000)",
    # r18437 - 480fcd7aaefc77c23e46b2aa9553a5354b6820c6 - 2to3 automated conversions.
    "Spacing fixes as identified by the Python 2to3 conversion program. (2013-02-07 15:49:20 +0000)",
    # r18345 - 8d4ead89d1e5114ede7306dad72a17b1a6adc185 - 2to3 automated conversions.
    "Python 3 fixes for the newly included Geometry.Transformation ScientificPython module. (2013-02-01 11:39:47 +0000)",
    # r17869 - 707467cc9d292a033d8042f5aac279da7a2fed26 - 2to3 automated conversions.
    "Fixes for weird print statements with double brackets generated by the 2to3 Python conversion script. (2012-10-16 16:07:12 +0000)",
    # r17863 - 100ebda169ef3a22a9bd3ac89db593d595fa1737 - 2to3 automated conversions.
    "Python 3 fixes for the script for generating plots of magnetic field lines. (2012-10-16 12:58:50 +0000)",
    # r17855 - c3782248bc420d1e045df389ac6a335db3717212 - 2to3 automated conversions.
    "Converted the branch specific Frame order code to be Python 3 compatible. (2012-10-16 11:31:32 +0000)",
    # r17851 - 43c7e95dc5a48bb7c46a2e9427ffdda73a5b6a00 - 2to3 automated conversions.
    "Python 3 update for the external Sobol library. (2012-10-16 09:38:17 +0000)",
    # r17849 - 6edf77be3bdd2ed8c371ed7a7a2aef3365f32d58 - 2to3 automated conversions.
    "Python 3 fix for the structural API. (2012-10-16 09:30:03 +0000)",
    # r17705 - df158daae9de2b3f8981bf31402830ff86bdcb6b - 2to3 automated conversions.
    "The relax_fit specific analysis module now supports both Python 2 and 3. (2012-10-05 17:48:03 +0000)",
    # r17674 - 1833765c56c4a5ac14be4782609552ee322ec121 - 2to3 automated conversions.
    "Python 2 and 3 support in the generic_fns.relax_data module using 2to3. (2012-10-02 14:12:01 +0000)",
    # r17665 - 759beb06a24f179bf25d876f80e4bff35135757c - 2to3 automated conversions.
    "Better support for both Python 2 and 3 in the relax data store. (2012-10-02 12:25:52 +0000)",
    # r17664 - 8bb164a47b36dbd420adaccf775726aca7d572f2 - 2to3 automated conversions.
    "Python 3 preparation - the relax data store (the data package) now supports both Python 2 and 3. (2012-10-02 12:23:43 +0000)",
    # r17656 - 6a3d5f636ad18d09c2302a300916cefbcbf2cdbd - 2to3 automated conversions.
    "Automatically converted the generic_fns.mol_res_spin module to support both Python 2 and 3. (2012-10-02 09:47:15 +0000)",
    # r17648 - 4c5d80dfb57014195223d8851851162744e7b699 - 2to3 automated conversions.
    "Converted the ScientificPython PDB reader to support both Python 2 and 3. (2012-10-02 08:45:46 +0000)",
    # r17598 - 98ce974c919ded9ea5d5aa83ab45564893d78c3b - 2to3 automated conversions.
    "Python 3 conversions using 2to3. (2012-09-28 14:40:50 +0000)",
    # r17596 - 324105295af06fffe6afe8b081ccd3efdd839f22 - 2to3 automated conversions.
    "Python 3 preparations - removed all usage of the xrange() in the generic_fns package as none are needed. (2012-09-28 11:36:50 +0000)",
    # r17593 - 3be3992ee15693d9f883a11dcac48bbb8ac19a9b - 2to3 automated conversions.
    "Python 3 preparations - the auto_analyses package is now fully Python 2 and 3 compatible. (2012-09-28 09:50:34 +0000)",
    # r17590 - 9bb16c08e49f8b24d997976dbae0f3852d44ab1a - 2to3 automated conversions.
    "Python 3 preparations - the GUI tests are now fully Python 2 and 3 compatible. (2012-09-28 09:43:29 +0000)",
    # r17585 - f9619e67fd4170e96c9be87bf9e6d7f9528baf15 - 2to3 automated conversions.
    "Python 3 preparations - the unit tests are now fully Python 2 and 3 compatible. (2012-09-28 09:09:41 +0000)",
    # r17581 - 7f3444d7db4a25e90edad4a93220abb8396c5c3e - 2to3 automated conversions.
    "Last Python 3 compatibility update for the system tests - they are now both Python 2 and 3 compatible! (2012-09-28 08:58:47 +0000)",
    # r16879 - bd05ab2c14a8c10b399da92a405ce81f2736e476 - 2to3 automated conversions.
    "Reverted the 2to3 changes of r16837 as these are deadly for Python 2.6! (2012-06-12 09:34:42 +0000)",
    # r16837 - 4c5a0d2a1d43aa98142ef3bed85d4e71e6327d7d - 2to3 automated conversions.
    "Python 3 updates for the entire relax code base. (2012-06-11 08:15:21 +0000)",
    # r16534 - 570a7076b71a33b8667a5c4e99decd01ecac4548 - 2to3 automated conversions.
    "Print statement conversions to function calls for Python 3.x. (2012-05-30 15:41:17 +0000)",
    # r15228 - 09f4391582c9ab826e7de192a835e1a7a39209f5 - 2to3 automated conversions.
    "Updates for Python 3.0. (2012-01-24 14:24:40 +0000)",
    # r14812 - cad3aac4d7ca177c4a4129b00f9f80e92a4b26ed - 2to3 automated conversions.
    "Updates for Python 3.0 using the Python 2to3 script. (2011-10-09 11:40:36 +0000)",
    # r12202 - 5012a2b474e539d8564847f1979a98619c99a42d - 2to3 automated conversions.
    "Updates for Python 3.0. (2011-01-11 11:58:33 +0000)",
    # r10860 - 67f4a1a6cf1adb11c6837a1d1d09a26630ce35f7 - 2to3 automated conversions.
    "A python 3.0 fix for the grace module. (2010-02-23 15:06:48 +0000)",
    # r9890  - ab69727887d0d5b006894b44583675d6b6306901 - Pure whitespace changes.
    "Converted tab characters to 8 spaces... (2009-11-19 19:05:50 +0000)",
    # r9456  - 3d46a3a94f8fcd95a22fabb1c418dd4f00fcfebb - 2to3 automated conversions.
    "More updates for Python3k. (2009-09-03 13:52:50 +0000)",
    # r9455  - 5ce17a589766fa238ed4588ebf4874e65684b681 - 2to3 automated conversions.
    "More updates for Python3k. (2009-09-03 13:24:48 +0000)",
    # r9453  - df67bbb6d3d4ff07d4852f513754ab05f9febaa0 - 2to3 automated conversions.
    "Updates for Python3k. (2009-09-03 13:20:11 +0000)",
    # r9452  - c1dc8cdbd7c71f597f3e8b97f866c71131f596c0 - 2to3 automated conversions.
    "Updates for Python3k. (2009-09-03 13:13:50 +0000)",
    # r9443  - 1b85d31298e0fddb5f0497f05b517b53b30ced7b - 2to3 automated conversions.
    "Updates for Python3k. (2009-09-03 12:30:10 +0000)",
    # r9442  - fb87350627c09dfb8ff40d89105c256ac96fb93f - 2to3 automated conversions.
    "Updates for Python3k. (2009-09-03 12:29:19 +0000)",
    # r9439  - d321897bcd64a59b0a957a985203ebabc11d988a - 2to3 automated conversions.
    "Some more print statement updates for Python 3.x. (2009-09-03 12:06:49 +0000)",
    # r9437  - 49096b29bb9de4d01b21abf858fecbcd1ea81138 - 2to3 automated conversions.
    "The whitespace after commas has been enforced (for Python 3.x). (2009-09-03 11:42:16 +0000)",
    # r9350  - 83361abda390570bcd9b98b30aaefed5880acdd2 - 2to3 automated conversions.
    "The Python 2.x idioms have been removed. (2009-08-21 10:07:01 +0000)",
    # r9348  - fdf873ca879f82125b201e584b4198be06c6812c - 2to3 automated conversions.
    "The execfile statement has been replaced with a call to the exec(compile()) function. (2009-08-21 08:50:08 +0000)",
    # r9347  - 18246323e5f762ec5ee21f0165f45b88071add01 - 2to3 automated conversions.
    "The exec statement has been replaced with a call to the exec() function. (2009-08-20 15:48:36 +0000)",
    # r9346  - 48143bb4b9cc97d5cbf50ed2827bb6d3184f4c6a - 2to3 automated conversions.
    "The dictionary keys() return value is now converted into a list. (2009-08-19 16:47:50 +0000)",
    # r9344  - 0d49ff5f482130641892a3930571b548c9a4e9d2 - 2to3 automated conversions.
    "Modified the behaviour of raise statements according to http://www.python.org/dev/peps/pep-3109/. (2009-08-19 15:31:11 +0000)",
    # r9343  - 6c4a44558c3436a8f362b7674428234f42c98c72 - 2to3 automated conversions.
    "Converted all print statements into print() function calls. (2009-08-19 15:18:47 +0000)",
    # r9342  - dc08433c02e77b35cd947b2f7575f08dba5c7ff3 - 2to3 automated conversions.
    "Removed all usages of the has_attr() dictionary method. (2009-08-19 14:09:33 +0000)",
    # r9340  - 25d0d36294f3cc9132d5eb548042d8c688b37792 - 2to3 automated conversions.
    "Replaced all instances of `x` with repr(x). (2009-08-19 13:37:09 +0000)",
    # r894, r895, etc. - 41775d02748d251373dff182ec220c34cbcd8cf0, 358f9909ed75b71a9262e261e6f0eeb86ca9d814, etc.
    "Updating to the archive 'backup_relax_2004-02-24a.tar.bz2'. (2004-02-24 06:45:20 +0000)"
]

# Commits to switch authorship of (e.g. if someone commits someone else's code).
# The data consists of:
#       0 - The comitter's name.
#       1 - The real author.
#       2 - The commit key, consisting of the first line of the commit message followed by the ISO date in brackets.
AUTHOR_SWITCH = [
    # r21008 - 0fa89a69d265a3e39c65c7582fa48e1634db25eb.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed several typo errors of \"Is it selected\"->\"It is selected\". A copy-paste error which have spreaded. (2013-10-07 13:41:55 +0000)"],
    # r21007 - aeae2d81602e411eb2ab38927a1f289a7ca9fd0f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added Tollinger model TSMFK01 to sample scripts. (2013-10-07 13:41:54 +0000)"],
    # r21006 - 652a1f694e1cea9de1405072870efe387212b3f6.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added Tollinger reference. (2013-10-07 13:41:52 +0000)"],
    # r21002 - 25bb33fa1c921d8c8238b087ae2214e4a5b6b624.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Another fix for bibtex string 'cp' instead of 'cj'. (2013-09-13 12:52:33 +0000)"],
    # r21001 - 67c3e1bac2faf2e3f612114c8389793f59c2210d.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for latex bibtex string 'cp' instead of 'cj'. (2013-09-13 12:52:32 +0000)"],
    # r21000 - 82a5c44a23bf5da1783c9b69117bc3d147b27352.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for bibtex warning 'Warning--string name \"mb\" is undefined'. (2013-09-13 12:52:30 +0000)"],
    # r20988 - e053ed7f9b031060a2e44dab1a8d53560158fd58.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for adding TSMFK01 to sample scripts. (2013-09-12 09:08:18 +0000)"],
    # r20987 - 2acd34ca7b89836299b3388e2527126b91c08c73.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added subsection with TSMFK01 model. (2013-09-12 09:08:16 +0000)"],
    # r20986 - 5df428dea43b8006b36e7912d5d273da062c3ddc.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added TSMFK01 to model overview table. (2013-09-12 09:08:15 +0000)"],
    # r20985 - 403716ea6ddc1215e3328aa0276dec6e8d2ef989.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added desc. item for model TSMFK01. (2013-09-12 09:08:14 +0000)"],
    # r20979 - 3bc5db46d827905d8758defa58d4482c2a5e5888.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Modified headers for scripts producing analysis for data which is full or truncated. (2013-09-11 11:06:37 +0000)"],
    # r20978 - f731ce39a9d4bd6927660e81f560e032584619c0.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added systemtests for conversion of kex to k_AB/k_BA for models where kex and pA is present. (2013-09-11 11:03:45 +0000)"],
    # r20977 - 7f97c47a1a7595a9f667e8ca1215140847d26186.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for passing system test on windows with python 32. Precision lowered by 2 decimals. (2013-09-11 11:03:44 +0000)"],
    # r20976 - fd7d7afb308a6b306e9d7ac4f9810418c51e2197.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added system test for testing conversion to k_BA from kex and pA. (2013-09-11 11:03:43 +0000)"],
    # r20975 - 8f3909d219ee35bdf88c368b871474059ffbc9c3.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the conversion to k_BA from kex and pA. (2013-09-11 11:03:41 +0000)"],
    # r20974 - 82b24b0aa7100f7f6ae4c4734d7c83cbe148399c.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed bug, where kex to k_AB where not possible if the model does not contain parameter 'pA'. The conversion is now skipped. (2013-09-11 11:03:40 +0000)"],
    # r20966 - 77e6d3b8c1c78d9b0b7a7545e74ddb2c67d32355.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the conversion to k_AB from kex and pA. k_AB = kex * (1.0 - pA). (2013-09-10 12:39:51 +0000)"],
    # r20965 - f5c8accda0254d9c277f0bfaa821b2b26806a487.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Optimized the target function for model TSMFK. (2013-09-10 12:39:49 +0000)"],
    # r20964 - 347a0637cd8414c78cdb43770ccc24d808d54c77.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added to calculate the tau_cpmg times when model is TSMFK01. (2013-09-10 12:39:47 +0000)"],
    # r20963 - 766b0b157ed6a558586a58555877974eb5745c87.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the write-out of 'dw' and 'k_AB' for model TSMFK01, when performing auto-analysis. (2013-09-10 12:39:44 +0000)"],
    # r20953 - 36f652d1cda77096b639f231ed0c8f4412ba3e9b.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Changed reference to Tollinger et al. instead of Tollinger/Kay. (2013-09-10 06:41:38 +0000)"],
    # r20943 - 955c24fcc2825ca239ff8b815c9d7f9588546b1f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the output from relax after analysis of all models. (2013-09-09 16:33:09 +0000)"],
    # r20942 - a90d59a6501bfec7dc77705c4676607e02d27fd0.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Modified doc string for the script analysing all models for residue L61. (2013-09-09 16:33:01 +0000)"],
    # r20941 - 581e3fb8d6b30d71797c60a9db692fe901c43872.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added to the README file for the 1.01 M GuHCL experiment. (2013-09-09 16:32:59 +0000)"],
    # r20940 - 0caa48355d94a2f741d272e9ebd614b9986f25dd.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added dataset experiment in 1.01 M GuHCl (guanidine hydrochloride). (2013-09-09 16:32:01 +0000)"],
    # r20939 - 38f7e2a2c8cf4089ded79863d1c0d764646b74eb.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Re-run of data after movement of scripts. (2013-09-09 16:31:59 +0000)"],
    # r20938 - 6748094a5b18f6e53f876857e8ac196998f370f5.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Changed scripts after moving data. (2013-09-09 16:31:57 +0000)"],
    # r20937 - 1616eb937851695b8a6f49df2df1850e00bbb989.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Moved files into folder which is specific for the experiment. (2013-09-09 16:30:55 +0000)"],
    # r20936 - d7cfc91e1af21df6cad46fb71717d43915bdcc5f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Modified system test after inclusion of 1M GuHCl dataset. (2013-09-09 16:30:53 +0000)"],
    # r20910 - 6b371ec7b8157b8641ceb85f3677353ce6908c78.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added k_AB to parameters. (2013-09-06 15:04:31 +0000)"],
    # r20905 - fddcf10d696fff3b43b3c72c8855bb0c7fa2958d.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Converted references of ka and kA to k_AB. (2013-09-06 14:12:15 +0000)"],
    # r20897 - 7b60e1e808e47273001f0929a27274e0106500b5.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed expydoc formatting. (2013-09-06 12:42:59 +0000)"],
    # r20896 - ebf3c6980c8e145eafb2b7cc6ea1befa119f510a.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed missing space typo. (2013-09-06 12:42:58 +0000)"],
    # r20893 - e3c86eeaa8dede6bc137e2043b2a08088cda5738.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Modified the script for the full analysis of all models of CPMG type. (2013-09-06 11:57:01 +0000)"],
    # r20892 - e596f3754824249e0975fca31989c882465abb5f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Started a system test for model TSMFK01. (2013-09-06 11:56:59 +0000)"],
    # r20886 - dac6f58571441a7d9e4395b77ca5e4bea05409ee.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for the residue index in the test suite when using the truncated spin system. (2013-09-06 09:43:35 +0000)"],
    # r20885 - 572067083b429ca6b811c783eae12b4bd885a467.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Changed the saved states to the truncated spin system. (2013-09-06 09:43:34 +0000)"],
    # r20884 - ff5b94a987b520fae1edfcfce57d4924039e897f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Changed the initialization script to use the truncated spin system. (2013-09-06 09:43:32 +0000)"],
    # r20883 - 6baf8f7ffb5074f18cc876f0bb63f77f28efd931.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added file which setup a truncated spin system. (2013-09-06 09:43:31 +0000)"],
    # r20882 - b508b95f2523fe841f1af2aacd034f15264fde10.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added \"CR72 full\" test suite for kteilum_fmpoulsen_makke_cpmg_data. (2013-09-06 09:43:30 +0000)"],
    # r20881 - b0cc3978441b9dbce1306c262f454bc5dbe6ce3b.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed values for system test: relax -s Relax_disp.test_kteilum_fmpoulsen_makke_cpmg_data_to_cr72 The test now passes. The values are compared to a relax run with 500 Monte Carlo simulations. (2013-09-06 09:43:29 +0000)"],
    # r20878 - dc643a1cbda5f4eabd3146a66f29094ea120c0c2.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the truncated test data for system test: relax -s Relax_disp.test_kteilum_fmpoulsen_makke_cpmg_data_to_cr72 (2013-09-06 08:26:42 +0000)"],
    # r20877 - 8e6249dc3abd7d44fa0c6f5a3cf60420df1a82bb.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed typo. (2013-09-06 08:26:41 +0000)"],
    # r20876 - 561fd72ef5b4a2986d06b206e1ccf0450f4e507c.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Moved the experiment type setting into per spectra settings. (2013-09-06 08:26:40 +0000)"],
    # r20805 - 2491c3719061d50cb34469c0844e5116cbb57263.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix epydoc HTML markup code. (2013-09-04 13:54:37 +0000)"],
    # r20804 - ff2cc86e13d98c209053c73cbedbbf099c96b1dc.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix trailing spaces. (2013-09-04 13:54:36 +0000)"],
    # r20803 - 94912f057e4825f408781785ad1a69d8b0360e36.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the first system test for model CR72 for the kteilum_fmpoulsen_makke_cpmg_data. (2013-09-04 13:27:19 +0000)"],
    # r20802 - 6b43dc16ca55120a28e17c4f9274edb04037b0fb.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added script files for generating a saved state file with R2eff values. (2013-09-04 13:26:24 +0000)"],
    # r20801 - ed59e318c717bc4be20011eb795a29ee91e2de2e.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Modified the script file for saving of a truncated base_pipe state file. (2013-09-04 13:23:41 +0000)"],
    # r20800 - 32433b400d14dbe7ea9119ccc3d9ee1e0e3d98d0.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Truncated the dataset to only one residue L61. The truncated dataset will be expanded later. (2013-09-04 13:23:07 +0000)"],
    # r20797 - a8fb612b4b60f7cc084bf089df963ce6ab9d9354.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added setup function for the system test of KTeilum_FMPoulsen_MAkke_2006 data. (2013-09-04 11:55:18 +0000)"],
    # r20773 - e01a74e2f0dfb76329655377a03b1efbccc26f2f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Moved the ordering of the model TSMF. Ordering conventions mentioned in this post: http://article.gmane.org/gmane.science.nmr.relax.devel/4500 (2013-09-03 15:07:38 +0000)"],
    # r20767 - 29be71687d5231d51227f70b97987384982044f7.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for unpacking the parameters correctly. (2013-09-03 09:27:05 +0000)"],
    # r20766 - 6f11f86697c8c81a497a64f8b7a5da4c32a7874d.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for r20 should be called r20a. (2013-09-03 09:27:04 +0000)"],
    # r20765 - 0bf6ba5160ebcbec907ec4bde74aaaac322b7908.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Renamed ka parameter to kA, to be consistent with naming conventions. (2013-09-03 09:27:03 +0000)"],
    # r20654 - 3089dbd891d5d59f5d5b36e96f72e1d13c77b6f8.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added support for the TSMFK01 model to the relax_disp.select_model user function back end. (2013-08-20 21:15:39 +0000)"],
    # r20653 - 06d2a6aaf030809e178ab91a167a81bb826eae59.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for converting dw from ppm to rad/s. (2013-08-20 21:15:37 +0000)"],
    # r20652 - 2d01aea46dbd4eedc2c300d280535442ea3180d0.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Copyright of Sebastien Morin and Edward d'Auvergne re-inserted, since tsmfk01 is an alteration of lm63.py and m61.py in same directory. (2013-08-20 21:14:36 +0000)"],
    # r20632 - 0ec7e943fb5f2718959b1fd8e3686515302f74ab.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the TSMFK01 model equations to the relax library: lib/dispersion/tsmfk01.py (2013-08-18 18:23:22 +0000)"],
    # r20631 - 2871a1a56b7d61c3c1bddd01a35b22a50ae8599e.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Created the TSMFK01 model target function for 2-site very-slow exchange model, range of microsecond to second time scale. (2013-08-18 18:23:12 +0000)"],
    # r20630 - 85a257befee0462a33fa69bc42b6ca49c7076fe7.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the TSMFK01 model to the user_functions/relax_disp.py select_model user function frontend. (2013-08-18 18:22:45 +0000)"],
    # r20629 - 1481f9fcfd09a8eeed697d5d76892eb964407938.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "lib/dispersion/lm63.py is copied to tsmfk01.py as part of the implementation of the TSMFK01 model equation. (2013-08-18 16:15:17 +0000)"],
    # r20628 - 0fb1231289b49ea9ec908c3fc2bc3801bddfc37b.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the new 'TSMFK01' model to the specific_analyses\relax_disp\variables.py module. (2013-08-18 14:01:43 +0000)"],
    # r20522 - 7384dcf4167e0b1a038d653dfb618d5907086973.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for two spaces are used after a period in documentation. (2013-08-02 22:08:28 +0000)"],
    # r20521 - 658ca7b73e7a2f96b4a613309ced53bcd8e8000c.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for two spaces are used after a period in documentation. (2013-08-02 22:08:26 +0000)"],
    # r20520 - c2da5e8839330c48290432de2b3291fe87731cb0.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for two spaces are used after a period in documentation. (2013-08-02 22:08:24 +0000)"],
    # r20519 - f8b0a9b0c15e9e28e948df39751d18b73a358b5e.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added a stub GUI describtion in the File formats, for NMRPipe seriesTab. (2013-08-02 20:07:52 +0000)"],
    # r20518 - 332c2c52c191f730698e37c51ffce6f19a0f45d9.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added GUI description for when supplying 'auto' to the spectrum_id. (2013-08-02 20:07:51 +0000)"],
    # r20517 - 21916108cfaf069ed64d9e773b44c8296ef0d030.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added epydoc documentation in pipe_control\spectrum.py .read() when supplying keyword 'auto'. (2013-08-02 20:07:49 +0000)"],
    # r20515 - 834347d2ffc5c03287a193b05848b76de3ace5f1.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Moved the adding function of adding the spectrum id (and ncproc) to the relax data store. (2013-08-02 18:59:02 +0000)"],
    # r20514 - 4ad351fb23e946aa688ce56d959482742d18816e.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Moved checks for matching length of spectrum IDs and intensities columns. (2013-08-02 18:59:00 +0000)"],
    # r20513 - 2526f50094f63f532d15d2fca60f09ea52641f09.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Remove from datalist where empty list starts. These are created where spins are skipped for ID = '?-?'. (2013-08-02 18:58:59 +0000)"],
    # r20512 - 1a38b36a4b9585260f2e9cda6154fd7f5829b73b.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Made it possible to autogenerate spectrum ID's, if spectrum_id='auto'. (2013-08-02 18:58:57 +0000)"],
    # r20511 - 275608ee8b7990126ff0bf0764b74eb7c91d618b.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added check for number of supplied spectra ID's and the number of returned intensity columns. (2013-08-02 18:58:55 +0000)"],
    # r20510 - b33bf75a135653ae76dae1d74612baf9e1fb19e9.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added system test for reading of a multi column formatted NMRPipe seriesTab file. (2013-08-02 18:56:54 +0000)"],
    # r20509 - 86a9fd5b8ce877803abcbee554e37c52e8d7c2a4.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "The ID of spins in seriesTab_multi.ser was not formatted correctly to SPARKY format. (2013-08-02 15:55:23 +0000)"],
    # r20508 - 3bfaef643c82eebce19de2415dde883b2e883670.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Replacing a pointer-reference structure to an empty creation of list of lists. (2013-08-02 15:35:57 +0000)"],
    # r20507 - edd8c338ce24feb1d6aa26385220434e2f630074.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for unit test of nmrpipe. (2013-08-02 15:35:01 +0000)"],
    # r20506 - b0d9f2622263d05b2addc8c7c63c7b3309eaf10f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Adding NMR seriesTab data file for a multiple column / multiple spectrum formatted file. (2013-08-02 12:00:20 +0000)"],
    # r20505 - ac462582c36768dad3f14992f246537c21bce280.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for handling reading spin of type heteronuc='NE1' and proton='HE1'. (2013-08-02 11:53:52 +0000)"],
    # r20504 - c48003924908e100b297ba5ab38dd7a10b354f68.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed the extraction of NMRPipe seriestab data in pipe_control.spectrum.read(). (2013-08-02 11:52:16 +0000)"],
    # r20503 - 37d763daea0e2e815427e0e1aaec87d193b7b472.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Modfied the intensity list to handle intensities for all spectra per spin. (2013-08-02 11:51:50 +0000)"],
    # r20502 - 95f3cc349660ed46d6144f15bb8d84991b350499.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fixed wrong reference to Sparky format. (2013-08-02 11:40:28 +0000)"],
    # r20501 - f90c252ca26eff3544fb267a87701ac57a782831.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Removed the flag for single_spectrum. (2013-08-02 11:39:53 +0000)"],
    # r20446 - 4f2d2ca67f50eb2202961a63d1221356aeaee31b.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Flag change added to reading of NMRPipe SeriesTab. (2013-07-22 06:49:41 +0000)"],
    # r20445 - a9ecea1f75602f8c3f1ded14eb3d5b07c0c8f709.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added flag for single or multiple extraction of spectrum. (2013-07-22 06:48:21 +0000)"],
    # r20444 - e25fb3e8507ad83ed9d163e30c22a8eb9cbedfd0.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Extraction of NMRPipe SeriesTab changed. (2013-07-22 06:47:33 +0000)"],
    # r20442 - bfb1ec5dd9e19b039130db3cf15ce71bd534e65f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Completed NMRPipe SeriesTab reader. (2013-07-22 06:37:58 +0000)"],
    # r20440 - 86ffa9dd18f255cbc78d2e15a71ff831bd5bd2bf.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Progress sr #3043: (https://gna.org/support/index.php?3043) - support for NMRPipe seriesTab format *.ser. (2013-07-22 06:34:04 +0000)"],
    # r20439 - 8767b75cd29ca83bba8f642e4a017b1ad82ad20f.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Progress sr #3043: (https://gna.org/support/index.php?3043) - support for NMRPipe seriesTab format *.ser. (2013-07-22 06:32:54 +0000)"],
    # r20350 - 1818bc2113206949aa13c38fdd5dbfb3b83a0775.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the script from Troels Linnet for backing up the relax wiki via FTP. (2013-07-17 11:58:11 +0000)"],
    # r20341 - f994554d76cddca51433fdf34b6d3e9f1627d60d.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the relax wiki backup script for dumping the MySQL database contents locally. (2013-07-16 15:44:42 +0000)"],
    # r20257 - 45087db216e4da7a019815af0fb1560a8c3231e1.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Imported the missing lib.software.nmrpipe module into pipe_control.spectrum. (2013-06-24 12:58:23 +0000)"],
    # r20256 - 948e4c620829430eb1eac217a967009452493660.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added function destination for auto-detected NMRPipe SeriesTab format. (2013-06-24 10:29:40 +0000)"],
    # r20251 - f9a093e6d6f63dd3accc44ef2cf6f4c4b8924750.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Autodetect format implemented for NMRPipe SeriesTab format implemented. (2013-06-21 18:01:06 +0000)"],
    # r20250 - 6c4f94357d2d081a11acb44d58dad0c24f73da97.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for commit (http://article.gmane.org/gmane.science.nmr.relax.scm/18004). The spin naming was wrong. (2013-06-21 17:46:58 +0000)"],
    # r20249 - 8ddee0172e11b02c6c7393a2e4df8c23ba9dfcbb.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Adding a NMRPipe function file in the folder lib\software\nmrpipe.py. (2013-06-21 16:33:03 +0000)"],
    # r20248 - 18c0143989ccd65bd73e157ede03ffa1911610a8.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Test function for NMRPipe SeriesTab format implemented. (2013-06-21 16:23:24 +0000)"],
    # r20247 - 75455e3f1430480c349c6375c38b49e3088a5537.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Adding a test data file in NMRPipe SeriesTab format. (2013-06-21 15:28:04 +0000)"],
    # r20196 - 57daa1453ebb3291ec812e52c0f809de61be13fc.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for bug #20916, (https://gna.org/bugs/?20916) - Suggestion for python script for PNG/EPS/SVG conversion of grace files. (2013-06-18 15:29:16 +0000)"],
    # r20187 - b9cbcced6dea6b17ee7f05999dc7a618b3219da6.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Fix for bug #20915, (https://gna.org/bugs/?20915) - Failure of Grace opening in MS Windows (2013-06-18 08:00:50 +0000)"],
    # r19895 - a1413d678d500467d8fdaff4db704a919d9ec483.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Added the 'test.seq' file from bug report #20873 (http://gna.org/bugs/?20873). (2013-06-06 15:06:42 +0000)"],
    # r10238 - 2d0bccf99aa99c0d2b2998e4b868b727fee79e81 - End of adding Michael's GUI 1.00.
    ["Edward d'Auvergne", "Michael Bieri",
        "Bug fix for the color_code_noe() method. (2010-01-15 11:40:52 +0000)"],
    # r10237 - c090b5dd1670e2e420d9b92787d47f1ec1051bbd.
    ["Edward d'Auvergne", "Michael Bieri",
        "A number of improvements to the final results analysis. (2010-01-15 10:30:17 +0000)"],
    # r10236 - 76c93c006a70e96921f88b7d1dcbf34d076c73ef.
    ["Edward d'Auvergne", "Michael Bieri",
        "Removed a number of calls to wx.PySimpleApp(). (2010-01-15 10:25:21 +0000)"],
    # r10235 - 280eec8f86a3c7e882203dd247b1df1aab76e271.
    ["Edward d'Auvergne", "Michael Bieri",
        "Simplifications to the file dialog code. (2010-01-15 10:24:40 +0000)"],
    # r10234 - b2746e0609846b4a94094b829e159d32da0ce576.
    ["Edward d'Auvergne", "Michael Bieri",
        "Shift of the GUI calculation code to using the relax API (rather than scripting). (2010-01-15 10:23:13 +0000)"],
    # r10233 - fa72615c4c659cfb9ddba688a0da2bcc3a3c291a.
    ["Edward d'Auvergne", "Michael Bieri",
        "Shifted from using msgbox() to relax_run_ok() to indication proper completion of the calculation. (2010-01-15 10:17:23 +0000)"],
    # r10232 - 05d33ce113973eb36a000f6234d7d6897cc89a62.
    ["Edward d'Auvergne", "Michael Bieri",
        "Removed an event.Skip() call. (2010-01-15 10:04:37 +0000)"],
    # r10231 - 86299d02dc12bef16f4d1179ec7e2de9572ceac7.
    ["Edward d'Auvergne", "Michael Bieri",
        "Expansion of exec_model_free() in preparation for rearrangements in the calc_modelfree module. (2010-01-15 10:03:40 +0000)"],
    # r10230 - 8803f88adc055e1e84789255664318eda1196f1c.
    ["Edward d'Auvergne", "Michael Bieri",
        "Modified how the r1_list and r2_list data structures are handled. (2010-01-15 09:59:06 +0000)"],
    # r10229 - a324f08aaf4e2a3c5c2b779adbade4c8e5fa9982.
    ["Edward d'Auvergne", "Michael Bieri",
        "relax execution now occurs automatically after clicking on the icon. (2010-01-15 09:54:54 +0000)"],
    # r10228 - 8a53d9fcd96e32cbee9f88e239aef8def7f50837.
    ["Edward d'Auvergne", "Michael Bieri",
        "Expanded the print out when exiting to include references and shifted to using question(). (2010-01-15 09:51:59 +0000)"],
    # r10227 - c3dc5b7ca9b24d3a7b51e66cac58dff0f2f86eaf.
    ["Edward d'Auvergne", "Michael Bieri",
        "Added actions for the new menu entries. (2010-01-15 09:46:48 +0000)"],
    # r10226 - 13bd66b7bb6d716d3c331985d4877e87a8253ccd.
    ["Edward d'Auvergne", "Michael Bieri",
        "Comment improvements throughout relax_gui. (2010-01-15 09:45:55 +0000)"],
    # r10225 - d82427c07c09ca3e259f506c13e456109f6a43dd.
    ["Edward d'Auvergne", "Michael Bieri",
        "Added a series of global variables to be used throughout the GUI. (2010-01-15 09:32:40 +0000)"],
    # r10224 - 1026067c47e78b65d8c63ada1470c34f9b004beb.
    ["Edward d'Auvergne", "Michael Bieri",
        "Increased the status bar width. (2010-01-15 09:17:00 +0000)"],
    # r10223 - cbdb7467cd555aca3634b476c09a25dcfafb52b1.
    ["Edward d'Auvergne", "Michael Bieri",
        "Simplified the whichmodel() function (not sure what the removed wx calls did anyway). (2010-01-15 09:12:53 +0000)"],
    # r10222 - 6ca187e562c490618d7c50594ae4ec36c9b0b6a9.
    ["Edward d'Auvergne", "Michael Bieri",
        "Improvements to how unresolved spin systems are handled. (2010-01-15 09:10:26 +0000)"],
    # r10221 - cbc0adf95100a37a7c9b4a3867c4bb6eab116bb2.
    ["Edward d'Auvergne", "Michael Bieri",
        "Updated the global setting dialog. (2010-01-14 18:05:43 +0000)"],
    # r10220 - a20e5ffb4b94d9a044f7f343bed42a9a9c45c156.
    ["Edward d'Auvergne", "Michael Bieri",
        "Properly introduced the import_seq(), settings(), param_file_setting() and reset_setting() methods. (2010-01-14 17:05:47 +0000)"],
    # r10219 - 1cc1f39134858fe3f41c96bc8d328895b40cf57c.
    ["Edward d'Auvergne", "Michael Bieri",
        "Reverted r10214 as the code was not placed in the correct spot! (2010-01-14 17:01:25 +0000)"],
    # r10218 - 7c7e5706472cac6b5525313ca1b945914268cc6f.
    ["Edward d'Auvergne", "Michael Bieri",
        "Bug fix.  Incorrect whitespace was introduced in the last revision (r10217). (2010-01-14 16:46:33 +0000)"],
    # r10217 - 977203b2644848a56ebaa6d92ac4eba0467e27f0.
    ["Edward d'Auvergne", "Michael Bieri",
        "Changes to all the opening and saving file dialogs. (2010-01-14 16:45:18 +0000)"],
    # r10216 - 5c248b83efd842e57e678f4f02729b56f063b019.
    ["Edward d'Auvergne", "Michael Bieri",
        "Switched from using msgbox() to using the specific dir_message() function. (2010-01-14 16:33:36 +0000)"],
    # r10215 - 647bec76129c4d3552216c79aa9e37b05704fe30.
    ["Edward d'Auvergne", "Michael Bieri",
        "Switched from using diropenbox() to opendir(). (2010-01-14 16:27:17 +0000)"],
    # r10214 - 5a5ce803f018eddf06141a0cbf76478f2baf7333.
    ["Edward d'Auvergne", "Michael Bieri",
        "Added the missing import_seq(), settings(), param_file_setting() and reset_setting() methods. (2010-01-14 15:10:02 +0000)"],
    # r10213 - 1053bac83d5d4f28be9336c5c478c7d38915dc77.
    ["Edward d'Auvergne", "Michael Bieri",
        "Expansion and improvements to the menu bar of the main window. (2010-01-14 15:06:06 +0000)"],
    # r10212 - d3bc64efa9b046c9aae36e6d325f30b4ad66715a.
    ["Edward d'Auvergne", "Michael Bieri",
        "Clean up of the gui_bieri.res.results_analysis module (much code deletion) (2010-01-14 14:45:19 +0000)"],
    # r10211 - ed977f50ec633dd050ef070e5cc2a07c500308c5.
    ["Edward d'Auvergne", "Michael Bieri",
        "Another import fix as this was forgotten in the last commit. (2010-01-14 14:06:48 +0000)"],
    # r10210 - 240521cad444abe40f4d67ab0b32cfb8bf7e1e1d.
    ["Edward d'Auvergne", "Michael Bieri",
        "Fixes for the relaxGUI imports. (2010-01-14 13:58:33 +0000)"],
    # r10209 - eb76464f0ac57a59ca668d4f966788366c00e76b.
    ["Edward d'Auvergne", "Michael Bieri",
        "Added version information to the GUI.  This includes a GUI version of 1.00. (2010-01-14 13:47:33 +0000)"],
    # r10206 - ed5807eb07c2189a495efd9075dcbb6a60ee1619 - Start of adding Michael's GUI 1.00.
    ["Edward d'Auvergne", "Michael Bieri",
        "Changed '/' to os.sep to make the Bieri GUI OS independent. (2010-01-14 10:13:05 +0000)"],
    # r10093 - 55ea96c362fe1b7dab61f84b5fca38ed102f9eaf.
    ["Edward d'Auvergne", "Michael Bieri",
        "Added the select_model_calc modules. (2009-12-14 13:48:05 +0000)"],
    # r10092 - 81aab2e3b2c72692a0edab23dbeebc51c40f162e.
    ["Edward d'Auvergne", "Michael Bieri",
        "Added the filedialog and message modules. (2009-12-14 13:41:14 +0000)"],
    # r9879  - 289d0c6a814bf7b23daed580dcbc040d4f208b9e.
    ["Edward d'Auvergne", "Michael Bieri",
        "Initial commit of Michael Bieri's GUI code. (2009-11-19 09:43:44 +0000)"],
]


def committer_info_cleanup(file_path, committer_info):
    """Clean up the committer info data structure.

    @param file_path:       The full file path.
    @type file_path:        str
    @param committer_info:  The committer info data structure, listing the committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @type committer_info:   dict of lists of str
    """

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


def git_log_data(file_path, repo_path=None, exclude=[], start_commit=[], author_switch=[], committer_info={}, after=None, before=None, init=False):
    """Get the committers and years of significant commits from the git log.

    @param file_path:           The full file path to obtain the git info for.
    @type file_path:            str
    @keyword repo_path:         The path to the local copy of the git repository.
    @type repo_path:            str
    @keyword exclude:           A list of commit keys to exclude from the search.  The commit key consists of the first line of the commit message followed by the ISO date in brackets.
    @type exclude:              list of str
    @keyword start_commit:      The starting commit for each file, where 'git log' identifies an incorrect history path.  This is a dictionary with the keys being the file paths and the values being the commit keys (the first line of the commit message followed by the ISO date in brackets).
    @type start_commit:         dict of str
    @keyword author_switch:     List of commit keys and authors to switch the authorship of.  The first element should be the comitter, the second the real comitter, and the third the commit key.  The commit key consists of the first line of the commit message followed by the ISO date in brackets.
    @type author_switch:        list of list of str
    @keyword committer_info:    The committer info data structure, listing the committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @type committer_info:       dict of lists of str
    @keyword after:             Show commits more recent than a specific date.
    @type after:                int or None
    @keyword before:            Show commits older than a specific date.
    @type before:               int or None
    @keyword init:              A flag which if True means that the current repository is the starting repository.
    @type init:                 bool
    """

    # File check.
    full_path = "%s%s%s" % (repo_path, sep, file_path)
    if not path.exists(full_path):
        sys.stderr.write("Warning, file missing from git: %s\n" % full_path)
        return

    # Date restrictions.
    after_opt = ''
    before_opt = ''
    if after:
        after_opt = '--after=%i-01-01' % after
    if before:
        before_opt = '--before=%i-12-31' % before

    # Exec.
    pipe = Popen("git log %s %s --numstat --follow --pretty='%%an Ø %%ad Ø %%H Ø %%s' --date=iso %s" % (after_opt, before_opt, full_path), shell=True, stdout=PIPE, close_fds=False)

    # Get the data.
    lines = pipe.stdout.readlines()
    i = 0
    committer = None
    commit_key = ''
    history_stop = False
    while 1:
        # Termination.
        if i >= len(lines):
            break
        if file_path in start_commit and start_commit[file_path] == commit_key:
            history_stop = True
            if DEBUG:
                sys.stderr.write("  Git:  Terminating to stop false history.  Commit by '%s': %s\n" % (committer, commit_key))
            break

        # Obtain the committer and date info.
        committer, date, commit_hash, subject = lines[i].decode().split(' Ø ')
        year = date.split('-')[0]
        commit_key = "%s (%s)" % (subject.strip(), date)

        # The next line is a committer, so skip the current line.
        if search(' Ø ', lines[i+1].decode()):
            i += 1
            continue

        # Commits to exclude.
        if commit_key in exclude:
            if DEBUG:
                sys.stderr.write("  Git:  Excluded commit by '%s': %s\n" % (committer, commit_key))
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
            if DEBUG:
                sys.stderr.write("  Git:  Not significant by '%s': %s\n" % (committer, commit_key))
            i += 3
            continue

        # Skip svnmerge.py merges for svn->git migration repositories as these do not imply copyright ownership for the comitter.
        if search("^Merged revisions .* via svnmerge from", subject):
            if DEBUG:
                sys.stderr.write("  Git:  Skipping svnmerge.py migrated commit: %s\n" % commit_key)
            i += 3
            continue

        # Author switch.
        for j in range(len(author_switch)):
            if author_switch[j][2] == commit_key:
                committer = author_switch[j][1]

        # Debugging printout.
        if DEBUG:
            sys.stderr.write("  Git:  Commit by '%s': %s\n" % (committer, commit_key))

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

    # Add committer info if the history was stopped, and no such info exists.
    if history_stop and committer and committer not in committer_info:
        committer_info[committer] = []
        committer_info[committer].append(year)

    # Always include the very first commit.
    if init:
        if committer and committer not in committer_info:
            committer_info[committer] = []
        if committer and year not in committer_info[committer]:
            committer_info[committer].append(year)


def svn_log_data(file_path, repo_path=None, exclude=[], start_commit=[], author_switch=[], svn_head=None, committer_info={}, after=None, before=None, init=False):
    """Get the committers and years of significant commits from the svn log.

    @param file_path:           The full file path to obtain the git info for.
    @type file_path:            str
    @keyword repo_path:         The path to the local copy of the svn repository.
    @type repo_path:            str
    @keyword exclude:           A list of commit keys to exclude from the search.  The commit key consists of the first line of the commit message followed by the ISO date in brackets.
    @type exclude:              list of str
    @keyword start_commit:      The starting commit for each file to exclude incorrectly labelled history (i.e. a svn copy followed by complete file replacement).  This is a dictionary with the keys being the file paths and the values being the commit keys (the first line of the commit message followed by the ISO date in brackets).
    @type start_commit:         dict of str
    @keyword author_switch:     List of commit keys and authors to switch the authorship of.  The first element should be the comitter, the second the real comitter, and the third the commit key.  The commit key consists of the first line of the commit message followed by the ISO date in brackets.
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
    """

    # File check.
    full_path = "%s%s%s%s%s" % (repo_path, sep, svn_head, sep, file_path)
    if not path.exists(full_path):
        sys.stderr.write("Warning, file missing from svn: %s\n" % full_path)
        return

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
    pipe = Popen("svn log --diff %s %s" % (date_range, full_path), shell=True, stdout=PIPE, close_fds=False)

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
    commit_key = ''
    history_stop = False
    while 1:
        # Termination.
        if i >= len(lines)-1:
            break
        if file_path in start_commit and start_commit[file_path] == commit_key:
            history_stop = True
            if DEBUG:
                sys.stderr.write("  SVN:  Terminating to stop false history.  Commit by '%s': %s\n" % (committer, commit_key))
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
            date = date.astimezone(tz=utc)

            # Find the diff.
            in_diff = False
            newlines = 0
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

            # Create the commit key.
            commit_key = "%s (%s +0000)" % (msg.strip(), date.strftime("%Y-%m-%d %H:%M:%S"))

        # Not a new commit.
        else:
            i += 1
            continue

        # Commits to exclude.
        if commit_key in exclude:
            if DEBUG:
                sys.stderr.write("  SVN:  Excluded commit by '%s': %s\n" % (committer, commit_key))
            continue

        # No diff found.
        if not in_diff:
            if DEBUG:
                sys.stderr.write("  SVN:  No diff found by '%s': %s\n" % (committer, commit_key))
            continue

        # Not significant.
        if newlines < SIG_CODE:
            if DEBUG:
                sys.stderr.write("  SVN:  Not significant by '%s': %s\n" % (committer, commit_key))
            continue

        # Author switch.
        for j in range(len(author_switch)):
            if author_switch[j][2] == commit_key:
                committer = author_switch[j][1]

        # Date already exists.
        if committer in committer_info and year in committer_info[committer]:
            continue

        # Skip svnmerge commits.
        if search("^Merged revisions .* via svnmerge from", msg):
            if DEBUG:
                sys.stderr.write("  SVN:  Skipping svnmerge.py migrated commit: %s\n" % commit_key)
            continue

        # Debugging printout.
        if DEBUG:
            sys.stderr.write("  SVN:  Commit by '%s': %s\n" % (committer, commit_key))

        # A new committer.
        if committer not in committer_info:
            committer_info[committer] = []

        # Store the info.
        committer_info[committer].append(year)

    # Add committer info if the history was stopped, and no such info exists.
    if history_stop and committer and committer not in committer_info:
        committer_info[committer] = []
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
            # Debugging.
            if DEBUG and DEBUG_FILE_NAME and file_name != DEBUG_FILE_NAME:
                continue

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

            # Determine the file type.
            type, encoding = mimetypes.guess_type(file_path)
            sys.stdout.write("Checking: %s (mimetype = '%s')\n" % (file_path, type))
            sys.stdout.flush()

            # Get the committer and year information from the repository logs.
            committer_info = {}
            init = True
            for repo_path, repo_type, repo_start, repo_end, repo_head in REPOS:
                if repo_type == 'git':
                    git_log_data(file_path, repo_path=repo_path, exclude=EXCLUDE, start_commit=GIT_START, author_switch=AUTHOR_SWITCH, committer_info=committer_info, after=repo_start, before=repo_end, init=init)
                else:
                    svn_log_data(file_path, repo_path=repo_path, exclude=EXCLUDE, start_commit=SVN_START, author_switch=AUTHOR_SWITCH, svn_head=repo_head, committer_info=committer_info, after=repo_start, before=repo_end, init=init)
                init = False
            committer_info_cleanup(file_path, committer_info)

            # Format the data as copyright statements.
            expected_copyright = format_copyright(committer_info)

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
