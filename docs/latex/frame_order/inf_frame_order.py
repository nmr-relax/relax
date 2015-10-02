# relax script.

# Python module imports.
from math import cos, pi, sin, sqrt
from numpy import array, cross, dot, eye, float64, transpose, zeros
from numpy.linalg import norm
from random import uniform
from string import lower
import sys

# relax module imports.
from lib.errors import RelaxError
from lib.geometry.angles import wrap_angles
from lib.geometry.rotations import axis_angle_to_R, R_random_hypersphere, R_to_euler_zyz, tilt_torsion_to_R
from lib.linear_algebra.kronecker_product import kron_prod
from lib.text.progress import progress_meter


# Variables.
#MODEL = 'rotor'
#MODEL = 'free_rotor'
#MODEL = 'iso_cone'
#MODEL = 'iso_cone_torsionless'
#MODEL = 'iso_cone_free_rotor'
#MODEL = 'pseudo-ellipse'
#MODEL = 'pseudo-ellipse_torsionless'
#MODEL = 'pseudo-ellipse_free_rotor'
MODEL = 'double_rotor'
#MODEL_TEXT = 'Rotor frame order model'
#MODEL_TEXT = 'Free rotor frame order model'
#MODEL_TEXT = 'Isotropic cone frame order model'
#MODEL_TEXT = 'Torsionless isotropic cone frame order model'
#MODEL_TEXT = 'Free rotor isotropic cone frame order model'
#MODEL_TEXT = 'Pseudo-ellipse frame order model'
#MODEL_TEXT = 'Torsionless pseudo-ellipse frame order model'
#MODEL_TEXT = 'Free rotor pseudo-ellipse frame order model'
MODEL_TEXT = 'Double rotor frame order model'
SAMPLE_SIZE = 1000000
TAG = 'in_frame'
#TAG = 'out_of_frame'
#TAG = 'axis2_1_3'

# Angular restrictions.
THETA_X = pi / 4
THETA_Y = 3 * pi / 8
THETA_Z = pi / 6
INC = 18
VAR = 'X'

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
    EIG_FRAME[:, 0] = vect_x
    EIG_FRAME[:, 1] = vect_y
    EIG_FRAME[:, 2] = vect_z



