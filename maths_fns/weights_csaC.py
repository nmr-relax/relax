###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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

from math import sqrt
from Numeric import outerproduct


##########
# Sphere #
##########


# Sphere weight.
################

def calc_csaC_sphere_ci(data, diff_data):
    """Weight for spherical diffusion.

    c0_csaC = 1/2 (3*(dx_csa1.dx_csa2 + dy_csa1.dy_csa2 + dz_csa1.dz_csa2) - 1 )
    """

    data.ci_csaC[0] = 0.5 * ( 3.0 * (data.dx_csa1 * data.dx_csa2 + data.dy_csa1 * data.dy_csa2 + data.dz_csa1 * data.dz_csa2 ) - 1.0 )




############
# Spheroid #
############


# Spheroid weights.
###################

def calc_csaC_spheroid_ci(data, diff_data):
    """Weights for spheroidal diffusion.

    The equations are

        c-1_csaC = 1/4 (3dz_csa1**2 - 1).(3dz_csa2**2 - 1),

        c0_csaC  = 3 (dx_csa1.dx_csa2 + dy_csa1.dy_csa2).dz_csa1.dz_csa2,

        c1_csaC  = 3/4 [(dx_csa1.dx_csa2 + dy_csa1.dy_csa2)**2 - (dx_csa1.dy_csa2 - dy_csa1.dx_csa2)**2]

    where dz_csaC is the direction cosine of the unit csa eigenvector along the z-axis of the diffusion
    tensor which is calculated as the dot product of the unit eigenvector with a unit vector along
    Dpar.
    """

    # Weights.
    data.ci_csaC[0] = 0.25 * (3.0 * data.dz_csa1**2 - 1.0) * (3.0 * data.dz_csa2**2 - 1.0)
    data.ci_csaC[1] = 3.0 * (data.dx_csa1 * data.dx_csa2 + data.dy_csa1 * data.dy_csa2) * data.dz_csa1 * data.dz_csa2
    data.ci_csaC[2] = 0.75 *((data.dx_csa1 * data.dx_csa2 + data.dy_csa1 * data.dy_csa2)**2 - (data.dx_csa1 * data.dy_csa2 - data.dy_csa1 * data.dx_csa2)**2) 



# Spheroid weight gradient.
###########################

def calc_csaC_spheroid_dci(data, diff_data):
    """Weight gradient for spheroidal diffusion.

    The equations are
 
        dc-1_csaC       /                            ddz_csa1                              ddz_csa2 \
        --------- = 1/4 | 6dz_csa1 (3dz_csa2**2 - 1) -------- + 6dz_csa2 (3dz_csa1**2 - 1) -------- | ,
          dOi           \                              dOi                                   dOi    /

        dc0_csaC      /  dx_csa1             dx_csa2             dy_csa1             dy_csa2          \
        --------  = 3 | --------  dx_csa2 + --------  dx_csa1 + --------  dy_csa2 + --------  dy_csa1 | dz_csa1 dz_csa2 +
          dOi         \   dOi                 dOi                 dOi                 dOi             /

                                                          /  dz_csa1             dz_csa2          \
                  + 3 (dx_csa1.dx_csa2 + dy_csa1.dy_csa2) | --------  dz_csa2 + --------  dz_csa1 |
                                                          \   dOi                 dOi             / 




        dc1_csaC       /                                      /        ddy_csa2   ddy_csa1                   ddx_csa2   ddx_csa1         
        -------- = 3/4 |2 (dy_csa1 dy_csa2 + dx_csa1 dx_csa2) |dy_csa1 -------- + -------- dy_csa2 + dx_csa1 -------- + -------- dx_csa2)
          dOi          \                                      \          dOi        dOi                        dOi        dOi            


                                                            /        ddy_csa2   ddx_csa1                   ddy_csa1   ddx_csa2        \\
                    - 2 (dx_csa1 dy_csa2 - dx_csa2 dy_csa1) |dx_csa1 -------- + -------- dy_csa2 - dx_csa2 -------- - -------- dy_csa1||
                                                            \          dOi        dOi                        dOi        dOi           //



  	    
    where the orientation parameter set O is {theta, phi}.
    """

    # Components.
    data.dci_csaC[2:, 0] = 1.5 * (3 * data.dz_csa1**2-1) * data.dz_csa2 * data.ddz_csa2_dO+1.5 * data.dz_csa1 * (3 * data.dz_csa2**2-1) * data.ddz_csa1_dO
    data.dci_csaC[2:, 1] = 3.0 * (data.dy_csa1 * data.dy_csa2+data.dx_csa1 * data.dx_csa2) * data.dz_csa1 * data.ddz_csa2_dO+3.0 * (data.dy_csa1 * data.dy_csa2+data.dx_csa1 * data.dx_csa2) * data.dz_csa2 * data.ddz_csa1_dO+3.0 * data.dz_csa1 * data.dz_csa2 * (data.dy_csa1 * data.ddy_csa2_dO+data.dy_csa2 * data.ddy_csa1_dO+data.dx_csa1 * data.ddx_csa2_dO+data.dx_csa2 * data.ddx_csa1_dO)
    data.dci_csaC[2:, 2] = 0.75 * (2 * (data.dy_csa1 * data.dy_csa2+data.dx_csa1 * data.dx_csa2) * (data.dy_csa1 * data.ddy_csa2_dO+data.dy_csa2 * data.ddy_csa1_dO+data.dx_csa1 * data.ddx_csa2_dO+data.dx_csa2 * data.ddx_csa1_dO)-2 * (data.dx_csa1 * data.dy_csa2-data.dx_csa2 * data.dy_csa1) * (data.dx_csa1 * data.ddy_csa2_dO-data.dx_csa2 * data.ddy_csa1_dO-data.dy_csa1 * data.ddx_csa2_dO+data.dy_csa2 * data.ddx_csa1_dO))




# Spheroid weight Hessian.
##########################

