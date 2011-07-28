###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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
"""Collection of all the image and icon paths.

This module allows for easy replacement of images and icons throughout the GUI.
"""

# Python module imports.
from os import sep
import sys

# relax module imports.
from status import Status; status = Status()


# GUI image and icon paths.
ANALYSIS_IMAGE_PATH = status.install_path + sep + 'graphics' + sep + 'analyses' + sep
OXY_ICON_PATH = status.install_path + sep + 'graphics' + sep + 'oxygen_icons' + sep
IMAGE_PATH = status.install_path + sep + 'gui' + sep + 'images' + sep
ICON_RELAX_PATH = status.install_path + sep + 'graphics' + sep + 'relax_icons' + sep
WIZARD_IMAGE_PATH = status.install_path + sep + 'graphics' + sep + 'wizards' + sep



class I16x16:
    """The 16x16 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # relax icons.
        path = ICON_RELAX_PATH + '16x16' + sep
        self.about_relax =              IMAGE_PATH + 'relax_16x16.png'
        self.about_relaxgui =           IMAGE_PATH + 'relax_16x16.png'
        self.molecule =                 path + 'molecule.png'
        self.molecule_grey =            path + 'molecule_grey.png'
        self.molecule_unfolded =        path + 'molecule_unfolded.png'
        self.molecule_unfolded_grey =   path + 'molecule_unfolded_grey.png'
        self.pipe =                     path + 'pipe.png'
        self.pipe_hybrid =              path + 'pipe_hybrid.png'
        self.relax_data =               path + 'fid.png'
        self.residue =                  path + 'residue.png'
        self.residue_grey =             path + 'residue_grey.png'
        self.sequence =                 path + 'sequence.png'
        self.spin =                     path + 'spin.png'
        self.spin_grey =                path + 'spin_grey.png'
        self.structure =                path + 'structure.png'
        self.value =                    path + 'value.png'

        # Oxygen icons.
        path = OXY_ICON_PATH + '16x16' + sep
        self.about =                path + 'actions'    + sep + 'help-about.png'
        self.add =                  path + 'actions'    + sep + 'list-add-relax-blue.png'
        self.cancel =               path + 'actions'    + sep + 'dialog-cancel.png'
        self.contact =              path + 'actions'    + sep + 'mail-mark-unread-new.png'
        self.controller =           path + 'apps'       + sep + 'preferences-system-performance.png'
        self.copy =                 path + 'actions'    + sep + 'list-add.png'
        self.dialog_close =         path + 'actions'    + sep + 'dialog-close.png'
        self.dialog_warning =       path + 'status'     + sep + 'dialog-warning.png'
        self.document_properties =  path + 'actions'    + sep + 'document-properties.png'
        self.document_close =       path + 'actions'    + sep + 'document-close.png'
        self.edit_delete =          path + 'actions'    + sep + 'edit-delete.png'
        self.exit =                 path + 'actions'    + sep + 'system-shutdown.png'
        self.flag_blue =            path + 'actions'    + sep + 'flag-blue.png'
        self.flag_red =             path + 'actions'    + sep + 'flag-red.png'
        self.go_bottom =            path + 'actions'    + sep + 'go-bottom.png'
        self.list_remove =          path + 'actions'    + sep + 'list-remove.png'
        self.load =                 path + 'actions'    + sep + 'arrow-right.png'
        self.manual =               path + 'mimetypes'  + sep + 'application-pdf.png'
        self.new =                  path + 'actions'    + sep + 'document-new.png'
        self.open =                 path + 'actions'    + sep + 'document-open.png'
        self.open_folder =          path + 'actions'    + sep + 'document-open-folder.png'
        self.pipe_switch =          path + 'actions'    + sep + 'system-switch-user.png'
        self.relax_prompt =         path + 'mimetypes'  + sep + 'application-x-executable-script.png'
        self.remove =               path + 'actions'    + sep + 'list-remove.png'
        self.save =                 path + 'actions'    + sep + 'document-save.png'
        self.save_as =              path + 'actions'    + sep + 'document-save-as.png'
        self.settings_global =      path + 'categories' + sep + 'preferences-system.png'
        self.settings_reset =       path + 'actions'    + sep + 'edit-delete.png'
        self.skip =                 path + 'actions'    + sep + 'arrow-right-double-relax-blue.png'
        self.system_run =           path + 'actions'    + sep + 'system-run.png'
        self.ref =                  path + 'actions'    + sep + 'flag-blue.png'
        self.uf_script =            path + 'mimetypes'  + sep + 'application-x-desktop.png'
        self.view_refresh =         path + 'actions'    + sep + 'view-refresh.png'
        self.view_statistics =      path + 'actions'    + sep + 'view-statistics.png'
        self.user_busy =            path + 'status'     + sep + 'user-busy.png'



class I22x22:
    """The 22x22 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # Oxygen icons.
        path = OXY_ICON_PATH + '22x22' + sep
        self.about =                path + 'actions'    + sep + 'help-about.png'
        self.add =                  path + 'actions'    + sep + 'list-add-relax-blue.png'
        self.apply =                path + 'actions'    + sep + 'dialog-ok-apply.png'
        self.cancel =               path + 'actions'    + sep + 'dialog-cancel.png'
        self.close =                path + 'actions'    + sep + 'dialog-close.png'
        self.copy =                 path + 'actions'    + sep + 'list-add.png'
        self.dialog_close =         path + 'actions'    + sep + 'dialog-close.png'
        self.dialog_warning =       path + 'status'     + sep + 'dialog-warning.png'
        self.document_close =       path + 'actions'    + sep + 'document-close.png'
        self.document_properties =  path + 'actions'    + sep + 'document-properties.png'
        self.go_bottom =            path + 'actions'    + sep + 'go-bottom.png'
        self.go_previous_view =     path + 'actions'    + sep + 'go-previous-view.png'
        self.go_next_view =         path + 'actions'    + sep + 'go-next-view.png'
        self.list_remove =          path + 'actions'    + sep + 'list-remove.png'
        self.new =                  path + 'actions'    + sep + 'document-new.png'
        self.ok =                   path + 'actions'    + sep + 'dialog-ok.png'
        self.open_folder =          path + 'actions'    + sep + 'document-open-folder.png'
        self.pipe_switch =          path + 'actions'    + sep + 'system-switch-user.png'
        self.save =                 path + 'actions'    + sep + 'document-save.png'
        self.skip =                 path + 'actions'    + sep + 'arrow-right-double-relax-blue.png'
        self.system_run =           path + 'actions'    + sep + 'system-run.png'
        self.view_refresh =         path + 'actions'    + sep + 'view-refresh.png'
        self.view_statistics =      path + 'actions'    + sep + 'view-statistics.png'
        self.user_busy =            path + 'status'     + sep + 'user-busy.png'

        # relax icons.
        path = ICON_RELAX_PATH + '22x22' + sep
        self.molecule =                 path + 'molecule.png'
        self.molecule_grey =            path + 'molecule_grey.png'
        self.molecule_unfolded =        path + 'molecule_unfolded.png'
        self.molecule_unfolded_grey =   path + 'molecule_unfolded_grey.png'
        self.pipe =                     path + 'pipe.png'
        self.pipe_hybrid =              path + 'pipe_hybrid.png'
        self.relax_data =               path + 'fid.png'
        self.residue =                  path + 'residue.png'
        self.residue_grey =             path + 'residue_grey.png'
        self.sequence =                 path + 'sequence.png'
        self.spin =                     path + 'spin.png'
        self.spin_grey =                path + 'spin_grey.png'
        self.structure =                path + 'structure.png'
        self.value =                    path + 'value.png'



