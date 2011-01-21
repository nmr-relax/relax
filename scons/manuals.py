###############################################################################
#                                                                             #
# Copyright (C) 2006, 2009 Edward d'Auvergne                                  #
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
from os import F_OK, access, chdir, getcwd, path, remove, rename, sep, system
import sys

from version import version


def clean_manual_files(target, source, env):
    """Builder action for removing the temporary manual files."""

    # Print out.
    print('')
    print("##########################################")
    print("# Cleaning up the temporary manual files #")
    print("##########################################\n\n")

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
            print(("Removing the file " + repr(file) + "."))

    # Final print out.
    print("\n\n\n")


def compile_api_manual_html(target, source, env):
    """Builder action for compiling the API documentation manual (HTML version) using Epydoc."""

    # Print out.
    print('')
    print("#####################################################")
    print("# Compiling API documentation manual (HTML version) #")
    print("#####################################################\n\n")


    # Set up the Epydoc configuration (adapted from http://epydoc.sourceforge.net/configfile.html).
    ###############################################################################################

    # exclude
    #   The list of objects to exclude.
    exclude = ['sample_scripts', 'scripts']

    # output
    #   The type of output that should be generated.  Should be one
    #   of: html, text, latex, dvi, ps, pdf.
    output = 'html'

    # target
    #   The path to the output directory.  May be relative or absolute.
    target = 'docs'+sep+'api'

    # docformat
    #   The default markup language for docstrings, for modules that do
    #   not define __docformat__.
    docformat = 'epytext'

    # css
    #   The CSS stylesheet for HTML output.  Can be the name of a builtin
    #   stylesheet, or the name of a file.
    css = 'white'

    # name
    #   The documented project's name.
    name = 'relax'

    # url
    #   The documented project's URL.
    url = 'http://nmr-relax.com'

    # link
    #   HTML code for the project link in the navigation bar.  If left
    #   unspecified, the project link will be generated based on the
    #   project's name and URL.
    #link = '<a href="http://nmr-relax.com">relax</a>'

    # top
    #   The "top" page for the documentation.  Can be a URL, the name
    #   of a module or class, or one of the special names "trees.html",
    #   "indices.html", or "help.html"
    # top = 'os.path'

    # help
    #   An alternative help file.  The named file should contain the
    #   body of an HTML file; navigation bars will be added to it.
    # help = 'my_helpfile.html'

    # frames
    #   Whether or not to include a frames-based table of contents.
    frames = 1

    # private
    #   Whether or not to inclue private variables.  (Even if included,
    #   private variables will be hidden by default.)
    private = 1

    # imports
    #   Whether or not to list each module's imports.
    imports = 1

    # verbosity
    #   An integer indicating how verbose epydoc should be.  The default
    #   value is 0; negative values will supress warnings and errors;
    #   positive values will give more verbose output.
    verbosity = 1

    # parse
    #   Whether or not parsing should be used to examine objects.
    parse = 1

    # introspect
    #   Whether or not introspection should be used to examine objects.
    introspect = 1

    # graph
    #   The list of graph types that should be automatically included
    #   in the output.  Graphs are generated using the Graphviz "dot"
    #   executable.  Graph types include: "classtree", "callgraph",
    #   "umlclass".  Use "all" to include all graph types
    graph = 'all'

    # dotpath
    #   The path to the Graphviz "dot" executable, used to generate
    #   graphs.
    #dotpath = '/usr/local/bin/dot'

    # sourcecode
    #   Whether or not to include syntax highlighted source code in
    #   the output (HTML only).
    sourcecode = 1

    # pstat
    #   The name of one or more pstat files (generated by the profile
    #   or hotshot module).  These are used to generate call graphs.
    #pstat = 'profile.out'

    # separate-classes
    #   Whether each class should be listed in its own section when
    #   generating LaTeX or PDF output.
    #separate-classes = 0



    # Construct the command line string.
    ####################################

    # Program name, output, target, docformat, css, name, and url.
    epydoc_cmd = 'epydoc' + ' --' + output + ' -o ' + target + ' --docformat ' + docformat + ' --css ' + css + ' --name ' + name + ' --url ' + url

    # Frames.
    if frames:
        epydoc_cmd = epydoc_cmd + ' --show-frames'
    else:
        epydoc_cmd = epydoc_cmd + ' --no-frames'

    # Private variables.
    if private:
        epydoc_cmd = epydoc_cmd + ' --show-private'
    else:
        epydoc_cmd = epydoc_cmd + ' --no-private'

    # Module imports.
    if imports:
        epydoc_cmd = epydoc_cmd + ' --show-imports'
    else:
        epydoc_cmd = epydoc_cmd + ' --no-imports'

    # Verbosity.
    if verbosity > 0:
        for i in range(verbosity):
            epydoc_cmd = epydoc_cmd + ' -v'
    elif verbosity < 0:
        for i in range(-verbosity):
            epydoc_cmd = epydoc_cmd + ' -q'

    # Parsing and introspection.
    if parse and not introspect:
        epydoc_cmd = epydoc_cmd + ' --parse-only'
    elif not parse and introspect:
        epydoc_cmd = epydoc_cmd + ' --introspect-only'

    # Graph.
    epydoc_cmd = epydoc_cmd + ' --graph ' + graph

    # Sourcecode.
    if sourcecode:
        epydoc_cmd = epydoc_cmd + ' --show-sourcecode'
    else:
        epydoc_cmd = epydoc_cmd + ' --no-sourcecode'

    # Excluded modules.
    for name in exclude:
        epydoc_cmd = epydoc_cmd + ' --exclude=' + name

    # Document all code!
    epydoc_cmd = epydoc_cmd + ' *'


    # Execute Epydoc.
    #################

    # Print out.
    print(("Running the command:\n$ " + epydoc_cmd + "\n\n\n"))

    # System call.
    system(epydoc_cmd)



    # Modify the CSS file.
    ######################

    # Open the file.
    css_file = open(target + sep+'epydoc.css', 'a')

    # Header.
    css_file.write("\n\n\n\n/* Edward */\n\n")

    # Append the new link style to the end.
    css_file.write("a { text-decoration:none; color:#0017aa; font-weight:normal; }\n")
    css_file.write("a:hover { color:#316fff; }\n")

    # Close the file.
    css_file.close()

    # Final print out.
    print("\n\n\n")


