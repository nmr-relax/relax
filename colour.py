###############################################################################
#                                                                             #
# Copyright (C) 2006-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for colour manipulation."""

# Python module imports.
from numpy import float64, array

# relax module imports.
from relax_errors import RelaxInvalidColourError
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


_linear_gradient_doc = Desc_container("Colour")
_linear_gradient_doc.add_paragraph("The values are coloured based on a linear colour gradient which is specified through starting and ending colours.  These can either be a string to identify one of the RGB (red, green, blue) colour arrays listed in the tables below, or you can give the RGB vector itself.  For example, 'white' and [1.0, 1.0, 1.0] both select the same colour.  Leaving both colours unset will select the default colour gradient which for each type of analysis is described below.")
_linear_gradient_doc.add_paragraph("When supplying the colours as strings, two lists of colours can be selected from which to match the strings.  These are the default Molmol colour list and the X11 colour list, both of which are described in the tables below.  The default behaviour is to first search the Molmol list and then the X11 colour list, raising an error if neither contain the name.  To explicitly select these lists, set the colour list to either 'molmol' or 'x11'.")

def linear_gradient(value, start, end, colour_list=None):
    """Return an RGB colour array of the value placed on a linear colour gradient.

    The argument value should be a number between zero and one.  The start and end colours can
    either be strings or RGB colour arrays.

    @param value:           The position on the gradient, ranging from zero to one.
    @type value:            float
    @param start:           The starting colour, either the name of the colour as a string or an RGB
                            colour array.
    @type start:            str or list of float
    @param end:             The ending colour, either the name of the colour as a string or an RGB
                            colour array.
    @type end:              str or list of float
    @keyword colour_list:   The colour names to use, one of 'x11' or 'molmol'.
    @type colour_list:      str
    @return:                The position in the gradient.
    @rtype:                 float
    """

    # Translate the end colour to RGB arrays if necessary.
    if isinstance(start, str):
        # Default (search the molmol list then the X11 list).
        if colour_list == None:
            try:
                start = molmol_colours(start)
            except:
                start = x11_colours(start)

        # Molmol colours.
        elif colour_list == 'molmol':
            start = molmol_colours(start)

        # X11 colours.
        elif colour_list == 'x11':
            start = x11_colours(start)

    # Translate the end colour to RGB arrays if necessary.
    if isinstance(end, str):
        # Default (search the molmol list then the X11 list).
        if colour_list == None:
            try:
                end = molmol_colours(end)
            except:
                end = x11_colours(end)

        # Molmol colours.
        elif colour_list == 'molmol':
            end = molmol_colours(end)

        # X11 colours.
        elif colour_list == 'x11':
            end = x11_colours(end)

    # Truncate the value to be between zero and one.
    if value < 0.0:
        value = 0.0
    elif value > 1.0:
        value = 1.0

    # The position on the linear gradient.
    return value * (end - start) + start


