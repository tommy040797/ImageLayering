from PIL import Image
import glob
import os
import io
import numpy as np
import Util.Util as Util
import logging
import configparser
import cv2 as cv

from wand.image import (
    Image as imgur,
)  # https://imagemagick.org/script/download.php#windows

config = configparser.ConfigParser()
config.read("config.ini")

finalheight = int(config["Default"]["FinaleHoeheDesBilds"])
targetwidth = int(config["Default"]["BreiteDesGelayertenBilds"])
targetwidthsecond = int(config["Default"]["BreiteDesZweitenBilds"])
zweitebild = Util.str2bool(config["Default"]["ZweitesBild"])
locationzweitex = int(config["Default"]["XWertDesZweitenBilds"])
locationzweitey = int(config["Default"]["YWertDesZweitenBilds"])
locationx = int(config["Default"]["XWertDesGelayertenBilds"])
locationy = int(config["Default"]["YWertDesGelayertenBilds"])
trimmen = Util.str2bool(config["Default"]["SkalierenEingeschaltet"])
skalieren = Util.str2bool(config["Default"]["TrimmenEingeschaltet"])
distortion = Util.str2bool(config["Default"]["VerzerrungEingeschaltet"])
transparenz = Util.str2bool(config["Default"]["TransparenzEingeschaltet"])
farbe = Util.str2bool(config["Default"]["VordergrundFarbeAendern"])
farber = int(config["Default"]["VordergrundR"])
farbeb = int(config["Default"]["VordergrundB"])
farbeg = int(config["Default"]["VordergrundG"])
farbealpha = int(config["Default"]["AlphawertVordergrund"])
fov = int(config["Default"]["VerzerrungsFaktor"])
grenzwertR = int(config["Default"]["grenzwertR"])
grenzwertG = int(config["Default"]["grenzwertG"])
grenzwertB = int(config["Default"]["grenzwertB"])
backgroundalpha = int(config["Default"]["ForegroundAlpha"])
customTexture = Util.str2bool(config["Default"]["CustomVordergrundTextur"])

logging.basicConfig(filename="Errorlog.log", level=logging.INFO)

dirname = os.path.dirname(os.path.realpath(__file__)).replace(os.sep, "/")
backgroundFolder = dirname + "/Background/*"
foregroundFolder = dirname + "/Foreground/*"
textureFolder = dirname + "/Textures/*"
outputFolder = dirname + "/Results"

backgroundlist = [Image.open(file) for file in glob.glob(backgroundFolder)]
foregroundlist = []
preforegroundlist = []
texturelist = [Image.open(file) for file in glob.glob(textureFolder)]


if customTexture:
    for file in glob.glob(foregroundFolder):
        img = Image.open(file)
        name = img.filename
        img = img.convert("RGBA")

        if trimmen:
            try:
                img = Util.crop(img)
            except Exception as error:
                logging.error(
                    "problem beim zuschneiden des bilds mit dem namen: "
                    + name
                    + ", evtl kein schwarz im bild vorhanden?"
                    + str(error)
                )
                print(
                    "problem beim zuschneiden des bilds mit dem namen: "
                    + name
                    + ", evtl kein schwarz im bild vorhanden?"
                )
                print(+str(error))
        originalw, originalh = img.size
        factor = originalw / targetwidth
        if skalieren:
            try:
                img = img.resize(
                    (targetwidth, int(originalh / factor)), resample=Image.BOX
                )  # diese zeile droppt den filename ??
            except Exception as error:
                logging.error(
                    "problem beim resizen des bilds mit dem namen: " + name + str(error)
                )
                print("problem beim resizen des bilds mit dem namen: " + name)
                print(+str(error))
        img = Util.replaceTexturePrep(img)
        img = Util.imageTransparentPattern(img)
        for file in glob.glob(textureFolder):
            textur = Image.open(file)
            textur = textur.convert("RGBA")
            textur.paste(img, (locationx, locationy), img)

            w, h = img.size
            box = (locationx, locationy, locationx + w, locationy + h)
            textur = textur.crop(box)
            textur = np.array(textur)
            textur = cv.dilate(textur, (5, 5), iterations=1)
            textur = Image.fromarray(textur)
            preforegroundlist.append(textur)

    for img in preforegroundlist:
        if transparenz:
            try:
                img = Util.whiteTranparent(img)
            except Exception as error:
                logging.error(
                    "problem beim transparentisieren des bilds mit dem namen: "
                    + str(error)
                )
                print("problem beim transparentisieren des bilds mit dem namen: ")
                print(+str(error))
        foregroundlist.append(img)


