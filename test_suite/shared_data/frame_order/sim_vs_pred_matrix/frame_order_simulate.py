# relax script.

# Python module imports.
from math import cos, pi, sin, sqrt
from numpy import array, cross, dot, eye, float64, outer, transpose, zeros
from numpy.linalg import det, inv, norm
from string import lower
import sys

# relax module imports.
from lib.geometry.angles import wrap_angles
from lib.geometry.rotations import R_random_hypersphere, R_to_euler_zyz


# Variables.
MODEL = 'pseudo-ellipse'
SAMPLE_SIZE = 100
TAG = 'in_frame'

# Angular restrictions.
THETA_X = pi / 4
THETA_Y = 3 * pi / 8
THETA_Z = pi / 6
INC = 18
VAR = 'Y'

# The frame order eigenframe - I.
if TAG == 'in_frame':
    EIG_FRAME = eye(3)

# The frame order eigenframe - rotated.
if TAG == 'out_of_frame':
    EIG_FRAME = array([[ 2, -1,  2],
                       [ 2,  2, -1],
                       [-1,  2,  2]], float64) / 3.0

# The frame order eigenframe (and tag) - original isotropic cone axis [2, 1, 3].
elif TAG == 'axis2_1_3':
    # Generate 3 orthogonal vectors.
    vect_z = array([2, 1, 3], float64)
    vect_x = cross(vect_z, array([1, 1, 1], float64))
    vect_y = cross(vect_z, vect_x)

    # Normalise.
    vect_x = vect_x / norm(vect_x)
    vect_y = vect_y / norm(vect_y)
    vect_z = vect_z / norm(vect_z)

    # Build the frame.
    EIG_FRAME = zeros((3, 3), float64)
    EIG_FRAME[:,0] = vect_x
    EIG_FRAME[:,1] = vect_y
    EIG_FRAME[:,2] = vect_z



