###############################################################################
#                                                                             #
# Copyright (C) 2006,2008-2009,2011-2012,2015,2017-2019 Edward d'Auvergne     #
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
"""SCons targets for building the relax manuals."""

# Python module imports.
from datetime import datetime
from glob import glob
from os import F_OK, access, chdir, getcwd, listdir, path, remove, rename, sep, system
from re import search
from subprocess import PIPE, Popen
import sys

# relax module imports.
from info import Info_box
from status import Status; status = Status()
import version


def clean_manual_files(target, source, env):
    """Builder action for removing the temporary manual files."""

    # Print out.
    print('')
    print("##########################################")
    print("# Cleaning up the temporary manual files #")
    print("##########################################\n\n")

    # File list to remove.
    files = [
        "relax.bbl",
        "relax.blg",
        "relax.dvi",
        "relax.idx",
        "relax.ilg",
        "relax.ind",
        "relax.lof",
        "relax.log",
        "relax.lot",
        "relax.out",
        "relax.toc",
        "copyright.tex"
    ]

    # Add the LaTeX directory.
    for i in range(len(files)):
        files[i] = path.join(env['LATEX_DIR'], files[i])

    # LaTeX auxillary files.
    for file in glob(env['LATEX_DIR'] + '*.aux'):
        files.append(file)
    for file in glob(env['LATEX_DIR'] + 'frame_order' + sep + '*.aux'):
        files.append(file)

    # Remove the files.
    for file in files:
        try:
            remove(file)
        except OSError:
            message = sys.exc_info()[1]

            # The file does not exist.
            if message.errno == 2:
                pass

            # All other errors.
            else:
                raise
        else:
            print("Removing the file " + repr(file) + ".")

    # Final printout.
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
    exclude = [
        'devel_scripts',
        'extern',
        'graphics',
        'minfx.scipy_subset',
        'multi.test_implementation',
        'multi.test_implementation2',
        'sample_scripts',
        'test_suite.system_tests.scripts',
        'test_suite.shared_data'
    ]

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
    url = 'http://www.nmr-relax.com'

    # link
    #   HTML code for the project link in the navigation bar.  If left
    #   unspecified, the project link will be generated based on the
    #   project's name and URL.
    link = '<a href="/">relax</a>'

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
    epydoc_cmd = 'epydoc' + ' --' + output + ' -o ' + target + ' --docformat ' + docformat + ' --css ' + css + ' --name ' + name + ' --url ' + url + ' --simple-term'
    if 'link' in locals():
        epydoc_cmd += ' --navlink \'%s\'' % link

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

    # Process all files and directories in the base relax directory.
    blacklist = ['relax_gui_mode.py']
    files = listdir(getcwd())
    for file in files:
        # Blacklisted.
        if file in blacklist:
            continue

        # The excluded ones.
        if file in exclude:
            continue

        # Hidden files and directories.
        if search(r'^\.', file):
            continue

        # Not a Python file.
        if not path.isdir(file) and not search('.py$', file):
            continue

        # Otherwise add it.
        epydoc_cmd = "%s %s" % (epydoc_cmd, file)


    # Execute Epydoc.
    #################

    # Printout.
    print("Running the command:\n$ " + epydoc_cmd + "\n\n\n")

    # System call.
    pipe = Popen(epydoc_cmd, shell=True, stdout=PIPE, stderr=PIPE, close_fds=False)

    # Parse the output.
    issues = []
    for line in pipe.stdout.readlines():
        if len(line.strip()) and line[0] in ['+', '|']:
            # Printout.
            sys.stdout.write(line)

            # A new issue
            if search(r"^\+----------", line):
                issues.append("")
                continue

            # Append the text.
            issues[-1] += line[2:].rstrip()

    # Check for issues.
    for issue in issues:
        # Skip wxPython docstring errors (not import errors).
        if "wx/" in issue:
            continue

        # Skip pystarlib docstring errors (not import errors).
        if "pystarlib/" in issue:
            continue

        # Fail on everything else.
        raise NameError("Errors or warnings found.")


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


    # Modify all HTML files.
    ########################

    # Print out.
    print("\n\nModifying the header of all HTML files.\n")

    # Copyright notice.
    today = datetime.today()
    creator = "Edward d'Auvergne"
    copyright = """\
<!--
    Copyright (C) %i %s

    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License, Version 1.3
    or any later version published by the Free Software Foundation;
    with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    A copy of the license is included in the section titled "GNU
    Free Documentation License" (fdl.html).
-->
""" % (today.year, creator)

    # The additional head tags.
    head_lines = []

    # The Google analytics JS.
    file = open(status.install_path + sep + 'devel_scripts' + sep + 'google_analytics.js')
    for line in file.readlines():
        head_lines.append(line)
    file.close()

    # Loop over the files.
    for file_name in listdir(status.install_path + sep + 'docs' + sep + 'api'):
        # The full path.
        full_path = status.install_path + sep + 'docs' + sep + 'api' + sep + file_name

        # Skip all non-html files.
        if not search('.html$', full_path):
            continue

        # Open the file and read the data.
        file = open(full_path)
        lines = file.readlines()
        file.close()

        # Modify the original file.
        file = open(full_path, 'w')

        # Loop over the lines.
        i = 0
        while 1:
            # Termination.
            if i > len(lines)-1:
                break

            # Pre-header copyright notice insertion.
            if search('<head>', lines[i]):
                file.write(copyright)

            # Header insertions (e.g. Google analytics JS).
            if search('</head>', lines[i]):
                start = False
                for j in range(len(head_lines)):
                    # Skip the copyright notice.
                    if not start and search("Google analytics JS", head_lines[j]):
                        start = True

                    # Write out the rest.
                    if start:
                        file.write(head_lines[j])

            # Write out the content line.
            file.write(lines[i])

            # Increment the line number.
            i += 1

        # Close the file.
        file.close()

    # Final printout.
    print("\n\n\n")


