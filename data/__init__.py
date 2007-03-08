###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2007 Edward d'Auvergne                        #
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

# Python module imports.
from math import pi
from re import match, search
from types import DictType, ListType

# relax module imports.
from data_classes import Element, Residue, SpecificData
from diff_tensor import DiffTensorData


__all__ = [ 'data_classes',
            'diff_tensor',
            'diff_tensor_auto_objects',
            'main' ]

# Global data.
##############

class Data(object):
    __instance = None

    def __init__(self):
        """Class containing all the program data."""

        # Fundamental constants.
        #self.h = 6.6260755e-34    # Old low precision value.
        self.h = 6.62606876e-34
        self.h_bar = self.h / ( 2.0*pi )
        self.mu0 = 4.0 * pi * 1e-7

        # PDB data.
        self.pdb = SpecificData()

        # Diffusion data.
        self.diff = DiffTensorData()

        # The residue specific data.
        self.res = Residue()

        # The name of the runs.
        self.run_names = []

        # The type of the runs.
        self.run_types = []

        # Hybrid models.
        self.hybrid_runs = {}

        # Global minimisation statistics.
        self.chi2 = {}
        self.iter = {}
        self.f_count = {}
        self.g_count = {}
        self.h_count = {}
        self.warning = {}


    def __new__(self, *args, **kargs): 
        """Method for implementing the singleton design pattern.

        If no other class instance currently exists, create a new instance of this class.  Otherwise
        return the class instance.  See http://en.wikipedia.org/wiki/Singleton_pattern for a
        description of this design pattern.
        """

        # Create a new instance if none exists.
        if self.__instance is None:
            self.__instance = object.__new__(self, *args, **kargs)

        # Return the class instance.
        return self.__instance


    def __repr__(self):
        text = "The data class containing all permanent program data.\n"
        text = text + "The class contains the following objects:\n"
        for name in dir(self):
            if match("^_", name):
                continue
            text = text + "  " + name + ", " + `type(getattr(self, name))` + "\n"
        return text


    def __reset__(self):
        """"""

        # Get the keys of self.__dict__.
        keys = self.__dict__.keys()

        # Loop over the keys and delete the corresponding object.
        for key in keys:
            # Delete the object.
            del self.__dict__[key]

        # Rerun the __init__() method.
        self.__init__()
