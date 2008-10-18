################################################################################
#                                                                              #
# Copyright (C) 2007  Gary S Thompson (see https://gna.org/users/varioustoxins #
#                                      for contact details)                    #
#                                                                              #
# This file is part of the program relax.                                      #
#                                                                              #
# relax is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 2 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# relax is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with relax; if not, write to the Free Software                         #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    #
#                                                                              #
################################################################################

# Module docstring.
"""Module for the multi-processor command system."""

# Python module imports.
import sys
import traceback
from re import match

# relax module imports.
from maths_fns.mf import Mf
#from minimise.generic import generic_minimise
#from minimise.generic import set_pre_and_post_amble as set_generic_pre_and_post_amble
#from minimise.grid import set_pre_and_post_amble as set_grid_pre_and_post_amble
from multi.processor import Capturing_exception, Memo, Result_command, Result_string, Slave_command


OFFSET_XK=0      #  The array of minimised parameter values
OFFSET_FK=1      #  The minimised function value,
OFFSET_K=2       #  The number of iterations,
OFFSET_F_COUNT=3 #  The number of function calls,
OFFSET_G_COUNT=4 #  The number of gradient calls,
OFFSET_H_COUNT=5 #  The number of Hessian calls,
OFFSET_WARNING=6 #  The warning string.

OFFSET_SHORT_MIN_PARAMS=0
OFFSET_SHORT_FK=1
OFFSET_SHORT_K=2


class MF_memo(Memo):
    """The model-free memo class.

    Not quite a momento so a memo.
    """

    def __init__(self, model_free, spin, sim_index, model_type, scaling, scaling_matrix):
        """Initialise the model-free memo class."""

        super(MF_memo, self).__init__()
        self.spin = spin
        self.sim_index = sim_index
        self.model_type = model_type
        self.model_free = model_free
        self.scaling = scaling
        self.scaling_matrix = scaling_matrix


class MF_result_command(Result_command):
    def __init__(self,processor,memo_id,param_vector, func, iter, fc, gc, hc, warning,completed):
        super(MF_result_command,self).__init__(processor=processor,completed=completed)
        self.memo_id=memo_id
        self.param_vector=param_vector
        self.func=func
        self.iter=iter
        self.fc=fc
        self.gc=gc
        self.hc=hc
        self.warning=warning

    def run(self,processor,memo):
        m_f=memo.model_free
        m_f.iter_count = 0
        m_f.f_count = 0
        m_f.g_count = 0
        m_f.h_count = 0
        #raise Exception()
        m_f.disassemble_result(param_vector=self.param_vector,func=self.func,iter=self.iter,fc=self.fc,
                               gc=self.gc,hc=self.hc, warning=self.warning,
                               run=memo.run, index=memo.index, sim_index=memo.sim_index,
                               param_set=memo.param_set, scaling=memo.scaling, scaling_matrix=memo.scaling_matrix)








class MF_minimise_command(Slave_command):
    def __init__(self):
        super(MF_minimise_command,self).__init__()


        #!! 'a0':1.0,'mu':0.0001,'eta':0.1,
        self.minimise_map={'args':(), 'x0':None, 'min_algor':None, 'min_options':None, 'func_tol':1e-25, 'grad_tol':None,
                     'maxiter':1e6, 'A':None, 'b':'None', 'l':None, 'u':None, 'c':None, 'dc':None, 'd2c':None,
                     'dc':None, 'd2c':None, 'full_output':0, 'verbosity':0,
                     'print_prefix':""}



        self.mf_map={'init_params':None, 'param_set':None, 'diff_type':None, 'diff_params':None,
                      'scaling_matrix':None, 'num_res':None, 'equations':None, 'param_types':None,
                      'param_values':None, 'relax_data':None, 'errors':None, 'bond_length':None,
                      'csa':None, 'num_frq':0, 'frq':None, 'num_ri':None, 'remap_table':None, 'noe_r1_table':None,
                      'ri_labels':None, 'gx':0, 'gh':0, 'g_ratio':0, 'h_bar':0, 'mu0':0, 'num_params':None, 'vectors':None}

        self.info_map={'res_id':None,'grid_size':1}
    #FIXME: bad names
    def set_mf(self, **kwargs):

        self.mf_map.update(kwargs)
