#
#
#
#

import cairo
import numpy as np
import cv2 as cv
import svgpathparser
from math import pi as M_PI
from math import e as M_E

# target output video size and length
OUT_WIDTH = 1920//3
OUT_HEIGHT = 1080//3
OUT_FPS = 60
FRAME_COUNT = 1*OUT_FPS

# the frame buffer that cairo prefers uses ARGB (32 bit / pixel) but 
# opencv videowriters prefer RGB (24 bit / pixel) so we have to do
# a lil conversion here in this function
def save_frame(tosave, vwriter, tbuff=None):
  h, w, c = tosave.shape
  if tbuff is None:
    tbuff = np.zeros((h, w, 3), dtype=np.uint8)
  for y in range(tbuff.shape[0]):
    for x in range(tbuff.shape[1]):
      tbuff[y, x] = (tosave[y, x][0], tosave[y, x][1], tosave[y, x][2])
  vwriter.write(tbuff)
  return tbuff

# the points we are calculating lie on the complex plane
# however we want to have points ying on an image buffer which are
# indexed differently so we convert from complex plane to image
# plane with this function
def get_cairo_point(inpoint, offset, scale):
  global OUT_WIDTH, OUT_HEIGHT
  return ((inpoint[0]-offset[0])/scale + OUT_WIDTH/2, OUT_HEIGHT/2 - (inpoint[1]-offset[1])/scale)


def main(argv) -> int:
  global OUT_HEIGHT, OUT_WIDTH
  if len(argv) != 3:
    print('Invalid usage: ' + argv[0] + ' <input.svg> <output.avi>')
    return 1
  # extract points from svg
  with open(argv[1], 'r') as fi:
    path = svgpathparser.firstpathinfile(fi)
  if not path:
    print('No path in svg file')
    return 0
  pathinfo = svgpathparser.readpath(path.attributes['d']).getpoints()
  for p in pathinfo:
    if type(p) == complex:
      print(p)
  points   = [p[0] for p in pathinfo]

  # get scaling informations
  bounds = max(points, key=lambda x:x.real).real, max(points, key=lambda x:x.imag).imag, \
           min(points, key=lambda x:x.real).real, min(points, key=lambda x:x.imag).imag
  pwidth = bounds[0] - bounds[2]
  pheight = bounds[1] - bounds[3]
  wscale = pwidth/(OUT_WIDTH)
  hscale = pheight/(OUT_HEIGHT)
  scale = max(wscale, hscale)/0.9
  xoff = (bounds[0] + bounds[2])/2
  yoff = (bounds[1] + bounds[3])/2
  off  = (xoff, yoff)
  
  # take the dft and sort it so that the
  # lowest freq are at the bottom
  freqs  = np.fft.fft(points)  
  sfs    = np.fft.fftfreq(len(points))
  freqs  = [(freqs[i], sfs[i]) for i in range(len(freqs))]
  freqs  = sorted(freqs, key=lambda x: abs(x[1]))

  # create current image buffer
  image  = np.zeros((OUT_HEIGHT, OUT_WIDTH, 4), dtype=np.uint8)
  tbuff  = None

  # setup cairo
  sfc    = cairo.ImageSurface.create_for_data(image, cairo.FORMAT_ARGB32, OUT_WIDTH, OUT_HEIGHT)
  ctx    = cairo.Context(sfc)
  ctx.scale(1/scale, 1/scale)
  ctx.translate(-xoff/scale + OUT_WIDTH/2, OUT_HEIGHT/2 - yoff/scale)
  ctx.set_line_width(2)
  ctx.set_line_cap(cairo.LineCap.ROUND)
  vwriter = cv.VideoWriter(argv[2],cv.VideoWriter_fourcc(*'MJPG'),OUT_FPS,(OUT_WIDTH, OUT_HEIGHT))

  # draw the frames
  todraw = [points[0]]
  #zeropoint = get_cairo_point((todraw[0].real, todraw[0].imag), off, scale)
  zeropoint = todraw[0]
  framessaved = 0
  for t in range(FRAME_COUNT):
    theta = (t / (FRAME_COUNT-1))*len(points)*2*M_PI
    curr = 0

    # a white background is nice
    ctx.set_source_rgb(1, 1, 1)
    nx, ny = ctx.device_to_user(0, 0)
    w, h   = ctx.device_to_user_distance(OUT_WIDTH, OUT_HEIGHT)
    ctx.rectangle(nx, ny, w, h)
    ctx.fill()

    # our complex exponential basis functions are
    # drawn in a nice light gray
    ctx.set_source_rgb(0.7, 0.7, 0.7)

    n = 0
    for weight, freq in freqs:
      # get the image plane point for the current accumlated point
      #center = get_cairo_point((curr.real, curr.imag), off, scale)
      center = curr
      curr += weight*pow(M_E, 1j*freq*theta)/len(points)

      # only draw if it's not the DC frequency (DC is an eyesore)
      if n != 0:
        # draw the circle and the line representing its current theta angle
        ctx.set_line_width(2)
        #ctx.arc(center[0], center[1], abs(weight)/(scale*len(points)), 0, 2*M_PI)
        ctx.arc(center.real, center.imag, abs(weight)/len(points), 0, 2*M_PI)
        ctx.stroke()
        ctx.move_to(center.real, center.imag)
        currpoint = get_cairo_point((curr.real, curr.imag), off, scale) 
        ctx.line_to(curr.real, curr.imag)
        ctx.stroke()
      n += 1

    # we want to draw the path so far, so we push the points
    # in a list of points we visited
    todraw.append(curr)

    # now we draw the path traced out so far
    ctx.move_to(zeropoint.real, zeropoint.imag)
    ctx.set_source_rgb(1, 0.05, 0.05)
    for i in range(1, len(todraw)):
      draw = todraw[i]
      cdraw = get_cairo_point((draw.real, draw.imag), off, scale)
      ctx.line_to(draw.real, draw.imag)
    ctx.stroke()

    # save the current frame
    tbuff = save_frame(image, vwriter, tbuff)

    # output the current frame number so we can monitor progress
    print(framessaved)
    framessaved += 1

  # release videowriter memory and close fp
  vwriter.release()

if __name__ == '__main__':
  import sys
  main(sys.argv)

