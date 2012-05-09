###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
# Copyright (C) 2007-2008 Sebastien Morin                                     #
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
"""Module containing the 'consistency_tests' user function data."""

# relax module imports.
from specific_fns.setup import consistency_tests_obj
from graphics import ANALYSIS_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('consistency_tests')
uf_class.title = "Class containing functions specific to consistency tests for datasets from different fields."
uf_class.menu_text = "&consistency_tests"
uf_class.gui_icon = "relax.consistency_testing"


# The consistency_tests.set_frq user function.
uf = uf_info.add_uf('consistency_tests.set_frq')
uf.title = "Select which relaxation data to use in the consistency tests by NMR spectrometer frequency."
uf.title_short = "Spectrometer selection."
uf.add_keyarg(
    name = "frq",
    py_type = "float",
    desc_short = "spectrometer frequency in Hz",
    desc = "The spectrometer frequency in Hz.  This must match the currently loaded data to the last decimal point."
)
uf.desc = """
This will select the relaxation data to use in the consistency tests corresponding to the given frequencies.
"""
uf.prompt_examples = """
relax> consistency_tests.set_frq(600.0 * 1e6)
relax> consistency_tests.set_frq(frq=600.0 * 1e6)
"""
uf.backend = consistency_tests_obj._set_frq
uf.menu_text = "&set_frq"
uf.wizard_size = (700, 400)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'consistency_testing_200x94.png'
