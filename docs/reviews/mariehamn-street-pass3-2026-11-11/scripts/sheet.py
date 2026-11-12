"""Review sheet: 2x2 grid of the original-scan crops (1968, 1978, 1985, 1995) for one area key, without overlay,
plus a labelled overlay of the 1995 crop with modern street names. Usage: sheet.py KEY [scale]"""
import sys,json,gzip
from pathlib import Path
from PIL import Image,ImageDraw
P=Path('data/map-scan-cache/review/mariehamn-major-roads/pass3');key=sys.argv[1];f=float(sys.argv[2]) if len(sys.argv)>2 else .5
ims=[Image.open(P/f'{key}-{y}.png').convert('RGB') for y in [1968,1978,1985,1995]]
w=int(max(i.width for i in ims)*f);h=int(max(i.height for i in ims)*f)
out=Image.new('RGB',(2*w+10,2*h+10),'white');d=ImageDraw.Draw(out)
for k,(im,y) in enumerate(zip(ims,[1968,1978,1985,1995])):
 x,yy=(k%2)*(w+10),(k//2)*(h+10);out.paste(im.resize((int(im.width*f),int(im.height*f))),(x,yy));d.rectangle([x,yy,x+60,yy+22],fill='black');d.text((x+5,yy+5),str(y),fill='yellow')
out.save(P/f'{key}-sheet.jpg',quality=82)
