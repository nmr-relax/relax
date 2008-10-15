from  StringIO import StringIO
import sys




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

class PrependStringIO(StringIO):

    def __init__(self,token):
        StringIO.__init__(self)
        self.token = token
        self.token_length = len(token)
        self.first_time = True


    def write(self,string):
        # FIXME: raising an exception here wedges mpi4py
        file_name = sys._getframe(1).f_code.co_filename.split('/')[-1]
        function_name = sys._getframe(1).f_code.co_name
        line_number = sys._getframe(1).f_lineno
        #msg = '<<%d - %s - %s - %d: %s>>'  %(id(self),file_name,function_name,line_number,string)
        #sys.__stdout__.write(msg)
        string = string.replace('\n', '\n' + self.token)
        if self.first_time == True:
            string ='\n' +self.token + string
            self.first_time = False


        StringIO.write(self,string)





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