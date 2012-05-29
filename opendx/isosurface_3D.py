###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing the OpenDX 3D space isosurface mapping class."""


# Python module imports.
from numpy import float64, zeros

# relax module imports.
from base_map import Base_Map
from generic_fns import pipes
from generic_fns import value


class Iso3D(Base_Map):
    """OpenDX 3D space isosurface mapping class."""


    def config_text(self):
        """Function for creating the text of the OpenDX program configuration file."""

        # Generate the text.
        text = """//
//
// time: """ + self.date + """
//
// version: 3.2.0 (format), 4.3.2 (DX)
//
//
// panel[0]: position = (0.0164,0.0000), size = 0.2521x0.1933, startup = 1, devstyle = 1
// title: value = Control Panel
//
// workspace: width = 251, height = 142
// layout: snap = 0, width = 50, height = 50, align = NN
//
// interactor Selector[1]: num_components = 1, value = 1 
// selections: maximum = 2, current = 0 
// option[0]: name = "Colour", value = 1
// option[1]: name = "Grey", value = 2
// instance: panel = 0, x = 81, y = 6, style = Scrolled List, vertical = 1, size = 170x136
// label: value = Colour Selector
//
// node Image[3]:
// title: value = Surface
// depth: value = 24
// window: position = (0.0000,0.0400), size = 0.9929x0.9276
"""

        # Return the text.
        return text


    def map_text(self, map_file):
        """Function for creating the text of a 3D map."""

        # Initialise.
        values = zeros(3, float64)
        percent = 0.0
        percent_inc = 100.0 / (self.inc + 1.0)**(self.n - 1.0)
        print(("%-10s%8.3f%-1s" % ("Progress:", percent, "%")))

        # Fix the diffusion tensor.
        unfix = False
        if hasattr(cdp, 'diff_tensor') and not cdp.diff_tensor.fixed:
            cdp.diff_tensor.fixed = True
            unfix = True

        # Initial value of the first parameter.
        values[0] = self.bounds[0, 0]

        # The model identifier.

        # Loop over the first parameter.
        for i in xrange((self.inc + 1)):
            # Initial value of the second parameter.
            values[1] = self.bounds[1, 0]

            # Loop over the second parameter.
            for j in xrange((self.inc + 1)):
                # Initial value of the third parameter.
                values[2] = self.bounds[2, 0]

                # Loop over the third parameter.
                for k in xrange((self.inc + 1)):
                    # Set the parameter values.
                    if self.spin_id:
                        value.set(val=values, param=self.params, spin_id=self.spin_id, force=True)
                    else:
                        value.set(val=values, param=self.params, force=True)

                    # Calculate the function values.
                    if self.spin_id:
                        self.calculate(spin_id=self.spin_id, verbosity=0)
                    else:
                        self.calculate(verbosity=0)

                    # Get the minimisation statistics for the model.
                    if self.spin_id:
                        k, n, chi2 = self.model_stats(spin_id=self.spin_id)
                    else:
                        k, n, chi2 = self.model_stats(model_info=0)

                    # Set maximum value to 1e20 to stop the OpenDX server connection from breaking.
                    if chi2 > 1e20:
                        map_file.write("%30f\n" % 1e20)
                    else:
                        map_file.write("%30f\n" % chi2)

                    # Increment the value of the third parameter.
                    values[2] = values[2] + self.step_size[2]

                # Progress incrementation and printout.
                percent = percent + percent_inc
                print(("%-10s%8.3f%-8s%-8g" % ("Progress:", percent, "%,  " + repr(values) + ",  f(x): ", chi2)))

                # Increment the value of the second parameter.
                values[1] = values[1] + self.step_size[1]

            # Increment the value of the first parameter.
            values[0] = values[0] + self.step_size[0]

        # Unfix the diffusion tensor.
        if unfix:
            cdp.diff_tensor.fixed = False


    def general_text(self):
        """Function for creating the text of the OpenDX .general file for a 3D map."""

        # Generate the text.
        text = ""
        text = text + "file = " + self.file_prefix + "\n"
        text = text + "grid = " + repr((self.inc + 1)) + " x " + repr((self.inc + 1)) + " x " + repr((self.inc + 1)) + "\n"
        text = text + "format = ascii\n"
        text = text + "interleaving = field\n"
        text = text + "majority = row\n"
        text = text + "field = data\n"
        text = text + "structure = scalar\n"
        text = text + "type = float\n"
        text = text + "dependency = positions\n"
        text = text + "positions = regular, regular, regular, 0, 1, 0, 1, 0, 1\n\n"
        text = text + "end\n"

        # Return the text.
        return text


    def point_text(self):
        """Function for creating the text of the .general file for the point."""

        # Generate the import text.
        text = ""
        text = text + "file = " + self.point_file + "\n"
        text = text + "points = 1\n"
        text = text + "format = ascii\n"
        text = text + "interleaving = field\n"
        text = text + "field = locations, field0\n"
        text = text + "structure = 3-vector, scalar\n"
        text = text + "type = float, float\n\n"
        text = text + "end\n"

        # Return the text.
        return text


    def program_text(self):
        """Function for creating the text of the OpenDX program for a 3D map."""

        # Image setup.
        image_array1 = "[" + repr(0.6 * (self.inc + 1.0)) + " " + repr(0.3 * (self.inc + 1.0)) + " " + repr(0.6 * (self.inc + 1.0)) + "]"
        image_array2 = "[" + repr(0.6 * (self.inc + 1.0)) + " " + repr(0.3 * (self.inc + 1.0)) + " " + repr(6.0 * (self.inc + 1.0)) + "]"
        image_val = repr(3.0 * (self.inc + 1.0))


        # Generate the text of the program.
        ###################################

        text = """//
// time: """ + self.date + """
//
// version: 3.2.0 (format), 4.3.2 (DX)
//
//
// MODULE main"""

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
// page assignment: Colour Space	order=3, windowed=0, showing=0
// page assignment: ColourScene	order=5, windowed=0, showing=0
// page assignment: Glyph	order=2, windowed=0, showing=0
// page assignment: Grey Space	order=4, windowed=0, showing=0
// page assignment: GreyScene	order=6, windowed=0, showing=0
// page assignment: Image	order=7, windowed=0, showing=0
// page assignment: Isosurfaces	order=1, windowed=0, showing=1"""
        # No sphere.
        else:
            text = text + """
// page assignment: Colour Space	order=4, windowed=0, showing=0
// page assignment: ColourScene	order=6, windowed=0, showing=0
// page assignment: Grey Space	order=5, windowed=0, showing=0
// page assignment: GreyScene	order=7, windowed=0, showing=0
// page assignment: Image	order=8, windowed=0, showing=0
// page assignment: Isosurfaces	order=2, windowed=0, showing=1"""

        # Common code.
        text = text + """
// workspace: width = 474, height = 354
// layout: snap = 0, width = 50, height = 50, align = NN
//
macro main(
) -> (
) {
    // """

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
    // node Import[4]: x = 177, y = 62, inputs = 6, label = """ + self.point_file + """
    // input[1]: defaulting = 0, visible = 1, type = 32, value = \"""" + self.point_file + """.general"
    // input[3]: defaulting = 1, visible = 1, type = 32, value = "general"
    // page group: Glyph
    //
