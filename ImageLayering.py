from PIL import Image
import glob
import os
import io
import numpy
import Util.Util as Util
import logging
import configparser
 
from wand.image import Image as imgur # https://imagemagick.org/script/download.php#windows

config = configparser.ConfigParser()
config.read("config.ini")

targetwidth = int(config["Default"]["BreiteDesGelayertenBilds"])
locationx = int(config["Default"]["XWertDesGelayertenBilds"])
locationy = int(config["Default"]["YWertDesGelayertenBilds"])
distortion = Util.str2bool(config["Default"]["VerzerrungEingeschaltet"])
fov = int(config["Default"]["VerzerrungsFaktor"])
grenzwertR = int(config["Default"]["grenzwertR"])
grenzwertG = int(config["Default"]["grenzwertG"]) 
grenzwertB = int(config["Default"]["grenzwertB"])

logging.basicConfig(filename="Errorlog.log", level=logging.INFO)

dirname = os.path.dirname(os.path.realpath(__file__)).replace(os.sep, '/')
backgroundFolder =  dirname + "/Background/*"
foregroundFolder = dirname + '/Foreground/*'
outputFolder = dirname + "/Results"

backgroundlist = [Image.open(file) for file in glob.glob(backgroundFolder)]
foregroundlist = []

for file in glob.glob(foregroundFolder):
    img = Image.open(file)
    name = img.filename
    img = img.convert("RGBA")
    try:
        img = Util.crop(img)
    except Exception as error:
        logging.error("problem beim zuschneiden des bilds mit dem namen: " + name + ", evtl kein schwarz im bild vorhanden?" + str(error))
        print("problem beim zuschneiden des bilds mit dem namen: " + name + ", evtl kein schwarz im bild vorhanden?")
        print(+ str(error))
    try:
        img = Util.tranparent(img, grenzwertR, grenzwertG, grenzwertB)
    except Exception as error:
        logging.error("problem beim transparentisieren des bilds mit dem namen: " + name + str(error))
        print("problem beim transparentisieren des bilds mit dem namen: " + name)
        print(+ str(error))
    originalw, originalh = img.size
    factor = originalw / targetwidth
    try:
        img = img.resize((targetwidth, int(originalh / factor)), resample=Image.BOX) #diese zeile droppt den filename ??
    except Exception as error:
        logging.error("problem beim resizen des bilds mit dem namen: " + name + str(error))
        print("problem beim resizen des bilds mit dem namen: " + name)
        print(+ str(error))
    img.save("Background/esGehtNichtNochUneleganter.png")
    
    if distortion:
        try:
            with imgur(filename="Background/esGehtNichtNochUneleganter.png") as img:
                img.background_color = "transparent"
                img.virtual_pixel = 'background'
                
                img.distort('plane_2_cylinder', (fov, originalw /2, originalh/2))
                #img.save(filename ='gogdistort1.png')
                img_buffer=numpy.asarray(bytearray(img.make_blob()), dtype=numpy.uint8)
            bytesio = io.BytesIO(img_buffer)
            img = Image.open(bytesio)
        except Exception as error:
            logging.error("problem beim zerren des bilds mit dem namen: " + str(error))
            print("problem beim zerren des bilds mit dem namen: " + name)
            print(+ str(error))
    foregroundlist.append(img)


counter = 1
for bg in backgroundlist:
    for fg in foregroundlist:
        name = counter
        counter += 1
        erg = bg.copy()
        try:
            try:
                erg.paste(fg, (locationx, locationy), fg.split()[3])
                erg.save(outputFolder+ "/" + str(name) + ".jpg")
            except:
                erg.paste(fg, (locationx, locationy), fg)
                erg.save(outputFolder+ "/" + str(name) + ".png")
        except Exception as error:
            logging.error("problem beim Layern des bilds mit dem namen: " + name)
            print("problem beim layern des bilds mit dem namen: " + name)
            print(+ str(error))
        

