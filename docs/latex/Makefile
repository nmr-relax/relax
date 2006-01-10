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


# Create the PDF manual.
manual :
	@echo -e "\n\n\n <<< Clean >>>\n\n\n"
	rm -f *.aux relax.bbl relax.blg relax.dvi relax.idx relax.ilg relax.ind relax.lof relax.log relax.lot relax.pdf relax.toc
	
	@echo -e "\n\n\n <<< Getting the relax version number >>>\n"
	./version
	
	@echo -e "\n\n\n <<< Fetching the docstrings >>>\n\n\n"
	#./fetch_docstrings
	
	@echo -e "\n\n\n <<< Latex (first round) >>>\n\n\n"
	latex relax.tex
	
	@echo -e "\n\n\n <<< Bibtex >>>\n\n\n"
	bibtex relax.aux
	
	@echo -e "\n\n\n <<< Makeindex >>>\n\n\n"
	makeindex relax.idx
	
	@echo -e "\n\n\n <<< Latex (second round) >>>\n\n\n"
	latex relax.tex
	
	@echo -e "\n\n\n <<< Latex (third round) >>>\n\n\n"
	latex relax.tex
	
	@echo -e "\n\n\n <<< dvips >>>\n\n\n"
	dvips -o relax.ps relax.dvi
	
	@echo -e "\n\n\n <<< ps2pdf >>>\n\n\n"
	#ps2pdf relax.ps
	ps2pdf -dAutoFilterColorImages=false -dAutoFilterGrayImages=false -dColorImageFilter=/FlateEncode -dColorImageFilter=/FlateEncode -dGrayImageFilter=/FlateEncode -dMonoImageFilter=/FlateEncode -dPDFSETTINGS=/prepress relax.ps
	
	@echo -e "\n\n\n <<< Removing the PS file and shifting the PDF down a directory >>>\n\n\n"
	rm -f relax.ps
	mv -f relax.pdf ..
	
	@echo -e "\n\n\n <<< acroread >>>\n\n\n"
	acroread -openInNewWindow ../relax.pdf &


# Create the HTML manual.
manual_html :
	latex2html -split +3 -html_version 4.0 -dir ../html relax.tex
