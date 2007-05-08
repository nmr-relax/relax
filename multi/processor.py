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

'''  The processor class is the central class in the multi python multiprocessor framework.

     Overview
     --------

     The framework has two main responsibilities

         1. process management - if needed the processor can create the slave processes it
            manages if they haven't been created by the operating system. It is also reponsible for
            reporting exceptions and shutting down the multiprocessor in the face of errors.

         2. sheduling commands on the slave processors via an interprocess communication fabric (MPI,
            PVM, threads etc) and processing returned text and result
            commands


     Using the processor framework
     -----------------------------

     users of the processor framework will typically use the following methodoloy:

         1. at application startup determine the name of the required processor implimentation a
            and  the number of slave processors requested
         2. create an Application_callback object
         3. dynamically load a processor implimentation using the name of the processor and the
            number of required slave processors using

            >>>
            processor = Processor.load_multiprocessor(relax_instance.multiprocessor_type,
                              callbacks, processor_size=relax_instance.n_processors)
         4. call run on the processor instance resturned above and handle all Exceptions
         5. after calling run the processor will call back to Application_callback.init_master from
            which you should call you main program (Application_callback defaults to
            self.master.run())
         5. once in the main program you should call processor.add_to_queue with a series of
            multi.Slave_command objects you wish to be run across the slave processor pool and then
            call processor.run_queue to actually execute the commands remotely while blocking.
            >>>
            example here...

         6. processor.Slave_commands will then run remotely on the slaves and any thrown exceptions
            and processor.result_commands queued to processor.return_object will be returned to the
            master processor and handled or executed. The slave processors also provide facilities
            for capturing the stderr and stdout streams and returning their contents as strings for
            display on the masters stout and stderr streams (***more**?)

    Extending the processor framework with a new interprocess communication fabric
    ------------------------------------------------------------------------------

     The processor class acts as a base class that defines all the commands that a processor
     implimenting a new inter processo communication fabric needs. All that is required is to
     impliment a subclass of processor providing the required methods (of course as python provides
     dynamic typing and polymorphism 'duck typing' you can always impliment a class with the same
     set of method and it will also work). Currnently processor classes are loaded from the
     processor module and are modules with names of the form:
     >>> multi.<type>_processor.<Type>_processor

     where <Type> is the name of the processor with the correct capitalisation e.g.

     >>>
     processor_name =  'mpi4py'
     callback = My_application-callback()
     proccesor_size=6
     processor.load_multiprocessor(processor_name, callback, processor_size):

     will load multi.mpi4py_processor.Mpi4py_Processor

     todo
     ----

     1. there is no ability of the processor to request command line arguments
     2. the processor can't currently be loaded from somewhere other than the multi directory

'''

def import_module(module_path, verbose=False):
    ''' import the python module named by module_path

        @type module_path: a string containing a dot separated module path
        @param module_path: a module path in python dot separated format
                            note: this currently doesn't support relative module
                            paths as defined by pep328 and python 2.5

        @type verbose: Boolean
        @param verbose: whether to report sucesses and failures for debugging

        @rtype:     list of class module instances or None
        @return:    the module path as a list of module instances or None
                    if the module path cannot be found in the python path

        '''

    result = None

    #try:
    module = __import__(module_path,globals(),  locals(), [])
    if verbose:
        print 'loaded module %s' % module_path
    #except Exception, e:
    #    if verbose:
    #        print 'failed to load module_path %s' % module_path
    #        print 'exception:',e

    #FIXME: needs more failure checking
    if module != None:
        result = [module]
        components = module_path.split('.')
        for component in components[1:]:
            module = getattr(module, component)
            result.append(module)
    return result

#FIXME: mode not required should be an instance variable of relax?
#FIXME error checking for if module require not found
#FIXME move module loading to processor
#FIXME module loading code needs to be in a util module
def load_multiprocessor(processor_name, callback, processor_size):

    processor_name =  processor_name + '_processor'
    class_name= processor_name[0].upper() + processor_name[1:]
    module_path = '.'.join(('multi',processor_name))


    modules = import_module(module_path)
    #print modules

    if hasattr(modules[-1],class_name):
        clazz =  getattr(modules[-1], class_name)
    else:
        raise Exception("can't load class %s from module %s" % (class_name,module_path))

    object = clazz(callback=callback,processor_size=processor_size)
    return object
