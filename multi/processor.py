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
'''The processor class is the central class in the multi python multiprocessor framework.

Overview
========

The framework has two main responsibilities:

     1. Process management - if needed the processor can create the slave processes it manages if
        they haven't been created by the operating system. It is also responsible for reporting
        exceptions and shutting down the multiprocessor in the face of errors.
     2. Scheduling commands on the slave processors via an interprocess communication fabric (MPI,
        PVM, threads etc) and processing returned text and result commands.


Using the processor framework
=============================

Users of the processor framework will typically use the following methodology:

     1. At application startup determine the name of the required processor implementation and the
        number of slave processors requested.

     2. Create an Application_callback object.

     3. Dynamically load a processor implementation using the name of the processor and the number
        of required slave processors using:
            processor = Processor.load_multiprocessor(relax_instance.multiprocessor_type,
                    callbacks, processor_size=relax_instance.n_processors)

     4. Call run on the processor instance returned above and handle all Exceptions.

     5. After calling run, the processor will call back to Application_callback.init_master from
        which you should call you main program (Application_callback defaults to self.master.run()).

     6. Once in the main program you should call processor.add_to_queue with a series of
        multi.Slave_command objects you wish to be run across the slave processor pool and then call
        processor.run_queue to actually execute the commands remotely while blocking.
        >>>
        example here...

     7. Processor.Slave_commands will then run remotely on the slaves and any thrown exceptions and
        processor.result_commands queued to processor.return_object will be returned to the master
        processor and handled or executed. The slave processors also provide facilities for capturing
        the STDERR and STDOUT streams and returning their contents as strings for display on the
        master's STDOUT and STDERR streams (***more**?).


Extending the processor framework with a new interprocess communication fabric
==============================================================================

The processor class acts as a base class that defines all the commands that a processor implementing
a new inter processor communication fabric needs. All that is required is to implement a subclass of
processor providing the required methods (of course as python provides dynamic typing and
polymorphism 'duck typing' you can always implement a class with the same set of method and it will
also work). Currently processor classes are loaded from the processor module and are modules with
names of the form:

>>> multi.<type>_processor.<Type>_processor

where <Type> is the name of the processor with the correct capitalisation e.g.

>>> processor_name =  'mpi4py'
>>> callback = My_application-callback()
>>> proccesor_size=6
>>> processor.load_multiprocessor(processor_name, callback, processor_size)

will load multi.mpi4py_processor.Mpi4py_Processor.


TODO
====

The following are yet to be implemented:

    1. There is no ability of the processor to request command line arguments.

    2. The processor can't currently be loaded from somewhere other than the multi directory.

'''

#FIXME: better  requirement of inherited commands
# TODO: check exceptiosn on master
import time,datetime,math,sys,os
import traceback,textwrap
from  multi.prependStringIO import PrependStringIO,PrependOut

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


