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

from multi.processor import Memo,Slave_command
from multi.processor import Result_command,Result_string,NULL_RESULT
from re import match

from maths_fns.mf import Mf
from minimise.generic import generic_minimise

class Exit_command(Slave_command):
    def __init__(self):
        super(Exit_command,self).__init__()

    def run(self,processor):
        processor.return_object(NULL_RESULT)
        processor.do_quit=True



class Get_name_command(Slave_command):
    def __init__(self):
        super(Exit_command,self).__init__()

    def run(self,processor):
        msg = processor.get_name()
        result = Result_string(msg,True)
        processor.return_object(result)

#not quite a momento so a memo
class MF_memo(Memo):
    def __init__(self,model_free,index,sim_index,run,param_set,scaling):
        super(MF_memo,self).__init__()
        self.index = index
        self.sim_index=sim_index
        self.run=run
        self.param_set=param_set
        self.model_free=model_free
        self.scaling=scaling


class MF_result_command(Result_command):
    def __init__(self,memo_id,param_vector, func, iter, fc, gc, hc, warning):
        super(MF_result_command,self).__init__(completed=True,memo_id=memo_id)
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
        m_f.disassemble_result(param_vector=self.param_vector,func=self.func,iter=self.iter,fc=self.fc,
                               gc=self.gc,hc=self.hc, warning=self.warning,
                               run=memo.run, index=memo.index,sim_index=memo.sim_index,
                               param_set=memo.param_set,scaling=memo.scaling)


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
        # note the creation of a dict prevents a bug in python 2.3.3  where
        # it complains update doesn't take keywords
        self.mf_map.update(kwargs)


    def set_minimise(self,**kwargs):
        print kwargs
        if 'res_id' in kwargs:
           self.info_map['res_id']= kwargs['res_id']
           del kwargs['res_id']
        if 'grid_size' in kwargs:
           self.info_map['grid_size']= kwargs['grid_size']
           del kwargs['grid_size']
        # note the creation of a dict prevents a bug in python 2.3.3  where
        # it complains update doesn't take keywords
        self.minimise_map.update(kwargs)

    def build_mf(self):
        return  Mf(**self.mf_map)

    def do_minimise(self,memo):

        self.mf = self.build_mf()
        results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, **self.minimise_map)

        m_f=memo.model_free
        param_vector, func, iter, fc, gc, hc, warning = results
        m_f.disassemble_result(param_vector=param_vector,func=func,iter=iter,fc=fc,
                               gc=gc,hc=hc, warning=warning,
                               run=memo.run, index=memo.index,sim_index=memo.sim_index,
                               param_set=memo.param_set,scaling=memo.scaling)

    def do_feedback(self):
        # Print out.
        #print_flag,param_set,residue_num,residue_name,min_algor,grid_size=None
        m_m=self.minimise_map
        m_f=self.mf_map
        i_m=self.info_map
        if m_m['print_flag'] >= 1:
            # Individual residue stuff.
            if m_f['param_set'] == 'mf' or m_f['param_set'] == 'local_tm':
                if m_m['print_flag'] >= 2:
                    print "\n\n"
                string = "Fitting to residue: " + i_m['res_id']
                print "\n\n" + string
                print len(string) * '~'
            if match('^[Gg]rid', m_m['min_algor']):
                print "Unconstrained grid search size: " + `i_m['grid_size']` + " (constraints may decrease this size).\n"

    def run(self,processor):
        self.mf = self.build_mf()


        self.do_feedback()
        results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, **self.minimise_map)
        param_vector, func, iter, fc, gc, hc, warning = results

        processor.return_object(MF_result_command(self.memo_id,param_vector, func, iter, fc, gc, hc, warning))

