#!/usr/bin/env python

#TODO clone communicators & resize
import sys
import os
import math
import time,datetime

from multi.processor import Memo,Slave_command
from multi.processor import Result_command,Result_string

#FIXME: me move top generic command module
from maths_fns.mf import Mf
from minimise.generic import generic_minimise

# load mpi
try:
    from  mpi4py import MPI
except ImportError:
    sys.stderr.write("The dependency 'mpi4py' has not been installed.\n")
    sys.exit()

# save original sys.exit to call after wrapper
if MPI.rank == 0:
    _sys_exit =  sys.exit


def rank_format_string():
    digits  = math.ceil(math.log10(MPI.size))
    format = '%%%di' % digits
    return format

RANK_FORMAT_STRING = rank_format_string

# wrapper sys.exit function
def exit(status=None):

    exit_mpi()
    _sys_exit(status)

def broadcast_command(command):
    for i in range(1,MPI.size):
        if i != 0:
            MPI.COMM_WORLD.Send(buf=command,dest=i)

def ditch_all_results():
    for i in range(1,MPI.size):
        if i != 0:
            while 1:
                result = MPI.COMM_WORLD.Recv(source=i)
                if result.completed:
                    break
def exit_mpi():
    if MPI.Is_initialized() and not MPI.Is_finalized() and MPI.rank == 0:
        broadcast_command(Exit_command())
        ditch_all_results()




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
        super(MF_completion_command,self).__init__(True,memo_id=memo_id)
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

#FIXME do some inheritance
class Mpi4py_processor:



    def __init__(self,relax_instance):
        self.relax_instance= relax_instance

        # wrap sys.exit to close down mpi before exiting
        sys.exit= exit
        self.do_quit=False

        #FIXME un clone from uniprocessor
        #command queue and memo queue
        self.command_queue=[]
        self.memo_map={}

    def add_to_queue(self,command,memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()]=memo

    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states
         self.run_command_queue(self.command_queue)
         del self.command_queue[:]
         self.memo_map.clear()

    def assert_on_master(self):
        if MPI.rank != 0:
            msg = 'running on slave when expected master with MPI.rank == 0, rank was %d'% MPI.rank
            raise Exception(msg)


    def get_name(self):
        return '%s-%s' % (MPI.Get_processor_name(),os.getpid())

    def exit(self):
        exit_mpi()

    def return_object(self,result):
        result.rank=MPI.rank
        MPI.COMM_WORLD.Send(buf=result, dest=0)


#    def process_commands(self,commands):
#        self.assert_on_master()
#
#        for i in range(1,MPI.size):
#            MPI.COMM_WORLD.Send(buf=command,dest=i)

    def run_command_globally(self,command):
        queue = [command for i in range(1,MPI.size)]
        self.run_command_queue(queue)

    def run_command_queue(self,queue):
        self.assert_on_master()

#        for i in range(1,MPI.size):
#                MPI.COMM_WORLD.Send(buf=command,dest=i)
#        for i in range(1,MPI.size):
#            elem = MPI.COMM_WORLD.Recv(source=i)
#            if type(elem) == 'object':
#                elem.run(relax_instance, relax_instance.processor)
#            else:
#                #FIXME can't cope with multiple lines
#                print i,elem
        #queue = [command for i in range(1,MPI.size*2)]
        running_set=set()
        idle_set=set([i for i in range(1,MPI.size)])

        while len(queue) != 0:

            while len(idle_set) != 0:
                if len(queue) != 0:
                    command = queue.pop()
                    dest=idle_set.pop()
                    MPI.COMM_WORLD.Send(buf=command,dest=dest)
                    running_set.add(dest)
                else:
                    break


            while len(running_set) !=0:
                result = MPI.COMM_WORLD.Recv(source=MPI.ANY_SOURCE)
                if isinstance(result, Exception):
                    #FIXME: clear command queue
                    #       and finalise mpi (or restart it if we can!
                    raise result

                if isinstance(result, Result):
                    if result.completed:
                        idle_set.add(result.rank)
                        running_set.remove(result.rank)

                    if isinstance(result, Result_command):
                        memo=None
                        if result.memo_id != None:
                            memo=self.memo_map[result.memo_id]
                        result.run(self.relax_instance,self,memo)
                        if result.memo_id != None and result.completed:
                            del self.memo_map[result.memo_id]

                    elif isinstance(result, Result_string):
                        #FIXME can't cope with multiple lines
                        print result.rank,result.string
                    else:
                        message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__,result)
                        raise Exception(message)


#        for i in range(MPI.size):
#            buf=[]
#            if i !=0:
#                print 'try',i
#                MPI.COMM_WORLD.Recv(buf=buf, source=i)
#                for i,elem in enumerate(buf):
#                    if elem.type!='object':
#                        print i,elem
#                    else:
#                        elem.run()

    def run(self):

#        if MPI.rank == 0:
#            self.relax_instance.multi_mode='multi_master'
#        else:
#            self.relax_instance.multi_mode='multi_slave'
#            self.relax_instance.mode='slave'
#            self.relax_instance.script_file=None
#            self.relax_instance.dummy_mode=True
#            #self.relax_instance.run()


        if MPI.rank ==0:
            start_time =  time.time()
            self.relax_instance.run()
            end_time = time.time()
            time_diff= end_time - start_time
            time_delta = datetime.timedelta(seconds=time_diff)
            sys.stderr.write('overall runtime: ' + time_delta.__str__() + '\n')
            sys.stderr.flush()
            # note this a mdofied exit that kills all MPI processors
            sys.exit()
        else:
            #self.relax_instance.run(deamon=True)
            while not self.do_quit:
                command = MPI.COMM_WORLD.Recv(source=0)
                try:
                    command.run(self)
                except Exception,e:
                    self.return_object(e)



            #if data=='close':
            #    exit_mpi()
            #    return




if __name__ == '__main__':
    test = Mpi4py_processor(None)
    print test
    print MPI.rank