class Frame_order:
    def __init__(self):
        """Calculate the frame order at infinity.

        This is when the starting positions are random.
        """

        # The tag.
        self.tag = '_%s_%s_theta_%s_ens%s.agr' % (MODEL, TAG, lower(VAR), SAMPLE_SIZE)

        # Set the initial storage structures.
        self.init_storage()

        # Init.
        index, type, round = 0, 0, 0
        char = ['/', '-', '\\', '|']

        # Loop over random starting positions.
        while 1:
            # Print out.
            if not index % 200:
                # Sim number.
                sys.stdout.write("\b"*100 + "Sim: %-9i %s" % (index, char[type]))
                sys.stdout.flush()

                # Twirly thing index.
                type += 1
                round += 1
                if type == 4: type = 0

            # Get the random rotation.
            R_random_hypersphere(self.rot)

            # Rotate the frame.
            frame = dot(self.rot, EIG_FRAME)

            # The rotation in the eigenframe.
            rot_eig = dot(transpose(EIG_FRAME), frame)

            # Loop over the angle incs.
            for i in range(INC):
                # Inside the cone.
                if not self.full[i] and self.inside(i, rot_eig):
                    # Sum of rotations and cross products.
                    self.first_frame_order[i] = self.first_frame_order[i] + self.rot
                    self.second_frame_order[i] = self.second_frame_order[i] + outer(self.rot, self.rot)

                    # Increment the counter.
                    self.count[i] = self.count[i] + 1

                    # Full.
                    if self.count[i] == SAMPLE_SIZE:
                        sys.stdout.write("\b"*100 + "The angle restriction of %s deg is complete.\n" % self.get_angle(i, deg=True))
                        self.full[i] = 1

            # Increment the global index.
            index = index + 1

            # Break out.
            if sum(self.full) == INC:
                break

        # Average.
        self.first_frame_order = self.first_frame_order / float(SAMPLE_SIZE)
        self.second_frame_order = self.second_frame_order / float(SAMPLE_SIZE)

        # Write the data.
        self.write_data()


    def get_angle(self, index, deg=False):
        """Return the angle corresponding to the incrementation index."""

        # The angle of one increment.
        inc_angle = pi / INC

        # The angle of the increment.
        angle = inc_angle * (index+1)

        # Return.
        if deg:
            return angle / (2*pi) * 360
        else:
            return angle


    def init_storage(self):
        """Initialise the storage structures."""

        # Create the average rotation matrix (first order).
        self.first_frame_order = zeros((INC, 3, 3), float64)

        # Create the frame order matrix (each element is ensemble averaged and corresponds to a different time step).
        self.second_frame_order = zeros((INC, 9, 9), float64)

        # Init the rotation matrix.
        self.rot = zeros((3, 3), float64)

        # Some data arrays.
        self.full = zeros(INC)
        self.count = zeros(INC)


    def inside(self, i, frame):
        """Determine if the frame is inside the limits."""

        # The new limits.
        theta_x, theta_y, theta_z = self.limits(i)

        # Decompose the frame into the zyz Euler angles.
        alpha, beta, gamma = R_to_euler_zyz(frame)

        # Sanity check!
        if beta > pi or beta < 0:
            raise NameError, "A beta value of %s is not possible!" % beta

        # Convert to tilt and torsion angles (properly wrapped).
        theta = beta
        phi = wrap_angles(gamma, -pi, pi)
        sigma = wrap_angles(alpha + gamma, -pi, pi)

        # Check for a torsion angle violation.
        if sigma < -theta_z or sigma > theta_z:
            return False

        # Check for a tilt angle violation.
        theta_max = 1.0 / sqrt(cos(phi)**2 / theta_x**2 + sin(phi)**2 / theta_y**2)
        if theta > theta_max:
            return False

        # Inside.
        return True


    def limits(self, i):
        """Determine the angular restrictions for the increment i."""

        # Get the angle for the increment.
        theta = self.get_angle(i)

        # Vary X.
        if VAR == 'X':
            return theta, THETA_Y, THETA_Z

        # Vary Y.
        elif VAR == 'Y':
            return THETA_X, theta, THETA_Z

        # Vary Z.
        elif VAR == 'Z':
            return THETA_X, THETA_Y, theta

        # Simulate the isotropic cone.
        elif VAR == 'ISO':
            return theta, theta, pi


    def write_data(self):
        """Dump the data to files."""

        # Open the files.
        file_1st = open("Sij" + self.tag, 'w')
        file_2nd = open("Sijkl" + self.tag, 'w')
        files = [file_1st, file_2nd]

        # The headers.
        for i in range(2):
            # Alias the file.
            file = files[i]

            # The titles.
            file.write("@with g0\n")
            if i == 0:
                file.write("@    world 0, 0, 180, 1\n")
            else:
                file.write("@    world 0, -0.5, 180, 1\n")
            file.write("@    title \"Simulated frame order matrix elements\"\n")
            if i == 0:
                file.write("@    subtitle \"1\\Sst\\N degree matrix, %i simulations\"\n" % SAMPLE_SIZE)
            else:
                file.write("@    subtitle \"2\\Snd\\N degree matrix, %i simulations\"\n" % SAMPLE_SIZE)

            # Legend.
            if i == 0:
                file.write("@    legend 0.23, 0.55\n")
            else:
                file.write("@    legend off\n")

            # Plot data.
            file.write("@    xaxis  bar linewidth 0.5\n")
            file.write("@    xaxis  label \"Cone half-angle \\xq\\f{}\\s%s\\N (deg.)\"\n" % VAR)
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

            file.write("\n")

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
                for k in range(INC):
                    # Get the angle.
                    angle = self.get_angle(k, deg=True)

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
                for k in range(INC):
                    # Get the angle.
                    angle = self.get_angle(k, deg=True)

                    # Write.
                    file_2nd.write('%s %s\n' % (angle, self.second_frame_order[k, i, j]))

                # Footer.
                file_2nd.write('&\n')

                # Inc.
                graph_num = graph_num + 1

        # No autoscaling.
        file_1st.write("@autoscale onread none\n")
        file_2nd.write("@autoscale onread none\n")



# Calculate the frame order.
Frame_order()
