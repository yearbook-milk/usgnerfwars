import cv2
import numpy as np

# https://stackoverflow.com/questions/32609098/how-to-fast-change-image-brightness-with-python-opencv
def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def line(image, hw, value, color = (0,255,0)):
    if hw == "X=":
        for i in range(0, image.shape[0]):
            image[i][value] = color
    elif hw == "Y=":
        for i in range(0, image.shape[1]):
            image[value][i] = color
    return image
