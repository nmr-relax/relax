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
"""Module for the main relax menu bar."""

# Python module imports.
import wx


def build_menu_item(menu, parent=None, id=None, text='', tooltip='', icon=None, fn=None):
    """Construct and return the menu sub-item.

    @param menu:        The menu object to place this entry in.
    @type menu:         wx.Menu instance
    @keyword id:        The element identification number.
    @type id:           int
    @keyword text:      The text for the menu entry.
    @type text:         None or str
    @keyword tooltip:   A tool tip.
    @type tooltip:      str
    @keyword icon:      The bitmap icon path.
    @type icon:         None or str
    @keyword fn:        The function to bind to the menu entry.
    @type fn:           class method
    @return:            The initialised wx.MenuItem() instance.
    @rtype:             wx.MenuItem() instance
    """

    # A new ID if necessary.
    if id == None:
        id = wx.NewId()

    # Initialise the GUI element.
    element = wx.MenuItem(menu, id, text, tooltip)

    # Set the icon.
    if icon:
        element.SetBitmap(wx.Bitmap(icon))

    # Bind the menu entry.
    if fn and parent:
        parent.Bind(wx.EVT_MENU, fn, id=id)

    # Return the element.
    return element
