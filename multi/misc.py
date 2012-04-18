###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""The non-public module for storing the API functions and classes of the multi-processor package.

This is for internal use only.  To access the multi-processor API, see the __init__ module.
"""

# Python module imports.
try:
    import importlib
except:
    importlib = None
import sys
import traceback, textwrap


def import_module(module_path):
    """Import the python module named by module_path.

    @param module_path: A module path in python dot separated format.  Note: this currently doesn't
                        support relative module paths as defined by pep328 and python 2.5.
    @type module_path:  str
    @return:            The module path as a list of module instances or None if the module path
                        cannot be found in the python path.
    @rtype:             list of class module instances or None
    """

    result = None

    # Import the module using the new Python 2.7 way.
    if importlib != None:
        module = importlib.import_module(module_path)

        # Return the module as a list.
        return [module]

    # Import the module using the old way.
    else:
        module = __import__(module_path, globals(), locals(), [])

        # Debugging.
        verbosity = Verbosity()
        if verbosity.level() > 2:
            print('loaded module %s' % module_path)

        #FIXME: needs more failure checking
        if module != None:
            result = [module]
            components = module_path.split('.')
            for component in components[1:]:
                module = getattr(module, component)
                result.append(module)
        return result


def raise_unimplemented(method):
    """Standard function for raising NotImplementedError for unimplemented abstract methods.

    @param method:              The method which should be abstract.
    @type method:               class method
    @raise NotImplementedError: A not implemented exception with the method name as a parameter.
    """

    msg = "Attempt to invoke unimplemented abstract method %s"
    raise NotImplementedError(msg % method.__name__)



class Capturing_exception(Exception):
    """A wrapper exception for an exception captured on a slave processor.

    The wrapper will remember the stack trace on the remote machine and when raised and caught has a
    string that includes the remote stack trace, which will be displayed along with the stack trace
    on the master.
    """

    def __init__(self, exc_info=None, rank='unknown', name='unknown'):
        """Initialise the wrapping exception.

        @todo:   Would it be easier to pass a processor here.

        @keyword exc_info:  Exception information as produced by sys.exc_info().
        @type exc_info:     tuple
        @keyword rank:      The rank of the processor on which the exception was raised.  The value
                            is always greater than 1.
        @type rank:         int
        @keyword name:      The name of the processor on which the exception was raised as returned
                            by processor.get_name().
        @type name:         str
        """

        Exception.__init__(self)
        self.rank = rank
        self.name = name
        if exc_info == None:
            (exception_type, exception_instance, exception_traceback) = sys.exc_info()
        else:
            (exception_type, exception_instance, exception_traceback) = exc_info

        # This is not an exception!
        if not exception_type:
            return

        #PY3K: this check can be removed once string based exceptions are no longer used
        if isinstance(exception_type, str):
                self.exception_name = exception_type + ' (legacy string exception)'
                self.exception_string = exception_type
        else:
            self.exception_name = exception_type.__name__
            self.exception_string = exception_instance.__str__()

        self.traceback = traceback.format_tb(exception_traceback)


    def __str__(self):
        """Get the string describing this exception.

        @return:    The string describing this exception.
        @rtype:     str
        """
        message = """

                     %s

                     %s

                     Nested Exception from sub processor
                     Rank: %s Name: %s
                     Exception type: %s
                     Message: %s

                     %s


                  """
        message = textwrap.dedent(message)
        result =  message % ('-'*120, ''.join(self.traceback), self.rank, self.name, self.exception_name, self.exception_string, '-'*120)
        return result



class Result(object):
    """A basic result object returned from a slave processor via return_object.

    This a very basic result and shouldn't be overridden unless you are also modifying the
    process_result method in all the processors in the framework (i.e. currently for implementors
    only). Most users should override Result_command.

    This result basically acts as storage for the following fields completed, memo_id,
    processor_rank.

    Results should only be created on slave processors.

    @see:   multi.processor.return_object.
    @see:   multi.processor.process_result.
    @see:   multi.processor.Result_command.
    """

    def __init__(self, processor, completed):
        """Initialise a result.

        This object is designed for subclassing and __init__ should be called via the super()
        function.

        @see:   multi.processor.Processor.

        @note:  The requirement for the user to know about completed will hopefully disappear with
                some slight of hand in the Slave_command and it may even disappear completely.

        @param processor:   Processor the processor instance we are running in.
        @type processor:    Processor instance
        @param completed:   A flag used in batching result returns to indicate that the sequence of
                            batched result commands has completed, the flag should be set by
                            slave_commands. The value should be the value passed to a Slave_commands
                            run method if it is the final result being returned otherwise it should
                            be False.
        @type completed:    bool
        """

        #TODO: assert on slave if processor_size > 1
        #TODO: check if a completed command will add a noticeable overhead (I doubt it will)
        self.completed = completed
        """A flag used in batching result returns to indicate that the sequence has completed.

        This is an optimisation to prevent the sending an extra batched result queue completion
        result being sent, it may be an over early optimisation."""
        self.memo_id = None
        """The memo_id of the Slave_command currently being processed on this processor.

        This value is set by the return_object method to the current Slave_commands memo_id."""
        self.rank = processor.rank()
        """The rank of the current processor, used in command scheduling on the master processor."""



# TODO: make this a result_command
class Result_string(Result):
    """A simple result from a slave containing a result.

    The processor will print this string via sys.stdout.

    @note:  This may become a result_command so as to simplify things in the end.
    """

    #TODO: correct order of parameters should be string, processor, completed
    def __init__(self, processor, string, completed):
        """Initialiser.

        @todo:  Check inherited parameters are documented.

        @param string:  A string to return the master processor for output to STDOUT (note the
                        master may split the string into components for STDOUT and STDERR depending
                        on the prefix string. This class is not really designed for subclassing.
        @type string:   str
        """

        super(Result_string, self).__init__(processor=processor, completed=completed)
        self.string = string



class Verbosity(object):
    """A special singleton structure for changing the verbosity level on the fly."""

    # Class variable for storing the class instance.
    instance = None

    def __new__(self, *args, **kargs): 
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            # Create a new object.
            self.instance = object.__new__(self, *args, **kargs)

            # Set the initial verbosity level to nothing.
            self._value = 0

        # Already initialised, so return the instance.
        return self.instance


    def level(self):
        """Return the current verbosity level.

        @return:            The current verbosity level.
        @rtype:             int
        """

        # Return the level.
        return self._value


    def set(self, value=0):
        """Set the verbosity level.

        @keyword value:     If given, then the verbosity level will be set.  A value of 0 suppresses all output.  A value of 1 causes the minimal amount of information to be printed.  A value of 2 will switch on a number of debugging print outs.  Values greater than 2 currently do nothing, though this might change in the future.
        @type value:        int
        """

        # Set the value if given.
        if value != None:
            self._value = value
