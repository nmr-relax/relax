class Result(object):
    def __init__(self,completed):
        self.completed=completed


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
    def __init__(self):
        super(Null_result_command,self).__init__(completed=True)

NULL_RESULT=Null_result_command()


class Slave_command(object):
    def __init__(self):
        self.memo_id=None

    def set_memo_id(self,memo):
        if memo != None:
            self.memo_id = memo.memo_id()
        else:
            self.memo_id=None

    def run(self,processor):
        pass

#FIXME do some inheritance


class Memo(object):
    def memo_id(self):
        return id(self)