def calc_csaC_spheroid_d2ci(data, diff_data):
    """Weight Hessian for spheroidal diffusion.

    The equations are

																      2
	 d2c-1_csaC     	      2	     ddz_csa2 ddz_csa2		     ddz_csa1	      ddz_csa2		      2		     d dz_csa2
	------------  = 1.5 (3 dz_csa1  - 1) -------- -------- + 9.0 dz_csa1 -------- dz_csa2 -------- + 1.5 (3 dz_csa1  - 1) dz_csa2 ---------
	  dOi.dOj       		       dOi      dOj		       dOi	        dOj				      dOi dOj

																     2
					   ddz_csa1	    ddz_csa2	   ddz_csa1 ddz_csa1	       2		    d dz_csa1	        2
			     + 9.0 dz_csa1 -------- dz_csa2 -------- + 1.5 -------- -------- (3 dz_csa2  - 1) + 1.5 dz_csa1 --------- (3 dz_csa2  - 1)
					     dOj	      dOi	     dOi      dOj				     dOi dOj







	 
         d2c0_csaC					     ddz_csa1 ddz_csa2
       ----------- = 3.0 (dy_csa1 dy_csa2 + dx_csa1 dx_csa2) -------- -------- + 3.0
	 dOi dOj					       dOi      dOj
		
																		 2
			  ddy_csa2   ddy_csa1		        ddx_csa2   ddx_csa1		     ddz_csa2						        d dz_csa2
		 (dy_csa1 -------- + -------- dy_csa2 + dx_csa1 -------- + -------- dx_csa2) dz_csa1 -------- + 3.0 (dy_csa1 dy_csa2 + dx_csa1 dx_csa2) dz_csa1 ---------
			    dOi	       dOi			  dOi	     dOi		       dOj							 dOi dOj
		
							   ddz_csa1 ddz_csa2		    ddy_csa2   ddy_csa1			  ddx_csa2   ddx_csa1
		 + 3.0 (dy_csa1 dy_csa2 + dx_csa1 dx_csa2) -------- -------- + 3.0 (dy_csa1 -------- + -------- dy_csa2 + dx_csa1 -------- + -------- dx_csa2) dz_csa1
							     dOj      dOi		      dOj	 dOj			    dOj	       dOj
		
		 ddz_csa2		 ddy_csa2   ddy_csa1		       ddx_csa2	  ddx_csa1	    ddz_csa1
		 -------- + 3.0 (dy_csa1 -------- + -------- dy_csa2 + dx_csa1 -------- + -------- dx_csa2) -------- dz_csa2
		   dOi			   dOi	      dOi			 dOi	    dOi		      dOj
		
							    2
							   d dz_csa1			    ddy_csa2   ddy_csa1			  ddx_csa2   ddx_csa1	       ddz_csa1
		 + 3.0 (dy_csa1 dy_csa2 + dx_csa1 dx_csa2) --------- dz_csa2 + 3.0 (dy_csa1 -------- + -------- dy_csa2 + dx_csa1 -------- + -------- dx_csa2) --------
							    dOi dOj			      dOj	 dOj			    dOj	       dOj		 dOi
		
							     2				     2						     2
				ddy_csa1 ddy_csa2	    d dy_csa2   ddy_csa1 ddy_csa2   d dy_csa1	        ddx_csa1 ddx_csa2	    d dx_csa2   ddx_csa1 ddx_csa2
		 dz_csa2 + 3.0 (-------- -------- + dy_csa1 --------- + -------- -------- + --------- dy_csa2 + -------- -------- + dx_csa1 --------- + -------- --------
				  dOi	   dOj		     dOi dOj	  dOj	   dOi	     dOi dOj		  dOi	   dOj		     dOi dOj	  dOj	   dOi
		
		    2
		   d dx_csa1
		 + --------- dx_csa2) dz_csa1 dz_csa2
		    dOi dOj



        2                                                                                      2                               2
       d d2c1_csaC                                                ddy_csa1 ddy_csa2           d dy_csa2   ddy_csa1 ddy_csa2   d dy_csa1
       ----------- = 0.75 (2 (dy_csa1 dy_csa2 + dx_csa1 dx_csa2) (-------- -------- + dy_csa1 --------- + -------- -------- + --------- dy_csa2
         dOi dOj                                                    dOi      dOj               dOi dOj      dOj      dOi       dOi dOj
		
		                                2                               2
		   ddx_csa1 ddx_csa2           d dx_csa2   ddx_csa1 ddx_csa2   d dx_csa1
		 + -------- -------- + dx_csa1 --------- + -------- -------- + --------- dx_csa2)
		     dOi      dOj               dOi dOj      dOj      dOi       dOi dOj
		
		              ddy_csa2   ddy_csa1                   ddx_csa2   ddx_csa1                   ddy_csa2   ddy_csa1                   ddx_csa2   ddx_csa1
		 + 2 (dy_csa1 -------- + -------- dy_csa2 + dx_csa1 -------- + -------- dx_csa2) (dy_csa1 -------- + -------- dy_csa2 + dx_csa1 -------- + -------- dx_csa2)
		                dOi        dOi                        dOi        dOi                        dOj        dOj                        dOj        dOj
		
		                                                                       2                               2
		                                          ddx_csa1 ddy_csa2           d dy_csa2   ddx_csa1 ddy_csa2   d dx_csa1           ddx_csa2 ddy_csa1
		 - 2 (dx_csa1 dy_csa2 - dx_csa2 dy_csa1) (-------- -------- + dx_csa1 --------- + -------- -------- + --------- dy_csa2 - -------- --------
		                                            dOi      dOj               dOi dOj      dOj      dOi       dOi dOj              dOi      dOj
		
		            2                               2
		           d dy_csa1   ddx_csa2 ddy_csa1   d dx_csa2                       ddy_csa2   ddx_csa1                   ddy_csa1   ddx_csa2
		 - dx_csa2 --------- - -------- -------- - --------- dy_csa1) - 2 (dx_csa1 -------- + -------- dy_csa2 - dx_csa2 -------- - -------- dy_csa1)
		            dOi dOj      dOj      dOi       dOi dOj                          dOi        dOi                        dOi        dOi
		
		          ddy_csa2   ddx_csa1                   ddy_csa1   ddx_csa2
		 (dx_csa1 -------- + -------- dy_csa2 - dx_csa2 -------- - -------- dy_csa1))
		            dOj        dOj                        dOj        dOj



    where the orientation parameter set O is {theta, phi}.
    """

    # Outer product.
    op_z1z1_csaC = outerproduct(data.ddz_csa1_dO, data.ddz_csa1_dO)
    op_z1z2_csaC = outerproduct(data.ddz_csa1_dO, data.ddz_csa2_dO)
    op_z2z1_csaC = outerproduct(data.ddz_csa2_dO, data.ddz_csa1_dO)
    op_z2z2_csaC = outerproduct(data.ddz_csa2_dO, data.ddz_csa2_dO)
    op_x1x1_csaC = outerproduct(data.ddx_csa1_dO, data.ddx_csa1_dO)
    op_x1x2_csaC = outerproduct(data.ddx_csa1_dO, data.ddx_csa2_dO)
    op_x2x1_csaC = outerproduct(data.ddx_csa2_dO, data.ddx_csa1_dO)
    op_x2x2_csaC = outerproduct(data.ddx_csa2_dO, data.ddx_csa2_dO)
    op_y1y1_csaC = outerproduct(data.ddy_csa1_dO, data.ddy_csa1_dO)
    op_y1y2_csaC = outerproduct(data.ddy_csa1_dO, data.ddy_csa2_dO)
    op_y2y1_csaC = outerproduct(data.ddy_csa2_dO, data.ddy_csa1_dO)
    op_y2y2_csaC = outerproduct(data.ddy_csa2_dO, data.ddy_csa2_dO)
    #
    op_z1x1_csaC = outerproduct(data.ddz_csa1_dO, data.ddx_csa1_dO)
    op_x1z1_csaC = outerproduct(data.ddx_csa1_dO, data.ddz_csa1_dO)
    op_z1y1_csaC = outerproduct(data.ddz_csa1_dO, data.ddy_csa1_dO)
    op_y1z1_csaC = outerproduct(data.ddy_csa1_dO, data.ddz_csa1_dO)
    op_z1x2_csaC = outerproduct(data.ddz_csa1_dO, data.ddx_csa2_dO)
    op_x2z1_csaC = outerproduct(data.ddx_csa2_dO, data.ddz_csa1_dO)
    op_z1y2_csaC = outerproduct(data.ddz_csa1_dO, data.ddy_csa2_dO)
    op_y2z1_csaC = outerproduct(data.ddy_csa2_dO, data.ddz_csa1_dO)
    op_z2x1_csaC = outerproduct(data.ddz_csa2_dO, data.ddx_csa1_dO)
    op_x1z2_csaC = outerproduct(data.ddx_csa1_dO, data.ddz_csa2_dO)
    op_z2y1_csaC = outerproduct(data.ddz_csa2_dO, data.ddy_csa1_dO)
    op_y1z2_csaC = outerproduct(data.ddy_csa1_dO, data.ddz_csa2_dO)
    op_z2x2_csaC = outerproduct(data.ddz_csa2_dO, data.ddx_csa2_dO)
    op_x2z2_csaC = outerproduct(data.ddx_csa2_dO, data.ddz_csa2_dO)
    op_z2y2_csaC = outerproduct(data.ddz_csa2_dO, data.ddy_csa2_dO)
    op_y2z2_csaC = outerproduct(data.ddy_csa2_dO, data.ddz_csa2_dO)
    #
    op_x1y1_csaC = outerproduct(data.ddx_csa1_dO, data.ddy_csa1_dO)
    op_y1x1_csaC = outerproduct(data.ddy_csa1_dO, data.ddx_csa1_dO)
    op_x1y2_csaC = outerproduct(data.ddx_csa1_dO, data.ddy_csa2_dO)
    op_y2x1_csaC = outerproduct(data.ddy_csa2_dO, data.ddx_csa1_dO)
    op_x2y1_csaC = outerproduct(data.ddx_csa2_dO, data.ddy_csa1_dO)
    op_y1x2_csaC = outerproduct(data.ddy_csa1_dO, data.ddx_csa2_dO)
    op_x2y2_csaC = outerproduct(data.ddx_csa2_dO, data.ddy_csa2_dO)
    op_y2x2_csaC = outerproduct(data.ddy_csa2_dO, data.ddx_csa2_dO)
    

    # Hessian.
    data.d2ci_csaC[2:, 2:, 0] = 1.5 * (3.0 * data.dz_csa1**2-1.0) * data.dz_csa2 * data.d2dz_csa2_dO2+1.5 * data.dz_csa1 * (3.0 * data.dz_csa2**2-1.0) * data.d2dz_csa1_dO2+1.5 * op_z1z1_csaC * (3.0 * data.dz_csa2**2-1.0)+9.0 * op_z1z2_csaC * data.dz_csa1 * data.dz_csa2+9.0 * op_z2z1_csaC * data.dz_csa1 * data.dz_csa2+1.5 * op_z2z2_csaC * (3.0 * data.dz_csa1**2-1.0)

    data.d2ci_csaC[2:, 2:, 1] = 3.0 * data.dy_csa1 * data.dy_csa2 * data.dz_csa1 * data.d2dz_csa2_dO2+3.0 * data.dx_csa1 * data.dx_csa2 * data.dz_csa1 * data.d2dz_csa2_dO2+3.0 * data.dy_csa1 * data.dy_csa2 * data.dz_csa2 * data.d2dz_csa1_dO2+3.0 * data.dx_csa1 * data.dx_csa2 * data.dz_csa2 * data.d2dz_csa1_dO2+3.0 * data.dy_csa1 * data.dz_csa1 * data.dz_csa2 * data.d2dy_csa2_dO2+3.0 * data.dy_csa2 * data.dz_csa1 * data.dz_csa2 * data.d2dy_csa1_dO2+3.0 * data.dx_csa1 * data.dz_csa1 * data.dz_csa2 * data.d2dx_csa2_dO2+3.0 * data.dx_csa2 * data.dz_csa1 * data.dz_csa2 * data.d2dx_csa1_dO2+3.0 * op_y1y2_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_y2y1_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_x1x2_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_x2x1_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_y1z1_csaC * data.dy_csa2 * data.dz_csa2+3.0 * op_z1y1_csaC * data.dy_csa2 * data.dz_csa2+3.0 * op_y2z1_csaC * data.dy_csa1 * data.dz_csa2+3.0 * op_z1y2_csaC * data.dy_csa1 * data.dz_csa2+3.0 * op_x1z1_csaC * data.dx_csa2 * data.dz_csa2+3.0 * op_z1x1_csaC * data.dx_csa2 * data.dz_csa2+3.0 * op_x2z1_csaC * data.dx_csa1 * data.dz_csa2+3.0 * op_z1x2_csaC * data.dx_csa1 * data.dz_csa2+3.0 * op_y1z2_csaC * data.dy_csa2 * data.dz_csa1+3.0 * op_z2y1_csaC * data.dy_csa2 * data.dz_csa1+3.0 * op_y2z2_csaC * data.dy_csa1 * data.dz_csa1+3.0 * op_z2y2_csaC * data.dy_csa1 * data.dz_csa1+3.0 * op_x1z2_csaC * data.dx_csa2 * data.dz_csa1+3.0 * op_z2x1_csaC * data.dx_csa2 * data.dz_csa1+3.0 * op_x2z2_csaC * data.dx_csa1 * data.dz_csa1+3.0 * op_z2x2_csaC * data.dx_csa1 * data.dz_csa1+3.0 * op_z1z2_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_z2z1_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_z1z2_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_z2z1_csaC * data.dx_csa1 * data.dx_csa2

    data.d2ci_csaC[2:, 2:, 2] = 1.5 * data.dy_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2-1.5 * data.dx_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2+3.0 * data.dx_csa1 * data.dx_csa2 * data.dy_csa1 * data.d2dy_csa2_dO2+1.5 * data.dy_csa1 * data.dy_csa2**2 * data.d2dy_csa1_dO2+3.0 * data.dx_csa1 * data.dx_csa2 * data.dy_csa2 * data.d2dy_csa1_dO2-1.5 * data.dx_csa2**2 * data.dy_csa1 * data.d2dy_csa1_dO2+3.0 * data.dx_csa1 * data.dy_csa1 * data.dy_csa2 * data.d2dx_csa2_dO2-1.5 * data.dx_csa2 * data.dy_csa1**2 * data.d2dx_csa2_dO2+1.5 * data.dx_csa1**2 * data.dx_csa2 * data.d2dx_csa2_dO2-1.5 * data.dx_csa1 * data.dy_csa2**2 * data.d2dx_csa1_dO2+3.0 * data.dx_csa2 * data.dy_csa1 * data.dy_csa2 * data.d2dx_csa1_dO2+1.5 * data.dx_csa1 * data.dx_csa2**2 * data.d2dx_csa1_dO2+1.5 * op_y1y1_csaC * data.dy_csa2**2-1.5 * op_x1x1_csaC * data.dy_csa2**2+3.0 * op_y1y2_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_y2y1_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_x1x2_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_x2x1_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_x1y1_csaC * data.dx_csa2 * data.dy_csa2+3.0 * op_y1x1_csaC * data.dx_csa2 * data.dy_csa2-3.0 * op_x1y2_csaC * data.dx_csa1 * data.dy_csa2+3.0 * op_x2y1_csaC * data.dx_csa1 * data.dy_csa2+3.0 * op_y1x2_csaC * data.dx_csa1 * data.dy_csa2-3.0 * op_y2x1_csaC * data.dx_csa1 * data.dy_csa2+1.5 * op_y2y2_csaC * data.dy_csa1**2-1.5 * op_x2x2_csaC * data.dy_csa1**2+3.0 * op_x1y2_csaC * data.dx_csa2 * data.dy_csa1-3.0 * op_x2y1_csaC * data.dx_csa2 * data.dy_csa1-3.0 * op_y1x2_csaC * data.dx_csa2 * data.dy_csa1+3.0 * op_y2x1_csaC * data.dx_csa2 * data.dy_csa1+3.0 * op_x2y2_csaC * data.dx_csa1 * data.dy_csa1+3.0 * op_y2x2_csaC * data.dx_csa1 * data.dy_csa1-1.5 * op_y1y1_csaC * data.dx_csa2**2+1.5 * op_x1x1_csaC * data.dx_csa2**2+3.0 * op_y1y2_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_y2y1_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_x1x2_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_x2x1_csaC * data.dx_csa1 * data.dx_csa2-1.5 * op_y2y2_csaC * data.dx_csa1**2+1.5 * op_x2x2_csaC * data.dx_csa1**2





#############
# Ellipsoid #
#############


# Ellipsoid weights.
####################



