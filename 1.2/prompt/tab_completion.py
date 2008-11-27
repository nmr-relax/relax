###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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

import __builtin__
from re import match, split
from rlcompleter import get_class_members


class Tab_completion:
    def __init__(self, name_space={}, print_flag=0):
        """Function for tab completion."""

        self.name_space = name_space
        self.print_flag = print_flag


    def create_list(self):
        """Function to create the dictionary of options for tab completion."""

        self.list = self.name_space.keys()

        self.options = []
        for name in self.list:
            if match(self.input, name) and name != "__builtins__":
                self.options.append(name)


    def create_sublist(self):
        """Function to create the dictionary of options for tab completion."""

        # Split the input.
        list = split('\.', self.input)
        if len(list) == 0:
            return

        # Construct the module and get the corresponding object.
        module = list[0]
        for i in xrange(1, len(list)-1):
            module = module + '.' + list[i]
        object = eval(module, self.name_space)

        # Get the object attributes.
        self.list = dir(object)

        # If the object is a class, get all the class attributes as well.
        if hasattr(object, '__class__'):
            self.list.append('__class__')
            self.list = self.list + get_class_members(object.__class__)

        # Possible completions.
        self.options = []
        for name in self.list:
            if match(list[-1], name) and name != "__builtins__":
                self.options.append(module + '.' + name)

        if self.print_flag:
            print "List: " + `list`
            print "Module: " + `module`
            print "self.list: " + `self.list`
            print "self.options: " + `self.options`


    def finish(self, input, state):
        """Return the next possible completion for 'input'"""

        self.input = input
        self.state = state

        # Create a list of all possible options.
        # Find a list of options by matching the input with self.list
        if self.print_flag:
            print "\nInput: " + `self.input`
        if not "." in self.input:
            if self.print_flag:
                print "Creating list."
            self.create_list()
            if self.print_flag:
                print "\tOk."
        else:
            if self.print_flag:
                print "Creating sublist."
            self.create_sublist()
            if self.print_flag:
                print "\tOk."


        # Return the options if self.options[state] exists, or return None otherwise.
        if self.print_flag:
            print "Returning options."
        if self.state < len(self.options):
            return self.options[self.state]
        else:
            return None
