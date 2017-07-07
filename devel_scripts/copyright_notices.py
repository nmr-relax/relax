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
import mimetypes
from os import getcwd, path, sep, walk
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

# Alternative names for the committers.
COMMITTER_ALT = {
    "Gary S Thompson": "Gary Thompson",
    "Troels Schwartz-Linnet": "Troels E. Linnet",
}

# Blacklisted files.
BLACKLISTED_FILES = [
    '.gitignore',                                               # Trivial file list.
    'docs/COPYING',                                             # The original GPLv3 licence text.
]

# Directories to skip.
DIR_SKIP = [
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

# Stop incorrect git history by specifying the first commit key of a misidentified file.
GIT_START = {
}

# Additional copyright notices that are not present in the git log.
ADDITIONAL_COPYRIGHT = {
}

# Additional copyright years and authors to add to the list.  The keys are lists of lists of the year as an int and the author name as a string.
ADDITIONAL_COPYRIGHT_YEARS = {
}

# False positives (copyright notices in files to ignore, as they are not in the git log).
FALSE_POS = {
}

# False negatives (significant git log commits which do not imply copyright ownership).
FALSE_NEG = {
}
FALSE_NEG_YEARS = {
}

# Commits to exclude as a list of commit keys - the first line of the commit message followed by the ISO date in brackets.
EXCLUDE = [
]

# Commits to switch authorship of (e.g. if someone commits someone else's code).
# The data consists of:
#       0 - The comitter's name.
#       1 - The real author.
#       2 - The commit key, consisting of the first line of the commit message followed by the ISO date in brackets.
AUTHOR_SWITCH = [
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


def git_log_data(file_path, exclude=[], start_commit=[], author_switch=[], committer_info={}):
    """Get the committers and years of significant commits from the git log.

    @param file_path:           The full file path to obtain the git info for.
    @type file_path:            str
    @keyword exclude:           A list of commit keys to exclude from the search.  The commit key consists of the first line of the commit message followed by the ISO date in brackets.
    @type exclude:              list of str
    @keyword start_commit:      The starting commit for each file, where 'git log' identifies an incorrect history path.  This is a dictionary with the keys being the file paths and the values being the commit keys (the first line of the commit message followed by the ISO date in brackets).
    @type start_commit:         dict of str
    @keyword author_switch:     List of commit keys and authors to switch the authorship of.  The first element should be the comitter, the second the real comitter, and the third the commit key.  The commit key consists of the first line of the commit message followed by the ISO date in brackets.
    @type author_switch:        list of list of str
    @keyword committer_info:    The committer info data structure, listing the committers and years of significant commits.  This is a dictionary with the committer's name as a key with the value as the list of years.
    @type committer_info:       dict of lists of str
    """

    # File check.
    if not path.exists(file_path):
        sys.stderr.write("Warning, file missing from git: %s\n" % file_path)
        return

    # Exec.
    pipe = Popen("git log --numstat --follow --pretty='%%an Ø %%ad Ø %%H Ø %%s' --date=iso \"%s\"" % file_path, shell=True, stdout=PIPE, close_fds=False)

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
                committer = translate_committer_name(author_switch[j][1])

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
            pipe = Popen("git ls-files \"%s\" --error-unmatch; echo $?" % file_path, shell=True, stderr=PIPE, stdout=PIPE, close_fds=False)
            err = pipe.stderr.readlines()
            if err:
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

            # Get the committer and year information from the git log.
            committer_info = {}
            git_log_data(file_path, exclude_hashes=EXCLUDE, start_commit=GIT_START, author_switch=AUTHOR_SWITCH, committer_info=committer_info)
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