def calc_csaC_ellipsoid_ci(data, diff_data):
    """Weight equations for ellipsoidal diffusion.

    The equations are
                                                  ___
        c2_csaC = 1/4 (d_csaC+e_csaC * cobeta + V 3  * f_csaC * sibeta),

        c-1_csaC = 3dy_csa1.dy_csa2.dz_csa1.dz_csa2,

        c0_csaC  = 3dx_csa1.dx_csa2.dz_csa1.dz_csa2,
        
	c1_csaC  = 3dx_csa1.dx_csa2.dy_csa1.dy_csa2,
                                                  ___   
        c-2_csaC  = 1/4 (d_csaC-e_csaC * cobeta - V 3  * f_csaC * sibeta),

    where
	d_csaC = 3 * (dx_csa1**2 * dx_csa2**2+dy_csa1**2 * dy_csa2**2+dz_csa1**2 * dz_csa2**2) - 1,
	e_csaC = 1-3 * (dz_csa1**2 * dz_csa2**2+dx_csa1**2 * dy_csa2**2+dy_csa1**2 * dx_csa2**2),
	f_csaC = 3 * dy_csa1**2 * dy_csa2**2-3 * dx_csa1**2 * dx_csa2**2-dy_csa1**2-dy_csa2**2+dx_csa1**2+dx_csa2**2 ,


    and where the factors cobeta and sibeta are defined as

                  /               2         \ -1
                  |    3 (Dx - Dy)          | ---              1          
        cobeta =  |   ----------------- + 1 |  2     =  ----------------
                  |           Dy + Dx 2     |                     2
                  |   4 (Dz - -------)      |           SQRT( 3 Dr  + 1)
                  \              2          /


                  /               2            \ -1        ___
                  |    3 (Dx - Dy)             | ---      V 3  (Dx - Dy)         - SQRT(3) Dr   
        sibeta =  |   -------------------- + 1 |  2     -----------------   =   ----------------
                  |     /     Dy + Dx \ 2      |     *           Dy + Dx                 2       
                  |   4 |Dz - ------- |        |         2 (Dz - -------)       SQRT(3 Dr  + 1)  
                  \     \        2    /        /                    2    

    
    dx_csaC, dy_csaC, and dz_csaC are the direction cosines of the csa eigenvectors along the x, y, and z-axes of the
    diffusion tensor, calculated as the dot product of the unit csa eigenvector and the unit vectors
    along Dx, Dy, and Dz respectively.
    """



    cobeta = 1.0/sqrt(3.0 * diff_data.params[2]**2 + 1.0)
    sibeta = -sqrt(3.0) * diff_data.params[2]/sqrt(3.0 * diff_data.params[2]**2 + 1.0)
    
    d_csaC = 3.0 * (data.dx_csa1**2 * data.dx_csa2**2+data.dy_csa1**2 * data.dy_csa2**2+data.dz_csa1**2 * data.dz_csa2**2)-1.0
    e_csaC = 1.0-3.0 * (data.dz_csa1**2 * data.dz_csa2**2+data.dx_csa1**2 * data.dy_csa2**2+data.dy_csa1**2 * data.dx_csa2**2)
    f_csaC = 3.0 * data.dy_csa1**2 * data.dy_csa2**2-3.0 * data.dx_csa1**2.0 * data.dx_csa2**2-data.dy_csa1**2-data.dy_csa2**2+data.dx_csa1**2+data.dx_csa2**2

    data.ci_csaC[4] = 0.25 * (d_csaC+e_csaC * cobeta+sqrt(3.0) * f_csaC * sibeta)
    data.ci_csaC[1] = 3.0 * data.dy_csa1 * data.dy_csa2 * data.dz_csa1 * data.dz_csa2
    data.ci_csaC[2] = 3.0 * data.dx_csa1 * data.dx_csa2 * data.dz_csa1 * data.dz_csa2
    data.ci_csaC[3] = 3.0 * data.dx_csa1 * data.dx_csa2 * data.dy_csa1 * data.dy_csa2
    data.ci_csaC[0] = 0.25 * (d_csaC-e_csaC * cobeta-sqrt(3.0) * f_csaC * sibeta)
    

# Ellipsoid weight gradient.
############################

def calc_csaC_ellipsoid_dci(data, diff_data):
    """Weight gradient for ellipsoidal diffusion.

    Oi partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~


       dc2_csaC           ___           2         ddy_csa2             ddy_csa2             ddy_csa1        2             ddy_csa1
       -------- = 0.25 ( V 3  (6 dy_csa1  dy_csa2 -------- - 2 dy_csa2 -------- + 6 dy_csa1 -------- dy_csa2  - 2 dy_csa1 --------
         dOi                                        dOi                  dOi                  dOi                           dOi
		
		            2         ddx_csa2             ddx_csa2             ddx_csa1        2             ddx_csa1
		 - 6 dx_csa1  dx_csa2 -------- + 2 dx_csa2 -------- - 6 dx_csa1 -------- dx_csa2  + 2 dx_csa1 --------) sibeta
		                        dOi                  dOi                  dOi                           dOi
		
		               2         ddz_csa2             ddz_csa1        2            2         ddy_csa2             ddy_csa1        2            2         ddx_csa2
		 + 3 (2 dz_csa1  dz_csa2 -------- + 2 dz_csa1 -------- dz_csa2  + 2 dy_csa1  dy_csa2 -------- + 2 dy_csa1 -------- dy_csa2  + 2 dx_csa1  dx_csa2 --------
		                           dOi                  dOi                                    dOi                  dOi                                    dOi
		
		             ddx_csa1        2                       2         ddz_csa2             ddz_csa1        2            2         ddy_csa2
		 + 2 dx_csa1 -------- dx_csa2 ) - 3 cobeta (2 dz_csa1  dz_csa2 -------- + 2 dz_csa1 -------- dz_csa2  + 2 dx_csa1  dy_csa2 --------
		               dOi                                               dOi                  dOi                                    dOi
		
		             ddx_csa1        2            2         ddy_csa1             ddx_csa2        2
		 + 2 dx_csa1 -------- dy_csa2  + 2 dx_csa2  dy_csa1 -------- + 2 dx_csa2 -------- dy_csa1 ))
		               dOi                                    dOi                  dOi




       dc-1_csaC                             ddz_csa2                     ddz_csa1                     ddy_csa2
       --------- = 3 dy_csa1 dy_csa2 dz_csa1 -------- + 3 dy_csa1 dy_csa2 -------- dz_csa2 + 3 dy_csa1 -------- dz_csa1 dz_csa2
          dOi                                  dOi                          dOi                          dOi

                    ddy_csa1
                + 3 -------- dy_csa2 dz_csa1 dz_csa2
                      dOi




       dc0_csaC                             ddz_csa2                     ddz_csa1                     ddx_csa2
       -------- = 3 dx_csa1 dx_csa2 dz_csa1 -------- + 3 dx_csa1 dx_csa2 -------- dz_csa2 + 3 dx_csa1 -------- dz_csa1 dz_csa2
         dOi                                  dOi                          dOi                          dOi

                    ddx_csa1
                + 3 -------- dx_csa2 dz_csa1 dz_csa2
                      dOi



       dc1_csaC                             ddy_csa2                     ddy_csa1                     ddx_csa2
       -------- = 3 dx_csa1 dx_csa2 dy_csa1 -------- + 3 dx_csa1 dx_csa2 -------- dy_csa2 + 3 dx_csa1 -------- dy_csa1 dy_csa2
         dOi                                  dOi                          dOi                          dOi

                    ddx_csa1
                + 3 -------- dx_csa2 dy_csa1 dy_csa2
                      dOi






       dc-2_csaC            ___           2         ddy_csa2             ddy_csa2             ddy_csa1        2             ddy_csa1
       --------- = 0.25 (- V 3  (6 dy_csa1  dy_csa2 -------- - 2 dy_csa2 -------- + 6 dy_csa1 -------- dy_csa2  - 2 dy_csa1 --------
          dOi                                         dOi                  dOi                  dOi                           dOi
               
                           2         ddx_csa2             ddx_csa2             ddx_csa1        2             ddx_csa1
                - 6 dx_csa1  dx_csa2 -------- + 2 dx_csa2 -------- - 6 dx_csa1 -------- dx_csa2  + 2 dx_csa1 --------) sibeta
                        dOi                  dOi                  dOi                           dOi
               
                              2         ddz_csa2             ddz_csa1        2            2         ddy_csa2             ddy_csa1        2            2         ddx_csa2
                + 3 (2 dz_csa1  dz_csa2 -------- + 2 dz_csa1 -------- dz_csa2  + 2 dy_csa1  dy_csa2 -------- + 2 dy_csa1 -------- dy_csa2  + 2 dx_csa1  dx_csa2 --------
                                          dOi                  dOi                                    dOi                  dOi                                    dOi
               
                            ddx_csa1        2                       2         ddz_csa2             ddz_csa1        2            2         ddy_csa2
                + 2 dx_csa1 -------- dx_csa2 ) + 3 cobeta (2 dz_csa1  dz_csa2 -------- + 2 dz_csa1 -------- dz_csa2  + 2 dx_csa1  dy_csa2 --------
                              dOi                                               dOi                  dOi                                    dOi
               
                            ddx_csa1        2            2         ddy_csa1             ddx_csa2        2
                + 2 dx_csa1 -------- dy_csa2  + 2 dx_csa2  dy_csa1 -------- + 2 dx_csa2 -------- dy_csa1 ))
                              dOi                                    dOi                  dOi
      

               
    where
                  /               2         \ -1
                  |    3 (Dx - Dy)          | ---              1          
        cobeta =  |   ----------------- + 1 |  2     =  ----------------
                  |           Dy + Dx 2     |                     2
                  |   4 (Dz - -------)      |           SQRT( 3 Dr  + 1)
                  \              2          /


                  /               2            \ -1        ___
                  |    3 (Dx - Dy)             | ---      V 3  (Dx - Dy)         - SQRT(3) Dr   
        sibeta =  |   -------------------- + 1 |  2     -----------------   =   ----------------
                  |     /     Dy + Dx \ 2      |     *           Dy + Dx                 2       
                  |   4 |Dz - ------- |        |         2 (Dz - -------)       SQRT(3 Dr  + 1)  
                  \     \        2    /        /                    2    


   






    and where the orietation parameter set O is

        O = {alpha, beta, gamma}.


    tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_csaC
        ---------  =  0,
          dtm

        dc-1_csaC
        ---------  =  0,
          dtm

        dc0_csaC
        --------   =  0,
          dtm

        dc1_csaC
        --------   =  0,
          dtm

        dc2_csaC
        --------   =  0.
          dtm


    Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~

        dc-2_csaC
        ---------  =  0,
          dDa

        dc-1_csaC
        ---------  =  0,
          dDa

        dc0_csaC
        --------   =  0,
          dDa

        dc1_csaC
        --------   =  0,
          dDa

        dc2_csaC
        --------   =  0.
          dDa



    Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~


                                               2        2          2        2          2        2
       dcp2_csaC           3 Dr (1 - 3 (dz_csa1  dz_csa2  + dx_csa1  dy_csa2  + dx_csa2  dy_csa1 ))
       --------- = 0.25 (- ------------------------------------------------------------------------
          dDr                                                2     3/2
                                                        (3 Dr  + 1)
                     
                                    2        2          2          2            2        2          2          2
                        3 (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                      - -----------------------------------------------------------------------------------------
                                                                      2
                                                             SQRT(3 Dr  + 1)
                     
                            2           2        2          2          2            2        2          2          2
                        9 Dr  (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                      + ---------------------------------------------------------------------------------------------)
                                                                    2     3/2
                                                               (3 Dr  + 1)



        dc-1_csaC
        ---------  =  0,
          dDr

        dc0_csaC
        --------   =  0,
          dDr

        dc1_csaC
        --------   =  0,
          dDr

                                              2        2          2        2          2        2
        dcm2_csaC         3 Dr (1 - 3 (dz_csa1  dz_csa2  + dx_csa1  dy_csa2  + dx_csa2  dy_csa1 ))
        --------- = 0.25 (------------------------------------------------------------------------
           dDr                                              2     3/2
                                                       (3 Dr  + 1)
                    
                                   2        2          2          2            2        2          2          2
                       3 (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                     + -----------------------------------------------------------------------------------------
                                                                     2
                                                            SQRT(3 Dr  + 1)
                    
                           2           2        2          2          2            2        2          2          2
                       9 Dr  (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                     - ---------------------------------------------------------------------------------------------)
                                                                   2     3/2
                                                              (3 Dr  + 1)




    """

    # Factors.
    cobeta = 1.0/sqrt(3.0 * diff_data.params[2]**2 + 1.0)
    sibeta = -sqrt(3.0) * diff_data.params[2]/sqrt(3.0 * diff_data.params[2]**2 + 1.0)

    # Oi partial derivative.
    ##########################

    data.dci_csaC[3:, 4] = 0.25 * (sqrt(3.0) * (6.0 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO-2.0 * data.dy_csa2 * data.ddy_csa2_dO+6.0 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO-2.0 * data.dy_csa1 * data.ddy_csa1_dO-6.0 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2.0 * data.dx_csa2 * data.ddx_csa2_dO-6.0 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO+2.0 * data.dx_csa1 * data.ddx_csa1_dO) * sibeta+3.0 * (2.0 * data.dz_csa1**2 * data.dz_csa2 * data.ddz_csa2_dO+2.0 * data.dz_csa1 * data.dz_csa2**2 * data.ddz_csa1_dO+2.0 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO+2.0 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO+2.0 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2.0 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO)-3.0 * cobeta * (2.0 * data.dz_csa1**2 * data.dz_csa2 * data.ddz_csa2_dO+2.0 * data.dz_csa1 * data.dz_csa2**2 * data.ddz_csa1_dO+2.0 * data.dx_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO+2.0 * data.dx_csa2**2 * data.dy_csa1 * data.ddy_csa1_dO+2.0 * data.dx_csa2 * data.dy_csa1**2 * data.ddx_csa2_dO+2.0 * data.dx_csa1 * data.dy_csa2**2 * data.ddx_csa1_dO))

    data.dci_csaC[3:, 1] = 3.0 * data.dy_csa1 * data.dy_csa2 * data.dz_csa1 * data.ddz_csa2_dO+3.0 * data.dy_csa1 * data.dy_csa2 * data.dz_csa2 * data.ddz_csa1_dO+3.0 * data.dy_csa1 * data.dz_csa1 * data.dz_csa2 * data.ddy_csa2_dO+3.0 * data.dy_csa2 * data.dz_csa1 * data.dz_csa2 * data.ddy_csa1_dO

    data.dci_csaC[3:, 2] = 3.0 * data.dx_csa1 * data.dx_csa2 * data.dz_csa1 * data.ddz_csa2_dO+3.0 * data.dx_csa1 * data.dx_csa2 * data.dz_csa2 * data.ddz_csa1_dO+3.0 * data.dx_csa1 * data.dz_csa1 * data.dz_csa2 * data.ddx_csa2_dO+3.0 * data.dx_csa2 * data.dz_csa1 * data.dz_csa2 * data.ddx_csa1_dO

    data.dci_csaC[3:, 3] = 3.0 * data.dx_csa1 * data.dx_csa2 * data.dy_csa1 * data.ddy_csa2_dO+3.0 * data.dx_csa1 * data.dx_csa2 * data.dy_csa2 * data.ddy_csa1_dO+3.0 * data.dx_csa1 * data.dy_csa1 * data.dy_csa2 * data.ddx_csa2_dO+3.0 * data.dx_csa2 * data.dy_csa1 * data.dy_csa2 * data.ddx_csa1_dO

    data.dci_csaC[3:, 0] = 0.25 * (-sqrt(3.0) * (6.0 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO-2.0 * data.dy_csa2 * data.ddy_csa2_dO+6.0 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO-2.0 * data.dy_csa1 * data.ddy_csa1_dO-6.0 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2.0 * data.dx_csa2 * data.ddx_csa2_dO-6.0 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO+2.0 * data.dx_csa1 * data.ddx_csa1_dO) * sibeta+3.0 * (2.0 * data.dz_csa1**2 * data.dz_csa2 * data.ddz_csa2_dO+2.0 * data.dz_csa1 * data.dz_csa2**2 * data.ddz_csa1_dO+2.0 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO+2.0 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO+2.0 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2.0 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO)+3.0 * cobeta * (2.0 * data.dz_csa1**2 * data.dz_csa2 * data.ddz_csa2_dO+2.0 * data.dz_csa1 * data.dz_csa2**2 * data.ddz_csa1_dO+2.0 * data.dx_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO+2.0 * data.dx_csa2**2 * data.dy_csa1 * data.ddy_csa1_dO+2.0 * data.dx_csa2 * data.dy_csa1**2 * data.ddx_csa2_dO+2.0 * data.dx_csa1 * data.dy_csa2**2 * data.ddx_csa1_dO))



    # Dr partial derivative.
    ########################

    # Weight c2.
    data.dci_csaC[2, 4] = 0.25 * (-3 * diff_data.params[2] * (1-3 * (data.dz_csa1**2 * data.dz_csa2**2+data.dx_csa1**2 * data.dy_csa2**2+data.dx_csa2**2 * data.dy_csa1**2))/(3 * diff_data.params[2]**2+1)**(3/2)-3 * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/sqrt(3 * diff_data.params[2]**2+1)+9 * diff_data.params[2]**2 * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/(3 * diff_data.params[2]**2+1)**(3/2))
     
    # Weight c-2.
    data.dci_csaC[2, 0] = 0.25 * (3 * diff_data.params[2] * (1-3 * (data.dz_csa1**2 * data.dz_csa2**2+data.dx_csa1**2 * data.dy_csa2**2+data.dx_csa2**2 * data.dy_csa1**2))/(3 * diff_data.params[2]**2+1)**(3/2)+3 * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/sqrt(3 * diff_data.params[2]**2+1)-9 * diff_data.params[2]**2 * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/(3 * diff_data.params[2]**2+1)**(3/2))



