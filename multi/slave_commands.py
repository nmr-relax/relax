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
"""Module containing command objects sent from the master to the slaves."""

# Python module imports.
import sys

# multi module imports.
from multi.misc import raise_unimplemented, Result, Result_string


class Slave_command(object):
    """A command to executed remotely on the slave processor - designed to be subclassed by users.

    The command should be queued with the command queue using the add_to_queue command of the master
    and B{must} return at least one Result_command even if it is a processor.NULL_RESULT. Results
    are returned from the Slave_command to the master processor using the return_object method of
    the processor passed to the command. Any exceptions raised will be caught wrapped and returned
    to the master processor by the slave processor.

    @note:  Good examples of subclassing a slave command include multi.commands.MF_minimise_command
            and multi.commands.Get_name_command.
    @see:   multi.commands.MF_minimise_command.
    @see:   multi.commands.Get_name_command.
    """

    def __init__(self):
        self.memo_id = None


    def run(self, processor, completed):
        """Run the slave command on the slave processor
        
        This is a base method which must be overridden.

        The run command B{must} return at least one Result_command even if it is a processor.NULL_RESULT.  Results are returned from the Slave_command to the master processor using the return_object method of the processor passed to the command. Any exceptions raised will be caught wrapped and returned to the master processor by the slave processor.


        @param processor:   The slave processor the command is running on.  Results from the command are returned via calls to processor.return_object.
        @type processor:    Processor instance
        @param completed:   The flag used in batching result returns to indicate that the sequence of batched result commands has completed. This value should be returned via the last result object retuned by this method or methods it calls. All other Result_commands should be initialised with completed=False. This is an optimisation to prevent the sending an extra batched result queue completion result command being sent, it may be an over early optimisation.
        @type completed:    bool
        """

        # This must be overridden!
        raise_unimplemented(self.run)


    def set_memo_id(self, memo):
        """Called by the master processor to remember this Slave_commands memo.

        @param memo:    The memo to remember, memos are remembered by getting the memo_id of the
                        memo.
        """

        if memo != None:
            self.memo_id = memo.memo_id()
        else:
            self.memo_id = None



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



class Slave_storage_command(Slave_command):
    """Special command for sending data for storage on the slaves."""

    def __init__(self):
        """Set up the command."""

        # Initialise the base class.
        super(Slave_command, self).__init__()

        # Initialise variables for holding data in transit.
        self.names = []
        self.values = []


    def add(self, name, value):
        """Pump in data to be held and transfered to the slave by the command.

        @keyword name:  The name of the data structure to store.
        @type name:     str
        @keyword value: The data structure.
        @type value:    anything
        """

        # Store the data.
        self.names.append(name)
        self.values.append(value)


    def clear(self):
        """Remove all data from the slave."""

        # Reinitialise the structures.
        self.names = []
        self.values = []


    def run(self, processor, completed):
        """Set the slave processor's do_quit flag to terminate.

        @param processor:   The slave processor the command is running on.  Results from the command are returned via calls to processor.return_object.
        @type processor:    Processor instance
        @param completed:   The flag used in batching result returns to indicate that the sequence of batched result commands has completed.  This value should be returned via the last result object retuned by this method or methods it calls. All other Result_commands should be initialised with completed=False.  This is an optimisation to prevent the sending an extra batched result queue completion result command being sent, it may be an over early optimisation.
        @type completed:    bool
        """

        # First return no result.
        processor.return_object(processor.NULL_RESULT)

        # Loop over and store the data.
        for i in range(len(self.names)):
            setattr(processor.data_store, self.names[i], self.values[i])

        # Clear the data.
        self.clear()
