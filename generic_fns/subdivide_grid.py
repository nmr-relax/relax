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

# Python module imports.
import math
from numpy import float, ones
from textwrap import dedent


#constants
##########

GRID_STEPS = 0
GRID_LOWER = 1
GRID_UPPER = 2


class Grid_info(object):
    def __init__(self, lower=None, upper=None, inc=None, n=None, start=0, range=None):
        """Initialise the grid sub-division object.

        @keyword lower: The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:    array of numbers
        @keyword upper: The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:    array of numbers
        @keyword inc:   The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
        @type inc:      array of int
        @keyword n:     The number of parameters, i.e. the dimensionality of the space.
        @type n:        int
        @keyword start: Unknown?
        @type start:    int
        @keyword range: Unknown?
        @type range:    int
        """

        # Store the args.
        self.lower = lower
        self.upper = upper
        self.inc = inc
        self.n = n
        self.start = start
        self.range = range

        # Calculate the data structures used to sub-divide the grid.
        self.steps = self.calc_grid_size()
        self.values = self.calc_grid_values()
        self.strides = self.calc_strides()

        #FIXME needs range checking i.e. is start = range > info.steps
        # need checks for empty/fractional ranges
        if range == None:
            self.range = self.steps - start
        else:
            self.range = range


    def __iter__(self):
        """Convert the class into an iterable object.

        @return:    An iterator object.
        @rtype:     Iterator instance
        """

        return Iterator(self, self.start, self.start+self.range)


    def __str__(self):
        message = '''\
                        grid info:

                        number of axes:        %d
                        full number of steps:  %d
                        sub range indices:     %d - %d

                        full grid range:

                  '''
        message = dedent(message)
        message = message % (self.n, self.steps, self.start, self.start+self.range)

        op_message_list = []
        for i, op in enumerate(self.grid_ops):
            op_message = '%d.  %f...[%d steps]...%f'
            op_list = (i+1, op[GRID_LOWER], op[GRID_STEPS], op[GRID_UPPER])
            op_message_list .append(op_message % op_list)

        op_message = '\n'.join(op_message_list)

        message = message + op_message

        return message


    def calc_grid_size(self):
        """Calculate the total number of grid points.

        @return:    The number of grid points.
        @rtype:     int
        """

        # Multiply the increments of all dimensions.
        size = 1
        for inc in self.inc:
            size = size * inc

        # Return the size.
        return size


    def calc_grid_values(self):
        """Calculate the coordinates of all grid points.

        @return:    A list of lists of coordinates for each grid point.  The first index corresponds to the dimensionality of the grid and the second is the increment values.
        @rtype:     list of lists of float
        """

        # Initialise the coordinate list.
        coords = []

        # Loop over the dimensions.
        for i in range(self.n):
            # Initialise the list of values for the dimension and add it to the coordinate list.
            values = []
            coords.append(values)

            # Loop over the increments.
            for j in range(self.inc[i]):
                values.append(self.lower[i] + j * (self.upper[i] - self.lower[i]) / (self.inc[i] - 1.0))

        # Return the grid points.
        return coords


    def calc_strides(self):
        """Calculate the strides data structure for dividing up the grid.

        @return:    The strides data structure.
        @rtype:     list of int
        """

        # Build the data structure.
        stride = 1
        data = []
        for i in range(self.n):
            data.append(stride)
            stride = stride * self.inc[i]

        # Return the strides data structure.
        return data


    def get_params(self, offsets, params=None):
        if params == None:
            params = ones(len(offsets), float)

        for i, offset in enumerate(offsets):
            params[i] = self.values[i][offset]

        return params


    def get_step_offset(self, step):
        result = []
        for stride in self.strides[-1::-1]:
            offset = step / stride
            result.append(offset)
            step = step - stride*offset

        result.reverse()

        return result
        #res_values = []
        #for i, elem in enumerate(result):
        #    res_values.append(self.values[i][elem])
        #
        #return res_values


    def print_steps(self):
        offsets = self.get_step_offset(self.start)
        #params = self.get_params(step_num)
        #for op in self.grid_ops:
        #    params.append(op[GRID_LOWER])

        for i in xrange(self.start, self.start+self.range):

            print `i+1` + '. ', self.get_params(offsets)
            for j in range(self.n):
                if offsets[j] < self.grid_ops[j][GRID_STEPS]-1:
                    offsets[j] = offsets[j] + 1

                    # Exit so that the other step numbers are not incremented.
                    break
                else:
                    offsets[j] = 0


    def sub_divide(self, steps):
        if steps > self.range:
            steps = self.range

        increment = self.range/(steps * 1.0)
        max_div_end = self.start + self.range

        divs = []
        last_div = self.start
        for i in range(steps):
            div_end = int(math.ceil(self.start + ((i+1) * increment)))

            # this garuntees completion in the face of roundoff errors
            if div_end > max_div_end:
                div_end = max_div_end

            div_range = div_end - last_div
            divs.append(self.sub_grid(start= last_div, range=div_range))
            last_div = div_end

        return divs


    def sub_grid(self, start, range):
        return Grid_info(self.grid_ops, start=start, range=range)



class Iterator(object):
    def __init__(self, info, start, end):
        self.info = info

        # start point
        self.start = start

        # end of range
        self.end = end

        #current step
        self.step = start

        self.offsets = info.get_step_offset(self.step)
        self.params = self.info.get_params(self.offsets)


    def __iter__(self):
        return self


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
                   params  %s ''' % (`self.info`, self.start, self.end, self.step, `self.offsets`, `self.params`)


    def increment(self):
        # Increment the grid search.
        for j in xrange(self.info.n):
            if self.offsets[j] < self.info.grid_ops[j][GRID_STEPS]-1:
                self.offsets[j] = self.offsets[j] + 1

                # Exit so that the other step numbers are not incremented.
                break
            else:
                self.offsets[j] = 0


    def next(self):
        if self.step >= self.end:
            raise StopIteration()

        self.params = self.info.get_params(self.offsets, self.params)

        self.step = self.step + 1
        self.increment()

        return self.params
