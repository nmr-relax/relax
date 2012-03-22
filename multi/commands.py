###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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

# multi module imports.
from multi.api import Result_string, Slave_command


class Exit_command(Slave_command):
    """Special command for terminating slave processors.

    This sets the processor's do_quit flag, terminating the Processor.run() loop for the slaves.
    """

    def run(self, processor, completed):
        """Set the slave processor's do_quit flag to terminate.

        @param processor:   The slave processor the command is running on.  Results from the command are returned via calls to processor.return_object.
        @type processor:    Processor instance
        @param completed:   The flag used in batching result returns to indicate that the sequence of batched result commands has completed.  This value should be returned via the last result object retuned by this method or methods it calls. All other Result_commands should be initialised with completed=False.  This is an optimisation to prevent the sending an extra batched result queue completion result command being sent, it may be an over early optimisation.
        @type completed:    bool
        """

        # First return no result.
        processor.return_object(processor.NULL_RESULT)

        # Then set the flag.
        processor.do_quit = True



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
