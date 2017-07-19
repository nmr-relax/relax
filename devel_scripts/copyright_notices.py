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
    'devel_scripts/byte_compile',                               # Trivial script.
    'devel_scripts/grep_tree',                                  # Trivial script.
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
    'sample_scripts/model_free/full_analysis.py',               # Single line file pointing to its renamed location.
    'test_suite/system_tests/scripts/nested_scripting/a.py',    # One line script.
    'test_suite/system_tests/scripts/nested_scripting/b.py',    # One line script.
    'test_suite/system_tests/scripts/nested_scripting/c.py',    # One line script.
    'test_suite/system_tests/scripts/nested_scripting/d.py',    # One line script.
]

# Directories to skip.
DIR_SKIP = [
    '.git',
    '.svn',
    'extern/numdifftools',                                      # External packages distributed with relax.
    'extern/sobol',                                             # External packages distributed with relax.
    'graphics/oxygen_icons',                                    # External source, copyright documented as much as possible.
]

# Add some new mimetypes.
mimetypes.add_type('application/bruker', '.bk')
mimetypes.add_type('application/bruker', '.fid')
mimetypes.add_type('application/bruker', '.ft2')
mimetypes.add_type('application/gromacs', '.trr')
mimetypes.add_type('application/matlab', '.mat')
mimetypes.add_type('application/numpy', '.npy')
mimetypes.add_type('application/octet-stream', '.icns')
mimetypes.add_type('application/pymol', '.pse')
mimetypes.add_type('image/xcf', '.xcf')

# Binary mimetypes.
BINARY_MIMETYPES = [
    'application/bruker',
    'application/gromacs',
    'application/matlab',
    'application/numpy',
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
    "pipe_control/structure/__init__.py":
        "Started to create the structure package. (2008-04-04 09:25:38 +0000)",
    "scons/__init__.py":
        "A number of large changes to the Scons system. (2006-10-12 04:02:01 +0000)",
    "specific_analyses/noe/__init__.py":
        "Shifted the NOE specific analysis code into its own package. (2010-09-17 16:02:20 +0000)",
    "specific_analyses/noe/parameter_object.py":
        "Shifted the NOE specific analysis code into its own package. (2010-09-17 16:02:20 +0000)",
    "specific_analyses/model_free/__init__.py":
        "Created the infrastructure for the splitting up of the 'specific_fns.model_free' module. (2007-03-07 05:56:48 +0000)",
    "specific_analyses/model_free/api.py":
        "Created the infrastructure for the splitting up of the 'specific_fns.model_free' module. (2007-03-07 05:56:48 +0000)",
    "specific_analyses/model_free/data.py":
        "Created the infrastructure for the splitting up of the 'specific_fns.model_free' module. (2007-03-07 05:56:48 +0000)",
    "specific_analyses/model_free/parameter_object.py":
        "Created the infrastructure for the splitting up of the 'specific_fns.model_free' module. (2007-03-07 05:56:48 +0000)",
    "specific_analyses/n_state_model/__init__.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/api.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/data.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/optimisation.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/parameter_object.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/parameters.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/uf.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "test_suite/system_tests/frame_order.py":
        "Added a system test for the frame order 'rigid' model with no tensor rotations and no motion. (2009-09-01 09:52:51 +0000)",
    "test_suite/system_tests/scripts/bug_19785_relax_data_delete.py":
        "Created a system test for catching bug #19785 (https://gna.org/bugs/?19785). (2012-06-05 15:52:56 +0000)",
    "test_suite/system_tests/scripts/relax_data_reset.py":
        "Created the Relax_data.test_reset() system test for testing relax_data.frq and relax_data.type. (2012-06-06 10:52:21 +0000)",
    "test_suite/unit_tests/__init__.py":
        "Execution of both the system/functional tests and unit tests when using the --test-suite option. (2006-11-21 03:47:13 +0000)",
    "test_suite/unit_tests/_lib/__init__.py":
        "Added empty packages to the unit tests for the lib and lib.geometry packages. (2013-03-01 22:59:51 +0000)",
    "test_suite/unit_tests/_lib/test___init__.py":
        "Added the package checking unit tests for the lib package. (2013-03-07 14:56:54 +0000)",
    "test_suite/unit_tests/_lib/_geometry/__init__.py":
        "Added empty packages to the unit tests for the lib and lib.geometry packages. (2013-03-01 22:59:51 +0000)",
    "test_suite/unit_tests/_lib/_geometry/test___init__.py":
        "Added the package checking unit tests for the lib package. (2013-03-07 14:56:54 +0000)",
    "test_suite/unit_tests/_lib/_text/__init__.py":
        "Added empty packages to the unit tests for the lib and lib.geometry packages. (2013-03-01 22:59:51 +0000)",
    "test_suite/unit_tests/_lib/_text/test___init__.py":
        "Created the framework for the unit tests of the lib.text package. (2013-03-07 17:16:08 +0000)",
    "test_suite/unit_tests/_specific_analyses/_consistency_tests/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_consistency_tests/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_frame_order/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_frame_order/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_jw_mapping/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_jw_mapping/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_n_state_model/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_n_state_model/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_noe/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_noe/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_fit/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_fit/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
}

