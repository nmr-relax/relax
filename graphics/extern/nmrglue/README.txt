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
convert -background none -blur 20x20 -interpolative-resize 16x16 -set option:distort:viewport "%[fx:max(w,h)]x%[fx:max(w,h)]-%[fx:max((h-w)/2,0)]-%[fx:max((w-h)/2,0)]" -filter point -distort SRT 0 +repage nmrglue_logo.svg ../../relax_icons/16x16/nmrglue_logo.png
#inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
#inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
#gzip ${s}x${s}/nmrglue_logo.eps

set s=22
mkdir -p ${s}x${s}
convert -background none -blur 10x10 -interpolative-resize 22x22 -set option:distort:viewport "%[fx:max(w,h)]x%[fx:max(w,h)]-%[fx:max((h-w)/2,0)]-%[fx:max((w-h)/2,0)]" -filter point -distort SRT 0 +repage nmrglue_logo.svg ../../relax_icons/22x22/nmrglue_logo.png
#inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
#inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
#gzip ${s}x${s}/nmrglue_logo.eps


set s=32
mkdir -p ${s}x${s}
convert -background none -blur 9x9 -interpolative-resize 32x32 -set option:distort:viewport "%[fx:max(w,h)]x%[fx:max(w,h)]-%[fx:max((h-w)/2,0)]-%[fx:max((w-h)/2,0)]" -filter point -distort SRT 0 +repage nmrglue_logo.svg ../../relax_icons/32x32/nmrglue_logo.png
#inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
#inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
#gzip ${s}x${s}/nmrglue_logo.eps

set s=48
mkdir -p ${s}x${s}
convert -background none -blur 5x5 -interpolative-resize 48x48 -set option:distort:viewport "%[fx:max(w,h)]x%[fx:max(w,h)]-%[fx:max((h-w)/2,0)]-%[fx:max((w-h)/2,0)]" -filter point -distort SRT 0 +repage nmrglue_logo.svg ../../relax_icons/48x48/nmrglue_logo.png
#inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
#inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
#gzip ${s}x${s}/nmrglue_logo.eps

set s=128
mkdir -p ${s}x${s}
convert -background none -blur 2x2 -interpolative-resize 128x128 -set option:distort:viewport "%[fx:max(w,h)]x%[fx:max(w,h)]-%[fx:max((h-w)/2,0)]-%[fx:max((w-h)/2,0)]" -filter point -distort SRT 0 +repage nmrglue_logo.svg ../../relax_icons/128x128/nmrglue_logo.png
#inkscape -z -e ${s}x${s}/nmrglue_logo.png -w ${s} -h ${s} nmrglue_logo.svg
#inkscape -z -E ${s}x${s}/nmrglue_logo.eps -w ${s} -h ${s} nmrglue_logo.svg
#gzip ${s}x${s}/nmrglue_logo.eps
