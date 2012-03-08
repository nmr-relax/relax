"""A reference implementation of the multi-processor package.

Description
===========

This is a basic but full implementation of the multi-processor package to demonstrate how it is used.


Testing
=======

To run in uni-processor mode on a dual core system, change the MULTI variable to False and type::

$ python test_implementation.py


To run in mpi4py multi-processor mode with one master and two slave processors on minimally a dual core system, change the MULTI variable to True and type::

$ mpiexec -n 3 python test_implementation.py

For a single dual core CPU (Intel Core 2 Duo E8400 at 3.00GHz), the total times averaged over 5 runs are:
    - Uni-processor:        51.548 seconds (51.054+52.224+51.257+51.112+52.093)
    - Mpi4py-processor:     43.185 seconds (43.867+41.478+46.209+39.941+44.429)
    - Scaling efficiency:   1.194


Linux
-----

For multi-core systems and late 2.6 Linux kernels, the following as root might be required to prevent the master processor from taking 100% of one CPU core while waiting for the slaves.

# echo "1" > /proc/sys/kernel/sched_compat_yield
"""

# Python module imports.
from numpy import dot, float64, zeros
try:
    import cProfile as profile
except ImportError:
    import profile
import pstats
from random import uniform
import sys

# Modify the module path.
sys.path.append('..')

# relax module imports.
from multi import Application_callback, load_multiprocessor, Memo, Processor_box, Result_command, Slave_command


# Module variables.
PROFILE = True
MULTI = True
if MULTI:
    FABRIC = 'mpi4py'
    PROCESSOR_NUM = 2
else:
    FABRIC = 'uni'
    PROCESSOR_NUM = 1


def print_stats(stats, status=0):
    """Profiling print out function, sorting first by cumulative time."""

    # Sorted print out.
    pstats.Stats(stats).sort_stats('cumulative').print_stats()



class Main:
    """The program."""

    def __init__(self):
        """Set up some initial variables."""

        # The total number of calculations to perform by all slave processors.
        self.N = 2000000

        # Variable for counting the completed calculations (to demonstrate slave->master communication).
        self.num = 0


    def run(self):
        """This required method executes the entire program."""

        # Initialise the Processor box singleton.
        processor_box = Processor_box()

        # Loop over the slaves.
        num = processor_box.processor.processor_size()
        for i in range(num):
            # Partition out the calculations to one slave.
            slave = Test_slave_command(N=self.N/num)

            # Initialise the memo object.
            memo = Test_memo(name="Memo_"+repr(i), sum_fn=self.sum_fn)

            # Queue the slave command and its memo.
            processor_box.processor.add_to_queue(slave, memo)

        # Execute the calculations, waiting for completion.
        processor_box.processor.run_queue()

        # Final program print out.
        print("\n\nTotal number of calculations: %s" % self.num)


    def sum_fn(self, num):
        """Method for slave->master communication.

        This is stored in the memo object and used by the result_command on the master (itself invoked by the slave command on the slave processors) to pass the slave data to the master.

        @param num:     The number of calculations performed by a given slave processor.
        @type num:      int
        """

        # Sum the total number of calculations performed on the slaves.
        self.num += num



class Test_memo(Memo):
    """The memo object containing data and functions for the results_command."""

    def __init__(self, name, sum_fn):
        """Store some data for the result command.

        @param name:    A name for the memo.
        @type name:     str
        @param sum_fn:  A method for summing the number calculations performed by all slaves.
        @type sum_fn:   method
        """

        # Store the arguments for later use by the result_command.
        self.name = name
        self.sum_fn = sum_fn



class Test_result_command(Result_command):
    """The result command for processing the results from the slaves on the master."""

    def __init__(self, processor, memo_id=None, num=None, completed=True):
        """Store all the slave results for processing on the master.

        @param processor:   The slave processor object.
        @type processor:    Processor instance
        @keyword memo_id:   The ID of the corresponding memo object (currently serves no purpose).
        @type memo_id:      int
        @keyword num:       The number of calculations performed by the slave.  This is an example of data transfer from the slave to master processor.
        @type num:          int
        @keyword completed: A flag saying if the calculation on the slave processor completed correctly.
        @type completed:    bool
        """

        # Execute the base class __init__() method (essential).
        super(Test_result_command, self).__init__(processor=processor, completed=completed)

        # Store the arguments.
        self.memo_id = memo_id
        self.num = num


    def run(self, processor, memo):
        """Essential method for doing something with the results from the slave processors.

        @param processor:   The slave processor object.
        @type processor:    Processor instance
        @param memo:        The slave's corresponding memo object.
        @type memo:         Memo instance
        """

        # Random print out.
        print("%s, %s calculations completed." % (memo.name, self.num))

        # Calling a method on the master.
        memo.sum_fn(self.num)



class Test_slave_command(Slave_command):
    """The slave command for use by the slave processor."""

    def __init__(self, N=0):
        """Set up the slave command object for the slave processor.

        @keyword N:     The number of calculations for the slave to perform.
        @type N:        int
        """

        # Store the argument.
        self.N = N

        # Initialise some matrices.
        self.A = zeros((3, 3), float64)
        self.B = zeros((3, 3), float64)


    def run(self, processor, completed=False):
        """Essential method for performing calculations on the slave processors.

        @param processor:   The slave processor object.
        @type processor:    Processor instance
        @keyword completed: A flag specifying if the slave calculation is completed.  This is currently meaningless, but will be passed to this run() method anyway so it needs to be present.
        @type completed:    bool
        """

        # Perform some random useless time-consuming stuff.
        num_calcs = 0
        for i in range(self.N):
            # Randomise the matrices.
            for j in range(3):
                for k in range(3):
                    self.A[j, k] = uniform(0, 1)
                    self.B[j, k] = uniform(0, 1)

            # Perform some linear algebra.
            dot(self.A, self.B)

            # Keep track of the number of calculations.
            num_calcs += 1

        # Process the results on the master.
        processor.return_object(Test_result_command(processor, memo_id=self.memo_id, num=num_calcs))



# Set up the processor.
processor = load_multiprocessor(FABRIC, Application_callback(master=Main()), processor_size=PROCESSOR_NUM, verbosity=1)

# Run in multi-processor mode.
if not PROFILE:
    processor.run()

# Run in multi-processor mode with profiling.
else:
    # Replace the default profiling print out function.
    profile.Profile.print_stats = print_stats

    # Execute with profiling.
    profile.runctx('processor.run()', globals(), locals())