main_Import_4_out_1 = 
    Import(
    main_Import_4_in_1,
    main_Import_4_in_2,
    main_Import_4_in_3,
    main_Import_4_in_4,
    main_Import_4_in_5,
    main_Import_4_in_6
    ) [instance: 4, cache: 1];
    // 
    // node Glyph[2]: x = 201, y = 182, inputs = 7, label = Glyph
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "sphere"
    // input[3]: defaulting = 1, visible = 1, type = 5, value = 10.0
    // input[4]: defaulting = 0, visible = 1, type = 5, value = """ + self.sphere_size + """
    // input[5]: defaulting = 0, visible = 1, type = 5, value = 0.0
    // page group: Glyph
    //
main_Glyph_2_out_1 = 
    Glyph(
    main_Import_4_out_1,
    main_Glyph_2_in_2,
    main_Glyph_2_in_3,
    main_Glyph_2_in_4,
    main_Glyph_2_in_5,
    main_Glyph_2_in_6,
    main_Glyph_2_in_7
    ) [instance: 2, cache: 1];
    // 
    // node Color[10]: x = 357, y = 278, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0 0 0]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 1.0
    // page group: Glyph
    //
main_Color_10_out_1 = 
    Color(
    main_Glyph_2_out_1,
    main_Color_10_in_2,
    main_Color_10_in_3,
    main_Color_10_in_4,
    main_Color_10_in_5
    ) [instance: 10, cache: 1];
    // 
    // node Transmitter[1]: x = 352, y = 386, inputs = 1, label = GreySphere
    // page group: Glyph
    //
GreySphere = main_Color_10_out_1;
    // 
    // node Receiver[2]: x = 190, y = 350, inputs = 1, label = GreySphere
    // page group: Grey Space
    //
main_Receiver_2_out_1[cache: 0] = GreySphere;"""

        # Common code.
        text = text + """
    // 
    // node Import[3]: x = 225, y = 84, inputs = 6, label = """ + self.file_prefix + """
    // input[1]: defaulting = 0, visible = 1, type = 32, value = \"""" + self.file_prefix + """.general"
    // input[3]: defaulting = 1, visible = 1, type = 32, value = "general"
    // page group: Isosurfaces
    //
main_Import_3_out_1 = 
    Import(
    main_Import_3_in_1,
    main_Import_3_in_2,
    main_Import_3_in_3,
    main_Import_3_in_4,
    main_Import_3_in_5,
    main_Import_3_in_6
    ) [instance: 3, cache: 1];
    // 
    // node Isosurface[5]: x = 102, y = 191, inputs = 6, label = Outer Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 500.0
    // page group: Isosurfaces
    //
main_Isosurface_5_out_1 = 
    Isosurface(
    main_Import_3_out_1,
    main_Isosurface_5_in_2,
    main_Isosurface_5_in_3,
    main_Isosurface_5_in_4,
    main_Isosurface_5_in_5,
    main_Isosurface_5_in_6
    ) [instance: 5, cache: 1];
    // 
    // node Transmitter[7]: x = 110, y = 292, inputs = 1, label = Surface4
    // page group: Isosurfaces
    //
Surface4 = main_Isosurface_5_out_1;
    // 
    // node Receiver[14]: x = 123, y = 51, inputs = 1, label = Surface4
    // page group: Grey Space
    //
main_Receiver_14_out_1[cache: 0] = Surface4;
    // 
    // node Color[6]: x = 142, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0 0 0]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.2
    // page group: Grey Space
    //
main_Color_6_out_1 = 
    Color(
    main_Receiver_14_out_1,
    main_Color_6_in_2,
    main_Color_6_in_3,
    main_Color_6_in_4,
    main_Color_6_in_5
    ) [instance: 6, cache: 1];
    // 
    // node Isosurface[6]: x = 200, y = 191, inputs = 6, label = Middle Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 100.0
    // page group: Isosurfaces
    //
main_Isosurface_6_out_1 = 
    Isosurface(
    main_Import_3_out_1,
    main_Isosurface_6_in_2,
    main_Isosurface_6_in_3,
    main_Isosurface_6_in_4,
    main_Isosurface_6_in_5,
    main_Isosurface_6_in_6
    ) [instance: 6, cache: 1];
    // 
    // node Transmitter[8]: x = 208, y = 292, inputs = 1, label = Surface3
    // page group: Isosurfaces
    //
Surface3 = main_Isosurface_6_out_1;
    // 
    // node Receiver[13]: x = 227, y = 51, inputs = 1, label = Surface3
    // page group: Grey Space
    //
main_Receiver_13_out_1[cache: 0] = Surface3;
    // 
    // node Color[7]: x = 246, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0.2 0.2 0.2]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.4
    // page group: Grey Space
    //
main_Color_7_out_1 = 
    Color(
    main_Receiver_13_out_1,
    main_Color_7_in_2,
    main_Color_7_in_3,
    main_Color_7_in_4,
    main_Color_7_in_5
    ) [instance: 7, cache: 1];
    // 
    // node Collect[5]: x = 203, y = 236, inputs = 2, label = Collect
    // page group: Grey Space
    //
main_Collect_5_out_1 = 
    Collect(
    main_Color_6_out_1,
    main_Color_7_out_1
    ) [instance: 5, cache: 1];
    // 
    // node Isosurface[7]: x = 298, y = 191, inputs = 6, label = Inner Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 20.0
    // page group: Isosurfaces
    //
main_Isosurface_7_out_1 = 
    Isosurface(
    main_Import_3_out_1,
    main_Isosurface_7_in_2,
    main_Isosurface_7_in_3,
    main_Isosurface_7_in_4,
    main_Isosurface_7_in_5,
    main_Isosurface_7_in_6
    ) [instance: 7, cache: 1];
    // 
    // node Transmitter[9]: x = 306, y = 292, inputs = 1, label = Surface2
    // page group: Isosurfaces
    //
Surface2 = main_Isosurface_7_out_1;
    // 
    // node Receiver[12]: x = 331, y = 51, inputs = 1, label = Surface2
    // page group: Grey Space
    //
main_Receiver_12_out_1[cache: 0] = Surface2;
    // 
    // node Color[8]: x = 350, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0.5 0.5 0.5]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.5
    // page group: Grey Space
    //
main_Color_8_out_1 = 
    Color(
    main_Receiver_12_out_1,
    main_Color_8_in_2,
    main_Color_8_in_3,
    main_Color_8_in_4,
    main_Color_8_in_5
    ) [instance: 8, cache: 1];
    // 
    // node Isosurface[8]: x = 396, y = 191, inputs = 6, label = Innermost Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 7.0
    // page group: Isosurfaces
    //