if not customTexture:
    for file in glob.glob(foregroundFolder):
        img = Image.open(file)
        name = img.filename
        img = img.convert("RGBA")

        if trimmen:
            try:
                img = Util.crop(img)
            except Exception as error:
                logging.error(
                    "problem beim zuschneiden des bilds mit dem namen: "
                    + name
                    + ", evtl kein schwarz im bild vorhanden?"
                    + str(error)
                )
                print(
                    "problem beim zuschneiden des bilds mit dem namen: "
                    + name
                    + ", evtl kein schwarz im bild vorhanden?"
                )
                print(+str(error))
        if farbe:
            try:
                img = Util.farbe(img, farber, farbeb, farbeg, farbealpha)
            except Exception as error:
                logging.error(
                    "problem beim Farbe verändern des Vordergrunds des bilds mit dem namen: "
                    + name
                    + str(error)
                )
                print(
                    "problem beim Farbe verändern des Vordergrunds  des bilds mit dem namen: "
                    + name
                )
                print(+str(error))

        if transparenz:
            try:
                img = Util.tranparent(
                    img, grenzwertR, grenzwertG, grenzwertB, backgroundalpha
                )
            except Exception as error:
                logging.error(
                    "problem beim transparentisieren des bilds mit dem namen: "
                    + name
                    + str(error)
                )
                print(
                    "problem beim transparentisieren des bilds mit dem namen: " + name
                )
                print(+str(error))

        originalw, originalh = img.size
        factor = originalw / targetwidth

        if skalieren:
            try:
                img = img.resize(
                    (targetwidth, int(originalh / factor)), resample=Image.BOX
                )  # diese zeile droppt den filename ??
            except Exception as error:
                logging.error(
                    "problem beim resizen des bilds mit dem namen: " + name + str(error)
                )
                print("problem beim resizen des bilds mit dem namen: " + name)
                print(+str(error))
            img.save("Util/esGehtNichtNochUneleganter.png")

        foregroundlist.append(img)


counter = 1
for bg in backgroundlist:
    for fg in foregroundlist:
        if distortion:
            fg.save("Util/esGehtNichtNochUneleganter.png")
            try:
                with imgur(filename="Util/esGehtNichtNochUneleganter.png") as img:
                    img.background_color = "transparent"
                    img.virtual_pixel = "background"
                    img.distort("plane_2_cylinder", (fov, originalw / 2, originalh / 2))
                    img_buffer = np.asarray(bytearray(img.make_blob()), dtype=np.uint8)
                bytesio = io.BytesIO(img_buffer)
                img = Image.open(bytesio)
            except Exception as error:
                logging.error(
                    "problem beim zerren des bilds mit dem namen: " + str(error)
                )
                print("problem beim zerren des bilds mit dem namen: ")
                print(+str(error))
        else:
            img = fg
        name = counter
        counter += 1
        erg = bg.copy()
        try:
            erg.paste(img, (locationx, locationy), img)
            if zweitebild:
                originalw, originalh = fg.size
                factor = originalw / targetwidthsecond
                fg = fg.resize(
                    (targetwidthsecond, int(originalh / factor)), resample=Image.BOX
                )
                erg.paste(fg, (locationzweitex, locationzweitey), fg)
            originalw, originalh = erg.size
            factor = originalh / finalheight
            erg = erg.resize(
                (int(originalw / factor), finalheight),
                resample=Image.BOX,
            )  # fehler
            erg.save(outputFolder + "/" + str(name) + ".png")
        except Exception as error:
            erg.save(outputFolder + "/" + str(name) + ".jpg")