# FIXME: add to checking class
#        self.mf_hash_map = self.get_hash_map(self.mf_map)

# FIXME: add to checking class
#    def get_hash_map(self,map):
#        import Numeric
#        result = {}
#        for key,elem in map.items():
#            #print key,  elem, type(elem),dir(type(elem))
#            #if isinstance(elem,Numeric.array):
#            #    print '*** here 888'
#            #    elem = tuple(elem.aslist())
#            #elem.__class__.__name__
#            result[key]=(`elem`)
#        return result

# FIXME: add to checking class
#    def assert_hash_map_same(self,ref_map,new_map):
#        for key in ref_map.keys():
#            if ref_map[key] != new_map[key]:
#                print 'bad compare ' + key


    def set_minimise(self,**kwargs):
        if 'res_id' in kwargs:
           self.info_map['res_id']= kwargs['res_id']
           del kwargs['res_id']
        if 'index' in kwargs:
           self.info_map['index']= kwargs['index']
           del kwargs['index']
        if 'grid_size' in kwargs:
           self.info_map['grid_size']= kwargs['grid_size']
           del kwargs['grid_size']
        if 'sim_index' in kwargs:
           self.info_map['sim_index']= kwargs['sim_index']
           del kwargs['sim_index']

        self.minimise_map.update(kwargs)
# FIXME: add to checking class
#        self.mf_minimise_map = self.get_hash_map(self.minimise_map)

    def build_mf(self):
        return  Mf(**self.mf_map)

#    def do_minimise(self,memo):
#
## FIXME: add to checking class
##        new_mf_map = self.get_hash_map(self.mf)
##        self.assert_hash_map_same(self.mf_hash_map,new_mf_map)
##        new_minimise_map = self.get_hash_map(self.minimise)
##        self.assert_hash_map_same(self.minimise_hash_map,new_minimise_map)
#
#        mf = self.build_mf()
#        results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, **self.minimise_map)
#
#        m_f=memo.model_free
#        param_vector, func, iter, fc, gc, hc, warning = results
#        m_f.disassemble_result(param_vector=param_vector,func=func,iter=iter,fc=fc,
#                               gc=gc,hc=hc, warning=warning,
#                               run=memo.run, index=memo.index,sim_index=memo.sim_index,
#                               param_set=memo.param_set,scaling=memo.scaling,scaling_matrix=memo.scaling_matrix)

    def do_feedback(self):
        """Minimisation print out."""

        # Only print out if verbosity is turned on.
        if self.minimise_map['verbosity'] >= 1:
            # montecarlo stuff
            if self.info_map['sim_index'] != None and self.info_map['index'] == 0:
                print 'Simulation '+ `self.info_map['sim_index']`+ '\n'
            # Individual residue stuff.
            if self.mf_map['param_set'] == 'mf' or self.mf_map['param_set'] == 'local_tm':
                if self.minimise_map['verbosity'] >= 2:
                    print "\n\n"
                string = "Fitting to residue: " + self.info_map['res_id']
                print "\n\n" + string
                print len(string) * '~'


    # rename confusing with processor process_results
    def process_results(self,results,processor,completed):
        param_vector, func, iter, fc, gc, hc, warning = results

        #FIXME: we need to interleave stdout and stderr
        (stdout,stderr)= processor.get_stdio_capture()
        result_string = stdout.getvalue() + stderr.getvalue()
        stdout.truncate(0)
        stderr.truncate(0)

        processor.return_object(MF_result_command(processor,self.memo_id,param_vector, func, iter, fc, gc, hc, warning,completed=False))
        processor.return_object(Result_string(processor,result_string,completed=completed))

    def pre_command_feed_back(self,processor):
        self.do_feedback()


    def pre_run(self,processor):
       pass
       #FIXME: move to processor startup



    def post_run(self,processor):
        #FIXME: move to processor startup
        pass

    def post_command_feedback(self,results,processor):
        pass

    def run_command(self,processor):
        self.mf = self.build_mf()
        return generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, **self.minimise_map)


