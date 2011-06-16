###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module for the analysis selection wizard."""

# relax GUI module imports.
from gui.wizard import Wiz_panel, Wiz_window


class Analysis_wizard:
    """The analysis selection wizard."""

    def __init__(self):
        """Setup the analysis selection wizard."""


    def run(self):
        """Run through the analysis selection wizard, returning the results.

        @return:    The analysis type and data pipe name.
        @rtype:     str, str
        """

        # Create the wizard.
        self.wizard = Wizard()
        self.wizard.ShowModal()
        self.wizard.Destroy()

        # FIXME.
        analysis_type = 'r1'
        pipe_name = 'x'

        # Return the analysis type and pipe name.
        return analysis_type, pipe_name


class Data_pipe(Wiz_panel):
    pass


class New_analysis(Wiz_panel):
    pass


class Wizard(Wiz_window):
    def __init__(self):
        # Initialise the panels.
        self.panel1 = New_analysis()
        self.panel2 = Data_pipe()