# Stop incorrect git history by specifying the first commit key of a misidentified file.
GIT_START = {
    "dep_check.py":
        "Shifted the dependency checks into a new module. (2008-06-07 22:29:50 +0000)",
    "sconstruct":
        "Added the shell of an Scons script. (2006-01-25 05:10:11 +0000)",
    "setup.py":
        "Added a script for building application packages of relax. (2011-07-28 13:57:47 +0000)",
    "status.py":
        "Addition of the relax status singleton object. (2010-02-25 11:36:30 +0000)",
    "auto_analyses/__init__.py":
        "Spun out the automatic model-free protocol code from the full_analysis.py script. (2010-01-25 10:13:06 +0000)",
    "data_store/exp_info.py":
        "Created a data container for storing experimental details. (2009-10-09 18:24:11 +0000)",
    "data_store/gui.py":
        "Created some data structures for holding all the GUI specific information. (2010-01-26 16:27:29 +0000)",
    "devel_scripts/memory_management/GUI_uf_align_tensor_init.py":
        "Created a script for testing the memory management when calling the time GUI user function. (2015-02-04 13:18:26 +0000)",
    "devel_scripts/memory_management/GUI_uf_time.py":
        "Created a script for testing the memory management when calling the time GUI user function. (2015-02-04 13:18:26 +0000)",
    "docs/__init__.py":
        "A complete shift from the make build system to the scons build system (and a bug fix). (2006-01-30 06:45:35 +0000)",
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
    "extern/__init__.py":
        "The 'extern' package is now a proper package - the __init__.py file has been added! (2011-06-03 15:54:51 +0000)",
    "graphics/__init__.py":
        "The graphics directory has been converted into a Python package. (2012-05-04 09:13:13 +0000)",
    "graphics/analyses/consistency_testing/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/analyses/dispersion/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/analyses/model_free/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/analyses/model_free/ellipsoid.pdb":
        "Created some initial graphics for the model-free analysis. (2011-06-22 07:19:39 +0000)",
    "graphics/misc/n_state_model/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/misc/pymol/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/misc/Rosenbrock_function/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/relax_icons/png/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/relax_icons/png/chemical_shift/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/relax_icons/png/frq/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/relax_icons/png/jw_mapping/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/relax_icons/png/model_free/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/relax_icons/svg/j_coupling.svg":
        "Added some basic initial relax icons for J couplings. (2013-06-13 15:17:14 +0000)",
    "graphics/screenshots/noe_analysis/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/screenshots/r1_analysis/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/screenshots/spin_viewer/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/wizards/dipole_pair/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/wizards/j_coupling.svg":
        "Created some basic initial GUI wizard graphics for J couplings. (2013-06-13 15:51:44 +0000)",
    "graphics/wizards/molmol/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/wizards/pymol/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/wizards/spectrum/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/wizards/structure/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "graphics/wizards/value/README":
        "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    "gui/__init__.py":
        "Converted the relaxGUI code into a Python package. (2009-11-19 10:18:50 +0000)",
    "gui/analyses/__init__.py":
        "Converted the analyses/ and execution/ directories into Python packages by adding __init__.py files. (2010-01-22 16:07:11 +0000)",
    "gui/analyses/auto_r1.py":
        "Create the Auto_r1 class for building the automatic R1 analysis frame. (2010-01-28 16:28:19 +0000)",
    "gui/analyses/auto_r2.py":
        "Created the new automatic R2 analysis frame. (2010-01-29 09:34:02 +0000)",
    "gui/analyses/base.py":
        "Shifted the title and subtitle creation for the NOE frame into a base class for all frames to use. (2011-06-09 10:29:21 +0000)",
    "gui/analyses/elements/__init__.py":
        "Rearrangements of the gui.analyses package. (2013-04-20 17:00:28 +0000)",
    "gui/base_classes.py":
        "Added a module for the GUI base classes. (2010-01-28 11:36:42 +0000)",
    "gui/components/__init__.py":
        "Shifted the peak list selection GUI component used in the R1 and R2 into its own class. (2010-01-29 14:46:04 +0000)",
    "gui/components/menu.py":
        "Converted the menu build_menu_item() method into a function of gui.components.menu. (2011-07-20 20:08:19 +0000)",
    "gui/input_elements/__init__.py":
        "Split up the gui.wizard_elements into a number of modules in the new gui.input_elements package. (2012-05-16 16:21:24 +0000)",
    "gui/spin_viewer/__init__.py":
        "Shifted the spin viewer window code into its own package. (2011-07-06 10:40:02 +0000)",
    "gui/spin_viewer/splitter.py":
        "Split up the spin viewer code into many more modules. (2011-07-06 12:26:24 +0000)",
    "gui/uf_objects.py":
        "Created a base class for the user function GUI elements. (2010-12-07 00:04:46 +0000)",
    "gui/wizards/__init__.py":
        "Created the gui.wizards package for holding all of the relax wizards. (2013-04-21 14:36:02 +0000)",
    "gui/wizards/wiz_objects.py":
        "Created a base class for the user function GUI elements. (2010-12-07 00:04:46 +0000)",
    "lib/__init__.py":
        "Initialised a new package called 'lib'. (2013-03-01 22:44:16 +0000)",
    "lib/alignment/__init__.py":
        "Created the empty lib.nmr package of the relax library. (2013-03-22 21:58:18 +0000)",
    "lib/alignment/paramag_centre.py":
        "Preparation for the optimisation of the paramagnetic centre in the N-state model. (2010-07-02 15:39:21 +0000)",
    "lib/alignment/rdc.py":
        "Created an empty module to dump RDC related computational functions into. (2008-07-09 13:49:39 +0000)",
    "lib/ansi.py":
        "Shifted the terminal colouring ANSI escape sequences into their own 'ansi' module. (2012-04-17 16:49:22 +0000)",
    "lib/auto_relaxation/__init__.py":
        "Created the empty packages lib.auto_relaxation and lib.spectral_densities. (2013-03-23 08:14:51 +0000)",
    "lib/checks.py":
        "Created a special Check class based on the strategy design pattern. (2014-09-26 09:31:29 +0000)",
    "lib/chemical_shift/__init__.py":
        "Created the empty lib.chemical_shift package. (2013-03-23 10:08:22 +0000)",
    "lib/compat.py":
        "Created a new module for simultaneous Python 2 and 3 support in relax called 'compat'. (2012-10-02 08:35:22 +0000)",
    "lib/curve_fit/__init__.py":
        "Created the lib.curve_fit package and associated unit tests. (2013-04-04 14:40:15 +0000)",
    "lib/curve_fit/exponential.py":
        "Created the new lib.curve_fit.exponential module for exponential curve-fitting. (2013-04-04 15:15:33 +0000)",
    "lib/diffusion/__init__.py":
        "Created the empty lib.diffusion package. (2013-03-23 08:28:12 +0000)",
    "lib/diffusion/correlation_time.py":
        "Updating to the archive 'backup_relax_2004-03-05.tar.bz2'. (2004-03-04 15:22:38 +0000)",
    "lib/diffusion/direction_cosine.py":
        "Updating to the archive 'backup_relax_2004-03-09.tar.bz2'. (2004-03-08 15:24:39 +0000)",
    "lib/diffusion/weights.py":
        "Updating to the archive 'backup_relax_2004-03-05.tar.bz2'. (2004-03-04 15:22:38 +0000)",
    "lib/dispersion/__init__.py":
        "Created the empty lib.dispersion package. (2013-03-23 10:06:19 +0000)",
    "lib/dispersion/b14.py":
        "Added empty b14.py to relax library lib/dispersion/b14.py. (2014-05-01 07:20:32 +0000)",
    "lib/dispersion/matrix_exponential.py":
        "Implemented the lib.linear_algebra.matrix_exponential.matrix_exponential() function. (2013-10-15 09:07:54 +0000)",
    "lib/dispersion/two_point.py":
        "Created the lib.dispersion.equations module. (2013-03-27 16:49:33 +0000)",
    "lib/float.py":
        "Added a skeleton for the isnan() and isinf() functions.  Two dummy functions have been created and the code in 'specific_fns/model_free.py' now points to these. (2006-09-03 06:06:12 +0000)",
    "lib/frame_order/__init__.py":
        "Created the empty lib.frame_order package. (2013-03-23 08:18:10 +0000)",
    "lib/frame_order/format.py":
        "Added a stub package for Frame Order related calculation code. (2009-06-17 17:36:36 +0000)",
    "lib/frame_order/free_rotor.py":
        "Spun out all of the frame order model specific code in frame_order_matrix_ops to separate modules. (2012-07-27 10:41:26 +0000)",
    "lib/frame_order/matrix_ops.py":
        "Added a stub package for Frame Order related calculation code. (2009-06-17 17:36:36 +0000)",
    "lib/frame_order/variables.py":
        "Created the new specific_analyses.frame_order.variables module. (2014-07-09 08:03:17 +0000)",
    "lib/geometry/__init__.py":
        "Initialised the lib.geometry package. (2013-03-01 22:46:56 +0000)",
    "lib/geometry/coord_transform.py":
        "Created a new module for performing coordinate transformations. (2010-08-06 09:29:23 +0000)",
    "lib/geometry/lines.py":
        "Created the lib.geometry.lines module for performing geometric operations with lines. (2013-03-07 14:46:56 +0000)",
    "lib/geometry/vectors.py":
        "Spun out the maths_fns.rotation_matrix.random_rot_axis() function into its own module. (2013-01-10 14:15:55 +0000)",
    "lib/linear_algebra/__init__.py":
        "Created the empty lib.algebra package - this is for advanced linear algebra not present in numpy. (2013-03-23 08:41:28 +0000)",
    "lib/linear_algebra/matrix_exponential.py":
        "Implemented the lib.linear_algebra.matrix_exponential.matrix_exponential() function. (2013-10-15 09:07:54 +0000)",
    "lib/linear_algebra/matrix_power.py":
        "Added the missing mpower() function as lib.linear_algebra.matrix_power.square_matrix_power(). (2013-07-12 15:12:38 +0000)",
    "lib/list.py":
        "Created the new lib.list module with the function count_unique_elements(). (2013-04-03 14:42:32 +0000)",
    "lib/mathematics.py":
        "Created the lib.mathematics relax library module. (2013-05-02 10:15:04 +0000)",
    "lib/order/__init__.py":
        "Created the empty lib.order package. (2013-03-23 09:07:42 +0000)",
    "lib/order/order_parameters.py":
        "Added the stub function maths_fns.order_parameters.iso_cone_S_to_cos_theta(). (2010-02-03 10:22:00 +0000)",
    "lib/physical_constants.py":
        "Shifted the physical constants h, hbar, and mu0 from the PipeContainer class to their own module. (2007-03-08 05:40:11 +0000)",
    "lib/plotting/__init__.py":
        "Created the empty lib.plotting package. (2014-12-18 10:05:44 +0000)",
    "lib/plotting/api.py":
        "Created the lib.plotting API function correlation_matrix(). (2014-12-18 11:05:07 +0000)",
    "lib/plotting/gnuplot.py":
        "Implemented a very basic gnuplot backend for the correlation_matrix() plotting API function. (2014-12-18 11:07:24 +0000)",
    "lib/plotting/text.py":
        "Shifted the matrix output of the structure.atomic_fluctuations user function into lib.plotting.text. (2014-12-18 11:23:42 +0000)",
    "lib/plotting/veusz.py":
        "Created the empty lib.plotting.veusz module for graphing using Veusz (http://home.gna.org/veusz/). (2015-02-06 11:05:31 +0000)",
    "lib/sequence_alignment/__init__.py":
        "Created an empty lib.sequence_alignment relax library package. (2015-01-21 09:07:23 +0000)",
    "lib/software/__init__.py":
        "Created the empty lib.software package. (2013-03-26 11:36:55 +0000)",
    "lib/software/opendx/__init__.py":
        "Created the empty lib.opendx package. (2013-03-23 20:29:03 +0000)",
    "lib/spectral_densities/__init__.py":
        "Created the empty packages lib.auto_relaxation and lib.spectral_densities. (2013-03-23 08:14:51 +0000)",
    "lib/spectrum/__init__.py":
        "Shifted code from pipe_control.spectrum to the new lib.spectrum.peak_list relax library module. (2013-08-09 12:58:32 +0000)",
    "lib/spectrum/nmrpipe.py":
        "Adding a NMRPipe function file in the folder lib\software\\nmrpipe.py. (2013-06-21 16:33:03 +0000)",
    "lib/structure/__init__.py":
        "Initialised the lib.structure package - this is currently empty. (2013-03-20 16:09:55 +0000)",
    "lib/structure/cones.py":
        "Added a new module for holding class objects defining different cone types. (2010-03-09 10:44:48 +0000)",
    "lib/structure/files.py":
        "Created the new lib.structure.files module. (2014-07-02 12:42:51 +0000)",
    "lib/structure/internal/__init__.py":
        "Created the empty lib.structure.internal package for holding the internal structural object. (2013-03-24 15:34:53 +0000)",
    "lib/structure/internal/displacements.py":
        "Started to create the structural object and the API for accessing, creating, modifying info. (2008-04-04 10:01:52 +0000)",
    "lib/structure/internal/selection.py":
        "Created a special internal structural object selection object. (2014-09-23 16:02:05 +0000)",
    "lib/structure/represent/__init__.py":
        "Created the empty lib.structure.represent package. (2013-03-24 15:56:29 +0000)",
    "lib/text/__init__.py":
        "Created the lib.text package for text manipulation. (2013-03-07 14:39:38 +0000)",
    "lib/text/gui.py":
        "Created the new gui.text module for holding all of the unicode text for the GUI. (2013-09-06 16:39:56 +0000)",
    "lib/text/progress.py":
        "Created a basic text based progress meter in the new lib.text.progress module. (2014-09-22 09:15:17 +0000)",
    "lib/text/sectioning.py":
        "Created the new lib.text.sectioning module for formatting titles, subtitles and other sectioning text. (2013-03-20 13:13:27 +0000)",
    "lib/text/string.py":
        "The script user function GUI element is now functional. (2010-12-06 23:10:30 +0000)",
    "lib/text/table.py":
        "Created a base class for the user function classes. (2009-08-21 15:23:56 +0000)",
    "lib/timing.py":
        "Created the time user function. (2014-07-15 10:36:47 +0000)",
    "lib/xml.py":
        "Added a module for the creation and parsing of XML documents representing a data pipe. (2008-06-22 11:21:23 +0000)",
    "multi/memo.py":
        "Shifted the Memo object into its own module. (2012-02-29 15:23:41 +0000)",
    "pipe_control/__init__.py":
        "Updating to the archive 'backup_relax_2004-02-24.tar.bz2'. (2004-02-23 15:14:03 +0000)",
    "pipe_control/domain.py":
        "Created the domain user function back end. (2011-12-05 14:52:45 +0000)",
    "pipe_control/error_analysis.py":
        "Updating to the archive 'backup_relax_2004-06-18.tar.bz2'. (2004-06-17 15:45:42 +0000)",
    "pipe_control/noesy.py":
        "Created an empty module for NOESY data. (2008-12-08 15:48:34 +0000)",
    "pipe_control/pipes.py":
        "Updating to the archive 'backup_relax_2004-02-23.tar.bz2'. (2004-02-23 08:00:39 +0000)",
    "pipe_control/plotting.py":
        "Created the pipe_control.plotting module. (2013-04-08 13:07:50 +0000)",
    "pipe_control/result_files.py":
        "Created the new generic_fns.result_files for standardising the handling of results files. (2012-09-18 14:15:01 +0000)",
    "pipe_control/spectrometer.py":
        "Wrote the spectrometer frequency setting function generic_fns.frq.set(). (2008-08-11 11:59:01 +0000)",
    "pipe_control/statistics.py":
        "Created the empty pipe_control.statistics module. (2015-02-05 14:45:47 +0000)",
    "pipe_control/structure/__init__.py":
        "Started to create the structure package. (2008-04-04 09:25:38 +0000)",
    "pipe_control/system.py":
        "Adding a new file at lib/system.py. (2016-04-02 10:52:04 +0000)",
    "prompt/doc_string.py":
        "Rewrite of the Grace plotting functions. (2005-06-26 14:40:34 +0000)",
    "prompt/uf_docstring.py":
        "Created a base class for the user function classes. (2009-08-21 15:23:56 +0000)",
    "prompt/uf_objects.py":
        "Added the prompt.objects module which contains the user function auto-generation objects. (2012-05-03 20:12:28 +0000)",
    "sample_scripts/model_free/back_calculate.py":
        "Added a sample script for back-calculating relaxation data from a model-free results file. (2015-11-23 09:20:47 +0000)",
    "sample_scripts/xh_vector_dist.py":
        "Added a sample script for the creation of the PDB representation of the XH bond vectors. (2008-12-03 21:56:23 +0000)",
    "scons/__init__.py":
        "Ported r2618 to r2632 from the 1.2 line. (2006-10-12 07:43:25 +0000)",
    "specific_analyses/__init__.py":
        "Updating to the archive 'backup_relax_2004-02-24.tar.bz2'. (2004-02-23 15:14:03 +0000)",
    "specific_analyses/frame_order/__init__.py":
        "Converted all of the specific analysis modules into packages. (2013-05-15 15:38:19 +0000)",
    "specific_analyses/model_free/__init__.py":
        "Created the infrastructure for the splitting up of the 'specific_fns.model_free' module. (2007-03-07 05:56:48 +0000)",
    "specific_analyses/model_free/api.py":
        "Created the infrastructure for the splitting up of the 'specific_fns.model_free' module. (2007-03-07 05:56:48 +0000)",
    "specific_analyses/model_free/bmrb.py":
        "Added a stub bmrb_write() model-free method. (2009-01-11 13:01:28 +0000)",
    "specific_analyses/n_state_model/__init__.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/api.py":
        "Created the framework for the N-state model specific code. (2007-12-20 15:50:39 +0000)",
    "specific_analyses/n_state_model/parameter_object.py":
        "Standardised all of the parameter list objects for the specific analyses. (2014-04-09 16:35:41 +0000)",
    "specific_analyses/noe/__init__.py":
        "Shifted the NOE specific analysis code into its own package. (2010-09-17 16:02:20 +0000)",
    "specific_analyses/noe/parameter_object.py":
        "Standardised all of the parameter list objects for the specific analyses. (2014-04-09 16:35:41 +0000)",
    "specific_analyses/relax_disp/catia.py":
        "Started to create the relax_disp.catia_input user function. (2013-09-12 16:39:21 +0000)",
    "specific_analyses/relax_disp/model.py":
        "Shifted out all of the variables and dispersion data specific code into separate modules. (2013-05-03 09:51:38 +0000)",
    "specific_analyses/relax_disp/optimisation.py":
        "Created the empty specific_analyses.relax_disp.optimisation module. (2013-09-11 08:34:17 +0000)",
    "specific_analyses/relax_fit/checks.py":
        "Created the new specific_analyses.relax_fit.checks module. (2014-11-29 17:55:20 +0000)",
    "specific_analyses/hybrid.py":
        "This is a file that should have been included in r2445. (2006-04-05 08:09:16 +0000)",
    "target_functions/dimensions.h":
        "Standardisation of the array dimensionality in the target function C code. (2014-08-26 16:25:19 +0000)",
    "target_functions/n_state_model.py":
        "Added the basic framework for the N-state model target function. (2008-01-08 16:17:43 +0000)",
    "target_functions/potential.py":
        "Created a module for calculating different optimisation/energy potentials. (2009-01-29 15:40:07 +0000)",
    "test_suite/__init__.py":
        "Creation of a framework for a relax test suite to check for regressions and new bugs. (2006-03-24 01:41:10 +0000)",
    "test_suite/formatting.py":
        "Changes to the output formatting functions of the test suite. (2007-01-13 10:00:17 +0000)",
    "test_suite/relax_test_loader.py":
        "The RelaxTestLoader has been added as a replacement for unittest.TestLoader. (2011-01-04 09:45:41 +0000)",
    "test_suite/relax_test_runner.py":
        "Created the framework for a new unittest runner to replace TextTestRunner. (2008-01-04 16:26:07 +0000)",
    "test_suite/test_suite_runner.py":
        "Execution of both the system/functional tests and unit tests when using the --test-suite option. (2006-11-21 03:47:13 +0000)",
    "test_suite/gui_tests/base_classes.py":
        "Shifted the GUI test check_exceptions() method into a base class for all tests to use. (2011-06-29 17:58:36 +0000)",
    "test_suite/gui_tests/dead_uf_pages.py":
        "Created the Dead_uf_pages.test_mol_create() GUI test demonstrating a failure in the user functions. (2012-05-29 07:14:46 +0000)",
    "test_suite/gui_tests/model_free.py":
        "Started to construct the model-free auto-analysis GUI test. (2011-07-26 07:31:41 +0000)",
    "test_suite/gui_tests/n_state_model.py":
        "Added all of the N-state model system tests as GUI tests. (2012-05-22 12:03:46 +0000)",
    "test_suite/gui_tests/noe.py":
        "Activated the NOE analysis system test. (2008-10-07 19:37:24 +0000)",
    "test_suite/gui_tests/rx.py":
        "Activated the NOE analysis system test. (2008-10-07 19:37:24 +0000)",
    "test_suite/gui_tests/state.py":
        "Created a GUI test for loading a relax save state file created in a non-GUI mode. (2011-07-20 13:00:05 +0000)",
    "test_suite/system_tests/__init__.py":
        "Creation of a framework for a relax test suite to check for regressions and new bugs. (2006-03-24 01:41:10 +0000)",
    "test_suite/system_tests/angles.py":
        "Implemented a test for the test suite which catches bug #7224 (https://gna.org/bugs/?7224). (2006-09-30 08:08:59 +0000)",
    "test_suite/system_tests/base_classes.py":
        "Created the SystemTestCase base class for all the system tests to use. (2010-01-25 17:04:17 +0000)",
    "test_suite/system_tests/bmrb.py":
        "Created a system test for the writing and reading of a BRMB STAR formatted file. (2009-01-11 11:20:07 +0000)",
    "test_suite/system_tests/chemical_shift.py":
        "Created the Chemical_shift.test_read_sparky system test for the reading of chemical shifts. (2013-08-21 08:28:17 +0000)",
    "test_suite/system_tests/dasha.py":
        "Started to add system tests for model-free analysis using Modelfree4. (2008-07-28 19:36:19 +0000)",
    "test_suite/system_tests/interatomic.py":
        "Created the new Interatomic system test class for testing out the interatomic data containers. (2012-06-28 12:17:56 +0000)",
    "test_suite/system_tests/load_spins.py":
        "Added a system test for the loading of spins from a small molecule. (2008-04-23 16:44:01 +0000)",
    "test_suite/system_tests/model_elimination.py":
        "Created a system test for model elimination of a model-free model. (2008-10-05 08:49:03 +0000)",
    "test_suite/system_tests/mol_res_spin.py":
        "Created a system test Mol_res_spin.test_residue_delete() demonstrating a failure of the user function. (2012-05-16 10:25:52 +0000)",
    "test_suite/system_tests/n_state_model.py":
        "Created the framework for adding system/functional tests for the N-state model. (2008-01-07 16:03:27 +0000)",
    "test_suite/system_tests/noe.py":
        "Activated the NOE analysis system test. (2008-10-07 19:37:24 +0000)",
    "test_suite/system_tests/noe_restraints.py":
        "Added the system test framework for NOE restraint reading tests. (2008-12-09 09:45:58 +0000)",
    "test_suite/system_tests/palmer.py":
        "Started to add system tests for model-free analysis using Modelfree4. (2008-07-28 19:36:19 +0000)",
    "test_suite/system_tests/pcs.py":
        "Created a system test with RDC data for loading RDCs from a file with spin ID strings at the start. (2011-10-17 16:31:38 +0000)",
    "test_suite/system_tests/peak_lists.py":
        "Added the framework for system tests for supporting NMRView within relax. (2008-07-03 18:47:48 +0000)",
    "test_suite/system_tests/pipes.py":
        "Creation of a framework for a relax test suite to check for regressions and new bugs. (2006-03-24 01:41:10 +0000)",
    "test_suite/system_tests/rdc.py":
        "Created a system test with RDC data for loading RDCs from a file with spin ID strings at the start. (2011-10-17 16:31:38 +0000)",
    "test_suite/system_tests/relax_data.py":
        "Created a very basic system test for the relax_data.back_calc() user function. (2011-03-03 14:19:47 +0000)",
    "test_suite/system_tests/results.py":
        "Wrote a system test for writing an empty results file. (2008-07-03 22:50:37 +0000)",
    "test_suite/system_tests/sequence.py":
        "Creation of a framework for a relax test suite to check for regressions and new bugs. (2006-03-24 01:41:10 +0000)",
    "test_suite/system_tests/spectrum.py":
        "Added the framework for system tests for supporting NMRView within relax. (2008-07-03 18:47:48 +0000)",
    "test_suite/system_tests/state.py":
        "Created a system test for the saving, loading, saving, and loading again of the system state. (2008-10-12 09:40:43 +0000)",
    "test_suite/system_tests/structure.py":
        "Added a system test to check the loading of a PDB file using the information in a results file. (2008-09-26 13:47:09 +0000)",
    "test_suite/system_tests/unit_vectors.py":
        "Added a simple system test for the calculation of unit XH bond vectors. (2008-09-25 13:48:24 +0000)",
    "test_suite/system_tests/value.py":
        "Created the new Value system test class with the first test Value.test_value_copy. (2013-05-03 17:18:42 +0000)",
    "test_suite/system_tests/scripts/__init__.py":
        "Converted the system test scripts directory into a Python package. (2012-01-27 10:59:24 +0000)",
    "test_suite/system_tests/scripts/frame_order/__init__.py":
        "Converted the frame order system test scripts directory into a Python package. (2012-01-27 11:00:49 +0000)",
    "test_suite/system_tests/scripts/frame_order/cam/__init__.py":
        "Converted the CaM frame order system test script directory into a Python package. (2012-01-27 11:02:12 +0000)",
    "test_suite/unit_tests/__init__.py":
        "Execution of both the system/functional tests and unit tests when using the --test-suite option. (2006-11-21 03:47:13 +0000)",
    "test_suite/unit_tests/align_tensor_testing_base.py":
        "Added the shell of the alignment tensor unit test base class. (2007-11-21 13:29:08 +0000)",
    "test_suite/unit_tests/base_classes.py":
        "Created the SystemTestCase base class for all the system tests to use. (2010-01-25 17:04:17 +0000)",
    "test_suite/unit_tests/diffusion_tensor_testing_base.py":
        "Set up the base class for unit tests of the diffusion_tensor modules. (2007-11-25 14:11:49 +0000)",
    "test_suite/unit_tests/minimisation_testing_base.py":
        "Created the base class for the unit tests of the prompt and generic_fns minimisation functions. (2008-01-07 10:05:40 +0000)",
    "test_suite/unit_tests/model_free_testing_base.py":
        "Added the framework for unit tests of the model-free user function args. (2008-01-13 11:31:20 +0000)",
    "test_suite/unit_tests/molecule_testing_base.py":
        "Added to empty unit test modules. (2007-03-17 01:58:48 +0000)",
    "test_suite/unit_tests/n_state_model_testing_base.py":
        "Wrote the empty N-state model base class for the unit tests. (2008-01-09 16:45:04 +0000)",
    "test_suite/unit_tests/package_checking.py":
        "Shifted the test___all__() method into the PackageTestCase base class. (2009-09-02 13:37:30 +0000)",
    "test_suite/unit_tests/relax_data_testing_base.py":
        "Added the base class framework for testing the relaxation data modules. (2007-11-26 18:35:34 +0000)",
    "test_suite/unit_tests/sequence_testing_base.py":
        "Added the base class for the unit tests of the prompt.sequence and generic_fns.sequence modules. (2007-11-21 22:57:08 +0000)",
    "test_suite/unit_tests/spin_testing_base.py":
        "Added to empty unit test modules. (2007-03-17 01:58:48 +0000)",
    "test_suite/unit_tests/state_testing_base.py":
        "Added the framework for implementing unit tests for the generic_fns.state module. (2007-11-20 16:41:59 +0000)",
    "test_suite/unit_tests/structure_testing_base.py":
        "Wrote 16 unit tests for all args of all structure user functions. (2008-01-06 11:32:25 +0000)",
    "test_suite/unit_tests/value_testing_base.py":
        "Added the base class for the tests of both the 'prompt.value' and 'generic_fns.value' modules. (2007-12-09 11:17:33 +0000)",
    "test_suite/unit_tests/_auto_analyses/__init__.py":
        "Added a __ini__ module to the _auto_analyses unit test package. (2010-02-18 12:38:32 +0000)",
    "test_suite/unit_tests/_auto_analyses/test___init__.py":
        "Added a unit test checking the generic_fns.structure.__all__ list. (2009-09-02 13:15:13 +0000)",
    "test_suite/unit_tests/_data_store/__init__.py":
        "Added an initial unit test framework for testing of the diffusion tensor objects. (2007-01-13 05:51:55 +0000)",
    "test_suite/unit_tests/_data_store/test___init__.py":
        "Added an initial unit test framework for testing of the diffusion tensor objects. (2007-01-13 05:51:55 +0000)",
    "test_suite/unit_tests/_data_store/test_diff_tensor.py":
        "Added an initial unit test framework for testing of the diffusion tensor objects. (2007-01-13 05:51:55 +0000)",
    "test_suite/unit_tests/_data_store/test_pipe_container.py":
        "Added a unit test for the PipeContainer.is_empty() method. (2008-04-21 21:38:49 +0000)",
    "test_suite/unit_tests/_lib/__init__.py":
        "Added empty packages to the unit tests for the lib and lib.geometry packages. (2013-03-01 22:59:51 +0000)",
    "test_suite/unit_tests/_lib/test___init__.py":
        "Added the package checking unit tests for the lib package. (2013-03-07 14:56:54 +0000)",
    "test_suite/unit_tests/_lib/test_io.py":
        "Added a framework for the unit tests of the relax_io module. (2007-11-20 18:23:32 +0000)",
    "test_suite/unit_tests/_lib/test_periodic_table.py":
        "Created the unit test infrastructure for the lib.periodic_table module. (2014-08-28 09:24:49 +0000)",
    "test_suite/unit_tests/_lib/test_regex.py":
        "Added a unit test for the generic_fns.relax_re.search() function. (2008-07-07 20:44:53 +0000)",
    "test_suite/unit_tests/_lib/test_statistics.py":
        "Addition of the file which should have been committed in the last commit (r27863). (2015-06-26 08:36:14 +0000)",
    "test_suite/unit_tests/_lib/_alignment/__init__.py":
        "Set up the unit testing infrastructure for the lib.nmr package. (2013-03-22 22:08:52 +0000)",
    "test_suite/unit_tests/_lib/_alignment/test___init__.py":
        "Set up the unit testing infrastructure for the lib.nmr package. (2013-03-22 22:08:52 +0000)",
    "test_suite/unit_tests/_lib/_auto_relaxation/__init__.py":
        "Created the empty packages lib.auto_relaxation and lib.spectral_densities. (2013-03-23 08:14:51 +0000)",
    "test_suite/unit_tests/_lib/_auto_relaxation/test___init__.py":
        "Created the empty packages lib.auto_relaxation and lib.spectral_densities. (2013-03-23 08:14:51 +0000)",
    "test_suite/unit_tests/_lib/_chemical_shift/__init__.py":
        "Created the empty lib.chemical_shift package. (2013-03-23 10:08:22 +0000)",
    "test_suite/unit_tests/_lib/_chemical_shift/test___init__.py":
        "Created the empty lib.chemical_shift package. (2013-03-23 10:08:22 +0000)",
    "test_suite/unit_tests/_lib/_curve_fit/__init__.py":
        "Created the lib.curve_fit package and associated unit tests. (2013-04-04 14:40:15 +0000)",
    "test_suite/unit_tests/_lib/_curve_fit/test___init__.py":
        "Created the lib.curve_fit package and associated unit tests. (2013-04-04 14:40:15 +0000)",
    "test_suite/unit_tests/_lib/_diffusion/__init__.py":
        "Created the empty lib.diffusion package. (2013-03-23 08:28:12 +0000)",
    "test_suite/unit_tests/_lib/_diffusion/test___init__.py":
        "Created the empty lib.diffusion package. (2013-03-23 08:28:12 +0000)",
    "test_suite/unit_tests/_lib/_dispersion/__init__.py":
        "Created the empty lib.dispersion package. (2013-03-23 10:06:19 +0000)",
    "test_suite/unit_tests/_lib/_dispersion/test___init__.py":
        "Created the empty lib.dispersion package. (2013-03-23 10:06:19 +0000)",
    "test_suite/unit_tests/_lib/_frame_order/__init__.py":
        "Created the empty lib.frame_order package. (2013-03-23 08:18:10 +0000)",
    "test_suite/unit_tests/_lib/_frame_order/test___init__.py":
        "Created the empty lib.frame_order package. (2013-03-23 08:18:10 +0000)",
    "test_suite/unit_tests/_lib/_geometry/__init__.py":
        "Added empty packages to the unit tests for the lib and lib.geometry packages. (2013-03-01 22:59:51 +0000)",
    "test_suite/unit_tests/_lib/_geometry/test___init__.py":
        "Added the package checking unit tests for the lib package. (2013-03-07 14:56:54 +0000)",
    "test_suite/unit_tests/_lib/_geometry/test_lines.py":
        "Created a unit test for the lib.geometry.lines.closest_point() function. (2013-03-07 15:27:05 +0000)",
    "test_suite/unit_tests/_lib/_geometry/test_pec.py":
        "Added some unit tests for the pseudo-elliptic cosine function. (2010-07-15 13:46:58 +0000)",
    "test_suite/unit_tests/_lib/_geometry/test_rotations.py":
        "Created the new maths_fns.rotation_matrix.R_to_euler_zyz() function and associated unit test. (2009-09-01 14:02:48 +0000)",
    "test_suite/unit_tests/_lib/_linear_algebra/__init__.py":
        "Created the empty lib.algebra package - this is for advanced linear algebra not present in numpy. (2013-03-23 08:41:28 +0000)",
    "test_suite/unit_tests/_lib/_linear_algebra/test___init__.py":
        "Created the empty lib.algebra package - this is for advanced linear algebra not present in numpy. (2013-03-23 08:41:28 +0000)",
    "test_suite/unit_tests/_lib/_linear_algebra/test_matrix_exponential.py":
        "Created a unit test for the lib.linear_algebra.matrix_exponential module. (2013-10-15 08:43:03 +0000)",
    "test_suite/unit_tests/_lib/_order/__init__.py":
        "Created the empty lib.order package. (2013-03-23 09:07:42 +0000)",
    "test_suite/unit_tests/_lib/_order/test___init__.py":
        "Created the empty lib.order package. (2013-03-23 09:07:42 +0000)",
    "test_suite/unit_tests/_lib/_sequence_alignment/__init__.py":
        "Added the unit testing infrastructure for the new lib.sequence_alignment package. (2015-01-21 10:25:26 +0000)",
    "test_suite/unit_tests/_lib/_sequence_alignment/test___init__.py":
        "Added the unit testing infrastructure for the new lib.sequence_alignment package. (2015-01-21 10:25:26 +0000)",
    "test_suite/unit_tests/_lib/_sequence_alignment/test_align_protein.py":
        "Created a unit test for checking the Needleman-Wunsch sequence alignment algorithm. (2015-01-21 10:39:24 +0000)",
    "test_suite/unit_tests/_lib/_sequence_alignment/test_needleman_wunsch.py":
        "Created a unit test for checking the Needleman-Wunsch sequence alignment algorithm. (2015-01-21 10:39:24 +0000)",
    "test_suite/unit_tests/_lib/_software/__init__.py":
        "Created the empty lib.software package. (2013-03-26 11:36:55 +0000)",
    "test_suite/unit_tests/_lib/_software/test___init__.py":
        "Created the empty lib.software package. (2013-03-26 11:36:55 +0000)",
    "test_suite/unit_tests/_lib/_software/_opendx/__init__.py":
        "Created the empty lib.opendx package. (2013-03-23 20:29:03 +0000)",
    "test_suite/unit_tests/_lib/_software/_opendx/test___init__.py":
        "Created the empty lib.software package. (2013-03-26 11:36:55 +0000)",
    "test_suite/unit_tests/_lib/_spectral_densities/__init__.py":
        "Created the empty packages lib.auto_relaxation and lib.spectral_densities. (2013-03-23 08:14:51 +0000)",
    "test_suite/unit_tests/_lib/_spectral_densities/test___init__.py":
        "Created the empty packages lib.auto_relaxation and lib.spectral_densities. (2013-03-23 08:14:51 +0000)",
    "test_suite/unit_tests/_lib/_spectrum/__init__.py":
        "Created the empty lib.software package. (2013-03-26 11:36:55 +0000)",
    "test_suite/unit_tests/_lib/_structure/__init__.py":
        "Created the unit test infrastructure for the lib.structure package. (2013-03-24 14:57:19 +0000)",
    "test_suite/unit_tests/_lib/_structure/test___init__.py":
        "Created the unit test infrastructure for the lib.structure package. (2013-03-24 14:57:19 +0000)",
    "test_suite/unit_tests/_lib/_structure/test_pdb_read.py":
        "Fix for the unit tests of the generic_fns.structure package. (2013-02-19 16:51:06 +0000)",
    "test_suite/unit_tests/_lib/_structure/_internal/__init__.py":
        "Created the empty lib.structure.internal package for holding the internal structural object. (2013-03-24 15:34:53 +0000)",
    "test_suite/unit_tests/_lib/_structure/_internal/test___init__.py":
        "Created the empty lib.structure.internal package for holding the internal structural object. (2013-03-24 15:34:53 +0000)",
    "test_suite/unit_tests/_lib/_structure/_internal/test_coordinates.py":
        "Created empty unit test infrastructure for testing the lib.structure.internal.coordinates module. (2015-01-28 13:41:51 +0000)",
    "test_suite/unit_tests/_lib/_structure/_internal/test_object.py":
        "Created the unit test infrastructure for the lib.structure.internal.object module. (2015-02-11 08:25:58 +0000)",
    "test_suite/unit_tests/_lib/_structure/_represent/__init__.py":
        "Created the empty lib.structure.represent package. (2013-03-24 15:56:29 +0000)",
    "test_suite/unit_tests/_lib/_structure/_represent/test___init__.py":
        "Created the empty lib.structure.represent package. (2013-03-24 15:56:29 +0000)",
    "test_suite/unit_tests/_lib/_text/__init__.py":
        "Created the framework for the unit tests of the lib.text package. (2013-03-07 17:16:08 +0000)",
    "test_suite/unit_tests/_lib/_text/test___init__.py":
        "Created the framework for the unit tests of the lib.text package. (2013-03-07 17:16:08 +0000)",
    "test_suite/unit_tests/_lib/_text/test_sectioning.py":
        "Created unit tests for the title() and subtitle() functions of the lib.text.sectioning module. (2013-03-20 13:13:55 +0000)",
    "test_suite/unit_tests/_lib/_text/test_table.py":
        "Created two unit tests for the lib.text.table.format_table() function. (2013-03-07 17:23:51 +0000)",
    "test_suite/unit_tests/_multi/__init__.py":
        "Added a unit test for the multi package __all__ list. (2009-09-03 12:56:00 +0000)",
    "test_suite/unit_tests/_multi/test___init__.py":
        "Added a unit test for the multi package __all__ list. (2009-09-03 12:56:00 +0000)",
    "test_suite/unit_tests/_pipe_control/__init__.py":
        "Added unit tests for the functions of the module 'generic_fns.pipes'. (2007-03-13 02:58:01 +0000)",
    "test_suite/unit_tests/_pipe_control/molecule.py":
        "Added a dummy molecule module for the unit tests. (2008-05-04 12:13:00 +0000)",
    "test_suite/unit_tests/_pipe_control/residue.py":
        "Created more dummy modules. (2008-05-04 12:18:57 +0000)",
    "test_suite/unit_tests/_pipe_control/spin.py":
        "Created more dummy modules. (2008-05-04 12:18:57 +0000)",
    "test_suite/unit_tests/_pipe_control/test___init__.py":
        "Renamed the generic_fns package to pipe_control. (2013-03-23 19:25:55 +0000)",
    "test_suite/unit_tests/_pipe_control/test_align_tensor.py":
        "Implemented the framework for the unit tests of the generic_fns.align_tensor module. (2007-11-26 11:24:20 +0000)",
    "test_suite/unit_tests/_pipe_control/test_diffusion_tensor.py":
        "Fixed the initialisation of the diffusion tensor system tests. (2007-11-25 21:04:40 +0000)",
    "test_suite/unit_tests/_pipe_control/test_molecule.py":
        "Added the framework for the unit tests of the generic_fns.sequence module. (2007-11-22 00:14:22 +0000)",
    "test_suite/unit_tests/_pipe_control/test_relax_data.py":
        "Added a base class for the unit tests of the specific_fns.relax_data module. (2007-11-28 08:21:34 +0000)",
    "test_suite/unit_tests/_pipe_control/test_residue.py":
        "Manually reverted r6073. (2008-05-04 12:24:44 +0000)",
    "test_suite/unit_tests/_pipe_control/test_sequence.py":
        "Added the framework for the unit tests of the generic_fns.sequence module. (2007-11-22 00:14:22 +0000)",
    "test_suite/unit_tests/_pipe_control/test_spin.py":
        "Manually reverted r6073. (2008-05-04 12:24:44 +0000)",
    "test_suite/unit_tests/_pipe_control/test_state.py":
        "Added the framework for implementing unit tests for the generic_fns.state module. (2007-11-20 16:41:59 +0000)",
    "test_suite/unit_tests/_pipe_control/test_value.py":
        "Added the framework for adding unit tests of the generic_fns.value module. (2007-12-09 20:50:56 +0000)",
    "test_suite/unit_tests/_pipe_control/_structure/__init__.py":
        "Added the directory for the unit tests of the generic_fns.structure package. (2008-04-20 16:17:59 +0000)",
    "test_suite/unit_tests/_pipe_control/_structure/test___init__.py":
        "Renamed the generic_fns package to pipe_control. (2013-03-23 19:25:55 +0000)",
    "test_suite/unit_tests/_pipe_control/_structure/test_internal.py":
        "Added the framework for the unit tests of the Scietific Python PDB structural object. (2008-04-20 16:37:37 +0000)",
    "test_suite/unit_tests/_prompt/__init__.py":
        "Copied the __init__.py file. (2007-11-18 20:21:39 +0000)",
    "test_suite/unit_tests/_prompt/container.py":
        "Converted all of the prompt unit tests to the new auto-generated user function design. (2012-05-24 09:20:53 +0000)",
    "test_suite/unit_tests/_prompt/test___init__.py":
        "Added many more checks for the package __all__ lists. (2009-09-02 13:43:16 +0000)",
    "test_suite/unit_tests/_prompt/test_align_tensor.py":
        "Added the framework for the unit tests of the align_tensor.x() user functions. (2007-11-21 13:27:01 +0000)",
    "test_suite/unit_tests/_prompt/test_dasha.py":
        "Created 7 arg unit tests for all fns of the dasha user function class. (2008-10-11 16:40:20 +0000)",
    "test_suite/unit_tests/_prompt/test_deselect.py":
        "Added the infrastructure for the arg unit tests of the deselect user function class. (2008-05-07 12:44:11 +0000)",
    "test_suite/unit_tests/_prompt/test_eliminate.py":
        "Wrote the arg unit test module for the eliminate() user function, with 2 unit tests. (2008-06-29 13:55:20 +0000)",
    "test_suite/unit_tests/_prompt/test_minimisation.py":
        "Wrote the print_flag arg unit test of the minimise.calc() user function. (2008-01-07 10:06:06 +0000)",
    "test_suite/unit_tests/_prompt/test_model_free.py":
        "Added the framework for unit tests of the model-free user function args. (2008-01-13 11:31:20 +0000)",
    "test_suite/unit_tests/_prompt/test_molecule.py":
        "Added to empty unit test modules. (2007-03-17 01:58:48 +0000)",
    "test_suite/unit_tests/_prompt/test_molmol.py":
        "Wrote 5 arg unit tests for the pymol.macro_exec() user function. (2009-08-26 09:26:41 +0000)",
    "test_suite/unit_tests/_prompt/test_n_state_model.py":
        "Added the framework for the user function arg unit tests of the N-state model. (2008-01-09 16:34:50 +0000)",
    "test_suite/unit_tests/_prompt/test_noe.py":
        "Wrote 2 arg unit tests for the noe.spectrum_type() user function. (2008-12-05 14:22:33 +0000)",
    "test_suite/unit_tests/_prompt/test_pymol.py":
        "Wrote 5 arg unit tests for the pymol.macro_exec() user function. (2009-08-26 09:26:41 +0000)",
    "test_suite/unit_tests/_prompt/test_relax_data.py":
        "Added the framework for the arg unit tests of the relax_data user functions. (2007-11-26 18:39:51 +0000)",
    "test_suite/unit_tests/_prompt/test_relax_disp.py":
        "Added 3 arg unit tests for the relax_fit user function class. (2008-10-22 16:14:40 +0000)",
    "test_suite/unit_tests/_prompt/test_relax_fit.py":
        "Added 3 arg unit tests for the relax_fit user function class. (2008-10-22 16:14:40 +0000)",
    "test_suite/unit_tests/_prompt/test_residue.py":
        "Added to empty unit test modules. (2007-03-17 01:58:48 +0000)",
    "test_suite/unit_tests/_prompt/test_select.py":
        "Added the infrastructure for the arg unit tests of the deselect user function class. (2008-05-07 12:44:11 +0000)",
    "test_suite/unit_tests/_prompt/test_sequence.py":
        "Added the framework and TestCase class for the unit tests of the prompt.sequence module. (2007-11-21 23:00:01 +0000)",
    "test_suite/unit_tests/_prompt/test_spectrum.py":
        "Created the skeleton module for arg unit tests of the spectrum user function class. (2008-10-22 08:44:40 +0000)",
    "test_suite/unit_tests/_prompt/test_spin.py":
        "Added to empty unit test modules. (2007-03-17 01:58:48 +0000)",
    "test_suite/unit_tests/_prompt/test_state.py":
        "Added the framework for implementing unit tests for the generic_fns.state module. (2007-11-20 16:41:59 +0000)",
    "test_suite/unit_tests/_prompt/test_uf_objects.py":
        "Created two unit tests for the _build_doc() methods of the prompt user function objects. (2012-06-01 07:04:05 +0000)",
    "test_suite/unit_tests/_prompt/test_value.py":
        "Added the infrastructure for the user function arg unit tests of prompt.value. (2007-12-09 16:41:47 +0000)",
    "test_suite/unit_tests/_scons/__init__.py":
        "Added an empty package __init__ module. (2008-05-22 16:11:52 +0000)",
    "test_suite/unit_tests/_specific_analyses/__init__.py":
        "Turned the 2 new dirs into modules. (2007-11-27 10:07:28 +0000)",
    "test_suite/unit_tests/_specific_analyses/test___init__.py":
        "Added many more checks for the package __all__ lists. (2009-09-02 13:43:16 +0000)",
    "test_suite/unit_tests/_specific_analyses/test_n_state_model.py":
        "Created a unit test for the N-state model assemble_param_vector() method. (2008-01-17 09:55:11 +0000)",
    "test_suite/unit_tests/_specific_analyses/_consistency_tests/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_consistency_tests/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_frame_order/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_frame_order/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_jw_mapping/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_jw_mapping/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_model_free/__init__.py":
        "Added an empty package __init__ module. (2008-05-22 16:15:20 +0000)",
    "test_suite/unit_tests/_specific_analyses/_model_free/test___init__.py":
        "Added many more checks for the package __all__ lists. (2009-09-02 13:43:16 +0000)",
    "test_suite/unit_tests/_specific_analyses/_model_free/test_api.py":
        "Wrote a unit test for the model-free duplicate_data() method. (2008-09-26 09:30:48 +0000)",
    "test_suite/unit_tests/_specific_analyses/_n_state_model/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_n_state_model/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_noe/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_noe/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_disp/__init__.py":
        "Added the unit test infrastructure for testing the specific_analyses.relax_disp package. (2014-02-19 12:59:52 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_disp/test___init__.py":
        "Added the unit test infrastructure for testing the specific_analyses.relax_disp package. (2014-02-19 12:59:52 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_disp/test_checks.py":
        "Split the unit test of specific_analyses.relax_disp.checks.get_times() into its own unit test file. (2014-08-18 12:21:01 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_disp/test_data.py":
        "Added the infrastructure for the unit tests of the specific_analyses.relax_disp.disp_data module. (2014-02-19 13:09:31 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_disp/test_variables.py":
        "Added initial unit test class for testing specific_analysis.relax_disp.variables. (2014-08-11 07:09:14 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_fit/__init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_specific_analyses/_relax_fit/test___init__.py":
        "Added units tests for package consistency testing for all of the remaining specific analyses. (2014-03-28 10:04:09 +0000)",
    "test_suite/unit_tests/_target_functions/__init__.py":
        "initial commit of maths fns unit tests and test for the unit test framework (2006-11-28 09:02:08 +0000)",
    "test_suite/unit_tests/_target_functions/test___init__.py":
        "Added many more checks for the package __all__ lists. (2009-09-02 13:43:16 +0000)",
    "test_suite/unit_tests/_target_functions/test_n_state_model.py":
        "Wrote a unit test for the maths_fns.n_state_model.func() optimisation target function. (2008-01-21 15:56:58 +0000)",
    "test_suite/unit_tests/_target_functions/test_relax_fit.py":
        "Created 2 unit tests for the target_functions.relax_fit relax C module. (2014-08-26 09:35:25 +0000)",
    "test_suite/unit_tests/_user_functions/__init__.py":
        "The unit test _user_functions package is now actually a package! (2012-05-03 17:40:36 +0000)",
    "test_suite/unit_tests/_user_functions/test___init__.py":
        "Added a unit test for the contents of the user_function package. (2012-05-03 17:41:45 +0000)",
    "test_suite/verification_tests/status_object.py":
        "Created the Status_object.test_install_path system verification test. (2014-05-12 19:29:47 +0000)",
    "user_functions/__init__.py":
        "Created the empty user_functions package. (2012-05-03 16:35:51 +0000)",
    "user_functions/bruker.py":
        "Created the prompt/script interface to the pdc.read() user function. (2011-02-17 15:22:15 +0000)",
    "user_functions/data.py":
        "Created the empty user_functions package. (2012-05-03 16:35:51 +0000)",
    "user_functions/objects.py":
        "Created a number of special objects for the user function data storage. (2012-05-03 17:33:24 +0000)",
    "user_functions/script.py":
        "Added the user_functions.script module which should have been committed in r16303. (2012-05-13 17:14:49 +0000)",
    "user_functions/spectrometer.py":
        "Converted the frq user functions to the auto-generation design. (2012-05-08 15:26:54 +0000)",
    "user_functions/statistics.py":
        "Created the empty statistics user function class. (2015-02-05 13:59:36 +0000)",
    "user_functions/sys_info.py":
        "Converted the sys_info user function to the auto-generation design. (2012-05-11 18:52:44 +0000)",
}