class Frame_order:
    def __init__(self):
        """Calculate the frame order at infinity.

        This is when the starting positions are random.
        """

        # The file name.
        file_name = '_%s_%s_theta_%s_ens%s.agr' % (MODEL, TAG, lower(VAR), SAMPLE_SIZE)

        # Set the initial storage structures.
        self.init_storage()

        # Init.
        index = 0
        self.torsion_check = True

        # Pre-transpose the eigenframe for speed.
        self.eig_frame_T = transpose(EIG_FRAME)

        # Generate the angle data structures.
        self.angles = []
        self.angles_deg = []
        for i in range(INC):
            # The angle of one increment.
            inc_angle = pi / INC

            # The angle of the increment.
            self.angles.append(inc_angle * (i+1))

            # In degrees for the graphs.
            self.angles_deg.append(self.angles[-1] / (2.0*pi) * 360.0)

        # Alias the bound checking methods.
        if MODEL == 'rotor':
            self.inside = self.inside_rotor
            self.rotation = self.rotation_z_axis
        elif MODEL == 'free_rotor':
            self.inside = self.inside_free_rotor
            self.rotation = self.rotation_z_axis
        elif MODEL == 'iso_cone':
            self.inside = self.inside_iso_cone
            self.rotation = self.rotation_hypersphere
        elif MODEL == 'iso_cone_torsionless':
            self.inside = self.inside_iso_cone
            self.rotation = self.rotation_hypersphere_torsionless
        elif MODEL == 'iso_cone_free_rotor':
            self.inside = self.inside_iso_cone
            self.rotation = self.rotation_hypersphere
            self.torsion_check = False
        elif MODEL == 'pseudo-ellipse':
            self.inside = self.inside_pseudo_ellipse
            self.rotation = self.rotation_hypersphere
        elif MODEL == 'pseudo-ellipse_torsionless':
            self.inside = self.inside_pseudo_ellipse
            self.rotation = self.rotation_hypersphere_torsionless
        elif MODEL == 'pseudo-ellipse_free_rotor':
            self.inside = self.inside_pseudo_ellipse
            self.rotation = self.rotation_hypersphere
            self.torsion_check = False
        elif MODEL == 'double_rotor':
            self.inside = self.inside_double_rotor
            self.rotation = self.rotation_double_xy_axes
        else:
            raise RelaxError("Unknown model '%s'." % MODEL)

        # Loop over random starting positions.
        while True:
            # Printout.
            progress_meter(index, a=1000, b=100000)

            # Generate the random rotation.
            theta, phi, sigma = self.rotation()

            # Pre-calculate the R Kronecker outer product for speed.
            Rx2 = kron_prod(self.rot, self.rot)

            # Loop over the angle incs.
            for i in range(INC):
                # The new limits.
                max_theta_x, max_theta_y, max_theta_z = self.limits(i)

                # Inside the cone.
                if not self.full[i] and self.inside(i=i, theta=theta, phi=phi, sigma=sigma, max_theta_x=max_theta_x, max_theta_y=max_theta_y, max_theta_z=max_theta_z):

                    # Sum of rotations and cross products.
                    self.first_frame_order[i] += self.rot
                    self.second_frame_order[i] += Rx2

                    # Increment the counter.
                    self.count[i] += 1

                    # Full.
                    if self.count[i] == SAMPLE_SIZE:
                        sys.stdout.write("\b"*100 + "The angle restriction of %s deg is complete.\n" % self.angles_deg[i])
                        self.full[i] = 1

            # Increment the global index.
            index += 1

            # Break out.
            if sum(self.full) == INC:
                break

        # Average.
        self.first_frame_order = self.first_frame_order / float(SAMPLE_SIZE)
        self.second_frame_order = self.second_frame_order / float(SAMPLE_SIZE)

        # Write the data.
        self.write_data(file_name=file_name)

        # Final printout.
        sys.stdout.write("Random rotations required: %i\n\n" % index)


    def init_storage(self):
        """Initialise the storage structures."""

        # Create the average rotation matrix (first order).
        self.first_frame_order = zeros((INC, 3, 3), float64)

        # Create the frame order matrix (each element is ensemble averaged and corresponds to a different time step).
        self.second_frame_order = zeros((INC, 9, 9), float64)

        # Init the rotation matrix.
        self.rot = zeros((3, 3), float64)
        self.rot2 = zeros((3, 3), float64)

        # Some data arrays.
        self.full = zeros(INC)
        self.count = zeros(INC)

        # Axes.
        self.x_axis = array([1, 0, 0], float64)
        self.y_axis = array([0, 1, 0], float64)
        self.z_axis = array([0, 0, 1], float64)


    def inside_double_rotor(self, i=None, theta=None, phi=None, sigma=None, max_theta_x=None, max_theta_y=None, max_theta_z=None):
        """Determine if the frame is inside the limits."""

        # Alias the angles.
        sigma1, sigma2 = theta, phi

        # Check for torsion angle violations.
        if sigma1 < -max_theta_y or sigma1 > max_theta_y:
            return False
        if sigma2 < -max_theta_x or sigma2 > max_theta_x:
            return False

        # Inside.
        return True


    def inside_free_rotor(self, i=None, theta=None, phi=None, sigma=None, max_theta_x=None, max_theta_y=None, max_theta_z=None):
        """Determine if the frame is inside the limits, which for the free rotor is always true."""

        # Inside.
        return True


    def inside_iso_cone(self, i=None, theta=None, phi=None, sigma=None, max_theta_x=None, max_theta_y=None, max_theta_z=None):
        """Determine if the frame is inside the limits."""

        # Check for a torsion angle violation.
        if self.torsion_check and (sigma < -max_theta_z or sigma > max_theta_z):
            return False

        # Check for a tilt angle violation.
        if theta > max_theta_x:
            return False

        # Inside.
        return True


    def inside_pseudo_ellipse(self, i=None, theta=None, phi=None, sigma=None, max_theta_x=None, max_theta_y=None, max_theta_z=None):
        """Determine if the frame is inside the limits."""

        # Check for a torsion angle violation.
        if self.torsion_check and (sigma < -max_theta_z or sigma > max_theta_z):
            return False

        # Check for a tilt angle violation.
        max_theta = 1.0 / sqrt(cos(phi)**2 / max_theta_x**2 + sin(phi)**2 / max_theta_y**2)
        if theta > max_theta:
            return False

        # Inside.
        return True


    def inside_rotor(self, i=None, theta=None, phi=None, sigma=None, max_theta_x=None, max_theta_y=None, max_theta_z=None):
        """Determine if the frame is inside the limits."""

        # Check for a torsion angle violation.
        if sigma < -max_theta_z or sigma > max_theta_z:
            return False

        # Inside.
        return True


    def limits(self, i):
        """Determine the angular restrictions for the increment i."""

        # Alias the angle for the increment.
        theta = self.angles[i]

        # The different angles to vary.
        if VAR == 'X':
            return theta, THETA_Y, THETA_Z
        elif VAR == 'Y':
            return THETA_X, theta, THETA_Z
        elif VAR == 'Z':
            return THETA_X, THETA_Y, theta


    def rotation_double_xy_axes(self):
        """Random double rotation around the x- and y-axes and return of torsion-tilt angles"""

        # First a random angle between -pi and pi for the y-axis.
        sigma1 = uniform(-pi, pi)
        axis_angle_to_R(self.y_axis, sigma1, self.rot)

        # Second a random angle between -pi and pi for the x-axis.
        sigma2 = uniform(-pi, pi)
        axis_angle_to_R(self.x_axis, sigma2, self.rot2)

        # Construct the frame.
        frame = dot(self.rot2, self.rot)

        # Rotate the frame.
        self.rot = dot(EIG_FRAME, dot(frame, self.eig_frame_T))

        # Return the two torsion angles, and zero.
        return sigma1, sigma2, 0.0


    def rotation_hypersphere(self):
        """Random rotation using 4D hypersphere point picking and return of torsion-tilt angles."""

        # Generate a random rotation.
        R_random_hypersphere(self.rot)

        # Rotate the frame.
        frame = dot(self.eig_frame_T, dot(self.rot, EIG_FRAME))

        # Decompose the frame into the zyz Euler angles.
        alpha, beta, gamma = R_to_euler_zyz(frame)

        # Convert to tilt and torsion angles (properly wrapped) and return them.
        theta = beta
        phi = wrap_angles(gamma, -pi, pi)
        sigma = wrap_angles(alpha + gamma, -pi, pi)
        return theta, phi, sigma


    def rotation_hypersphere_torsionless(self):
        """Random rotation using 4D hypersphere point picking and return of torsion-tilt angles."""

        # Obtain the random torsion-tilt angles from the random hypersphere method.
        theta, phi, sigma = self.rotation_hypersphere()

        # Reconstruct a rotation matrix, setting the torsion angle to zero.
        tilt_torsion_to_R(phi, theta, 0.0, self.rot)

        # Rotate the frame.
        self.rot = dot(EIG_FRAME, dot(self.rot, self.eig_frame_T))

        # Return the angles.
        return theta, phi, 0.0


    def rotation_z_axis(self):
        """Random rotation around the z-axis and return of torsion-tilt angles"""

        # Random angle between -pi and pi.
        angle = uniform(-pi, pi)

        # Generate the rotation matrix.
        axis_angle_to_R(self.z_axis, angle, self.rot)

        # Decompose the rotation into the zyz Euler angles.
        alpha, beta, gamma = R_to_euler_zyz(self.rot)

        # Rotate the frame.
        self.rot = dot(EIG_FRAME, dot(self.rot, self.eig_frame_T))

        # Convert to tilt and torsion angles (properly wrapped) and return them.
        theta = beta
        phi = wrap_angles(gamma, -pi, pi)
        sigma = wrap_angles(alpha + gamma, -pi, pi)
        return theta, phi, sigma


    def write_data(self, file_name=None):
        """Dump the data to files.

        @keyword file_name:     The end part of the files to create.  This will be prepended by either 'Sij' or 'Sijkl'.
        @type file_name:        str
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
            file.write("@    title \"Simulated frame order matrix elements\"\n")
            if i == 0:
                file.write("@    subtitle \"%s, 1\\Sst\\N degree matrix, %i simulations\"\n" % (MODEL_TEXT, SAMPLE_SIZE))
            else:
                file.write("@    subtitle \"%s, 2\\Snd\\N degree matrix, %i simulations\"\n" % (MODEL_TEXT, SAMPLE_SIZE))

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

        # Header for first order matrix.
        graph_num = 0
        for i in range(3):
            for j in range(3):
                file_1st.write("@    s%i legend \"\\q<c\\s%s%s\\N>\"\n" % (graph_num, i+1, j+1))
                file_1st.write("@    s%i linewidth 0.5\n" % graph_num)
                graph_num += 1

        # Header for second order matrix.
        graph_num = 0
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        file_2nd.write("@    s%i legend \"<\\qc\\s%s%s\\N.c\\s%s%s\\N>\"\n" % (graph_num, i+1, j+1, k+1, l+1))
                        file_2nd.write("@    s%i linewidth 0.5\n" % graph_num)
                        graph_num += 1

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
                    file_1st.write("%s %s\n" % (self.angles_deg[k], self.first_frame_order[k, i, j]))

                # Footer.
                file_1st.write("&\n")

                # Inc.
                graph_num += 1

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
                    file_2nd.write('%s %s\n' % (self.angles_deg[k], self.second_frame_order[k, i, j]))

                # Footer.
                file_2nd.write('&\n')

                # Inc.
                graph_num += 1

        # No autoscaling.
        file_1st.write("@autoscale onread none\n")
        file_2nd.write("@autoscale onread none\n")

        # Close the files.
        file_1st.close()
        file_2nd.close()


# Calculate the frame order.
Frame_order()
