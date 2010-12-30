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

# Install path.
if not hasattr(__main__, 'install_path'):
    __main__.install_path = sys.path[0]

# GUI image and icon paths.
OXY_ICON_PATH = __main__.install_path + sep + 'graphics' + sep + 'oxygen_icons' + sep
IMAGE_PATH = __main__.install_path + sep + 'gui_bieri' + sep + 'images' + sep
ICON_RELAX_PATH = __main__.install_path + sep + 'graphics' + sep + 'relax_icons' + sep
WIZARD_IMAGE_PATH = __main__.install_path + sep + 'graphics' + sep + 'wizards' + sep



class I16x16:
    """The 16x16 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # relax icons.
        path = ICON_RELAX_PATH + '16x16' + sep
        self.about_relax =          IMAGE_PATH + 'relax_16x16.png'
        self.about_relaxgui =       IMAGE_PATH + 'relax_16x16.png'
        self.molecule =             path + 'molecule.png'
        self.molecule_unfolded =    path + 'molecule_unfolded.png'
        self.pipe =                 path + 'pipe.png'
        self.residue =              path + 'residue.png'
        self.sequence =             path + 'sequence.png'
        self.spin =                 path + 'spin.png'

        # Oxygen icons.
        path = OXY_ICON_PATH + '16x16' + sep
        self.about =                path + 'actions'    + sep + 'help-about.png'
        self.add =                  path + 'actions'    + sep + 'list-add-relax-blue.png'
        self.cancel =               path + 'actions'    + sep + 'dialog-cancel.png'
        self.contact =              path + 'actions'    + sep + 'mail-mark-unread-new.png'
        self.controller =           path + 'apps'       + sep + 'preferences-system-performance.png'
        self.edit_delete =          path + 'actions'    + sep + 'edit-delete.png'
        self.exit =                 path + 'actions'    + sep + 'system-shutdown.png'
        self.load =                 path + 'actions'    + sep + 'arrow-right.png'
        self.manual =               path + 'mimetypes'  + sep + 'application-pdf.png'
        self.new =                  path + 'actions'    + sep + 'document-new.png'
        self.open =                 path + 'actions'    + sep + 'document-open.png'
        self.pipe_switch =          path + 'actions'    + sep + 'system-switch-user.png'
        self.relax_prompt =         path + 'mimetypes'  + sep + 'application-x-executable-script.png'
        self.remove =               path + 'actions'    + sep + 'list-remove.png'
        self.save =                 path + 'actions'    + sep + 'document-save.png'
        self.save_as =              path + 'actions'    + sep + 'document-save-as.png'
        self.settings =             path + 'actions'    + sep + 'document-properties.png'
        self.settings_global =      path + 'categories' + sep + 'preferences-system.png'
        self.settings_reset =       path + 'actions'    + sep + 'edit-delete.png'
        self.ref =                  path + 'actions'    + sep + 'flag-blue.png'
        self.uf_script =            path + 'mimetypes'  + sep + 'application-x-desktop.png'
        self.view_refresh =         path + 'actions'    + sep + 'view-refresh.png'



class I22x22:
    """The 22x22 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # Oxygen icons.
        path = OXY_ICON_PATH + '22x22' + sep
        self.about =                path + 'actions' + sep + 'help-about.png'
        self.apply =                path + 'actions' + sep + 'dialog-ok-apply.png'
        self.cancel =               path + 'actions' + sep + 'dialog-cancel.png'
        self.close =                path + 'actions' + sep + 'dialog-close.png'
        self.ok =                   path + 'actions' + sep + 'dialog-ok.png'

        # relax icons.
        path = ICON_RELAX_PATH + '22x22' + sep
        self.molecule =             path + 'molecule.png'
        self.molecule_unfolded =    path + 'molecule_unfolded.png'
        self.pipe =                 path + 'pipe.png'
        self.residue =              path + 'residue.png'
        self.sequence =             path + 'sequence.png'
        self.spin =                 path + 'spin.png'
        self.view_refresh =         path + 'actions'    + sep + 'view-refresh.png'



class I32x32:
    """The 32x32 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # Oxygen icons.
        path = OXY_ICON_PATH + '32x32' + sep
        self.about =        path + 'actions' + sep + 'help-about.png'
        self.apply =        path + 'actions' + sep + 'dialog-ok-apply.png'
        self.cancel =       path + 'actions' + sep + 'dialog-cancel.png'
        self.close =        path + 'actions' + sep + 'dialog-close.png'
        self.ok =           path + 'actions' + sep + 'dialog-ok.png'
        self.view_refresh = path + 'actions' + sep + 'view-refresh.png'



class I48x48:
    """The 48x48 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # Oxygen icons.
        path = OXY_ICON_PATH + '48x48' + sep
        self.about =        path + 'actions' + sep + 'help-about.png'
        self.add =          path + 'actions' + sep + 'list-add-relax-blue.png'
        self.backwards =    path + 'actions' + sep + 'go-previous-view.png'
        self.cancel =       path + 'actions' + sep + 'dialog-cancel.png'
        self.forwards =     path + 'actions' + sep + 'go-next-view.png'
        self.remove =       path + 'actions' + sep + 'list-remove.png'
        self.view_refresh = path + 'actions' + sep + 'view-refresh.png'

        # relax icons.
        path = ICON_RELAX_PATH + '48x48' + sep
        self.pipe =                 path + 'pipe.png'
        self.sequence =             path + 'sequence.png'


# Set up all icon classes.
icon_16x16 = I16x16()
icon_22x22 = I22x22()
icon_32x32 = I32x32()
icon_48x48 = I48x48()
