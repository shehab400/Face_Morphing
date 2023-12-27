# import required library
import cv2

# read the input image
img = cv2.imread('1.jpg')

# define the contrast and brightness value
contrast = 1 # Contrast control ( 0 to 127)
brightness = 0 # Brightness control (0-100)

# call addWeighted function. use beta = 0 to effectively only
#operate on one image
out = cv2.addWeighted( img, contrast, img, 0, brightness)

# display the image with changed contrast and brightness
cv2.imshow('adjusted', out)
cv2.waitKey(0)
cv2.destroyAllWindows()