main_Isosurface_8_out_1 = 
    Isosurface(
    main_Import_3_out_1,
    main_Isosurface_8_in_2,
    main_Isosurface_8_in_3,
    main_Isosurface_8_in_4,
    main_Isosurface_8_in_5,
    main_Isosurface_8_in_6
    ) [instance: 8, cache: 1];
    // 
    // node Transmitter[10]: x = 404, y = 292, inputs = 1, label = Surface1
    // page group: Isosurfaces
    //
Surface1 = main_Isosurface_8_out_1;
    // 
    // node Receiver[11]: x = 434, y = 51, inputs = 1, label = Surface1
    // page group: Grey Space
    //
main_Receiver_11_out_1[cache: 0] = Surface1;
    // 
    // node Color[9]: x = 453, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "white"
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.7
    // page group: Grey Space
    //
main_Color_9_out_1 = 
    Color(
    main_Receiver_11_out_1,
    main_Color_9_in_2,
    main_Color_9_in_3,
    main_Color_9_in_4,
    main_Color_9_in_5
    ) [instance: 9, cache: 1];
    // 
    // node Collect[6]: x = 409, y = 236, inputs = 2, label = Collect
    // page group: Grey Space
    //
main_Collect_6_out_1 = 
    Collect(
    main_Color_8_out_1,
    main_Color_9_out_1
    ) [instance: 6, cache: 1];
    // 
    // node Collect[7]: x = 307, y = 327, inputs = 2, label = Collect
    // page group: Grey Space
    //
main_Collect_7_out_1 = 
    Collect(
    main_Collect_5_out_1,
    main_Collect_6_out_1
    ) [instance: 7, cache: 1];
    // """

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
    // node Collect[8]: x = 293, y = 431, inputs = 2, label = Collect
    // page group: Grey Space
    //
main_Collect_8_out_1 = 
    Collect(
    main_Receiver_2_out_1,
    main_Collect_7_out_1
    ) [instance: 8, cache: 1];
    // 
    // node Transmitter[4]: x = 282, y = 517, inputs = 1, label = GreySpace"""

        # No sphere.
        else:
            text = text + """
    // node Transmitter[4]: x = 296, y = 439, inputs = 1, label = GreySpace"""

        # Common code.
        text = text + """
    // page group: Grey Space
    // """

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
GreySpace = main_Collect_8_out_1;"""

        # No sphere.
        else:
            text = text + """
GreySpace = main_Collect_7_out_1;"""

        # Common code.
        text = text + """
    // 
    // node Receiver[3]: x = 137, y = 57, inputs = 1, label = GreySpace
    // page group: GreyScene
    //
main_Receiver_3_out_1[cache: 0] = GreySpace;
    // 
    // node Scale[3]: x = 163, y = 159, inputs = 2, label = Scale
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 1 1]
    // page group: GreyScene
    //
main_Scale_3_out_1 = 
    Scale(
    main_Receiver_3_out_1,
    main_Scale_3_in_2
    ) [instance: 3, cache: 1];
    // 
    // node AutoCamera[2]: x = 273, y = 264, inputs = 9, label = AutoCamera
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 -1 1]
    // input[3]: defaulting = 1, visible = 1, type = 5, value = 500.0
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 640
    // input[5]: defaulting = 0, visible = 0, type = 5, value = .75
    // input[6]: defaulting = 0, visible = 0, type = 8, value = [-1 1 0 ]
    // input[7]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[8]: defaulting = 0, visible = 0, type = 5, value = 30.0
    // input[9]: defaulting = 0, visible = 1, type = 32, value = "white"
    // page group: GreyScene
    //
main_AutoCamera_2_out_1 = 
    AutoCamera(
    main_Scale_3_out_1,
    main_AutoCamera_2_in_2,
    main_AutoCamera_2_in_3,
    main_AutoCamera_2_in_4,
    main_AutoCamera_2_in_5,
    main_AutoCamera_2_in_6,
    main_AutoCamera_2_in_7,
    main_AutoCamera_2_in_8,
    main_AutoCamera_2_in_9
    ) [instance: 2, cache: 1];
    // 
    // node AutoAxes[2]: x = 175, y = 379, inputs = 19, label = AutoAxes
    // input[3]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.labels + """
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 30
    // input[5]: defaulting = 0, visible = 1, type = 16777224, value = """ + self.corners + """
    // input[6]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[7]: defaulting = 1, visible = 0, type = 3, value = 1
    // input[9]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[10]: defaulting = 0, visible = 1, type = 16777224, value = {[1 1 1] [0.1 0.1 0.1] [0 0 0] [0 0 0]}
    // input[11]: defaulting = 0, visible = 1, type = 16777248, value = {"background" "grid" "labels" "ticks"}
    // input[12]: defaulting = 1, visible = 0, type = 5, value = 0.4
    // input[13]: defaulting = 0, visible = 0, type = 32, value = "area"
    // input[14]: defaulting = 0, visible = 1, type = 16777221, value = """ + self.tick_locations[0] + """
    // input[15]: defaulting = 0, visible = 1, type = 16777221, value = """ + self.tick_locations[1] + """
    // input[16]: defaulting = 0, visible = 1, type = 16777221, value = """ + self.tick_locations[2] + """
    // input[17]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.tick_values[0] + """
    // input[18]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.tick_values[1] + """
    // input[19]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.tick_values[2] + """
    // page group: GreyScene
    //
main_AutoAxes_2_out_1 = 
    AutoAxes(
    main_Scale_3_out_1,
    main_AutoCamera_2_out_1,
    main_AutoAxes_2_in_3,
    main_AutoAxes_2_in_4,
    main_AutoAxes_2_in_5,
    main_AutoAxes_2_in_6,
    main_AutoAxes_2_in_7,
    main_AutoAxes_2_in_8,
    main_AutoAxes_2_in_9,
    main_AutoAxes_2_in_10,
    main_AutoAxes_2_in_11,
    main_AutoAxes_2_in_12,
    main_AutoAxes_2_in_13,
    main_AutoAxes_2_in_14,
    main_AutoAxes_2_in_15,
    main_AutoAxes_2_in_16,
    main_AutoAxes_2_in_17,
    main_AutoAxes_2_in_18,
    main_AutoAxes_2_in_19
    ) [instance: 2, cache: 1];
    // """

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
    // node Color[11]: x = 133, y = 278, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 0 0]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 1.0
    // page group: Glyph
    //
main_Color_11_out_1 = 
    Color(
    main_Glyph_2_out_1,
    main_Color_11_in_2,
    main_Color_11_in_3,
    main_Color_11_in_4,
    main_Color_11_in_5
    ) [instance: 11, cache: 1];
    // 
    // node Transmitter[2]: x = 122, y = 386, inputs = 1, label = ColourSphere
    // page group: Glyph
    //
ColourSphere = main_Color_11_out_1;
    // 
    // node Receiver[1]: x = 179, y = 349, inputs = 1, label = ColourSphere
    // page group: Colour Space
    //
main_Receiver_1_out_1[cache: 0] = ColourSphere;"""

        # Common code.
        text = text + """
    // 
    // node Receiver[10]: x = 123, y = 51, inputs = 1, label = Surface4
    // page group: Colour Space
    //