# Additional copyright notices that are not present in the git log.
ADDITIONAL_COPYRIGHT = {
    'docs/latex/relax.bst' : ["Copyright (C) 1988, all rights reserved."],
}

# Additional copyright years and authors to add to the list.  The keys are lists of lists of the year as an int and the author name as a string.
ADDITIONAL_COPYRIGHT_YEARS = {
    'docs/html/icons/contents.png':                                     [[1993, "Nikos Drakos"]],
    'docs/html/icons/crossref.png':                                     [[1993, "Nikos Drakos"]],
    'docs/html/icons/footnote.png':                                     [[1993, "Nikos Drakos"]],
    'docs/html/icons/index.png':                                        [[1993, "Nikos Drakos"]],
    'docs/html/icons/next_g.png':                                       [[1993, "Nikos Drakos"]],
    'docs/html/icons/next.png':                                         [[1993, "Nikos Drakos"]],
    'docs/html/icons/prev_g.png':                                       [[1993, "Nikos Drakos"]],
    'docs/html/icons/prev.png':                                         [[1993, "Nikos Drakos"]],
    'docs/html/icons/up_g.png':                                         [[1993, "Nikos Drakos"]],
    'docs/html/icons/up.png':                                           [[1993, "Nikos Drakos"]],
    'graphics/README':                                                  [[2017, "Edward d'Auvergne"]],
    'graphics/analyses/README':                                         [[2017, "Edward d'Auvergne"]],
    'graphics/misc/README':                                             [[2017, "Edward d'Auvergne"]],
    'graphics/relax_icons/128x128/README':                              [[2017, "Edward d'Auvergne"]],
    'graphics/relax_icons/16x16/README':                                [[2017, "Edward d'Auvergne"]],
    'graphics/relax_icons/22x22/README':                                [[2017, "Edward d'Auvergne"]],
    'graphics/relax_icons/32x32/README':                                [[2017, "Edward d'Auvergne"]],
    'graphics/relax_icons/48x48/README':                                [[2017, "Edward d'Auvergne"]],
    'graphics/screenshots/README':                                      [[2017, "Edward d'Auvergne"]],
    'graphics/screenshots/dispersion_analysis/README':                  [[2017, "Edward d'Auvergne"]],
    'graphics/screenshots/mf_analysis/README':                          [[2017, "Edward d'Auvergne"]],
    'graphics/wizards/README':                                          [[2017, "Edward d'Auvergne"]],
}

