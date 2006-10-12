###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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


# Import statements.
from glob import glob
import platform
from os import F_OK, access, chdir, getcwd, path, remove, sep, system
from shutil import move
import sys

from version import version



def acro(target, source, env):
    """Builder action for executing Adobe Acrobat reader with the PDF manual."""

    # Print out.
    print
    print "##############################################"
    print "# Viewing the PDF manual using Adobe Acrobat #"
    print "##############################################\n\n"

    print "Running the command:\n$ acroread -openInNewWindow " + env['DOCS_DIR'] + "relax.pdf &\n\n\n"
    system("acroread -openInNewWindow " + env['DOCS_DIR'] + "relax.pdf &")


def clean_manual_files(target, source, env):
    """Builder action for removing the temporary manual files."""

    # Print out.
    print
    print "##########################################"
    print "# Cleaning up the temporary manual files #"
    print "##########################################\n\n"

    # File list to remove.
    files = ["relax.bbl",
             "relax.blg",
             "relax.dvi",
             "relax.idx",
             "relax.ilg",
             "relax.ind",
             "relax.lof",
             "relax.log",
             "relax.lot",
             "relax.out",
             "relax.toc"]

    # Add the LaTeX directory.
    for i in xrange(len(files)):
        files[i] = path.join(env['LATEX_DIR'], files[i])

    # LaTeX auxillary files.
    for file in glob(env['LATEX_DIR'] + '*.aux'):
        files.append(file)

    # Remove the files.
    for file in files:
        try:
            remove(file)
        except OSError, message:
            # The file does not exist.
            if message.errno == 2:
                pass

            # All other errors.
            else:
                raise
        else:
            print "Removing the file " + `file` + "."

    # Final print out.
    print "\n\n\n"


def fetch_docstrings(target, source, env):
    """Builder action for fetching the relax user function docstrings."""

    # Print out.
    print
    print "###############################################"
    print "# Fetching the relax user function docstrings #"
    print "###############################################\n\n"

    # Import the fetch_docstrings module (needs to be done here so that Sconstruct doesn't need to load the entire program each time).
    sys.path.append(getcwd())
    from docs.latex.fetch_docstrings import Fetch_docstrings

    # Get the docstrings.
    Fetch_docstrings(env['LATEX_DIR'] + sep + 'docstring.tex')

    # Final print out.
    print "\n\n\n"


def user_manual_html(target, source, env):
    """Builder action for creating the HTML manual."""

    # Print out.
    print
    print "############################"
    print "# Creating the HTML manual #"
    print "############################\n\n"

    # Go to the LaTeX directory.
    base_dir = getcwd()
    chdir(env['LATEX_DIR'])

    # Get the docstrings.
    print "Running the command:\n$ latex2html -split +3 -html_version 4.0 -dir " + path.pardir + path.sep + "html relax.tex\n\n\n"
    system("latex2html -split +3 -html_version 4.0 -dir " + path.pardir + path.sep + "html relax.tex")

    # Return to the base directory.
    chdir(base_dir)

    # Final print out.
    print "\n\n\n"


def user_manual_pdf(target, source, env):
    """Builder action for compiling the LaTeX manual into a PDF file."""

    # Print out.
    print
    print "###################################"
    print "# LaTeX compilation of the manual #"
    print "###################################\n\n"

    # Go to the LaTeX directory.
    base_dir = getcwd()
    chdir(env['LATEX_DIR'])

    print "\n\n\n <<< LaTeX (first round) >>>\n\n\n"
    system('latex relax')

    print "\n\n\n <<< Bibtex >>>\n\n\n"
    system('bibtex relax')

    print "\n\n\n <<< Makeindex >>>\n\n\n"
    system('makeindex relax')

    print "\n\n\n <<< LaTeX (second round) >>>\n\n\n"
    system('latex relax')

    print "\n\n\n <<< LaTeX (third round) >>>\n\n\n"
    system('latex relax')

    print "\n\n\n <<< LaTeX (fourth round) >>>\n\n\n"
    system('latex relax')

    print "\n\n\n <<< dvips >>>\n\n\n"
    system('dvips -o relax.ps relax.dvi')

    print "\n\n\n <<< ps2pdf >>>\n\n\n"
    if env['SYSTEM'] == 'Windows':
        # According to the Ghostscript documentation, "When passing options to ghostcript through a batch
        # file wrapper such as ps2pdf.bat you need to substitute '#' for '=' as the separator between options
        # and their arguments."
        assign = '#'
    else:
        assign = '='
    system('ps2pdf -dAutoFilterColorImages' + assign + 'false -dAutoFilterGrayImages' + assign + 'false -dColorImageFilter' + assign + '/FlateEncode -dColorImageFilter' + assign + '/FlateEncode -dGrayImageFilter' + assign + '/FlateEncode -dMonoImageFilter' + assign + '/FlateEncode -dPDFSETTINGS' + assign + '/prepress relax.ps relax.pdf')

    print "\n\n\n <<< Removing the PS file and shifting the PDF down a directory >>>\n\n\n"
    if access('relax.ps', F_OK):
        remove('relax.ps')
    if access('relax.pdf', F_OK):
        move('relax.pdf', path.pardir)

    # Return to the base directory.
    chdir(base_dir)

    # Final print out.
    print "\n\n\n"


def version_file(target, source, env):
    """Builder action for creating the LaTeX relax version file."""

    # Print out.
    print
    print "################################################"
    print "# Creating the LaTeX relax version number file #"
    print "################################################"

    # Place the program version number into a LaTeX file.
    file = open(env['LATEX_DIR'] + sep + 'relax_version.tex', 'w')
    file.write("Version " + version + '\n')
    file.close()

    # Final print out.
    print "\n\n\n"
