import cv2
import numpy as np

# https://stackoverflow.com/questions/32609098/how-to-fast-change-image-brightness-with-python-opencv
# brightens an image by a certain amount and returns the newly modified image
# example: img2 = helpers.increase_brightness(img1, 100)
def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img
    
    
# draws a line at the specified coordinate on the image (passed in as a nparray), then returns the newly drawn on image
# examples: 
# img2 = helpers.line(img1, "X=", 420)
# img4 = helpers.line(img3, "Y=", 69)
def line(image, hw, value, color = (0,255,0)):
    if hw == "X=":
        for i in range(0, image.shape[0]):
            image[i][value] = color
    elif hw == "Y=":
        for i in range(0, image.shape[1]):
            image[value][i] = color
    return image

# returns the contents of a text-encoded file as a string
def file_get_contents(file_name):
    with open(file_name, 'r') as file:
        content = file.read()
    return content

# returns a tuple of two ints representing the center of a bounding box in the format tuple:(x, y, width, height)
# example: centerx, centery = helpers.center_of_bbox( (120, 30, 10, 20) )
def center_of_bbox(inputbox):
    cp = ( \
    int(inputbox[0] + (0.5 * (inputbox[2]))), \
    int(inputbox[1] + (0.5 * (inputbox[3]))) \
    )
    return cp

# returns a boolean signaling whether box A is entirely in box B
# both boxes must be in the format tuple:(x, y, width, height)
def AentirelyinB(a, b):
    return (a[0] in range(b[0], b[0] + b[2]) and a[1] in range(b[1], b[1] + b[3]) and a[2] <= b[2] and a[3] <= b[3])

# returns a boolean signaling whether or not box A touches box BaseException
# both boxes must be in the formst tuple:(x, y, width, height)
def AtouchesB(a, b):
    if (
        AentirelyinB((a[0],a[1],0,0), b) or
        AentirelyinB((a[0],a[1]+a[3],0,0), b) or
        AentirelyinB((a[0]+a[2],a[1],0,0), b) or
        AentirelyinB((a[0]+a[2],a[1]+a[3],0,0), b) or
        AentirelyinB(b, a) or 
        AentirelyinB(a, b)
    ):
        return True
    else:
        for i in range(a[0], a[0] + a[2]):
            if AentirelyinB( (i, a[1], 0, 0), b): return True
            if AentirelyinB( (i, a[1] + a[3], 0, 0), b): return True
        for i in range(a[1], a[1] + a[3]):
            if AentirelyinB( (a[0], i, 0, 0), b): return True
            if AentirelyinB( (a[0] + a[2], i, 0, 0), b): return True

    return False

# takes in a bounding box in the format tuple:(x,y,width,height) and returns a new box, in the same format, but resized
# the centerpoint of the box should remain the same but the box on the whole will be resized
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
    
