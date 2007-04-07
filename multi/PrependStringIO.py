from  StringIO import StringIO
import sys

# these may need to be in c they cause an pprox 10% slowdown

class PrependOut(StringIO):

    def __init__(self,token,stream):
        StringIO.__init__(self)
        self.token = token
        self.token_length = len(token)
        self.first_time = True
        self.stream=stream

    def write(self,string):
        if self.first_time == True:
            string =self.token + string
            self.first_time = False
        string = string.replace('\n', '\n' + self.token)
        #StringIO.write(self,string)
        self.stream.write(string)
        #self.truncate(0)

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
        if self.first_time == True:
            string =self.token + string
            self.first_time = False
        string = string.replace('\n', '\n' + self.token)
        StringIO.write(self,string)





    def getvalue(self):
        result = StringIO.getvalue(self)
        #if len(result) <= len(self.token):
        #   result = ''
        #if result.endswith('\n' + self.token):
        #    result = result[0:-self.token_length-1]
        return result

if __name__ =='__main__':
    prepend = PrependStringIO('>001 | ')

    prepend.write('test\ntest2\n')
    tout = sys.stdout
    sys.stdout=prepend
    print 'test3'
    sys.stdout=tout
    print prepend.getvalue()