###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Collection of all the image and icon paths.

This module allows for easy replacement of images and icons throughout the GUI.
"""

# Python module imports.
import __main__
from os import sep
import sys


# GUI image and icon paths.
ICON_PATH = __main__.install_path +sep+'gui_bieri'+sep+'oxygen_icons'+sep
IMAGE_PATH = __main__.install_path +sep+'gui_bieri'+sep+'images'+sep
ICON_RELAX_PATH = __main__.install_path +sep+'graphics'+sep+'relax_icons'+sep

# 16x16 icons.
ABOUT_RELAX_ICON = IMAGE_PATH + 'relax_16x16.png'
ABOUT_RELAXGUI_ICON = IMAGE_PATH + 'relax_16x16.png'
ADD_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'list-add-relax-blue.png'
CANCEL_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'dialog-cancel.png'
CONTACT_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'mail-mark-unread-new.png'
CONTROLLER_ICON = ICON_PATH + '16x16'+sep+'apps'+sep+'preferences-system-performance.png'
EXIT_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'system-shutdown.png'
LOAD_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'arrow-right.png'
MANUAL_ICON = ICON_PATH + '16x16'+sep+'mimetypes'+sep+'application-pdf.png'
NEW_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'document-new.png'
OPEN_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'document-open.png'
RELAX_PROMPT_ICON = ICON_PATH + '16x16'+sep+'mimetypes'+sep+'application-x-executable-script.png'
REMOVE_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'list-remove.png'
SAVE_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'document-save.png'
SAVE_AS_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'document-save-as.png'
SETTINGS_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'document-properties.png'
SETTINGS_GLOBAL_ICON = ICON_PATH + '16x16'+sep+'categories'+sep+'preferences-system.png'
SETTINGS_RESET_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'edit-delete.png'
REF_ICON = ICON_PATH + '16x16'+sep+'actions'+sep+'flag-blue.png'
UF_SCRIPT_ICON = ICON_PATH + '16x16'+sep+'mimetypes'+sep+'application-x-desktop.png'

# 48x48 icons.
#ADD_ICON = ICON_PATH + '48x48'+sep+'actions'+sep+'list-add-relax-blue.png'
BACKWARDS_ICON = ICON_PATH + '48x48'+sep+'actions'+sep+'go-previous-view.png'
#CANCEL_ICON = ICON_PATH + '48x48'+sep+'actions'+sep+'dialog-cancel.png'
FORWARDS_ICON = ICON_PATH + '48x48'+sep+'actions'+sep+'go-next-view.png'
#REMOVE_ICON = ICON_PATH + '48x48'+sep+'actions'+sep+'list-remove.png'

MOLECULE_ICON = ICON_RELAX_PATH + '22x22'+sep+'molecule.png'
RESIDUE_ICON = ICON_RELAX_PATH + '22x22'+sep+'residue.png'