#    def process_result(self,processor):
#        self.process_results(self.results,processor,completed)



    def run(self,processor, completed):

#        #FIXME: move to processor startup
#        save_stdout = sys.stdout
#        save_stderr = sys.stderr
#        pre_string = processor.rank_format_string() % processor.rank()
#        # add debug flag or extra channels that output immediately
#        sys.stdout = PrependStringIO(pre_string + ' S> ')
#        sys.stderr = PrependStringIO(pre_string + ' E> ')
        try:
            self.pre_run(processor)
            self.pre_command_feed_back(processor)
            results = self.run_command(processor)
            self.post_command_feedback(results, processor)
            self.process_results(results, processor, completed)
            self.post_run(processor)
        except Exception,e :
            processor.restore_stdio()
            if isinstance(e, Capturing_exception):
                raise e
            else:
                raise Capturing_exception(rank=processor.rank(),name=processor.get_name())






#        #FIXME: move to processor startup
#        sys.stdout.close()
#        sys.stderr.close()
#        sys.stdout = save_stdout
#        sys.stderr = save_stderr

class MF_grid_command(MF_minimise_command):
    def __init__(self):
        super(MF_grid_command,self).__init__()

#    def run(self,processor,completed):
#        pass

    def pre_command_feed_back(self,processor):
#        print_prefix  = self.minimise_map['print_prefix']
#        verbosity  = self.minimise_map['verbosity']
#        grid_step = self.minimise_map['min_options'].start
#        grid_size = self.minimise_map['min_options'].steps
#        full_output = self.minimise_map['full_output']
#        A = self.minimise_map['A']
#        b = self.minimise_map['b']
#

        set_generic_pre_and_post_amble(False)
        set_grid_pre_and_post_amble(False)
#        if grid_step == 0:
#            print "Unconstrained grid search size: " + `grid_size` + " (constraints may decrease this size).\n"
#
#            if verbosity:
#                if verbosity >= 2:
#                    print print_prefix
#                print print_prefix
#                print print_prefix + "Grid search"
#                print print_prefix + "~~~~~~~~~~~"
#
#            # Linear constraints.
#            if A != None and b != None:
#                if verbosity >= 3:
#                    print print_prefix + "Linear constraint matrices."
#                    print print_prefix + "A: " + `A`
#                    print print_prefix + "b: " + `b`

        #def run_command()
        #    return super(MF_grid_command,self).run(processor,completed)
    def post_command_feedback(self,results,processor):

        set_generic_pre_and_post_amble(True)
        set_grid_pre_and_post_amble(True)

    def process_results(self,results,processor,completed):
        param_vector, func, iter, fc, gc, hc, warning = results

        (stdout,stderr)= processor.get_stdio_capture()
        result_string = stdout.getvalue() + stderr.getvalue()
        stdout.truncate(0)
        stderr.truncate(0)


        processor.return_object(MF_grid_result_command(processor,result_string,self.memo_id,param_vector, func, iter, fc, gc, hc, warning,completed=completed))

class MF_grid_memo(Memo):
    def __init__(self,super_grid_memo):
        super(MF_grid_memo,self).__init__()
        self.super_grid_memo = super_grid_memo
        self.super_grid_memo.add_sub_memo(self)


    def add_result(self,results):
        self.super_grid_memo.add_result(self,results)

class MF_super_grid_memo(MF_memo):
    def __init__(self,model_free,index,sim_index,run,param_set,scaling,scaling_matrix,print_prefix,verbosity,full_output,A,b,grid_size):
        super(MF_super_grid_memo,self).__init__(model_free,index,sim_index,run,param_set,scaling,scaling_matrix)
        self.full_output=full_output
        self.print_prefix = print_prefix
        self.verbosity = verbosity
        self.sub_memos = []
        self.completed = False

        self.A=A
        self.b=b
        self.grid_size=grid_size
        # aggregated results
        #             min_params, f_min, k
        short_result=[None, None, 0]
        self.xk = None
        self.fk = 1e300
        self.k = 0
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0
        self.warning = []
        self.first_time=None





    def add_sub_memo(self,memo):
        self.sub_memos.append(memo)

    def add_result(self,sub_memo,results):
