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


def import_module(module_path, verbose=False):
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


def raise_unimplemented(method):
    '''Standard function for raising NotImplementedError for unimplemented abstract methods.

    @param method:              The method which should be abstract.
    @type method:               class method
    @raise NotImplementedError: A not implemented exception with the method name as a parameter.
    '''

    msg = "Attempt to invoke unimplemented abstract method %s"
    raise NotImplementedError(msg % method.__name__)
