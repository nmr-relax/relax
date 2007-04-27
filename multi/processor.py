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
import time,datetime,math,sys
from multi.PrependStringIO import  PrependStringIO,PrependOut
import traceback,textwrap



def raise_unimplimented(method):
    raise NotImplementedError("Attempt to invoke unimplemented abstract method %s") % method.__name__

#requires 2.4 decorators@abstract
#def abstract(f):
#    raise_unimplimented(f)
#    return f

class Processor(object):

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

    # FIXME is this used?
    def exit(self):
        raise_unimplimented(self.exit)

    def on_master(self):
        raise_unimplimented(self.on_master)

    def on_slave(self):
        return not self.on_master()

    def rank(self):
        raise_unimplimented(self.rank)

    def processor_size(self):
        raise_unimplimented(self.processor_size())

    def restore_stdio(self):
        sys.stderr = self.save_stderr
        sys.stdout = self.save_stdout

    def run_command_globally(self,command):
        queue = [command for i in range(self.processor_size())]
        self.run_command_queue(queue)

    def abort(self):
        sys.exit()

    #FIXME: remname chunk* grain*
    def __init__(self,relax_instance,chunkyness=1):
        self.chunkyness = chunkyness
        self.relax_instance = relax_instance

    def pre_run(self):
        if self.on_master():
            self.start_time =  time.time()

        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr

        if self.processor_size() > 1:

            pre_string = 'M'*self.rank_format_string_width()
            sys.stdout = PrependOut(pre_string + ' S> ', sys.stdout)
            sys.stderr = PrependOut(pre_string + ' E> ', sys.stderr)

    def get_time_delta(self,start_time,end_time):

        time_diff= end_time - start_time
        time_delta = datetime.timedelta(seconds=time_diff)
        time_delta_str = time_delta.__str__()
        (time_delta_str,millis) = time_delta_str.split('.',1)
        return time_delta_str

    def post_run(self):
        if self.on_master():
            end_time = time.time()
            time_delta_str = self.get_time_delta(self.start_time,end_time)
            print 'overall runtime: ' + time_delta_str + '\n'

        if self.processor_size() > 1:
            self.restore_stdio()

    def rank_format_string_width(self):
        return int(math.ceil(math.log10(self.processor_size())))

    def rank_format_string(self):
        digits  = self.rank_format_string_width()
        format = '%%%di' % digits
        return format




class Result(object):
    def __init__(self,completed):
        self.completed=completed
        self.memo_id=None



class Result_string(Result):
    #FIXME move result up a level
    def __init__(self,string,completed):
        super(Result_string,self).__init__(completed=completed)
        self.string=string


class Result_command(Result):
    def __init__(self,completed,memo_id=None):
        super(Result_command,self).__init__(completed=completed)
        self.memo_id=memo_id

    def run(self,relax,processor,memo):
        pass

class Null_result_command(Result_command):
    def __init__(self,completed=True):
        super(Null_result_command,self).__init__(completed=completed)

NULL_RESULT=Null_result_command()

class Result_exception(Result_command):
    def __init__(self,exception,completed=True):
        super(Result_exception,self).__init__(completed=completed)
        self.exception=exception

    def run(self,relax,processor,memos):
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
        self.exception_name =  exception_type.__name__
        self.exception_string = exception_instance.__str__()
        self.traceback = traceback.format_tb(exception_traceback)

    def __str__(self):
        message ='''

                     %s

                     Nested Exception from sub processor
                     Rank: %s  Name: %s
                     Exception type: %s
                     Message: %s

                     %s

                     %s


                 '''
        message = textwrap.dedent(message)
        result =  message % ('-'*120,self.rank, self.name, self.exception_name,
                             self.exception_string, '\n'.join(self.traceback),
                             '-'*120)
        return result


