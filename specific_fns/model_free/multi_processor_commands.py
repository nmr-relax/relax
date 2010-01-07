###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2008, 2010 Edward d'Auvergne                                  #
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
"""Module for the multi-processor command system."""

# Python module imports.
import sys
from re import match

# relax module imports.
from maths_fns.mf import Mf
from minfx.generic import generic_minimise
from minfx.grid import grid
from multi.processor import Capturing_exception, Memo, Result_command, Result_string, Slave_command


class MF_grid_memo(Memo):
    def __init__(self, super_grid_memo):

        # Execute the base class __init__() method.
        super(MF_grid_memo, self).__init__()

        self.super_grid_memo = super_grid_memo
        self.super_grid_memo.add_sub_memo(self)


    def add_result(self, results):
        self.super_grid_memo.add_result(self, results)


class MF_grid_result_command(Result_command):
    def __init__(self, processor, result_string, memo_id, param_vector, func, iter, fc, gc, hc, warning, completed):

        # Execute the base class __init__() method.
        super(MF_grid_result_command, self).__init__(processor=processor, completed=completed)

        self.result_string = result_string
        self.memo_id = memo_id
        self.param_vector = param_vector
        self.func = func
        self.iter = iter
        self.fc = fc
        self.gc = gc
        self.hc = hc
        self.warning = warning


    def run(self, processor, memo):
        # FIXME: Check against full result
        # FIXME: names not consistent in memo
        # FIXME: too much repacking
        results = (self.param_vector, self.func, self.iter, self.fc, self.gc, self.hc, self.warning)
        memo.add_result(results)

        sgm = memo.super_grid_memo

        print_prefix = sgm.print_prefix
        verbosity = sgm.verbosity
        full_output = sgm.full_output
        A = sgm.A
        b = sgm.b
        grid_size = sgm.grid_size

        if sgm.first_time:
            print()
            print("Unconstrained grid search size: " + repr(grid_size) + " (constraints may decrease this size).\n")
            if verbosity:
                if verbosity >= 2:
                    print(print_prefix)
                print(print_prefix)
                print(print_prefix + "Grid search")
                print(print_prefix + "~~~~~~~~~~~")

            # Linear constraints.
            if A != None and b != None:
                if verbosity >= 3:
                    print(print_prefix + "Linear constraint matrices.")
                    print(print_prefix + "A: " + repr(A))
                    print(print_prefix + "b: " + repr(b))

        # we don't want to prepend the masters stdout tag
        sys.stdout.write('\n'+self.result_string),

        if sgm.completed:
            if verbosity and results != None:
                if full_output:
                    print('')
                    print('')
                    print(print_prefix + "Parameter values: " + repr(sgm.xk))
                    print(print_prefix + "Function value:   " + repr(sgm.fk))
                    print(print_prefix + "Iterations:       " + repr(sgm.k))
                    print(print_prefix + "Function calls:   " + repr(sgm.f_count))
                    print(print_prefix + "Gradient calls:   " + repr(sgm.g_count))
                    print(print_prefix + "Hessian calls:    " + repr(sgm.h_count))
                    if sgm.warning:
                        print(print_prefix + "Warning:          " + sgm.warning)
                    else:
                        print(print_prefix + "Warning:          None")
                else:
                    print(print_prefix + "Parameter values: " + repr(sgm.short_results))
                print("")

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            sgm.model_free.iter_count = 0
            sgm.model_free.f_count = 0
            sgm.model_free.g_count = 0
            sgm.model_free.h_count = 0

            # Disassemble the results.
            sgm.model_free._disassemble_result(param_vector=sgm.xk, func=sgm.fk, iter=sgm.k, fc=sgm.f_count, gc=sgm.g_count, hc=sgm.h_count, warning=sgm.warning, spin=sgm.spin, sim_index=sgm.sim_index, model_type=sgm.model_type, scaling=sgm.scaling, scaling_matrix=sgm.scaling_matrix)