def compile_user_manual_html(target, source, env):
    """Builder action for compiling the user manual (HTML version) from the LaTeX sources."""

    # Print out.
    print('')
    print("############################################")
    print("# Compiling the user manual (HTML version) #")
    print("############################################\n\n")

    # Go to the LaTeX directory.
    base_dir = getcwd()
    chdir(env['LATEX_DIR'])

    # Run the latex2html command.
    cmd = "latex2html -no_math -address http://nmr-relax.com -local_icons -html_version 4.0 -long_titles 5 -split 3 -dir %s -auto_navigation -antialias relax.tex" % (path.pardir + path.sep + "html")
    print("Running the command:\n$ %s\n\n\n" % cmd)
    system(cmd)

    # Return to the base directory.
    chdir(base_dir)

    # Final print out.
    print("\n\n\n")


def compile_user_manual_pdf(target, source, env):
    """Builder action for compiling the user manual (PDF version) from the LaTeX sources."""

    # Print out.
    print('')
    print("###########################################")
    print("# Compiling the user manual (PDF version) #")
    print("###########################################\n\n")

    # Go to the LaTeX directory.
    base_dir = getcwd()
    chdir(env['LATEX_DIR'])

    print("\n\n\n <<< LaTeX (first round) >>>\n\n\n")
    system('latex relax')

    print("\n\n\n <<< Bibtex >>>\n\n\n")
    system('bibtex relax')

    print("\n\n\n <<< Makeindex >>>\n\n\n")
    system('makeindex relax')

    print("\n\n\n <<< LaTeX (second round) >>>\n\n\n")
    system('latex relax')

    print("\n\n\n <<< LaTeX (third round) >>>\n\n\n")
    system('latex relax')

    print("\n\n\n <<< LaTeX (fourth round) >>>\n\n\n")
    system('latex relax')

    print("\n\n\n <<< dvips >>>\n\n\n")
    system('dvips -R0 -o relax.ps relax.dvi')

    print("\n\n\n <<< ps2pdf >>>\n\n\n")
    if env['SYSTEM'] == 'Windows':
        # According to the Ghostscript documentation, "When passing options to ghostcript through a batch
        # file wrapper such as ps2pdf.bat you need to substitute '#' for '=' as the separator between options
        # and their arguments."
        assign = '#'
    else:
        assign = '='
    system('ps2pdf -dAutoFilterColorImages' + assign + 'false -dAutoFilterGrayImages' + assign + 'false -dColorImageFilter' + assign + '/FlateEncode -dColorImageFilter' + assign + '/FlateEncode -dGrayImageFilter' + assign + '/FlateEncode -dMonoImageFilter' + assign + '/FlateEncode -dPDFSETTINGS' + assign + '/prepress relax.ps relax.pdf')

    print("\n\n\n <<< Removing the PS file and shifting the PDF down a directory >>>\n\n\n")
    if access('relax.ps', F_OK):
        remove('relax.ps')
    if access('relax.pdf', F_OK):
        rename('relax.pdf', path.pardir+path.sep+'relax.pdf')

    # Return to the base directory.
    chdir(base_dir)

    # Final print out.
    print("\n\n\n")


def fetch_docstrings(target, source, env):
    """Builder action for fetching the relax user function docstrings."""

    # Print out.
    print('')
    print("###############################################")
    print("# Fetching the relax user function docstrings #")
    print("###############################################\n\n")

    # Import the fetch_docstrings module (needs to be done here so that Sconstruct doesn't need to load the entire program each time).
    sys.path.append(getcwd())
    from docs.latex.fetch_docstrings import Fetch_docstrings

    # Get the docstrings.
    Fetch_docstrings(env['LATEX_DIR'] + sep + 'docstring.tex')

    # Delete the Fetch_docstrings class.  This allows the loaded dll files to be deleted through python on MS Windows.
    del Fetch_docstrings

    # Final print out.
    print("\n\n\n")


def version_file(target, source, env):
    """Builder action for creating the LaTeX relax version file."""

    # Print out.
    print('')
    print("################################################")
    print("# Creating the LaTeX relax version number file #")
    print("################################################")

    # Place the program version number into a LaTeX file.
    file = open(env['LATEX_DIR'] + sep + 'relax_version.tex', 'w')
    file.write("Version " + version + '\n')
    file.close()

    # Final print out.
    print("\n\n\n")
