###############################################################################
#                                                                             #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
import platform
from Queue import Queue
from re import search
import sys
from threading import Lock, RLock

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
            self._instance.pedantic = False
            self._instance.test_mode = False
            self._instance.show_gui = False
            self._instance.install_path = sys.path[0]

            # Set up the singleton.
            self._instance._setup()

        # Already instantiated, so return the instance.
        return self._instance


    def _setup(self):
        """Initialise all the status data structures."""

        # Execution lock object.
        self.exec_lock = Exec_lock()

        # The data pipe lock object.
        self.pipe_lock = Relax_lock(name='pipe_lock')

        # The molecule, residue, spin structure lock object.
        self.spin_lock = Relax_lock(name='spin_lock')

        # The exception queue for handling exceptions in threads.
        self.exception_queue = Queue()

        # The auto-analysis status containers.
        self.auto_analysis = {}
        self.current_analysis = None

        # GUI structures.
        self.controller_max_entries = 100000    # Scroll back limit in the relax controller.

        # A structure for skipped system and unit tests.
        self.skipped_tests = []
        """The skipped tests list.  Each element should be a list of the test case name, the missing Python module, and the name of the test suite category (i.e. 'system' or 'unit')."""

        # Set up the observer objects.
        self._setup_observers()

        # Text wrapping on different operating systems.
        if platform.uname()[0] in ['Windows', 'Microsoft']:
            self.text_width = 79
        else:
            self.text_width = 100

        # Text output colouring.
        self.text_colouring = False


    def _setup_observers(self):
        """Set up all the observer objects."""

        # A container for all the observers.
        self.observers = Status_container()

        # The observer object for status changes in the auto-analyses.
        self.observers.auto_analyses = Observer('auto_analyses')

        # The observer object for pipe switches.
        self.observers.pipe_alteration = Observer('pipe_alteration')

        # The observer object for GUI user function completion.
        self.observers.gui_uf = Observer('gui_uf')

        # The observer object for changes to the GUI analysis tabs.
        self.observers.gui_analysis = Observer('gui_analysis')

        # The observer object for relax resets.
        self.observers.reset = Observer('reset')

        # The observer object for the execution lock.
        self.observers.exec_lock = Observer('exec_lock')

        # The observer object for the creation of results files.
        self.observers.result_file = Observer('result_file')


    def init_auto_analysis(self, name, type):
        """Initialise a status container for an auto-analysis.

        @param name:    The unique name of the auto-analysis.  This will act as a key.
        @type name:     str.
        @param type:    The type of auto-analysis.
        @type type:     str
        """

        # Add a status container.
        self.auto_analysis[name] = Auto_analysis(name, type)


    def reset(self):
        """Reset the status object to its initial state."""

        # Simply call the setup again.
        self._setup()



class Auto_analysis:
    """The auto-analysis status container."""

    def __init__(self, name, type):
        """Initialise the auto-analysis status object.

        @param name:    The unique name of the auto-analysis.  This will act as a key.
        @type name:     str.
        @param type:    The type of auto-analysis.
        @type type:     str
        """

        # The status container.
        self._status = Status()

        # Store the analysis type.
        self.__dict__['type'] = type

        # The completion flag.
        self.__dict__['fin'] = False

        # The Monte Carlo simulation status, if used.
        self.__dict__['mc_number'] = None


    def __setattr__(self, name, value):
        """Replacement __setattr__() method.

        @param name:    The name of the attribute.
        @type name:     str
        @param value:   The value of the attribute.
        @type value:    anything
        """

        # First set the attribute.
        self.__dict__[name] = value

        # Then notify the observers.
        self._status.observers.auto_analyses.notify()



class Exec_lock:
    """A type of locking object for locking execution of relax."""

    def __init__(self, fake_lock=False):
        """Set up the lock-like object.

        @keyword fake_lock: A flag which is True will allow this object to be debugged as the locking mechanism is turned off.
        @type fake_lock:    bool
        """

        # Store the arg.
        self._fake_lock = fake_lock

        # Init a threading.Lock object.
        self._lock = Lock()

        # The status container.
        self._status = Status()

        # The name and mode of the locker.
        self._name = None
        self._mode = None

        # Script nesting level.
        self._script_nest = 0

        # Auto-analysis from script launch.
        self._auto_from_script = False

        # Debugging.
        if self._fake_lock:
            self.log = open('lock.log', 'w')


    def acquire(self, name, mode='script'):
        """Simulate the Lock.acquire() mechanism.

        @param name:    The name of the locking code.
        @type name:     str
        @keyword mode:  The mode of the code trying to obtain the lock.  This can be one of 'script' for the scripting interface or 'auto-analysis' for the auto-analyses.
        @type mode:     str
        """

        # Debugging.
        if self._status.debug:
            sys.stdout.write("debug> Execution lock:  Acquisition by '%s' ('%s' mode).\n" % (name, mode))

        # Do not acquire if lunching a script from a script.
        if mode == 'script' and self._mode == 'script' and self.locked():
            # Increment the nesting counter.
            self._script_nest += 1

            # Debugging.
            if self._fake_lock:
                self.log.write("Nested by %s (to level %s)\n" % (name, self._script_nest))
                self.log.flush()

            # Return without doing anything.
            return

        # Skip locking if an auto-analysis is called from a script.
        if self.locked() and self._mode == 'script' and mode == 'auto-analysis':
            # Debugging.
            if self._fake_lock:
                self.log.write("Skipped unlocking of '%s' lock by '%s'\n" % (self._name, name))
                self.log.flush()

            # Switch the flag.
            self._auto_from_script = True

            # Return without doing anything.
            return

        # Store the new name and mode.
        self._name = name
        self._mode = mode

        # Debugging.
        if self._fake_lock:
            self.log.write("Acquired by %s\n" % self._name)
            self.log.flush()
            return

        # Acquire the real lock.
        lock = self._lock.acquire()

        # Notify observers.
        status = Status()
        status.observers.exec_lock.notify()

        # Return the real lock.
        return lock


    def locked(self):
        """Simulate the Lock.locked() mechanism."""

        # Debugging (pseudo-locking based on _name).
        if self._fake_lock:
            if self._name:
                return True
            else:
                return False

        # Call the real method.
        return self._lock.locked()


    def release(self):
        """Simulate the Lock.release() mechanism."""

        # Debugging.
        if self._status.debug:
            sys.stdout.write("debug> Execution lock:  Release by '%s' ('%s' mode).\n" % (self._name, self._mode))

        # Nested scripting.
        if self._script_nest:
            # Debugging.
            if self._fake_lock:
                self.log.write("Script termination, nest decrement (%s -> %s)\n" % (self._script_nest, self._script_nest-1))
                self.log.flush()

            # Decrement.
            self._script_nest -= 1

            # Return without releasing the lock.
            return

        # Auto-analysis launched from script.
        if self._auto_from_script:
            # Debugging.
            if self._fake_lock:
                self.log.write("Auto-analysis launched from script, skipping release.\n")
                self.log.flush()

            # Unset the flag.
            self._auto_from_script = False

            # Return without releasing the lock.
            return

        # Reset the name and mode.
        self._name = None
        self._mode = None

        # Debugging.
        if self._fake_lock:
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
        release = self._lock.release()

        # Notify observers.
        status = Status()
        status.observers.exec_lock.notify()

        # Return the status.
        return release



