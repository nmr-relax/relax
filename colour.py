###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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

from Numeric import Float64, array


class Colour:
    def __init__(self):
        """Class for all functions relating to colour."""


    def linear_gradient(self, value, start, end):
        """Return an RGB colour array of the value placed on a linear colour gradient.

        The argment value should be a number between zero and one.  The start and end colours can
        either be strings or RGB colour arrays.
        """

        # Translate the start and end colours to RGB arrays if necessary.
        if type(start) == str:
            start = self.rgb(start)
        if type(end) == str:
            end = self.rgb(end)

        # Truncate the value to be between zero and one.
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0

        # The position on the linear gradient.
        return value * (end - start) + start


    def rgb(self, name):
        """
        RGB colour arrays
        ~~~~~~~~~~~~~~~~~

        Table of RGB colour values and the corresponding colour name.
        _______________________________________________________________
        |                               |         |         |         |
        | Name                          | Red     | Green   | Blue    |
        |_______________________________|_________|_________|_________|
        |                               |         |         |         |
        | 'black'                       | 0.000   | 0.000   | 0.000   |
        | 'navy'                        | 0.000   | 0.000   | 0.502   |
        | 'blue'                        | 0.000   | 0.000   | 1.000   |
        | 'dark green'                  | 0.000   | 0.392   | 0.000   |
        | 'green'                       | 0.000   | 1.000   | 0.000   |
        | 'cyan'                        | 0.000   | 1.000   | 1.000   |
        | 'turquoise'                   | 0.251   | 0.878   | 0.816   |
        | 'royal blue'                  | 0.255   | 0.412   | 0.882   |
        | 'aquamarine'                  | 0.498   | 1.000   | 0.831   |
        | 'sky green'                   | 0.529   | 0.808   | 0.922   |
        | 'dark violet'                 | 0.580   | 0.000   | 0.827   |
        | 'pale green'                  | 0.596   | 0.984   | 0.596   |
        | 'purple'                      | 0.627   | 0.125   | 0.941   |
        | 'brown'                       | 0.647   | 0.165   | 0.165   |
        | 'light blue'                  | 0.678   | 0.847   | 0.902   |
        | 'grey'                        | 0.745   | 0.745   | 0.745   |
        | 'light grey'                  | 0.827   | 0.827   | 0.827   |
        | 'violet'                      | 0.933   | 0.510   | 0.933   |
        | 'light coral'                 | 0.941   | 0.502   | 0.502   |
        | 'khaki'                       | 0.941   | 0.902   | 0.549   |
        | 'beige'                       | 0.961   | 0.961   | 0.863   |
        | 'red'                         | 1.000   | 0.000   | 0.000   |
        | 'magenta'                     | 1.000   | 0.000   | 1.000   |
        | 'deep pink'                   | 1.000   | 0.078   | 0.576   |
        | 'orange red'                  | 1.000   | 0.271   | 0.000   |
        | 'hot pink'                    | 1.000   | 0.412   | 0.706   |
        | 'coral'                       | 1.000   | 0.498   | 0.314   |
        | 'dark orange'                 | 1.000   | 0.549   | 0.000   |
        | 'orange'                      | 1.000   | 0.647   | 0.000   |
        | 'pink'                        | 1.000   | 0.753   | 0.796   |
        | 'gold'                        | 1.000   | 0.843   | 0.000   |
        | 'yellow'                      | 1.000   | 1.000   | 0.000   |
        | 'light yellow'                | 1.000   | 1.000   | 0.878   |
        | 'ivory'                       | 1.000   | 1.000   | 0.941   |
        | 'white'                       | 1.000   | 1.000   | 1.000   |
        |_______________________________|_________|_________|_________|

        """

        # Initialise the dictionary of colours.
        colours = {}

        # The colours sorted by the RGB float values.
        colours['black']        = [0.000, 0.000, 0.000]
        colours['navy']         = [0.000, 0.000, 0.502]
        colours['blue']         = [0.000, 0.000, 1.000]
        colours['dark green']   = [0.000, 0.392, 0.000]
        colours['green']        = [0.000, 1.000, 0.000]
        colours['cyan']         = [0.000, 1.000, 1.000]
        colours['turquoise']    = [0.251, 0.878, 0.816]
        colours['royal blue']   = [0.255, 0.412, 0.882]
        colours['aquamarine']   = [0.498, 1.000, 0.831]
        colours['sky green']    = [0.529, 0.808, 0.922]
        colours['dark violet']  = [0.580, 0.000, 0.827]
        colours['pale green']   = [0.596, 0.984, 0.596]
        colours['purple']       = [0.627, 0.125, 0.941]
        colours['brown']        = [0.647, 0.165, 0.165]
        colours['light blue']   = [0.678, 0.847, 0.902]
        colours['grey']         = [0.745, 0.745, 0.745]
        colours['light grey']   = [0.827, 0.827, 0.827]
        colours['violet']       = [0.933, 0.510, 0.933]
        colours['light coral']  = [0.941, 0.502, 0.502]
        colours['khaki']        = [0.941, 0.902, 0.549]
        colours['beige']        = [0.961, 0.961, 0.863]
        colours['red']          = [1.000, 0.000, 0.000]
        colours['magenta']      = [1.000, 0.000, 1.000]
        colours['deep pink']    = [1.000, 0.078, 0.576]
        colours['orange red']   = [1.000, 0.271, 0.000]
        colours['hot pink']     = [1.000, 0.412, 0.706]
        colours['coral']        = [1.000, 0.498, 0.314]
        colours['dark orange']  = [1.000, 0.549, 0.000]
        colours['orange']       = [1.000, 0.647, 0.000]
        colours['pink']         = [1.000, 0.753, 0.796]
        colours['gold']         = [1.000, 0.843, 0.000]
        colours['yellow']       = [1.000, 1.000, 0.000]
        colours['light yellow'] = [1.000, 1.000, 0.878]
        colours['ivory']        = [1.000, 1.000, 0.941]
        colours['white']        = [1.000, 1.000, 1.000]

        # Convert to Numeric arrays.
        for key in colours:
            colours[key] = array(colours[key], Float64)

        # Invalid colour string.
        if not colours.has_key(name):
            raise RelaxInvalidColourError, name

        # Return the RGB colour array.
        return colours[name]
