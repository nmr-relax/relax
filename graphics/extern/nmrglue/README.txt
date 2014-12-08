Images created after discussion:
http://thread.gmane.org/gmane.science.nmr.relax.devel/7321

Namely on:
http://thread.gmane.org/gmane.science.nmr.relax.devel/7391

wget https://github.com/jjhelmus/nmrglue_logo/archive/master.zip
unzip master.zip
rm master.zip
mv nmrglue_logo-master/* .
rmdir nmrglue_logo-master

# Make 200x wide
inkscape -z -e nmrglue_logo_200x.png -w 200 nmrglue_logo.svg
inkscape -z -E nmrglue_logo_200x.eps -w 200 nmrglue_logo.svg
gzip nmrglue_logo_200x.eps

set s=16
mkdir -p ${s}x${s}
inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
gzip ${s}x${s}/nmrglue_logo.eps

set s=22
mkdir -p ${s}x${s}
inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
gzip ${s}x${s}/nmrglue_logo.eps


set s=32
mkdir -p ${s}x${s}
inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
gzip ${s}x${s}/nmrglue_logo.eps

set s=48
mkdir -p ${s}x${s}
inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
gzip ${s}x${s}/nmrglue_logo.eps

set s=128
mkdir -p ${s}x${s}
inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
gzip ${s}x${s}/nmrglue_logo.eps
