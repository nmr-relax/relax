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

# FIXME better  requirement of inherited commands
# TODO: check exceptiosn on master
import time,datetime,math,sys,os
import traceback,textwrap
from  multi.prependStringIO import PrependStringIO,PrependOut

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

    def __init__(self,master):
        self.master=master
        self.init_master = self.default_init_master
        self.handle_exception= self.default_handle_exception

    def default_init_master(self,processor):
        self.master.run()

    def default_handle_exception(self,processor,exception):
        #TODO: could do with flag to force __stdout__ vs  stdout
        traceback.print_exc(file=sys.__stdout__)
        processor.abort()


def raise_unimplimented(method):
    raise NotImplementedError("Attempt to invoke unimplemented abstract method %s") % method.__name__

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