def compile_user_manual_html(target, source, env):
    """Builder action for compiling the user manual (HTML version) from the LaTeX sources."""

    # Make the PDF manual to generate the aux files.
    compile_user_manual_pdf(target, source, env, convert=False)

    # Print out.
    print('')
    print("############################################")
    print("# Compiling the user manual (HTML version) #")
    print("############################################\n\n")

    # Go to the LaTeX directory.
    base_dir = getcwd()
    chdir(env['LATEX_DIR'])

    # The target directory.
    dir = path.pardir + path.sep + "html"

    # Run the latex2html command.
    cmd = "latex2html -dir %s relax.tex" % (dir)
    print("Running the command:\n$ %s\n\n\n" % cmd)
    system(cmd)

    # Create the proper index.html file.
    cmd = "cp -vp %s%sThe_relax_user_manual.html %s%sindex.html" % (dir, path.sep, dir, path.sep)
    print("Running the command:\n$ %s\n\n\n" % cmd)
    system(cmd)

    # Modify the CSS file.
    css_file = open(path.join(dir, 'relax.css'))
    css = css_file.readlines()
    css_file.close()
    css_file = open(path.join(dir, 'relax.css'), 'w')
    for line in css:
        # Fix the body width.
        if search("^BODY { ", line):
            css_file.write("BODY { width:95%; }\n")

        # Preserve all other lines.
        else:
            css_file.write(line)

    # Return to the base directory.
    chdir(base_dir)

    # Final printout.
    print("\n\n\n")


def compile_user_manual_pdf(target, source, env, convert=True):
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

    print("\n\n\n <<< Makeindex >>>\n\n\n")
    system('makeindex relax')

    print("\n\n\n <<< LaTeX (fourth round) >>>\n\n\n")
    system('latex relax')

    # Skip the rest.
    if not convert:
        # Return to the base directory.
        chdir(base_dir)

        # Return.
        return

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

    # Final printout.
    print("\n\n\n")


def copyright_file(target, source, env):
    """Builder action for creating the LaTeX copyright notice file."""

    # Print out.
    print('')
    print("##################################################")
    print("# Creating the LaTeX relax copyright notice file #")
    print("##################################################")

    # The LaTeX file.
    file = open(env['LATEX_DIR'] + sep + 'copyright.tex', 'w')

    # Initialise the info box.
    info = Info_box()

    # The notice.
    file.write("\\noindent %s\n\n" % info.copyright_latex)
    file.write("\\vspace{5px}\n\n")

    # The text.
    file.write("\\noindent Permission is granted to copy, distribute and/or modify this document under the terms of the GNU General Public License (GPL), Version 3 or any later version published by the Free Software Foundation.\n")
    file.write("\\vspace{5px}\n\n")
    file.write("\\noindent The Oxygen Icons used herein are licensed under the terms of the GNU Lesser General Public License (GPL), Version 3 or any later version published by the Free Software Foundation.\n")

    # Close the file.
    file.close()

    # Final printout.
    print("\n\n\n")


def fetch_docstrings(target, source, env):
    """Builder action for fetching the relax user function docstrings."""

    # Print out.
    print('')
    print("###############################################")
    print("# Fetching the relax user function docstrings #")
    print("###############################################\n\n")

    # Import the fetch_docstrings module (needs to be done here so that Sconstruct doesn't need to load the entire program each time).
    sys.path.insert(0, getcwd())
    from docs.latex.fetch_docstrings import Fetch_docstrings

    # Get the docstrings.
    Fetch_docstrings(env['LATEX_DIR'] + sep + 'docstring.tex')

    # Delete the Fetch_docstrings class.  This allows the loaded dll files to be deleted through python on MS Windows.
    del Fetch_docstrings

    # Final printout.
    print("\n\n\n")


def replicate_title_check(target, source, env):
    """Builder action for checking for replicated titles in the LaTeX sources."""

    # Print out.
    print('')
    print("#######################################################")
    print("# Checking for replicated titles in the LaTeX sources #")
    print("#######################################################\n\n")

    # Import the find_replicate_titles module (needs to be done here so that Sconstruct doesn't need to load the entire program each time).
    sys.path.insert(0, getcwd())
    from docs.latex.find_replicate_titles import Replicated_titles

    # Find the replicates.
    replicates = Replicated_titles()
    if replicates.find():
        print("\n\nFatal error:  Replicated titles found.")
        print("\n\n\n")
        sys.exit(1)

    # Delete the Replicate_titles class.  This allows the loaded dll files to be deleted through python on MS Windows.
    del replicates
    del Replicated_titles

    # Final printout.
    print("No replicated titles found.")
    print("\n\n\n")


def version_file(target, source, env):
    """Builder action for creating the LaTeX relax version file."""

    # Print out.
    print('')
    print("################################################")
    print("# Creating the LaTeX relax version number file #")
    print("################################################")

    # Add the repository revision if not a normal release.
    text = version.version
    if text == 'repository commit':
        if version.repo_type == 'git':
            text += ' %s' % version.repo_head
        else:
            text += ' r%s' % version.repo_head

    # Place the program version number into a LaTeX file.
    file = open(env['LATEX_DIR'] + sep + 'relax_version.tex', 'w')
    file.write("Version " + text + '\n')
    file.close()

    # Final printout.
    print("\n\n\n")