def molmol_colours(name):
    """Return the RGB colour array corresponding to the Molmol colour name.

    @param name:    The Molmol colour name.
    @type name:     str
    @return:        The RGB colour array.
    @rtype:         list of float
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

    # Convert to numpy arrays.
    for key in colours:
        colours[key] = array(colours[key], float64)

    # Invalid colour string.
    if name not in colours:
        raise RelaxInvalidColourError(name)

    # Return the RGB colour array.
    return colours[name]

# User function documentation.
__molmol_colours_doc__ = Desc_container("Molmol RGB colour arrays")
__molmol_colours_doc__.add_paragraph("The following table is a list of colours used in Molmol and their corresponding RGB colour values ranging from 0 to 1.")
table = uf_tables.add_table(label="table: Molmol colours", caption="Molmol colour names and corresponding RGB colour values (from 0 to 1)", spacing=False, longtable=False)
table.add_headings(["Name", "Red", "Green", "Blue"])
table.add_row(["'black'", "0.000", "0.000", "0.000"])
table.add_row(["'navy'", "0.000", "0.000", "0.502"])
table.add_row(["'blue'", "0.000", "0.000", "1.000"])
table.add_row(["'dark green'", "0.000", "0.392", "0.000"])
table.add_row(["'green'", "0.000", "1.000", "0.000"])
table.add_row(["'cyan'", "0.000", "1.000", "1.000"])
table.add_row(["'turquoise'", "0.251", "0.878", "0.816"])
table.add_row(["'royal blue'", "0.255", "0.412", "0.882"])
table.add_row(["'aquamarine'", "0.498", "1.000", "0.831"])
table.add_row(["'sky green'", "0.529", "0.808", "0.922"])
table.add_row(["'dark violet'", "0.580", "0.000", "0.827"])
table.add_row(["'pale green'", "0.596", "0.984", "0.596"])
table.add_row(["'purple'", "0.627", "0.125", "0.941"])
table.add_row(["'brown'", "0.647", "0.165", "0.165"])
table.add_row(["'light blue'", "0.678", "0.847", "0.902"])
table.add_row(["'grey'", "0.745", "0.745", "0.745"])
table.add_row(["'light grey'", "0.827", "0.827", "0.827"])
table.add_row(["'violet'", "0.933", "0.510", "0.933"])
table.add_row(["'light coral'", "0.941", "0.502", "0.502"])
table.add_row(["'khaki'", "0.941", "0.902", "0.549"])
table.add_row(["'beige'", "0.961", "0.961", "0.863"])
table.add_row(["'red'", "1.000", "0.000", "0.000"])
table.add_row(["'magenta'", "1.000", "0.000", "1.000"])
table.add_row(["'deep pink'", "1.000", "0.078", "0.576"])
table.add_row(["'orange red'", "1.000", "0.271", "0.000"])
table.add_row(["'hot pink'", "1.000", "0.412", "0.706"])
table.add_row(["'coral'", "1.000", "0.498", "0.314"])
table.add_row(["'dark orange'", "1.000", "0.549", "0.000"])
table.add_row(["'orange'", "1.000", "0.647", "0.000"])
table.add_row(["'pink'", "1.000", "0.753", "0.796"])
table.add_row(["'gold'", "1.000", "0.843", "0.000"])
table.add_row(["'yellow'", "1.000", "1.000", "0.000"])
table.add_row(["'light yellow'", "1.000", "1.000", "0.878"])
table.add_row(["'ivory'", "1.000", "1.000", "0.941"])
table.add_row(["'white'", "1.000", "1.000", "1.000"])
__molmol_colours_doc__.add_table(table.label)


def x11_colours(name):
    """Return the RGB colour array corresponding to the X11 colour name.

    @param name:    The X11 colour name, as defined in the /usr/X11R6/lib/X11/rgb.txt file.
    @type name:     str
    @return:        The RGB colour array.
    @rtype:         list of float
    """

    # Initialise the dictionary of colours.
    colours = {}

    # The colours as sorted in the /usr/X11R6/lib/X11/rgb.txt file.
    colours['snow']                     = [255, 250, 250]
    colours['ghost white']              = [248, 248, 255]
    colours['white smoke']              = [245, 245, 245]
    colours['gainsboro']                = [220, 220, 220]
    colours['floral white']             = [255, 250, 240]
    colours['old lace']                 = [253, 245, 230]
    colours['linen']                    = [250, 240, 230]
    colours['antique white']            = [250, 235, 215]
    colours['papaya whip']              = [255, 239, 213]
    colours['blanched almond']          = [255, 235, 205]
    colours['bisque']                   = [255, 228, 196]
    colours['peach puff']               = [255, 218, 185]
    colours['navajo white']             = [255, 222, 173]
    colours['moccasin']                 = [255, 228, 181]
    colours['cornsilk']                 = [255, 248, 220]
    colours['ivory']                    = [255, 255, 240]
    colours['lemon chiffon']            = [255, 250, 205]
    colours['seashell']                 = [255, 245, 238]
    colours['honeydew']                 = [240, 255, 240]
    colours['mint cream']               = [245, 255, 250]
    colours['azure']                    = [240, 255, 255]
    colours['alice blue']               = [240, 248, 255]
    colours['lavender']                 = [230, 230, 250]
    colours['lavender blush']           = [255, 240, 245]
    colours['misty rose']               = [255, 228, 225]
    colours['white']                    = [255, 255, 255]
    colours['black']                    = [  0,   0,   0]
    colours['dark slate grey']          = [ 47,  79,  79]
    colours['dim grey']                 = [105, 105, 105]
    colours['slate grey']               = [112, 128, 144]
    colours['light slate grey']         = [119, 136, 153]
    colours['grey']                     = [190, 190, 190]
    colours['light grey']               = [211, 211, 211]
    colours['midnight blue']            = [ 25,  25, 112]
    colours['navy']                     = [  0,   0, 128]
    colours['cornflower blue']          = [100, 149, 237]
    colours['dark slate blue']          = [ 72,  61, 139]
    colours['slate blue']               = [106,  90, 205]
    colours['medium slate blue']        = [123, 104, 238]
    colours['light slate blue']         = [132, 112, 255]
    colours['medium blue']              = [  0,   0, 205]
    colours['royal blue']               = [ 65, 105, 225]
    colours['blue']                     = [  0,   0, 255]
    colours['dodger blue']              = [ 30, 144, 255]
    colours['deep sky blue']            = [  0, 191, 255]
    colours['sky blue']                 = [135, 206, 235]
    colours['light sky blue']           = [135, 206, 250]
    colours['steel blue']               = [ 70, 130, 180]
    colours['light steel blue']         = [176, 196, 222]
    colours['light blue']               = [173, 216, 230]
    colours['powder blue']              = [176, 224, 230]
    colours['pale turquoise']           = [175, 238, 238]
    colours['dark turquoise']           = [  0, 206, 209]
    colours['medium turquoise']         = [ 72, 209, 204]
    colours['turquoise']                = [ 64, 224, 208]
    colours['cyan']                     = [  0, 255, 255]
    colours['light cyan']               = [224, 255, 255]
    colours['cadet blue']               = [ 95, 158, 160]
    colours['medium aquamarine']        = [102, 205, 170]
    colours['aquamarine']               = [127, 255, 212]
    colours['dark green']               = [  0, 100,   0]
    colours['dark olive green']         = [ 85, 107,  47]
    colours['dark sea green']           = [143, 188, 143]
    colours['sea green']                = [ 46, 139,  87]
    colours['medium sea green']         = [ 60, 179, 113]
    colours['light sea green']          = [ 32, 178, 170]
    colours['pale green']               = [152, 251, 152]
    colours['spring green']             = [  0, 255, 127]
    colours['lawn green']               = [124, 252,   0]
    colours['green']                    = [  0, 255,   0]
    colours['chartreuse']               = [127, 255,   0]
    colours['medium spring green']      = [  0, 250, 154]
    colours['green yellow']             = [173, 255,  47]
    colours['lime green']               = [ 50, 205,  50]
    colours['yellow green']             = [154, 205,  50]
    colours['forest green']             = [ 34, 139,  34]
    colours['olive drab']               = [107, 142,  35]
    colours['dark khaki']               = [189, 183, 107]
    colours['khaki']                    = [240, 230, 140]
    colours['pale goldenrod']           = [238, 232, 170]
    colours['light goldenrod yellow']   = [250, 250, 210]
    colours['light yellow']             = [255, 255, 224]
    colours['yellow']                   = [255, 255,   0]
    colours['gold']                     = [255, 215,   0]
    colours['light goldenrod']          = [238, 221, 130]
    colours['goldenrod']                = [218, 165,  32]
    colours['dark goldenrod']           = [184, 134,  11]
    colours['rosy brown']               = [188, 143, 143]
    colours['indian red']               = [205,  92,  92]
    colours['saddle brown']             = [139,  69,  19]
    colours['sienna']                   = [160,  82,  45]
    colours['peru']                     = [205, 133,  63]
    colours['burlywood']                = [222, 184, 135]
    colours['beige']                    = [245, 245, 220]
    colours['wheat']                    = [245, 222, 179]
    colours['sandy brown']              = [244, 164,  96]
    colours['tan']                      = [210, 180, 140]
    colours['chocolate']                = [210, 105,  30]
    colours['firebrick']                = [178,  34,  34]
    colours['brown']                    = [165,  42,  42]
    colours['dark salmon']              = [233, 150, 122]
    colours['salmon']                   = [250, 128, 114]
    colours['light salmon']             = [255, 160, 122]
    colours['orange']                   = [255, 165,   0]
    colours['dark orange']              = [255, 140,   0]
    colours['coral']                    = [255, 127,  80]
    colours['light coral']              = [240, 128, 128]
    colours['tomato']                   = [255,  99,  71]
    colours['orange red']               = [255,  69,   0]
    colours['red']                      = [255,   0,   0]
    colours['hot pink']                 = [255, 105, 180]
    colours['deep pink']                = [255,  20, 147]
    colours['pink']                     = [255, 192, 203]
    colours['light pink']               = [255, 182, 193]
    colours['pale violet red']          = [219, 112, 147]
    colours['maroon']                   = [176,  48,  96]
    colours['medium violet red']        = [199,  21, 133]
    colours['violet red']               = [208,  32, 144]
    colours['magenta']                  = [255,   0, 255]
    colours['violet']                   = [238, 130, 238]
    colours['plum']                     = [221, 160, 221]
    colours['orchid']                   = [218, 112, 214]
    colours['medium orchid']            = [186,  85, 211]
    colours['dark orchid']              = [153,  50, 204]
    colours['dark violet']              = [148,   0, 211]
    colours['blue violet']              = [138,  43, 226]
    colours['purple']                   = [160,  32, 240]
    colours['medium purple']            = [147, 112, 219]
    colours['thistle']                  = [216, 191, 216]
    colours['snow 1']                   = [255, 250, 250]
    colours['snow 2']                   = [238, 233, 233]
    colours['snow 3']                   = [205, 201, 201]
    colours['snow 4']                   = [139, 137, 137]
    colours['seashell 1']               = [255, 245, 238]
    colours['seashell 2']               = [238, 229, 222]
    colours['seashell 3']               = [205, 197, 191]
    colours['seashell 4']               = [139, 134, 130]
    colours['antique white 1']          = [255, 239, 219]
    colours['antique white 2']          = [238, 223, 204]
    colours['antique white 3']          = [205, 192, 176]
    colours['antique white 4']          = [139, 131, 120]
    colours['bisque 1']                 = [255, 228, 196]
    colours['bisque 2']                 = [238, 213, 183]
    colours['bisque 3']                 = [205, 183, 158]
    colours['bisque 4']                 = [139, 125, 107]
    colours['peach puff 1']             = [255, 218, 185]
    colours['peach puff 2']             = [238, 203, 173]
    colours['peach puff 3']             = [205, 175, 149]
    colours['peach puff 4']             = [139, 119, 101]
    colours['navajo white 1']           = [255, 222, 173]
    colours['navajo white 2']           = [238, 207, 161]
    colours['navajo white 3']           = [205, 179, 139]
    colours['navajo white 4']           = [139, 121,  94]
    colours['lemon chiffon 1']          = [255, 250, 205]
    colours['lemon chiffon 2']          = [238, 233, 191]
    colours['lemon chiffon 3']          = [205, 201, 165]
    colours['lemon chiffon 4']          = [139, 137, 112]
    colours['cornsilk 1']               = [255, 248, 220]
    colours['cornsilk 2']               = [238, 232, 205]
    colours['cornsilk 3']               = [205, 200, 177]
    colours['cornsilk 4']               = [139, 136, 120]
    colours['ivory 1']                  = [255, 255, 240]
    colours['ivory 2']                  = [238, 238, 224]
    colours['ivory 3']                  = [205, 205, 193]
    colours['ivory 4']                  = [139, 139, 131]
    colours['honeydew 1']               = [240, 255, 240]
    colours['honeydew 2']               = [224, 238, 224]
    colours['honeydew 3']               = [193, 205, 193]
    colours['honeydew 4']               = [131, 139, 131]
    colours['lavender blush 1']         = [255, 240, 245]
    colours['lavender blush 2']         = [238, 224, 229]
    colours['lavender blush 3']         = [205, 193, 197]
    colours['lavender blush 4']         = [139, 131, 134]
    colours['misty rose 1']             = [255, 228, 225]
    colours['misty rose 2']             = [238, 213, 210]
    colours['misty rose 3']             = [205, 183, 181]
    colours['misty rose 4']             = [139, 125, 123]
    colours['azure 1']                  = [240, 255, 255]
    colours['azure 2']                  = [224, 238, 238]
    colours['azure 3']                  = [193, 205, 205]
    colours['azure 4']                  = [131, 139, 139]
    colours['slate blue 1']             = [131, 111, 255]
    colours['slate blue 2']             = [122, 103, 238]
    colours['slate blue 3']             = [105,  89, 205]
    colours['slate blue 4']             = [ 71,  60, 139]
    colours['royal blue 1']             = [ 72, 118, 255]
    colours['royal blue 2']             = [ 67, 110, 238]
    colours['royal blue 3']             = [ 58,  95, 205]
    colours['royal blue 4']             = [ 39,  64, 139]
    colours['blue 1']                   = [  0,   0, 255]
    colours['blue 2']                   = [  0,   0, 238]
    colours['blue 3']                   = [  0,   0, 205]
    colours['blue 4']                   = [  0,   0, 139]
    colours['dodger blue 1']            = [ 30, 144, 255]
    colours['dodger blue 2']            = [ 28, 134, 238]
    colours['dodger blue 3']            = [ 24, 116, 205]
    colours['dodger blue 4']            = [ 16,  78, 139]
    colours['steel blue 1']             = [ 99, 184, 255]
    colours['steel blue 2']             = [ 92, 172, 238]
    colours['steel blue 3']             = [ 79, 148, 205]
    colours['steel blue 4']             = [ 54, 100, 139]
    colours['deep sky blue 1']          = [  0, 191, 255]
    colours['deep sky blue 2']          = [  0, 178, 238]
    colours['deep sky blue 3']          = [  0, 154, 205]
    colours['deep sky blue 4']          = [  0, 104, 139]
    colours['sky blue 1']               = [135, 206, 255]
    colours['sky blue 2']               = [126, 192, 238]
    colours['sky blue 3']               = [108, 166, 205]
    colours['sky blue 4']               = [ 74, 112, 139]
    colours['light sky blue 1']         = [176, 226, 255]
    colours['light sky blue 2']         = [164, 211, 238]
    colours['light sky blue 3']         = [141, 182, 205]
    colours['light sky blue 4']         = [ 96, 123, 139]
    colours['slate grey 1']             = [198, 226, 255]
    colours['slate grey 2']             = [185, 211, 238]
    colours['slate grey 3']             = [159, 182, 205]
    colours['slate grey 4']             = [108, 123, 139]
    colours['light steel blue 1']       = [202, 225, 255]
    colours['light steel blue 2']       = [188, 210, 238]
    colours['light steel blue 3']       = [162, 181, 205]
    colours['light steel blue 4']       = [110, 123, 139]
    colours['light blue 1']             = [191, 239, 255]
    colours['light blue 2']             = [178, 223, 238]
    colours['light blue 3']             = [154, 192, 205]
    colours['light blue 4']             = [104, 131, 139]
    colours['light cyan 1']             = [224, 255, 255]
    colours['light cyan 2']             = [209, 238, 238]
    colours['light cyan 3']             = [180, 205, 205]
    colours['light cyan 4']             = [122, 139, 139]
    colours['pale turquoise 1']         = [187, 255, 255]
    colours['pale turquoise 2']         = [174, 238, 238]
    colours['pale turquoise 3']         = [150, 205, 205]
    colours['pale turquoise 4']         = [102, 139, 139]
    colours['cadet blue 1']             = [152, 245, 255]
    colours['cadet blue 2']             = [142, 229, 238]
    colours['cadet blue 3']             = [122, 197, 205]
    colours['cadet blue 4']             = [ 83, 134, 139]
    colours['turquoise 1']              = [  0, 245, 255]
    colours['turquoise 2']              = [  0, 229, 238]
    colours['turquoise 3']              = [  0, 197, 205]
    colours['turquoise 4']              = [  0, 134, 139]
    colours['cyan 1']                   = [  0, 255, 255]
    colours['cyan 2']                   = [  0, 238, 238]
    colours['cyan 3']                   = [  0, 205, 205]
    colours['cyan 4']                   = [  0, 139, 139]
    colours['dark slate grey 1']        = [151, 255, 255]
    colours['dark slate grey 2']        = [141, 238, 238]
    colours['dark slate grey 3']        = [121, 205, 205]
    colours['dark slate grey 4']        = [ 82, 139, 139]
    colours['aquamarine 1']             = [127, 255, 212]
    colours['aquamarine 2']             = [118, 238, 198]
    colours['aquamarine 3']             = [102, 205, 170]
    colours['aquamarine 4']             = [ 69, 139, 116]
    colours['dark sea green 1']         = [193, 255, 193]
    colours['dark sea green 2']         = [180, 238, 180]
    colours['dark sea green 3']         = [155, 205, 155]
    colours['dark sea green 4']         = [105, 139, 105]
    colours['sea green 1']              = [ 84, 255, 159]
    colours['sea green 2']              = [ 78, 238, 148]
    colours['sea green 3']              = [ 67, 205, 128]
    colours['sea green 4']              = [ 46, 139,  87]
    colours['pale green 1']             = [154, 255, 154]
    colours['pale green 2']             = [144, 238, 144]
    colours['pale green 3']             = [124, 205, 124]
    colours['pale green 4']             = [ 84, 139,  84]
    colours['spring green 1']           = [  0, 255, 127]
    colours['spring green 2']           = [  0, 238, 118]
    colours['spring green 3']           = [  0, 205, 102]
    colours['spring green 4']           = [  0, 139,  69]
    colours['green 1']                  = [  0, 255,   0]
    colours['green 2']                  = [  0, 238,   0]
    colours['green 3']                  = [  0, 205,   0]
    colours['green 4']                  = [  0, 139,   0]
    colours['chartreuse 1']             = [127, 255,   0]
    colours['chartreuse 2']             = [118, 238,   0]
    colours['chartreuse 3']             = [102, 205,   0]
    colours['chartreuse 4']             = [ 69, 139,   0]
    colours['olive drab 1']             = [192, 255,  62]
    colours['olive drab 2']             = [179, 238,  58]
    colours['olive drab 3']             = [154, 205,  50]
    colours['olive drab 4']             = [105, 139,  34]
    colours['dark olive green 1']       = [202, 255, 112]
    colours['dark olive green 2']       = [188, 238, 104]
    colours['dark olive green 3']       = [162, 205,  90]
    colours['dark olive green 4']       = [110, 139,  61]
    colours['khaki 1']                  = [255, 246, 143]
    colours['khaki 2']                  = [238, 230, 133]
    colours['khaki 3']                  = [205, 198, 115]
    colours['khaki 4']                  = [139, 134,  78]
    colours['light goldenrod 1']        = [255, 236, 139]
    colours['light goldenrod 2']        = [238, 220, 130]
    colours['light goldenrod 3']        = [205, 190, 112]
    colours['light goldenrod 4']        = [139, 129,  76]
    colours['light yellow 1']           = [255, 255, 224]
    colours['light yellow 2']           = [238, 238, 209]
    colours['light yellow 3']           = [205, 205, 180]
    colours['light yellow 4']           = [139, 139, 122]
    colours['yellow 1']                 = [255, 255,   0]
    colours['yellow 2']                 = [238, 238,   0]
    colours['yellow 3']                 = [205, 205,   0]
    colours['yellow 4']                 = [139, 139,   0]
    colours['gold 1']                   = [255, 215,   0]
    colours['gold 2']                   = [238, 201,   0]
    colours['gold 3']                   = [205, 173,   0]
    colours['gold 4']                   = [139, 117,   0]
    colours['goldenrod 1']              = [255, 193,  37]
    colours['goldenrod 2']              = [238, 180,  34]
    colours['goldenrod 3']              = [205, 155,  29]
    colours['goldenrod 4']              = [139, 105,  20]
    colours['dark goldenrod 1']         = [255, 185,  15]
    colours['dark goldenrod 2']         = [238, 173,  14]
    colours['dark goldenrod 3']         = [205, 149,  12]
    colours['dark goldenrod 4']         = [139, 101,   8]
    colours['rosy brown 1']             = [255, 193, 193]
    colours['rosy brown 2']             = [238, 180, 180]
    colours['rosy brown 3']             = [205, 155, 155]
    colours['rosy brown 4']             = [139, 105, 105]
    colours['indian red 1']             = [255, 106, 106]
    colours['indian red 2']             = [238,  99,  99]
    colours['indian red 3']             = [205,  85,  85]
    colours['indian red 4']             = [139,  58,  58]
    colours['sienna 1']                 = [255, 130,  71]
    colours['sienna 2']                 = [238, 121,  66]
    colours['sienna 3']                 = [205, 104,  57]
    colours['sienna 4']                 = [139,  71,  38]
    colours['burlywood 1']              = [255, 211, 155]
    colours['burlywood 2']              = [238, 197, 145]
    colours['burlywood 3']              = [205, 170, 125]
    colours['burlywood 4']              = [139, 115,  85]
    colours['wheat 1']                  = [255, 231, 186]
    colours['wheat 2']                  = [238, 216, 174]
    colours['wheat 3']                  = [205, 186, 150]
    colours['wheat 4']                  = [139, 126, 102]
    colours['tan 1']                    = [255, 165,  79]
    colours['tan 2']                    = [238, 154,  73]
    colours['tan 3']                    = [205, 133,  63]
    colours['tan 4']                    = [139,  90,  43]
    colours['chocolate 1']              = [255, 127,  36]
    colours['chocolate 2']              = [238, 118,  33]
    colours['chocolate 3']              = [205, 102,  29]
    colours['chocolate 4']              = [139,  69,  19]
    colours['firebrick 1']              = [255,  48,  48]
    colours['firebrick 2']              = [238,  44,  44]
    colours['firebrick 3']              = [205,  38,  38]
    colours['firebrick 4']              = [139,  26,  26]
    colours['brown 1']                  = [255,  64,  64]
    colours['brown 2']                  = [238,  59,  59]
    colours['brown 3']                  = [205,  51,  51]
    colours['brown 4']                  = [139,  35,  35]
    colours['salmon 1']                 = [255, 140, 105]
    colours['salmon 2']                 = [238, 130,  98]
    colours['salmon 3']                 = [205, 112,  84]
    colours['salmon 4']                 = [139,  76,  57]
    colours['light salmon 1']           = [255, 160, 122]
    colours['light salmon 2']           = [238, 149, 114]
    colours['light salmon 3']           = [205, 129,  98]
    colours['light salmon 4']           = [139,  87,  66]
    colours['orange 1']                 = [255, 165,   0]
    colours['orange 2']                 = [238, 154,   0]
    colours['orange 3']                 = [205, 133,   0]
    colours['orange 4']                 = [139,  90,   0]
    colours['dark orange 1']            = [255, 127,   0]
    colours['dark orange 2']            = [238, 118,   0]
    colours['dark orange 3']            = [205, 102,   0]
    colours['dark orange 4']            = [139,  69,   0]
    colours['coral 1']                  = [255, 114,  86]
    colours['coral 2']                  = [238, 106,  80]
    colours['coral 3']                  = [205,  91,  69]
    colours['coral 4']                  = [139,  62,  47]
    colours['tomato 1']                 = [255,  99,  71]
    colours['tomato 2']                 = [238,  92,  66]
    colours['tomato 3']                 = [205,  79,  57]
    colours['tomato 4']                 = [139,  54,  38]
    colours['orange red 1']             = [255,  69,   0]
    colours['orange red 2']             = [238,  64,   0]
    colours['orange red 3']             = [205,  55,   0]
    colours['orange red 4']             = [139,  37,   0]
    colours['red 1']                    = [255,   0,   0]
    colours['red 2']                    = [238,   0,   0]
    colours['red 3']                    = [205,   0,   0]
    colours['red 4']                    = [139,   0,   0]
    colours['deep pink 1']              = [255,  20, 147]
    colours['deep pink 2']              = [238,  18, 137]
    colours['deep pink 3']              = [205,  16, 118]
    colours['deep pink 4']              = [139,  10,  80]
    colours['hot pink 1']               = [255, 110, 180]
    colours['hot pink 2']               = [238, 106, 167]
    colours['hot pink 3']               = [205,  96, 144]
    colours['hot pink 4']               = [139,  58,  98]
    colours['pink 1']                   = [255, 181, 197]
    colours['pink 2']                   = [238, 169, 184]
    colours['pink 3']                   = [205, 145, 158]
    colours['pink 4']                   = [139,  99, 108]
    colours['light pink 1']             = [255, 174, 185]
    colours['light pink 2']             = [238, 162, 173]
    colours['light pink 3']             = [205, 140, 149]
    colours['light pink 4']             = [139,  95, 101]
    colours['pale violet red 1']        = [255, 130, 171]
    colours['pale violet red 2']        = [238, 121, 159]
    colours['pale violet red 3']        = [205, 104, 137]
    colours['pale violet red 4']        = [139,  71,  93]
    colours['maroon 1']                 = [255,  52, 179]
    colours['maroon 2']                 = [238,  48, 167]
    colours['maroon 3']                 = [205,  41, 144]
    colours['maroon 4']                 = [139,  28,  98]
    colours['violet red 1']             = [255,  62, 150]
    colours['violet red 2']             = [238,  58, 140]
    colours['violet red 3']             = [205,  50, 120]
    colours['violet red 4']             = [139,  34,  82]
    colours['magenta 1']                = [255,   0, 255]
    colours['magenta 2']                = [238,   0, 238]
    colours['magenta 3']                = [205,   0, 205]
    colours['magenta 4']                = [139,   0, 139]
    colours['orchid 1']                 = [255, 131, 250]
    colours['orchid 2']                 = [238, 122, 233]
    colours['orchid 3']                 = [205, 105, 201]
    colours['orchid 4']                 = [139,  71, 137]
    colours['plum 1']                   = [255, 187, 255]
    colours['plum 2']                   = [238, 174, 238]
    colours['plum 3']                   = [205, 150, 205]
    colours['plum 4']                   = [139, 102, 139]
    colours['medium orchid 1']          = [224, 102, 255]
    colours['medium orchid 2']          = [209,  95, 238]
    colours['medium orchid 3']          = [180,  82, 205]
    colours['medium orchid 4']          = [122,  55, 139]
    colours['dark orchid 1']            = [191,  62, 255]
    colours['dark orchid 2']            = [178,  58, 238]
    colours['dark orchid 3']            = [154,  50, 205]
    colours['dark orchid 4']            = [104,  34, 139]
    colours['purple 1']                 = [155,  48, 255]
    colours['purple 2']                 = [145,  44, 238]
    colours['purple 3']                 = [125,  38, 205]
    colours['purple 4']                 = [ 85,  26, 139]
    colours['medium purple 1']          = [171, 130, 255]
    colours['medium purple 2']          = [159, 121, 238]
    colours['medium purple 3']          = [137, 104, 205]
    colours['medium purple 4']          = [ 93,  71, 139]
    colours['thistle 1']                = [255, 225, 255]
    colours['thistle 2']                = [238, 210, 238]
    colours['thistle 3']                = [205, 181, 205]
    colours['thistle 4']                = [139, 123, 139]
    colours['grey 0']                   = [  0,   0,   0]
    colours['grey 1']                   = [  3,   3,   3]
    colours['grey 2']                   = [  5,   5,   5]
    colours['grey 3']                   = [  8,   8,   8]
    colours['grey 4']                   = [ 10,  10,  10]
    colours['grey 5']                   = [ 13,  13,  13]
    colours['grey 6']                   = [ 15,  15,  15]
    colours['grey 7']                   = [ 18,  18,  18]
    colours['grey 8']                   = [ 20,  20,  20]
    colours['grey 9']                   = [ 23,  23,  23]
    colours['grey 10']                  = [ 26,  26,  26]
    colours['grey 11']                  = [ 28,  28,  28]
    colours['grey 12']                  = [ 31,  31,  31]
    colours['grey 13']                  = [ 33,  33,  33]
    colours['grey 14']                  = [ 36,  36,  36]
    colours['grey 15']                  = [ 38,  38,  38]
    colours['grey 16']                  = [ 41,  41,  41]
    colours['grey 17']                  = [ 43,  43,  43]
    colours['grey 18']                  = [ 46,  46,  46]
    colours['grey 19']                  = [ 48,  48,  48]
    colours['grey 20']                  = [ 51,  51,  51]
    colours['grey 21']                  = [ 54,  54,  54]
    colours['grey 22']                  = [ 56,  56,  56]
    colours['grey 23']                  = [ 59,  59,  59]
    colours['grey 24']                  = [ 61,  61,  61]
    colours['grey 25']                  = [ 64,  64,  64]
    colours['grey 26']                  = [ 66,  66,  66]
    colours['grey 27']                  = [ 69,  69,  69]
    colours['grey 28']                  = [ 71,  71,  71]
    colours['grey 29']                  = [ 74,  74,  74]
    colours['grey 30']                  = [ 77,  77,  77]
    colours['grey 31']                  = [ 79,  79,  79]
    colours['grey 32']                  = [ 82,  82,  82]
    colours['grey 33']                  = [ 84,  84,  84]
    colours['grey 34']                  = [ 87,  87,  87]
    colours['grey 35']                  = [ 89,  89,  89]
    colours['grey 36']                  = [ 92,  92,  92]
    colours['grey 37']                  = [ 94,  94,  94]
    colours['grey 38']                  = [ 97,  97,  97]
    colours['grey 39']                  = [ 99,  99,  99]
    colours['grey 40']                  = [102, 102, 102]
    colours['grey 41']                  = [105, 105, 105]
    colours['grey 42']                  = [107, 107, 107]
    colours['grey 43']                  = [110, 110, 110]
    colours['grey 44']                  = [112, 112, 112]
    colours['grey 45']                  = [115, 115, 115]
    colours['grey 46']                  = [117, 117, 117]
    colours['grey 47']                  = [120, 120, 120]
    colours['grey 48']                  = [122, 122, 122]
    colours['grey 49']                  = [125, 125, 125]
    colours['grey 50']                  = [127, 127, 127]
    colours['grey 51']                  = [130, 130, 130]
    colours['grey 52']                  = [133, 133, 133]
    colours['grey 53']                  = [135, 135, 135]
    colours['grey 54']                  = [138, 138, 138]
    colours['grey 55']                  = [140, 140, 140]
    colours['grey 56']                  = [143, 143, 143]
    colours['grey 57']                  = [145, 145, 145]
    colours['grey 58']                  = [148, 148, 148]
    colours['grey 59']                  = [150, 150, 150]
    colours['grey 60']                  = [153, 153, 153]
    colours['grey 61']                  = [156, 156, 156]
    colours['grey 62']                  = [158, 158, 158]
    colours['grey 63']                  = [161, 161, 161]
    colours['grey 64']                  = [163, 163, 163]
    colours['grey 65']                  = [166, 166, 166]
    colours['grey 66']                  = [168, 168, 168]
    colours['grey 67']                  = [171, 171, 171]
    colours['grey 68']                  = [173, 173, 173]
    colours['grey 69']                  = [176, 176, 176]
    colours['grey 70']                  = [179, 179, 179]
    colours['grey 71']                  = [181, 181, 181]
    colours['grey 72']                  = [184, 184, 184]
    colours['grey 73']                  = [186, 186, 186]
    colours['grey 74']                  = [189, 189, 189]
    colours['grey 75']                  = [191, 191, 191]
    colours['grey 76']                  = [194, 194, 194]
    colours['grey 77']                  = [196, 196, 196]
    colours['grey 78']                  = [199, 199, 199]
    colours['grey 79']                  = [201, 201, 201]
    colours['grey 80']                  = [204, 204, 204]
    colours['grey 81']                  = [207, 207, 207]
    colours['grey 82']                  = [209, 209, 209]
    colours['grey 83']                  = [212, 212, 212]
    colours['grey 84']                  = [214, 214, 214]
    colours['grey 85']                  = [217, 217, 217]
    colours['grey 86']                  = [219, 219, 219]
    colours['grey 87']                  = [222, 222, 222]
    colours['grey 88']                  = [224, 224, 224]
    colours['grey 89']                  = [227, 227, 227]
    colours['grey 90']                  = [229, 229, 229]
    colours['grey 91']                  = [232, 232, 232]
    colours['grey 92']                  = [235, 235, 235]
    colours['grey 93']                  = [237, 237, 237]
    colours['grey 94']                  = [240, 240, 240]
    colours['grey 95']                  = [242, 242, 242]
    colours['grey 96']                  = [245, 245, 245]
    colours['grey 97']                  = [247, 247, 247]
    colours['grey 98']                  = [250, 250, 250]
    colours['grey 99']                  = [252, 252, 252]
    colours['grey 100']                 = [255, 255, 255]
    colours['dark grey']                = [169, 169, 169]
    colours['dark blue']                = [  0,   0, 139]
    colours['dark cyan']                = [  0, 139, 139]
    colours['dark magenta']             = [139,   0, 139]
    colours['dark red']                 = [139,   0,   0]
    colours['light green']              = [144, 238, 144]

    # Invalid colour string.
    if name not in colours:
        raise RelaxInvalidColourError(name)

    # Return the RGB colour array (in numpy format and between 0 and 1).
    return array(colours[name], float64) / 255.

# User function documentation.
__x11_colours_doc__ = Desc_container("X11 RGB colour arrays")
__x11_colours_doc__.add_paragraph("The following table is the list of X11 colour names and their corresponding RGB colour values ranging from 0 to 255.")
table = uf_tables.add_table(label="table: X11 colours", caption="X11 colour names and corresponding RGB colour values", spacing=False, longtable=True)
table.add_headings(["Name", "Red", "Green", "Blue"])
table.add_row(["snow", "255", "250", "250"])
table.add_row(["ghost white", "248", "248", "255"])
table.add_row(["white smoke", "245", "245", "245"])
table.add_row(["gainsboro", "220", "220", "220"])
table.add_row(["floral white", "255", "250", "240"])
table.add_row(["old lace", "253", "245", "230"])
table.add_row(["linen", "250", "240", "230"])
table.add_row(["antique white", "250", "235", "215"])
table.add_row(["papaya whip", "255", "239", "213"])
table.add_row(["blanched almond", "255", "235", "205"])
table.add_row(["bisque", "255", "228", "196"])
table.add_row(["peach puff", "255", "218", "185"])
table.add_row(["navajo white", "255", "222", "173"])
table.add_row(["moccasin", "255", "228", "181"])
table.add_row(["cornsilk", "255", "248", "220"])
table.add_row(["ivory", "255", "255", "240"])
table.add_row(["lemon chiffon", "255", "250", "205"])
table.add_row(["seashell", "255", "245", "238"])
table.add_row(["honeydew", "240", "255", "240"])
table.add_row(["mint cream", "245", "255", "250"])
table.add_row(["azure", "240", "255", "255"])
table.add_row(["alice blue", "240", "248", "255"])
table.add_row(["lavender", "230", "230", "250"])
table.add_row(["lavender blush", "255", "240", "245"])
table.add_row(["misty rose", "255", "228", "225"])
table.add_row(["white", "255", "255", "255"])
table.add_row(["black", "0", "0", "0"])
table.add_row(["dark slate grey", "47", "79", "79"])
table.add_row(["dim grey", "105", "105", "105"])
table.add_row(["slate grey", "112", "128", "144"])
table.add_row(["light slate grey", "119", "136", "153"])
table.add_row(["grey", "190", "190", "190"])
table.add_row(["light grey", "211", "211", "211"])
table.add_row(["midnight blue", "25", "25", "112"])
table.add_row(["navy", "0", "0", "128"])
table.add_row(["cornflower blue", "100", "149", "237"])
table.add_row(["dark slate blue", "72", "61", "139"])
table.add_row(["slate blue", "106", "90", "205"])
table.add_row(["medium slate blue", "123", "104", "238"])
table.add_row(["light slate blue", "132", "112", "255"])
table.add_row(["medium blue", "0", "0", "205"])
table.add_row(["royal blue", "65", "105", "225"])
table.add_row(["blue", "0", "0", "255"])
table.add_row(["dodger blue", "30", "144", "255"])
table.add_row(["deep sky blue", "0", "191", "255"])
table.add_row(["sky blue", "135", "206", "235"])
table.add_row(["light sky blue", "135", "206", "250"])
table.add_row(["steel blue", "70", "130", "180"])
table.add_row(["light steel blue", "176", "196", "222"])
table.add_row(["light blue", "173", "216", "230"])
table.add_row(["powder blue", "176", "224", "230"])
table.add_row(["pale turquoise", "175", "238", "238"])
table.add_row(["dark turquoise", "0", "206", "209"])
table.add_row(["medium turquoise", "72", "209", "204"])
table.add_row(["turquoise", "64", "224", "208"])
table.add_row(["cyan", "0", "255", "255"])
table.add_row(["light cyan", "224", "255", "255"])
table.add_row(["cadet blue", "95", "158", "160"])
table.add_row(["medium aquamarine", "102", "205", "170"])
table.add_row(["aquamarine", "127", "255", "212"])
table.add_row(["dark green", "0", "100", "0"])
table.add_row(["dark olive green", "85", "107", "47"])
table.add_row(["dark sea green", "143", "188", "143"])
table.add_row(["sea green", "46", "139", "87"])
table.add_row(["medium sea green", "60", "179", "113"])
table.add_row(["light sea green", "32", "178", "170"])
table.add_row(["pale green", "152", "251", "152"])
table.add_row(["spring green", "0", "255", "127"])
table.add_row(["lawn green", "124", "252", "0"])
table.add_row(["green", "0", "255", "0"])
table.add_row(["chartreuse", "127", "255", "0"])
table.add_row(["medium spring green", "0", "250", "154"])
table.add_row(["green yellow", "173", "255", "47"])
table.add_row(["lime green", "50", "205", "50"])
table.add_row(["yellow green", "154", "205", "50"])
table.add_row(["forest green", "34", "139", "34"])
table.add_row(["olive drab", "107", "142", "35"])
table.add_row(["dark khaki", "189", "183", "107"])
table.add_row(["khaki", "240", "230", "140"])
table.add_row(["pale goldenrod", "238", "232", "170"])
table.add_row(["light goldenrod yellow", "250", "250", "210"])
table.add_row(["light yellow", "255", "255", "224"])
table.add_row(["yellow", "255", "255", "0"])
table.add_row(["gold", "255", "215", "0"])
table.add_row(["light goldenrod", "238", "221", "130"])
table.add_row(["goldenrod", "218", "165", "32"])
table.add_row(["dark goldenrod", "184", "134", "11"])
table.add_row(["rosy brown", "188", "143", "143"])
table.add_row(["indian red", "205", "92", "92"])
table.add_row(["saddle brown", "139", "69", "19"])
table.add_row(["sienna", "160", "82", "45"])
table.add_row(["peru", "205", "133", "63"])
table.add_row(["burlywood", "222", "184", "135"])
table.add_row(["beige", "245", "245", "220"])
table.add_row(["wheat", "245", "222", "179"])
table.add_row(["sandy brown", "244", "164", "96"])
table.add_row(["tan", "210", "180", "140"])
table.add_row(["chocolate", "210", "105", "30"])
table.add_row(["firebrick", "178", "34", "34"])
table.add_row(["brown", "165", "42", "42"])
table.add_row(["dark salmon", "233", "150", "122"])
table.add_row(["salmon", "250", "128", "114"])
table.add_row(["light salmon", "255", "160", "122"])
table.add_row(["orange", "255", "165", "0"])
table.add_row(["dark orange", "255", "140", "0"])
table.add_row(["coral", "255", "127", "80"])
table.add_row(["light coral", "240", "128", "128"])
table.add_row(["tomato", "255", "99", "71"])
table.add_row(["orange red", "255", "69", "0"])
table.add_row(["red", "255", "0", "0"])
table.add_row(["hot pink", "255", "105", "180"])
table.add_row(["deep pink", "255", "20", "147"])
table.add_row(["pink", "255", "192", "203"])
table.add_row(["light pink", "255", "182", "193"])
table.add_row(["pale violet red", "219", "112", "147"])
table.add_row(["maroon", "176", "48", "96"])
table.add_row(["medium violet red", "199", "21", "133"])
table.add_row(["violet red", "208", "32", "144"])
table.add_row(["magenta", "255", "0", "255"])
table.add_row(["violet", "238", "130", "238"])
table.add_row(["plum", "221", "160", "221"])
table.add_row(["orchid", "218", "112", "214"])
table.add_row(["medium orchid", "186", "85", "211"])
table.add_row(["dark orchid", "153", "50", "204"])
table.add_row(["dark violet", "148", "0", "211"])
table.add_row(["blue violet", "138", "43", "226"])
table.add_row(["purple", "160", "32", "240"])
table.add_row(["medium purple", "147", "112", "219"])
table.add_row(["thistle", "216", "191", "216"])
table.add_row(["snow 1", "255", "250", "250"])
table.add_row(["snow 2", "238", "233", "233"])
table.add_row(["snow 3", "205", "201", "201"])
table.add_row(["snow 4", "139", "137", "137"])
table.add_row(["seashell 1", "255", "245", "238"])
table.add_row(["seashell 2", "238", "229", "222"])
table.add_row(["seashell 3", "205", "197", "191"])
table.add_row(["seashell 4", "139", "134", "130"])
table.add_row(["antique white 1", "255", "239", "219"])
table.add_row(["antique white 2", "238", "223", "204"])
table.add_row(["antique white 3", "205", "192", "176"])
table.add_row(["antique white 4", "139", "131", "120"])
table.add_row(["bisque 1", "255", "228", "196"])
table.add_row(["bisque 2", "238", "213", "183"])
table.add_row(["bisque 3", "205", "183", "158"])
table.add_row(["bisque 4", "139", "125", "107"])
table.add_row(["peach puff 1", "255", "218", "185"])
table.add_row(["peach puff 2", "238", "203", "173"])
table.add_row(["peach puff 3", "205", "175", "149"])
table.add_row(["peach puff 4", "139", "119", "101"])
table.add_row(["navajo white 1", "255", "222", "173"])
table.add_row(["navajo white 2", "238", "207", "161"])
table.add_row(["navajo white 3", "205", "179", "139"])
table.add_row(["navajo white 4", "139", "121", "94"])
table.add_row(["lemon chiffon 1", "255", "250", "205"])
table.add_row(["lemon chiffon 2", "238", "233", "191"])
table.add_row(["lemon chiffon 3", "205", "201", "165"])
table.add_row(["lemon chiffon 4", "139", "137", "112"])
table.add_row(["cornsilk 1", "255", "248", "220"])
table.add_row(["cornsilk 2", "238", "232", "205"])
table.add_row(["cornsilk 3", "205", "200", "177"])
table.add_row(["cornsilk 4", "139", "136", "120"])
table.add_row(["ivory 1", "255", "255", "240"])
table.add_row(["ivory 2", "238", "238", "224"])
table.add_row(["ivory 3", "205", "205", "193"])
table.add_row(["ivory 4", "139", "139", "131"])
table.add_row(["honeydew 1", "240", "255", "240"])
table.add_row(["honeydew 2", "224", "238", "224"])
table.add_row(["honeydew 3", "193", "205", "193"])
table.add_row(["honeydew 4", "131", "139", "131"])
table.add_row(["lavender blush 1", "255", "240", "245"])
table.add_row(["lavender blush 2", "238", "224", "229"])
table.add_row(["lavender blush 3", "205", "193", "197"])
table.add_row(["lavender blush 4", "139", "131", "134"])
table.add_row(["misty rose 1", "255", "228", "225"])
table.add_row(["misty rose 2", "238", "213", "210"])
table.add_row(["misty rose 3", "205", "183", "181"])
table.add_row(["misty rose 4", "139", "125", "123"])
table.add_row(["azure 1", "240", "255", "255"])
table.add_row(["azure 2", "224", "238", "238"])
table.add_row(["azure 3", "193", "205", "205"])
table.add_row(["azure 4", "131", "139", "139"])
table.add_row(["slate blue 1", "131", "111", "255"])
table.add_row(["slate blue 2", "122", "103", "238"])
table.add_row(["slate blue 3", "105", "89", "205"])
table.add_row(["slate blue 4", "71", "60", "139"])
table.add_row(["royal blue 1", "72", "118", "255"])
table.add_row(["royal blue 2", "67", "110", "238"])
table.add_row(["royal blue 3", "58", "95", "205"])
table.add_row(["royal blue 4", "39", "64", "139"])
table.add_row(["blue 1", "0", "0", "255"])
table.add_row(["blue 2", "0", "0", "238"])
table.add_row(["blue 3", "0", "0", "205"])
table.add_row(["blue 4", "0", "0", "139"])
table.add_row(["dodger blue 1", "30", "144", "255"])
table.add_row(["dodger blue 2", "28", "134", "238"])
table.add_row(["dodger blue 3", "24", "116", "205"])
table.add_row(["dodger blue 4", "16", "78", "139"])
table.add_row(["steel blue 1", "99", "184", "255"])
table.add_row(["steel blue 2", "92", "172", "238"])
table.add_row(["steel blue 3", "79", "148", "205"])
table.add_row(["steel blue 4", "54", "100", "139"])
table.add_row(["deep sky blue 1", "0", "191", "255"])
table.add_row(["deep sky blue 2", "0", "178", "238"])
table.add_row(["deep sky blue 3", "0", "154", "205"])
table.add_row(["deep sky blue 4", "0", "104", "139"])
table.add_row(["sky blue 1", "135", "206", "255"])
table.add_row(["sky blue 2", "126", "192", "238"])
table.add_row(["sky blue 3", "108", "166", "205"])
table.add_row(["sky blue 4", "74", "112", "139"])
table.add_row(["light sky blue 1", "176", "226", "255"])
table.add_row(["light sky blue 2", "164", "211", "238"])
table.add_row(["light sky blue 3", "141", "182", "205"])
table.add_row(["light sky blue 4", "96", "123", "139"])
table.add_row(["slate grey 1", "198", "226", "255"])
table.add_row(["slate grey 2", "185", "211", "238"])
table.add_row(["slate grey 3", "159", "182", "205"])
table.add_row(["slate grey 4", "108", "123", "139"])
table.add_row(["light steel blue 1", "202", "225", "255"])
table.add_row(["light steel blue 2", "188", "210", "238"])
table.add_row(["light steel blue 3", "162", "181", "205"])
table.add_row(["light steel blue 4", "110", "123", "139"])
table.add_row(["light blue 1", "191", "239", "255"])
table.add_row(["light blue 2", "178", "223", "238"])
table.add_row(["light blue 3", "154", "192", "205"])
table.add_row(["light blue 4", "104", "131", "139"])
table.add_row(["light cyan 1", "224", "255", "255"])
table.add_row(["light cyan 2", "209", "238", "238"])
table.add_row(["light cyan 3", "180", "205", "205"])
table.add_row(["light cyan 4", "122", "139", "139"])
table.add_row(["pale turquoise 1", "187", "255", "255"])
table.add_row(["pale turquoise 2", "174", "238", "238"])
table.add_row(["pale turquoise 3", "150", "205", "205"])
table.add_row(["pale turquoise 4", "102", "139", "139"])
table.add_row(["cadet blue 1", "152", "245", "255"])
table.add_row(["cadet blue 2", "142", "229", "238"])
table.add_row(["cadet blue 3", "122", "197", "205"])
table.add_row(["cadet blue 4", "83", "134", "139"])
table.add_row(["turquoise 1", "0", "245", "255"])
table.add_row(["turquoise 2", "0", "229", "238"])
table.add_row(["turquoise 3", "0", "197", "205"])
table.add_row(["turquoise 4", "0", "134", "139"])
table.add_row(["cyan 1", "0", "255", "255"])
table.add_row(["cyan 2", "0", "238", "238"])
table.add_row(["cyan 3", "0", "205", "205"])
table.add_row(["cyan 4", "0", "139", "139"])
table.add_row(["dark slate grey 1", "151", "255", "255"])
table.add_row(["dark slate grey 2", "141", "238", "238"])
table.add_row(["dark slate grey 3", "121", "205", "205"])
table.add_row(["dark slate grey 4", "82", "139", "139"])
table.add_row(["aquamarine 1", "127", "255", "212"])
table.add_row(["aquamarine 2", "118", "238", "198"])
table.add_row(["aquamarine 3", "102", "205", "170"])
table.add_row(["aquamarine 4", "69", "139", "116"])
table.add_row(["dark sea green 1", "193", "255", "193"])
table.add_row(["dark sea green 2", "180", "238", "180"])
table.add_row(["dark sea green 3", "155", "205", "155"])
table.add_row(["dark sea green 4", "105", "139", "105"])
table.add_row(["sea green 1", "84", "255", "159"])
table.add_row(["sea green 2", "78", "238", "148"])
table.add_row(["sea green 3", "67", "205", "128"])
table.add_row(["sea green 4", "46", "139", "87"])
table.add_row(["pale green 1", "154", "255", "154"])
table.add_row(["pale green 2", "144", "238", "144"])
table.add_row(["pale green 3", "124", "205", "124"])
table.add_row(["pale green 4", "84", "139", "84"])
table.add_row(["spring green 1", "0", "255", "127"])
table.add_row(["spring green 2", "0", "238", "118"])
table.add_row(["spring green 3", "0", "205", "102"])
table.add_row(["spring green 4", "0", "139", "69"])
table.add_row(["green 1", "0", "255", "0"])
table.add_row(["green 2", "0", "238", "0"])
table.add_row(["green 3", "0", "205", "0"])
table.add_row(["green 4", "0", "139", "0"])
table.add_row(["chartreuse 1", "127", "255", "0"])
table.add_row(["chartreuse 2", "118", "238", "0"])
table.add_row(["chartreuse 3", "102", "205", "0"])
table.add_row(["chartreuse 4", "69", "139", "0"])
table.add_row(["olive drab 1", "192", "255", "62"])
table.add_row(["olive drab 2", "179", "238", "58"])
table.add_row(["olive drab 3", "154", "205", "50"])
table.add_row(["olive drab 4", "105", "139", "34"])
table.add_row(["dark olive green 1", "202", "255", "112"])
table.add_row(["dark olive green 2", "188", "238", "104"])
table.add_row(["dark olive green 3", "162", "205", "90"])
table.add_row(["dark olive green 4", "110", "139", "61"])
table.add_row(["khaki 1", "255", "246", "143"])
table.add_row(["khaki 2", "238", "230", "133"])
table.add_row(["khaki 3", "205", "198", "115"])
table.add_row(["khaki 4", "139", "134", "78"])
table.add_row(["light goldenrod 1", "255", "236", "139"])
table.add_row(["light goldenrod 2", "238", "220", "130"])
table.add_row(["light goldenrod 3", "205", "190", "112"])
table.add_row(["light goldenrod 4", "139", "129", "76"])
table.add_row(["light yellow 1", "255", "255", "224"])
table.add_row(["light yellow 2", "238", "238", "209"])
table.add_row(["light yellow 3", "205", "205", "180"])
table.add_row(["light yellow 4", "139", "139", "122"])
table.add_row(["yellow 1", "255", "255", "0"])
table.add_row(["yellow 2", "238", "238", "0"])
table.add_row(["yellow 3", "205", "205", "0"])
table.add_row(["yellow 4", "139", "139", "0"])
table.add_row(["gold 1", "255", "215", "0"])
table.add_row(["gold 2", "238", "201", "0"])
table.add_row(["gold 3", "205", "173", "0"])
table.add_row(["gold 4", "139", "117", "0"])
table.add_row(["goldenrod 1", "255", "193", "37"])
table.add_row(["goldenrod 2", "238", "180", "34"])
table.add_row(["goldenrod 3", "205", "155", "29"])
table.add_row(["goldenrod 4", "139", "105", "20"])
table.add_row(["dark goldenrod 1", "255", "185", "15"])
table.add_row(["dark goldenrod 2", "238", "173", "14"])
table.add_row(["dark goldenrod 3", "205", "149", "12"])
table.add_row(["dark goldenrod 4", "139", "101", "8"])
table.add_row(["rosy brown 1", "255", "193", "193"])
table.add_row(["rosy brown 2", "238", "180", "180"])
table.add_row(["rosy brown 3", "205", "155", "155"])
table.add_row(["rosy brown 4", "139", "105", "105"])
table.add_row(["indian red 1", "255", "106", "106"])
table.add_row(["indian red 2", "238", "99", "99"])
table.add_row(["indian red 3", "205", "85", "85"])
table.add_row(["indian red 4", "139", "58", "58"])
table.add_row(["sienna 1", "255", "130", "71"])
table.add_row(["sienna 2", "238", "121", "66"])
table.add_row(["sienna 3", "205", "104", "57"])
table.add_row(["sienna 4", "139", "71", "38"])
table.add_row(["burlywood 1", "255", "211", "155"])
table.add_row(["burlywood 2", "238", "197", "145"])
table.add_row(["burlywood 3", "205", "170", "125"])
table.add_row(["burlywood 4", "139", "115", "85"])
table.add_row(["wheat 1", "255", "231", "186"])
table.add_row(["wheat 2", "238", "216", "174"])
table.add_row(["wheat 3", "205", "186", "150"])
table.add_row(["wheat 4", "139", "126", "102"])
table.add_row(["tan 1", "255", "165", "79"])
table.add_row(["tan 2", "238", "154", "73"])
table.add_row(["tan 3", "205", "133", "63"])
table.add_row(["tan 4", "139", "90", "43"])
table.add_row(["chocolate 1", "255", "127", "36"])
table.add_row(["chocolate 2", "238", "118", "33"])
table.add_row(["chocolate 3", "205", "102", "29"])
table.add_row(["chocolate 4", "139", "69", "19"])
table.add_row(["firebrick 1", "255", "48", "48"])
table.add_row(["firebrick 2", "238", "44", "44"])
table.add_row(["firebrick 3", "205", "38", "38"])
table.add_row(["firebrick 4", "139", "26", "26"])
table.add_row(["brown 1", "255", "64", "64"])
table.add_row(["brown 2", "238", "59", "59"])
table.add_row(["brown 3", "205", "51", "51"])
table.add_row(["brown 4", "139", "35", "35"])
table.add_row(["salmon 1", "255", "140", "105"])
table.add_row(["salmon 2", "238", "130", "98"])
table.add_row(["salmon 3", "205", "112", "84"])
table.add_row(["salmon 4", "139", "76", "57"])
table.add_row(["light salmon 1", "255", "160", "122"])
table.add_row(["light salmon 2", "238", "149", "114"])
table.add_row(["light salmon 3", "205", "129", "98"])
table.add_row(["light salmon 4", "139", "87", "66"])
table.add_row(["orange 1", "255", "165", "0"])
table.add_row(["orange 2", "238", "154", "0"])
table.add_row(["orange 3", "205", "133", "0"])
table.add_row(["orange 4", "139", "90", "0"])
table.add_row(["dark orange 1", "255", "127", "0"])
table.add_row(["dark orange 2", "238", "118", "0"])
table.add_row(["dark orange 3", "205", "102", "0"])
table.add_row(["dark orange 4", "139", "69", "0"])
table.add_row(["coral 1", "255", "114", "86"])
table.add_row(["coral 2", "238", "106", "80"])
table.add_row(["coral 3", "205", "91", "69"])
table.add_row(["coral 4", "139", "62", "47"])
table.add_row(["tomato 1", "255", "99", "71"])
table.add_row(["tomato 2", "238", "92", "66"])
table.add_row(["tomato 3", "205", "79", "57"])
table.add_row(["tomato 4", "139", "54", "38"])
table.add_row(["orange red 1", "255", "69", "0"])
table.add_row(["orange red 2", "238", "64", "0"])
table.add_row(["orange red 3", "205", "55", "0"])
table.add_row(["orange red 4", "139", "37", "0"])
table.add_row(["red 1", "255", "0", "0"])
table.add_row(["red 2", "238", "0", "0"])
table.add_row(["red 3", "205", "0", "0"])
table.add_row(["red 4", "139", "0", "0"])
table.add_row(["deep pink 1", "255", "20", "147"])
table.add_row(["deep pink 2", "238", "18", "137"])
table.add_row(["deep pink 3", "205", "16", "118"])
table.add_row(["deep pink 4", "139", "10", "80"])
table.add_row(["hot pink 1", "255", "110", "180"])
table.add_row(["hot pink 2", "238", "106", "167"])
table.add_row(["hot pink 3", "205", "96", "144"])
table.add_row(["hot pink 4", "139", "58", "98"])
table.add_row(["pink 1", "255", "181", "197"])
table.add_row(["pink 2", "238", "169", "184"])
table.add_row(["pink 3", "205", "145", "158"])
table.add_row(["pink 4", "139", "99", "108"])
table.add_row(["light pink 1", "255", "174", "185"])
table.add_row(["light pink 2", "238", "162", "173"])
table.add_row(["light pink 3", "205", "140", "149"])
table.add_row(["light pink 4", "139", "95", "101"])
table.add_row(["pale violet red 1", "255", "130", "171"])
table.add_row(["pale violet red 2", "238", "121", "159"])
table.add_row(["pale violet red 3", "205", "104", "137"])
table.add_row(["pale violet red 4", "139", "71", "93"])
table.add_row(["maroon 1", "255", "52", "179"])
table.add_row(["maroon 2", "238", "48", "167"])
table.add_row(["maroon 3", "205", "41", "144"])
table.add_row(["maroon 4", "139", "28", "98"])
table.add_row(["violet red 1", "255", "62", "150"])
table.add_row(["violet red 2", "238", "58", "140"])
table.add_row(["violet red 3", "205", "50", "120"])
table.add_row(["violet red 4", "139", "34", "82"])
table.add_row(["magenta 1", "255", "0", "255"])
table.add_row(["magenta 2", "238", "0", "238"])
table.add_row(["magenta 3", "205", "0", "205"])
table.add_row(["magenta 4", "139", "0", "139"])
table.add_row(["orchid 1", "255", "131", "250"])
table.add_row(["orchid 2", "238", "122", "233"])
table.add_row(["orchid 3", "205", "105", "201"])
table.add_row(["orchid 4", "139", "71", "137"])
table.add_row(["plum 1", "255", "187", "255"])
table.add_row(["plum 2", "238", "174", "238"])
table.add_row(["plum 3", "205", "150", "205"])
table.add_row(["plum 4", "139", "102", "139"])
table.add_row(["medium orchid 1", "224", "102", "255"])
table.add_row(["medium orchid 2", "209", "95", "238"])
table.add_row(["medium orchid 3", "180", "82", "205"])
table.add_row(["medium orchid 4", "122", "55", "139"])
table.add_row(["dark orchid 1", "191", "62", "255"])
table.add_row(["dark orchid 2", "178", "58", "238"])
table.add_row(["dark orchid 3", "154", "50", "205"])
table.add_row(["dark orchid 4", "104", "34", "139"])
table.add_row(["purple 1", "155", "48", "255"])
table.add_row(["purple 2", "145", "44", "238"])
table.add_row(["purple 3", "125", "38", "205"])
table.add_row(["purple 4", "85", "26", "139"])
table.add_row(["medium purple 1", "171", "130", "255"])
table.add_row(["medium purple 2", "159", "121", "238"])
table.add_row(["medium purple 3", "137", "104", "205"])
table.add_row(["medium purple 4", "93", "71", "139"])
table.add_row(["thistle 1", "255", "225", "255"])
table.add_row(["thistle 2", "238", "210", "238"])
table.add_row(["thistle 3", "205", "181", "205"])
table.add_row(["thistle 4", "139", "123", "139"])
table.add_row(["grey 0", "0", "0", "0"])
table.add_row(["grey 1", "3", "3", "3"])
table.add_row(["grey 2", "5", "5", "5"])
table.add_row(["grey 3", "8", "8", "8"])
table.add_row(["grey 4", "10", "10", "10"])
table.add_row(["grey 5", "13", "13", "13"])
table.add_row(["grey 6", "15", "15", "15"])
table.add_row(["grey 7", "18", "18", "18"])
table.add_row(["grey 8", "20", "20", "20"])
table.add_row(["grey 9", "23", "23", "23"])
table.add_row(["grey 10", "26", "26", "26"])
table.add_row(["grey 11", "28", "28", "28"])
table.add_row(["grey 12", "31", "31", "31"])
table.add_row(["grey 13", "33", "33", "33"])
table.add_row(["grey 14", "36", "36", "36"])
table.add_row(["grey 15", "38", "38", "38"])
table.add_row(["grey 16", "41", "41", "41"])
table.add_row(["grey 17", "43", "43", "43"])
table.add_row(["grey 18", "46", "46", "46"])
table.add_row(["grey 19", "48", "48", "48"])
table.add_row(["grey 20", "51", "51", "51"])
table.add_row(["grey 21", "54", "54", "54"])
table.add_row(["grey 22", "56", "56", "56"])
table.add_row(["grey 23", "59", "59", "59"])
table.add_row(["grey 24", "61", "61", "61"])
table.add_row(["grey 25", "64", "64", "64"])
table.add_row(["grey 26", "66", "66", "66"])
table.add_row(["grey 27", "69", "69", "69"])
table.add_row(["grey 28", "71", "71", "71"])
table.add_row(["grey 29", "74", "74", "74"])
table.add_row(["grey 30", "77", "77", "77"])
table.add_row(["grey 31", "79", "79", "79"])
table.add_row(["grey 32", "82", "82", "82"])
table.add_row(["grey 33", "84", "84", "84"])
table.add_row(["grey 34", "87", "87", "87"])
table.add_row(["grey 35", "89", "89", "89"])
table.add_row(["grey 36", "92", "92", "92"])
table.add_row(["grey 37", "94", "94", "94"])
table.add_row(["grey 38", "97", "97", "97"])
table.add_row(["grey 39", "99", "99", "99"])
table.add_row(["grey 40", "102", "102", "102"])
table.add_row(["grey 41", "105", "105", "105"])
table.add_row(["grey 42", "107", "107", "107"])
table.add_row(["grey 43", "110", "110", "110"])
table.add_row(["grey 44", "112", "112", "112"])
table.add_row(["grey 45", "115", "115", "115"])
table.add_row(["grey 46", "117", "117", "117"])
table.add_row(["grey 47", "120", "120", "120"])
table.add_row(["grey 48", "122", "122", "122"])
table.add_row(["grey 49", "125", "125", "125"])
table.add_row(["grey 50", "127", "127", "127"])
table.add_row(["grey 51", "130", "130", "130"])
table.add_row(["grey 52", "133", "133", "133"])
table.add_row(["grey 53", "135", "135", "135"])
table.add_row(["grey 54", "138", "138", "138"])
table.add_row(["grey 55", "140", "140", "140"])
table.add_row(["grey 56", "143", "143", "143"])
table.add_row(["grey 57", "145", "145", "145"])
table.add_row(["grey 58", "148", "148", "148"])
table.add_row(["grey 59", "150", "150", "150"])
table.add_row(["grey 60", "153", "153", "153"])
table.add_row(["grey 61", "156", "156", "156"])
table.add_row(["grey 62", "158", "158", "158"])
table.add_row(["grey 63", "161", "161", "161"])
table.add_row(["grey 64", "163", "163", "163"])
table.add_row(["grey 65", "166", "166", "166"])
table.add_row(["grey 66", "168", "168", "168"])
table.add_row(["grey 67", "171", "171", "171"])
table.add_row(["grey 68", "173", "173", "173"])
table.add_row(["grey 69", "176", "176", "176"])
table.add_row(["grey 70", "179", "179", "179"])
table.add_row(["grey 71", "181", "181", "181"])
table.add_row(["grey 72", "184", "184", "184"])
table.add_row(["grey 73", "186", "186", "186"])
table.add_row(["grey 74", "189", "189", "189"])
table.add_row(["grey 75", "191", "191", "191"])
table.add_row(["grey 76", "194", "194", "194"])
table.add_row(["grey 77", "196", "196", "196"])
table.add_row(["grey 78", "199", "199", "199"])
table.add_row(["grey 79", "201", "201", "201"])
table.add_row(["grey 80", "204", "204", "204"])
table.add_row(["grey 81", "207", "207", "207"])
table.add_row(["grey 82", "209", "209", "209"])
table.add_row(["grey 83", "212", "212", "212"])
table.add_row(["grey 84", "214", "214", "214"])
table.add_row(["grey 85", "217", "217", "217"])
table.add_row(["grey 86", "219", "219", "219"])
table.add_row(["grey 87", "222", "222", "222"])
table.add_row(["grey 88", "224", "224", "224"])
table.add_row(["grey 89", "227", "227", "227"])
table.add_row(["grey 90", "229", "229", "229"])
table.add_row(["grey 91", "232", "232", "232"])
table.add_row(["grey 92", "235", "235", "235"])
table.add_row(["grey 93", "237", "237", "237"])
table.add_row(["grey 94", "240", "240", "240"])
table.add_row(["grey 95", "242", "242", "242"])
table.add_row(["grey 96", "245", "245", "245"])
table.add_row(["grey 97", "247", "247", "247"])
table.add_row(["grey 98", "250", "250", "250"])
table.add_row(["grey 99", "252", "252", "252"])
table.add_row(["grey 100", "255", "255", "255"])
table.add_row(["dark grey", "169", "169", "169"])
table.add_row(["dark blue", "0", "0", "139"])
table.add_row(["dark cyan", "0", "139", "139"])
table.add_row(["dark magenta", "139", "0", "139"])
table.add_row(["dark red", "139", "0", "0"])
table.add_row(["light green", "144", "238", "144"])
__x11_colours_doc__.add_table(table.label)