main_Receiver_10_out_1[cache: 0] = Surface4;
    // 
    // node Color[12]: x = 142, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0 0 0.2]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.3
    // input[4]: defaulting = 1, visible = 0, type = 32, value = NULL
    // input[5]: defaulting = 1, visible = 0, type = 3, value = NULL
    // page group: Colour Space
    //
main_Color_12_out_1 = 
    Color(
    main_Receiver_10_out_1,
    main_Color_12_in_2,
    main_Color_12_in_3,
    main_Color_12_in_4,
    main_Color_12_in_5
    ) [instance: 12, cache: 1];
    // 
    // node Receiver[9]: x = 227, y = 51, inputs = 1, label = Surface3
    // page group: Colour Space
    //
main_Receiver_9_out_1[cache: 0] = Surface3;
    // 
    // node Color[13]: x = 246, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "blue"
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.3
    // page group: Colour Space
    //
main_Color_13_out_1 = 
    Color(
    main_Receiver_9_out_1,
    main_Color_13_in_2,
    main_Color_13_in_3,
    main_Color_13_in_4,
    main_Color_13_in_5
    ) [instance: 13, cache: 1];
    // 
    // node Collect[9]: x = 203, y = 236, inputs = 2, label = Collect
    // page group: Colour Space
    //
main_Collect_9_out_1 = 
    Collect(
    main_Color_12_out_1,
    main_Color_13_out_1
    ) [instance: 9, cache: 1];
    // 
    // node Receiver[8]: x = 331, y = 51, inputs = 1, label = Surface2
    // page group: Colour Space
    //
main_Receiver_8_out_1[cache: 0] = Surface2;
    // 
    // node Color[14]: x = 350, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0.5 0.5 1]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.2
    // page group: Colour Space
    //
main_Color_14_out_1 = 
    Color(
    main_Receiver_8_out_1,
    main_Color_14_in_2,
    main_Color_14_in_3,
    main_Color_14_in_4,
    main_Color_14_in_5
    ) [instance: 14, cache: 1];
    // 
    // node Receiver[7]: x = 434, y = 51, inputs = 1, label = Surface1
    // page group: Colour Space
    //
main_Receiver_7_out_1[cache: 0] = Surface1;
    // 
    // node Color[15]: x = 453, y = 145, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "white"
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.55
    // input[4]: defaulting = 1, visible = 0, type = 32, value = "positions"
    // page group: Colour Space
    //
main_Color_15_out_1 = 
    Color(
    main_Receiver_7_out_1,
    main_Color_15_in_2,
    main_Color_15_in_3,
    main_Color_15_in_4,
    main_Color_15_in_5
    ) [instance: 15, cache: 1];
    // 
    // node Collect[10]: x = 409, y = 236, inputs = 2, label = Collect
    // page group: Colour Space
    //
main_Collect_10_out_1 = 
    Collect(
    main_Color_14_out_1,
    main_Color_15_out_1
    ) [instance: 10, cache: 1];
    // 
    // node Collect[11]: x = 307, y = 327, inputs = 2, label = Collect
    // page group: Colour Space
    //
main_Collect_11_out_1 = 
    Collect(
    main_Collect_9_out_1,
    main_Collect_10_out_1
    ) [instance: 11, cache: 1];
    // """

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
    // node Collect[12]: x = 293, y = 431, inputs = 2, label = Collect
    // page group: Colour Space
    //
main_Collect_12_out_1 = 
    Collect(
    main_Receiver_1_out_1,
    main_Collect_11_out_1
    ) [instance: 12, cache: 1];
    // 
    // node Transmitter[3]: x = 276, y = 517, inputs = 1, label = ColourSpace"""

        # No sphere.
        else:
            text = text + """
    // node Transmitter[3]: x = 290, y = 440, inputs = 1, label = ColourSpace"""

        # Common code.
        text = text + """
    // page group: Colour Space
    // """

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
ColourSpace = main_Collect_12_out_1;"""

        # No sphere.
        else:
            text = text + """
ColourSpace = main_Collect_11_out_1;"""

        # Common code.
        text = text + """
    // 
    // node Receiver[4]: x = 131, y = 58, inputs = 1, label = ColourSpace
    // page group: ColourScene
    //
main_Receiver_4_out_1[cache: 0] = ColourSpace;
    // 
    // node Scale[5]: x = 163, y = 159, inputs = 2, label = Scale
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 1 1]
    // page group: ColourScene
    //
main_Scale_5_out_1 = 
    Scale(
    main_Receiver_4_out_1,
    main_Scale_5_in_2
    ) [instance: 5, cache: 1];
    // 
    // node AutoCamera[4]: x = 273, y = 264, inputs = 9, label = AutoCamera
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 -1 1]
    // input[3]: defaulting = 1, visible = 1, type = 5, value = 500.0
    // input[5]: defaulting = 0, visible = 0, type = 5, value = .75
    // input[6]: defaulting = 0, visible = 0, type = 8, value = [-1 1 0 ]
    // input[7]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[8]: defaulting = 0, visible = 0, type = 5, value = 30.0
    // input[9]: defaulting = 0, visible = 1, type = 32, value = "black"
    // page group: ColourScene
    //
main_AutoCamera_4_out_1 = 
    AutoCamera(
    main_Scale_5_out_1,
    main_AutoCamera_4_in_2,
    main_AutoCamera_4_in_3,
    main_AutoCamera_4_in_4,
    main_AutoCamera_4_in_5,
    main_AutoCamera_4_in_6,
    main_AutoCamera_4_in_7,
    main_AutoCamera_4_in_8,
    main_AutoCamera_4_in_9
    ) [instance: 4, cache: 1];
    // 
    // node AutoAxes[4]: x = 175, y = 379, inputs = 19, label = AutoAxes
    // input[3]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.labels + """
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 30
    // input[5]: defaulting = 0, visible = 1, type = 16777224, value = """ + self.corners + """
    // input[6]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[7]: defaulting = 1, visible = 0, type = 3, value = 1
    // input[9]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[10]: defaulting = 0, visible = 1, type = 16777224, value = {[0.05 0.05 0.05] [0.3 0.3 0.3] [1 1 1] [1 1 0]}
    // input[11]: defaulting = 0, visible = 1, type = 16777248, value = {"background" "grid" "labels" "ticks"}
    // input[12]: defaulting = 1, visible = 0, type = 5, value = 0.4
    // input[13]: defaulting = 0, visible = 0, type = 32, value = "area"
    // input[14]: defaulting = 0, visible = 1, type = 16777221, value = """ + self.tick_locations[0] + """
    // input[15]: defaulting = 0, visible = 1, type = 16777221, value = """ + self.tick_locations[1] + """
    // input[16]: defaulting = 0, visible = 1, type = 16777221, value = """ + self.tick_locations[2] + """
    // input[17]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.tick_values[0] + """
    // input[18]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.tick_values[1] + """
    // input[19]: defaulting = 0, visible = 1, type = 16777248, value = """ + self.tick_values[2] + """
    // page group: ColourScene
    //
