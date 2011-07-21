###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
from re import search
import sys
from threading import Lock

# relax module imports.
from relax_errors import RelaxError


class Status(object):
    """The relax status singleton class."""

    # Class variable for storing the class instance (for the singleton).
    _instance = None

    def __new__(self, *args, **kargs):
        """Replacement method for implementing the singleton design pattern."""

        # First instantiation.
        if self._instance is None:
            # Instantiate.
            self._instance = object.__new__(self, *args, **kargs)

            # Initialise some variables.
            self._instance.debug = False
            self._instance.install_path = sys.path[0]

            # Set up the singleton.
            self._instance._setup()

        # Already instantiated, so return the instance.
        return self._instance


    def _setup(self):
        """Initialise all the status data structures."""

        # Execution lock object.
        self.exec_lock = Exec_lock()

        # Testing mode flag.
        self.test_mode = False

        # The GUI flag.
        self.show_gui = False

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

        # A structure for skipped system and unit tests.
        self.skipped_tests = []
        """The skipped tests list.  Each element should be a list of the test case name, the missing Python module, and the name of the test suite category (i.e. 'system' or 'unit')."""

        # Set up the observer objects.
        self._setup_observers()


    def _setup_observers(self):
        """Set up all the observer objects."""

        # A container for all the observers.
        self.observers = Status_container()

        # The observer object for pipe switches.
        self.observers.pipe_alteration = Observer()

        # The observer object for GUI user function completion.
        self.observers.gui_uf = Observer()

        # The observer object for changes to the GUI analysis tabs.
        self.observers.gui_analysis = Observer()

        # The observer object for relax resets
        self.observers.reset = Observer()


class Status_container:
    """The generic empty container for the status data."""



class Exec_lock:
    """A type of locking object for locking execution of relax."""

    def __init__(self, debug=False):
        """Set up the lock-like object."""

        # Store the arg.
        self.debug = debug

        # Init a threading.Lock object.
        self._lock = Lock()

        # The name of the locker.
        self._name = None

        # Script nesting level.
        self._script_nest = 0

        # Auto-analysis from script launch.
        self._auto_from_script = False

        # Debugging.
        if self.debug:
            self.log = open('lock.log', 'w')


    def acquire(self, name):
        """Simulate the Lock.acquire() mechanism.

        @param name:    The name of the locking code.
        @type name:     str
        """

        # Do not acquire if lunching a script from a script.
        if name == 'script UI' and self._name == 'script UI' and self.locked():
            # Increment the nesting counter.
            self._script_nest += 1

            # Debugging.
            if self.debug:
                self.log.write("Nested by %s (to level %s)\n" % (name, self._script_nest))
                self.log.flush()

            # Return without doing anything.
            return

        # Skip locking if an auto-analysis is called from a script.
        if self.locked() and self._name == 'script UI' and search('^auto', name):
            # Debugging.
            if self.debug:
                self.log.write("Skipped unlocking of '%s' lock by '%s'\n" % (self._name, name))
                self.log.flush()

            # Switch the flag.
            self._auto_from_script = True

            # Return without doing anything.
            return

        # Store the new name.
        self._name = name

        # Debugging.
        if self.debug:
            self.log.write("Acquired by %s\n" % self._name)
            self.log.flush()
            return

        # Acquire the real lock.
        return self._lock.acquire()


    def locked(self):
        """Simulate the Lock.locked() mechanism."""

        # Debugging (pseudo-locking based on _name).
        if self.debug:
            if self._name:
                return True
            else:
                return False

        # Call the real method.
        return self._lock.locked()


    def release(self):
        """Simulate the Lock.release() mechanism."""

        # Nested scripting.
        if self._script_nest:
            # Debugging.
            if self.debug:
                self.log.write("Script termination, nest decrement (%s -> %s)\n" % (self._script_nest, self._script_nest-1))
                self.log.flush()

            # Decrement.
            self._script_nest -= 1

            # Return without releasing the lock.
            return

        # Auto-analysis launched from script.
        if self._auto_from_script:
            # Debugging.
            if self.debug:
                self.log.write("Auto-analysis launched from script, skipping release.\n")
                self.log.flush()

            # Unset the flag.
            self._auto_from_script = False

            # Return without releasing the lock.
            return

        # Reset the name.
        self._name = None

        # Debugging.
        if self.debug:
            # Main text.
            text = 'Release'

            # Test suite info.
            if hasattr(self, 'test_name'):
                text = text + 'd by %s' % self.test_name

            # Write out, flush, and exit the method.
            self.log.write("%s\n\n" % text)
            self.log.flush()
            return

        # Release the real lock.
        return self._lock.release()



class Observer(object):
    """The observer design pattern base class."""

    def __init__(self):
        """Set up the object."""

        # The dictionary of callback methods.
        self._callback = {}

        # The list of keys, for ordered execution.
        self._keys = []


    def notify(self):
        """Notify all observers of the state change."""

        # Loop over the callback methods and execute them.
        for key in self._keys:
            self._callback[key]()


    def register(self, key, method):
        """Register a method to be called when the state changes.

        @param key:     The key to identify the observer's method.
        @type key:      str
        @param method:  The observer's method to be called after a state change.
        @type method:   method
        """

        # Already exists.
        if key in self._keys:
            raise RelaxError("The observer '%s' already exists." % key)

        # Add the method to the dictionary of callbacks.
        self._callback[key] = method

        # Add the key to the ordered list.
        self._keys.append(key)


    def reset(self):
        """Reset the object."""

        # Reinitialise the dictionary of callback methods.
        self._callback = {}

        # Reinitialise the key list.
        self._keys = []


    def unregister(self, key):
        """Unregister the method corresponding to the key.

        @param key:     The key to identify the observer's method.
        @type key:      str
        """

        # Does not exist.
        if key not in self._keys:
            raise RelaxError("The key '%s' does not exist." % key)

        # Remove the method from the dictionary of callbacks.
        self._callback.pop(key)

        # Remove the key for the ordered key list.
        self._keys.remove(key)