# False positives (copyright notices in files to ignore, as they are not in the git log).
FALSE_POS = {
    'info.py':                                                          ["self.copyright.append(\"Copyright (C) 2001-2006 Edward d'Auvergne\")", "self.copyright.append(\"Copyright (C) 2006-2016 the relax development team\")", "self.copyright_short = \"Copyright (C) 2001-2016 the relax development team\""],
    'devel_scripts/copyright_notices.py':                               ["Copyright (C) year1, year2, year3 copyright-holder"],
    'graphics/wizards/oxygen-icon-weather-snow-scattered-night.png':    ["Copyright (C) 2007 Nuno Pinheiro <nuno@oxygen-icons.org>", "Copyright (C) 2007 David Vignoni <david@icon-king.com>", "Copyright (C) 2007 David Miller <miller@oxygen-icons.org>", "Copyright (C) 2007 Johann Ollivier Lapeyre <johann@oxygen-icons.org>", "Copyright (C) 2007 Kenneth Wimer <kwwii@bootsplash.org>", "Copyright (C) 2007 Riccardo Iaconelli <riccardo@oxygen-icons.org>"],
    'graphics/wizards/object-locked-unlocked.png':                      ["Copyright (C) 2007 Nuno Pinheiro <nuno@oxygen-icons.org>", "Copyright (C) 2007 David Vignoni <david@icon-king.com>", "Copyright (C) 2007 David Miller <miller@oxygen-icons.org>", "Copyright (C) 2007 Johann Ollivier Lapeyre <johann@oxygen-icons.org>", "Copyright (C) 2007 Kenneth Wimer <kwwii@bootsplash.org>", "Copyright (C) 2007 Riccardo Iaconelli <riccardo@oxygen-icons.org>"],
    'graphics/wizards/oxygen-icon-weather-clear.png':                   ["Copyright (C) 2007 Nuno Pinheiro <nuno@oxygen-icons.org>", "Copyright (C) 2007 David Vignoni <david@icon-king.com>", "Copyright (C) 2007 David Miller <miller@oxygen-icons.org>", "Copyright (C) 2007 Johann Ollivier Lapeyre <johann@oxygen-icons.org>", "Copyright (C) 2007 Kenneth Wimer <kwwii@bootsplash.org>", "Copyright (C) 2007 Riccardo Iaconelli <riccardo@oxygen-icons.org>"],
    'graphics/wizards/dipole_pair/VectorFieldPlot.py':                  ["Copyright (C) 2010 Geek3"],
    'lib/dispersion/b14.py':                                            ["Copyright (C) 2014 Andrew Baldwin"],
    'lib/dispersion/cr72.py':                                           ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/dpl94.py':                                          ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/it99.py':                                           ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/lm63.py':                                           ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/lm63_3site.py':                                     ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/m61.py':                                            ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/m61b.py':                                           ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/mp05.py':                                           ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger"],
    'lib/dispersion/ns_mmq_2site.py':                                   ["Copyright (C) 2013 Mathilde Lescanne", "Copyright (C) 2013 Dominique Marion"],
    'lib/dispersion/ns_mmq_3site.py':                                   ["Copyright (C) 2013 Mathilde Lescanne", "Copyright (C) 2013 Dominique Marion"],
    'lib/dispersion/ns_cpmg_2site_3d.py':                               ["Copyright (C) 2010-2013 Paul Schanda", "Copyright (C) 2013 Mathilde Lescanne", "Copyright (C) 2013 Dominique Marion"],
    'lib/dispersion/ns_cpmg_2site_expanded.py':                         ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger", "Copyright (C) 2010-2013 Paul Schanda", "Copyright (C) 2013 Mathilde Lescanne", "Copyright (C) 2013 Dominique Marion"],
    'lib/dispersion/ns_cpmg_2site_star.py':                             ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger", "Copyright (C) 2010-2013 Paul Schanda", "Copyright (C) 2013 Mathilde Lescanne", "Copyright (C) 2013 Dominique Marion"],
    'lib/dispersion/ns_matrices.py':                                    ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger", "Copyright (C) 2010-2013 Paul Schanda", "Copyright (C) 2013 Mathilde Lescanne", "Copyright (C) 2013 Dominique Marion"],
    'lib/dispersion/ns_r1rho_2site.py':                                 ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger"],
    'lib/dispersion/ns_r1rho_3site.py':                                 ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger"],
    'lib/dispersion/tap03.py':                                          ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger"],
    'lib/dispersion/tp02.py':                                           ["Copyright (C) 2000-2001 Nikolai Skrynnikov", "Copyright (C) 2000-2001 Martin Tollinger"],
    'lib/dispersion/tsmfk01.py':                                        ["Copyright (C) 2009 Sebastien Morin"],
    'lib/dispersion/two_point.py':                                      ["Copyright (C) 2009 Sebastien Morin"],
    'sample_scripts/model_free/final_data_extraction.py':               ["Copyright (C) 2009-2011 Michael Bieri"],
    'specific_analyses/model_free/api.py':                              ["Copyright (C) 2007 Gary S Thompson"],
    'specific_analyses/model_free/data.py':                             ["Copyright (C) 2007 Gary S Thompson"],
    'specific_analyses/model_free/optimisation.py':                     ["Copyright (C) 2007 Gary S Thompson"],
    'target_functions/relax_disp.py':                                   ["Copyright (C) 2009 Sebastien Morin"],
    'test_suite/system_tests/scripts/relax_fit_saturation_recovery.py': ["Copyright (C) 2014 Andras Boeszoermenyi"],
}

