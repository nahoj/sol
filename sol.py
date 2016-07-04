#! /usr/bin/env python3

# Copyright © 2016 Johan Grande
# License = MIT

'''
Generates an SVG portraying the Solar System "on a square-root scale"
'''

from datetime import date
from enum import Enum
from math import cos, sin, radians
import sys


language = "fr"
known_languages = ["", "en", "fr"]


def km_of_au(x):
    return x * 149597871


def scale(x):
    return x ** (1/2) / 10

def unscale(x):
    return (x*10) ** 2


class Dir(Enum):
    right = 0
    up = 270
    left = 180
    down = 90

    def next(self):
        return Dir((self.value-90) % 360)

    def text_anchor(self):
        if self in [Dir.up]:
            return "start"
        elif self in [Dir.down]:
            return "end"
        else:
            return "middle"


# Celestial body
class A:
    dir = Dir.right

    def __init__(self, ename, fname, dist, rad, color, satellites):
        self.name = { "en": ename, "fr": fname }
        self.dist = dist
        self.rad = rad
        self.color = color
        self.satellites = satellites

    def __str__(self):
        x = scale(self.dist)

        fmt = "  <circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s' />\n"
        res = fmt % (x, 0, scale(self.rad), self.color)

        if language != "":
            if self.name["en"] == "Sun":
                fmt = "  <g transform='translate(%.1f %.1f) rotate(%d)'>"
                res += fmt % (x, -scale(self.rad) - scale(40000), -self.dir.value)
                fmt = "<text text-anchor='start'>%s</text></g>\n"
                res += fmt % (self.name[language])
            else:
                fmt = "  <g transform='translate(%.1f %.1f) rotate(%d)'>"
                res += fmt % (x, scale(self.rad) + scale(40000), -self.dir.value)
                fmt = "<text text-anchor='%s'>%s</text></g>\n"
                res += fmt % (self.dir.text_anchor(), self.name[language])

        # children
        if self.satellites != []:
            res += "<g transform='translate(%.1f) rotate(-90)' style='font-size: smaller'>\n" % x
            for obj in self.satellites:
                obj.dir = self.dir.next()
                res += str(obj)
            res += "</g>\n"

        return res


# Ring
class R:
    dir = Dir.right

    def __init__(self, ename, fname, inner_rad, outer_rad, color, name_angle):
        self.name = { "en": ename, "fr": fname }
        self.inner_rad = inner_rad
        self.outer_rad = outer_rad
        self.color = color
        self.name_angle = radians(name_angle)

    def __str__(self):
        angle = 0.5
        ro = scale(self.outer_rad)
        ri = scale(self.inner_rad)
        xo = ro * cos(angle)
        xi = ri * cos(angle)
        yo = ro * sin(angle)
        yi = ri * sin(angle)
        data = "M %f %f A %f %f 0 0 0 %f %f L %f %f A %f %f 0 0 1 %f %f Z"
        data %= xo, yo, ro, ro, xo, -yo, xi, -yi, ri, ri, xi, yi

        stroke_width = scale(scale(self.outer_rad)) / 5
        fmt = "  <path class='ring' d='%s' stroke-width='%.1f' fill='%s' />\n"
        res = fmt % (data, stroke_width, self.color)

        if language != "":
            rt = (scale(self.inner_rad)+scale(self.outer_rad)) / 2
            xt = rt * cos(self.name_angle)
            yt = rt * sin(self.name_angle)
            fmt = "  <g transform='translate(%.1f %.1f) rotate(%d)'>"
            res += fmt % (xt, yt, -self.dir.value)
            fmt = "<text text-anchor='%s'>%s</text></g>\n"
            res += fmt % (self.dir.text_anchor(), self.name[language])

        return res


# Scale
class S:
    dir = Dir.right

    def __init__(self, dist, length, width, au_from, au_to, mkm_from, mkm_to):
        self.dist = dist
        self.length = length
        self.width = width
        self.au_from = au_from
        self.au_to = au_to
        self.mkm_from = mkm_from
        self.mkm_to = mkm_to

    def __str__(self):
        if language == "":
            return ""

        line ="  <line x1='%.1f' y1='%.1f' x2='%.1f' y2='%.1f' />\n"

        def grad_text(i):
            if i >= 0:
                return "%d" % 10 ** i
            else:
                return ("0," if language=="fr" else "0.") + "0"*(-i-1) + "1"

        def au_text(x, text):
            y = -self.width/2-scale(10000)
            my_dir = self.dir.next()
            anchor = my_dir.next().next().text_anchor()
            fmt = "  <g transform='translate(%.1f %.1f) rotate(%d)'>"
            res = fmt % (x, y, -my_dir.value)
            fmt = "<text text-anchor='%s'>%s</text></g>\n"
            res += fmt % (anchor, text)
            return res

        def mkm_text(x, text):
            y = self.width/2+scale(10000)
            my_dir = self.dir.next()
            anchor = my_dir.text_anchor()
            fmt = "  <g transform='translate(%.1f %.1f) rotate(%d)'>"
            res = fmt % (x, y, -my_dir.value)
            fmt = "<text text-anchor='%s'>%s</text></g>\n"
            res += fmt % (anchor, text)
            return res

        def str_of_grads(a, b, y1, y2, unit="Mkm"):
            res = ""
            for i in range(a, b+1):
                for j in range(1, 10):
                    x_raw = j * 10 ** i
                    x_km = km_of_au(x_raw) if unit=="AU" else x_raw * 1000000
                    x = scale(x_km)
                    res += line % (x, y1, x, y2)
                    if j == 1:
                        text = grad_text(i)
                        if unit=="AU":
                            res += au_text(x, text)
                        else:
                            res += mkm_text(x, text)
            return res

        res = "<g transform='translate(%.1f) rotate(-90)' style='stroke: white; font-size: smaller'>\n" % self.dist
        res += line % (0, 0, self.length*1.1, 0)
        res += line % (0, -self.width/2, 0, self.width/2)
        res += au_text(self.length, "UA" if language=="fr" else "AU")
        res += str_of_grads(self.au_from, self.au_to, -self.width/2, 0, unit="AU")
        res += mkm_text(self.length, "Mkm")
        res += str_of_grads(self.mkm_from, self.mkm_to, 0, self.width/2)
        res += "</g>\n"
        return res


