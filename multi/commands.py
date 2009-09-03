###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
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
"""Module containing classes for the multi-processor commands."""

# relax module imports.
from multi.processor import Result_string, Slave_command


class Exit_command(Slave_command):
    def __init__(self):
        # Execute the base class __init__() method.
        super(Exit_command, self).__init__()


    def run(self, processor, completed):
        processor.return_object(processor.NULL_RESULT)
        processor.do_quit = True


class Get_name_command(Slave_command):
    def __init__(self):
        # Execute the base class __init__() method.
        super(Exit_command, self).__init__()


    def run(self, processor, completed):
        msg = processor.get_name()
        result = Result_string(msg, completed)
        processor.return_object(result)


class Set_processor_property_command(Slave_command):
    def __init__(self, property_map):
        # Execute the base class __init__() method.
        super(Set_processor_property_command, self).__init__()

        self.property_map = property_map


    def run(self, processor, completed):
        for property, value in list(self.property_map.items()):
            try:
                setattr(processor, property, value)
                processor.return_object(processor.NULL_RESULT)
            except Exception, e:
                processor.return_object(e)
