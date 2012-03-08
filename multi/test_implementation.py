"""
To run in uni-processor mode on a dual core system, change the MULTI variable to False and type:

$ python parallel_test.py


To run in mpi4py multi-processor mode with one master and two slave processors on minimally a dual core system, change the MULTI variable to True and type:

$ mpiexec -n 3 python parallel_test.py

For a single dual core CPU (Intel Core 2 Duo E8400 at 3.00GHz), the total times averaged over 5 runs are:
    - Uni-processor:        31.293 seconds (30.724+30.413+31.197+31.866+32.266)
    - Mpi4py-processor:     23.772 seconds (24.854+21.756+22.514+26.899+22.836)
    - Scaling efficiency:   1.316
"""

# Python module imports.
from numpy import dot, float64, zeros
try:
    import cProfile as profile
except ImportError:
    import profile
import pstats
from random import uniform

# relax module imports.
from multi import Application_callback, load_multiprocessor, Memo, Processor_box, Result_command, Slave_command
from maths_fns.rotation_matrix import R_random_hypersphere


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
    """Profiling print out function."""

    pstats.Stats(stats).sort_stats('time', 'name').print_stats()



class Main:
    def __init__(self):
        """Set up some initial variables."""

        self.N = 10000000
        self.num = 0


    def run(self):
        # Initialise the Processor box singleton.
        processor_box = Processor_box()

        # Loop over the slaves.
        num = processor_box.processor.processor_size()
        for i in range(num):
            # Queue the slave command and memo.
            processor_box.processor.add_to_queue(Test_slave_command(N=self.N/num), Test_memo(name="Memo_"+repr(i), sum_fn=self.sum_fn))

        # Execute the calculations.
        processor_box.processor.run_queue()

        # Print out.
        print("\n\nTotal number of calculations: %s" % self.num)


    def sum_fn(self, num):
        self.num += num


class Test_memo(Memo):
    def __init__(self, name, sum_fn):
        """Store some data for the result_command."""

        # Store the args.
        self.name = name
        self.sum_fn = sum_fn



class Test_result_command(Result_command):
    def __init__(self, processor, memo_id=None, num=None, completed=True):
        """Store all the slave results for processing on the master."""

        # Execute the base class __init__() method.
        super(Test_result_command, self).__init__(processor=processor, completed=completed)

        # Store the arguments.
        self.memo_id = memo_id
        self.num = num


    def run(self, processor, memo):

        # Print out.
        print("%s, %s calculations completed." % (memo.name, self.num))

        # Calling a function on the master.
        memo.sum_fn(self.num)



class Test_slave_command(Slave_command):
    def __init__(self, N=None):
        self.N = N

        # Initialise the matrices.
        self.A = zeros((3, 3), float64)
        self.B = zeros((3, 3), float64)


    def run(self, processor, completed):

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
main = Main()
processor = load_multiprocessor(FABRIC, Application_callback(master=Main()), processor_size=PROCESSOR_NUM, verbosity=1)

# Run in multi-processor mode.
if not PROFILE:
    processor.run()

# Run in multi-processor mode with profiling.
else:
    profile.Profile.print_stats = print_stats
    profile.runctx('processor.run()', globals(), locals())

