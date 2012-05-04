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
import platform
from re import split
import sys
from textwrap import wrap

# relax module imports.
import ansi
import help
from status import Status; status = Status()
from string import split, strip

# The width of the text.
if platform.uname()[0] in ['Windows', 'Microsoft']:
    width = 80
else:
    width = 100


# Module variables.
###################

# The prompts (to change the Python prompt, as well as the function print outs).
PS1_ORIG = 'relax> '
PS2_ORIG = 'relax| '
PS3_ORIG = '\n%s' % PS1_ORIG

# Coloured text.
PS1_COLOUR = "%s%s%s" % (ansi.relax_prompt, PS1_ORIG, ansi.end)
PS2_COLOUR = "%s%s%s" % (ansi.relax_prompt, PS2_ORIG, ansi.end)
PS3_COLOUR = "\n%s%s%s" % (ansi.relax_prompt, PS1_ORIG, ansi.end)


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
    stripped_text = _strip_lead(text)

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
        for wrapped_line in wrap(line, width):
            new_text = new_text + wrapped_line + "\n"

    # Return the formatted text.
    return new_text


def _strip_lead(text):
    """Strip the leading whitespace from the given text.

    @param text:    The text to strip the leading whitespace from.
    @type text:     str
    @return:        The text with leading whitespace removed.
    @rtype:         str
    """

    # Split by newline.
    lines = split(text, '\n')

    # Find the minimum whitespace.
    min_white = 1000
    for line in lines:
        # Empty lines.
        if strip(line) == '':
            continue

        # Count the whitespace for the current line.
        num_white = 0
        for i in range(len(line)):
            if line[i] != ' ':
                break
            num_white = num_white + 1

        # The min value.
        min_white = min(min_white, num_white)

    # Strip the whitespace.
    new_text = ''
    for line in lines:
        new_text = new_text + line[min_white:] + '\n'

    # Return the new text.
    return new_text



class User_fn_class:
    def __init__(self):
        """Initialise the user function class, compiling the help string."""

        # Add the generic help string.
        self.__relax_help__ = self.__doc__ + "\n" + help.relax_class_help

        # Add a description to the help string.
        if hasattr(self, '__description__'):
            self.__relax_help__ = self.__relax_help__ + "\n\n" + _strip_lead(self.__description__)
