###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2010 Edward d'Auvergne                            #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

#FIXME exceptiosn not progated properly in main loop
import math
from Numeric import  Float
from textwrap import dedent

from Numeric import Float64, ones


#constants
##########

GRID_STEPS = 0
GRID_LOWER = 1
GRID_UPPER = 2

# FIXME: a somewhat inglorious hack, printing needs to be revisited in the light of multiprocessing
pre_and_post_amble =  True


def set_pre_and_post_amble(value):
    global pre_and_post_amble
    pre_and_post_amble=value

class Grid_info(object):
    def __init__(self,grid_ops,start=0,range=None):
        self.grid_ops = grid_ops
        for op in self.grid_ops:
            op[GRID_LOWER] = float(op[GRID_LOWER])
            op[GRID_UPPER] = float(op[GRID_UPPER])
        self.steps = self.count_grid_steps(grid_ops)
        self.grid_dimension = len(grid_ops)
        self.values = self.calc_grid_values(grid_ops)
        self.strides = self.calc_strides(grid_ops)
        self.start=start

        #FIXME needs range checking i.e. is start = range > info.steps
        # need checks for empty/fractional ranges

        if range == None:
            self.range = self.steps-start
        else:
            self.range=range


    def sub_grid(self,start,range):
        return Grid_info(self.grid_ops,start=start,range=range)

    def sub_divide(self,steps):
        if steps > self.range:
            steps =  self.range

        increment = self.range/(steps * 1.0)
        max_div_end = self.start + self.range


        divs = []
        last_div=self.start
        for i in range(steps):
            div_end =  int(math.ceil(self.start + ((i+1) * increment)))

            # this garuntees completion in the face of roundoff errors
            if div_end > max_div_end:
                div_end=max_div_end

            div_range  = div_end - last_div
            divs.append(self.sub_grid(start= last_div,range=div_range))
            last_div = div_end

        return divs

    def calc_strides(self,grid_ops):
        stride = 1
        result = []
        for op in grid_ops:
            result.append(stride)
            stride=stride*op[GRID_STEPS]

        return result


    def count_grid_steps(self,grid_ops=None):
        """ calculate the number of steps in a grid search """

        result = 1
        for op in grid_ops:
            result = result * op[GRID_STEPS]

        return result

    def calc_grid_values(self,grid_ops=None):
        """ calculate the values the points along each grid dimension can take"""
        result = []
        for  op in grid_ops:
            values=[]
            result.append(values)

            op_range = op[GRID_UPPER] - op[GRID_LOWER]
            for i in xrange(op[GRID_STEPS]):
                values.append(op[GRID_LOWER] + i * op_range / (op[GRID_STEPS] - 1))

        return result

    def __str__(self):
        message = '''\
                        grid info:

                        number of axes:        %d
                        full number of steps:  %d
                        sub range indices:     %d - %d

                        full grid range:

                  '''
        message = dedent(message)
        message = message % (self.grid_dimension,self.steps,self.start,self.start+self.range)

        op_message_list = []
        for i,op in enumerate(self.grid_ops):
            op_message  = '%d.  %f...[%d steps]...%f'
            op_list = (i+1,op[GRID_LOWER], op[GRID_STEPS], op[GRID_UPPER])
            op_message_list .append(op_message % op_list)

        op_message =  '\n'.join(op_message_list)

        message = message+op_message

        return message

    def print_steps(self):
        offsets = self.get_step_offset(self.start)
        #params = self.get_params(step_num)
        #for op in  self.grid_ops:
        #    params.append(op[GRID_LOWER])

        for i in xrange(self.start,self.start+self.range):

            print `i+1` + '. ',self.get_params(offsets)
            for j in range(self.grid_dimension):
                if offsets[j] < self.grid_ops[j][GRID_STEPS]-1:
                    offsets[j] = offsets[j] + 1
                    break    # Exit so that the other step numbers are not incremented.
                else:
                    offsets[j] = 0

    def get_step_offset(self,step):
        result=[]
        for stride in self.strides[-1::-1]:
            offset  = step / stride
            result.append(offset)
            step= step - stride*offset

        result.reverse()

        return result
        #res_values = []
        #for i,elem in enumerate(result):
        #    res_values.append(self.values[i][elem])
        #
        #return res_values

    def get_params(self,offsets,params=None):
        if params==None:
            params=ones(len(offsets),Float)


        for i,offset in enumerate(offsets):
            params[i]=self.values[i][offset]

        return params

    class Iterator(object):
        def __init__(self,info,start,end):
            self.info=info

            # start point
            self.start =start

            # end of range
            self.end = end

            #current step
            self.step = start

            self.offsets= info.get_step_offset(self.step)
            self.params = self.info.get_params(self.offsets)




        def __iter__(self):
            return self



        def next(self):


            if self.step >= self.end:
                raise StopIteration()

            self.params=self.info.get_params(self.offsets,self.params)

            self.step=self.step+1
            self.increment()

            return self.params



        def increment(self):
            # Increment the grid search.
            for j in xrange(self.info.grid_dimension):
                if self.offsets[j] < self.info.grid_ops[j][GRID_STEPS]-1:
                    self.offsets[j] = self.offsets[j] + 1
                    break    # Exit so that the other step numbers are not incremented.
                else:
                    self.offsets[j] = 0

        def __str__(self):
            print type(self.start)
            print type(self.end)
            print type(self.step)
            return ''' info:

                       %s

                       iter:

                       start %d
                       end   %d
                       step  %d
                       offsets %s
                       params  %s ''' % (`self.info`,self.start,self.end,self.step,`self.offsets`,`self.params`)



    def __iter__(self):
        return Grid_info.Iterator(self,self.start,self.start+self.range)
