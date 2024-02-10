from PIL import Image
import glob
import os
import io
import numpy
 
from wand.image import Image as imgur # https://imagemagick.org/script/download.php#windows

targetwidth = 400
locationx = 0
locationy = 500
distortion = False
fov = 90 

dirname = os.path.dirname(os.path.realpath(__file__)).replace(os.sep, '/')
backgroundFolder =  dirname + "/Background/*"
foregroundFolder = dirname + '/Foreground/*'
outputFolder = dirname + "/Results"

backgroundlist = [Image.open(file) for file in glob.glob(backgroundFolder)]
foregroundlist = []

for file in glob.glob(foregroundFolder):
    img = Image.open(file)
    originalw, originalh = img.size
    factor = originalw / targetwidth
    print(factor)
    img = img.resize((targetwidth, int(originalh / factor)), resample=Image.BOX).convert("RGBA") #diese zeile droppt den filename ??
    img.save("esGehtNichtNochUneleganter.png")
    
    if distortion:
        with imgur(filename="esGehtNichtNochUneleganter.png") as img:
            img.background_color = "transparent"
            img.virtual_pixel = 'background'
            img.distort('plane_2_cylinder', (fov, originalw /2, originalh/2))
            #img.save(filename ='gogdistort1.png')
            img_buffer=numpy.asarray(bytearray(img.make_blob()), dtype=numpy.uint8)
        bytesio = io.BytesIO(img_buffer)
        img = Image.open(bytesio)
    foregroundlist.append(img)


counter = 1
for bg in backgroundlist:
    for fg in foregroundlist:
        name = counter
        counter += 1
        erg = bg.copy()
        try:
            erg.paste(fg, (locationx, locationy), fg.split()[3])
            erg.save(outputFolder+ "/" + str(name) + ".jpg")
        except:
            erg.paste(fg, (locationx, locationy), fg)
            erg.save(outputFolder+ "/" + str(name) + ".png")
        

