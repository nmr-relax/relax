###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Module containing the status singleton object."""

# Python module imports.
from threading import Lock

# relax module imports.
from relax_errors import RelaxError


class Status(object):
    """The relax status singleton class."""

    # Class variable for storing the class instance (for the singleton).
    _instance = None

    def __init__(self):
        """Initialise all the status data structures."""

        # Execution lock object.
        self.exec_lock = Exec_lock()

        # The Monte Carlo simulation status.
        self.mc_number = None

        # The dAuvergne_protocol automatic analysis status.
        self.dAuvergne_protocol = Status_container()
        self.dAuvergne_protocol.diff_model = None        # The global diffusion model.
        self.dAuvergne_protocol.round = None             # The round of optimisation, i.e. the global iteration.
        self.dAuvergne_protocol.mf_models = None         # The list of model-free models for optimisation, i.e. the global iteration.
        self.dAuvergne_protocol.local_tm_models = None   # The list of model-free local tm models for optimisation, i.e. the global iteration.
        self.dAuvergne_protocol.current_model = None     # The current model-free model.
        self.dAuvergne_protocol.convergence = False      # The convergence of the global model.


    def __new__(self, *args, **kargs):
        """Replacement method for implementing the singleton design pattern."""

        # First instantiation.
        if self._instance is None:
            # Instantiate.
            self._instance = object.__new__(self, *args, **kargs)

        # Already instantiated, so return the instance.
        return self._instance



class Status_container:
    """The generic empty container for the status data."""



class Exec_lock:
    """A type of locking object for locking execution of relax."""

    def __init__(self):
        """Set up the lock-like object."""

        # Init a threading.Lock object.
        self._lock = Lock()

        # The name of the locker.
        self._name = None


    def acquire(self, name):
        """Simulate the Lock.acquire() mechanism.

        @param name:    The name of the locking code.
        @type name:     str
        """

        # Store the name.
        self._name = name

        # Acquire the real lock.
        return self._lock.acquire()


    def locked(self):
        """Simulate the Lock.locked() mechanism."""

        # Call the real method.
        return self._lock.locked()


    def release(self):
        """Simulate the Lock.release() mechanism."""

        # Reset the name.
        self._name = None

        # Release the real lock.
        return self._lock.release()
