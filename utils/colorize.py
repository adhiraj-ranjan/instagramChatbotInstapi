import numpy as np
import cv2
#from numpy.core.fromnumeric import resize
import sys, getopt


def main(argv):
   try:
      opts, args = getopt.getopt(argv,"i:",["image=",])
   except getopt.GetoptError:
      print('main.py -i <imagepath>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('main.py -i <imagepath>')
         sys.exit()
      elif opt in ("-i", "--image"):
         imagePath = arg
         return imagePath

image_path = main(sys.argv[1:])


prototxt_path = '/home/runner/PeacefulAnnualTechnicianChat/colorization/colorization_deploy_v2.prototxt'
model_path = '/home/runner/PeacefulAnnualTechnicianChat/colorization/colorization_release_v2.caffemodel'
kernel_path = '/home/runner/PeacefulAnnualTechnicianChat/colorization/pts_in_hull.npy'

net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
points = np.load(kernel_path)

points = points.transpose().reshape(2, 313, 1, 1)
net.getLayer(net.getLayerId("class8_ab")).blobs = [points.astype(np.float32)]
net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [np.full([1, 313], 2.606, dtype="float32")]

bw_image = cv2.imread(image_path)
#bw_image = cv2.resize(bw_image, (960, 540))
normalized = bw_image.astype("float32") / 255.0
lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)

resizd_image = cv2.resize(lab, (224, 224))
L = cv2.split(resizd_image)[0]
L -= 50

net.setInput(cv2.dnn.blobFromImage(L))
ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

ab = cv2.resize(ab, (bw_image.shape[1], bw_image.shape[0]))
L = cv2.split(lab)[0]

colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
colorized = cv2.cvtColor(colorized, cv2.COLOR_Lab2BGR)
colorized = (255.0 * colorized).astype("uint8")

cv2.imwrite('temps/colorized_img.jpg', colorized)