main_AutoAxes_4_out_1 = 
    AutoAxes(
    main_Scale_5_out_1,
    main_AutoCamera_4_out_1,
    main_AutoAxes_4_in_3,
    main_AutoAxes_4_in_4,
    main_AutoAxes_4_in_5,
    main_AutoAxes_4_in_6,
    main_AutoAxes_4_in_7,
    main_AutoAxes_4_in_8,
    main_AutoAxes_4_in_9,
    main_AutoAxes_4_in_10,
    main_AutoAxes_4_in_11,
    main_AutoAxes_4_in_12,
    main_AutoAxes_4_in_13,
    main_AutoAxes_4_in_14,
    main_AutoAxes_4_in_15,
    main_AutoAxes_4_in_16,
    main_AutoAxes_4_in_17,
    main_AutoAxes_4_in_18,
    main_AutoAxes_4_in_19
    ) [instance: 4, cache: 1];
    // 
    // node Selector[1]: x = 245, y = 66, inputs = 7, label = Selector
    // input[1]: defaulting = 0, visible = 0, type = 32, value = "Selector_1"
    // input[2]: defaulting = 0, visible = 0, type = 32, value = "Colour" 
    // input[3]: defaulting = 0, visible = 0, type = 29, value = 1 
    // input[4]: defaulting = 1, visible = 1, type = 16777248, value = { "Colour" "Grey" }
    // input[5]: defaulting = 1, visible = 0, type = 16777245, value = { 1 2 }
    // output[1]: visible = 1, type = 29, value = 1 
    // output[2]: visible = 1, type = 32, value = "Colour" 
    // page group: Image
    //
    // 
    // node Transmitter[6]: x = 299, y = 487, inputs = 1, label = ColourImage
    // page group: ColourScene
    //
ColourImage = main_AutoAxes_4_out_1;
    // 
    // node Receiver[5]: x = 76, y = 190, inputs = 1, label = ColourImage
    // page group: Image
    //
main_Receiver_5_out_1[cache: 0] = ColourImage;
    // 
    // node Transmitter[5]: x = 305, y = 489, inputs = 1, label = GreyImage
    // page group: GreyScene
    //
GreyImage = main_AutoAxes_2_out_1;
    // 
    // node Receiver[6]: x = 199, y = 190, inputs = 1, label = GreyImage
    // page group: Image
    //
main_Receiver_6_out_1[cache: 0] = GreyImage;
    // 
    // node Switch[1]: x = 177, y = 293, inputs = 3, label = Switch
    // page group: Image
    //
main_Switch_1_out_1 = 
    Switch(
    main_Selector_1_out_1,
    main_Receiver_5_out_1,
    main_Receiver_6_out_1
    ) [instance: 1, cache: 1];
    // 
    // node Switch[14]: x = 325, y = 293, inputs = 3, label = Switch
    // input[2]: defaulting = 0, visible = 1, type = 67108863, value = "black"
    // input[3]: defaulting = 0, visible = 1, type = 67108863, value = "white"
    // page group: Image
    //
main_Switch_14_out_1 = 
    Switch(
    main_Selector_1_out_1,
    main_Switch_14_in_2,
    main_Switch_14_in_3
    ) [instance: 14, cache: 1];
    // 
    // node Image[3]: x = 252, y = 424, inputs = 49, label = Image
    // input[1]: defaulting = 0, visible = 0, type = 67108863, value = "Image_3"
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 1
    // input[5]: defaulting = 0, visible = 0, type = 8, value = """ + image_array1 + """
    // input[6]: defaulting = 0, visible = 0, type = 8, value = """ + image_array2 + """
    // input[7]: defaulting = 0, visible = 0, type = 5, value = """ + image_val + """
    // input[8]: defaulting = 0, visible = 0, type = 1, value = 1376
    // input[9]: defaulting = 0, visible = 0, type = 5, value = 0.678
    // input[10]: defaulting = 0, visible = 0, type = 8, value = [-0.109685 0.243133 0.963772]
    // input[11]: defaulting = 1, visible = 0, type = 5, value = 30.9877
    // input[12]: defaulting = 0, visible = 0, type = 1, value = 0
    // input[14]: defaulting = 0, visible = 0, type = 1, value = 1
    // input[15]: defaulting = 0, visible = 0, type = 32, value = "none"
    // input[16]: defaulting = 0, visible = 0, type = 32, value = "none"
    // input[17]: defaulting = 1, visible = 0, type = 1, value = 1
    // input[18]: defaulting = 1, visible = 0, type = 1, value = 1
    // input[19]: defaulting = 0, visible = 0, type = 1, value = 0
    // input[22]: defaulting = 1, visible = 1, type = 32, value = "black"
    // input[25]: defaulting = 0, visible = 0, type = 32, value = "iso"
    // input[26]: defaulting = 0, visible = 0, type = 32, value = "tiff"
    // input[29]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[30]: defaulting = 1, visible = 0, type = 16777248, value = """ + self.labels + """
    // input[32]: defaulting = 1, visible = 0, type = 16777224, value = """ + self.corners + """
    // input[33]: defaulting = 0, visible = 0, type = 3, value = 1
    // input[34]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[36]: defaulting = 0, visible = 0, type = 3, value = 1
    // input[41]: defaulting = 0, visible = 0, type = 32, value = "rotate"
    // input[42]: defaulting = 0, visible = 0, type = 32, value = "Surface"
    // page group: Image
    // title: value = Surface
    // depth: value = 24
    // window: position = (0.0000,0.0400), size = 0.9929x0.9276
    // internal caching: 1
    //
main_Image_3_out_1,
main_Image_3_out_2,
main_Image_3_out_3 = 
    Image(
    main_Image_3_in_1,
    main_Switch_1_out_1,
    main_Image_3_in_3,
    main_Image_3_in_4,
    main_Image_3_in_5,
    main_Image_3_in_6,
    main_Image_3_in_7,
    main_Image_3_in_8,
    main_Image_3_in_9,
    main_Image_3_in_10,
    main_Image_3_in_11,
    main_Image_3_in_12,
    main_Image_3_in_13,
    main_Image_3_in_14,
    main_Image_3_in_15,
    main_Image_3_in_16,
    main_Image_3_in_17,
    main_Image_3_in_18,
    main_Image_3_in_19,
    main_Image_3_in_20,
    main_Image_3_in_21,
    main_Switch_14_out_1,
    main_Image_3_in_23,
    main_Image_3_in_24,
    main_Image_3_in_25,
    main_Image_3_in_26,
    main_Image_3_in_27,
    main_Image_3_in_28,
    main_Image_3_in_29,
    main_Image_3_in_30,
    main_Image_3_in_31,
    main_Image_3_in_32,
    main_Image_3_in_33,
    main_Image_3_in_34,
    main_Image_3_in_35,
    main_Image_3_in_36,
    main_Image_3_in_37,
    main_Image_3_in_38,
    main_Image_3_in_39,
    main_Image_3_in_40,
    main_Image_3_in_41,
    main_Image_3_in_42,
    main_Image_3_in_43,
    main_Image_3_in_44,
    main_Image_3_in_45,
    main_Image_3_in_46,
    main_Image_3_in_47,
    main_Image_3_in_48,
    main_Image_3_in_49
    ) [instance: 3, cache: 1];
