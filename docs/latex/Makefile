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
.PHONY: manual
manual:
	make clean
	make version
	make fetch_docstrings
	make latex
	make move
	make acro


# Create the PDF manual without fetching the docstrings.
.PHONY: manual_nofetch
manual_nofetch:
	make clean
	make version
	make latex
	make move
	make acro


# Create the PDF manual for distribution (remember to add make fetch_docstrings).
.PHONY: manual_dist
manual_dist:
	make clean
	make version
	make fetch_docstrings
	make latex
	make move
	make clean


# Create the HTML manual.
.PHONY: manual_html
manual_html:
	make clean
	latex2html -split +3 -html_version 4.0 -dir ../html relax.tex


# Clean up the temporary manual files.
.PHONY: clean
clean:
	@echo -e "\n\n\n <<< Cleaning up the temporary manual files >>>\n\n\n"
	rm -f *.aux
	rm -f relax.bbl
	rm -f relax.blg
	rm -f relax.dvi
	rm -f relax.idx
	rm -f relax.ilg
	rm -f relax.ind
	rm -f relax.lof
	rm -f relax.log
	rm -f relax.lot
	rm -f relax.toc


# Rule for getting the program version.
.PHONY: version
version:
	@echo -e "\n\n\n <<< Getting the relax version number >>>\n"
	./version


# Rule for getting the docstrings.
.PHONY: fetch_docstrings
fetch_docstrings:
	@echo -e "\n\n\n <<< Fetching the docstrings >>>\n\n\n"
	./fetch_docstrings


# Rule for compiling the LaTeX into the PDF file.
.PHONY: latex
latex:
	@echo -e "\n\n\n <<< LaTeX (first round) >>>\n\n\n"
	latex relax.tex
	
	@echo -e "\n\n\n <<< Bibtex >>>\n\n\n"
	bibtex relax.aux
	
	@echo -e "\n\n\n <<< Makeindex >>>\n\n\n"
	makeindex relax.idx
	
	@echo -e "\n\n\n <<< LaTeX (second round) >>>\n\n\n"
	latex relax.tex
	
	@echo -e "\n\n\n <<< LaTeX (third round) >>>\n\n\n"
	latex relax.tex
	
	@echo -e "\n\n\n <<< dvips >>>\n\n\n"
	dvips -o relax.ps relax.dvi
	
	@echo -e "\n\n\n <<< ps2pdf >>>\n\n\n"
	ps2pdf -dAutoFilterColorImages=false -dAutoFilterGrayImages=false -dColorImageFilter=/FlateEncode -dColorImageFilter=/FlateEncode -dGrayImageFilter=/FlateEncode -dMonoImageFilter=/FlateEncode -dPDFSETTINGS=/prepress relax.ps


# Rule for post LaTeX compilation.
.PHONY: move
move:
	@echo -e "\n\n\n <<< Removing the PS file and shifting the PDF down a directory >>>\n\n\n"
	rm -f relax.ps
	mv -f relax.pdf ..


# Rule for running Adobe Acrobat Reader with the PDF manual.
.PHONY: acro
acro:
	@echo -e "\n\n\n <<< acroread >>>\n\n\n"
	acroread -openInNewWindow ../relax.pdf &
