"""Zoom on part of a review image. Usage: zoom.py IMAGE x0 y0 x1 y1 factor OUT"""
import sys
from PIL import Image
a=sys.argv;im=Image.open(a[1]).crop(tuple(map(int,a[2:6])));f=float(a[6]);im.resize((int(im.width*f),int(im.height*f)),Image.LANCZOS).convert('RGB').save(a[7],quality=88)