// network: end of macro body
CacheScene(main_Image_3_in_1, main_Image_3_out_1, main_Image_3_out_2);
}"""

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
main_Import_4_in_1 = \"""" + self.point_file + """.general";
main_Import_4_in_2 = NULL;
main_Import_4_in_3 = NULL;
main_Import_4_in_4 = NULL;
main_Import_4_in_5 = NULL;
main_Import_4_in_6 = NULL;
main_Import_4_out_1 = NULL;
main_Glyph_2_in_2 = "sphere";
main_Glyph_2_in_3 = NULL;
main_Glyph_2_in_4 = """ + self.sphere_size + """;
main_Glyph_2_in_5 = 0.0;
main_Glyph_2_in_6 = NULL;
main_Glyph_2_in_7 = NULL;
main_Glyph_2_out_1 = NULL;
main_Color_10_in_2 = [0 0 0];
main_Color_10_in_3 = 1.0;
main_Color_10_in_4 = NULL;
main_Color_10_in_5 = NULL;
main_Color_10_out_1 = NULL;
main_Transmitter_1_out_1 = NULL;
main_Receiver_2_out_1 = NULL;"""

        # Common code.
        text = text + """
main_Import_3_in_1 = \"""" + self.file_prefix + """.general";
main_Import_3_in_2 = NULL;
main_Import_3_in_3 = NULL;
main_Import_3_in_4 = NULL;
main_Import_3_in_5 = NULL;
main_Import_3_in_6 = NULL;
main_Import_3_out_1 = NULL;
main_Isosurface_5_in_2 = 500.0;
main_Isosurface_5_in_3 = NULL;
main_Isosurface_5_in_4 = NULL;
main_Isosurface_5_in_5 = NULL;
main_Isosurface_5_in_6 = NULL;
main_Isosurface_5_out_1 = NULL;
main_Transmitter_7_out_1 = NULL;
main_Receiver_14_out_1 = NULL;
main_Color_6_in_2 = [0 0 0];
main_Color_6_in_3 = 0.2;
main_Color_6_in_4 = NULL;
main_Color_6_in_5 = NULL;
main_Color_6_out_1 = NULL;
main_Isosurface_6_in_2 = 100.0;
main_Isosurface_6_in_3 = NULL;
main_Isosurface_6_in_4 = NULL;
main_Isosurface_6_in_5 = NULL;
main_Isosurface_6_in_6 = NULL;
main_Isosurface_6_out_1 = NULL;
main_Transmitter_8_out_1 = NULL;
main_Receiver_13_out_1 = NULL;
main_Color_7_in_2 = [0.2 0.2 0.2];
main_Color_7_in_3 = 0.4;
main_Color_7_in_4 = NULL;
main_Color_7_in_5 = NULL;
main_Color_7_out_1 = NULL;
main_Collect_5_out_1 = NULL;
main_Isosurface_7_in_2 = 20.0;
main_Isosurface_7_in_3 = NULL;
main_Isosurface_7_in_4 = NULL;
main_Isosurface_7_in_5 = NULL;
main_Isosurface_7_in_6 = NULL;
main_Isosurface_7_out_1 = NULL;
main_Transmitter_9_out_1 = NULL;
main_Receiver_12_out_1 = NULL;
main_Color_8_in_2 = [0.5 0.5 0.5];
main_Color_8_in_3 = 0.5;
main_Color_8_in_4 = NULL;
main_Color_8_in_5 = NULL;
main_Color_8_out_1 = NULL;
main_Isosurface_8_in_2 = 7.0;
main_Isosurface_8_in_3 = NULL;
main_Isosurface_8_in_4 = NULL;
main_Isosurface_8_in_5 = NULL;
main_Isosurface_8_in_6 = NULL;
main_Isosurface_8_out_1 = NULL;
main_Transmitter_10_out_1 = NULL;
main_Receiver_11_out_1 = NULL;
main_Color_9_in_2 = "white";
main_Color_9_in_3 = 0.7;
main_Color_9_in_4 = NULL;
main_Color_9_in_5 = NULL;
main_Color_9_out_1 = NULL;
main_Collect_6_out_1 = NULL;
main_Collect_7_out_1 = NULL;"""

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
main_Collect_8_out_1 = NULL;"""

        # Common code.
        text = text + """
