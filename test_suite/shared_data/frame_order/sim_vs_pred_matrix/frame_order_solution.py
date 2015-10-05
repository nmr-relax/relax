# relax script!

# Python module imports.
from math import pi
from numpy import array, cross, eye, float64, zeros
from numpy.linalg import norm
from string import lower

# relax module imports.
from lib.errors import RelaxError
from lib.frame_order import double_rotor, free_rotor, iso_cone, iso_cone_free_rotor, iso_cone_torsionless, pseudo_ellipse, pseudo_ellipse_free_rotor, pseudo_ellipse_torsionless, rotor
from lib.linear_algebra.kronecker_product import kron_prod

# Variables.
MODELS = [
    'rotor',
    'free_rotor',
    'iso_cone',
    'iso_cone_torsionless',
    'iso_cone_free_rotor',
    'pseudo-ellipse',
    'pseudo-ellipse_torsionless',
    'pseudo-ellipse_free_rotor',
    'double_rotor'
]
MODEL_TEXT = [
    'Rotor frame order model',
    'Free-rotor frame order model',
    'Isotropic cone frame order model',
    'Isotropic cone, torsionless frame order model',
    'Isotropic cone, free rotor frame order model',
    'Pseudo-ellipse frame order model',
    'Pseudo-ellipse, torsionless frame order model',
    'Pseudo-ellipse, free rotor frame order model',
    'Double rotor frame order model'
]
TAGS = [
    'in_frame',
    'out_of_frame',
    'axis2_1_3'
]

# Angular restrictions.
THETA_X = pi / 4
THETA_Y = 3 * pi / 8
THETA_Z = pi / 6
INC = 18


