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

# file dialog script

# Python module imports.
from os import chdir, getcwd
import wx



def multi_openfile(msg, directory, filetype, default): # open multiple file

    #Input format:
    #msg:              message to display
    #directory:        directory, where dialog opens as default
    #filetype:         proposed file to open
    #default:          list of supported files, indicated as "(Label)|os command|...

    #command:
    #openfile('select file to open', '/usr', 'save.relaxGUI', 'relaxGUI files (*.relaxGUI)|*.relaxGUI|all files (*.*)|*.*')
    #suggests to open /usr/save.relaxGUI, supported files to open are: *.relaxGUI, *.*

    newfile = []
    dialog = wx.FileDialog ( None, message = msg, style = wx.OPEN | wx.FD_MULTIPLE, defaultDir= directory, defaultFile = filetype, wildcard = default)

    if dialog.ShowModal() == wx.ID_OK:
        return newfile


def opendir(msg, default): # select directory, msg is message to display, default is starting directory
    newdir = None
    dlg = wx.DirDialog(None, message = msg, style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON, defaultPath = default)
    if dlg.ShowModal() == wx.ID_OK:
        newdir = dlg.GetPath()
        return newdir


def openfile(msg, filetype, default):
    """Open a file.

    For example to open save.relaxGUI, where the supported files to open are: *.relaxGUI, *.*:
        openfile('select file to open', 'save.relaxGUI', 'relaxGUI files (*.relaxGUI)|*.relaxGUI|all files (*.*)|*.*')


    @param msg:         The message to display.
    @type msg:          str
    @param filetype:    The file to default selection to.
    @type filetype:     str
    @param default:     A list of supported files, indicated as "(Label)|os command|...
    @type default:      str
    """

    # Open the dialog.
    dialog = wx.FileDialog(None, message=msg, style=wx.OPEN, defaultDir=getcwd(), defaultFile=filetype, wildcard=default)

    # A file was selected.
    if dialog.ShowModal() == wx.ID_OK:
        # Change the current working directory.
        chdir(dialog.GetDirectory())

        # Return the full file path.
        return dialog.GetPath()


def savefile(msg, directory, filetype, default): # save a file

    #Input format:
    #msg:              message to display
    #directory:        directory, where dialog opens as default
    #filetype:         proposed file to save
    #default:          list of supported files, indicated as "(Label)|os command|...

    #command:
    #savefile('select file to save', '/usr', 'save.relaxGUI', 'relaxGUI files (*.relaxGUI)|*.relaxGUI|all files (*.*)|*.*')
    #suggests to save /usr/save.relaxGUI, supported files to save are: *.relaxGUI, *.*

    newfile = None
    dialog = wx.FileDialog ( None, message = msg, style = wx.SAVE, defaultDir= directory, defaultFile = filetype, wildcard = default)
    if dialog.ShowModal() == wx.ID_OK:
        newfile = dialog.GetPath()
        return newfile
