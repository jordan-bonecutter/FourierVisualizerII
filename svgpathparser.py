#
#
#
#

import numpy as np
import cv2 as cv
import pyxml

teststr = "M1084.5,1622.5c195-93,405-249,472-382s-75-254-121-16-106,496-106,496,44-231,126-262,164-28,149,61-48,208,63,208,248-113,249-199-118.5-149.5-144-14c-26.13,138.85,21,210,163,202s297-315,313-474-190-215-188,109,79,363,168,363,306-194,325-461-176-149-189,78,42,367,164,365,83-249,279-260,97,294-25,291S2603,1599,2671,1516s221.5-58.5,280.5-77.5,105-60,105-60"

def bezier(t, z0, z1):
  return z0*(1-t) + z1*t

def n_bezier(t, *control_points):
  if len(control_points) == 2:
    return bezier(t, control_points[0], control_points[1])
  return bezier(t, n_bezier(t, *control_points[:-1]), n_bezier(t, *control_points[1:]))

def _findfirstpath(root):
  # dfs for first path in file
  if len(root.children) == 0:
    return None

  for child in root.children:
    if child.name == 'path':
      return child
    ret =  _findfirstpath(child)
    if ret != None:
      return ret

  return None
  
def firstpathinfile(fd):
  # read contents
  contents = pyxml.xml_tree.fromFile(fd)
  return _findfirstpath(contents.root)

def readpath(pathstr):
  ret = SVGPathArtist()
  r_i = 0
  currcommand = None
  while r_i < len(pathstr):
    # read in whitespace
    while pathstr[r_i].isspace():
      r_i += 1
      if r_i == len(pathstr):
        return ret

    # new command character
    if pathstr[r_i].isalpha():
      currcommand = pathstr[r_i]
      r_i += 1

    while r_i < len(pathstr) and pathstr[r_i].isspace():
      r_i += 1

    if currcommand.upper() == 'M':
      nx = ''
      ny = ''
      b  = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        nx += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1

      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] != '-'or b==r_i):
        ny += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      if currcommand.islower():
        ret.moveto(complex(float(nx), float(ny)), absolute=False)
      else:
        ret.moveto(complex(float(nx), float(ny)), absolute=True)

    elif currcommand.upper() == 'Z':
      ret.closepath()

    elif currcommand.upper() == 'L':
      lx = ''
      ly = ''

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1

      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        lx += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1

      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] != '-'or b==r_i):
        ly += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      if currcommand.islower():
        ret.lineto(complex(float(lx), float(ly)), absolute=False)
      else:
        ret.lineto(complex(float(lx), float(ly)), absolute=True)
      
    elif currcommand.upper() == 'H':
      nx = ''

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1

      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] != '-'or b==r_i):
        nx += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      if currcommand.islower():
        ret.horizontalto(float(nx), absolute=False)
      else:
        ret.horizontalto(float(nx), absolute=True)

    elif currcommand.upper() == 'V':
      ny = ''

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1

      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] !='-'or r_i == b):
        ny += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      if currcommand.islower():
        ret.verticalto(float(ny), absolute=False)
      else:
        ret.verticalto(float(ny), absolute=True)

    elif currcommand.upper() == 'C':
      c1x = ''
      c1y = ''
      c2x = ''
      c2y = ''
      nx  = ''
      ny  = ''

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c1x += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c1y += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c2x += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c2y += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        nx += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] != '-'or b==r_i):
        ny += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      cp1 = complex(float(c1x), float(c1y))
      cp2 = complex(float(c2x), float(c2y))
      np  = complex(float(nx),  float(ny))

      if currcommand.islower():
        ret.curveto(cp1, cp2, np, absolute=False)
      else:
        ret.curveto(cp1, cp2, np, absolute=True)

    elif currcommand.upper() == 'S':
      c2x = ''
      c2y = ''
      nx  = ''
      ny  = ''

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c2x += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c2y += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        nx += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] != '-'or b==r_i):
        ny += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      cp2 = complex(float(c2x), float(c2y))
      np  = complex(float(nx),  float(ny))

      if currcommand.islower():
        ret.smoothcurveto(cp2, np, absolute=False)
      else:
        ret.smoothcurveto(cp2, np, absolute=True)

    elif currcommand.upper() == 'Q':
      c1x = ''
      c1y = ''
      nx  = ''
      ny  = ''

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c1x += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        c1y += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        nx += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] != '-'or b==r_i):
        ny += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      cp1 = complex(float(c2x), float(c2y))
      np  = complex(float(nx),  float(ny))

      if currcommand.islower():
        ret.qcurveto(cp1, np, absolute=False)
      else:
        ret.qcurveto(cp1, np, absolute=True)

    elif currcommand.upper() == 'T':
      nx  = ''
      ny  = ''

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (pathstr[r_i] != '-' or b == r_i) and pathstr[r_i] != ',':
        nx += pathstr[r_i]
        r_i += 1

      if pathstr[r_i] == ',':
        r_i += 1

      # read in whitespace
      while pathstr[r_i].isspace():
        r_i += 1
      
      b = r_i
      while (not pathstr[r_i].isalpha()) and pathstr[r_i] != ',' and (pathstr[r_i] != '-'or b==r_i):
        ny += pathstr[r_i]
        r_i += 1
        if r_i == len(pathstr):
          break

      if r_i < len(pathstr) and pathstr[r_i] == ',':
        r_i += 1

      np  = complex(float(nx),  float(ny))

      if currcommand.islower():
        ret.smoothqcurveto(np, absolute=False)
      else:
        ret.smoothqcurveto(np, absolute=True)

  return ret