#        print '**** add result ****', sub_memo.memo_id(), results[OFFSET_FK], len(self.sub_memos)
#        print results
#        print self.full_output
#        print results[OFFSET_FK],self.fk
        sys.stdout.flush()
        if self.full_output:
            if results[OFFSET_FK] < self.fk:
                #print 'adding ******'
                self.xk = results[OFFSET_XK]
                self.fk = results[OFFSET_FK]
            self.k += results[OFFSET_K]
            self.f_count += results[OFFSET_F_COUNT]

            self.g_count += results[OFFSET_G_COUNT]
            self.h_count += results[OFFSET_H_COUNT]
            if results[OFFSET_WARNING] != None:
                self.warning.append(results[OFFSET_WARNING])

        #FIXME: TESTME: do we use short results?
        else:
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
                self.warning= ', '.join(self.warning)

        # the order here is important !
        if self.first_time == True:
            self.first_time=False

        if self.first_time == None:
            self.first_time = True
        #print   '****', self.xk,self.fk,self.k,self.f_count,self.g_count,self.h_count,self.warning

class MF_grid_result_command(Result_command):
    def __init__(self,processor,result_string,memo_id,param_vector, func, iter, fc, gc, hc, warning,completed):
        super(MF_grid_result_command,self).__init__(processor=processor,completed=completed)
        self.result_string=result_string
        self.memo_id=memo_id
        self.param_vector=param_vector
        self.func=func
        self.iter=iter
        self.fc=fc
        self.gc=gc
        self.hc=hc
        self.warning=warning

    def run(self,processor,memo):

        # FIXME: Check against full result
        # FIXME: names not consistent in memo
        # FIXME: too much repacking
        results = (self.param_vector,self.func,self.iter,self.fc,self.gc,self.hc, self.warning)
        memo.add_result(results)

        sgm =  memo.super_grid_memo

        print_prefix  = sgm.print_prefix
        verbosity  = sgm.verbosity
        full_output = sgm.full_output
        A = sgm.A
        b = sgm.b
        grid_size = sgm.grid_size



        if sgm.first_time:


            print
            print "Unconstrained grid search size: " + `grid_size` + " (constraints may decrease this size).\n"

            if verbosity:
                if verbosity >= 2:
                    print print_prefix
                print print_prefix
                print print_prefix + "Grid search"
                print print_prefix + "~~~~~~~~~~~"

            # Linear constraints.
            if A != None and b != None:
                if verbosity >= 3:
                    print print_prefix + "Linear constraint matrices."
                    print print_prefix + "A: " + `A`
                    print print_prefix + "b: " + `b`

        # we don't want to prepend the masters stdout tag
        sys.__stdout__.write('\n'+self.result_string),


        if sgm.completed:


            if verbosity and results != None:
                if full_output:
                    print ''
                    print ''
                    print print_prefix + "Parameter values: " + `sgm.xk`
                    print print_prefix + "Function value:   " + `sgm.fk`
                    print print_prefix + "Iterations:       " + `sgm.k`
                    print print_prefix + "Function calls:   " + `sgm.f_count`
                    print print_prefix + "Gradient calls:   " + `sgm.g_count`
                    print print_prefix + "Hessian calls:    " + `sgm.h_count`
                    if sgm.warning:
                        print print_prefix + "Warning:          " + sgm.warning
                    else:
                        print print_prefix + "Warning:          None"
                else:
                    print print_prefix + "Parameter values: " + `sgm.short_results`
                print ""




            m_f=sgm.model_free
            m_f.iter_count = 0
            m_f.f_count = 0
            m_f.g_count = 0
            m_f.h_count = 0
            #raise Exception()
            m_f.disassemble_result(param_vector=sgm.xk,func=sgm.fk,iter=sgm.k,fc=sgm.f_count,
                                   gc=sgm.g_count,hc=sgm.h_count, warning=sgm.warning,
                                   run=sgm.run, index=sgm.index, sim_index=sgm.sim_index,
                                   param_set=sgm.param_set, scaling=sgm.scaling, scaling_matrix=sgm.scaling_matrix)