class Observer(object):
    """The observer design pattern base class."""

    def __init__(self, name='unknown'):
        """Set up the object.

        @keyword name:      The special name for the observer object, used in debugging.
        @type name:         str
        """

        # Store the args.
        self._name = name

        # The dictionary of callback methods.
        self._callback = {}

        # The list of keys, for ordered execution.
        self._keys = []

        # The status container.
        self._status = Status()


    def notify(self):
        """Notify all observers of the state change."""

        # Loop over the callback methods and execute them.
        for key in self._keys:
            # Debugging.
            if self._status.debug:
                sys.stdout.write("debug> Observer: '%s' notifying '%s'.\n" % (self._name, key))

            # Call the method.
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

        # Debugging.
        if self._status.debug:
            sys.stdout.write("debug> Observer: '%s' registering '%s'.\n" % (self._name, key))

        # Add the method to the dictionary of callbacks.
        self._callback[key] = method

        # Add the key to the ordered list.
        self._keys.append(key)


    def reset(self):
        """Reset the object."""

        # Debugging.
        if self._status.debug:
            sys.stdout.write("debug> Resetting observer '%s'.\n" % self._name)

        # Reinitialise the dictionary of callback methods.
        self._callback = {}

        # Reinitialise the key list.
        self._keys = []


    def unregister(self, key):
        """Unregister the method corresponding to the key.

        @param key:     The key to identify the observer's method.
        @type key:      str
        """

        # Debugging.
        if self._status.debug:
            sys.stdout.write("debug> Observer: '%s' unregistering '%s'.\n" % (self._name, key))

        # Does not exist, so return (allow multiple code paths to unregister methods).
        if key not in self._keys:
            if self._status.debug:
                sys.stdout.write("debug> The key '%s' does not exist." % key)
            return

        # Remove the method from the dictionary of callbacks.
        self._callback.pop(key)

        # Remove the key for the ordered key list.
        self._keys.remove(key)



class Relax_lock:
    """A type of locking object for relax."""

    def __init__(self, name='unknown', fake_lock=False):
        """Set up the lock-like object.

        @keyword name:      The special name for the lock, used in debugging.
        @type name:         str
        @keyword fake_lock: A flag which is True will allow this object to be debugged as the locking mechanism is turned off.
        @type fake_lock:    bool
        """

        # Store the args.
        self.name = name
        self._fake_lock = fake_lock

        # Init a reentrant lock object.
        self._lock = RLock()

        # The status container.
        self._status = Status()

        # Fake lock.
        if self._fake_lock:
            # Track the number of acquires.
            self._lock_level = 0


    def acquire(self, acquirer='unknown'):
        """Simulate the RLock.acquire() mechanism.

        @keyword acquirer:  The optional name of the acquirer.
        @type acquirer:     str
        """

        # Debugging.
        if self._status.debug:
            sys.stdout.write("debug> Lock '%s':  Acquisition by '%s'.\n" % (self.name, acquirer))

        # Fake lock.
        if self._fake_lock:
            # Increment the lock level.
            self._lock_level += 1

            # Throw an error.
            if self._lock_level > 1:
                raise

            # Return to prevent real locking.
            return

        # Acquire the real lock.
        lock = self._lock.acquire()

        # Return the real lock.
        return lock


    def locked(self):
        """Simulate the RLock.locked() mechanism."""

        # Call the real method.
        return self._lock.locked()


    def release(self, acquirer='unknown'):
        """Simulate the RLock.release() mechanism.

        @keyword acquirer:  The optional name of the acquirer.
        @type acquirer:     str
        """

        # Debugging.
        if self._status.debug:
            sys.stdout.write("debug> Lock '%s':  Release by '%s'.\n" % (self.name, acquirer))

        # Fake lock.
        if self._fake_lock:
            # Decrement the lock level.
            self._lock_level -= 1

            # Return to prevent real lock release.
            return

        # Release the real lock.
        release = self._lock.release()

        # Return the status.
        return release



class Status_container:
    """The generic empty container for the status data."""


