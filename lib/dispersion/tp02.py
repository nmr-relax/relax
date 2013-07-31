###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
# Copyright (C) 2013 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""This Trott and Palmer (2002) 2-site exchange R1rho model.

The code originates as the funTrottPalmer.m Matlab file from the sim_all.tar file attached to task #7712 (https://gna.org/task/?7712).  This is code from Nikolai Skrynnikov and Martin Tollinger.

Links to the copyright licensing agreements from all authors are:

    - Nikolai Skrynnikov, http://article.gmane.org/gmane.science.nmr.relax.devel/4279
    - Martin Tollinger, http://article.gmane.org/gmane.science.nmr.relax.devel/4276
"""

function residual = funTrottPalmer(optpar)

% TrottPalmer's equ. acc. to Korzhnev (JBiomolNMR, 26, 39-48, 2003)

global nu_0 x y Rcalc rms nfields offset w1 R1_51 R1_81
%keyboard
Rcalc=zeros(nfields,size(w1,2));
tau_ex=optpar(1);
pb=optpar(2);
pa=1-pb;
kex=1/tau_ex;

for k=1:nfields
    % we assume that A resonates at 0 [s^-1], without loss of generality
    dw=nu_0(k)*optpar(3)*2*pi;   	% [s^-1]
    Wa=0*2*pi;             		% Larmor frequ. [s^-1]
    Wb=dw;         			% Larmor frequ. [s^-1]
    Wsl=offset*2*pi;   			% Larmor frequ. of spin lock [s^-1]
    W=pa*Wa+pb*Wb;			% pop-averaged Larmor frequ. [s^-1]
    da=Wa-Wsl;				% offset of sl from A
    db=Wb-Wsl;				% offset of sl from B
    d =W -Wsl; 				% offset of sl from pop-average
    waeff2=w1.^2+da.^2;			% effective field at A
    wbeff2=w1.^2+db.^2;			% effective field at B
    weff2=w1.^2+d.^2;			% effective field at pop-average
    theta=atan(w1/d);
    theta_degrees=atan(w1/d)*360/(2*pi);	% not used, just to check

    Rinf=optpar(3+k);
    xx=pa*pb*dw^2*kex;
    yytrottpalmer=waeff2.*wbeff2./weff2+kex^2;
    yytrottpalmer_extended=waeff2.*wbeff2./weff2+kex^2-2*(sin(theta).^2)*pa*pb*dw^2;
 
    %keyboard
   if k==1; 
   Rcalc(k,:)=(cos(theta).^2)*R1_51+(sin(theta).^2)*(Rinf)+(sin(theta).^2).*xx./yytrottpalmer_extended;
   end
   if k==2; 
   Rcalc(k,:)=(cos(theta).^2)*R1_81+(sin(theta).^2)*(Rinf)+(sin(theta).^2).*xx./yytrottpalmer_extended;
   end


end

if (size(Rcalc)==size(y))
    residual=sum(sum((y-Rcalc).^2)); 
    rms=sqrt(residual/(size(y,1)*size(y,2)));
end

