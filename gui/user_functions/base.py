###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
"""Base class module for the user function GUI elements."""

# relax module imports.
from prompt.base_class import _strip_lead

# relax GUI imports.
from gui.wizard import Wiz_page


class UF_base:
    """User function GUI element base class."""

    def __init__(self, gui, interpreter):
        """Set up the user function class."""

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # Specific set up.
        self.setup()


    def setup(self):
        """Dummy method to be overwritten."""


class UF_page(Wiz_page):
    """User function specific pages for the wizards."""

    # The path to the user function.
    uf_path = None

    def __init__(self, parent, gui, interpreter):
        """Set up the window.

        @param parent:      The parent class containing the GUI and interpreter objects.
        @type parent:       class instance
        @param gui:         The GUI base object.
        @type gui:          wx.Frame instance
        @param interpreter: The relax interpreter.
        @type interpreter:  prompt.interpreter.Interpreter instance
        """

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # User function path is supplied, so set the main text to the docstring.
        if self.uf_path != None:
            # Get the user function class (or function).
            uf_class = getattr(self.interpreter, self.uf_path[0])

            # Get the user function.
            if len(self.uf_path) == 1:
                uf = uf_class
            else:
                uf = getattr(uf_class, self.uf_path[1])

            # Set the user function title.
            title = uf._doc_title

            # Set the main text to the description doc.
            if hasattr(uf, '_doc_desc'):
                self.main_text = title + '\n\n' + self._format_text(uf._doc_desc)

                # Remove trailing newlines.
                if self.main_text[-1] == '\n':
                    self.main_text = self.main_text[:-1]

        # Execute the base class method.
        super(UF_page, self).__init__(parent)


    def _format_text(self, text):
        """Format the text by stripping whitespace.

        @param text:    The text to strip.
        @type text:     str
        @return:        The stripped text.
        @rtype:         str
        """

        # First strip whitespace.
        stripped_text = _strip_lead(text)

        # Remove the first characters if newlines.
        while 1:
            if stripped_text[0] == "\n":
                stripped_text = stripped_text[1:]
            else:
                break

        # Remove the last character if a newline.
        while 1:
            if stripped_text[-1] == "\n":
                stripped_text = stripped_text[:-1]
            else:
                break

        # Return the text.
        return stripped_text


    def on_completion(self):
        """Notify that the user function has completed."""

        # Notify.
        self.gui.user_functions.notify_observers()