# FIXME better  requirement of inherited commands
# TODO: check exceptiosn on master
import time,datetime,math,sys,os
import traceback,textwrap
from  multi.prependStringIO import PrependStringIO,PrependOut

#FIXME: move elsewhere
def traceit(frame, event, arg):
    import linecache
    if event == "line":
        file_name = os.path.split(frame.f_code.co_filename)[-1]
        function_name = frame.f_code.co_name
        line_number = frame.f_lineno
        line = linecache.getline(file_name, line_number)
        msg = '<< %s - %s - %d>> %s'  %(file_name,function_name,line_number, line[:-1])
        print >> sys.__stdout__, msg

    return traceit


#sys.settrace(traceit)
# FIXME useful debugging code but where to put it
def print_file_lineno(range=xrange(1,2)):


    for level in range:
        print '<< ', level,
        try:
            file_name = sys._getframe(level).f_code.co_filename
            function_name = sys._getframe(level).f_code.co_name
            line_number = sys._getframe(level).f_lineno
            msg = ': %s - %s - %d>>'  %(file_name,function_name,line_number)
            print msg
        except Exception, e:
            print e
            break
    #FIXME: useful for debugging but where to put it
    def print_message(processor,message):
        f=open ('error' + `processor.rank()` + '.txt','a')
        f.write(message+'\n')
        f.flush()
        f.close()

class Application_callback(object):
    ''' call backs provided to the host application by the multi processor framework. This class
        allows for independance from the host class/application.
    '''
    def __init__(self,master):
        '''  initialise the callback interface
             @type master: object
             @param master: the data for the host application. In the default implimentation this is
                            an object we call methods on but it could be anything...
        '''
        self.master=master
        self.init_master = self.default_init_master
        self.handle_exception= self.default_handle_exception

    def default_init_master(self,processor):
        ''' start the main loop of the host application.

             the processor framework
        '''
        self.master.run()

    def default_handle_exception(self,processor,exception):
        ''' handle an exception rased int eh processor framework'''
        #TODO: could do with flag to force __stdout__ vs  stdout
        traceback.print_exc(file=sys.__stdout__)
        processor.abort()


def raise_unimplimented(method):
    msg = "Attempt to invoke unimplemented abstract method %s"
    raise NotImplementedError(msg % method.__name__)

#requires 2.4 decorators@abstract
#def abstract(f):
#    raise_unimplimented(f)

#    return f

class Processor(object):

    #FIXME: remname chunk* grain*
    def __init__(self,processor_size,callback, stdio_capture=None):
        self.callback=callback
        self.chunkyness=1
        self.pre_queue_command=None
        self.post_queue_command=None
        self.NULL_RESULT=Null_result_command(processor=self)
        self._processor_size=processor_size


        self.setup_stdio_capture(stdio_capture)

    load_multiprocessor = staticmethod(load_multiprocessor)

    def add_to_queue(self,command,memo=None):
         raise_unimplimented(self.add_to_queue)

    def run_queue(self):
        raise_unimplimented(self.run_queue)

    def run(self):
        raise_unimplimented(self.run)

    def return_object(self,result):
        raise_unimplimented(self.return_object)

    def get_name(self):
        raise_unimplimented(self.get_name)

    def abort(self):
        sys.exit()

    # FIXME is this used?
#    def exit(self):
#        raise_unimplimented(self.exit)



    def rank(self):
        raise_unimplimented(self.rank)

    def processor_size(self):
        return self._processor_size

    def get_intro_string(self):
        raise_unimplimented(self.get_intro_string)