uni_width = 5000000000
svg_width = scale(uni_width)

svg_height = 2 * scale(5000000)
uni_height = unscale(svg_height)

universe = [
  A ("Sun", "Soleil", unscale(svg_height/2), 696000, "yellow",
     [A ("Mercury", "Mercure", 57909176, 2440, "grey", []),
      A ("Venus", "Vénus", 108208930, 6052, "grey", []),
      A ("Earth", "Terre", 149597888, 6378, "blue",
         [A ("Moon", "Lune", 384399, 1737, "grey", [])] ),
      S ((scale(149597888)+scale(227936637))/2, svg_height*0.46,
         svg_height/16, -4, -2, -2, 0),
      A ("Mars", "Mars", 227936637, 3396, "red", []),
      R ("Asteroid belt", "Ceinture d'astéroïdes", 308000000, 489000000, "#111111", 2.5),
      A ("Ceres", "Cérès", 414703838, 487, "grey", []),
      A ("Jupiter", "Jupiter", 778412027, 71492, "orange",
         [A ("Io", "Io", 421800, 3643, "yellow", []),
          A ("Europa", "Europe", 671100, 1561, "grey", []),
          A ("Ganymede", "Ganymède", 1070400, 5262, "green", []),
          A ("Callisto", "Callisto", 1882700, 4820, "red", []) ]),
      A ("Saturn", "Saturne", 1421179772, 60268, "orange",
         [R ("B Ring", "Anneau B", 92000, 117580, "tan", 45),
          R ("A Ring", "Anneau A", 122170, 136775, "tan", 35),
          A ("Mimas", "Mimas", 185600, 396, "grey", []),
          A ("Enceladus", "Encelade", 238020, 504, "grey", []),
          A ("Tethys", "Téthys", 294992, 1066, "grey", []),
          A ("Dione", "Dioné", 377400, 1118, "grey", []),
          A ("Rhea", "Rhéa", 527070, 1529, "grey", []),
          A ("Titan", "Titan", 1221870, 5151, "yellow", []),
          A ("Iapetus", "Japet", 3560840, 1495, "grey", []) ]),
      A ("Uranus", "Uranus", 2876679082, 25559, "blue",
         [A ("Miranda", "Miranda", 129900, 474, "grey", []),
          A ("Ariel", "Ariel", 190900, 1159, "grey", []),
          A ("Umbriel", "Umbriel", 266000, 1169, "grey", []),
          A ("Titania", "Titania", 436300, 1578, "grey", []),
          A ("Oberon", "Obéron", 583500, 1523, "grey", []) ]),
      A ("Neptune", "Neptune", 4503443661, 24764, "blue",
         [A ("Proteus", "Protée", 117646, 416, "grey", []),
          A ("Triton", "Triton", 354759, 2707, "grey", []) ]) ]),
  S (svg_height*7/8, svg_width*0.99, svg_height/8, -3, 1, -1, 3) ]


def main():
    global language

    if len(sys.argv) > 1:
        if sys.argv[1] not in known_languages:
            print("Unknown language", file=sys.stderr)
            sys.exit(1)
        language = sys.argv[1]

    w = svg_width
    h = svg_height

    intro = '''\
<?xml version='1.0' encoding='utf-8'?>
<svg xmlns='http://www.w3.org/2000/svg' version='1.1' xml:lang='%s' width='%.1f' height='%.1f'>
  <!-- Copyright © %d Johan Grande -->
  <!-- License = CC-BY -->
  <!-- Generated %s -->
  <style>
path.ring {
  stroke: grey;
  stroke-dasharray: 2,1;
}
text {
  fill: white;
  dominant-baseline: middle;
}
  </style>
''' % (language, w, h, date.today().year, date.today().isoformat())

    print(intro)
    print("  <rect width='%.1f' height='%.1f' x='0' y='0' fill='black' />" % (w, h))
    print("<g transform='rotate(90)' style='font-size: x-small'>")
    for obj in universe:
        obj.dir = Dir.down
        print(obj)
    print("</g>")
    print("</svg>")


main()
