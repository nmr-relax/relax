###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

from re import match
from types import DictType


class Diffusion(DictType):
    def __init__(self):
        """Class containing all the diffusion tensor data."""


    def __repr__(self):
        text = "Diffusion tensor data:\n"
        if len(self) == 0:
            text = text + "  {}\n"
        else:
            i = 0
            for key in self.keys():
                if i == 0:
                    text = text + "  { "
                else:
                    text = text + "  , "
                text = text + "Diffusion tensor key " + `key` + ":\n"
                for name in dir(self[key]):
                    if match("^__", name):
                        continue
                    text = text + "    " + name + ", " + `type(getattr(self[key], name))` + "\n"
                i = i + 1
            text = text + "  }\n"

        return text


    def add_item(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = Element()


class Element:
    def __init__(self):
        """Empty data container."""


    def __repr__(self):
        text = "Diffusion tensor data:\n"
        for name in dir(self):
            if match("^__", name):
                continue
            text = text + "    " + name + ", " + `type(getattr(self, name))` + "\n"
        return text