main_Transmitter_4_out_1 = NULL;
main_Receiver_3_out_1 = NULL;
main_Scale_3_in_2 = [1 1 1];
main_Scale_3_out_1 = NULL;
main_AutoCamera_2_in_2 = [1 -1 1];
main_AutoCamera_2_in_3 = NULL;
main_AutoCamera_2_in_4 = 640;
main_AutoCamera_2_in_5 = .75;
main_AutoCamera_2_in_6 = [-1 1 0 ];
main_AutoCamera_2_in_7 = 0;
main_AutoCamera_2_in_8 = 30.0;
main_AutoCamera_2_in_9 = "white";
main_AutoCamera_2_out_1 = NULL;
main_AutoAxes_2_in_3 = """ + self.labels + """;
main_AutoAxes_2_in_4 = 30;
main_AutoAxes_2_in_5 = """ + self.corners + """;
main_AutoAxes_2_in_6 = 1;
main_AutoAxes_2_in_7 = NULL;
main_AutoAxes_2_in_8 = NULL;
main_AutoAxes_2_in_9 = 1;
main_AutoAxes_2_in_10 = {[1 1 1] [0.1 0.1 0.1] [0 0 0] [0 0 0]};
main_AutoAxes_2_in_11 = {"background" "grid" "labels" "ticks"};
main_AutoAxes_2_in_12 = NULL;
main_AutoAxes_2_in_13 = "area";
main_AutoAxes_2_in_14 = """ + self.tick_locations[0] + """;
main_AutoAxes_2_in_15 = """ + self.tick_locations[1] + """;
main_AutoAxes_2_in_16 = """ + self.tick_locations[2] + """;
main_AutoAxes_2_in_17 = """ + self.tick_values[0] + """;
main_AutoAxes_2_in_18 = """ + self.tick_values[1] + """;
main_AutoAxes_2_in_19 = """ + self.tick_values[2] + """;
main_AutoAxes_2_out_1 = NULL;"""

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
main_Color_11_in_2 = [1 0 0];
main_Color_11_in_3 = 1.0;
main_Color_11_in_4 = NULL;
main_Color_11_in_5 = NULL;
main_Color_11_out_1 = NULL;
main_Transmitter_2_out_1 = NULL;
main_Receiver_1_out_1 = NULL;"""

        # Common code.
        text = text + """
main_Receiver_10_out_1 = NULL;
main_Color_12_in_2 = [0 0 0.2];
main_Color_12_in_3 = 0.3;
main_Color_12_in_4 = NULL;
main_Color_12_in_5 = NULL;
main_Color_12_out_1 = NULL;
main_Receiver_9_out_1 = NULL;
main_Color_13_in_2 = "blue";
main_Color_13_in_3 = 0.3;
main_Color_13_in_4 = NULL;
main_Color_13_in_5 = NULL;
main_Color_13_out_1 = NULL;
main_Collect_9_out_1 = NULL;
main_Receiver_8_out_1 = NULL;
main_Color_14_in_2 = [0.5 0.5 1];
main_Color_14_in_3 = 0.2;
main_Color_14_in_4 = NULL;
main_Color_14_in_5 = NULL;
main_Color_14_out_1 = NULL;
main_Receiver_7_out_1 = NULL;
main_Color_15_in_2 = "white";
main_Color_15_in_3 = 0.55;
main_Color_15_in_4 = NULL;
main_Color_15_in_5 = NULL;
main_Color_15_out_1 = NULL;
main_Collect_10_out_1 = NULL;
main_Collect_11_out_1 = NULL;"""

        # Include the sphere.
        if self.num_points == 1:
            text = text + """
main_Collect_12_out_1 = NULL;"""

        # Common code.
        text = text + """
main_Transmitter_3_out_1 = NULL;
main_Receiver_4_out_1 = NULL;
main_Scale_5_in_2 = [1 1 1];
main_Scale_5_out_1 = NULL;
main_AutoCamera_4_in_2 = [1 -1 1];
main_AutoCamera_4_in_3 = NULL;
main_AutoCamera_4_in_4 = NULL;
main_AutoCamera_4_in_5 = .75;
main_AutoCamera_4_in_6 = [-1 1 0 ];
main_AutoCamera_4_in_7 = 0;
main_AutoCamera_4_in_8 = 30.0;
main_AutoCamera_4_in_9 = "black";
main_AutoCamera_4_out_1 = NULL;
main_AutoAxes_4_in_3 = """ + self.labels + """;
main_AutoAxes_4_in_4 = 30;
main_AutoAxes_4_in_5 = """ + self.corners + """;
main_AutoAxes_4_in_6 = 1;
main_AutoAxes_4_in_7 = NULL;
main_AutoAxes_4_in_8 = NULL;
main_AutoAxes_4_in_9 = 1;
main_AutoAxes_4_in_10 = {[0.05 0.05 0.05] [0.3 0.3 0.3] [1 1 1] [1 1 0]};
main_AutoAxes_4_in_11 = {"background" "grid" "labels" "ticks"};
main_AutoAxes_4_in_12 = NULL;
main_AutoAxes_4_in_13 = "area";
main_AutoAxes_4_in_14 = """ + self.tick_locations[0] + """;
main_AutoAxes_4_in_15 = """ + self.tick_locations[1] + """;
main_AutoAxes_4_in_16 = """ + self.tick_locations[2] + """;
main_AutoAxes_4_in_17 = """ + self.tick_values[0] + """;
main_AutoAxes_4_in_18 = """ + self.tick_values[1] + """;
main_AutoAxes_4_in_19 = """ + self.tick_values[2] + """;
main_AutoAxes_4_out_1 = NULL;
main_Selector_1_in_1 = "Selector_1";
main_Selector_1_in_2 = "Colour" ;
main_Selector_1_in_3 = 1 ;
main_Selector_1_in_4 = NULL;
main_Selector_1_in_5 = NULL;
main_Selector_1_in_6 = NULL;
main_Selector_1_in_7 = NULL;
main_Selector_1_out_1 = 1 ;
main_Transmitter_6_out_1 = NULL;
main_Receiver_5_out_1 = NULL;
main_Transmitter_5_out_1 = NULL;
main_Receiver_6_out_1 = NULL;
main_Switch_1_out_1 = NULL;
main_Switch_14_in_2 = "black";
main_Switch_14_in_3 = "white";
main_Switch_14_out_1 = NULL;
macro Image(
        id,
        object,
        where,
        useVector,
        to,
        from,
        width,
        resolution,
        aspect,
        up,
        viewAngle,
        perspective,
        options,
        buttonState = 1,
        buttonUpApprox = "none",
        buttonDownApprox = "none",
        buttonUpDensity = 1,
        buttonDownDensity = 1,
        renderMode = 0,
        defaultCamera,
        reset,
        backgroundColor,
        throttle,
        RECenable = 0,
        RECfile,
        RECformat,
        RECresolution,
        RECaspect,
        AAenable = 0,
        AAlabels,
        AAticks,
        AAcorners,
        AAframe,
        AAadjust,
        AAcursor,
        AAgrid,
        AAcolors,
        AAannotation,
        AAlabelscale,
        AAfont,
        interactionMode,
        title,
        AAxTickLocs,
        AAyTickLocs,
        AAzTickLocs,
        AAxTickLabels,
        AAyTickLabels,
        AAzTickLabels,
        webOptions) -> (
        object,
        camera,
        where)
{
    ImageMessage(
        id,
        backgroundColor,
        throttle,
        RECenable,
        RECfile,
        RECformat,
        RECresolution,
        RECaspect,
        AAenable,
        AAlabels,
        AAticks,
        AAcorners,
        AAframe,
        AAadjust,
        AAcursor,
        AAgrid,
        AAcolors,
        AAannotation,
        AAlabelscale,
        AAfont,
        AAxTickLocs,
        AAyTickLocs,
        AAzTickLocs,
        AAxTickLabels,
        AAyTickLabels,
        AAzTickLabels,
        interactionMode,
        title,
        renderMode,
        buttonUpApprox,
        buttonDownApprox,
        buttonUpDensity,
        buttonDownDensity) [instance: 1, cache: 1];
    autoCamera =
        AutoCamera(
            object,
            "front",
            object,
            resolution,
            aspect,
            [0,1,0],
            perspective,
            viewAngle,
            backgroundColor) [instance: 1, cache: 1];
    realCamera =
        Camera(
            to,
            from,
            width,
            resolution,
            aspect,
            up,
            perspective,
            viewAngle,
            backgroundColor) [instance: 1, cache: 1];
    coloredDefaultCamera = 
	 UpdateCamera(defaultCamera,
            background=backgroundColor) [instance: 1, cache: 1];
    nullDefaultCamera =
        Inquire(defaultCamera,
            "is null + 1") [instance: 1, cache: 1];
    resetCamera =
        Switch(
            nullDefaultCamera,
            coloredDefaultCamera,
            autoCamera) [instance: 1, cache: 1];
    resetNull = 
        Inquire(
            reset,
            "is null + 1") [instance: 2, cache: 1];
    reset =
        Switch(
            resetNull,
            reset,
            0) [instance: 2, cache: 1];
    whichCamera =
        Compute(
            "($0 != 0 || $1 == 0) ? 1 : 2",
            reset,
            useVector) [instance: 1, cache: 1];
    camera = Switch(
            whichCamera,
            resetCamera,
            realCamera) [instance: 3, cache: 1];
    AAobject =
        AutoAxes(
            object,
            camera,
            AAlabels,
            AAticks,
            AAcorners,
            AAframe,
            AAadjust,
            AAcursor,
            AAgrid,
            AAcolors,
            AAannotation,
            AAlabelscale,
            AAfont,
            AAxTickLocs,
            AAyTickLocs,
            AAzTickLocs,
            AAxTickLabels,
            AAyTickLabels,
            AAzTickLabels) [instance: 1, cache: 1];
    switchAAenable = Compute("$0+1",
	     AAenable) [instance: 2, cache: 1];
    object = Switch(
	     switchAAenable,
	     object,
	     AAobject) [instance:4, cache: 1];
    SWapproximation_options =
        Switch(
            buttonState,
            buttonUpApprox,
            buttonDownApprox) [instance: 5, cache: 1];
    SWdensity_options =
        Switch(
            buttonState,
            buttonUpDensity,
            buttonDownDensity) [instance: 6, cache: 1];
    HWapproximation_options =
        Format(
            "%s,%s",
            buttonDownApprox,
            buttonUpApprox) [instance: 1, cache: 1];
    HWdensity_options =
        Format(
            "%d,%d",
            buttonDownDensity,
            buttonUpDensity) [instance: 2, cache: 1];
    switchRenderMode = Compute(
	     "$0+1",
	     renderMode) [instance: 3, cache: 1];
    approximation_options = Switch(
	     switchRenderMode,
            SWapproximation_options,
	     HWapproximation_options) [instance: 7, cache: 1];
    density_options = Switch(
	     switchRenderMode,
            SWdensity_options,
            HWdensity_options) [instance: 8, cache: 1];
    renderModeString = Switch(
            switchRenderMode,
            "software",
            "hardware")[instance: 9, cache: 1];
    object_tag = Inquire(
            object,
            "object tag")[instance: 3, cache: 1];
    annoted_object =
        Options(
            object,
            "send boxes",
            0,
            "cache",
            1,
            "object tag",
            object_tag,
            "ddcamera",
            whichCamera,
            "rendering approximation",
            approximation_options,
            "render every",
            density_options,
            "button state",
            buttonState,
            "rendering mode",
            renderModeString) [instance: 1, cache: 1];
    RECresNull =
        Inquire(
            RECresolution,
            "is null + 1") [instance: 4, cache: 1];
    ImageResolution =
        Inquire(
            camera,
            "camera resolution") [instance: 5, cache: 1];
    RECresolution =
        Switch(
            RECresNull,
            RECresolution,
            ImageResolution) [instance: 10, cache: 1];
    RECaspectNull =
        Inquire(
            RECaspect,
            "is null + 1") [instance: 6, cache: 1];
    ImageAspect =
        Inquire(
            camera,
            "camera aspect") [instance: 7, cache: 1];
    RECaspect =
        Switch(
            RECaspectNull,
            RECaspect,
            ImageAspect) [instance: 11, cache: 1];
    switchRECenable = Compute(
          "$0 == 0 ? 1 : (($2 == $3) && ($4 == $5)) ? ($1 == 1 ? 2 : 3) : 4",
            RECenable,
            switchRenderMode,
            RECresolution,
            ImageResolution,
            RECaspect,
	     ImageAspect) [instance: 4, cache: 1];
    NoRECobject, RECNoRerenderObject, RECNoRerHW, RECRerenderObject = Route(switchRECenable, annoted_object);
    Display(
        NoRECobject,
        camera,
        where,
        throttle) [instance: 1, cache: 1];
    image =
        Render(
            RECNoRerenderObject,
            camera) [instance: 1, cache: 1];
    Display(
        image,
        NULL,
        where,
        throttle) [instance: 2, cache: 1];
    WriteImage(
        image,
        RECfile,
        RECformat) [instance: 1, cache: 1];
    rec_where = Display(
        RECNoRerHW,
        camera,
        where,
        throttle) [instance: 1, cache: 0];
    rec_image = ReadImageWindow(
        rec_where) [instance: 1, cache: 1];
    WriteImage(
        rec_image,
        RECfile,
        RECformat) [instance: 1, cache: 1];
    RECupdateCamera =
	UpdateCamera(
	    camera,
	    resolution=RECresolution,
	    aspect=RECaspect) [instance: 2, cache: 1];
    Display(
        RECRerenderObject,
        camera,
        where,
        throttle) [instance: 1, cache: 1];
    RECRerenderObject =
	ScaleScreen(
	    RECRerenderObject,
	    NULL,
	    RECresolution,
	    camera) [instance: 1, cache: 1];
    image =
        Render(
            RECRerenderObject,
            RECupdateCamera) [instance: 2, cache: 1];
    WriteImage(
        image,
        RECfile,
        RECformat) [instance: 2, cache: 1];
}
main_Image_3_in_1 = "Image_3";
main_Image_3_in_3 = "X24,,Surface";
main_Image_3_in_4 = 1;
main_Image_3_in_5 = """ + image_array1 + """;
main_Image_3_in_6 = """ + image_array2 + """;
main_Image_3_in_7 = """ + image_val + """;
main_Image_3_in_8 = 1376;
main_Image_3_in_9 = 0.678;
main_Image_3_in_10 = [-0.109685 0.243133 0.963772];
main_Image_3_in_11 = NULL;
main_Image_3_in_12 = 0;
main_Image_3_in_13 = NULL;
main_Image_3_in_14 = 1;
main_Image_3_in_15 = "none";
main_Image_3_in_16 = "none";
main_Image_3_in_17 = NULL;
main_Image_3_in_18 = NULL;
main_Image_3_in_19 = 0;
main_Image_3_in_20 = NULL;
main_Image_3_in_21 = NULL;
main_Image_3_in_23 = NULL;
main_Image_3_in_25 = "iso";
main_Image_3_in_26 = "tiff";
main_Image_3_in_27 = NULL;
main_Image_3_in_28 = NULL;
main_Image_3_in_29 = 0;
main_Image_3_in_30 = NULL;
main_Image_3_in_31 = NULL;
main_Image_3_in_32 = NULL;
main_Image_3_in_33 = 1;
main_Image_3_in_34 = 0;
main_Image_3_in_35 = NULL;
main_Image_3_in_36 = 1;
main_Image_3_in_37 = NULL;
main_Image_3_in_38 = NULL;
main_Image_3_in_39 = NULL;
main_Image_3_in_40 = NULL;
main_Image_3_in_41 = "rotate";
main_Image_3_in_42 = "Surface";
main_Image_3_in_43 = NULL;
main_Image_3_in_44 = NULL;
main_Image_3_in_45 = NULL;
main_Image_3_in_46 = NULL;
main_Image_3_in_47 = NULL;
main_Image_3_in_48 = NULL;
main_Image_3_in_49 = NULL;
Executive("product version 4 3 2");
$sync
main();
"""

        # Return the text.
        return text
