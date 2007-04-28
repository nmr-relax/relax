from  StringIO import StringIO
import sys



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