class I32x32:
    """The 32x32 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # Oxygen icons.
        path = OXY_ICON_PATH + '32x32' + sep
        self.about =                path + 'actions'    + sep + 'help-about.png'
        self.add =                  path + 'actions'    + sep + 'list-add-relax-blue.png'
        self.apply =                path + 'actions'    + sep + 'dialog-ok-apply.png'
        self.cancel =               path + 'actions'    + sep + 'dialog-cancel.png'
        self.close =                path + 'actions'    + sep + 'dialog-close.png'
        self.dialog_close =         path + 'actions'    + sep + 'dialog-close.png'
        self.dialog_warning =       path + 'status'     + sep + 'dialog-warning.png'
        self.document_close =       path + 'actions'    + sep + 'document-close.png'
        self.document_properties =  path + 'actions'    + sep + 'document-properties.png'
        self.copy =                 path + 'actions'    + sep + 'list-add.png'
        self.go_bottom =            path + 'actions'    + sep + 'go-bottom.png'
        self.list_remove =          path + 'actions'    + sep + 'list-remove.png'
        self.new =                  path + 'actions'    + sep + 'document-new.png'
        self.ok =                   path + 'actions'    + sep + 'dialog-ok.png'
        self.open_folder =          path + 'actions'    + sep + 'document-open-folder.png'
        self.pipe_switch =          path + 'actions'    + sep + 'system-switch-user.png'
        self.save =                 path + 'actions'    + sep + 'document-save.png'
        self.skip =                 path + 'actions'    + sep + 'arrow-right-double-relax-blue.png'
        self.system_run =           path + 'actions'    + sep + 'system-run.png'
        self.view_refresh =         path + 'actions'    + sep + 'view-refresh.png'
        self.view_statistics =      path + 'actions'    + sep + 'view-statistics.png'
        self.user_busy =            path + 'status'     + sep + 'user-busy.png'

        # relax icons.
        self.pipe_hybrid =              path + 'pipe_hybrid.png'
        self.structure =                path + 'structure.png'


class I48x48:
    """The 48x48 pixel icons."""

    def __init__(self):
        """Initialise all paths."""

        # Oxygen icons.
        path = OXY_ICON_PATH + '48x48' + sep
        self.about =                path + 'actions'    + sep + 'help-about.png'
        self.add =                  path + 'actions'    + sep + 'list-add-relax-blue.png'
        self.backwards =            path + 'actions'    + sep + 'go-previous-view.png'
        self.cancel =               path + 'actions'    + sep + 'dialog-cancel.png'
        self.copy =                 path + 'actions'    + sep + 'list-add.png'
        self.dialog_close =         path + 'actions'    + sep + 'dialog-close.png'
        self.dialog_warning =       path + 'status'     + sep + 'dialog-warning.png'
        self.document_close =       path + 'actions'    + sep + 'document-close.png'
        self.document_properties =  path + 'actions'    + sep + 'document-properties.png'
        self.forwards =             path + 'actions'    + sep + 'go-next-view.png'
        self.go_bottom =            path + 'actions'    + sep + 'go-bottom.png'
        self.list_remove =          path + 'actions'    + sep + 'list-remove.png'
        self.new =                  path + 'actions'    + sep + 'document-new.png'
        self.open_folder =          path + 'actions'    + sep + 'document-open-folder.png'
        self.pipe_switch =          path + 'actions'    + sep + 'system-switch-user.png'
        self.remove =               path + 'actions'    + sep + 'list-remove.png'
        self.save =                 path + 'actions'    + sep + 'document-save.png'
        self.skip =                 path + 'actions'    + sep + 'arrow-right-double-relax-blue.png'
        self.system_run =           path + 'actions'    + sep + 'system-run.png'
        self.view_refresh =         path + 'actions'    + sep + 'view-refresh.png'
        self.view_statistics =      path + 'actions'    + sep + 'view-statistics.png'
        self.user_busy =            path + 'status'     + sep + 'user-busy.png'

        # relax icons.
        path = ICON_RELAX_PATH + '48x48' + sep
        self.pipe =                 path + 'pipe.png'
        self.pipe_hybrid =          path + 'pipe_hybrid.png'
        self.relax_data =           path + 'fid.png'
        self.sequence =             path + 'sequence.png'
        self.structure =            path + 'structure.png'
        self.value =                path + 'value.png'


# Set up all icon classes.
icon_16x16 = I16x16()
icon_22x22 = I22x22()
icon_32x32 = I32x32()
icon_48x48 = I48x48()
