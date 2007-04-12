################################################################################
#                                                                              #
# Copyright (C) 2007  Gary S Thompson (see https://gna.org/users/varioustoxins #
#                                      for contact details)                    #
#                                                                              #
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
from  multi.PrependStringIO import PrependStringIO

from multi.processor import Memo,Slave_command
from multi.processor import Result_command,Result_string,NULL_RESULT
from re import match

from maths_fns.mf import Mf
from minimise.generic import generic_minimise

import sys

class Exit_command(Slave_command):
    def __init__(self):
        super(Exit_command,self).__init__()

    def run(self,processor,completed):
        processor.return_object(NULL_RESULT)
        processor.do_quit=True



class Get_name_command(Slave_command):
    def __init__(self):
        super(Exit_command,self).__init__()

    def run(self,processor,completed):
        msg = processor.get_name()
        result = Result_string(msg,completed)
        processor.return_object(result)



#not quite a momento so a memo
class MF_memo(Memo):
    def __init__(self,model_free,index,sim_index,run,param_set,scaling,scaling_matrix):
        super(MF_memo,self).__init__()
        self.index = index
        self.sim_index=sim_index
        self.run=run
        self.param_set=param_set
        self.model_free=model_free
        self.scaling=scaling
        self.scaling_matrix=scaling_matrix

OFFSET_XK=0
OFFSET_FK=1
OFFSET_K=2
OFFSET_F_COUNT=3
OFFSET_G_COUNT=4
OFFSET_H_COUNT=5
OFFSET_WARNING=6

OFFSET_SHORT_MIN_PARAMS=0
OFFSET_SHORT_FK=1
OFFSET_SHORT_K=2



class MF_result_command(Result_command):
    def __init__(self,memo_id,param_vector, func, iter, fc, gc, hc, warning,completed):
        super(MF_result_command,self).__init__(completed=completed)
        self.memo_id=memo_id
        self.param_vector=param_vector
        self.func=func
        self.iter=iter
        self.fc=fc
        self.gc=gc
        self.hc=hc
        self.warning=warning

    def run(self,relax,processor,memo):
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
                     'dc':None, 'd2c':None, 'full_output':0, 'print_flag':0,
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
        # Print out.
        #print_flag,param_set,residue_num,residue_name,min_algor,grid_size=None
        m_m=self.minimise_map
        m_f=self.mf_map
        i_m=self.info_map
#        print 'minimising...' + i_m['res_id'] + ' '+  `i_m['index']` + ' ' + `i_m['sim_index']` + ' ' + m_f['param_set'] + ' '  + `m_m['print_flag']`
#        sys.stdout.flush())
        if m_m['print_flag'] >= 1:
            # montecarlo stuff
            if i_m['sim_index'] != None and i_m['index'] == 0:
                print 'Simulation '+ `i_m['sim_index']`+ '\n'
            # Individual residue stuff.
            if m_f['param_set'] == 'mf' or m_f['param_set'] == 'local_tm':
                if m_m['print_flag'] >= 2:
                    print "\n\n"
                string = "Fitting to residue: " + i_m['res_id']
                print "\n\n" + string
                print len(string) * '~'
            if match('^[Gg]rid', m_m['min_algor']):
                print "Unconstrained grid search size: " + `i_m['grid_size']` + " (constraints may decrease this size).\n"

    def process_results(self,results,processor,completed):
        param_vector, func, iter, fc, gc, hc, warning = results

        result_string = sys.stdout.getvalue() + sys.stderr.getvalue()
        processor.return_object(Result_string(result_string,completed=False))
        processor.return_object(MF_result_command(self.memo_id,param_vector, func, iter, fc, gc, hc, warning,completed=completed))

    def run(self,processor, completed):

        #FIXME: move to processor startup
        save_stdout = sys.stdout
        save_stderr = sys.stderr
        pre_string = processor.rank_format_string() % processor.rank()
        # add debug flag or extra channels that output immediately
        sys.stdout = PrependStringIO(pre_string + ' S> ')
        sys.stderr = PrependStringIO(pre_string + ' E> ')

        self.mf = self.build_mf()


        self.do_feedback()
        results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, **self.minimise_map)
        self.process_results(results,processor,completed)

        #FIXME: move to processor startup
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = save_stdout
        sys.stderr = save_stderr