# Ellipsoid weight Hessian.
###########################

def calc_csaC_ellipsoid_d2ci(data, diff_data):
    """Weight Hessian for ellipsoidal diffusion.

    Oi-Oj partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

                                                                                                                                                    2
        d2cp2_csaC                           2 ddy_csa2 ddy_csa2     ddy_csa2 ddy_csa2              ddy_csa1         ddy_csa2            2         d dy_csa2
       ----------- = 0.25 (SQRT(3) (6 dy_csa1  -------- -------- - 2 -------- -------- + 12 dy_csa1 -------- dy_csa2 -------- + 6 dy_csa1  dy_csa2 ---------
        dOi dOj                                  dOi      dOj          dOi      dOj                   dOi              dOj                          dOi dOj
        
                                2                                                                                           2
                               d dy_csa2              ddy_csa1         ddy_csa2     ddy_csa1 ddy_csa1        2             d dy_csa1        2     ddy_csa1 ddy_csa1
                   - 2 dy_csa2 --------- + 12 dy_csa1 -------- dy_csa2 -------- + 6 -------- -------- dy_csa2  + 6 dy_csa1 --------- dy_csa2  - 2 -------- --------
                                dOi dOj                 dOj              dOi          dOi      dOj                          dOi dOj                 dOi      dOj
                  
                                2                                                                                                                          2
                               d dy_csa1            2 ddx_csa2 ddx_csa2     ddx_csa2 ddx_csa2              ddx_csa1         ddx_csa2            2         d dx_csa2
                   - 2 dy_csa1 --------- - 6 dx_csa1  -------- -------- + 2 -------- -------- - 12 dx_csa1 -------- dx_csa2 -------- - 6 dx_csa1  dx_csa2 ---------
                                dOi dOj                 dOi      dOj          dOi      dOj                   dOi              dOj                          dOi dOj
                  
                                2                                                                                           2
                               d dx_csa2              ddx_csa1         ddx_csa2     ddx_csa1 ddx_csa1        2             d dx_csa1        2     ddx_csa1 ddx_csa1
                   + 2 dx_csa2 --------- - 12 dx_csa1 -------- dx_csa2 -------- - 6 -------- -------- dx_csa2  - 6 dx_csa1 --------- dx_csa2  + 2 -------- --------
                                dOi dOj                 dOj              dOi          dOi      dOj                          dOi dOj                 dOi      dOj
                  
                                2                                                                                                              2
                               d dx_csa1                       2 ddz_csa2 ddz_csa2             ddz_csa1         ddz_csa2            2         d dz_csa2
                   + 2 dx_csa1 ---------) sibeta + 3 (2 dz_csa1  -------- -------- + 4 dz_csa1 -------- dz_csa2 -------- + 2 dz_csa1  dz_csa2 ---------
                                dOi dOj                            dOi      dOj                  dOi              dOj                          dOi dOj
                  
                                                                                                     2
                               ddz_csa1         ddz_csa2     ddz_csa1 ddz_csa1        2             d dz_csa1        2            2 ddy_csa2 ddy_csa2
                   + 4 dz_csa1 -------- dz_csa2 -------- + 2 -------- -------- dz_csa2  + 2 dz_csa1 --------- dz_csa2  + 2 dy_csa1  -------- --------
                                 dOj              dOi          dOi      dOj                          dOi dOj                          dOi      dOj
                  
                                                                               2
                               ddy_csa1         ddy_csa2            2         d dy_csa2             ddy_csa1         ddy_csa2     ddy_csa1 ddy_csa1        2
                   + 4 dy_csa1 -------- dy_csa2 -------- + 2 dy_csa1  dy_csa2 --------- + 4 dy_csa1 -------- dy_csa2 -------- + 2 -------- -------- dy_csa2
                                 dOi              dOj                          dOi dOj                dOj              dOi          dOi      dOj
                  
                                2                                                                                                            2
                               d dy_csa1        2            2 ddx_csa2 ddx_csa2             ddx_csa1         ddx_csa2            2         d dx_csa2
                   + 2 dy_csa1 --------- dy_csa2  + 2 dx_csa1  -------- -------- + 4 dx_csa1 -------- dx_csa2 -------- + 2 dx_csa1  dx_csa2 ---------
                                dOi dOj                          dOi      dOj                  dOi              dOj                          dOi dOj
                  
                                                                                                     2
                               ddx_csa1         ddx_csa2     ddx_csa1 ddx_csa1        2             d dx_csa1        2
                   + 4 dx_csa1 -------- dx_csa2 -------- + 2 -------- -------- dx_csa2  + 2 dx_csa1 --------- dx_csa2 )
                                 dOj              dOi          dOi      dOj                          dOi dOj
                  
                                                                                                                        2
                                        2 ddz_csa2 ddz_csa2             ddz_csa1         ddz_csa2            2         d dz_csa2             ddz_csa1         ddz_csa2
                   - 3 cobeta (2 dz_csa1  -------- -------- + 4 dz_csa1 -------- dz_csa2 -------- + 2 dz_csa1  dz_csa2 --------- + 4 dz_csa1 -------- dz_csa2 --------
                                            dOi      dOj                  dOi              dOj                          dOi dOj                dOj              dOi
                  
                                                               2
                       ddz_csa1 ddz_csa1        2             d dz_csa1        2            2 ddy_csa2 ddy_csa2             ddx_csa1         ddy_csa2
                   + 2 -------- -------- dz_csa2  + 2 dz_csa1 --------- dz_csa2  + 2 dx_csa1  -------- -------- + 4 dx_csa1 -------- dy_csa2 --------
                         dOi      dOj                          dOi dOj                          dOi      dOj                  dOi              dOj
                  
                                         2                                                                                          2
                              2         d dy_csa2             ddx_csa1         ddy_csa2     ddx_csa1 ddx_csa1        2             d dx_csa1        2
                   + 2 dx_csa1  dy_csa2 --------- + 4 dx_csa1 -------- dy_csa2 -------- + 2 -------- -------- dy_csa2  + 2 dx_csa1 --------- dy_csa2
                                         dOi dOj                dOj              dOi          dOi      dOj                          dOi dOj
                  
                                                                                                              2
                              2 ddy_csa1 ddy_csa1             ddx_csa2         ddy_csa1            2         d dy_csa1             ddx_csa2         ddy_csa1
                   + 2 dx_csa2  -------- -------- + 4 dx_csa2 -------- dy_csa1 -------- + 2 dx_csa2  dy_csa1 --------- + 4 dx_csa2 -------- dy_csa1 --------
                                  dOi      dOj                  dOi              dOj                          dOi dOj                dOj              dOi
                  
                                                               2
                       ddx_csa2 ddx_csa2        2             d dx_csa2        2
                   + 2 -------- -------- dy_csa1  + 2 dx_csa2 --------- dy_csa1 ))
                         dOi      dOj                          dOi dOj
        

        
        d2cm1_csaC                     ddz_csa1 ddz_csa2             ddy_csa2         ddz_csa2     ddy_csa1                 ddz_csa2
       ----------- = 3 dy_csa1 dy_csa2 -------- -------- + 3 dy_csa1 -------- dz_csa1 -------- + 3 -------- dy_csa2 dz_csa1 --------
         dOi dOj                         dOi      dOj                  dOi              dOj          dOi                      dOj
        
                                                2
                                               d dz_csa2                     ddz_csa1 ddz_csa2             ddy_csa2         ddz_csa2     ddy_csa1                 ddz_csa2
                   + 3 dy_csa1 dy_csa2 dz_csa1 --------- + 3 dy_csa1 dy_csa2 -------- -------- + 3 dy_csa1 -------- dz_csa1 -------- + 3 -------- dy_csa2 dz_csa1 --------
                                                dOi dOj                        dOj      dOi                  dOj              dOi          dOj                      dOi
                  
                                                                                                                    2
                               ddy_csa2 ddz_csa1             ddy_csa1         ddz_csa1                             d dz_csa1                     ddy_csa2 ddz_csa1
                   + 3 dy_csa1 -------- -------- dz_csa2 + 3 -------- dy_csa2 -------- dz_csa2 + 3 dy_csa1 dy_csa2 --------- dz_csa2 + 3 dy_csa1 -------- -------- dz_csa2
                                 dOi      dOj                  dOi              dOj                                 dOi dOj                        dOj      dOi
                  
                                                                                                            2
                       ddy_csa1         ddz_csa1             ddy_csa1 ddy_csa2                             d dy_csa2                     ddy_csa1 ddy_csa2
                   + 3 -------- dy_csa2 -------- dz_csa2 + 3 -------- -------- dz_csa1 dz_csa2 + 3 dy_csa1 --------- dz_csa1 dz_csa2 + 3 -------- -------- dz_csa1 dz_csa2
                         dOj              dOi                  dOi      dOj                                 dOi dOj                        dOj      dOi
                  
                        2
                       d dy_csa1
                   + 3 --------- dy_csa2 dz_csa1 dz_csa2
                        dOi dOj
                  

        
        d2c0_csaC                     ddz_csa1 ddz_csa2             ddx_csa2         ddz_csa2     ddx_csa1                 ddz_csa2
       ---------- = 3 dx_csa1 dx_csa2 -------- -------- + 3 dx_csa1 -------- dz_csa1 -------- + 3 -------- dx_csa2 dz_csa1 --------
        dOi dOj                         dOi      dOj                  dOi              dOj          dOi                      dOj
        
                                                2
                                               d dz_csa2                     ddz_csa1 ddz_csa2             ddx_csa2         ddz_csa2     ddx_csa1                 ddz_csa2
                   + 3 dx_csa1 dx_csa2 dz_csa1 --------- + 3 dx_csa1 dx_csa2 -------- -------- + 3 dx_csa1 -------- dz_csa1 -------- + 3 -------- dx_csa2 dz_csa1 --------
                                                dOi dOj                        dOj      dOi                  dOj              dOi          dOj                      dOi
                  
                                                                                                                    2
                               ddx_csa2 ddz_csa1             ddx_csa1         ddz_csa1                             d dz_csa1                     ddx_csa2 ddz_csa1
                   + 3 dx_csa1 -------- -------- dz_csa2 + 3 -------- dx_csa2 -------- dz_csa2 + 3 dx_csa1 dx_csa2 --------- dz_csa2 + 3 dx_csa1 -------- -------- dz_csa2
                                 dOi      dOj                  dOi              dOj                                 dOi dOj                        dOj      dOi
                  
                                                                                                            2
                       ddx_csa1         ddz_csa1             ddx_csa1 ddx_csa2                             d dx_csa2                     ddx_csa1 ddx_csa2
                   + 3 -------- dx_csa2 -------- dz_csa2 + 3 -------- -------- dz_csa1 dz_csa2 + 3 dx_csa1 --------- dz_csa1 dz_csa2 + 3 -------- -------- dz_csa1 dz_csa2
                         dOj              dOi                  dOi      dOj                                 dOi dOj                        dOj      dOi
                  
                        2
                       d dx_csa1
                   + 3 --------- dx_csa2 dz_csa1 dz_csa2
                        dOi dOj
        

        
        d2cp1_csaC                     ddy_csa1 ddy_csa2             ddx_csa2         ddy_csa2     ddx_csa1                 ddy_csa2
       ----------- = 3 dx_csa1 dx_csa2 -------- -------- + 3 dx_csa1 -------- dy_csa1 -------- + 3 -------- dx_csa2 dy_csa1 --------
         dOi dOj                         dOi      dOj                  dOi              dOj          dOi                      dOj
          
                                                2
                                               d dy_csa2                     ddy_csa1 ddy_csa2             ddx_csa2         ddy_csa2     ddx_csa1                 ddy_csa2
                   + 3 dx_csa1 dx_csa2 dy_csa1 --------- + 3 dx_csa1 dx_csa2 -------- -------- + 3 dx_csa1 -------- dy_csa1 -------- + 3 -------- dx_csa2 dy_csa1 --------
                                                dOi dOj                        dOj      dOi                  dOj              dOi          dOj                      dOi
                  
                                                                                                                    2
                               ddx_csa2 ddy_csa1             ddx_csa1         ddy_csa1                             d dy_csa1                     ddx_csa2 ddy_csa1
                   + 3 dx_csa1 -------- -------- dy_csa2 + 3 -------- dx_csa2 -------- dy_csa2 + 3 dx_csa1 dx_csa2 --------- dy_csa2 + 3 dx_csa1 -------- -------- dy_csa2
                                 dOi      dOj                  dOi              dOj                                 dOi dOj                        dOj      dOi
                  
                                                                                                            2
                       ddx_csa1         ddy_csa1             ddx_csa1 ddx_csa2                             d dx_csa2                     ddx_csa1 ddx_csa2
                   + 3 -------- dx_csa2 -------- dy_csa2 + 3 -------- -------- dy_csa1 dy_csa2 + 3 dx_csa1 --------- dy_csa1 dy_csa2 + 3 -------- -------- dy_csa1 dy_csa2
                         dOj              dOi                  dOi      dOj                                 dOi dOj                        dOj      dOi
                  
                        2
                       d dx_csa1
                   + 3 --------- dx_csa2 dy_csa1 dy_csa2
                        dOi dOj


                                                                                                                                                     2
        d2cm2_csaC                             2 ddy_csa2 ddy_csa2     ddy_csa2 ddy_csa2              ddy_csa1         ddy_csa2            2         d dy_csa2
       ----------- = 0.25 (- SQRT(3) (6 dy_csa1  -------- -------- - 2 -------- -------- + 12 dy_csa1 -------- dy_csa2 -------- + 6 dy_csa1  dy_csa2 ---------
         dOi dOj                                   dOi      dOj          dOi      dOj                   dOi              dOj                          dOi dOj
                  
                                2                                                                                           2
                               d dy_csa2              ddy_csa1         ddy_csa2     ddy_csa1 ddy_csa1        2             d dy_csa1        2     ddy_csa1 ddy_csa1
                   - 2 dy_csa2 --------- + 12 dy_csa1 -------- dy_csa2 -------- + 6 -------- -------- dy_csa2  + 6 dy_csa1 --------- dy_csa2  - 2 -------- --------
                                dOi dOj                 dOj              dOi          dOi      dOj                          dOi dOj                 dOi      dOj
                  
                                2                                                                                                                          2
                               d dy_csa1            2 ddx_csa2 ddx_csa2     ddx_csa2 ddx_csa2              ddx_csa1         ddx_csa2            2         d dx_csa2
                   - 2 dy_csa1 --------- - 6 dx_csa1  -------- -------- + 2 -------- -------- - 12 dx_csa1 -------- dx_csa2 -------- - 6 dx_csa1  dx_csa2 ---------
                                dOi dOj                 dOi      dOj          dOi      dOj                   dOi              dOj                          dOi dOj
                  
                                2                                                                                           2
                               d dx_csa2              ddx_csa1         ddx_csa2     ddx_csa1 ddx_csa1        2             d dx_csa1        2     ddx_csa1 ddx_csa1
                   + 2 dx_csa2 --------- - 12 dx_csa1 -------- dx_csa2 -------- - 6 -------- -------- dx_csa2  - 6 dx_csa1 --------- dx_csa2  + 2 -------- --------
                                dOi dOj                 dOj              dOi          dOi      dOj                          dOi dOj                 dOi      dOj
                  
                                2                                                                                                              2
                               d dx_csa1                       2 ddz_csa2 ddz_csa2             ddz_csa1         ddz_csa2            2         d dz_csa2
                   + 2 dx_csa1 ---------) sibeta + 3 (2 dz_csa1  -------- -------- + 4 dz_csa1 -------- dz_csa2 -------- + 2 dz_csa1  dz_csa2 ---------
                                dOi dOj                            dOi      dOj                  dOi              dOj                          dOi dOj
                  
                                                                                                     2
                               ddz_csa1         ddz_csa2     ddz_csa1 ddz_csa1        2             d dz_csa1        2            2 ddy_csa2 ddy_csa2
                   + 4 dz_csa1 -------- dz_csa2 -------- + 2 -------- -------- dz_csa2  + 2 dz_csa1 --------- dz_csa2  + 2 dy_csa1  -------- --------
                                 dOj              dOi          dOi      dOj                          dOi dOj                          dOi      dOj
                  
                                                                               2
                               ddy_csa1         ddy_csa2            2         d dy_csa2             ddy_csa1         ddy_csa2     ddy_csa1 ddy_csa1        2
                   + 4 dy_csa1 -------- dy_csa2 -------- + 2 dy_csa1  dy_csa2 --------- + 4 dy_csa1 -------- dy_csa2 -------- + 2 -------- -------- dy_csa2
                                 dOi              dOj                          dOi dOj                dOj              dOi          dOi      dOj
                  
                                2                                                                                                            2
                               d dy_csa1        2            2 ddx_csa2 ddx_csa2             ddx_csa1         ddx_csa2            2         d dx_csa2
                   + 2 dy_csa1 --------- dy_csa2  + 2 dx_csa1  -------- -------- + 4 dx_csa1 -------- dx_csa2 -------- + 2 dx_csa1  dx_csa2 ---------
                                dOi dOj                          dOi      dOj                  dOi              dOj                          dOi dOj
                  
                                                                                                     2
                               ddx_csa1         ddx_csa2     ddx_csa1 ddx_csa1        2             d dx_csa1        2
                   + 4 dx_csa1 -------- dx_csa2 -------- + 2 -------- -------- dx_csa2  + 2 dx_csa1 --------- dx_csa2 )
                                 dOj              dOi          dOi      dOj                          dOi dOj
                  
                                                                                                                        2
                                        2 ddz_csa2 ddz_csa2             ddz_csa1         ddz_csa2            2         d dz_csa2             ddz_csa1         ddz_csa2
                   + 3 cobeta (2 dz_csa1  -------- -------- + 4 dz_csa1 -------- dz_csa2 -------- + 2 dz_csa1  dz_csa2 --------- + 4 dz_csa1 -------- dz_csa2 --------
                                            dOi      dOj                  dOi              dOj                          dOi dOj                dOj              dOi
                  
                                                               2
                       ddz_csa1 ddz_csa1        2             d dz_csa1        2            2 ddy_csa2 ddy_csa2             ddx_csa1         ddy_csa2
                   + 2 -------- -------- dz_csa2  + 2 dz_csa1 --------- dz_csa2  + 2 dx_csa1  -------- -------- + 4 dx_csa1 -------- dy_csa2 --------
                         dOi      dOj                          dOi dOj                          dOi      dOj                  dOi              dOj
                  
                                         2                                                                                          2
                              2         d dy_csa2             ddx_csa1         ddy_csa2     ddx_csa1 ddx_csa1        2             d dx_csa1        2
                   + 2 dx_csa1  dy_csa2 --------- + 4 dx_csa1 -------- dy_csa2 -------- + 2 -------- -------- dy_csa2  + 2 dx_csa1 --------- dy_csa2
                                         dOi dOj                dOj              dOi          dOi      dOj                          dOi dOj
                  
                                                                                                              2
                              2 ddy_csa1 ddy_csa1             ddx_csa2         ddy_csa1            2         d dy_csa1             ddx_csa2         ddy_csa1
                   + 2 dx_csa2  -------- -------- + 4 dx_csa2 -------- dy_csa1 -------- + 2 dx_csa2  dy_csa1 --------- + 4 dx_csa2 -------- dy_csa1 --------
                                  dOi      dOj                  dOi              dOj                          dOi dOj                dOj              dOi
                  
                                                               2
                       ddx_csa2 ddx_csa2        2             d dx_csa2        2
                   + 2 -------- -------- dy_csa1  + 2 dx_csa2 --------- dy_csa1 ))
                         dOi      dOj                          dOi dOj
                  


    Oi-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csaC
        ------------  =  0,
          dOi.dtm


         d2c-1_csaC
        ------------  =  0,
          dOi.dtm


         d2c0_csaC
        ------------  =  0,
          dOi.dtm


         d2c1_csaC
        ------------  =  0,
          dOi.dtm


         d2c2_csaC
        ------------  =  0.
          dOi.dtm


    Oi-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csaC
        ------------  =  0,
          dOi.dDa


         d2c-1_csaC
        ------------  =  0,
          dOi.dDa


         d2c0_csaC
        ------------  =  0,
          dOi.dDa


         d2c1_csaC
        ------------  =  0,
          dOi.dDa


         d2c2_csaC
        ------------  =  0.
          dOi.dDa


    Oi-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

        dc2_csaC                        2         ddz_csa2             ddz_csa1        2            2         ddy_csa2             ddx_csa1        2
        -------- = 0.25 (9 Dr (2 dz_csa1  dz_csa2 -------- + 2 dz_csa1 -------- dz_csa2  + 2 dx_csa1  dy_csa2 -------- + 2 dx_csa1 -------- dy_csa2
        dOi.dDr                                     dOi                  dOi                                    dOi                  dOi
                 
                              2         ddy_csa1             ddx_csa2        2       2     3/2
                   + 2 dx_csa2  dy_csa1 -------- + 2 dx_csa2 -------- dy_csa1 )/(3 Dr  + 1)    - 3
                                          dOi                  dOi
                 
                             2         ddy_csa2             ddy_csa2             ddy_csa1        2             ddy_csa1            2         ddx_csa2             ddx_csa2
                   (6 dy_csa1  dy_csa2 -------- - 2 dy_csa2 -------- + 6 dy_csa1 -------- dy_csa2  - 2 dy_csa1 -------- - 6 dx_csa1  dx_csa2 -------- + 2 dx_csa2 --------
                                         dOi                  dOi                  dOi                           dOi                           dOi                  dOi
                 
                               ddx_csa1        2             ddx_csa1           2            2           2         ddy_csa2             ddy_csa2             ddy_csa1        2
                   - 6 dx_csa1 -------- dx_csa2  + 2 dx_csa1 --------)/SQRT(3 Dr  + 1) + 9 Dr  (6 dy_csa1  dy_csa2 -------- - 2 dy_csa2 -------- + 6 dy_csa1 -------- dy_csa2
                                 dOi                           dOi                                                   dOi                  dOi                  dOi
                 
                               ddy_csa1            2         ddx_csa2             ddx_csa2             ddx_csa1        2             ddx_csa1       2     3/2
                   - 2 dy_csa1 -------- - 6 dx_csa1  dx_csa2 -------- + 2 dx_csa2 -------- - 6 dx_csa1 -------- dx_csa2  + 2 dx_csa1 --------)/(3 Dr  + 1)   )
                                 dOi                           dOi                  dOi                  dOi                           dOi


         d2c-1_csaC
        ------------  =  0,
          dOi.dDr


         d2c0_csaC
        ------------  =  0,
          dOi.dDr


         d2c1_csaC
        ------------  =  0,
          dOi.dDr



        dc-2_csaC                          2         ddz_csa2             ddz_csa1        2            2         ddy_csa2             ddx_csa1        2
        --------- = 0.25 (- 9 Dr (2 dz_csa1  dz_csa2 -------- + 2 dz_csa1 -------- dz_csa2  + 2 dx_csa1  dy_csa2 -------- + 2 dx_csa1 -------- dy_csa2
         dOi.dDr                                       dOi                  dOi                                    dOi                  dOi

                            2         ddy_csa1             ddx_csa2        2       2     3/2
                 + 2 dx_csa2  dy_csa1 -------- + 2 dx_csa2 -------- dy_csa1 )/(3 Dr  + 1)    + 3
                                        dOi                  dOi
                
                           2         ddy_csa2             ddy_csa2             ddy_csa1        2             ddy_csa1            2         ddx_csa2             ddx_csa2
                 (6 dy_csa1  dy_csa2 -------- - 2 dy_csa2 -------- + 6 dy_csa1 -------- dy_csa2  - 2 dy_csa1 -------- - 6 dx_csa1  dx_csa2 -------- + 2 dx_csa2 --------
                                       dOi                  dOi                  dOi                           dOi                           dOi                  dOi
                
                             ddx_csa1        2             ddx_csa1           2            2           2         ddy_csa2             ddy_csa2             ddy_csa1        2
                 - 6 dx_csa1 -------- dx_csa2  + 2 dx_csa1 --------)/SQRT(3 Dr  + 1) - 9 Dr  (6 dy_csa1  dy_csa2 -------- - 2 dy_csa2 -------- + 6 dy_csa1 -------- dy_csa2
                               dOi                           dOi                                                   dOi                  dOi                  dOi
                
                             ddy_csa1            2         ddx_csa2             ddx_csa2             ddx_csa1        2             ddx_csa1       2     3/2
                 - 2 dy_csa1 -------- - 6 dx_csa1  dx_csa2 -------- + 2 dx_csa2 -------- - 6 dx_csa1 -------- dx_csa2  + 2 dx_csa1 --------)/(3 Dr  + 1)   )
                               dOi                           dOi                  dOi                  dOi                           dOi
                
                 

    tm-tm partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_csaC
        ----------  =  0,
          dtm2


        d2c-1_csaC
        ----------  =  0,
          dtm2


        d2c0_csaC
        ---------   =  0,
          dtm2


        d2c1_csaC
        ---------   =  0,
          dtm2


        d2c2_csaC
        ---------   =  0.
          dtm2


    tm-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csaC
        ------------  =  0,
          dtm.dDa


         d2c-1_csaC
        ------------  =  0,
          dtm.dDa


         d2c0_csaC
        ------------  =  0,
          dtm.dDa


         d2c1_csaC
        ------------  =  0,
          dtm.dDa


         d2c2_csaC
        ------------  =  0.
          dtm.dDa


    tm-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csaC
        ------------  =  0,
          dtm.dDr


         d2c-1_csaC
        ------------  =  0,
          dtm.dDr


         d2c0_csaC
        ------------  =  0,
          dtm.dDr


         d2c1_csaC
        ------------  =  0,
          dtm.dDr


         d2c2_csaC
        ------------  =  0.
          dtm.dDr


    Da-Da partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

        d2c-2_csaC
        -----------  =  0,
          dDa**2


        d2c-1_csaC
        -----------  =  0,
          dDa**2


         d2c0_csaC
        -----------  =  0,
          dDa**2


         d2c1_csaC
        -----------  =  0,
          dDa**2


         d2c2_csaC
        -----------  =  0.
          dDa**2


    Da-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~

         d2c-2_csaC
        ------------  =  0,
          dDa.dDr


         d2c-1_csaC
        ------------  =  0,
          dDa.dDr


         d2c0_csaC
        ------------  =  0,
          dDa.dDr


         d2c1_csaC
        ------------  =  0,
          dDa.dDr


         d2c2_csaC
        ------------  =  0.
          dDa.dDr


    Dr-Dr partial derivatives
    ~~~~~~~~~~~~~~~~~~~~~~~~~


         2                                   2        2          2        2          2        2
        d c2_csaC           3 (1 - 3 (dz_csa1  dz_csa2  + dx_csa1  dy_csa2  + dx_csa2  dy_csa1 ))
        --------- = 0.25 (- ---------------------------------------------------------------------
             2                                              2     3/2
          dDr                                          (3 Dr  + 1)
                 
                         2                2        2          2        2          2        2
                    27 Dr  (1 - 3 (dz_csa1  dz_csa2  + dx_csa1  dy_csa2  + dx_csa2  dy_csa1 ))
                  + --------------------------------------------------------------------------
                                                       2     5/2
                                                  (3 Dr  + 1)
                 
                                    2        2          2          2            2        2          2          2
                    27 Dr (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                  + ---------------------------------------------------------------------------------------------
                                                                2     3/2
                                                           (3 Dr  + 1)
                 
                         3           2        2          2          2            2        2          2          2
                    81 Dr  (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                  - ----------------------------------------------------------------------------------------------)
                                                                 2     5/2
                                                             (3 Dr  + 1)


        d2c-1_csaC
        -----------  =  0,
          dDr**2


         d2c0_csaC
        -----------  =  0,
          dDr**2


         d2c1_csaC
        -----------  =  0,
          dDr**2


         2                                  2        2          2        2          2        2
        d cm2_csaC         3 (1 - 3 (dz_csa1  dz_csa2  + dx_csa1  dy_csa2  + dx_csa2  dy_csa1 ))
        ---------- = 0.25 (---------------------------------------------------------------------
              2                                            2     3/2
           dDr                                        (3 Dr  + 1)
                
                         2                2        2          2        2          2        2
                    27 Dr  (1 - 3 (dz_csa1  dz_csa2  + dx_csa1  dy_csa2  + dx_csa2  dy_csa1 ))
                  - --------------------------------------------------------------------------
                                                       2     5/2
                                                  (3 Dr  + 1)
                
                                    2        2          2          2            2        2          2          2
                    27 Dr (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                  - ---------------------------------------------------------------------------------------------
                                                                2     3/2
                                                           (3 Dr  + 1)
                
                         3           2        2          2          2            2        2          2          2
                    81 Dr  (3 dy_csa1  dy_csa2  - dy_csa2  - dy_csa1  - 3 dx_csa1  dx_csa2  + dx_csa2  + dx_csa1 )
                  + ----------------------------------------------------------------------------------------------)
                                                                 2     5/2
                                                            (3 Dr  + 1)

     """

    # Oi-Oj partial derivative.
    ###############################
   

    cobeta = 1.0/sqrt(3.0 * diff_data.params[2]**2 + 1.0)
    sibeta = -sqrt(3.0) * diff_data.params[2]/sqrt(3.0 * diff_data.params[2]**2 + 1.0)

    
    # Outer product.
    op_z1z1_csaC = outerproduct(data.ddz_csa1_dO, data.ddz_csa1_dO)
    op_z1z2_csaC = outerproduct(data.ddz_csa1_dO, data.ddz_csa2_dO)
    op_z2z1_csaC = outerproduct(data.ddz_csa2_dO, data.ddz_csa1_dO)
    op_z2z2_csaC = outerproduct(data.ddz_csa2_dO, data.ddz_csa2_dO)
    op_x1x1_csaC = outerproduct(data.ddx_csa1_dO, data.ddx_csa1_dO)
    op_x1x2_csaC = outerproduct(data.ddx_csa1_dO, data.ddx_csa2_dO)
    op_x2x1_csaC = outerproduct(data.ddx_csa2_dO, data.ddx_csa1_dO)
    op_x2x2_csaC = outerproduct(data.ddx_csa2_dO, data.ddx_csa2_dO)
    op_y1y1_csaC = outerproduct(data.ddy_csa1_dO, data.ddy_csa1_dO)
    op_y1y2_csaC = outerproduct(data.ddy_csa1_dO, data.ddy_csa2_dO)
    op_y2y1_csaC = outerproduct(data.ddy_csa2_dO, data.ddy_csa1_dO)
    op_y2y2_csaC = outerproduct(data.ddy_csa2_dO, data.ddy_csa2_dO)
    #
    op_z1x1_csaC = outerproduct(data.ddz_csa1_dO, data.ddx_csa1_dO)
    op_x1z1_csaC = outerproduct(data.ddx_csa1_dO, data.ddz_csa1_dO)
    op_z1y1_csaC = outerproduct(data.ddz_csa1_dO, data.ddy_csa1_dO)
    op_y1z1_csaC = outerproduct(data.ddy_csa1_dO, data.ddz_csa1_dO)
    op_z1x2_csaC = outerproduct(data.ddz_csa1_dO, data.ddx_csa2_dO)
    op_x2z1_csaC = outerproduct(data.ddx_csa2_dO, data.ddz_csa1_dO)
    op_z1y2_csaC = outerproduct(data.ddz_csa1_dO, data.ddy_csa2_dO)
    op_y2z1_csaC = outerproduct(data.ddy_csa2_dO, data.ddz_csa1_dO)
    op_z2x1_csaC = outerproduct(data.ddz_csa2_dO, data.ddx_csa1_dO)
    op_x1z2_csaC = outerproduct(data.ddx_csa1_dO, data.ddz_csa2_dO)
    op_z2y1_csaC = outerproduct(data.ddz_csa2_dO, data.ddy_csa1_dO)
    op_y1z2_csaC = outerproduct(data.ddy_csa1_dO, data.ddz_csa2_dO)
    op_z2x2_csaC = outerproduct(data.ddz_csa2_dO, data.ddx_csa2_dO)
    op_x2z2_csaC = outerproduct(data.ddx_csa2_dO, data.ddz_csa2_dO)
    op_z2y2_csaC = outerproduct(data.ddz_csa2_dO, data.ddy_csa2_dO)
    op_y2z2_csaC = outerproduct(data.ddy_csa2_dO, data.ddz_csa2_dO)
    #
    op_x1y1_csaC = outerproduct(data.ddx_csa1_dO, data.ddy_csa1_dO)
    op_y1x1_csaC = outerproduct(data.ddy_csa1_dO, data.ddx_csa1_dO)
    op_x1y2_csaC = outerproduct(data.ddx_csa1_dO, data.ddy_csa2_dO)
    op_y2x1_csaC = outerproduct(data.ddy_csa2_dO, data.ddx_csa1_dO)
    op_x2y1_csaC = outerproduct(data.ddx_csa2_dO, data.ddy_csa1_dO)
    op_y1x2_csaC = outerproduct(data.ddy_csa1_dO, data.ddx_csa2_dO)
    op_x2y2_csaC = outerproduct(data.ddx_csa2_dO, data.ddy_csa2_dO)
    op_y2x2_csaC = outerproduct(data.ddy_csa2_dO, data.ddx_csa2_dO)
    
   
    # Weight c2.
    data.d2ci_csaC[3:, 3:, 4] = 1.5 * sqrt(3.0) * data.dy_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2 * sibeta-0.5 * sqrt(3.0) * data.dy_csa2 * data.d2dy_csa2_dO2 * sibeta+1.5 * sqrt(3.0) * data.dy_csa1 * data.dy_csa2**2 * data.d2dy_csa1_dO2 * sibeta-0.5 * sqrt(3.0) * data.dy_csa1 * data.d2dy_csa1_dO2 * sibeta-1.5 * sqrt(3.0) * data.dx_csa1**2 * data.dx_csa2 * data.d2dx_csa2_dO2 * sibeta+0.5 * sqrt(3.0) * data.dx_csa2 * data.d2dx_csa2_dO2 * sibeta-1.5 * sqrt(3.0) * data.dx_csa1 * data.dx_csa2**2 * data.d2dx_csa1_dO2 * sibeta+0.5 * sqrt(3.0) * data.dx_csa1 * data.d2dx_csa1_dO2 * sibeta+1.5 * sqrt(3.0) * op_y1y1_csaC * data.dy_csa2**2 * sibeta+3.0 * sqrt(3.0) * op_y1y2_csaC * data.dy_csa1 * data.dy_csa2 * sibeta+3.0 * sqrt(3.0) * op_y2y1_csaC * data.dy_csa1 * data.dy_csa2 * sibeta+1.5 * sqrt(3.0) * op_y2y2_csaC * data.dy_csa1**2 * sibeta-1.5 * sqrt(3.0) * op_x1x1_csaC * data.dx_csa2**2 * sibeta-3.0 * sqrt(3.0) * op_x1x2_csaC * data.dx_csa1 * data.dx_csa2 * sibeta-3.0 * sqrt(3.0) * op_x2x1_csaC * data.dx_csa1 * data.dx_csa2 * sibeta-1.5 * sqrt(3.0) * op_x2x2_csaC * data.dx_csa1**2 * sibeta-0.5 * sqrt(3.0) * op_y2y2_csaC * sibeta-0.5 * sqrt(3.0) * op_y1y1_csaC * sibeta+0.5 * sqrt(3.0) * op_x2x2_csaC * sibeta+0.5 * sqrt(3.0) * op_x1x1_csaC * sibeta-1.5 * cobeta * data.dz_csa1**2 * data.dz_csa2 * data.d2dz_csa2_dO2+1.5 * data.dz_csa1**2 * data.dz_csa2 * data.d2dz_csa2_dO2-1.5 * cobeta * data.dz_csa1 * data.dz_csa2**2 * data.d2dz_csa1_dO2+1.5 * data.dz_csa1 * data.dz_csa2**2 * data.d2dz_csa1_dO2+1.5 * data.dy_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2-1.5 * cobeta * data.dx_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2+1.5 * data.dy_csa1 * data.dy_csa2**2 * data.d2dy_csa1_dO2-1.5 * cobeta * data.dx_csa2**2 * data.dy_csa1 * data.d2dy_csa1_dO2-1.5 * cobeta * data.dx_csa2 * data.dy_csa1**2 * data.d2dx_csa2_dO2+1.5 * data.dx_csa1**2 * data.dx_csa2 * data.d2dx_csa2_dO2-1.5 * cobeta * data.dx_csa1 * data.dy_csa2**2 * data.d2dx_csa1_dO2+1.5 * data.dx_csa1 * data.dx_csa2**2 * data.d2dx_csa1_dO2-1.5 * cobeta * op_z1z1_csaC * data.dz_csa2**2+1.5 * op_z1z1_csaC * data.dz_csa2**2-3.0 * cobeta * op_z1z2_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_z1z2_csaC * data.dz_csa1 * data.dz_csa2-3.0 * cobeta * op_z2z1_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_z2z1_csaC * data.dz_csa1 * data.dz_csa2-1.5 * cobeta * op_z2z2_csaC * data.dz_csa1**2+1.5 * op_z2z2_csaC * data.dz_csa1**2+1.5 * op_y1y1_csaC * data.dy_csa2**2-1.5 * cobeta * op_x1x1_csaC * data.dy_csa2**2+3.0 * op_y1y2_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_y2y1_csaC * data.dy_csa1 * data.dy_csa2-3.0 * cobeta * op_x1y2_csaC * data.dx_csa1 * data.dy_csa2-3.0 * cobeta * op_y2x1_csaC * data.dx_csa1 * data.dy_csa2+1.5 * op_y2y2_csaC * data.dy_csa1**2-1.5 * cobeta * op_x2x2_csaC * data.dy_csa1**2-3.0 * cobeta * op_x2y1_csaC * data.dx_csa2 * data.dy_csa1-3.0 * cobeta * op_y1x2_csaC * data.dx_csa2 * data.dy_csa1-1.5 * cobeta * op_y1y1_csaC * data.dx_csa2**2+1.5 * op_x1x1_csaC * data.dx_csa2**2+3.0 * op_x1x2_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_x2x1_csaC * data.dx_csa1 * data.dx_csa2-1.5 * cobeta * op_y2y2_csaC * data.dx_csa1**2+1.5 * op_x2x2_csaC * data.dx_csa1**2
  
    # Weight c-1.
    data.d2ci_csaC[3:, 3:, 1] = 3.0 * data.dy_csa1 * data.dy_csa2 * data.dz_csa1 * data.d2dz_csa2_dO2+3.0 * data.dy_csa1 * data.dy_csa2 * data.dz_csa2 * data.d2dz_csa1_dO2+3.0 * data.dy_csa1 * data.dz_csa1 * data.dz_csa2 * data.d2dy_csa2_dO2+3.0 * data.dy_csa2 * data.dz_csa1 * data.dz_csa2 * data.d2dy_csa1_dO2+3.0 * op_y1y2_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_y2y1_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_y1z1_csaC * data.dy_csa2 * data.dz_csa2+3.0 * op_z1y1_csaC * data.dy_csa2 * data.dz_csa2+3.0 * op_y2z1_csaC * data.dy_csa1 * data.dz_csa2+3.0 * op_z1y2_csaC * data.dy_csa1 * data.dz_csa2+3.0 * op_y1z2_csaC * data.dy_csa2 * data.dz_csa1+3.0 * op_z2y1_csaC * data.dy_csa2 * data.dz_csa1+3.0 * op_y2z2_csaC * data.dy_csa1 * data.dz_csa1+3.0 * op_z2y2_csaC * data.dy_csa1 * data.dz_csa1+3.0 * op_z1z2_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_z2z1_csaC * data.dy_csa1 * data.dy_csa2
  
    # Weight c0.
    data.d2ci_csaC[3:, 3:, 2] = 3.0 * data.dx_csa1 * data.dx_csa2 * data.dz_csa1 * data.d2dz_csa2_dO2+3.0 * data.dx_csa1 * data.dx_csa2 * data.dz_csa2 * data.d2dz_csa1_dO2+3.0 * data.dx_csa1 * data.dz_csa1 * data.dz_csa2 * data.d2dx_csa2_dO2+3.0 * data.dx_csa2 * data.dz_csa1 * data.dz_csa2 * data.d2dx_csa1_dO2+3 * op_x1x2_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_x2x1_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_x1z1_csaC * data.dx_csa2 * data.dz_csa2+3.0 * op_z1x1_csaC * data.dx_csa2 * data.dz_csa2+3.0 * op_x2z1_csaC * data.dx_csa1 * data.dz_csa2+3.0 * op_z1x2_csaC * data.dx_csa1 * data.dz_csa2+3.0 * op_x1z2_csaC * data.dx_csa2 * data.dz_csa1+3.0 * op_z2x1_csaC * data.dx_csa2 * data.dz_csa1+3.0 * op_x2z2_csaC * data.dx_csa1 * data.dz_csa1+3.0 * op_z2x2_csaC * data.dx_csa1 * data.dz_csa1+3.0 * op_z1z2_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_z2z1_csaC * data.dx_csa1 * data.dx_csa2

    # Weight c1.
    data.d2ci_csaC[3:, 3:, 3] = 3.0 * data.dx_csa1 * data.dx_csa2 * data.dy_csa1 * data.d2dy_csa2_dO2+3.0 * data.dx_csa1 * data.dx_csa2 * data.dy_csa2 * data.d2dy_csa1_dO2+3.0 * data.dx_csa1 * data.dy_csa1 * data.dy_csa2 * data.d2dx_csa2_dO2+3.0 * data.dx_csa2 * data.dy_csa1 * data.dy_csa2 * data.d2dx_csa1_dO2+3.0 * op_x1x2_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_x2x1_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_x1y1_csaC * data.dx_csa2 * data.dy_csa2+3.0 * op_y1x1_csaC * data.dx_csa2 * data.dy_csa2+3.0 * op_x2y1_csaC * data.dx_csa1 * data.dy_csa2+3.0 * op_y1x2_csaC * data.dx_csa1 * data.dy_csa2+3.0 * op_x1y2_csaC * data.dx_csa2 * data.dy_csa1+3.0 * op_y2x1_csaC * data.dx_csa2 * data.dy_csa1+3.0 * op_x2y2_csaC * data.dx_csa1 * data.dy_csa1+3.0 * op_y2x2_csaC * data.dx_csa1 * data.dy_csa1+3.0 * op_y1y2_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_y2y1_csaC * data.dx_csa1 * data.dx_csa2

    # Weight c-2.
    data.d2ci_csaC[3:, 3:, 0] = -1.5 * sqrt(3.0) * data.dy_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2 * sibeta+0.5 * sqrt(3.0) * data.dy_csa2 * data.d2dy_csa2_dO2 * sibeta-1.5 * sqrt(3.0) * data.dy_csa1 * data.dy_csa2**2 * data.d2dy_csa1_dO2 * sibeta+0.5 * sqrt(3.0) * data.dy_csa1 * data.d2dy_csa1_dO2 * sibeta+1.5 * sqrt(3.0) * data.dx_csa1**2 * data.dx_csa2 * data.d2dx_csa2_dO2 * sibeta-0.5 * sqrt(3.0) * data.dx_csa2 * data.d2dx_csa2_dO2 * sibeta+1.5 * sqrt(3.0) * data.dx_csa1 * data.dx_csa2**2 * data.d2dx_csa1_dO2 * sibeta-0.5 * sqrt(3.0) * data.dx_csa1 * data.d2dx_csa1_dO2 * sibeta-1.5 * sqrt(3.0) * op_y1y1_csaC * data.dy_csa2**2 * sibeta-3.0 * sqrt(3.0) * op_y1y2_csaC * data.dy_csa1 * data.dy_csa2 * sibeta-3.0 * sqrt(3.0) * op_y2y1_csaC * data.dy_csa1 * data.dy_csa2 * sibeta-1.5 * sqrt(3.0) * op_y2y2_csaC * data.dy_csa1**2 * sibeta+1.5 * sqrt(3.0) * op_x1x1_csaC * data.dx_csa2**2 * sibeta+3.0 * sqrt(3.0) * op_x1x2_csaC * data.dx_csa1 * data.dx_csa2 * sibeta+3.0 * sqrt(3.0) * op_x2x1_csaC * data.dx_csa1 * data.dx_csa2 * sibeta+1.5 * sqrt(3.0) * op_x2x2_csaC * data.dx_csa1**2 * sibeta+0.5 * sqrt(3.0) * op_y2y2_csaC * sibeta+0.5 * sqrt(3.0) * op_y1y1_csaC * sibeta-0.5 * sqrt(3.0) * op_x2x2_csaC * sibeta-0.5 * sqrt(3.0) * op_x1x1_csaC * sibeta+1.5 * cobeta * data.dz_csa1**2 * data.dz_csa2 * data.d2dz_csa2_dO2+1.5 * data.dz_csa1**2 * data.dz_csa2 * data.d2dz_csa2_dO2+1.5 * cobeta * data.dz_csa1 * data.dz_csa2**2 * data.d2dz_csa1_dO2+1.5 * data.dz_csa1 * data.dz_csa2**2 * data.d2dz_csa1_dO2+1.5 * data.dy_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2+1.5 * cobeta * data.dx_csa1**2 * data.dy_csa2 * data.d2dy_csa2_dO2+1.5 * data.dy_csa1 * data.dy_csa2**2 * data.d2dy_csa1_dO2+1.5 * cobeta * data.dx_csa2**2 * data.dy_csa1 * data.d2dy_csa1_dO2+1.5 * cobeta * data.dx_csa2 * data.dy_csa1**2 * data.d2dx_csa2_dO2+1.5 * data.dx_csa1**2 * data.dx_csa2 * data.d2dx_csa2_dO2+1.5 * cobeta * data.dx_csa1 * data.dy_csa2**2 * data.d2dx_csa1_dO2+1.5 * data.dx_csa1 * data.dx_csa2**2 * data.d2dx_csa1_dO2+1.5 * cobeta * op_z1z1_csaC * data.dz_csa2**2+1.5 * op_z1z1_csaC * data.dz_csa2**2+3.0 * cobeta * op_z1z2_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_z1z2_csaC * data.dz_csa1 * data.dz_csa2+3.0 * cobeta * op_z2z1_csaC * data.dz_csa1 * data.dz_csa2+3.0 * op_z2z1_csaC * data.dz_csa1 * data.dz_csa2+1.5 * cobeta * op_z2z2_csaC * data.dz_csa1**2+1.5 * op_z2z2_csaC * data.dz_csa1**2+1.5 * op_y1y1_csaC * data.dy_csa2**2+1.5 * cobeta * op_x1x1_csaC * data.dy_csa2**2+3.0 * op_y1y2_csaC * data.dy_csa1 * data.dy_csa2+3.0 * op_y2y1_csaC * data.dy_csa1 * data.dy_csa2+3.0 * cobeta * op_x1y2_csaC * data.dx_csa1 * data.dy_csa2+3.0 * cobeta * op_y2x1_csaC * data.dx_csa1 * data.dy_csa2+1.5 * op_y2y2_csaC * data.dy_csa1**2+1.5 * cobeta * op_x2x2_csaC * data.dy_csa1**2+3.0 * cobeta * op_x2y1_csaC * data.dx_csa2 * data.dy_csa1+3.0 * cobeta * op_y1x2_csaC * data.dx_csa2 * data.dy_csa1+1.5 * cobeta * op_y1y1_csaC * data.dx_csa2**2+1.5 * op_x1x1_csaC * data.dx_csa2**2+3.0 * op_x1x2_csaC * data.dx_csa1 * data.dx_csa2+3.0 * op_x2x1_csaC * data.dx_csa1 * data.dx_csa2+1.5 * cobeta * op_y2y2_csaC * data.dx_csa1**2+1.5 * op_x2x2_csaC * data.dx_csa1**2


    # Oi-Dr partial derivative.
    #############################
    # Weight c2.
    data.d2ci_csaC[3:, 2, 4] = 0.25 * (9 * diff_data.params[2] * (2 * data.dz_csa1**2 * data.dz_csa2 * data.ddz_csa2_dO+2 * data.dz_csa1 * data.dz_csa2**2 * data.ddz_csa1_dO+2 * data.dx_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO+2 * data.dx_csa2**2 * data.dy_csa1 * data.ddy_csa1_dO+2 * data.dx_csa2 * data.dy_csa1**2 * data.ddx_csa2_dO+2 * data.dx_csa1 * data.dy_csa2**2 * data.ddx_csa1_dO)/(3 * diff_data.params[2]**2+1)**(3/2)-3 * (6 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO-2 * data.dy_csa2 * data.ddy_csa2_dO+6 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO-2 * data.dy_csa1 * data.ddy_csa1_dO-6 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2 * data.dx_csa2 * data.ddx_csa2_dO-6 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO+2 * data.dx_csa1 * data.ddx_csa1_dO)/sqrt(3 * diff_data.params[2]**2+1)+9 * diff_data.params[2]**2 * (6 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO-2 * data.dy_csa2 * data.ddy_csa2_dO+6 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO-2 * data.dy_csa1 * data.ddy_csa1_dO-6 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2 * data.dx_csa2 * data.ddx_csa2_dO-6 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO+2 * data.dx_csa1 * data.ddx_csa1_dO)/(3 * diff_data.params[2]**2+1)**(3/2))
    
    # Weight c-2.
    data.d2ci_csaC[3:, 2, 0] = 0.25 * (-9 * diff_data.params[2] * (2 * data.dz_csa1**2 * data.dz_csa2 * data.ddz_csa2_dO+2 * data.dz_csa1 * data.dz_csa2**2 * data.ddz_csa1_dO+2 * data.dx_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO+2 * data.dx_csa2**2 * data.dy_csa1 * data.ddy_csa1_dO+2 * data.dx_csa2 * data.dy_csa1**2 * data.ddx_csa2_dO+2 * data.dx_csa1 * data.dy_csa2**2 * data.ddx_csa1_dO)/(3 * diff_data.params[2]**2+1)**(3/2)+3 * (6 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO-2 * data.dy_csa2 * data.ddy_csa2_dO+6 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO-2 * data.dy_csa1 * data.ddy_csa1_dO-6 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2 * data.dx_csa2 * data.ddx_csa2_dO-6 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO+2 * data.dx_csa1 * data.ddx_csa1_dO)/sqrt(3 * diff_data.params[2]**2+1)-9 * diff_data.params[2]**2 * (6 * data.dy_csa1**2 * data.dy_csa2 * data.ddy_csa2_dO-2 * data.dy_csa2 * data.ddy_csa2_dO+6 * data.dy_csa1 * data.dy_csa2**2 * data.ddy_csa1_dO-2 * data.dy_csa1 * data.ddy_csa1_dO-6 * data.dx_csa1**2 * data.dx_csa2 * data.ddx_csa2_dO+2 * data.dx_csa2 * data.ddx_csa2_dO-6 * data.dx_csa1 * data.dx_csa2**2 * data.ddx_csa1_dO+2 * data.dx_csa1 * data.ddx_csa1_dO)/(3 * diff_data.params[2]**2+1)**(3/2))



    # Dr-Dr partial derivative.
    ###########################

    # Weight c2.
    data.d2ci_csaC[2, 2, 4] = 0.25 * (-3 * (1-3 * (data.dz_csa1**2 * data.dz_csa2**2+data.dx_csa1**2 * data.dy_csa2**2+data.dx_csa2**2 * data.dy_csa1**2))/(3 * diff_data.params[2]**2+1)**(3/2)+27 * diff_data.params[2]**2 * (1-3 * (data.dz_csa1**2 * data.dz_csa2**2+data.dx_csa1**2 * data.dy_csa2**2+data.dx_csa2**2 * data.dy_csa1**2))/(3 * diff_data.params[2]**2+1)**(5/2)+27 * diff_data.params[2] * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/(3 * diff_data.params[2]**2+1)**(3/2)-81 * diff_data.params[2]**3 * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/(3 * diff_data.params[2]**2+1)**(5/2))

    # Weight c-2.
    data.d2ci_csaC[2, 2, 0] = 0.25 * (3 * (1-3 * (data.dz_csa1**2 * data.dz_csa2**2+data.dx_csa1**2 * data.dy_csa2**2+data.dx_csa2**2 * data.dy_csa1**2))/(3 * diff_data.params[2]**2+1)**(3/2)-27 * diff_data.params[2]**2 * (1-3 * (data.dz_csa1**2 * data.dz_csa2**2+data.dx_csa1**2 * data.dy_csa2**2+data.dx_csa2**2 * data.dy_csa1**2))/(3 * diff_data.params[2]**2+1)**(5/2)-27 * diff_data.params[2] * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/(3 * diff_data.params[2]**2+1)**(3/2)+81 * diff_data.params[2]**3 * (3 * data.dy_csa1**2 * data.dy_csa2**2-data.dy_csa2**2-data.dy_csa1**2-3 * data.dx_csa1**2 * data.dx_csa2**2+data.dx_csa2**2+data.dx_csa1**2)/(3 * diff_data.params[2]**2+1)**(5/2))
