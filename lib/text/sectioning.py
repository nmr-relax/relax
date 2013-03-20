###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Functions for the formatting of titles, subtitles and other sectioning."""


def box(file=None, text=None, char=None):
    """Format and write out a box surrounding the text.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The text to box.
    @type text:         str
    @keyword char:      The single character to use for the box.
    @type char:         str
    """

    # The length and horizontal box text.
    length = len(text) + 4
    hline = char * length

    # The text.
    file.write("%s\n" % hline)
    file.write("%s %s %s\n" % (char, text, char))
    file.write("%s\n" % hline)


def section(file=None, text=None, prespace=2, postspace=1):
    """Format and write out a section to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The section text.
    @type text:         str
    @keyword prespace:  The number of empty lines prior to the text printout.
    @type prespace:     int
    @keyword postspace: The number of empty lines after the text printout.
    @type postspace:    int
    """

    # Format the text.
    file.write("\n" * prespace)
    underline(file=file, text=text, char="=")
    file.write("\n" * postspace)


def subsection(file=None, text=None, prespace=1, postspace=1):
    """Format and write out a subsection to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The subsection text.
    @type text:         str
    @keyword prespace:  The number of empty lines prior to the text printout.
    @type prespace:     int
    @keyword postspace: The number of empty lines after the text printout.
    @type postspace:    int
    """

    # Format the text.
    file.write("\n" * prespace)
    underline(file=file, text=text, char="-")
    file.write("\n" * postspace)


def subsubsection(file=None, text=None, prespace=1, postspace=1):
    """Format and write out a subsubsection to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The subsubsection text.
    @type text:         str
    @keyword prespace:  The number of empty lines prior to the text printout.
    @type prespace:     int
    @keyword postspace: The number of empty lines after the text printout.
    @type postspace:    int
    """

    # Format the text.
    file.write("\n" * prespace)
    underline(file=file, text=text, char="~")
    file.write("\n" * postspace)


def subsubtitle(file=None, text=None, prespace=1, postspace=1):
    """Format and write out a subsubtitle to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The subsubtitle text.
    @type text:         str
    @keyword prespace:  The number of empty lines prior to the text printout.
    @type prespace:     int
    @keyword postspace: The number of empty lines after the text printout.
    @type postspace:    int
    """

    # Format the text.
    file.write("\n" * prespace)
    box(file=file, text=text, char="~")
    file.write("\n" * postspace)


def subtitle(file=None, text=None, prespace=1, postspace=1):
    """Format and write out a subtitle to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The subtitle text.
    @type text:         str
    @keyword prespace:  The number of empty lines prior to the text printout.
    @type prespace:     int
    @keyword postspace: The number of empty lines after the text printout.
    @type postspace:    int
    """

    # Format the text.
    file.write("\n" * prespace)
    box(file=file, text=text, char="-")
    file.write("\n" * postspace)


def title(file=None, text=None, prespace=2, postspace=1):
    """Format and write out a title to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The title text.
    @type text:         str
    @keyword prespace:  The number of empty lines prior to the text printout.
    @type prespace:     int
    @keyword postspace: The number of empty lines after the text printout.
    @type postspace:    int
    """

    # Format the text.
    file.write("\n" * prespace)
    box(file=file, text=text, char="=")
    file.write("\n" * postspace)


def underline(file=None, text=None, char=None):
    """Format and write out the text underlined by the given character.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The text to underline.
    @type text:         str
    @keyword char:      The single character to use for the underline.
    @type char:         str
    """

    # The length and horizontal underline text.
    length = len(text)
    hline = char * length

    # The text.
    file.write("%s\n" % text)
    file.write("%s\n" % hline)