#    def restore_stdio(self):
#        sys.stderr = self.save_stderr
#        sys.stdout = self.save_stdout

    def run_command_globally(self,command):
        queue = [command for i in range(self.processor_size())]
        self.run_command_queue(queue)


    def pre_run(self):
        if self.rank() == 0:
            self.start_time =  time.time()


    def get_time_delta(self,start_time,end_time):

        time_diff= end_time - start_time
        time_delta = datetime.timedelta(seconds=time_diff)
        time_delta_str = time_delta.__str__()
        (time_delta_str,millis) = time_delta_str.split('.',1)
        return time_delta_str

    def post_run(self):
        if self.rank() == 0:
            end_time = time.time()
            time_delta_str = self.get_time_delta(self.start_time,end_time)
            print 'overall runtime: ' + time_delta_str + '\n'



    def rank_format_string_width(self):
        return int(math.ceil(math.log10(self.processor_size())))

    def rank_format_string(self):
        digits  = self.rank_format_string_width()
        format = '%%%di' % digits
        return format

    def setup_stdio_capture(self,stdio_capture=None):

        rank =self.rank()
        pre_strings=('','')

        if stdio_capture==None:
            pre_strings = self.get_stdio_pre_strings(rank)
            stdio_capture=self.std_stdio_capture(pre_strings=pre_strings)

        self.stdio_capture=stdio_capture


    def std_stdio_capture(self,rank=0,pre_strings=None):
            if pre_strings == None:
                pre_strings=('','')

            stdout_capture = None
            stderr_capture = None

            if self.rank() ==0:
                stdout_capture = PrependOut(pre_strings[0], sys.stdout)
                #FIXME: seems to be that writing to stderr results leeds to incorrect serialisation of output
                stderr_capture = PrependOut(pre_strings[1], sys.__stdout__)
            else:
                stdout_capture = PrependStringIO(pre_strings[0])
                stderr_capture = PrependStringIO(pre_strings[1],target_stream=stdout_capture)


            return (stdout_capture,stderr_capture)

    def capture_stdio(self,stdio_capture=None):

        if stdio_capture  == None:
            stdio_capture=self.stdio_capture

        sys.stdout = self.stdio_capture[0]
        sys.stderr = self.stdio_capture[1]

    def get_stdio_capture(self):
        return self.stdio_capture

    def restore_stdio(self):
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__

    def get_stdio_pre_strings(self,rank=0):
        pre_string =''
        stdout_string = ''
        stderr_string = ''

        if self.processor_size() > 1 and rank > 0:
            pre_string = self.rank_format_string() % self.rank()
        elif self.processor_size() > 1 and rank == 0:
            pre_string = 'M'*self.rank_format_string_width()

        if self.processor_size() > 1:
            stderr_string  =  pre_string + ' E> '
            stdout_string  =  pre_string + ' S> '

        return (stdout_string,stderr_string)

class Result(object):
    def __init__(self,processor,completed):
        self.completed=completed
        self.memo_id=None
        self.rank = processor.rank()


class Result_string(Result):
    #FIXME move result up a level
    def __init__(self,processor,string,completed):
        super(Result_string,self).__init__(processor=processor,completed=completed)
        self.string=string


class Result_command(Result):
    def __init__(self,processor,completed,memo_id=None):
        super(Result_command,self).__init__(processor=processor,completed=completed)
        self.memo_id=memo_id


    def run(self,processor,memo):
        pass

class Null_result_command(Result_command):
    def __init__(self,processor,completed=True):
        super(Null_result_command,self).__init__(processor=processor,completed=completed)



class Result_exception(Result_command):
    def __init__(self,processor,exception,completed=True):
        super(Result_exception,self).__init__(processor=processor,completed=completed)
        self.exception=exception

    def run(self,processor,memos):
        raise self.exception


class Slave_command(object):
    def __init__(self):
        self.memo_id=None

    def set_memo_id(self,memo):
        if memo != None:
            self.memo_id = memo.memo_id()
        else:
            self.memo_id=None

    def run(self,processor,completed):
        pass



class Memo(object):
    def memo_id(self):
        return id(self)



class Capturing_exception(Exception):
    def __init__(self,exc_info=None, rank='unknown', name='unknown'):
        Exception.__init__(self)
        self.rank=rank
        self.name=name
        if exc_info == None:
            (exception_type,exception_instance,exception_traceback)=sys.exc_info()
        else:
            (exception_type,exception_instance,exception_traceback)=exc_info
        #PY3K: this check can be removed once string based exceptions are no longer used
    	if type(exception_type) ==  str:
                self.exception_name = exception_type + ' (legacy string exception)'
                self.exception_string=exception_type
        else:
            self.exception_name =  exception_type.__name__
            self.exception_string = exception_instance.__str__()

        self.traceback = traceback.format_tb(exception_traceback)

    def __str__(self):
        message ='''

                     %s

                     %s

                     Nested Exception from sub processor
                     Rank: %s  Name: %s
                     Exception type: %s
                     Message: %s

                     %s


                 '''
        message = textwrap.dedent(message)
        result =  message % ('-'*120, ''.join(self.traceback) ,self.rank, self.name, self.exception_name,
                             self.exception_string, '-'*120)
        return result


