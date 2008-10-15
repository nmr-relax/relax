from  StringIO import StringIO
import sys
from threading import currentThread

class Multiplex_stdout(StringIO):
    def __init__(self):
        StringIO.__init__(self)
        self.thread_stream_map={}

    def current_thread_id(self):
        return self.thread_id(currentThread())

    def thread_id(self,thread):
        # wanted to use thread.get_ident but main thread barfes on it could use -1?
        return id(thread)

    def add_stream(self,stream):
        thread_id = self.current_thread_id()
        self.thread_stream_map[thread_id]=stream

    def write(self,string):
        thread=  currentThread()
        thread_id = self.thread_id(thread)

        stream = self.thread_stream_map[thread_id]
        return stream.write(string)

    def get_stream(self,thread=None):
        if thread ==  None:
            thread_id =  self.current_thread_id()
        else:
            thread_id=self.thread_id(thread)

        return self.thread_stream_map[thread_id]

    def getvalue(self):
        return self.get_stream().getvalue()

#FIXME could these two classes be merged via use of a target stream and multiple inheritance?
class PrependOut(StringIO):

    def __init__(self,token,stream):
        StringIO.__init__(self)
        self.token = token
        self.token_length = len(token)
        self.first_time = True

        self.stream=stream

    def write(self,string):
        #sys.__stdout__.write('<<' + string + '>>\n')

        string = string.replace('\n', '\n' + self.token)
        if self.first_time == True:
            string = '\n'+self.token + string
            self.first_time = False

        #StringIO.write(self,string)
        #sys.__stdout__.write('<<' + string + '>>\n')
        self.stream.write(string)
        #self.truncate(0)

    # lost more functions needed use dict???
    def isatty(self,*args,**kwargs):
        return stream.isatty(*args,**kwargs)
#    def flush(self):
#        self.stream.write(self.getvalue().rstrip(self.token))
#        self.truncate(0)
#        self.first_time=True

#TODO: maybe this hsould be a delegate to a stringio rather than being a stringio as this will speed things up and simplify things
class PrependStringIO(StringIO):

    def __init__(self,token,target_stream=None):
        StringIO.__init__(self)
        self.token = token
        self.token_length = len(token)
        self.first_time = True
        if target_stream == None:
            self.target_stream=self
        else:
            self.target_stream=target_stream




    def write(self,string):
        # FIXME: raising an exception here wedges mpi4py

        string = string.replace('\n', '\n' + self.token)
        if self.first_time == True:
            string ='\n' +self.token + string
            self.first_time = False


        StringIO.write(self.target_stream,string)



    def truncate(self,size=None):
        if size ==0:
           self.first_time=True
        #PY3K: should be a call to super but StringIO is a old style class
        StringIO.truncate(self,size)

    def getvalue(self):
        result = StringIO.getvalue(self)
        if len(result) > 0  and result[-1] == '\n':
           result = result[0:-self.token_length-1]
           result=result+'\n'

        return result

if __name__ =='__main__':
    prepend = PrependStringIO('>001 | ')

    prepend.write('test\ntest2\n')
    tout = sys.stdout
    sys.stdout=prepend
    print 'test3'
    sys.stdout=tout
    print prepend.getvalue()