class MF_memo(Memo):
    """The model-free memo class.

    Not quite a momento so a memo.
    """

    def __init__(self, model_free, spin, sim_index, model_type, scaling, scaling_matrix):
        """Initialise the model-free memo class."""

        # Execute the base class __init__() method.
        super(MF_memo, self).__init__()

        self.spin = spin
        self.sim_index = sim_index
        self.model_type = model_type
        self.model_free = model_free
        self.scaling = scaling
        self.scaling_matrix = scaling_matrix


class MF_minimise_command(Slave_command):
    """Command class for standard model-free minimisation."""

    def __init__(self):
        """Initialise the class with empty maps."""

        # Execute the base class __init__() method.
        super(MF_minimise_command, self).__init__()

        # The minimisation map containing the minimisation information.
        self.minimise_map = {'args':(), 'x0':None, 'min_algor':None, 'min_options':None, 'func_tol':1e-25, 'grad_tol':None, 'maxiter':1e6, 'A':None, 'b':None, 'l':None, 'u':None, 'c':None, 'dc':None, 'd2c':None, 'dc':None, 'd2c':None, 'full_output':0, 'print_flag':0, 'print_prefix':""}

        # A map containing generic information.
        self.info_map = {'mf':None, 'model_type':None, 'spin_id':None, 'sim_index':None, 'grid_size':1}

        # A flag for silencing output.
        self.silence = False


    def initial_printout(self):
        """Generate some print outs for normal analysis."""

        # Only print out if verbosity is turned on.
        if self.minimise_map['print_flag'] >= 1:
            # Monte Carlo simulation print out.
            if self.info_map['sim_index'] != None and self.info_map['index'] == 0:
                print('Simulation '+ repr(self.info_map['sim_index'])+ '\n')

            # Individual spin print out.
            if self.model_type == 'mf' or self.model_type == 'local_tm':
                if self.minimise_map['print_flag'] >= 2:
                    print("\n\n")
                string = "Fitting to spin: " + self.info_map['spin_id']
                print("\n\n" + string)
                print(len(string) * '~')


    # rename confusing with processor process_results
    def process_results(self, results, processor, completed):

        # Disassemble the results list.
        param_vector, func, iter, fc, gc, hc, warning = results

        # Get the STDOUT and STDERR messages.
        #FIXME: we need to interleave stdout and stderr
        (stdout, stderr)= processor.get_stdio_capture()
        result_string = stdout.getvalue() + stderr.getvalue()
        stdout.truncate(0)
        stderr.truncate(0)

        processor.return_object(MF_result_command(processor, self.memo_id, param_vector, func, iter, fc, gc, hc, warning, completed=False))
        processor.return_object(Result_string(processor, result_string, completed=completed))


    def run(self, processor, completed):
        """Execute the model-free optimisation."""

        # Silencing.
        if self.silence:
            self.minimise_map['print_flag'] = 0

        # Run catching all errors.
        try:
            # Initial print outs.
            self.initial_printout()

            # Minimisation.
            results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, **self.minimise_map)

            # Processing.
            self.process_results(results, processor, completed)

        # An error occurred.
        except Exception, e :
            if isinstance(e, Capturing_exception):
                raise e
            else:
                raise Capturing_exception(rank=processor.rank(), name=processor.get_name())


    def set_minimise(self, **kwargs):
        """Place the minimisation and other information into the appropriate maps."""

        # The optimisation class.
        self.mf = kwargs['mf']
        del kwargs['mf']

        # The model type.
        self.model_type = kwargs['model_type']
        del kwargs['model_type']

        # Strip out and store special arguments into the info_map.
        if 'spin_id' in kwargs:
           self.info_map['spin_id'] = kwargs['spin_id']
           del kwargs['spin_id']
        if 'index' in kwargs:
           self.info_map['index'] = kwargs['index']
           del kwargs['index']
        if 'grid_size' in kwargs:
           self.info_map['grid_size'] = kwargs['grid_size']
           del kwargs['grid_size']
        if 'sim_index' in kwargs:
           self.info_map['sim_index'] = kwargs['sim_index']
           del kwargs['sim_index']

        # Fill out the minimise_map using the remaining keyword args.
        self.minimise_map.update(kwargs)