#FIXME error checking for if module required not found
#FIXME module loading code needs to be in a util module
#FIXME: remove parameters that are not required to load the module (processor_size)
def load_multiprocessor(processor_name, callback, processor_size):
    ''' load a multi processor given its name

        dynamically load a multi processor, the current algorithm is to search in module multi for
        a module called <prcoessor_name>.<Processor_name> (note capiltalisation).

        @todo: This algorithm needs to be improved to allow users to load processors without
               altering the relax source code.

        @todo: remove unrequired parameters

        @type processor_name: String
        @param processor_name: name of the prcoessor module/class to load

        @rtype: object of type  multi.processor.Processor
        @return: a loaded processor object or none to indicate failure

    '''

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

        @note: B{The logic behind the design} the callbacks are defined as two attributes
               self.init_master and self.handle_exception as handle_exception can be null (which
               is used to request the use of the processors default error handling code). Note,
               however, that a class with the equivalent methods would also works as python
               effectivley handles methods as attributes of a class. The signatures for the callback
               methods are documented by the default methods default_init_master &
               default_handle_exception
    '''
    def __init__(self,master):
        '''  initialise the callback interface
             @type master: object
             @param master: the data for the host application. In the default implimentation this is
                            an object we call methods on but it could be anything...
        '''

        self.master=master
        ''' the hst applocation'''

        self.init_master = self.default_init_master
        self.handle_exception= self.default_handle_exception

    def default_init_master(self,processor):
        ''' start the main loop of the host application.

            @type processor: instance of multi.processor.Processor
            @param processor: the processor instance
        '''
        self.master.run()

    def default_handle_exception(self,processor,exception):
        ''' handle an exception rased int the processor framework, the function is reponsible for
            aborting the processor by calling processor.abort() as its final act.
            @type processor: instance of multi.processor.Processor
            @param processor: the processor instance

            @param exception: the exception raised by the processor or slave processor. In the case
            of a slave processor exception this may well be a wrapped exception of type
            multi.processor.Capturing_exception which was raised at the point the exception was
            recieved on the master processor but contains an enclosed exception from a slave.

        '''
        #TODO: should use stderr?
        # note we print to __stdout__ as sys.stdout may be a wrapper we applied
        traceback.print_exc(file=sys.__stdout__)
        processor.abort()

#requires 2.4 decorators@abstract
#def abstract(f):
#    raise_unimplimented(f)

#    return f

def raise_unimplimented(method):
    ''' standard function to raise an NotImplementedError exception for an unimplimented abstract
        methods.

        @todo: for python versions >= 2.4 it is possible to use annotations and meta classes to
               provide a very elegant implimentation of abstract methods that check on class
               instantiation that the derived class is a complete implimentation of the abstract
               class. Note some people think abstract classes shouldn't be used with python,
               however. they are proposed for python 3k by Guido van Rossum in pep3119 ;-)

        @see: http://soiland.no/blog/py/abstract
        @see: http://www.python.org/dev/peps/pep-3119

        @param method: the method which should be abstract
        @type method: method (i.e. a function bound to a class)

        @raise NotImplementedError:  a not implimented exception with the method name as a parameter
    '''

    msg = "Attempt to invoke unimplemented abstract method %s"
    raise NotImplementedError(msg % method.__name__)


class Processor(object):
    ''' the central class of the multi prcoessor framework which provides facilities for process
        management, command queueing, command sheduling, remote execution of commands, and handling
        of results and error from commands. The class is abstract and should be overridden to
        impliment new interprocess communication methods, however, even then users are encouraged to
        override the more full implimented multi.multi_processor.Multi_processor class. Most users
        should instantiate instances of this class by calling the static method
        Processor.load_multiprocessor.

        The class is designed top be subclassed and has abstract methods that a subclass needs to
        override. Methods which can be overridded are clearly marked with a note annotation stating
        that they can be overriden

        @todo: it maybe a good idea to separate out the features of the class that purely deal with
               the interprocess communication fabric
        @todo: the processor can't currently harvest the required command line arguments from the
               current command line
    '''

    def __init__(self,processor_size,callback, stdio_capture=None):
        ''' initialise the processor

            @param processor_size: the requested number of __slave__processors, if the number of
                                   processors is set by the enivironment (e.g. in the case of MPI
                                   via mpiexec -np <n-processors> on the command line the processor
                                   is free to ignore this value.

                                   The default value fom the command line is -1, and subclasses
                                   on recieving this value either raise and exception or detemine
                                   the correct number of slaves to create (e.g. on a muli cored
                                   machine using a threaded implimentaion the correct number of
                                   slaves would be equal to the number of cores available).

            @type processor_size: int

            @param callback: the application callback which allows the host application to start its
                             main loop and handle exceptions from the processor.
            @type callback: an instance of multi.processor.Application_callback

            @param stdio_capture: an array of streams used for writing to stdout and stderr while
                                  using the processor. Stdout and stderr should be in slots 0 and 1
                                  of the array. This facility is provided for subclasses to use so
                                  that they can install there on file like classes for manipulation
                                  stdout and stderr including decorating them merging them and
                                  storing them. Suclasses should replace sys.stdout and sys.stderr
                                  as needed but not touch sys.__stdout__ and sys.__stderr__. if a
                                  value of None is provided a default implimentation that decorates
                                  stderr and stdout if more than one slave processor is vailable is
                                  used other wise stdout and stderr are used.

            @type stdio_capture:  a two slot array of file line objects.



        '''

        self.callback=callback
        ''' callback to interface to the host application @see Application_callback'''

        self.grainyness=1
        ''' the number of sub jobs to queue for each processor if we have more jobs than
            processors'''

#        # CHECKME: am  I implimented?, should I be an application callback function
#        self.pre_queue_command=None
#        ''' command to call before the queue is run'''
#        # CHECKME: am  I implimented?, should I be an application callback function
#        self.post_queue_command=None
#        ''' command to call after the queue has completed running'''
#
        #CHECKME: should I be a singleton
        self.NULL_RESULT=Null_result_command(processor=self)
        ''' empty result command used by commands which do not return a result (a singleton?)'''


        self._processor_size=processor_size
        '''  number of slave processors available in this processor'''

        # CHECKME: integration with with stdo capture on slaves
        # setup captured std output and error streams used for capturing and modifying proccessor
        # output on masters and slaves
        # processor id the replacement stdio file like objects are stored in the modulevariable
        # global_stdio_capture
        self.setup_stdio_capture(stdio_capture)

    # register load multi_processor as a ststic function of the class
    # FIXME: cleanup move function into class
    load_multiprocessor = staticmethod(load_multiprocessor)

    def add_to_queue(self,command,memo=None):
        ''' add a command for remote execution to the queue - an abstract method

            @param command: a command to excute on a slave processor
            @type command: a subclass of

            @param memo: a place to place data needed on command completion (e.g. where to save the
                         results) the data stored in the memo is provided to Result_commands
                         generated by the command submitted.
            @type memo: a sub class of Memo

            @see: multi.processor.Slave_command
            @see: multi.processor.Result_command
            @see: multi.processor.Memo

        '''
        raise_unimplimented(self.add_to_queue)

    def run_queue(self):
        ''' run the processor queue - an abtract method

            all commands queued with add_to_queue will be executed, this function causes
            the current thread to block until the command has completed
        '''
        raise_unimplimented(self.run_queue)

    def run(self):
        ''' run the processor - an abstract method

            this function runs the processor main loop and is called after all processor setup has
            been completed. It does remote execution setup and teardown round either side of a call
            to Application_callback.init_master

            @see: multi.processor.Application_callback
        '''
        raise_unimplimented(self.run)

    def return_object(self,result):
        ''' return a result to the master processor from a slave - an abstract method

            @param result: a result to be returned to the master processor, if the
            @type result: a Result_string, Result_command or an Exception

            @see: multi.processor.Result_string
            @see: multi.processor.Resulf_command
        '''
        raise_unimplimented(self.return_object)

    def get_name(self):
        ''' get the name of the current processor - an abstract method

            the string should indentify the current master or slave processor uniquely but is
            purely for information and debugging. For example the mpi implimentation uses the string
            <host-name>-<process-id> whereas the thread implimentation uses the id of the current
            thread as provided by python.

            @return: the identifier for the prcoessor
            @rtype: String
        '''
        raise_unimplimented(self.get_name)

    def abort(self):
        ''' shutdown the multi processor in exceptional conditions - designed for overriding

            this method is called after an exception from the master or slave has been raised and
            prcoessed and is reposnible for the shutdown of the multi prcocessor fabric and
            terminiating the application. The functions should be called as the last thing that
            Application_callback.handle_exception does.

            As an example of the methods use see Mpi4py_prcoessor.abort which calls
            MPI.COMM_WORLD.Abort() to cleanly shutdown the mpi framework and remove dangling
            processes.

            The default action is to call sys.exit()

            @see: multi.processor.Application_callback
            @see: multi.mpi4py_processor.Mpi4py_processor.abort()
            @see: mpi4py.MPI.COMM_WORLD.Abort()
        '''
        sys.exit()

    # FIXME is this used?
#    def exit(self):
#        raise_unimplimented(self.exit)



    def rank(self):
        ''' get the rank of this processor - an abstract method

            the rank of the processor should be a numbe between 0 and n where n is the number of
            slave proessors, the rank of 0 is reserved for the master processor.

            @return: the rank of the prcoessor
            @rtype: integer

        '''
        raise_unimplimented(self.rank)

    def processor_size(self):
        ''' get the number of slave processors - designed for overriding

            @return: the number of slave processors
            @rtype: int
        '''
        return self._processor_size

    def get_intro_string(self):
        ''' get a string describing the multi processor - designed for overriding

            the string should be suitable for display at application startup and should be less than
            100 characters wide. A good example is the string returned by mpi4py_prcoessor:

            >>>MPI running via mpi4py with <n> slave processors & 1 master, mpi version = <x>.<y>


            @return: a stringdecribing the multi processor
            @rtype: string

            @see: multi.processor.mpi4py_prcoessor.Mpi4py_processor.get_intro_string
        '''
        raise_unimplimented(self.get_intro_string)


#    def restore_stdio(self):
#        sys.stderr = self.save_stderr
#        sys.stdout = self.save_stdout

    def run_command_globally(self,command):
        ''' run the same command on all slave processors

            @param command: a slave command
            @type command: an instance of Slave_command

            @see: multi.processor.processor.Slave_command


        '''
        queue = [command for i in range(self.processor_size())]
        self.run_command_queue(queue)


    def pre_run(self):
        ''' method called before starting the applicationm main loop - designed for overriding

            the default implimentation just saves the start time for application timing

            all subclasses should call the base method via super()

            only called on the master

            '''

        if self.rank() == 0:
            self.start_time =  time.time()


    def get_time_delta(self,start_time,end_time):
        ''' utility function called toformat the difference between application start and end times
            as a string

            @param start_time: the time the application started in seconds since the epoch
            @type start_time: float

            @param end_time: the time the application ended in seconds since the epoch
            @type end_time: float

            # TODO: check my format is correctr
            @return: the time difference in the format hours:minutes:seconds
            @rtype: string

        '''

        time_diff= end_time - start_time
        time_delta = datetime.timedelta(seconds=time_diff)
        time_delta_str = time_delta.__str__()
        (time_delta_str,millis) = time_delta_str.split('.',1)
        return time_delta_str

    def post_run(self):
        ''' method called after the application main loop has finished- designed for overriding

            the default implimentation ouputs the application runtime to stdout

            all subclasses should call the base method as their last action  via super()

            only called on the master on normal exit from the applications run loop

        '''
        if self.rank() == 0:
            end_time = time.time()
            time_delta_str = self.get_time_delta(self.start_time,end_time)
            print 'overall runtime: ' + time_delta_str + '\n'



    def rank_format_string_width(self):
        ''' get the width of the string deignating the rank of a slave process

            typically this will be the number of digits in the slaves rank

            @return: the number of digits in the biggest slave pcoressors rank
            @rtype: integer
        '''
        return int(math.ceil(math.log10(self.processor_size())))

    def rank_format_string(self):
        ''' get a formatted string with the rank of a slave

            only called on slaves

            @return: the string designating the rank of the slave
            @rtype: a string


        '''
        digits  = self.rank_format_string_width()
        format = '%%%di' % digits
        return format

    # fixme: is an argument of the form stio_capture needed
    def setup_stdio_capture(self,stdio_capture=None):
        ''' default function to setup capturing and manipulating of stdio on slaves and master
            processors - designed for overriding

            @note: these function will replace sys.stdou and sys.stderr with custom functions
                   restore_stdio should be called to return the system to a pristine state
                   the original stdout and stderr are always available in sys.__stdout__ and
                   sys.__stderr__
            @note: the sys.stdout and sys.stderr streams are not replaced by this function but by
                   calling capture_stdio all it does is save replacements to self.stdio_capture

            @see: multi.prependStringIO
            @see: multi.processor.restore_stdio
            @see: multi.processor.capture_stdio
            @see: sys


            @todo: remove useless stdio_capture parameter

        '''
        rank =self.rank()
        pre_strings=('','')

        if stdio_capture==None:
            pre_strings = self.get_stdio_pre_strings()
            stdio_capture=self.std_stdio_capture(pre_strings=pre_strings)

        self.stdio_capture=stdio_capture

    #TODO check if pre_strings are used anyhere if not delete
    def std_stdio_capture(self,pre_strings=('','')):
        ''' get the default sys.stdout and sys.stderr replacements

            on the master the replacement prepend output with 'MM S]' or MM E]' for the stdout
            and stderr channels repectivley on slaves the outputs are replaced by StringIO objects
            that prepend 'NN S]' or NN E]' for stdout and stderr where NN is the rank of the
            processor. On the slave prcoessors the saved strings are retrieved for return to the
            master prcoessor by calling getvalue() on sys.stdout and sys.stderr.

            @note: by default stdout and stderr are conjoined as otherwise the context of stdout
                   and stderr messages are lost
            @todo: improve segregation of sys.sdout and sys.stderr

            @param pre_strings: pre strings for the sys.stdout and sys.stderr channels
            @type pre_strings: an array of two strings  for stdoutand stderr respectivley

            @return: file like objects to replace stdout and stderr respectivley in order
            @rtype: a tuple of two file like objects
        '''



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
        ''' enable capture of the sys.stdout and sys.stderr streams by those in self.stdio_capture
            or user supplied streams

            @note: on slave processors the replacement stdout and stderr streams should be file like
                   objects which implement the methods truncate and getvalue (see PrependStringIO)

            @note: both or neither stream has to be replaced you can't just replace one!

            @param stdio_capture: a pair of file like objects used to replace sys.stdout and
                                  sys.stderr respectivley
            @type stdio_capture: a list of two fil like objects to replace sys.stdout and sys.stderr
                                 in that order


        '''

        if stdio_capture  == None:
            stdio_capture=self.stdio_capture

        sys.stdout = self.stdio_capture[0]
        sys.stderr = self.stdio_capture[1]

    def get_stdio_capture(self):
        ''' get the file like objects currently replacing sys.stdout and sys.stderr

            @return: the file like objects currently replacing sys.stdout and sys.stderr
            @rtype: a tuple of two file like objects replacing sys.stdout and sys.stderr
        '''

        return self.stdio_capture

    def restore_stdio(self):
        ''' restore sys.stdout and sys.stderr to the system defaults

            @note: sys.stdout and sys.stderr are replaced with sys.__stdout__ ans sys.__stderr__
        '''

        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__

    def get_stdio_pre_strings(self):
        ''' get the strings used prepend stdout and stderr dependant on the current rank
            for processors with only one slave the result should be ('','') - designed for
            overriding

            @note: the defaults are ('MM X]',MM E]') and  ('NN S]' , NN E]') for masters and slaves
                   respectivley with NN replaced by the rank of the prcoessor

            @return: a list of two strings for stdout and stderr respectivley
            @rtype: list of two strings
        '''


        pre_string =''
        stdout_string = ''
        stderr_string = ''
        rank =self.rank()

        if self.processor_size() > 1 and rank > 0:
            pre_string = self.rank_format_string() % rank
        elif self.processor_size() > 1 and rank == 0:
            pre_string = 'M'*self.rank_format_string_width()

        if self.processor_size() > 1:
            stderr_string  =  pre_string + ' E> '
            stdout_string  =  pre_string + ' S> '

        return (stdout_string,stderr_string)

# TODO currently uni_processor doesn't have a prcoess_result should this be integrated
class Result(object):
    ''' a basic result object returned from a alave processor via return_object

        this a very basic result and shouldn't be overriden unless you are also modifying the
        process_result method in all the processors in the framework (i.e. currently for
        implimentors only). Most users should override Result_command

        this result basically acts as stroage for the following fields completed,memo_id,
        processor_rank

        results should only be created on slave processors

        @see: multi.processor.return_object
        @see: multi.processor.process_result
        @see: multi.prcoessor.Result_command

    '''

    def __init__(self,processor,completed):
        ''' initialise a result

            this object is designed for subclassing and __init__ should be called via the super()
            function

            result_command objects

            @param processor: processor the processor instance we are running in
            @type processor: an instance of prcoessor

            @param completed: a flag used in batching result returns to indicate that the sequence of batched result
                              commands has completed, the flag should be set by slave_commands. The
                              value should be the value passed to a Slave_commands run method if it
                              is the final result being returned otherwise it should be False.
            @type completed: boolean

            @note: the requirement for the user to know about completed will hopefully disappear
                   with some slight of hand in the Slave_command and it may even disappear
                   completely


            @see: multi.processor.Processor
        '''
        #TODO: assert on slave if processor_size > 1
        #TODO: check if a completed command will add a noticeable overhead (I doubt it will)
        self.completed=completed
        '''a flag used in batching result returns to indicate that the sequence of batched result
           commands has completed. This is an optimisation to prevent the sending an extra batched
           result queue completion result being sent, it may be an over early optimisation '''
        self.memo_id=None
        '''the memo_id of the Slave_command currently being processed on this processor, this value
           is set by the return_object method to the current Slave_commands memo_id'''
        self.rank = processor.rank()
        '''the rank of the current processor, used in command sheduling on the master prcoessor'''

# TODO: make this a result_command
class Result_string(Result):
    ''' A simple result from a slave containing a result, the processor will print this string via
        sys__stdout__

        @note: this may become a result_command so as to simpliy things in the end
    '''
    #TODO: correct order of parameters should be string,processor,completed
    def __init__(self,processor,string,completed):
        '''initialiser

            @param string: a string to return the master processor for output to stdout (note the
                           master may split the string into compoenets for stdout and stderr
                           depending on the prefix string. This class is not really designed for
                           subclassing.

            @type string: a string

            @see: multi.processor.Processor.std_stdio_capture
            #TODO: check inherited parameters are documented

        '''
        super(Result_string,self).__init__(processor=processor,completed=completed)
        self.string=string


class Result_command(Result):
    ''' A general result command - designed to be subclassed by users

        This is a general result command from a Slave command that will have its run() method called
        on return to the master processor

        @see: multi.processor.Slave_command

    '''

    def __init__(self,processor,completed,memo_id=None):
        #TODO: check this method is documnted by its parent
        super(Result_command,self).__init__(processor=processor,completed=completed)
        self.memo_id=memo_id


    def run(self,processor,memo):
        ''' the run method of the result command

            this method will be called when the result command is processed by the master and should
            carry out any actions the slave command needs carried out on the master (e.g. save or
            register results).

            @param processor: The master processor that queued the original Slave_command
            @type processor: an instance of Processor

            @param memo: a memo that was registered when the original slave command was placed on
                         the queue. This provides local storage on the master
            @type memo: an instance of Memo or None

            @see: multi.processor.Processsor
            @see: multi.processor.Slave_command
            @see: multi.prcoessor.Memo



        '''
        pass

class Null_result_command(Result_command):
    ''' an empty result command

        This command should be returned from slave_command if no other Result_command  is returned.
        This allows the queue processor to register that the slave processor has completed its
        processing and schedule new Slave-commands to it .
    '''
    def __init__(self,processor,completed=True):
        super(Null_result_command,self).__init__(processor=processor,completed=completed)



class Result_exception(Result_command):
    ''' return and raise an exception from the salve processor
    '''
    def __init__(self,processor,exception,completed=True):
        ''' initialise the result command with an exception

            @param exception: an exception that was raised on the slave processor (note the real
                              exception will be warapped in a Capturing_exception
            @type exception: an exception most probably wrapped in a capturing exception
        '''
        super(Result_exception,self).__init__(processor=processor,completed=completed)
        self.exception=exception

    def run(self,processor,memo):
        ''' raise the exception from the Slave_processor
        '''
        raise self.exception


class Slave_command(object):
    ''' a command to executed remotely on the slave processor -designed to be subclassed by users

        the command should be queued with the command queue using the add_to_queue command of the
        master and B{must} return at least one Result_command even if it is a prcoessor.NULL_RESULT.
        results are returned from the Slave_command to the master prcoessor uuing the return_object
        method of the prcoessor passed to the command. Any exceptions raised will be caught wrapped
        and returned to the master prcoessor by the slave processor.

        @note: good examples of subclassing a slave command include
               multi.commands.MF_minimise_command and multi.commands.Get_name_command

        @see: multi.commands.MF_minimise_command
        @see: multi.commands.Get_name_command

    '''

    def __init__(self):
        self.memo_id=None

    def set_memo_id(self,memo):
        '''called by the master processor to remember this Slave_commands memo on the master
           processor

            @param memo: the memo to remember, memos are remembered by getting the memo_id of the
                         memo
        '''
        if memo != None:
            self.memo_id = memo.memo_id()
        else:
            self.memo_id=None

    def run(self,processor,completed):
        ''' run the slave command on the slave processor. The run command B{must} return at least
            one Result_command even if it is a processor.NULL_RESULT.  results are returned from the
            Slave_command to the master prcoessor uuing the return_object method of the processor
            passed to the command. Any exceptions raised will be caught wrapped and returned to the
            master processor by the slave processor.

            @param processor: The slave prcoessor the command is running on. results from the
                              command are returned via calls to processor.return_object
            @type processor: an instance of Processor

            @param completed: The  flag used in batching result returns to indicate that the  a
                              sequence of batched result commands has completed. This cvlaue should
                              be returned via the last result object retuned by this method or
                              methods it calls. All other Result_commands should be initialised with
                              completed=False. This is an optimisation to prevent the sending an
                              extra batched result queue completion result command being sent, it
                              may be an over early optimisation.
            @type completed: Boolean


        '''
        pass



class Memo(object):
    ''' a memo of objects and data that a slave_command want to provide to its results-commands upon
        their return to the master processor - designed for overring by users'''

    def memo_id(self):
        ''' get the unique id for the memo, currently this is the objects unique python id (note
            these ids can be recycled once the memo has been garbage collected it cannot be used as
            a unique longterm hash)

            @return: a unique id for this memo
            @rtype: inetegr
        '''
        return id(self)



class Capturing_exception(Exception):
    ''' a wrapper exception for an exception captured on a slave processor

        the wrapper will remeber the stack trace on the remote machine and when raised and caught
        has a string that includes the remote stack trace, which will be displayed along with the
        stack trace on the master.

    '''
    def __init__(self,exc_info=None, rank='unknown', name='unknown'):
        '''initialise the wrapping exception

           @param exc_info: exception information as produced by sys.exc_info()
           @type exc_info: a tuple as prcouced by sys.exc_info()

           @todo: would it be easier to pass a processor here
           @param rank: The rank of the processor on which the xception was raised
           @type rank: an integer > 1

           @param name: The name of the processor on which the exception was raised as returned by
                        processor.get_name()
           @type name:  a string
        '''

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
        '''get the string describing this exception
            @return: The string describing this exception
            @rtype: a string
        '''
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
        result =  message % ('-'*120, ''.join(self.traceback) ,self. rank, self.name, self.exception_name,
                             self.exception_string, '-'*120)
        return result


