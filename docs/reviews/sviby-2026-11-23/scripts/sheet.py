"""Tile renders side by side: sheet.py OUT.jpg COLS IN1.jpg IN2.jpg ..."""
import sys
from PIL import Image
out, cols, ins = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(p) for p in ins]; w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
W = Image.new('RGB', (cols * w, rows * h), 'white')
for i, im in enumerate(ims): W.paste(im, ((i % cols) * w, (i // cols) * h))
W.save(out, quality=85); print(out)
