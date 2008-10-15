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



class Memo(object):
    def memo_id(self):
        return id(self)