# False negatives (significant git log commits which do not imply copyright ownership).
FALSE_NEG = {
}
FALSE_NEG_YEARS = {
    'docs/html/icons/contents.png':                                     [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/crossref.png':                                     [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/footnote.png':                                     [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/index.png':                                        [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/next_g.png':                                       [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/next.png':                                         [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/prev_g.png':                                       [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/prev.png':                                         [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/up_g.png':                                         [[2011, "Edward d'Auvergne"]],
    'docs/html/icons/up.png':                                           [[2011, "Edward d'Auvergne"]],
    'graphics/wizards/oxygen-icon-weather-snow-scattered-night.png':    [[2012, "Edward d'Auvergne"]],
    'graphics/wizards/object-locked-unlocked.png':                      [[2012, "Edward d'Auvergne"]],
    'graphics/wizards/oxygen-icon-weather-clear.png':                   [[2012, "Edward d'Auvergne"]],
    'sample_scripts/model_free/final_data_extraction.py':               [[2010, "Michael Bieri"], [2011, "Michael Bieri"]],
}

# Commits to exclude as a list of commit keys - the first line of the commit message followed by the ISO date in brackets.
EXCLUDE = [
    # 0152ac6f384fb86fa082a4521d17fc3e1b8a15a4 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all scripts in the test_suite/shared_data/ directory. (2017-08-21 23:37:02 +0200)",
    # 4272a7f11dfa057d74d9b631f0ad3be1c72486a0 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all system test modules and scripts. (2017-07-27 18:12:23 +0200)",
    # a840151f3a07267c1a38e4ca586a708ad4585d2d - Copyright notice updates.
    "Update to FSF compliant copyright notices for all unit test modules. (2017-07-27 16:16:16 +0200)",
    # 668618021a79893169c66e02c3626e487ead49a5 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules and files in the base relax directory. (2017-07-21 13:10:55 +0200)",
    # c2dfa522ce02ed9b88449388c58bc04f00c669af - Copyright notice updates.
    "Update to FSF compliant copyright notices for all scripts in the sample_scripts/ directory. (2017-07-19 12:21:25 +0200)",
    # bfffa6fb149961244a9b8bc74b66743ed7f48fe7 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules in the prompt package. (2017-07-19 10:59:45 +0200)",
    # c9c29ba6bbbe7a5636616c65e093062b5267689a - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules in the pipe_control package. (2017-07-19 09:08:21 +0200)",
    # 4ae077acc40d3c00760b9074ca54e8145c6790a1 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules in the multi package. (2017-07-18 14:53:22 +0200)",
    # 98e89a92c5ce2e98bcc0661cc11ac3e1c828d915 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules in the lib package. (2017-07-11 14:16:19 +0200)",
    # 96766bcc37727f4449da83abee7191cef7dcfda6 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules in the gui package. (2017-07-11 12:42:18 +0200)",
    # 54740b75877c76685dc986ef88f3f42ba9951019 - Copyright notice updates.
    "FSF compliant copyright notices for the entirety of the devel_scripts/ directory. (2017-07-11 11:51:06 +0200)",
    # f808f9bcd05844c055ee08984e3d0b0415f5af74 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules in the data_store package. (2017-07-11 11:31:20 +0200)",
    # 3ec0a6f920dcf0c47208f2890f973d4e20ce1ac0 - Copyright notice updates.
    "Update to FSF compliant copyright notices for all modules in the auto_analyses package. (2017-07-11 11:11:08 +0200)",
    # 2afc3b9212ddbcb037024aa32307fbd2b43e69ab - Copyright notice updates.
    "FSF compliant copyright notices for the extern/ directory. (2017-07-11 10:48:17 +0200)",
    # d86ae0491175ca3e6f7f5c9cacf651491d3c88df - Copyright notice updates.
    "FSF compliant copyright notices for the entirety of the graphics/ directory. (2017-07-07 11:49:32 +0200)",
    # 936698bc132fc1d029f717d2c40116deab255237 - Copyright notice updates.
    "Added the original oxygen icon AUTHORS and COPYING files and standardised the README file titles. (2017-07-10 11:07:43 +0200)",
    # 720e1dd29c6f62b6029048254d17af3470020915 - Copyright notice updates.
    "FSF compliant copyright notices for all remaining files in the documentation directory. (2017-07-07 11:17:37 +0200)",
    # 79af68053a461a79b7b1314e81c8e05f684f10e8 - Copyright notice updates.
    "FSF compliant copyright notices for all files in the documentation directory docs/html/. (2017-07-07 11:07:40 +0200)",
    # c30653225f37f6ee893ea481f887afb8619b9950 - Copyright notice updates.
    "FSF compliant copyright notices for all files in the documentation directory docs/latex/. (2017-07-07 10:22:52 +0200)",
    # 87b9acdd180f11d1e8a5c48b6269d0d5a281f015 - Copyright notice updates.
    "FSF compliant copyright notices for all files in the documentation directory docs/devel/. (2017-07-07 09:12:47 +0200)",
    # r27848 - 8cea9e80ccc4cfe9f80a4c31e7a4d11464c0ffb8.
    "Reverted r27840-r27845, related to Bug #23618, queuing system for multi processors is not well designed. (2015-06-11 11:15:54 +0000)",
    # r27845 - 8284128b7e65604fd7fd581353339074b2c1cd44.
    "Suggestion for fix 2, where jobs are continously replenished when other jobs are finished. (2015-05-27 01:09:59 +0000)",
    # r27844 - 9d4bbdd0e58947e9e38ba79afb1ce4e19446f2f3.
    "Suggestion Fix 1, in multi.processor.run_queue(). (2015-05-27 01:09:57 +0000)",
    # r27843 - 130ce65f4cd1f509ec62589284f1ff7122ca422b.
    "In pipe_control of minimise, adding the possibility to control verbosity in multi processor mode. (2015-05-27 01:09:55 +0000)",
    # r27842 - 229d7d3d7df69e5344080ae5769f25e0194ae0f1.
    "In multi.processor(), moving up the debugging print-out of running sets of calculatation. (2015-05-27 01:09:52 +0000)",
    # r27841 - da852d05b0f3fdf03a59cea9437e46a36e30cb32.
    "Adding to user function minimise.execute() the keyword \"mp_verbosity\", to control the amount of information to print when running multi processors. (2015-05-27 01:09:50 +0000)",
    # r27840 - e06d116f17a9f3978a655940d50c4e3d47f3ebaf.
    "Adding keyword for verbosity for multi processor mode. (2015-05-27 01:09:48 +0000)",
    # r27214 - 25ba046c14486d55ce33be611458e48d79371a74.
    "Reverted range of commits r27213:r27202 as this was a bad implementation. (2015-01-17 13:16:50 +0000)",
    # r27213 - 689e2403d8b85190e29eba67be352202fbaf1ac9.
    "Added 'sos' and 'sos_std' as parameter object in relaxation dispersion. (2015-01-16 22:20:13 +0000)",
    # r27212 - 54f60bb436ca61d4c3bcc5e7aa113fd60663862c.
    "Implemented in the relaxation dispersion API, the function to return errors as the standard deviation of sums squared residuals. (2015-01-16 22:20:11 +0000)",
    # r27211 - 5b08a8691f1fc06c9e022819db0474f6e68483a6.
"Implemented the api_base method of return_error_sum_squares(), as raising an error if not defined for the api for the pipe_type. (2015-01-16 22:20:08 +0000)",
    # r27210 - 1797025ef590c937ed6334407aacf2c8bb92336a.
    "Extended backend in pipe_control.error_analysis.monte_carlo_create_data() to return errors as the standard deviation of the sum of squares of the residual. (2015-01-16 22:20:06 +0000)",
    # r27209 - 20e70867b9c7fb11782b8a248bbee279a3f3f253.
    "Extended user function monte_carlo.create_data() to accept 'method=\"sum_squares\"', to create Monte-Carlo data. (2015-01-16 22:20:04 +0000)",
    # r27208 - 4cb9ace10a6ad9db69f8f565a723de228174e922.
    "Speed-up of systemtest Relax_disp.test_task_7882_monte_carlo_std_residual() by copying pipe instead of reading results 3 times. (2015-01-16 22:20:01 +0000)",
    # r27207 - dce94e688605a61efc882999cedf7db82e7e2a2c.
    "In systemtest Relax_disp.test_task_7882_monte_carlo_std_residual() inserted sanity checks of calculation of degrees of freedom. (2015-01-16 22:19:58 +0000)",
    # r27206 - 378db59919058b2d64b1c4e8f2499d1e4c1c02d9.
    "Extracted \"sos\" and \"sos_std\" after grid search. (2015-01-16 22:19:56 +0000)",
    # r27205 - 7c90802c2f916d3e0817089f57a568b9db184492."Added to systemtest Relax_disp.test_task_7882_monte_carlo_std_residual() that spin.sos and spin.sos_std is stored after grid search. (2015-01-16 22:19:54 +0000)",
    # r27204 - ca9a8ef3a005207e0971a08fec571ac3607048e8.
    "Stored the sums of squares of the residuals \"sos\" and standard deviation of this \"sos_std\" per spin after optimisation. (2015-01-16 22:19:51 +0000)",
    # r27203 - 51c596b2b7ef471081543e032cd6e3266c0fb36b.
    "Implemented storing of sum of squares and the standard deviation of these for relaxation dispersion, when doing a point calculation. (2015-01-16 22:19:50 +0000)",
    # r27202 - c75faf5b589f69733c93c6669357046f20f13907.
    "Implemented target function for relaxation dispersion, which calculate the sum of squares of residuals and the standard deviation of these. (2015-01-16 22:19:47 +0000)",
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
    # r25132 - fd718a0780136324085b28da3359b6ab35f8a472.
    "Replaced that folder names for writing out results should be with replaced with underscores \"_\". (2014-08-20 21:03:53 +0000)",
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
    # r23546 - efddab673939e10c72c5dea09320b2700fa2ad1d.
    "Reverted r23531-23526 as this would prevent a clean merge back into the trunk. (2014-05-28 15:55:10 +0000)",
    # r23531 - dc6a093be1ebf83616b34583b10b5ff9419d8ad3.
    "Added 9th and 10th unit test case for model B14. (2014-05-28 14:49:08 +0000)",
    # r23530 - 389d04a2e6517b7456769d2ebefbe4ce432ccc96.
    "Added all the default values for the lower/upper bounds which is set for the parameters in the grid search. (2014-05-28 14:49:06 +0000)",
    # r23529 - 68e37f55859129d2afaa894190def81dde8db5a7.
    "Added grid_upper to be handled in specific_analyses/parameter_object.py. (2014-05-28 14:49:05 +0000)",
    # r23528 - 8e6d4e22ecfc9aa59dbbb167ee34c5fb73088cdf.
    "Added the default value upper grid value to be set for the pA parameter. (2014-05-28 14:49:03 +0000)",
    # r23527 - ce38d703eb75caadef368b1fc1f6e741a68f073e.
    "Added grid_lower to be handled in specific_analyses/parameter_object.py. (2014-05-28 14:49:02 +0000)",
    # r23526 - da5b41770b1d2fff19d91f1f4b6ef9ff5ec04eaf.
    "Added the default value lower grid value to be set for the pA parameter. (2014-05-28 14:49:00 +0000)",
    # r22919 - f9a3794208e0395b53ec59ded24913a6da2a0463.
    "Replaced Copyright notice for the Baldwin.py script. (2014-05-02 09:57:09 +0000)",
    # r22816 - 89c302bba91132115ca23e213b59a894e21db539 - 2to3 automated conversions.
    "Python 3 fixes throughout the codebase. (2014-04-22 15:49:39 +0000)",
    # r21770 - 209ff73223c70d3920df367a631f9bd4c4d77c0c.
    "Renamed the 'ns_mmq_3site_branched' dispersion test data directory to 'ns_mmq_3site'. (2013-12-04 11:21:09 +0000)",
    # r21155 - a6af21049e0cbe825c9609ede890cab76269ed99 - 2to3 automated conversions.
    "A number of Python 3 fixes. (2013-10-17 09:09:48 +0000)",
    # r20785 - d4372c6612d94f2957df246b30ae0e69f9bd73a3 - 2to3 automated conversions.
    "Python 3 fixes. (2013-09-04 07:29:14 +0000)",
    # r20659 - 16399fd3ad31573dc3ab0084a88c05ffc2a6ebed.
    "Shifted all the modules from lib.software to do with peak lists to lib.spectrum. (2013-08-21 12:21:51 +0000)",
    # r20441 - 423abd67f91cfbe0d7a4111cd2d46eacaf7ea802.
    "Reverted r20438 and r20439 as the commit messages were incomplete!!! (2013-07-22 06:36:56 +0000)",
    # r20439 - 8767b75cd29ca83bba8f642e4a017b1ad82ad20f.
    "Progress sr #3043: (https://gna.org/support/index.php?3043)",
    # r20438 - ab5a48ba1d6f3566b3f7b567ac3ce9a094cfb0fe.
    "Fix for the dispersion auto-analysis for when only the single R2eff model is optimised. (2013-07-20 15:51:47 +0000)",
    # r20291 - 521787f4e4cefb4a1d7e343d873c75d617a88585 - 2to3 automated conversions.
    "Spacing fixes for the lib.dispersion.ns_2site_star module as determined by the 2to3 program. (2013-07-15 08:03:08 +0000)",
    # r19926 - 8cee1be0ce60f6e6356e2cca58eddb322117721f - 2to3 automated conversions.
    "Python 3 fixes. (2013-06-06 21:19:36 +0000)",
    # r19477 - 9053d23b5594ab07bd7942d447183d80717656f1.
    "Renamed the relaxation dispersion test suite data directory to 'dispersion'. (2013-04-13 16:54:46 +0000)",
    # r19255 - 9b77cc6b8d51b2830dca0dd452f33c7629c5929c.
    "Ported r17253 from the old relax_disp branch into the new branch. (2013-03-27 14:56:09 +0000)",
    # ca07a9a44bb5a2f6a97a9d8d205f08f7fd9adc91.
    "Ported r12837 from the old relax_disp branch into the new branch. (2013-03-27 14:53:41 +0000)",
    # fb2aca15d54a530a767258701c4ac837cacbed48.
    "Ported r11698 from the old relax_disp branch into the new branch. (2013-03-27 14:53:01 +0000)",
    # 537b6d6b7f62ff39b5a7c0e632e8ec7b2e317afb.
    "Ported r9864 from the old relax_disp branch into the new branch. (2013-03-27 14:49:13 +0000)",
    # b0411f41b2ce4e6b0bf737b78c48ffe45d162220.
    "Ported r8733 from the old relax_disp branch into the new branch. (2013-03-27 14:45:35 +0000)",
    # 7459e0a9a42e9c8d48531901d8582f16e7bd47e6.
    "Ported r8724 from the old relax_disp branch into the new branch. (2013-03-27 14:44:59 +0000)",
    # b17a2e502ce4f1fa89333400c7006e2c09b6fb4b.
    "Ported r8722 from the old relax_disp branch into the new branch. (2013-03-27 14:44:25 +0000)",
    # 7f27850aba40db5f570e8113094e0b5a2e089568.
    "Ported r8720 from the old relax_disp branch into the new branch. (2013-03-27 14:40:18 +0000)",
    # 4427e6cc9ce89d97521d5feeb5076fc2c3bb7c7d.
    "Ported r8719 from the old relax_disp branch into the new branch. (2013-03-27 14:39:15 +0000)",
    # 391ccf74e332a3a7b17a1778f6a7f3a4bbc91c47.
    "Ported r8709 from the old relax_disp branch into the new branch. (2013-03-27 14:37:36 +0000)",
    # 8ec6e2a22551338435582204fd6341cfa7f9b302.
    "Ported r8703 from the old relax_disp branch into the new branch. (2013-03-27 14:35:20 +0000)",
    # cdbc7b4d21b6befa055d2f8bbee7530760628afb.
    "Ported r8702 from the old relax_disp branch into the new branch. (2013-03-27 14:30:02 +0000)",
    # 37752ed226ac8561b98d98854c8c00d19a497cd7.
    "Ported r8699 from the old relax_disp branch into the new branch. (2013-03-27 14:29:18 +0000)",
    # c76b4c33f51bc45e3e17b6cd57a3626e652f2194.
    "Ported r8697 from the old relax_disp branch into the new branch. (2013-03-27 14:27:10 +0000)",
    # f4dd6107233b5a6b838b2a97a1c4e5938f0a1903.
    "Ported r8696 from the old relax_disp branch into the new branch. (2013-03-27 14:26:18 +0000)",
    # 1226aeda8ce95957ab0821dec86def1edec55e97.
    "Ported r8688 from the old relax_disp branch into the new branch. (2013-03-27 14:25:23 +0000)",
    # a40e0a76a80ef8d3555f9ee54113fb24e38f01cd.
    "Ported r8687 from the old relax_disp branch into the new branch. (2013-03-27 14:24:08 +0000)",
    # e488fd7e71f41c50a3530a21cb7767c0031775ac.
    "Ported r8686 from the old relax_disp branch into the new branch. (2013-03-27 14:22:11 +0000)",
    # adcccf986d39a4133119c76e19e054d071adf13f.
    "Ported r8678 from the old relax_disp branch into the new branch. (2013-03-27 14:18:03 +0000)",
    # 880a3759e6512d3408016be26535f8cba040e21b.
    "Ported r8676 from the old relax_disp branch into the new branch. (2013-03-27 14:17:19 +0000)",
    # 63c8996580c00076a164c8d653e8465ee0b20ea2.
    "Ported r8675 from the old relax_disp branch into the new branch. (2013-03-27 14:16:44 +0000)",
    # 25578deaf671b10cea17d0233ef725fc1062526e.
    "Ported r8673 from the old relax_disp branch into the new branch. (2013-03-27 14:16:16 +0000)",
    # 01c1407a0ab47f3dff280a4e1b811ab370db45e3.
    "Ported r8670 from the old relax_disp branch into the new branch. (2013-03-27 14:15:46 +0000)",
    # c60a077f996134d96d700f5ab37a148ed73c7c41.
    "Ported r8669 from the old relax_disp branch into the new branch. (2013-03-27 14:14:25 +0000)",
    # 7844bec9aa6b4c3312072c2b8e6764c47ed540f2.
    "Ported r8656 from the old relax_disp branch into the new branch. (2013-03-27 14:13:42 +0000)",
    # 2bd679040b8bbecd647e193559dac1906be5b08a.
    "Ported r8491 from the old relax_disp branch into the new branch. (2013-03-27 14:04:40 +0000)",
    # a320ad6e652a22578ac2e2d07d9643a71ba8f181.
    "Ported r8490 from the old relax_disp branch into the new branch. (2013-03-27 14:04:02 +0000)",
    # a2ae1991f0fe523f22ad607dc7c170f4f0319b0a.
    "Ported r8472 from the old relax_disp branch into the new branch. (2013-03-27 13:49:26 +0000)",
    # e84cec011f740b63d808352f265477913269ff49.
    "Ported r8435 from the old relax_disp branch into the new branch. (2013-03-27 13:45:40 +0000)",
    # 000833f63e324e9d0bd3f57819183c9bf5c219e7.
    "Ported r8430 from the old relax_disp branch into the new branch. (2013-03-27 13:42:37 +0000)",
    # e8f5151fa9f8a2c0258d832954075a32fc3ef98c.
    "Ported r8429 from the old relax_disp branch into the new branch. (2013-03-27 13:42:05 +0000)",
    # 5898a33d44175e73e72777fd0fb3f4290e647e18.
    "Ported r8428 from the old relax_disp branch into the new branch. (2013-03-27 13:41:32 +0000)",
    # 532a69e3e4ca969abcf6bb49be4759abc1ad0e4a.
    "Ported r8426 from the old relax_disp branch into the new branch. (2013-03-27 13:40:58 +0000)",
    # 1b11dad6f0e093c26e528c7404547c68ae74d88b.
    "Ported r8417 from the old relax_disp branch into the new branch. (2013-03-27 13:33:37 +0000)",
    # a66a770d32efc7a1d709c1da1b706331f4aa334b.
    "Ported r8415 from the old relax_disp branch into the new branch. (2013-03-27 13:32:54 +0000)",
    # 1658b90a6f2c65331063bb16db1b597ff4cd46b2.
    "Ported r8399 from the old relax_disp branch into the new branch. (2013-03-27 13:32:24 +0000)",
    # db09e9bf50d2d3957ecee46fbdf748cfed8e60f4.
    "Ported r8398 from the old relax_disp branch into the new branch. (2013-03-27 13:31:30 +0000)",
    # 2e122b4cabee9f4b1b3151295166a8273f336005.
    "Ported r8397 from the old relax_disp branch into the new branch. (2013-03-27 13:30:35 +0000)",
    # dc0fd62e181d1b08ed09be7b819b8fe19349be96.
    "Ported r8396 from the old relax_disp branch into the new branch. (2013-03-27 13:29:34 +0000)",
    # 5f26a11cef48253bff224e584fde3dd8d9a04cdf.
    "Ported r8395 from the old relax_disp branch into the new branch. (2013-03-27 13:28:24 +0000)",
    # e93e1fddce2baa8d50c7d48f497f238f1832e842.
    "Ported r8394 from the old relax_disp branch into the new branch. (2013-03-27 13:27:31 +0000)",
    # 6876fe2c396634cbb32e014b8056380e544c61b5.
    "Ported r8391 from the old relax_disp branch into the new branch. (2013-03-27 13:25:51 +0000)",
    # d6965fb29389f93b7b00c2da37b7909ce3b2ecd5.
    "Ported r8390 from the old relax_disp branch into the new branch. (2013-03-27 13:24:55 +0000)",
    # dc0fbdffa1666609072b1ff4d1a4a3c13edd9b31.
    "Ported r8389 from the old relax_disp branch into the new branch. (2013-03-27 13:24:05 +0000)",
    # 65e9fdf03686f31b2aea3742b2469965cb322b62.
    "Ported r8367 from the old relax_disp branch into the new branch. (2013-03-27 13:22:17 +0000)",
    # f0c9e429d0e5adb98f77c774bcfb124d4a5e06aa.
    "Ported r8366 from the old relax_disp branch into the new branch. (2013-03-27 13:21:09 +0000)",
    # 48802df6b71c3ae8773a1ac9ba75db8275f7f487.
    "Ported r8365 from the old relax_disp branch into the new branch. (2013-03-27 13:20:28 +0000)",
    # dce985be655be937eae57c3fcf36dbf7a58c6bd7.
    "Ported r8364 from the old relax_disp branch into the new branch. (2013-03-27 13:19:40 +0000)",
    # f3a60c2633073834260c046de3beaaa54a82d1ed.
    "Ported r8363 from the old relax_disp branch into the new branch. (2013-03-27 13:17:17 +0000)",
    # 984eed2c987044cd73128a5663a39e563690d95e.
    "Ported r8362 from the old relax_disp branch into the new branch. (2013-03-27 13:16:22 +0000)",
    # 9c537d568dafd2d36d146213671bdd8396bbd8ba.
    "Ported r8361 from the old relax_disp branch into the new branch. (2013-03-27 13:15:01 +0000)",
    # f164d0037e645bc7ecc1844b636fc6ab9b5dfb9f.
    "Ported r8360 from the old relax_disp branch into the new branch. (2013-03-27 13:13:02 +0000)",
    # 9535fff698dc11b389982c95302cc5f6b6edaa47.
    "Ported r8359 from the old relax_disp branch into the new branch. (2013-03-27 13:12:27 +0000)",
    # 48089eab6869056dc714a207f739b4edbba24362.
    "Ported r8358 from the old relax_disp branch into the new branch. (2013-03-27 13:11:50 +0000)",
    # 6eb71642cc1a36a4658d5386a20b90e849f4ed16.
    "Ported r8357 from the old relax_disp branch into the new branch. (2013-03-27 13:11:14 +0000)",
    # 2034925209aa9901677514650ad6c2e71edde734.
    "Ported r8355 from the old relax_disp branch into the new branch. (2013-03-27 13:10:15 +0000)",
    # 1ae426e4699dc5e4d20bf364c3ac65bf83bc96dc.
    "Ported r8354 from the old relax_disp branch into the new branch. (2013-03-27 13:09:39 +0000)",
    # 10e22ef9d30be03ce6b010f5db8732731a947eed.
    "Ported r8353 from the old relax_disp branch into the new branch. (2013-03-27 13:08:59 +0000)",
    # 16e6064333eea7637c0d931c6318a9048a06ed85.
    "Ported r8352 from the old relax_disp branch into the new branch. (2013-03-27 13:08:20 +0000)",
    # 2948c1b81d2dc33ecc90c2fe0cfe15d4d8630b82.
    "Ported r8351 from the old relax_disp branch into the new branch. (2013-03-27 13:07:46 +0000)",
    # ba75cf90300351ab20f07dbf911aa06ad1eb476c.
    "Ported r from the old relax_disp branch into the new branch. (2013-03-27 13:03:10 +0000)",
    # 098d0ef28dba97bfdec4d5dc41b0bd46ba22faf9.
    "Ported r8343 from the old relax_disp branch into the new branch. (2013-03-27 12:58:48 +0000)",
    # 51a3e2e426a261d7c893c36ba896c59b326e1b4b.
    "Ported r8342 from the old relax_disp branch into the new branch. (2013-03-27 12:51:22 +0000)",
    # 57a69f3e46be9735428ac8b96a37b6a1ad69cb07.
    "Ported r8340 from the old relax_disp branch into the new branch. (2013-03-27 12:49:27 +0000)",
    # 2e9674c51e07481c1892bad7e4512d9d57fd9532.
    "Ported r8339 from the old relax_disp branch into the new branch. (2013-03-27 12:47:48 +0000)",
    # 985829bcfb65a57f860bd07356b8ed0d99681a7b.
    "Ported r8337 from the old relax_disp branch into the new branch. (2013-03-27 12:06:34 +0000)",
    # cc79ed19f7ebce0b16b7356b38088b654fbdeffe.
    "Ported r8335 from the old relax_disp branch into the new branch. (2013-03-27 12:05:12 +0000)",
    # 1e355306a0a29e93470824ee6ee91bac6e200b2b.
    "Ported r8331 from the old relax_disp branch into the new branch. (2013-03-27 12:04:25 +0000)",
    # 23b4961f0f15377e69873b4601eea86930331bfc.
    "Ported r8330 from the old relax_disp branch into the new branch. (2013-03-27 12:03:48 +0000)",
    # 4cc1839fc4439ac9f7882813709f3201c22026fa.
    "Ported r8329 from the old relax_disp branch into the new branch. (2013-03-27 12:03:12 +0000)",
    # f39aaa3998f64842e1a54fd23a48cf2baef4d70d.
    "Ported r8328 from the old relax_disp branch into the new branch. (2013-03-27 12:02:20 +0000)",
    # 85659fe5d644ebed00d3a5912ae6f29bf4d2973e.
    "Ported r8327 from the old relax_disp branch into the new branch. (2013-03-27 12:01:18 +0000)",
    # b5c30ea3208e2e21b35b29b7cd87f32c0f1fc785.
    "Ported r8326 from the old relax_disp branch into the new branch. (2013-03-27 11:59:17 +0000)",
    # e295439144df8b6d14a76e2aeda0a59a4310d9a3.
    "Ported r8325 from the old relax_disp branch into the new branch. (2013-03-27 11:57:14 +0000)",
    # a454dc065fd73bb068e0159bc8542ed032b3fc00.
    "Ported r8324 from the old relax_disp branch into the new branch. (2013-03-27 11:56:08 +0000)",
    # 429a638bdf435b1c22522212cea75c20c9461fa7.
    "Ported r8323 from the old relax_disp branch into the new branch. (2013-03-27 11:55:14 +0000)",
    # b988d337af59769849225da1a3e045b745d44250.
    "Ported r8248 from the old relax_disp branch into the new branch. (2013-03-27 11:14:58 +0000)",
    # 10bd33cd25eca2786e56429d628681c4df0629de.
    "Ported r8247 from the old relax_disp branch into the new branch. (2013-03-27 11:14:09 +0000)",
    # r19169 - e5bbdc00d0d89247c74be7d61dfcb5d90868dba0.
    "Ported r8246 from the old relax_disp branch into the new branch. (2013-03-27 11:12:45 +0000)",
    # r19111 - d0366e24397ac94dbba04403784da9f5d0b237d0.
    "Shifted the pipe_control.structure.cones module to lib.structure.cones. (2013-03-24 15:02:11 +0000)",
    # r19110 - b8ce38698eaeb3f03617b3d35978dcd46201d73f.
    "Shifted the pipe_control.structure.pdb_read and pipe_control.structure.pdb_write modules to lib.structure. (2013-03-24 14:59:13 +0000)",
    # r19108 - dabbcf24ba79ca656dfba89ae3a543ca8cf8bf03.
    "Shifted the pipe_control.structure.statistics module to lib.structure.statistics. (2013-03-24 14:54:57 +0000)",
    # r19107 - c5fea9401ff064bb5d614c58d04ff2629ab004ec.
    "Shifted the pipe_control.structure.superimpose module to lib.structure.superimpose. (2013-03-24 14:53:19 +0000)",
    # r19083 - 27128548bbffadc390927272fcdd847b89f3be81.
    "Shifted most of the modules of target_functions.frame_order to lib.frame_order. (2013-03-23 20:02:52 +0000)",
    # r19082 - 7f7862c5084a9bacb9388c2c5468b5dd94fd60d3.
    "Shifted the target_functions.frame_order.pec module to lib.geometry.pec. (2013-03-23 19:56:32 +0000)",
    # r19081 - 10d9922ecc700a8f1cea4a1ceef8e65b95f75e10.
    "Renamed the pipe_control.frame_order module to lib.frame_order.format. (2013-03-23 19:51:12 +0000)",
    # r19079 - 1e3e93331a17e1bc34bf5c491e9fd48727de0f2e.
    "Renamed the generic_fns package to pipe_control. (2013-03-23 19:25:55 +0000)",
    # r19073 - eb58eb2c62901f6fd19a81ea5253895b6ca19768.
    "Renamed the generic_fns.relax_re module to lib.regex. (2013-03-23 17:27:27 +0000)",
    # r19069 - d1da49abf152a9dffd899022a47e655d676d227b.
    "Shifted the generic_fns.xplor module to lib.xplor. (2013-03-23 17:08:56 +0000)",
    # r19068 - 642e56bafa3c519413842d200a58c46922da2d21.
    "Reverted revisions r19065, r19066 and r19067. (2013-03-23 17:00:41 +0000)",
    # r19067 - 1eceee2b1b80f081805798aef140aa89305d04b1.
    "Renamed data_store.lib to data_store.control. (2013-03-23 16:55:11 +0000)",
    # r19066 - 0d7e7199493c16a3dca0af316c44aefca1504046.
    "Shifted most of the modules containing data store objects into data_store.objects. (2013-03-23 13:00:16 +0000)",
    # r19065 - 4d3f2f346ea81b89e1645a0d08cdce5d9a3e5b14.
    "Created two new empty packages data_store.lib and data_store.objects. (2013-03-23 12:52:00 +0000)",
    # r19061 - 234bd7ec51cb4a13485380e542299deb7ccf08e3.
    "Moved the check_types module into the lib package. (2013-03-23 09:46:51 +0000)",
    # r19060 - 0d0eaaaa2ffb679cbeaf4f07f85effc276258a68.
    "Shifted the arg_check module to lib.arg_check. (2013-03-23 09:43:57 +0000)",
    # r19059 - 3761e2ed0f96117e9e16360080e3b0978b1e33ba.
    "Shifted the target_functions.paramag_centre module to lib.alignment.paramag_centre. (2013-03-23 09:38:28 +0000)",
    # r19058 - 0bbfb5a2e7f23f1506d72860ee83efde36cbd08d.
    "Shifted the target_functions.correlation_time module to lib.diffusion.correlation_time. (2013-03-23 09:35:51 +0000)",
    # r19057 - 94bdca7305ca378d280cd8bbe6791f1f69cf722e.
    "Moved the target_functions.weights module to lib.diffusion.weights. (2013-03-23 09:33:30 +0000)",
    # r19056 - 6e252adab42be9431bc835620579fa52eb5d7e89.
    "Moved the target_functions.ri_comps module to lib.auto_relaxation.ri_comps. (2013-03-23 09:29:45 +0000)",
    # r19053 - 674c47326fa3cfde57a98ed05729f7ad3a547a93.
    "Shifted the target_functions.ri_prime module to lib.auto_relaxation.ri_prime. (2013-03-23 09:20:58 +0000)",
    # r19052 - 46a66d852c7d6744c2786a21775ff273c414e262.
    "Shifted the target_functions.ri module to lib.auto_relaxation.ri. (2013-03-23 09:17:04 +0000)",
    # r19051 - 075587609e6f42c59b2ea7045d9e2aec2e61e553.
    "Shifted the target_functions.order_parameters module to lib.order.order_parameters. (2013-03-23 09:11:02 +0000)",
    # r19049 - 64901802278e3d051af55f4bbce41129c4b56d08.
    "Shifted the target_functions.jw_mf_comps module to lib.pectral_densities.model_free_components. (2013-03-23 09:04:57 +0000)",
    # r19048 - b881a39bd2cb8d0b2d9f40bb1160ca106dde663e.
    "Shifted the target_functions.jw_mf module to lib.spectral_densities.model_free. (2013-03-23 09:00:36 +0000)",
    # r19046 - 6794f60fb367403f6c7094f17ad049b1f17809b2.
    "Moved the target_functions.kronecker_product module to lib.algebra.kronecker_product. (2013-03-23 08:44:52 +0000)",
    # r19044 - a850a9a1de747d124718de6b264e5af382586544.
    "Shifted the target_functions.direction_cosine module to lib.diffusion.direction_cosine. (2013-03-23 08:37:15 +0000)",
    # r19041 - 2cc0901c74e3364c57f820e63e564274ebc8ffa0.
    "Shifted the target_functions.coord_transform module to lib.geometry.coord_transform. (2013-03-23 08:26:06 +0000)",
    # r19035 - 366711903f05eb34a2508bf00a1e2148f4700b95.
    "Renamed the lib.nmr package to lib.alignment. (2013-03-23 08:06:15 +0000)",
    # r19032 - d61b9a5e7701b8fb2d58002d7436505070b51995.
    "Shifted the target_functions.vectors module to lib.geometry.vectors. (2013-03-23 07:59:15 +0000)",
    # r19028 - 5b8fb0ffdc9ee7e37c75fb067f155496ea733ccb.
    "Renamed the data package to data_store. (2013-03-22 23:25:25 +0000)",
    # r19027 - 1fd705d9785609da6be242c864cb1272dbd43ded.
    "Shifted the float module into the lib package. (2013-03-22 23:04:33 +0000)",
    # r19026 - fa10d72942af42e328ee0952f841f1d78fbe5c66.
    "Renamed the maths_fns package to target_functions. (2013-03-22 23:00:31 +0000)",
    # r19025 - e4d289130c47e9b7cde3e4d4bcedf90a11543212.
    "Copyright updates which should have gone into r19024. (2013-03-22 22:51:05 +0000)",
    # r19024 - 44ac4a86559d295788a0f48815546cfa51bbed21.
    "Renamed the specific_fns package to specific_analyses. (2013-03-22 22:32:08 +0000)",
    # r19023 - 87786ffc6b29958c7040b9209f07bcb24a88fc0e.
    "Shifted the maths_fns.rdc and maths_fns.pcs modules to lib.nmr. (2013-03-22 22:14:21 +0000)",
    # r19022 - 53a506e4c44f5726e48d53ec2225076c39fb8607.
    "Shifted the maths_fns.alignment_tensor module to lib.nmr.alignment_tensor. (2013-03-22 22:10:32 +0000)",
    # r19018 - d9a2205ebebaf21def77e07b80dec43b8e2da03d.
    "Renamed the maths_fns.rotation_matrix module to lib.geometry.rotations. (2013-03-22 21:54:54 +0000)",
    # r19017 - c64679b818e2a31b3d8fb469f96a68046177cfb3.
    "Shifted the physical_constants module into the lib package. (2013-03-22 21:45:30 +0000)",
    # r19016 - cb142fb14dfa85b79421d1fa6b69a59ad2729524.
    "Renamed the ansi module to lib.ansi. (2013-03-22 21:39:49 +0000)",
    # r19011 - b696e5c9f021b3fc485ea7b2f60cbfd709071fce.
    "Renamed the relax_warnings module to lib.warnings. (2013-03-22 20:58:13 +0000)",
    # r19009 - 6f4e33c64d64ccdd6bb775b2ec9420b985bceacd.
    "Renamed the relax_io module to lib.io. (2013-03-22 20:51:55 +0000)",
    # r19008 - be26f8de5507246dcf372238e0150bf250f60476.
    "Renamed the relax_string module to lib.text.string. (2013-03-22 20:44:59 +0000)",
    # r19007 - 491f276d2265184c14ac0d97aea25b43a12804c2.
    "Renamed the relax_errors module to lib.errors. (2013-03-22 20:41:29 +0000)",
    # r19004 - 75c236a76a79b3fe9b43a59da673db10f1a10090.
    "Final synchronisation of all the frame_order_testing branch files back to trunk for the merger. (2013-03-22 16:49:23 +0000)",
    # r19003 - ef17cc187446e4eda7e7383e3d56d5b1c36f39f4.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:35:56 +0000)",
    # r19002 - f4f82f892272130d0dc7ecad4b35bc9dc9bf2fbf.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:34:27 +0000)",
    # r19001 - e9c27cd39ab4dfca5156cd6cf0b8356e43de5e2b.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:31:38 +0000)",
    # r19000 - d09da10c48560af77ecdfce04c8a0da1e5a68263.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:27:57 +0000)",
    # r18999 - 12fd5a040a5f10233fd3d093740a7bc7cdf08558.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:27:05 +0000)",
    # r18998 - 71e2e87f33b3b4a071dced80a24d0a3d5ed1540e.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:26:16 +0000)",
    # r18997 - d01167edeb7cebef06003ae3041444616f501850.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:24:22 +0000)",
    # r18996 - 0c691ec49cdb6f3c8acf98a8d9bc47d0d1c4cdc0.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:23:00 +0000)",
    # r18995 - 3b25f71b2d5eb2738607d011f6f0c2614b0f675d.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:18:31 +0000)",
    # r18994 - d02ec8b2c4f52ff9a5c4be821fa9a2799b0d7de1.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:15:19 +0000)",
    # r18993 - cb27367c85de3e4a8603433822d50a04320d13be.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:14:20 +0000)",
    # r18992 - 2020fd0cc7aedd1c14f7ba87abfba686ec0745d4.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:12:07 +0000)",
    # r18991 - bdf80b55c35fa8f228fa4d6fce60721c6c453784.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:08:33 +0000)",
    # r18990 - fda5fbbb96a3ff1b7bb4fa58f4130a6ed27e5112.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:05:42 +0000)",
    # r18989 - 47dad1d00b7b3f7697a0f893043227ef46997607.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:03:52 +0000)",
    # r18988 - d46917bd2333bd48e1fea33425287b1c53cd9d97.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:02:35 +0000)",
    # r18987 - a34fcdf97e218883d2014d3dcad1bbb516613e1b.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 16:01:22 +0000)",
    # r18986 - 268f7269fdc7a7e6ee5a0a036ce21d54f6117ebd.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:56:08 +0000)",
    # r18985 - a98e5bf34408d6046faa70dc4dc3da7323486664.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:55:10 +0000)",
    # r18984 - e38db07d61a8cbd77621db4740191b42f9850922.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:54:21 +0000)",
    # r18983 - 6552fc1b190f01d4d53ccbcc7dcd66da4fef1627.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:51:35 +0000)",
    # r18982 - e3cfc834a2230bc14e3ee294cb70ad92189ad338.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:49:43 +0000)",
    # r18981 - 164504cd38b553264fa958f15e9e0108217d4df0.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:47:10 +0000)",
    # r18980 - 4b93870ad309776d6022fb1641ed1bdfc87cf694.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:45:57 +0000)",
    # r18979 - a8d7f011308ad927b1627e6a5c36545c2f28de49.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:44:07 +0000)",
    # r18978 - a553320e401e96cb085d84c3f92e34237473e67f.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:42:12 +0000)",
    # r18977 - 63aa683a9a040ea2c6f4fa5324fabd5fbfe1ac12.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:40:06 +0000)",
    # r18976 - 5f72b074caccc357bae14abd102cb392473cd134.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:37:50 +0000)",
    # r18975 - a0c07835413a927262eccdd556b2b1abba5d98b5.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:36:30 +0000)",
    # r18974 - cbd3da28098dbb096c6007189a9d7f3af67cc364.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:31:24 +0000)",
    # r18973 - cbc8f6caec122b16a33f2133b8c8df3e195c5441.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:27:35 +0000)",
    # r18972 - 6eaa40323f5373b969b6b08cd0ffe841c70ceb1c.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:24:53 +0000)",
    # r18971 - e5a809c9a466048a4cd0d83c63f979785e611be0.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:23:24 +0000)",
    # r18970 - 9e145350ff0bfa48bad572ca9f5bb0976dfde2ab.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:21:05 +0000)",
    # r18969 - a304e88d8949a72ba2649b50ee2ab745b8960222.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:19:53 +0000)",
    # r18968 - e77e67909b9f19e5fe56f82996419fb25f153953.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 15:18:26 +0000)",
    # r18967 - 8289a9bcc14c11e5794b62898aa5de744964f7a6.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:43:19 +0000)",
    # r18966 - 1dec4b16003bd9727ffa5f263d106d5d1f17fc25.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:37:30 +0000)",
    # r18965 - 370b45b18f6ffc36d0a3822410c493913d93e2b8.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:36:09 +0000)",
    # r18964 - 90254744ecd53b38c4c7399cd7686e9319915a85.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:33:31 +0000)",
    # r18963 - 525f68335d5e423e579c10a3c33d3113bd96d052.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:32:31 +0000)",
    # r18962 - 017b681c4cefffd0f886f1a0417cbfaa6cb6ec29.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:30:59 +0000)",
    # r18961 - 87f532b53e27914ad068c86f89b56ad67b07b64e.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:29:40 +0000)",
    # r18960 - 72ade78839113e26c99f648aad5cb3c7854c5515.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 14:28:26 +0000)",
    # r18959 - 0258e88b2071a6e83e8859d7ea224a16d6280532.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:54:25 +0000)",
    # r18958 - deb34da3b605d4133a56807a6d358465ab9106c4.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:49:41 +0000)",
    # r18957 - 77fd77f22062fb67d18901864c5aac3602ce1d5b.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:47:52 +0000)",
    # r18956 - 285dd6be2310c34ce05d2abbf8bcaa2f8f7122eb.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:44:20 +0000)",
    # r18955 - fffa41de539d225388e6d20dd463292eb2167837.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:34:25 +0000)",
    # r18954 - fa6d56dfbf5c417d4130f7d630b1cd8113c5fa9a.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:33:01 +0000)",
    # r18953 - 65b373440618bf574e449974b8ae5c11872c7e07.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:28:51 +0000)",
    # r18952 - 244853ac49b85364cc10c1fbb3407f4848e16995.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:21:56 +0000)",
    # r18951 - 58c6b39c4b454829ad43daa768f0da8d83c1758f.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:14:53 +0000)",
    # r18950 - 9d4927cc23f24cb6f2e5217b28df1220d37cbfb4.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:06:56 +0000)",
    # r18949 - b1e2161747c74d44f9375e8d3a56253b70583db0.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:05:23 +0000)",
    # r18948 - 34070e7dd310328ca709eab6c387d90d8ff173a2.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 11:01:21 +0000)",
    # r18947 - 40de7ccfc24912166fe700f9dba2bb3b0b03aae8.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 10:59:41 +0000)",
    # r18946 - 7688bf7bca6f3d126bf110257a59bb30464bfa5c.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 10:56:17 +0000)",
    # r18945 - cad69a4f697fc41a7d9cf01d05e464f7e08d78f4.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 10:52:14 +0000)",
    # r18944 - 5a53667f70e6f631bcdc4beaee4184886dda9e42.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 10:49:43 +0000)",
    # r18943 - e6522db9e7a56dafafb6d2856d4bf628716b1c05.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 10:47:48 +0000)",
    # r18942 - 48699182fa170203a69655c23b2123065608935a.
    "Next block of the manual merger of the frame_order_testing branch. (2013-03-22 10:46:15 +0000)",
    # r18941 - ccff03c397e69f62ea2a3104a38132a3ee5f1f41.
    "Started the manual merger of the frame_order_testing branch back to trunk. (2013-03-22 10:41:32 +0000)",
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
    # r17089 - 44447548a0ca6901ec17ea9fd88a70926fc3b5c3.
    "Reverted the CaM synthetic randomised data change of r17071, as the data randomisation shouldn't change. (2012-06-28 10:15:51 +0000)",
    # r17071 - f8aebcb685ef46acf62ad00291f5c1b05f843c89.
    "Converted all RDC data and generations scripts used by the N-state model to the interatom design. (2012-06-27 14:03:17 +0000)",
    # r16879 - bd05ab2c14a8c10b399da92a405ce81f2736e476 - 2to3 automated conversions.
    "Reverted the 2to3 changes of r16837 as these are deadly for Python 2.6! (2012-06-12 09:34:42 +0000)",
    # r16837 - 4c5a0d2a1d43aa98142ef3bed85d4e71e6327d7d - 2to3 automated conversions.
    "Python 3 updates for the entire relax code base. (2012-06-11 08:15:21 +0000)",
    # r16534 - 570a7076b71a33b8667a5c4e99decd01ecac4548 - 2to3 automated conversions.
    "Print statement conversions to function calls for Python 3.x. (2012-05-30 15:41:17 +0000)",
    # r15849 - c2244dad9c29130d4560dce6906cf6332a385828.
    "Renamed the PDC to Bruker DC in the test suite. (2012-04-30 10:43:05 +0000)",
    # r15228 - 09f4391582c9ab826e7de192a835e1a7a39209f5 - 2to3 automated conversions.
    "Updates for Python 3.0. (2012-01-24 14:24:40 +0000)",
    # r14812 - cad3aac4d7ca177c4a4129b00f9f80e92a4b26ed - 2to3 automated conversions.
    "Updates for Python 3.0 using the Python 2to3 script. (2011-10-09 11:40:36 +0000)",
    # r14069 - b53f99f555ae895e416802f3c16c314db9558733.
    "Reverted r14068 as this svnmerge commit breaks the branch. (2011-08-02 14:26:05 +0000)",
    # r13456 - 9403da5ca58d48ca56a0bc2c19da89a44efced44.
    "Partly reverted r13453 as the coloured residue graphic was accidentally replaced with the greyscale one. (2011-07-06 15:14:24 +0000)",
    # r13453 - 6888758caa637c256837b8fce9ebb9093d1656a2.
    "The greyscale conversion of graphics is now better. (2011-07-06 13:36:42 +0000)",
    # r13148 - 088087256b6960730976fccab203a45093720ad8.
    "Removed the svn:executable and svn:mime-type properties from the consistency testing graphics. (2011-06-21 14:46:47 +0000)",
    # r12792 - e0d3226dccbe8590a9295ab586896aad0d39a0cb.
    "Shifted all of the model-free sample scripts into the new subdirectory sample_scripts/model_free. (2011-03-04 13:14:44 +0000)",
    # r12412 - 3497eb7bdb85ea656e0f33a8b972602cc5bde6ed.
    "Renamed the gui_bieri package to gui. (2011-01-21 11:18:47 +0000)",
    # r12202 - 5012a2b474e539d8564847f1979a98619c99a42d - 2to3 automated conversions.
    "Updates for Python 3.0. (2011-01-11 11:58:33 +0000)",
    # r12087 - a53a2164a8fb91d6d0304b28586839033c6e1ab6.
    "Shifted the location of the truncated PSE-4 data for the relax 1.2 results reading system test. (2011-01-03 09:26:24 +0000)",
    # r11914 - 73d6afd501eef48159ec7d48d69839000c6de023.
    "Reverted r11913 as this was completely wrong and broke the reading of results files. (2010-12-20 15:28:56 +0000)",
    # r11913 - 44b3298effc90d6ba03df0ea5f10ea9a5bf12579.
    "Added a check to make sure the relax save states can not be loaded by results.read(). (2010-12-20 15:15:56 +0000)",
    # r10860 - 67f4a1a6cf1adb11c6837a1d1d09a26630ce35f7 - 2to3 automated conversions.
    "A python 3.0 fix for the grace module. (2010-02-23 15:06:48 +0000)",
    # r10737 - ddc552bd3042775c5f24409473c849c771c32731.
    "Shifted the Gromacs phthalic acid structure. (2010-02-18 14:57:22 +0000)",
    # r9890  - ab69727887d0d5b006894b44583675d6b6306901 - Pure whitespace changes.
    "Converted tab characters to 8 spaces... (2009-11-19 19:05:50 +0000)",
    # r9885 - d5d1314a8a26e5f2f669450376f458e4e83b4412.
    "Renamed the relaxGUI module to match the relax naming conventions. (2009-11-19 10:22:18 +0000)",
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
    # r8705 - c539aa91dbf320d423eb11dab8913990dc7eaf04.
    "Corrected an error introduced in r8704 where the __init__.py file for system tests was modified for the purpose of fast testing while coding... (2009-02-01 19:35:57 +0000)",
    # r8704 - 39d106407a1a57bd953c124fa6b9c3974458d0fe.
    "Copied C files for Rx curve fitting for adapting as the code for dispersion curve fitting. (2009-02-01 19:33:20 +0000)",
    # r8224 - 2210c04e8dd7e10b53ff7060add85b1ff64a5e91 - Whitespace cleanup.
    "Many corrections of formatting. (2008-12-23 16:04:48 +0000)",
    # r7857 - 425c0e9f57a207ccda8e6a1130eb3ca16eb79c7c.
    "Alphabetical sorting of class methods. (2008-10-20 19:27:28 +0000)",
    # r7856 - 0844466e3b086eadc34c1e86130ec643db877a3c.
    "A large number of spacing fixes. (2008-10-20 19:25:25 +0000)",
    # r7855 - ea3843a6b73938d5f2a3f1345a80177afb9956b9.
    "Added the copyright statement. (2008-10-20 19:21:44 +0000)",
    # r7845 - 289107393a33918401c94ea78858270a6dd99f41.
    "Shifted a class out of order to allow for subclassing. (2008-10-19 19:36:13 +0000)",
    # r7738 - 0af9485b3ad9f1b284a7a7d9e4d09123c0bb8704.
    "Manually merged the last of the multi_processor branch. (2008-10-15 22:33:21 +0000)",
    # r7737 - fd065c9eeba07781002f527ba0b9c9adb63bc7e2.
    "Manually ported r3274 from the multi_processor branch. (2008-10-15 22:26:21 +0000)",
    # r7736 - 7b1324f9ae9b5c970b57fa63c1ccc724772f2cd6.
    "Manually ported r3269, r3270, and r3271 from the multi_processor branch. (2008-10-15 22:24:12 +0000)",
    # r7735 - 41800082875933346c23fe3febbc1f9c981c8aa4.
    "Manually ported r3268 from the multi_processor branch. (2008-10-15 22:21:57 +0000)",
    # r7734 - a4e0489be506de6f5dea73086cc1e67130721455.
    "Merged all that could be merged from r3267. (2008-10-15 22:17:30 +0000)",
    # r7732 - 4d430bc6c099842b691ddd47be927c74240da2cd.
    "Merged all that could be merged from r3266. (2008-10-15 22:15:01 +0000)",
    # r7729 - eb760d318fe4133fbdda2b41fc83d4c0c9cd7a65.
    "Manually ported r3261 from the multi_processor branch. (2008-10-15 21:32:04 +0000)",
    # r7727 - 298d3ad98c8a01850e1a6c3b2c8f8529412321b6.
    "Manually ported r3254 from the multi_processor branch. (2008-10-15 21:12:52 +0000)",
    # r7726 - 880bfaebb61f628a15a668965fe975745ee12987.
    "Manually ported r3253 from the multi_processor branch. (2008-10-15 21:12:00 +0000)",
    # r7725 - 3e1dfa4ace4ebbafc292fa1bf6ab5ec84bc39f57.
    "Manually ported r3252 from the multi_processor branch. (2008-10-15 21:10:22 +0000)",
    # r7724 - 625a5c8d6fb4068cdfafff91f824aacb4d37e91d.
    "Manually ported r3251 from the multi_processor branch. (2008-10-15 21:09:28 +0000)",
    # r7723 - 1306db0ac71de602e29e12d975acb04a9e322966.
    "Manually ported r3250 from the multi_processor branch. (2008-10-15 21:05:57 +0000)",
    # r7722 - f83e51870d6b919fc9e078020094ae499b7dbe9e.
    "Manually ported r3249 from the multi_processor branch. (2008-10-15 21:04:33 +0000)",
    # r7721 - ee3a6e01662c9e54a59e82add28e91e89519e7a3.
    "Manually ported r3248 from the multi_processor branch. (2008-10-15 20:57:55 +0000)",
    # r7720 - 1753fcf964c6a76df69d6f4aca9892e19b5e5a68.
    "Manually ported r3246 from the multi_processor branch. (2008-10-15 20:55:11 +0000)",
    # r7719 - 968d1221d835cd4b22e231c343defb47cdc188da.
    "Manually ported r3243 from the multi_processor branch. (2008-10-15 20:53:04 +0000)",
    # r7718 - 61ff6d48504f5b11828a48594db42c938c3e84cd.
    "Manually ported r3242  from the multi_processor branch. (2008-10-15 20:40:20 +0000)",
    # r7717 - 379837305a05961d8537446d1e1db2c043d27482.
    "Partially ported r3241 from the multi_processor branch. (2008-10-15 20:10:31 +0000)",
    # r7716 - 8595bccc89b7d1de8e9d913b3fed4c9d0af40093.
    "Manually ported r3239 from the multi_processor branch. (2008-10-15 20:05:14 +0000)",
    # r7715 - 2363550c85706647d706e37b7b724d57f381c438.
    "Manually ported r3238 from the multi_processor branch. (2008-10-15 20:04:11 +0000)",
    # r7714 - e141b0c785fe72808403d7cad3f329f66f968619.
    "Manually ported r3237 from the multi_processor branch. (2008-10-15 19:55:41 +0000)",
    # r7713 - 92aaac2fdd6fefaa3dc7f7ec19077c682a021443.
    "Manually merged r3236 from the multi_processor branch. (2008-10-15 19:54:17 +0000)",
    # r7712 - 14421d0f53fa09fcd92ef1132dd53a6348a9d8ed.
    "Manually merge r3235 from the multi_processor branch. (2008-10-15 19:51:39 +0000)",
    # r7711 - 4a43c5de4cd699d7f9b697e2cc3aa53a9bf0ccfb.
    "Added a change which occurred in r3208 of the multi_processor branch but was somehow not ported. (2008-10-15 19:48:43 +0000)",
    # r7710 - bd06f8c7726dd3487cbd4b372c6be25f91837159.
    "Manually ported r3210 from the multi_processor branch. (2008-10-15 19:46:10 +0000)",
    # r7709 - 0f759c3725972afefdd9ac78eccd457bdbdf6d35.
    "Manually merged r3208 from the multi_processor branch. (2008-10-15 19:40:06 +0000)",
    # r5977 - 6050b0be1d27af4df20b0dbf043cac3968231465.
    "Shifted the relaxation curve fitting data into the 'test_suite/shared_data/' directory. (2008-04-24 14:51:43 +0000)",
    # r3735 - 5dbdf89b20db84dc7ab6b88d0c9667c648ffe1a5.
    "Renamed all the unit test directories to start with an underscore. (2007-11-20 22:41:25 +0000)",
    # r2910 - 95982d7a7a02126d01a8d34c5aa41a12d256969f.
    "Merged the 'test_suite' branch back into the 1.3 line. (2006-12-02 05:46:28 +0000)",
    # r2718 - fa8eb08c3b6fc667b3f88b57ba87d8f1ee6388eb.
    "reconfigure for new system test and unit test framework (2006-10-31 14:58:38 +0000)",
    # r2403 - 988aa94991d3e9e5d81319fcf1d767a0818dd7be.
    "Shifted the test suite from the directory 'testing' to 'test_suite'. (2006-03-24 02:17:11 +0000)",
    # r894, r895, etc. - 41775d02748d251373dff182ec220c34cbcd8cf0, 358f9909ed75b71a9262e261e6f0eeb86ca9d814, etc.
    "Updating to the archive 'backup_relax_2004-02-24a.tar.bz2'. (2004-02-24 06:45:20 +0000)"
]

# Commits to switch authorship of (e.g. if someone commits someone else's code).
# The data consists of:
#       0 - The comitter's name.
#       1 - The real author.
#       2 - The commit key, consisting of the first line of the commit message followed by the ISO date in brackets.
AUTHOR_SWITCH = [
    # r26860 - 5ed60182fe5f70fac8040f37fb10e65615e7f68c.
    ["Edward d'Auvergne", "Sebastien Morin",
        "Copied synthetic inversion recovery Sparky peak lists from Sébastien Morin's inversion-recovery branch. (2014-11-29 23:27:28 +0000)"],
    # r23022 - d6115145be75f30e16cc0211d32b5ac4c5f7247b.
    ["Troels Emtekær Linnet", "Andrew Baldwin (andrew.baldwin@chem.ox.ac.uk),",
        "Added the synthetic data for B14 model whereby the simplification R20A = R20B is assumed. (2014-05-06 15:34:04 +0000)"],
    # r22948 - 5b1ea93924ee887041c675806fbc7b5946a015e4.
    ["Troels Emtekær Linnet", "Andrew Baldwin (andrew.baldwin@chem.ox.ac.uk),",
        "Added the synthetic N15 data for systemtest Relax_disp.test_baldwin_synthetic. (2014-05-04 12:49:31 +0000)"],
    # r22906 - 01d6c4a272ed3a486f300c68820551afdd368277.
    ["Troels Emtekær Linnet", "Andrew Baldwin (andrew.baldwin@chem.ox.ac.uk),",
        "Added Baldwin model B14 test data. (2014-05-01 08:47:35 +0000)"],
    # r22080 - 7ab9dac72fe60f60eafb70fa70d017e8a6724bfa.
    ["Edward d'Auvergne", "Dhanasekaran Muthu (dhanas@email.arizona.edu)",
        "Added the truncated data for creating a system test to catch bug #21562. (2014-01-31 08:50:28 +0000)"],
    # r21729 - 4b36d8c249da452817c14ac2acab6ef015eced75.
    ["Edward d'Auvergne", "Nilamoni Nath (nilamoni.nath@gmail.com)",
        "Added another Gaussian log file of strchnine, this time with DFT structure optimisation. (2013-12-02 07:33:37 +0000)"],
    # r21719 - 9b03f10cf4b9dee8d87580342af976ae7226c634.
    ["Edward d'Auvergne", "Nilamoni Nath (nilamoni.nath@gmail.com)",
        "Added a Gaussian DFT optimisation log file to the shared data directories. (2013-11-29 13:47:36 +0000)"],
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
    # r20782 - 0a8f0f800d97106640cacc817a59a56125eea168.
    ["Edward d'Auvergne", "Troels Emtekær Linnet",
        "Data provided for the implementation of the slow-exchange analytic model of the Tollinger/Kay (2001). (2013-09-03 16:49:54 +0000)"],
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
    # r14793 - 4e298cc3cd77c68b406b4d91fb313ab5aec327d6.
    ["Edward d'Auvergne", "Elio Cino (ecino@uwo.ca)",
        "Added some peak list files in preparation for a system test to catch bug #18789. (2011-10-05 16:41:37 +0000)"],
    # r13110 - 7a3a8bcc76740e1acea65281d5fd984f8ec47123.
    ["Edward d'Auvergne", "Han Sun",
        "Generating two new functions '__parse_xyz_record()' and 'fill_object_from_xyz()'. (2011-06-17 14:10:19 +0000)"],
    # r13109 - b202796fa628c879a96f125e8716db55d76d1593.
    ["Edward d'Auvergne", "Han Sun",
        "Debugging and cleaning up the user functions load_xyz() and __parse_models_xyz(). (2011-06-17 13:57:30 +0000)"],
    # r13106 - 38d18340a13ad1dfaf5a3640a868bd2bc64d9198.
    ["Edward d'Auvergne", "Han Sun",
        "Changing the name of the user function __parse_models() to __parse_models_pdb() (2011-06-17 12:50:41 +0000)"],
    # r13091 - 88f7142e74c216ea0e150d3e4da6095c8c5c5579.
    ["Edward d'Auvergne", "Han Sun",
        "Generating new user functions load_xyz() and __parse_models_xyz(). (2011-06-17 10:05:06 +0000)"],
    # r13090 - efed417e2adb3e28309238e29f2d06a03805de46.
    ["Edward d'Auvergne", "Han Sun",
        "Generating new system test 'test_read_xyz_internal2()'. (2011-06-17 09:39:57 +0000)"],
    # r13089 - c91b5bbbbfcc075ba08f9b7b990c08856ef73f1b.
    ["Edward d'Auvergne", "Han Sun",
        "Modifying test_suite/shared_data/structures/Indol_test.xyz (2011-06-17 09:17:27 +0000)"],
    # r13082 - d335b984528a07daff7810c79de7970931a48258.
    ["Edward d'Auvergne", "Han Sun",
        "Modifying the user function 'read_xyz()'. (2011-06-17 08:38:40 +0000)"],
    # r13061 - c900d55ec819d9ac2b17d8221735eb520b7619e5.
    ["Edward d'Auvergne", "Han Sun",
        "Adding a new test xyz file. (2011-06-16 09:37:42 +0000)"],
    # r12968 - d132e4d35fac5f37bd04b8d6b841d100ca3ac305.
    ["Edward d'Auvergne", "Han Sun",
        "Generating new user function 'read_xyz()'. (2011-06-10 13:08:46 +0000)"],
    # r12958 - dc814f60f9755df80f91dac2264df88d049c04b2.
    ["Edward d'Auvergne", "Han Sun",
        "Generating new user function 'read_xyz()'. (2011-06-10 10:13:16 +0000)"],
    # r12953 - 9407f2880108594c9481df4bcaa0c242a28561d6.
    ["Edward d'Auvergne", "Han Sun",
        "Modifying the function test 'test_read_xyz_internal1()'. (2011-06-10 09:14:46 +0000)"],
    # r12946 - 21c7223809beffe8de475e64994d3c6c7c812974.
    ["Edward d'Auvergne", "Han Sun",
        "Modifying the function test 'test_read_xyz_internal1()'. (2011-06-09 18:02:09 +0000)"],
    # r12942 - de8b4e6afa609366b16ffa6b106550dbd4182761.
    ["Edward d'Auvergne", "Han Sun",
        "Creation of a new system test test_read_xyz_internal1(). (2011-06-09 16:49:18 +0000)"],
    # r12060 - c1a61d03a865e0290646ae24e9287ef3dc57cc9b.
    ["Edward d'Auvergne", "Michael Bieri",
        "Added Michael Bieri's model-free data extraction script. (2010-12-31 08:36:09 +0000)"],
    # r10743 - 14fd24529b55a34763a362051dc2cd96f216786e.
    ["Edward d'Auvergne", "Uwe Reinscheid (urei@nmr.mpibpc.mpg.de)",
        "Added a few Gromacs QM/MM snapshots. (2010-02-18 16:08:35 +0000)"],
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
    # r8205 - 69f296590d627d2df4d809f10721cc8abf1fcd2e.
    ["Edward d'Auvergne", "Mate Erdelyi (mate.erdelyi@chem.gu.se)",
        "Added 10 tag PDB files for the lactose system test. (2008-12-12 09:56:09 +0000)"],
    # r8202 - a16582e14f1c8feacae5b2ecf5c1b75102072ac6.
    ["Edward d'Auvergne", "Mate Erdelyi (mate.erdelyi@chem.gu.se)",
        "Added 3 more lactose structures. (2008-12-12 09:31:12 +0000)"],
    # r6613 - 60e9185a242b6abb950a06fcc442bd82a240bfec.
    ["Edward d'Auvergne", "Ryan Hoffman (rmhoff@scripps.edu)",
        "Addition of an NMRView peak list for use in the relax test suite. (2008-07-03 18:35:54 +0000)"],
    # r26791 - efd2b6c69986d2f98bf74323d1a869aa8b0f068a.
    ["Edward d'Auvergne", "Andras Boeszoermenyi (Andras_Boeszoermenyi@hms.harvard.edu)",
        "Added the synthetic saturation-recovery data in the form of Sparky peak lists to the repository. (2014-11-27 18:11:38 +0000)"],
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
            if line[0] in ['#', '%', '*']:
                line = line[1:]
            if line[-1] in ['#', '%', '*']:
                line = line[:-2]
            if search("^rem", line):
                line = line[4:]
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
    file_name = file_name.replace('+', '\+')
    for line in lines:
        if search("^%s: " % file_name, line) and "Copyright (C)" in line:
            statements.append(line[line.index("Copyright"):].strip())

    # Return the list of copyright statements.
    return statements


def extract_public_domain_readme(file_name, root):
    """Try to extract public domain information for the file from the README file.

    @param file_name:   The isolated file name to search for the public domain notice.
    @type file_name:    str
    @param root:        The file path root which should contain the README file.
    @type root:         str
    @return:            True if the file is stated as public domain, False otherwise.
    @rtype:             bool
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
    file_name = file_name.replace('+', '\+')
    for line in lines:
        if search("^%s: " % file_name, line) and "Public domain" in line:
            return True

    # Not public domain.
    return False


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
        statements.append("Copyright (C) %s %s" % (years, committer))

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
    pipe = Popen("git log %s %s --numstat --follow --pretty='%%an Ø %%ad Ø %%H Ø %%s' --date=iso \"%s\"" % (after_opt, before_opt, full_path), shell=True, stdout=PIPE, close_fds=False)

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
        year = int(date.split('-')[0])
        commit_key = "%s (%s)" % (subject.strip(), date)

        # Translate the committer name, if necessary.
        committer = translate_committer_name(committer)

        # The next line is a committer, so skip the current line.
        if search(' Ø ', lines[i+1].decode()):
            i += 1
            continue

        # Author switch.
        for j in range(len(author_switch)):
            if author_switch[j][2] == commit_key:
                committer = translate_committer_name(author_switch[j][1])

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
    pipe = Popen("svn log --diff %s \"%s\"" % (date_range, full_path), shell=True, stdout=PIPE, close_fds=False)

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
        if search('^------------------------------------------------------------------------$', lines[i]) and lines[i+1][0] == 'r':
            # Move to the summary line.
            i += 1

            # Extract the committer and year.
            rev, svn_committer, date, length = lines[i].split(' | ')
            committer = SVN_COMMITTERS[svn_committer]
            year = int(date.split()[0].split('-')[0])
            date = date.split(" (")[0]
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')
            date = date.astimezone(tz=utc)

            # Translate the committer name, if necessary.
            committer = translate_committer_name(committer)

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
                if i >= len(lines):
                    break
                if search('^------------------------------------------------------------------------$', lines[i]) and i < len(lines)-1 and len(lines[i+1]) and lines[i+1][0] == 'r':
                    break

                # Inside the diff.
                if search('^===================================================================$', lines[i]):
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

        # Author switch.
        for j in range(len(author_switch)):
            if author_switch[j][2] == commit_key:
                committer = translate_committer_name(author_switch[j][1])

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


def translate_committer_name(committer):
    """Translate the committer name, if necessary.

    @param committer:   The committer name to translate.
    @type committer:    str
    @return:            The translated name.
    @rtype:             str
    """

    # The name is in the translation table.
    if committer in COMMITTERS:
        return COMMITTERS[committer]

    # Or not.
    return committer


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

    # Handle files as arguments.
    file_arg = None
    if path.isfile(directory):
        directory, file_arg = path.split(directory)

    # Initial printout.
    if file_arg:
        sys.stdout.write("\nFSF copyright notice compliance checking for the file '%s%s%s'.\n\n" % (directory, sep, file_arg))
    else:
        sys.stdout.write("\nFSF copyright notice compliance checking for the directory '%s'.\n\n" % directory)
    sys.stdout.flush()

    # Counters.
    files_total = 0
    files_blacklisted = 0
    files_untracked = 0
    files_valid = 0
    files_nonvalid = 0

    # Walk through the current dir, alphabetically.
    for root, dirs, files in walk(directory):
        dirs.sort()

        # Single file argument.
        if file_arg and directory != root:
            continue

        # Directory skip.
        skip = False
        for name in DIR_SKIP:
            if name in root:
                skip = True
                break
        if skip:
            continue

        # Validate any copyright statements in the README file, if present.
        validate_readme(root)

        # Loop over the files.
        files.sort()
        for file_name in files:
            # Command line argument supplied file.
            if file_arg and file_name != file_arg:
                continue

            # Count the file.
            files_total += 1

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
                files_blacklisted += 1
                continue

            # Check for untracked files.
            if REPOS[-1][1] == 'git':
                pipe = Popen("git ls-files \"%s\" --error-unmatch; echo $?" % file_path, shell=True, stderr=PIPE, stdout=PIPE, close_fds=False)
            else:
                pipe = Popen("svn info \"%s/%s/%s\"" % (REPOS[-1][0], REPOS[-1][4], file_path), shell=True, stderr=PIPE, stdout=PIPE, close_fds=False)
            err = pipe.stderr.readlines()
            if err:
                sys.stdout.write("Untracked file: %s (mimetype = '%s')\n" % (file_path, type))
                sys.stdout.flush()
                files_untracked += 1
                continue

            # Determine the file type.
            type, encoding = mimetypes.guess_type(file_path)
            sys.stdout.write("Checking: %s (mimetype = '%s')\n" % (file_path, type))
            sys.stdout.flush()

            # Public domain files.
            if extract_public_domain_readme(file_name, root):
                files_valid += 1
                continue

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

            # Add any additional committer years.
            if file_path in ADDITIONAL_COPYRIGHT_YEARS:
                for year, committer in ADDITIONAL_COPYRIGHT_YEARS[file_path]:
                    if not committer in committer_info:
                        committer_info[committer] = []
                    if year not in committer_info[committer]:
                        committer_info[committer].append(year)

            # Remove false negative years.
            if file_path in FALSE_NEG_YEARS:
                for year, committer in FALSE_NEG_YEARS[file_path]:
                    if committer in committer_info and year in committer_info[committer]:
                        committer_info[committer].pop(committer_info[committer].index(year))
                        if not len(committer_info[committer]):
                            del committer_info[committer]

            # Format the data as copyright statements.
            expected_copyright = format_copyright(committer_info)

            # Search for missing copyright notices in local README files.
            recorded_copyright = extract_copyright_readme(file_name, root)

            # Otherwise parse text files for the current copyright statements.
            if not len(recorded_copyright) and type not in BINARY_MIMETYPES and file_path not in BINARY_FILES:
                recorded_copyright = extract_copyright(file_path)

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
                files_valid += 1
                continue
            files_nonvalid += 1

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

    # Final printout.
    sys.stdout.write("\n\nStatistics:\n\n")
    sys.stdout.write("    %-35s %8i\n" % ("All files:", files_total))
    sys.stdout.write("    %-35s %8i\n" % ("Blacklisted files:", files_blacklisted))
    sys.stdout.write("    %-35s %8i\n" % ("Untracked files:", files_untracked))
    sys.stdout.write("\n")
    sys.stdout.write("    %-35s %8i\n" % ("Validated file count:", files_valid+files_nonvalid))
    sys.stdout.write("    %-35s %8i\n" % ("Non-matching copyright notices:", files_nonvalid))
