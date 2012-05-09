###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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
"""Module containing the Reduced Spectral Density Mapping 'jw_mapping' user function data."""

# relax module imports.
from generic_fns import frq
from graphics import WIZARD_IMAGE_PATH
from specific_fns.setup import jw_mapping_obj
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('jw_mapping')
uf_class.title = "Class containing functions specific to reduced spectral density mapping."
uf_class.menu_text = "&jw_mapping"


# The jw_mapping.set_frq user function.
uf = uf_info.add_uf('jw_mapping.set_frq')
uf.title = "Select which relaxation data to use in the J(w) mapping by NMR spectrometer frequency."
uf.title_short = "Spectrometer selection."
uf.add_keyarg(
    name = "frq",
    py_type = "float",
    desc_short = "spectrometer frequency in Hz",
    desc = "The spectrometer frequency in Hz.  This must match the currently loaded data to the last decimal point.  See the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file.",
    wiz_element_type = 'combo',
    wiz_combo_iter = frq.get_values,
    wiz_read_only = True,
)
uf.desc = """
This will select the relaxation data to use in the reduced spectral density mapping corresponding to the given frequency.  The data is selected by the spectrometer frequency in Hertz, which should be set to the exact value (see the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file).  Note thought that the R1, R2 and NOE are all expected to have the exact same frequency in the J(w) mapping analysis (to the last decimal point).
"""
uf.prompt_examples = """
relax> jw_mapping.set_frq(600.0 * 1e6)
relax> jw_mapping.set_frq(frq=600.0 * 1e6)
"""
uf.backend = jw_mapping_obj._set_frq
uf.menu_text = "&set_frq"
uf.wizard_height_desc = 350
uf.wizard_size = (800, 600)