class MF_grid_command(MF_minimise_command):
    def __init__(self):
        super(MF_grid_command,self).__init__()

    def process_results(self,results,processor,completed):
        param_vector, func, iter, fc, gc, hc, warning = results

        result_string = sys.stdout.getvalue() + sys.stderr.getvalue()
        processor.return_object(Result_string(result_string,completed=False))
        processor.return_object(MF_grid_result_command(self.memo_id,param_vector, func, iter, fc, gc, hc, warning,completed=completed))

def MF_grid_memo(memo):
    def __init__(self,super_grid_memo):
        super(MF_grid_memo,self).__init__()
        self.super_grid_memo = super_grid_memo


    def add_results(self,results):
        self.super_grid_memo.add_result(results)

class MF_super_grid_memo(MF_memo):
    def __init__(self,model_free,index,sim_index,run,param_set,scaling,scaling_matrix):
        super(MF_super_grid_memo,self).__init__(model_free,index,sim_index,run,param_set,scaling,scaling_matrix)
        self.sub_memos = []
        self.completed = False

        # aggregated results
        #             min_params, f_min, k
        short_result=[None, None, 0]
        self.xk = None
        self.fk = None
        self.k = 0
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0
        self.warning = []




    def add_sub_memo(self):
        self.sub_memos.append(memo)

    def add_result(self,sub_memo,results,full_output):
        if full_output:
            if results[OFFSET_FK] < self.fk:
                self.xk = results[OFFSET_XK]
                self.fk = results[OFFSET_FK]
                self.k += results[OFFSET_K]
                self.f_count += results[OFFSET_F_COUNT]
                self.g_count += results[OFFSET_G_COUNT]
                self.h_count += results[OFFSET_H_COUNT]
                self.warning.append(results[WARNING_OFFSET])

        else:
            if results[OFFSET_SHORT_FK] < short_result[OFFSET_SHORT_FK]:
                self.short_result[OFFSET_SHORT_MIN_PARAMS] = results[OFFSET_SHORT_MIN_PARAMS]
                self.short_result[OFFSET_SHORT_FK] = results[OFFSET_SHORT_FK]
                self.short_result[OFFSET_SHORT_K] += results[OFFSET_SHORT_K]
        self.sub_memos.remove(sub_memo)

        if len(self.sub_memos) < 1:
            self.completed = True

class MF_grid_result_command(Result_command):
    def __init__(self,memo_id,param_vector, func, iter, fc, gc, hc, warning,completed):
        super(MF_grid_result_command,self).__init__(completed=completed)
        self.memo_id=memo_id
        self.param_vector=param_vector
        self.func=func
        self.iter=iter
        self.fc=fc
        self.gc=gc
        self.hc=hc
        self.warning=warning

    def run(self,relax,processor,memo):

        # FIXME: Check against full result
        # FIXME: names not consistent in memo
        # FIXME too much repacking
        results = (self.param_vector,self.func,self.iter,self.fc,self.gc,self.hc, self.warning)
        memo.add_result(results,full_result=True)

        sgm =  memo.super_grid_memo
        if sgm.completed:



            m_f=memo.model_free
            m_f.iter_count = 0
            m_f.f_count = 0
            m_f.g_count = 0
            m_f.h_count = 0
            #raise Exception()
            m_f.disassemble_result(param_vector=sgm.xk,func=sgm.fk,iter=sgm.k,fc=sgm.fc,
                                   gc=sgm.gc,hc=sgm.hc, warning=sgm.warning,
                                   run=memo.run, index=memo.index, sim_index=memo.sim_index,
                                   param_set=memo.param_set, scaling=memo.scaling, scaling_matrix=memo.scaling_matrix)
