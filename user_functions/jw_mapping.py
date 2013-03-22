###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
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
"""The jw_mapping user function definitions for Reduced Spectral Density Mapping."""

# relax module imports.
from generic_fns import frq
from graphics import ANALYSIS_IMAGE_PATH
from specific_analyses.setup import jw_mapping_obj
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('jw_mapping')
uf_class.title = "Class containing functions specific to reduced spectral density mapping."
uf_class.menu_text = "&jw_mapping"
uf_class.gui_icon = "relax.jw_mapping"


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
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will select the relaxation data to use in the reduced spectral density mapping corresponding to the given frequency.  The data is selected by the spectrometer frequency in Hertz, which should be set to the exact value (see the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file).  Note thought that the R1, R2 and NOE are all expected to have the exact same frequency in the J(w) mapping analysis (to the last decimal point).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_prompt("relax> jw_mapping.set_frq(600.0 * 1e6)")
uf.desc[-1].add_prompt("relax> jw_mapping.set_frq(frq=600.0 * 1e6)")
uf.backend = jw_mapping_obj._set_frq
uf.menu_text = "&set_frq"
uf.gui_icon = "relax.frq"
uf.wizard_height_desc = 350
uf.wizard_size = (700, 500)
