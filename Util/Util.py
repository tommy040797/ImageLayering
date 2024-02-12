import numpy as np
from PIL import Image
import cv2


def crop(img):
    array = np.array(img)
    try:
        blacky, blackx, dummy = np.where(array != 255)
    except:
        blacky, blackx = np.where(array != 255)
    top, bottom = blacky[0], blacky[-1]

    left, right = min(blackx), max(blackx)

    img = array[top : bottom, left: right]
    im_pil = Image.fromarray(img)
    return im_pil


def tranparent(img, grenzwertR, grenzwertG, grenzwertB):
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] > grenzwertR and item[1] > grenzwertG and item[2] > grenzwertB:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

def str2bool(v):
    return v.lower() in ("True", "true")