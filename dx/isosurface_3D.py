###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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


from Numeric import Float64, zeros
from time import asctime, localtime

from base_map import Base_Map


class Iso3D(Base_Map):
    def __init__(self, relax):
        """3D isosurface class."""

        self.relax = relax


    def create_map(self):
        """Function for creating a 3D map."""

        # Map file.
        if self.dir:
            map_file = open(self.dir + "/" + self.file, "w")
        else:
            map_file = open(self.file, "w")

        # Initialise.
        values = zeros(3, Float64)
        self.percent = 0.0
        self.percent_inc = 100.0 / (self.inc + 1.0)**(self.n - 1.0)
        print "%-10s%8.3f%-1s" % ("Progress:", self.percent, "%")

        # Create the map.
        values[self.swap[0]] = self.bounds[self.swap[0], 0]
        for i in xrange((self.inc + 1)):
            values[self.swap[1]] = self.bounds[self.swap[1], 0]
            for j in xrange((self.inc + 1)):
                values[self.swap[2]] = self.bounds[self.swap[2], 0]
                for k in xrange((self.inc + 1)):
                    # Calculate the function values.
                    self.minimise(run=self.run, i=self.index, init_params=self.remap(values), scaling_matrix=self.scaling_matrix, min_algor='fixed', min_options=self.remap(values), print_flag=0)

                    # Set maximum value to 1e20 to stop the OpenDX server connection from breaking.
                    if self.relax.data.res[self.index].chi2[self.run] > 1e20:
                        map_file.write("%30f\n" % 1e20)
                    else:
                        map_file.write("%30f\n" % self.relax.data.res[self.index].chi2[self.run])

                    values[self.swap[2]] = values[self.swap[2]] + self.step_size[self.swap[2]]
                self.percent = self.percent + self.percent_inc
                print "%-10s%8.3f%-8s%-8g" % ("Progress:", self.percent, "%, value: ", self.relax.data.res[self.index].chi2[self.run])
                values[self.swap[1]] = values[self.swap[1]] + self.step_size[self.swap[1]]
            values[self.swap[0]] = values[self.swap[0]] + self.step_size[self.swap[0]]

        # Close the file.
        map_file.close()


    def create_point(self):
        """Function for creating a sphere at a given position within the 3D map.

        The formula used to calculate the coordinate position is:

                            V - L
            coord =   Inc * -----
                            U - L

        where:
            V is the coordinate or parameter value.
            L is the lower bound value.
            U is the upper bound value.
            Inc is the number of increments.

        Both a data file and .general file will be created.
        """

        # Open the data and .general files.
        if self.dir:
            point_file = open(self.dir + "/" + self.point_file, "w")
            general_file = open(self.dir + "/" + self.point_file + ".general", "w")
        else:
            point_file = open(self.point_file, "w")
            general_file = open(self.point_file + ".general", "w")

        # Calculate the coordinate values.
        coords = self.inc * (self.point - self.bounds[:, 0]) / (self.bounds[:, 1] - self.bounds[:, 0])
        for i in xrange(self.n):
            point_file.write("%-15.5g" % coords[self.swap[i]])
        point_file.write("1\n")

        # Generate the import text.
        general_file.write("file = " + self.point_file + "\n")
        general_file.write("points = 1\n")
        general_file.write("format = ascii\n")
        general_file.write("interleaving = field\n")
        general_file.write("field = locations, field0\n")
        general_file.write("structure = 3-vector, scalar\n")
        general_file.write("type = float, float\n\n")
        general_file.write("end\n")

        # Close the data and .general files.
        point_file.close()
        general_file.close()


    def general(self):
        """Function for creating the OpenDX .general file for a 3D map."""

        # Open the file.
        if self.dir:
            general_file = open(self.dir + "/" + self.file + ".general", "w")
        else:
            general_file = open(self.file + ".general", "w")

        # Generate the text.
        general_file.write("file = " + self.file + "\n")
        general_file.write("grid = " + `(self.inc + 1)` + " x " + `(self.inc + 1)` + " x " + `(self.inc + 1)` + "\n")
        general_file.write("format = ascii\n")
        general_file.write("interleaving = field\n")
        general_file.write("majority = row\n")
        general_file.write("field = data\n")
        general_file.write("structure = scalar\n")
        general_file.write("type = float\n")
        general_file.write("dependency = positions\n")
        general_file.write("positions = regular, regular, regular, 0, 1, 0, 1, 0, 1\n\n")
        general_file.write("end\n")

        # Close the file.
        general_file.close()


    def program(self):
        """Function for creating the OpenDX program for a 3D map."""

        # Open the file.
        if self.dir:
            program_file = open(self.dir + "/" + self.file + ".net", "w")
        else:
            program_file = open(self.file + ".net", "w")

        # Replacement strings
        #####################

        # Equation type specific function setup.
        self.map_labels = self.relax.specific_setup.setup("map_labels", self.relax.data.run_types[self.relax.data.run_names.index(run)])

        # Default labels.
        if self.map_labels == None or self.labels != None:
            # Axis increments.
            axis_incs = 5.0

            # Labels.
            if self.labels:
                labels = "{\"" + self.labels[self.swap[0]] + "\" \""
                labels = labels + self.labels[self.swap[1]] + "\" \""
                labels = labels + self.labels[self.swap[2]] + "\"}"
            else:
                labels = "{\"" + self.relax.data.res[self.index].params[self.run][self.swap[0]] + "\" \""
                labels = labels + self.relax.data.res[self.index].params[self.run][self.swap[1]] + "\" \""
                labels = labels + self.relax.data.res[self.index].params[self.run][self.swap[2]] + "\"}"

            # Tick locations.
            tick_locations = []
            for i in xrange(3):
                string = "{"
                inc = self.inc / axis_incs
                val = 0.0
                for i in xrange(axis_incs + 1):
                    string = string + " " + `val`
                    val = val + inc
                string = string + " }"
                tick_locations.append(string)

            # Tick values.
            tick_values = []
            inc = (self.bounds[:, 1] - self.bounds[:, 0]) / axis_incs
            for i in xrange(3):
                vals = self.bounds[self.swap[i], 0] * 1.0
                string = "{"
                for j in xrange(axis_incs + 1):
                    if self.relax.data.res[self.index].scaling.has_key(self.run):
                        string = string + "\"" + "%.2g" % (vals * self.scaling_matrix[self.swap[i], self.swap[i]]) + "\" "
                    else:
                        string = string + "\"" + "%.2g" % vals + "\" "
                    vals = vals + inc[self.swap[i]]
                string = string + "}"
                tick_values.append(string)

        # Specific labels.
        else:
            labels, tick_locations, tick_values = self.map_labels(self.run, self.index, self.relax.data.res[self.index].params[self.run], self.bounds, self.swap, self.inc, self.scaling_matrix)


        # Corners.
        corners = "{[0 0 0] [" + `self.inc` + " "  + `self.inc` + " " + `self.inc` + "]}"

        # Image setup.
        image_array1 = "[" + `0.6 * (self.inc + 1.0)` + " " + `0.3 * (self.inc + 1.0)` + " " + `0.6 * (self.inc + 1.0)` + "]"
        image_array2 = "[" + `0.6 * (self.inc + 1.0)` + " " + `0.3 * (self.inc + 1.0)` + " " + `6.0 * (self.inc + 1.0)` + "]"
        image_val = `3.0 * (self.inc + 1.0)`

        # Sphere size.
        sphere_size = `0.025 * (self.inc + 1.0)`

        # Date.
        date = asctime(localtime())

        # Generate the text.
        ####################
        text = """//
// time: """ + date + """
//
// version: 3.1.2 (format), 4.1.3 (DX)
//
//
// MODULE main
// workspace: width = 596, height = 582
// layout: snap = 0, width = 50, height = 50, align = NN
//
macro main(
) -> (
) {"""

        if self.num_points == 1:
            text = text + """
    // 
    // node Import[2]: x = 30, y = 159, inputs = 6, label = """ + self.point_file + """
    // input[1]: defaulting = 0, visible = 1, type = 32, value = \"""" + self.point_file + """.general"
    // input[3]: defaulting = 1, visible = 1, type = 32, value = "general"
    //
main_Import_2_out_1 = 
    Import(
    main_Import_2_in_1,
    main_Import_2_in_2,
    main_Import_2_in_3,
    main_Import_2_in_4,
    main_Import_2_in_5,
    main_Import_2_in_6
    ) [instance: 2, cache: 1];
    // 
    // node Glyph[1]: x = 54, y = 238, inputs = 7, label = Glyph
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "sphere"
    // input[3]: defaulting = 1, visible = 1, type = 5, value = 10.0
    // input[4]: defaulting = 0, visible = 1, type = 5, value = """ + sphere_size + """
    // input[5]: defaulting = 0, visible = 1, type = 5, value = 0.0
    //
main_Glyph_1_out_1 = 
    Glyph(
    main_Import_2_out_1,
    main_Glyph_1_in_2,
    main_Glyph_1_in_3,
    main_Glyph_1_in_4,
    main_Glyph_1_in_5,
    main_Glyph_1_in_6,
    main_Glyph_1_in_7
    ) [instance: 1, cache: 1];
    // 
    // node Color[4]: x = 102, y = 314, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 0 0]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 1.0
    //
main_Color_4_out_1 = 
    Color(
    main_Glyph_1_out_1,
    main_Color_4_in_2,
    main_Color_4_in_3,
    main_Color_4_in_4,
    main_Color_4_in_5
    ) [instance: 4, cache: 1];"""

        text = text + """
    // 
    // node Import[1]: x = 39, y = 48, inputs = 6, label = """ + self.file + """
    // input[1]: defaulting = 0, visible = 1, type = 32, value = \"""" + self.file + """.general"
    // input[3]: defaulting = 1, visible = 1, type = 32, value = "general"
    //
main_Import_1_out_1 = 
    Import(
    main_Import_1_in_1,
    main_Import_1_in_2,
    main_Import_1_in_3,
    main_Import_1_in_4,
    main_Import_1_in_5,
    main_Import_1_in_6
    ) [instance: 1, cache: 1];
    // 
    // node Isosurface[1]: x = 150, y = 42, inputs = 6, label = Outer Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 500.0
    //
main_Isosurface_1_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_1_in_2,
    main_Isosurface_1_in_3,
    main_Isosurface_1_in_4,
    main_Isosurface_1_in_5,
    main_Isosurface_1_in_6
    ) [instance: 1, cache: 1];
    // 
    // node Color[1]: x = 177, y = 121, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0 0 0.2]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.4
    //
main_Color_1_out_1 = 
    Color(
    main_Isosurface_1_out_1,
    main_Color_1_in_2,
    main_Color_1_in_3,
    main_Color_1_in_4,
    main_Color_1_in_5
    ) [instance: 1, cache: 1];
    // 
    // node Collect[1]: x = 243, y = 218, inputs = 2, label = Collect
    //
main_Collect_1_out_1 = 
    Collect("""

        if self.num_points == 1:
            text = text + "\n    main_Color_4_out_1,"
        else:
            text = text + "\n    main_Collect_1_in_1,"

        text = text + """
    main_Color_1_out_1
    ) [instance: 1, cache: 1];
    // 
    // node Isosurface[2]: x = 265, y = 42, inputs = 6, label = Middle Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 100.0
    //
main_Isosurface_2_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_2_in_2,
    main_Isosurface_2_in_3,
    main_Isosurface_2_in_4,
    main_Isosurface_2_in_5,
    main_Isosurface_2_in_6
    ) [instance: 2, cache: 1];
    // 
    // node Color[2]: x = 292, y = 121, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "blue"
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.45
    //
main_Color_2_out_1 = 
    Color(
    main_Isosurface_2_out_1,
    main_Color_2_in_2,
    main_Color_2_in_3,
    main_Color_2_in_4,
    main_Color_2_in_5
    ) [instance: 2, cache: 1];
    // 
    // node Isosurface[3]: x = 382, y = 42, inputs = 6, label = Inner Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 50.0
    //
main_Isosurface_3_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_3_in_2,
    main_Isosurface_3_in_3,
    main_Isosurface_3_in_4,
    main_Isosurface_3_in_5,
    main_Isosurface_3_in_6
    ) [instance: 3, cache: 1];
    // 
    // node Color[3]: x = 409, y = 122, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0.5 0.5 1]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.3
    //
main_Color_3_out_1 = 
    Color(
    main_Isosurface_3_out_1,
    main_Color_3_in_2,
    main_Color_3_in_3,
    main_Color_3_in_4,
    main_Color_3_in_5
    ) [instance: 3, cache: 1];
    // 
    // node Collect[2]: x = 355, y = 217, inputs = 2, label = Collect
    //
main_Collect_2_out_1 = 
    Collect(
    main_Color_2_out_1,
    main_Color_3_out_1
    ) [instance: 2, cache: 1];
    // 
    // node Isosurface[4]: x = 497, y = 42, inputs = 6, label = Inner Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 20.0
    //
main_Isosurface_4_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_4_in_2,
    main_Isosurface_4_in_3,
    main_Isosurface_4_in_4,
    main_Isosurface_4_in_5,
    main_Isosurface_4_in_6
    ) [instance: 4, cache: 1];
    // 
    // node Color[5]: x = 524, y = 122, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "white"
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.55
    //
main_Color_5_out_1 = 
    Color(
    main_Isosurface_4_out_1,
    main_Color_5_in_2,
    main_Color_5_in_3,
    main_Color_5_in_4,
    main_Color_5_in_5
    ) [instance: 5, cache: 1];
    // 
    // node Collect[4]: x = 424, y = 276, inputs = 2, label = Collect
    //
main_Collect_4_out_1 = 
    Collect(
    main_Collect_2_out_1,
    main_Color_5_out_1
    ) [instance: 4, cache: 1];
    // 
    // node Collect[3]: x = 322, y = 337, inputs = 2, label = Collect
    //
main_Collect_3_out_1 = 
    Collect(
    main_Collect_1_out_1,
    main_Collect_4_out_1
    ) [instance: 3, cache: 1];
    // 
    // node Scale[2]: x = 158, y = 425, inputs = 2, label = Scale
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 1 1]
    //
main_Scale_2_out_1 = 
    Scale(
    main_Collect_3_out_1,
    main_Scale_2_in_2
    ) [instance: 2, cache: 1];
    // 
    // node AutoCamera[1]: x = 323, y = 443, inputs = 9, label = AutoCamera
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 -1 1]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 500.0
    // input[5]: defaulting = 0, visible = 0, type = 5, value = .75
    // input[6]: defaulting = 0, visible = 0, type = 8, value = [-1 1 0 ]
    // input[7]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[8]: defaulting = 0, visible = 0, type = 5, value = 30.0
    // input[9]: defaulting = 0, visible = 0, type = 32, value = "black"
    //
main_AutoCamera_1_out_1 = 
    AutoCamera(
    main_Scale_2_out_1,
    main_AutoCamera_1_in_2,
    main_AutoCamera_1_in_3,
    main_AutoCamera_1_in_4,
    main_AutoCamera_1_in_5,
    main_AutoCamera_1_in_6,
    main_AutoCamera_1_in_7,
    main_AutoCamera_1_in_8,
    main_AutoCamera_1_in_9
    ) [instance: 1, cache: 1];
    // 
    // node AutoAxes[1]: x = 170, y = 520, inputs = 19, label = AutoAxes
    // input[3]: defaulting = 0, visible = 1, type = 16777248, value = """ + labels + """
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 30
    // input[5]: defaulting = 0, visible = 1, type = 16777224, value = """ + corners + """
    // input[6]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[7]: defaulting = 1, visible = 0, type = 3, value = 1
    // input[9]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[12]: defaulting = 0, visible = 0, type = 5, value = 0.4
    // input[13]: defaulting = 0, visible = 0, type = 32, value = "area"
    // input[14]: defaulting = 0, visible = 1, type = 16777221, value = """ + tick_locations[0] + """
    // input[15]: defaulting = 0, visible = 1, type = 16777221, value = """ + tick_locations[1] + """
    // input[16]: defaulting = 0, visible = 1, type = 16777221, value = """ + tick_locations[2] + """
    // input[17]: defaulting = 0, visible = 1, type = 16777248, value = """ + tick_values[0] + """
    // input[18]: defaulting = 0, visible = 1, type = 16777248, value = """ + tick_values[1] + """
    // input[19]: defaulting = 0, visible = 1, type = 16777248, value = """ + tick_values[2] + """
    //
main_AutoAxes_1_out_1 = 
    AutoAxes(
    main_Scale_2_out_1,
    main_AutoCamera_1_out_1,
    main_AutoAxes_1_in_3,
    main_AutoAxes_1_in_4,
    main_AutoAxes_1_in_5,
    main_AutoAxes_1_in_6,
    main_AutoAxes_1_in_7,
    main_AutoAxes_1_in_8,
    main_AutoAxes_1_in_9,
    main_AutoAxes_1_in_10,
    main_AutoAxes_1_in_11,
    main_AutoAxes_1_in_12,
    main_AutoAxes_1_in_13,
    main_AutoAxes_1_in_14,
    main_AutoAxes_1_in_15,
    main_AutoAxes_1_in_16,
    main_AutoAxes_1_in_17,
    main_AutoAxes_1_in_18,
    main_AutoAxes_1_in_19
    ) [instance: 1, cache: 1];
    // 
    // node Image[2]: x = 510, y = 480, inputs = 49, label = Image
    // input[1]: defaulting = 0, visible = 0, type = 67108863, value = "Image_2"
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 1
    // input[5]: defaulting = 0, visible = 0, type = 8, value = """ + image_array1 + """
    // input[6]: defaulting = 0, visible = 0, type = 8, value = """ + image_array2 + """
    // input[7]: defaulting = 0, visible = 0, type = 5, value = """ + image_val + """
    // input[8]: defaulting = 0, visible = 0, type = 1, value = 1258
    // input[9]: defaulting = 0, visible = 0, type = 5, value = 0.757
    // input[10]: defaulting = 0, visible = 0, type = 8, value = [0 1 0]
    // input[11]: defaulting = 1, visible = 0, type = 5, value = 30.0000
    // input[12]: defaulting = 0, visible = 0, type = 1, value = 0
    // input[14]: defaulting = 0, visible = 0, type = 1, value = 1
    // input[15]: defaulting = 1, visible = 0, type = 32, value = "none"
    // input[16]: defaulting = 1, visible = 0, type = 32, value = "none"
    // input[17]: defaulting = 1, visible = 0, type = 1, value = 1
    // input[18]: defaulting = 1, visible = 0, type = 1, value = 1
    // input[19]: defaulting = 0, visible = 0, type = 1, value = 0
    // input[25]: defaulting = 0, visible = 0, type = 32, value = "best"
    // input[26]: defaulting = 0, visible = 0, type = 32, value = "tiff"
    // input[29]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[30]: defaulting = 1, visible = 0, type = 16777248, value = """ + labels + """
    // input[32]: defaulting = 1, visible = 0, type = 16777224, value = """ + corners + """
    // input[33]: defaulting = 0, visible = 0, type = 3, value = 1
    // input[34]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[36]: defaulting = 0, visible = 0, type = 3, value = 1
    // input[41]: defaulting = 0, visible = 0, type = 32, value = "rotate"
    // depth: value = 24
    // window: position = (0.0000,0.0000), size = 0.9938x0.9727
    // internal caching: 1
    //
main_Image_2_out_1,
main_Image_2_out_2,
main_Image_2_out_3 = 
    Image(
    main_Image_2_in_1,
    main_AutoAxes_1_out_1,
    main_Image_2_in_3,
    main_Image_2_in_4,
    main_Image_2_in_5,
    main_Image_2_in_6,
    main_Image_2_in_7,
    main_Image_2_in_8,
    main_Image_2_in_9,
    main_Image_2_in_10,
    main_Image_2_in_11,
    main_Image_2_in_12,
    main_Image_2_in_13,
    main_Image_2_in_14,
    main_Image_2_in_15,
    main_Image_2_in_16,
    main_Image_2_in_17,
    main_Image_2_in_18,
    main_Image_2_in_19,
    main_Image_2_in_20,
    main_Image_2_in_21,
    main_Image_2_in_22,
    main_Image_2_in_23,
    main_Image_2_in_24,
    main_Image_2_in_25,
    main_Image_2_in_26,
    main_Image_2_in_27,
    main_Image_2_in_28,
    main_Image_2_in_29,
    main_Image_2_in_30,
    main_Image_2_in_31,
    main_Image_2_in_32,
    main_Image_2_in_33,
    main_Image_2_in_34,
    main_Image_2_in_35,
    main_Image_2_in_36,
    main_Image_2_in_37,
    main_Image_2_in_38,
    main_Image_2_in_39,
    main_Image_2_in_40,
    main_Image_2_in_41,
    main_Image_2_in_42,
    main_Image_2_in_43,
    main_Image_2_in_44,
    main_Image_2_in_45,
    main_Image_2_in_46,
    main_Image_2_in_47,
    main_Image_2_in_48,
    main_Image_2_in_49
    ) [instance: 2, cache: 1];
// network: end of macro body
CacheScene(main_Image_2_in_1, main_Image_2_out_1, main_Image_2_out_2);
}"""

        if self.num_points == 1:
            text = text + """
main_Import_2_in_1 = \"""" + self.point_file + """.general";
main_Import_2_in_2 = NULL;
main_Import_2_in_3 = NULL;
main_Import_2_in_4 = NULL;
main_Import_2_in_5 = NULL;
main_Import_2_in_6 = NULL;
main_Import_2_out_1 = NULL;
main_Glyph_1_in_2 = "sphere";
main_Glyph_1_in_3 = NULL;
main_Glyph_1_in_4 = """ + sphere_size + """;
main_Glyph_1_in_5 = 0.0;
main_Glyph_1_in_6 = NULL;
main_Glyph_1_in_7 = NULL;
main_Glyph_1_out_1 = NULL;
main_Color_4_in_2 = [1 0 0];
main_Color_4_in_3 = 1.0;
main_Color_4_in_4 = NULL;
main_Color_4_in_5 = NULL;
main_Color_4_out_1 = NULL;"""

        text = text + """
main_Import_1_in_1 = \"""" + self.file + """.general";
main_Import_1_in_2 = NULL;
main_Import_1_in_3 = NULL;
main_Import_1_in_4 = NULL;
main_Import_1_in_5 = NULL;
main_Import_1_in_6 = NULL;
main_Import_1_out_1 = NULL;
main_Isosurface_1_in_2 = 50.0;
main_Isosurface_1_in_3 = NULL;
main_Isosurface_1_in_4 = NULL;
main_Isosurface_1_in_5 = NULL;
main_Isosurface_1_in_6 = NULL;
main_Isosurface_1_out_1 = NULL;
main_Color_1_in_2 = [0 0 0.2];
main_Color_1_in_3 = 0.4;
main_Color_1_in_4 = NULL;
main_Color_1_in_5 = NULL;
main_Color_1_out_1 = NULL;"""

        if self.num_points == 1:
            pass
        else:
            text = text + "\nmain_Collect_1_in_1 = NULL;"

        text = text + """
main_Collect_1_out_1 = NULL;
main_Isosurface_2_in_2 = 10.0;
main_Isosurface_2_in_3 = NULL;
main_Isosurface_2_in_4 = NULL;
main_Isosurface_2_in_5 = NULL;
main_Isosurface_2_in_6 = NULL;
main_Isosurface_2_out_1 = NULL;
main_Color_2_in_2 = "blue";
main_Color_2_in_3 = 0.45;
main_Color_2_in_4 = NULL;
main_Color_2_in_5 = NULL;
main_Color_2_out_1 = NULL;
main_Isosurface_3_in_2 = 5.0;
main_Isosurface_3_in_3 = NULL;
main_Isosurface_3_in_4 = NULL;
main_Isosurface_3_in_5 = NULL;
main_Isosurface_3_in_6 = NULL;
main_Isosurface_3_out_1 = NULL;
main_Color_3_in_2 = [0.5 0.5 1];
main_Color_3_in_3 = 0.3;
main_Color_3_in_4 = NULL;
main_Color_3_in_5 = NULL;
main_Color_3_out_1 = NULL;
main_Collect_2_out_1 = NULL;
main_Isosurface_4_in_2 = 2.0;
main_Isosurface_4_in_3 = NULL;
main_Isosurface_4_in_4 = NULL;
main_Isosurface_4_in_5 = NULL;
main_Isosurface_4_in_6 = NULL;
main_Isosurface_4_out_1 = NULL;
main_Color_5_in_2 = "white";
main_Color_5_in_3 = 1.0;
main_Color_5_in_4 = NULL;
main_Color_5_in_5 = NULL;
main_Color_5_out_1 = NULL;
main_Collect_4_out_1 = NULL;
main_Collect_3_out_1 = NULL;
main_Scale_2_in_2 = [1 1 1];
main_Scale_2_out_1 = NULL;
main_AutoCamera_1_in_2 = [1 -1 1];
main_AutoCamera_1_in_3 = 500.0;
main_AutoCamera_1_in_4 = NULL;
main_AutoCamera_1_in_5 = .75;
main_AutoCamera_1_in_6 = [-1 1 0 ];
main_AutoCamera_1_in_7 = 0;
main_AutoCamera_1_in_8 = 30.0;
main_AutoCamera_1_in_9 = "black";
main_AutoCamera_1_out_1 = NULL;
main_AutoAxes_1_in_3 = """ + labels + """;
main_AutoAxes_1_in_4 = 30;
main_AutoAxes_1_in_5 = """ + corners + """;
main_AutoAxes_1_in_6 = 1;
main_AutoAxes_1_in_7 = NULL;
main_AutoAxes_1_in_8 = NULL;
main_AutoAxes_1_in_9 = 1;
main_AutoAxes_1_in_10 = NULL;
main_AutoAxes_1_in_11 = NULL;
main_AutoAxes_1_in_12 = 0.4;
main_AutoAxes_1_in_13 = "area";
main_AutoAxes_1_in_14 = """ + tick_locations[0] + """;
main_AutoAxes_1_in_15 = """ + tick_locations[1] + """;
main_AutoAxes_1_in_16 = """ + tick_locations[2] + """;
main_AutoAxes_1_in_17 = """ + tick_values[0] + """;
main_AutoAxes_1_in_18 = """ + tick_values[1] + """;
main_AutoAxes_1_in_19 = """ + tick_values[2] + """;
main_AutoAxes_1_out_1 = NULL;
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
main_Image_2_in_1 = "Image_2";
main_Image_2_in_3 = "X24,,";
main_Image_2_in_4 = 1;
main_Image_2_in_5 = """ + image_array1 + """;
main_Image_2_in_6 = """ + image_array2 + """;
main_Image_2_in_7 = """ + image_val + """;
main_Image_2_in_8 = 1258;
main_Image_2_in_9 = 0.757;
main_Image_2_in_10 = [0 1 0];
main_Image_2_in_11 = 30.0000;
main_Image_2_in_12 = 0;
main_Image_2_in_13 = NULL;
main_Image_2_in_14 = 1;
main_Image_2_in_15 = NULL;
main_Image_2_in_16 = NULL;
main_Image_2_in_17 = NULL;
main_Image_2_in_18 = NULL;
main_Image_2_in_19 = 0;
main_Image_2_in_20 = NULL;
main_Image_2_in_21 = NULL;
main_Image_2_in_22 = NULL;
main_Image_2_in_23 = NULL;
main_Image_2_in_25 = "best";
main_Image_2_in_26 = "tiff";
main_Image_2_in_27 = NULL;
main_Image_2_in_28 = NULL;
main_Image_2_in_29 = 0;
main_Image_2_in_30 = NULL;
main_Image_2_in_31 = NULL;
main_Image_2_in_32 = NULL;
main_Image_2_in_33 = 1;
main_Image_2_in_34 = 0;
main_Image_2_in_35 = NULL;
main_Image_2_in_36 = 1;
main_Image_2_in_37 = NULL;
main_Image_2_in_38 = NULL;
main_Image_2_in_39 = NULL;
main_Image_2_in_40 = NULL;
main_Image_2_in_41 = "rotate";
main_Image_2_in_42 = NULL;
main_Image_2_in_43 = NULL;
main_Image_2_in_44 = NULL;
main_Image_2_in_45 = NULL;
main_Image_2_in_46 = NULL;
main_Image_2_in_47 = NULL;
main_Image_2_in_48 = NULL;
main_Image_2_in_49 = NULL;
Executive("product version 4 1 3");
$sync
main();
"""

        program_file.write(text)

        # Close the file.
        program_file.close()
