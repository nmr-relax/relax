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


def subtitle(file=None, text=None):
    """Format and write out a subtitle to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The subtitle.
    @type text:         str
    """

    # The length and hline text.
    length = len(text) + 2
    hline = '#' * length

    # First the spacing above the section.
    file.write("\n")

    # The text.
    file.write("# %s\n" % text)
    file.write("%s\n" % hline)

    # Final spacing.
    file.write("\n")


def title(file=None, text=None):
    """Format and write out a title to the given file.

    @keyword file:      The file object to write to.
    @type file:         file object
    @keyword text:      The title.
    @type text:         str
    """

    # The length and hline text.
    length = len(text) + 4
    hline = '#' * length

    # First the spacing above the section.
    file.write("\n\n")

    # The text.
    file.write("%s\n" % hline)
    file.write("# %s #\n" % text)
    file.write("%s\n" % hline)

    # Final spacing.
    file.write("\n")
