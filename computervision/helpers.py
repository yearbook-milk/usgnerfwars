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

def file_get_contents(file_name):
    with open(file_name, 'r') as file:
        content = file.read()
    return content

def center_of_bbox(inputbox):
    cp = ( \
    int(inputbox[0] + (0.5 * (inputbox[2]))), \
    int(inputbox[1] + (0.5 * (inputbox[3]))) \
    )
    return cp

def AsubsetofB(a, b):
    return (a[0] in range(b[0], b[0] + b[2]) and a[1] in range(b[1], b[1] + b[3]) and a[2] <= b[2] and a[3] <= b[3])

def AtouchesB(a, b):
    return (
        AsubsetofB((a[0],a[1],0,0), b) or
        AsubsetofB((a[0],a[1]+a[3],0,0), b) or
        AsubsetofB((a[0]+a[2],a[1],0,0), b) or
        AsubsetofB((a[0]+a[2],a[1]+a[3],0,0), b)
    )

def resizeBox(inputbox, scale):
    #print(inputbox)
    cp = ( \
    int(inputbox[0] + (0.5 * (inputbox[2]))), \
    int(inputbox[1] + (0.5 * (inputbox[3]))) \
    )
    #print(cp)
    
    nb = ( \
    cp[0] - (0.5 * scale * inputbox[2]), \
    cp[1] - (0.5 * scale * inputbox[3]), \
    (scale * inputbox[2]), \
    (scale * inputbox[3]) \
    )
    
    x, y, w, h = nb
    #print(nb)
    
    return (int(x), int(y), int(w), int(h))
    