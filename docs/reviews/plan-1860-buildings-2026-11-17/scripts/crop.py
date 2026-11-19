import sys
from PIL import Image,ImageDraw
im=Image.open(sys.argv[7] if len(sys.argv)>7 else 'dist/assets/mariehamn-plan-1860.png').convert('RGB');K=2048/1824
name=sys.argv[1];vx0,vy0,vx1,vy1=map(int,sys.argv[2:6]);Z=float(sys.argv[6]) if len(sys.argv)>6 else 4
c=im.crop((int(vx0*K),int(vy0*K),int(vx1*K),int(vy1*K)));c=c.resize((int((vx1-vx0)*Z),int((vy1-vy0)*Z)),Image.LANCZOS);d=ImageDraw.Draw(c)
for g in range(vx0-vx0%10,vx1+1,10):
    X=(g-vx0)*Z;d.line([(X,0),(X,c.size[1])],fill=(0,90,255) if g%50==0 else (150,190,255),width=1)
    if g%50==0: d.text((X+2,2),str(g),fill=(0,0,180))
for g in range(vy0-vy0%10,vy1+1,10):
    Y=(g-vy0)*Z;d.line([(0,Y),(c.size[0],Y)],fill=(0,90,255) if g%50==0 else (150,190,255),width=1)
    if g%50==0: d.text((2,Y+2),str(g),fill=(0,0,180))
c.save(f'crops/{name}.png');print(name,c.size)
