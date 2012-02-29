###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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


__all__ = ['commands',
           'mpi4py_processor',
           'multi_processor_base',
           'processor_io',
           'processor',
           'uni_processor']

__doc__ = \
"""Package for multi-processor code execution."""

# Python module imports.
import sys


def _import_module(module_path, verbose=False):
    '''Import the python module named by module_path.

    @param module_path: A module path in python dot separated format.  Note: this currently doesn't
                        support relative module paths as defined by pep328 and python 2.5.
    @type module_path:  str
    @keyword verbose:   Whether to report successes and failures for debugging.
    @type verbose:      bool
    @return:            The module path as a list of module instances or None if the module path
                        cannot be found in the python path.
    @rtype:             list of class module instances or None
    '''

    result = None

    # Import the module.
    module = __import__(module_path, globals(), locals(), [])
    if verbose:
        print('loaded module %s' % module_path)

    #FIXME: needs more failure checking
    if module != None:
        result = [module]
        components = module_path.split('.')
        for component in components[1:]:
            module = getattr(module, component)
            result.append(module)
    return result


#FIXME error checking for if module required not found.
#FIXME module loading code needs to be in a util module.
#FIXME: remove parameters that are not required to load the module (processor_size).
def load_multiprocessor(processor_name, callback, processor_size):
    '''Load a multi processor given its name.

    Dynamically load a multi processor, the current algorithm is to search in module multi for a
    module called <processor_name>.<Processor_name> (note capitalisation).


    @todo:  This algorithm needs to be improved to allow users to load processors without altering
            the relax source code.

    @todo:  Remove non-essential parameters.

    @param processor_name:  Name of the processor module/class to load.
    @type processor_name:   str
    @return:                A loaded processor object or None to indicate failure.
    @rtype:                 multi.processor.Processor instance
    '''

    # Check that the processor type is supported.
    if processor_name not in ['uni', 'mpi4py']:
        sys.stderr.write("The processor type '%s' is not supported.\n" % processor_name)
        sys.exit()

    # The Processor details.
    processor_name = processor_name + '_processor'
    class_name = processor_name[0].upper() + processor_name[1:]
    module_path = '.'.join(('multi', processor_name))

    # Load the module containing the specific processor.
    modules = _import_module(module_path)

    # Access the class from within the module.
    if hasattr(modules[-1], class_name):
        clazz = getattr(modules[-1], class_name)
    else:
        raise Exception("can't load class %s from module %s" % (class_name, module_path))

    # Instantiate the Processor.
    object = clazz(callback=callback, processor_size=processor_size)

    # Load the Processor_box container and store the details and Processor instance.
    processor_box = Processor_box()
    processor_box.processor = object
    processor_box.processor_name = processor_name
    processor_box.class_name = class_name

    # Return the Processor instance.
    return object



class Processor_box(object):
    """A storage class for the Processor instance and its attributes.

    This singleton contains Processor instances and information about these Processors.  Importantly
    this container gives the calling code access to the Processor.
    """

    # Class variable for storing the class instance.
    instance = None

    def __new__(self, *args, **kargs): 
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            self.instance = object.__new__(self, *args, **kargs)

        # Already initialised, so return the instance.
        return self.instance
