
from multi.processor import Memo,Slave_command
from multi.processor import Result_command,Result_string,NULL_RESULT

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

#not quit a momento so a memo
class MF_completion_memo(Memo):
    def __init__(self,model_free,index,sim_index,run,param_set,scaling):
        self.index = index
        self.sim_index=sim_index
        self.run=run
        self.param_set=param_set
        self.model_free=model_free
        self.scaling=scaling


class MF_completion_command(Result_command):
    def __init__(self,memo_id,param_vector, func, iter, fc, gc, hc, warning):
        super(MF_completion_command,self).__init__(completed=True,memo_id=memo_id)
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


    #FIXME: bad names
    def set_mf(self, **kwargs):
        self.mf_map.update(**kwargs)


    def set_minimise(self,**kwargs):
        self.minimise_map.update(**kwargs)

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
    def run(self,processor):
        self.mf = self.build_mf()
        results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, **self.minimise_map)
        param_vector, func, iter, fc, gc, hc, warning = results

        processor.return_object(MF_completion_command(self.memo_id,param_vector, func, iter, fc, gc, hc, warning))

