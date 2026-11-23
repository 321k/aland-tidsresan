"""Find the printed 1 km KKJ grid crosses ("+") on a base-map scan and fit them, for registering a sheet.

Usage: grid_crosses.py SCAN.jpg E1 N1 X1 Y1 E2 N2 X2 Y2 EMIN EMAX NMIN NMAX [OUT.json]
  Two seed crosses (KKJ km E,N and their approximate pixels) give a first similarity transform. For every km
  intersection E in [EMIN, EMAX], N in [NMIN, NMAX] the cross is searched within ±R px (env R, default 30) of its
  prediction: the dark row and dark column through the window, each needing a run of dark pixels on both sides of
  the centre (a cross, not a line or a letter). Found crosses are fitted with an affine transform; residuals are printed
  and outliers over 4 m dropped. OUT.json gets the crosses and the affine fit (pixel → KKJ metres)."""
import sys, json, os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

scan = sys.argv[1]
e1, n1, x1, y1, e2, n2, x2, y2 = map(float, sys.argv[2:10])
emin, emax, nmin, nmax = map(int, sys.argv[10:14])
out = sys.argv[14] if len(sys.argv) > 14 else None
R = int(os.environ.get('R', 30))
img = np.asarray(Image.open(scan).convert('L'), dtype=float)

# similarity transform from the two seeds (km → px), allowing rotation and scale
a = complex(x2 - x1, y2 - y1) / complex(e2 - e1, -(n2 - n1))
def predict(e, n):
    z = complex(x1, y1) + a * complex(e - e1, -(n - n1)); return z.real, z.imag

def find(px, py):
    x0, y0 = int(round(px)) - R, int(round(py)) - R
    w = img[y0:y0 + 2 * R + 1, x0:x0 + 2 * R + 1]
    if w.shape != (2 * R + 1, 2 * R + 1): return None
    dark = w < 120
    row, col = int(np.argmax(dark.sum(1))), int(np.argmax(dark.sum(0)))
    # arms: dark pixels along the row on both sides of the column, and along the column on both sides of the row
    left, right = dark[row, max(0, col - 14):col - 3].sum(), dark[row, col + 4:col + 15].sum()
    up, down = dark[max(0, row - 14):row - 3, col].sum(), dark[row + 4:row + 15, col].sum()
    if min(left, right, up, down) < 6: return None
    # sub-pixel centre: mean position of the dark pixels on the cross row/column near the centre
    cy = (np.arange(w.shape[0])[:, None] * dark[:, max(0, col - 1):col + 2]).sum() / max(1, dark[:, max(0, col - 1):col + 2].sum())
    cx = (np.arange(w.shape[1])[None, :] * dark[max(0, row - 1):row + 2, :]).sum() / max(1, dark[max(0, row - 1):row + 2, :].sum())
    return x0 + cx, y0 + cy

found = []
for e in range(emin, emax + 1):
    for n in range(nmin, nmax + 1):
        p = find(*predict(e, n))
        if p: found.append(dict(km=[e, n], pixel=[round(float(p[0]), 1), round(float(p[1]), 1)]))
def fit(rows):
    A = np.array([[r['pixel'][0], r['pixel'][1], 1] for r in rows]); B = np.array([[r['km'][0] * 1000, r['km'][1] * 1000] for r in rows])
    M = np.linalg.lstsq(A, B, rcond=None)[0]; return M, np.linalg.norm(A @ M - B, axis=1)
M, res = fit(found)
keep = [r for r, d in zip(found, res) if d <= 4]
for _ in range(3):                                   # refine: predict from the fit, search again, refit
    M, res = fit(keep)
    Minv = np.linalg.lstsq(np.column_stack([M[:2].T @ np.eye(2), M[2]]).T if False else np.array([[M[0, 0], M[1, 0]], [M[0, 1], M[1, 1]]]).T, np.eye(2), rcond=None)[0]
    def predict(e, n, M=M):
        A = np.array([[M[0, 0], M[1, 0]], [M[0, 1], M[1, 1]]]); b = np.array([e * 1000, n * 1000]) - M[2]
        return tuple(np.linalg.solve(A, b))
    found = []
    for e in range(emin, emax + 1):
        for n in range(nmin, nmax + 1):
            q = find(*predict(e, n))
            if q: found.append(dict(km=[e, n], pixel=[round(float(q[0]), 1), round(float(q[1]), 1)]))
    M, res = fit(found)
    keep = [r for r, d in zip(found, res) if d <= 4]
M, res = fit(keep)
for r, d in zip(keep, res): r['residualMeters'] = round(float(d), 2)
print(f'{len(found)} crosses found, {len(keep)} kept; residual max {res.max():.2f} m, mean {res.mean():.2f} m')
for r in keep: print('  ', r['km'], r['pixel'], r['residualMeters'])
if out:
    json.dump(dict(scan=os.path.basename(scan), crosses=keep, affine=M.tolist()), open(out, 'w'), indent=1)