class SVGPathArtist:
  def __init__(self):
    self.cursor = complex(0)
    self.instr  = []

  def moveto(self, point, absolute=True):
    if absolute:
      self.cursor = point 
    else:
      self.cursor += point

  def closepath(self):
    self.instr.append(('z'))      

  def lineto(self, point, absolute=True):
    if absolute:
      self.instr.append(('l', self.cursor, point))
      self.cursor = point
    else:
      self.instr.append(('l', self.cursor, self.cursor + point))
      self.cursor += point

  def horizontalto(self, h, absolute=True):
    if absolute:
      self.instr.append(('l', self.cursor, complex(h, self.cursor.imag)))
      self.cursor = complex(h, self.cursor.imag)
    else:
      self.instr.append(('l', self.cursor, complex(self.cursor.real + h, self.cursor.imag)))
      self.cursor = complex(self.cursor.real + h, self.cursor.imag)

  def verticalto(self, v, absolute=True):
    if absolute:
      self.instr.append(('l', self.cursor, complex(self.cursor.real, v)))
      self.cursor = complex(self.cursor.real, v)
    else:
      self.instr.append(('l', self.cursor, complex(self.cursor.real, self.cursor.imag + v)))
      self.cursor = complex(self.cursor.real, self.cursor.imag + v)

  def curveto(self, cp1, cp2, cp3, absolute=True):
    if absolute:
      self.instr.append(('c', self.cursor, cp1, cp2, cp3))
      self.cursor = cp3
    else:
      self.instr.append(('c', self.cursor, self.cursor+cp1, self.cursor+cp2, self.cursor+cp3))
      self.cursor += cp3

  def smoothcurveto(self, cp2, cp3, absolute=True):
    if absolute:
      previ = self.instr[-1]
      cp1 = previ[3] + 2*(previ[4] - previ[3])
      self.instr.append(('c', self.cursor, cp1, cp2, cp3))
      self.cursor = cp3
    else:
      previ = self.instr[-1]
      cp1 = previ[3] + 2*(previ[4] - previ[3])
      self.instr.append(('c', self.cursor, cp1, self.cursor+cp2, self.cursor+cp3))
      self.cursor += cp3

  def qcurveto(self, cp1, cp2, absolute=True):
    if absolute:
      self.instr.append(('q', self.cursor, cp1, cp2))
      self.cursor = cp2
    else:
      self.instr.append(('q', self.cursor, self.cursor+cp1, self.cursor+cp2))
      self.cursor += cp2

  def smoothqcurveto(self, cp2, absolute=True):
    if absolute:
      previ = self.instr[-1]
      cp1   = previ[1] + 2*(previ[2] - previ[1])
      self.instr.append(('q', self.cursor, cp1, cp2))
      self.cursor = cp2
    else:
      previ = self.instr[-1]
      cp1   = previ[1] + 2*(previ[2] - previ[1])
      self.instr.append(('q', self.cursor, cp1, self.cursor+cp2))
      self.cursor += cp2

  def getpoints(self, translate=complex(0)):
    points = []
    for instr in self.instr:
      if instr[0] == 'l':
        for t in range(100):
          points.append(bezier(t/100., instr[1], instr[2]) + translate)
      elif instr[0] == 'q':
        for t in range(100):
          points.append(n_bezier(t/100., instr[1], instr[2], instr[3]) + translate)
      elif instr[0] == 'c':
        for t in range(100):
          points.append(n_bezier(t/100., instr[1], instr[2], instr[3], instr[4]) + translate)
    return points

if __name__ == '__main__':
  print(readpath(teststr))
