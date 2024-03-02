import numpy as np
from PIL import Image
import cv2 as cv


def replaceTexturePrep(img):
    array = np.array(img)
    gray = cv.cvtColor(array, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (5, 5), 0)
    dummy, array = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    array = cv.cvtColor(array, cv.COLOR_GRAY2RGBA)
    im_pil = Image.fromarray(array)
    return im_pil


def imageTransparentPattern(img):
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] < 255 and item[1] < 255 and item[2] < 255:
            newData.append((200, 200, 200, 0))  # ÄNDERN SONST GEHT NET
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def crop(img):
    array = np.array(img)
    try:
        blacky, blackx, dummy = np.where(array != 255)
    except:
        blacky, blackx = np.where(array != 255)
    top, bottom = blacky[0], blacky[-1]

    left, right = min(blackx), max(blackx)

    img = array[top:bottom, left:right]
    im_pil = Image.fromarray(img)
    return im_pil


def whiteTranparent(img):
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def tranparent(img, grenzwertR, grenzwertG, grenzwertB, alpha):
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] > grenzwertR and item[1] > grenzwertG and item[2] > grenzwertB:
            newData.append((255, 255, 255, alpha))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def farbe(img, targetR, targetG, targetB, targetAlpha):
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] < 255 and item[1] < 255 and item[2] < 255 != 0:
            newData.append((targetR, targetB, targetG, targetAlpha))
        else:
            newData.append(item)

    img.putdata(newData)
    return img


def str2bool(v):
    return v.lower() in ("True", "true")
