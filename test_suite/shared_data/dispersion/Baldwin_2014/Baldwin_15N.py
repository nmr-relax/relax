#!/usr/bin/python
###############################################################################
#                                                                             #
# Copyright (C) 2014 Andrew Baldwin (andrew.baldwin@chem.ox.ac.uk),           #
# University of Oxford                                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

######################################################################
# Script to simulate R2eff from a CPMG experiment
#
# Note assumption of only inphase magnetisation and 2 site exchange
# only. 
#
# Requires numpy.
#
#
#
 
import numpy
from math import cos, sin, atan2
g1H = 26.7522212 * 1e7
g15N = -2.7126 * 1e7

############################################################################
#Note dw is in rad s-1.
def BaldDisp(kex, pb, dw, ncyc, Trel, R2g, R2e, outfile):
    pa=(1-pb)
    keg=kex*(1-pb)
    kge=kex*pb
    deltaR2=R2e-R2g
    nu_cpmg=ncyc/Trel
    tcp=Trel/(4.0*ncyc)  #time for one free precession element
    #########################################################################
    #get the real and imaginary components of the exchange induced shift
    g1=2*dw*(deltaR2+keg-kge)                   #same as carver richards zeta
    g2=(deltaR2+keg-kge)**2.0+4*keg*kge-dw**2   #same as carver richards psi
    g3=cos(0.5*atan2(g1, g2))*(g1**2.0+g2**2.0)**(1/4.0)   #trig faster than square roots
    g4=sin(0.5*atan2(g1, g2))*(g1**2.0+g2**2.0)**(1/4.0)   #trig faster than square roots
    #########################################################################
    #time independent factors
    N=complex(kge+g3-kge, g4)            #N=oG+oE
    NNc=(g3**2.+g4**2.)
    f0=(dw**2.+g3**2.)/(NNc)              #f0
    f2=(dw**2.-g4**2.)/(NNc)              #f2
    #t1=(-dw+g4)*(complex(-dw,-g3))/(NNc) #t1
    t2=(dw+g4)*(complex(dw, -g3))/(NNc) #t2
    t1pt2=complex(2*dw**2., -g1)/(NNc)     #t1+t2
    oGt2=complex((deltaR2+keg-kge-g3), (dw-g4))*t2  #-2*oG*t2
    Rpre=(R2g+R2e+kex)/2.0   #-1/Trel*log(LpreDyn)
    E0= 2.0*tcp*g3  #derived from relaxation       #E0=-2.0*tcp*(f00R-f11R)
    E2= 2.0*tcp*g4  #derived from chemical shifts  #E2=complex(0,-2.0*tcp*(f00I-f11I))
    E1=(complex(g3, -g4))*tcp    #mixed term (complex) (E0-iE2)/2
    ex0b=(f0*numpy.cosh(E0)-f2*numpy.cos(E2))               #real
    ex0c=(f0*numpy.sinh(E0)-f2*numpy.sin(E2)*complex(0, 1.)) #complex
    ex1c=(numpy.sinh(E1))                                   #complex
    v3=numpy.sqrt(ex0b**2.-1)  #exact result for v2v3
    y=numpy.power((ex0b-v3)/(ex0b+v3), ncyc)
    v2pPdN=(( complex(deltaR2+kex, dw) )*ex0c+(-oGt2-kge*t1pt2)*2*ex1c)        #off diagonal common factor. sinh fuctions
    Tog=(((1+y)/2+(1-y)/(2*v3)*(v2pPdN)/N))     
    Minty=Rpre-ncyc/(Trel)*numpy.arccosh((ex0b).real)-1/Trel*numpy.log((Tog.real))  #estimate R2eff

    array=[]
    for i in range(len(ncyc)):
        array.append((nu_cpmg[i], Minty[i]))
    if(outfile!='Null'):
        outy=open(outfile, 'w')
        for i in range(len(array)):
            outy.write('%f\t%f\n' % (array[i][0], array[i][1]))
        outy.close()
    return array


def ppm_to_rads(ppm, dfrq):
    return ppm*2*numpy.pi*dfrq* g15N/g1H


if __name__ == "__main__":  #run this if this file is run as standalone
    #otherwise use the function form your own code.
    outfile='test_15N.out'  #set to 'Null' if output is not required
    kex=1000.  #exchange rate = k+ + k- (s-1)
    pb=0.01    #fractional population of excited state k+/kex
    dw_ppm=2.  #deltaOmega in ppm
    dfrq=200.  #spectrometer frequency of nucleci (MHz) 
    ncyc=numpy.array((2, 4, 8, 10, 20, 40, 500,)) #number of cpmg cycles (1 cycle = delay/180/delay/delay/180/delay)
    R2g=2.     #relaxation rate of ground (s-1)
    R2e=100.   #relaxation rate of excited (s-1)
    Trelax=0.04 #total time of CPMG block
    BaldDisp(kex, pb, ppm_to_rads(dw_ppm, dfrq), ncyc, Trelax, R2g, R2e, outfile)
