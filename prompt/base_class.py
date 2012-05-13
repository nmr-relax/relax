###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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

# Module docstring.
"""The base class for all the user function classes."""

# Python module imports.
from string import split
from textwrap import wrap

# relax module imports.
import ansi
import help
from relax_string import strip_lead
from status import Status; status = Status()


def _bold_text(text):
    """Convert the text to bold.

    This is for use in the help system.

    @param text:    The text to make bold.
    @type text:     str
    @return:        The bold text.
    @rtype:         str
    """

    # Init.
    new_text = ''

    # Add the bold character to all characters.
    for i in range(len(text)):
        new_text += "%s\b%s" % (text[i], text[i])

    # Return the text.
    return new_text


def _build_doc(fn):
    """Build the fn.__doc__ docstring.

    @param fn:  The user function to build the docstring for.
    @type fn:   method
    """

    # Initialise.
    fn.__doc__ = ""

    # Add the title.
    fn.__doc__ = "%s%s\n" % (fn.__doc__, fn._doc_title)

    # Add the keyword args.
    if hasattr(fn, '_doc_args'):
        fn.__doc__ = fn.__doc__ + _build_subtitle("Keyword Arguments")
        for arg, desc in fn._doc_args:
            # The text.
            text = "%s:  %s" % (arg, desc)

            # Format.
            text = _format_text(text)

            # Add to the docstring.
            fn.__doc__ = "%s%s\n" % (fn.__doc__, text)

    # Add the description.
    if hasattr(fn, '_doc_desc'):
        fn.__doc__ = fn.__doc__ + _build_subtitle("Description")
        fn.__doc__ = fn.__doc__ + _format_text(fn._doc_desc)

    # Add the examples.
    if hasattr(fn, '_doc_examples'):
        fn.__doc__ = fn.__doc__ + '\n' + _build_subtitle("Examples")
        fn.__doc__ = fn.__doc__ + _format_text(fn._doc_examples)

    # Add the additional sections.
    if hasattr(fn, '_doc_additional'):
        # Loop over each section.
        for i in range(len(fn._doc_additional)):
            fn.__doc__ = fn.__doc__ + '\n' + _build_subtitle(fn._doc_additional[i][0])
            fn.__doc__ = fn.__doc__ + _format_text(fn._doc_additional[i][1])

    # Convert the _doc_args list into a dictionary for easy argument description retrieval.
    if hasattr(fn, '_doc_args'):
        # Init.
        fn._doc_args_dict = {}

        # Loop over the args.
        for arg, desc in fn._doc_args:
            fn._doc_args_dict[arg] = desc



def _build_subtitle(text, bold=True):
    """Create the formatted subtitle string.

    @param text:        The name of the subtitle.
    @type text:         str
    @keyword colour:    A flag which if true will return bold text.  Otherwise an underlined title will be returned.
    @type colour:       bool
    @return:            The formatted subtitle.
    @rtype:             str
    """

    # Bold.
    if bold:
        new = "\n%s\n\n" % _bold_text(text)

    # Underline.
    else:
        new = "\n%s\n%s\n\n" % (text, "~"*len(text))

    # Return the subtitle.
    return new


def _format_text(text):
    """Format the text by stripping whitespace and wrapping.

    @param text:    The text to strip and wrap.
    @type text:     str
    @return:        The stripped and wrapped text.
    @rtype:         str
    """

    # First strip whitespace.
    stripped_text = strip_lead(text)

    # Remove the first characters if newlines.
    while True:
        if stripped_text[0] == "\n":
            stripped_text = stripped_text[1:]
        else:
            break

    # Remove the last character if a newline.
    while True:
        if stripped_text[-1] == "\n":
            stripped_text = stripped_text[:-1]
        else:
            break

    # Then split into lines.
    lines = split(stripped_text, "\n")

    # Then wrap each line.
    new_text = ""
    for line in lines:
        # Empty line, so preserve.
        if not len(line):
            new_text = new_text + "\n"

        # Wrap the line.
        for wrapped_line in wrap(line, status.text_width):
            new_text = new_text + wrapped_line + "\n"

    # Return the formatted text.
    return new_text
