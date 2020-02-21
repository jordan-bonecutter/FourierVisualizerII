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
OUT_WIDTH = 1920
OUT_HEIGHT = 1080
OUT_FPS = 60
FRAME_COUNT = 20*OUT_FPS


def save_frame(tosave, vwriter, tbuff=None):
  h, w, c = tosave.shape
  if tbuff is None:
    tbuff = np.zeros((h, w, 3), dtype=np.uint8)
  for y in range(tbuff.shape[0]):
    for x in range(tbuff.shape[1]):
      tbuff[h - y - 1, x] = (tosave[y, x][0], tosave[y, x][1], tosave[y, x][2])
  vwriter.write(tbuff)
  return tbuff


def get_freq(index, n_freqs):
  scaled = 2.*(index/n_freqs)
  if int(scaled)%2 == 1:
    return ((scaled*M_PI)%M_PI) - M_PI
  else:
    return (scaled*M_PI)%M_PI


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
  points = svgpathparser.readpath(path.attributes['d']).getpoints()

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
  ctx.set_line_width(2)
  ctx.set_line_cap(cairo.LineCap.ROUND)
  vwriter = cv.VideoWriter(argv[2],cv.VideoWriter_fourcc(*'MJPG'),OUT_FPS,(OUT_WIDTH, OUT_HEIGHT))

  # draw the frames
  todraw = [points[0]]
  zeropoint = get_cairo_point((todraw[0].real, todraw[0].imag), off, scale)
  framessaved = 0
  for t in range(FRAME_COUNT):
    theta = (t / (FRAME_COUNT-1))*len(points)*2*M_PI
    curr = 0

    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, OUT_WIDTH, OUT_HEIGHT)
    ctx.fill()
    ctx.set_source_rgb(0.7, 0.7, 0.7)

    n = 0
    for weight, freq in freqs:
      center = get_cairo_point((curr.real, curr.imag), off, scale)
      curr += weight*pow(M_E, 1j*freq*theta)/len(points)
      if n != 0:
        ctx.set_line_width(2)
        ctx.arc(center[0], center[1], abs(weight)/(scale*len(points)), 0, 2*M_PI)
        ctx.stroke()
        ctx.move_to(center[0], center[1])
        currpoint = get_cairo_point((curr.real, curr.imag), off, scale) 
        ctx.line_to(currpoint[0], currpoint[1])
        ctx.stroke()
      n += 1

    todraw.append(curr)
    ctx.move_to(zeropoint[0], zeropoint[1])
    ctx.set_source_rgb(1, 0.05, 0.05)
    for i in range(1, len(todraw)):
      draw = todraw[i]
      cdraw = get_cairo_point((draw.real, draw.imag), off, scale)
      ctx.line_to(cdraw[0], cdraw[1])
    ctx.stroke()
    tbuff = save_frame(image, vwriter, tbuff)
    print(framessaved)
    framessaved += 1
  vwriter.release()

if __name__ == '__main__':
  import sys
  main(sys.argv)