class MF_grid_command(MF_minimise_command):
    """Command class for the model-free grid search."""

    def __init__(self):
        """Execute the MF_minimise_command __init__() method."""

        # Execute the base class __init__() method.
        super(MF_grid_command, self).__init__()

        # A flag for silencing output.
        self.silence = True


    def initial_printout(self, processor):
        """Dummy method to overwrite the base class method."""

        pass


    def process_results(self, results, processor, completed):
        param_vector, func, iter, fc, gc, hc, warning = results

        processor.return_object(MF_grid_result_command(processor, result_string, self.memo_id, param_vector, func, iter, fc, gc, hc, warning, completed=completed))


class MF_result_command(Result_command):
    def __init__(self, processor, memo_id, param_vector, func, iter, fc, gc, hc, warning, completed):

        # Execute the base class __init__() method.
        super(MF_result_command, self).__init__(processor=processor, completed=completed)

        self.memo_id = memo_id
        self.param_vector = param_vector
        self.func = func
        self.iter = iter
        self.fc = fc
        self.gc = gc
        self.hc = hc
        self.warning = warning


    def run(self, processor, memo):
        """Disassemble the model-free optimisation results.

        @param processor:   Unused!
        @type processor:    None
        @param memo:        The model-free memo.
        @type memo:         memo
        """

        # Initialise the iteration counter and function, gradient, and Hessian call counters.
        memo.model_free.iter_count = 0
        memo.model_free.f_count = 0
        memo.model_free.g_count = 0
        memo.model_free.h_count = 0

        # Disassemble the results.
        memo.model_free._disassemble_result(param_vector=self.param_vector, func=self.func, iter=self.iter, fc=self.fc, gc=self.gc, hc=self.hc, warning=self.warning, spin=memo.spin, sim_index=memo.sim_index, model_type=memo.model_type, scaling=memo.scaling, scaling_matrix=memo.scaling_matrix)


class MF_super_grid_memo(MF_memo):
    def __init__(self, model_free, spin, sim_index, model_type, scaling, scaling_matrix, print_prefix, verbosity, full_output, A, b, grid_size):

        # Execute the base class __init__() method.
        super(MF_super_grid_memo, self).__init__(model_free, spin, sim_index, model_type, scaling, scaling_matrix)

        self.full_output = full_output
        self.print_prefix = print_prefix
        self.verbosity = verbosity
        self.sub_memos = []
        self.completed = False

        self.A = A
        self.b = b
        self.grid_size = grid_size
        # aggregated results
        #             min_params, f_min, k
        self.xk = None
        self.fk = 1e300
        self.k = 0
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0
        self.warning = []
        self.first_time = None


    def add_result(self, sub_memo, results):

        # Normal minimisation.
        if self.full_output:
            # Unpack the results.
            param_vector, func, iter, fc, gc, hc, warning = results

            if func < self.fk:
                self.xk = param_vector
                self.fk = func
            self.k += iter
            self.f_count += fc

            self.g_count += gc
            self.h_count += hc
            if warning != None:
                self.warning.append(warning)

        # Grid search.
        #FIXME: TESTME: do we use short results?
        else:
            # Unpack the results.
            param_vector, func, iter, warning = results

            if results[OFFSET_SHORT_FK] < self.short_result[OFFSET_SHORT_FK]:
                self.short_result[OFFSET_SHORT_MIN_PARAMS] = results[OFFSET_SHORT_MIN_PARAMS]
                self.short_result[OFFSET_SHORT_FK] = results[OFFSET_SHORT_FK]
            self.short_result[OFFSET_SHORT_K] += results[OFFSET_SHORT_K]
        self.sub_memos.remove(sub_memo)

        if len(self.sub_memos) < 1:
            self.completed = True
            if len(self.warning) == 0:
                self.warning = None
            else:
                self.warning = ', '.join(self.warning)

        # the order here is important !
        if self.first_time == True:
            self.first_time = False

        if self.first_time == None:
            self.first_time = True


    def add_sub_memo(self, memo):
        self.sub_memos.append(memo)