class Frame_order:
    def __init__(self):
        """Calculate the frame order at infinity.

        This is when the starting positions are random.
        """

        # Loop over the models.
        for model_index in range(len(MODELS)):
            # Aliases.
            model = MODELS[model_index]
            model_text = MODEL_TEXT[model_index]

            # Loop over the tags.
            for tag in TAGS:
                # Set up the variables to loop over.
                if model in ['rotor', 'free_rotor']:
                    vars = ['Z']
                elif model in ['iso_cone_free_rotor', 'iso_cone_torsionless']:
                    vars = ['X']
                elif model in ['iso_cone']:
                    vars = ['X', 'Z']
                elif model in ['double_rotor', 'pseudo-ellipse_free_rotor', 'pseudo-ellipse_torsionless']:
                    vars = ['X', 'Y']
                elif model in ['pseudo-ellipse']:
                    vars = ['X', 'Y', 'Z']
                else:
                    raise RelaxError("Unknown model '%s'." % model)

                # Loop over the variables.
                for var in vars:
                    # The file name.
                    file_name = '_%s_%s_theta_%s_calc.agr' % (model, tag, lower(var))
                    print("Creating the '*%s' files." % file_name)

                    # Set up the eigenframe.
                    self.setup_eigenframe(tag=tag)

                    # The Kronecker product of the eigenframe rotation.
                    Rx2_eigen = kron_prod(self.eigenframe, self.eigenframe)

                    # Set the initial storage structures.
                    self.init_storage()

                    # Loop over the angle incs.
                    for i in range(INC+1):
                        # Get the angle for the increment.
                        theta = self.get_angle(i-1, model=model, var=var)

                        # Vary X.
                        if var == 'X':
                            theta_x = theta
                            theta_y = THETA_Y
                            theta_z = THETA_Z

                        # Vary Y.
                        elif var == 'Y':
                            theta_x = THETA_X
                            theta_y = theta
                            theta_z = THETA_Z

                        # Vary Z.
                        elif var == 'Z':
                            theta_x = THETA_X
                            theta_y = THETA_Y
                            theta_z = theta

                        # Calculate the frame order matrices.
                        if model == 'rotor':
                            self.first_frame_order[i] = rotor.compile_1st_matrix_rotor(self.first_frame_order[i], self.eigenframe, theta_z)
                            self.second_frame_order[i] = rotor.compile_2nd_matrix_rotor(self.second_frame_order[i], Rx2_eigen, theta_z)
                        elif model == 'free_rotor':
                            self.first_frame_order[i] = free_rotor.compile_1st_matrix_free_rotor(self.first_frame_order[i], self.eigenframe)
                            self.second_frame_order[i] = free_rotor.compile_2nd_matrix_free_rotor(self.second_frame_order[i], Rx2_eigen)
                        elif model == 'iso_cone':
                            self.first_frame_order[i] = iso_cone.compile_1st_matrix_iso_cone(self.first_frame_order[i], self.eigenframe, theta_x, theta_z)
                            self.second_frame_order[i] = iso_cone.compile_2nd_matrix_iso_cone(self.second_frame_order[i], Rx2_eigen, theta_x, theta_z)
                        elif model == 'iso_cone_free_rotor':
                            self.first_frame_order[i] = iso_cone_free_rotor.compile_1st_matrix_iso_cone_free_rotor(self.first_frame_order[i], self.eigenframe, theta_x)
                            self.second_frame_order[i] = iso_cone_free_rotor.compile_2nd_matrix_iso_cone_free_rotor(self.second_frame_order[i], Rx2_eigen, theta_x)
                        elif model == 'iso_cone_torsionless':
                            self.first_frame_order[i] = iso_cone_torsionless.compile_1st_matrix_iso_cone_torsionless(self.first_frame_order[i], self.eigenframe, theta_x)
                            self.second_frame_order[i] = iso_cone_torsionless.compile_2nd_matrix_iso_cone_torsionless(self.second_frame_order[i], Rx2_eigen, theta_x)
                        elif model == 'pseudo-ellipse':
                            self.first_frame_order[i] = pseudo_ellipse.compile_1st_matrix_pseudo_ellipse(self.first_frame_order[i], self.eigenframe, theta_x, theta_y, theta_z)
                            self.second_frame_order[i] = pseudo_ellipse.compile_2nd_matrix_pseudo_ellipse(self.second_frame_order[i], Rx2_eigen, theta_x, theta_y, theta_z)
                        elif model == 'pseudo-ellipse_free_rotor':
                            self.first_frame_order[i] = pseudo_ellipse_free_rotor.compile_1st_matrix_pseudo_ellipse_free_rotor(self.first_frame_order[i], self.eigenframe, theta_x, theta_y)
                            self.second_frame_order[i] = pseudo_ellipse_free_rotor.compile_2nd_matrix_pseudo_ellipse_free_rotor(self.second_frame_order[i], Rx2_eigen, theta_x, theta_y)
                        elif model == 'pseudo-ellipse_torsionless':
                            self.first_frame_order[i] = pseudo_ellipse_torsionless.compile_1st_matrix_pseudo_ellipse_torsionless(self.first_frame_order[i], self.eigenframe, theta_x, theta_y)
                            self.second_frame_order[i] = pseudo_ellipse_torsionless.compile_2nd_matrix_pseudo_ellipse_torsionless(self.second_frame_order[i], Rx2_eigen, theta_x, theta_y)
                        elif model == 'double_rotor':
                            self.first_frame_order[i] = double_rotor.compile_1st_matrix_double_rotor(self.first_frame_order[i], self.eigenframe, theta_y, theta_x)
                            self.second_frame_order[i] = double_rotor.compile_2nd_matrix_double_rotor(self.second_frame_order[i], Rx2_eigen, theta_y, theta_x)
                        else:
                            raise RelaxError("Unknown model '%s'." % model)

                    # Write the data.
                    self.write_data(file_name=file_name, model=model, model_text=model_text, var=var)


    def get_angle(self, index, model=None, var=None, deg=False):
        """Return the angle corresponding to the incrementation index."""

        # The angle of one increment.
        inc_angle = pi / INC

        # The angle of the increment.
        angle = inc_angle * (index+1)

        # Slightly offset from zero for the first increment, to avoid artifacts in the pseudo-ellipse equations.
        if model in ['pseudo-ellipse', 'pseudo-ellipse_free_rotor', 'pseudo-ellipse_torsionless'] and var in ['X', 'Y'] and angle == 0.0:
            angle = 0.01

        # Return.
        if deg:
            return angle / (2*pi) * 360
        else:
            return angle


    def init_storage(self):
        """Initialise the storage structures."""

        # Create the average rotation matrix (first order).
        self.first_frame_order = zeros((INC+1, 3, 3), float64)

        # Create the frame order matrix (each element is ensemble averaged and corresponds to a different time step).
        self.second_frame_order = zeros((INC+1, 9, 9), float64)

        # Init the rotation matrix.
        self.rot = zeros((3, 3), float64)

        # Some data arrays.
        self.full = zeros(INC+1)
        self.count = zeros(INC+1)


    def setup_eigenframe(self, tag=None):
        """Construct the eigenframe for the given tag.

        @keyword tag:   The frame to use.  It should be one of 'in_frame', 'out_of_frame', or 'axis2_1_3'.
        @type tag:      str
        """

        # The frame order eigenframe - I.
        if tag == 'in_frame':
            self.eigenframe = eye(3)
        
        # The frame order eigenframe - rotated.
        elif tag == 'out_of_frame':
            self.eigenframe = array([[ 2, -1,  2],
                               [ 2,  2, -1],
                               [-1,  2,  2]], float64) / 3.0

        # The frame order eigenframe (and tag) - original isotropic cone axis [2, 1, 3].
        elif tag == 'axis2_1_3':
            # Generate 3 orthogonal vectors.
            vect_z = array([2, 1, 3], float64)
            vect_x = cross(vect_z, array([1, 1, 1], float64))
            vect_y = cross(vect_z, vect_x)

            # Normalise.
            vect_x = vect_x / norm(vect_x)
            vect_y = vect_y / norm(vect_y)
            vect_z = vect_z / norm(vect_z)

            # Build the frame.
            self.eigenframe = zeros((3, 3), float64)
            self.eigenframe[:, 0] = vect_x
            self.eigenframe[:, 1] = vect_y
            self.eigenframe[:, 2] = vect_z


    def write_data(self, file_name=None, model=None, model_text=None, var=None):
        """Dump the data to files.

        @keyword file_name:     The end part of the files to create.  This will be prepended by either 'Sij' or 'Sijkl'.
        @type file_name:        str
        @keyword model_text:    The text describing the model to use in the subheading.
        @type model_text:       str
        @keyword var:           The name of the half-angle being varied for labelling the X-axis.
        @type var:              str
        """

        # Open the files.
        file_1st = open("Sij" + file_name, 'w')
        file_2nd = open("Sijkl" + file_name, 'w')
        files = [file_1st, file_2nd]

        # The headers.
        for i in range(2):
            # Alias the file.
            file = files[i]

            # The titles.
            file.write("@with g0\n")
            if i == 0:
                file.write("@    world 0, -0.2, 180, 1\n")
            else:
                file.write("@    world 0, -0.7, 180, 1\n")
            file.write("@    title \"Calculated frame order matrix elements\"\n")
            if i == 0:
                file.write("@    subtitle \"%s, 1\\Sst\\N degree matrix\"\n" % model_text)
            else:
                file.write("@    subtitle \"%s, 2\\Snd\\N degree matrix\"\n" % model_text)

            # Legend.
            if i == 0:
                file.write("@    legend 0.23, 0.55\n")
            else:
                file.write("@    legend off\n")

            # Plot data.
            file.write("@    xaxis  bar linewidth 0.5\n")
            file.write("@    xaxis  label \"Cone half-angle \\xq\\f{}\\s%s\\N (deg.)\"\n" % var)
            file.write("@    xaxis  label char size 1.000000\n")
            file.write("@    xaxis  tick major 45\n")
            file.write("@    xaxis  tick major linewidth 0.5\n")
            file.write("@    xaxis  tick minor ticks 3\n")
            file.write("@    xaxis  tick minor linewidth 0.5\n")
            file.write("@    yaxis  bar linewidth 0.5\n")
            if i == 0:
                file.write("@    yaxis  label \"Order parameter \qS\sij\"\n")
            else:
                file.write("@    yaxis  label \"Order parameter \qS\sijkl\"\n")
            file.write("@    yaxis  label char size 1.000000\n")
            file.write("@    yaxis  tick major 0.2\n")
            file.write("@    yaxis  tick major linewidth 0.5\n")
            file.write("@    yaxis  tick minor ticks 1\n")
            file.write("@    yaxis  tick minor linewidth 0.5\n")

        # Header for first order matrix.
        graph_num = 0
        for i in range(3):
            for j in range(3):
                # Legend.
                file_1st.write("@    s%i legend \"\\q<c\\s%s%s\\N>\"\n" % (graph_num, i+1, j+1))
                file_1st.write("@    s%i linewidth 0.5\n" % graph_num)

                # Inc.
                graph_num = graph_num + 1

        # Header for second order matrix.
        graph_num = 0
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        # Legend.
                        file_2nd.write("@    s%i legend \"<\\qc\\s%s%s\\N.c\\s%s%s\\N>\"\n" % (graph_num, i+1, j+1, k+1, l+1))
                        file_2nd.write("@    s%i linewidth 0.5\n" % graph_num)

                        # Inc.
                        graph_num = graph_num + 1

        # Loop over the first rotation matrix index.
        graph_num = 0
        for i in range(3):
            # Loop over the second rotation matrix index.
            for j in range(3):
                # Header.
                file_1st.write("@target G0.S%i\n" % graph_num)
                file_1st.write("@type xy\n")

                # Loop over each time point.
                for k in range(INC+1):
                    # Get the angle.
                    angle = self.get_angle(k-1, model=model, var=var, deg=True)

                    # Write.
                    file_1st.write("%s %s\n" % (angle, self.first_frame_order[k, i, j]))

                # Footer.
                file_1st.write("&\n")

                # Inc.
                graph_num = graph_num + 1

        # Loop over the first frame order index.
        graph_num = 0
        for i in range(9):
            # Loop over the second frame order index.
            for j in range(9):
                # Header.
                file_2nd.write('@target G0.S%i\n' % graph_num)
                file_2nd.write('@type xy\n')

                # Loop over each time point.
                for k in range(INC+1):
                    # Get the angle.
                    angle = self.get_angle(k-1, model=model, var=var, deg=True)

                    # Write.
                    file_2nd.write('%s %s\n' % (angle, self.second_frame_order[k, i, j]))

                # Footer.
                file_2nd.write('&\n')

                # Inc.
                graph_num = graph_num + 1

        # No autoscaling.
        file_1st.write("@autoscale onread none\n")
        file_2nd.write("@autoscale onread none\n")

        # Close the files.
        file_1st.close()
        file_2nd.close()


# Calculate the frame order.
Frame_order()
