#! /bin/bash
# Animación de imagenes GLM sobre CONUS
# (C) 2019 Alejandro Aguilar Sierra <asierra@unam.mx>
# Laboratorio Nacional de Observación de la Tierra, UNAM

DAYS=2
RATE=100
SCALE=720
OUTFPS=100

origdir=/data/goes16/glm/vistas/conus
outdir=/var/www/html/animations/glm

# Siempre usa un directorio de trabajo local
# procesar archivos en un directorio remoto
# aumenta innecesariamente el tráfico en la red
# y el trabajo en el disco del servidor remoto.
workingdir=/var/tmp/video_glm_conus

if [ ! -d $workingdir ]
then
        echo "Creando directorio de trabajo $workingdir"
        mkdir -p $workingdir
fi

cd $workingdir
rm -rf *

# ls por omisión genera una lista ordenada 
# de los nombres de los archivos
count=0
for i in `find $origdir -type f -mtime -$DAYS|sort`
do
	printf -v out "%06d.png" $count
#        ln -s $origdir/$i $out
        ln -s $i $out
        ((count++))
done

ffmpeg -framerate $RATE -pattern_type sequence -i %06d.png \
	-an -vcodec libx264 -r $OUTFPS -pix_fmt yuv420p -profile:v baseline \
        -level 3 -vf scale=-1:$SCALE -crf 30 -y out.mp4

if [ -f $outdir/lastest.mp4 ]; then
    mv $outdir/lastest.mp4 $outdir/previous.mp4
fi

mv out.mp4 $outdir/lastest.mp4

