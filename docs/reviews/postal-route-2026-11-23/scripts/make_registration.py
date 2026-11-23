"""Write printed-grid mesh registrations for sheet 1012 15 (with 0034 15 in 1968–1985, with 1012 03 in 1994) from the
fitted km crosses (data/data-reg-YEAR.json, from grid_crosses.py), and validate them with the project's
registration_pair. Frame: KKJ (EPSG:2391) E 1 416 000–1 420 000, N 6 672 000–6 680 000. The nine mesh nodes are placed
by the affine fit of the printed crosses (the 1 420 000 and 6 680 000 lines lie on or just outside the neat line, where
only margin ticks are printed); four printed crosses, one in each mesh cell, are the independent checks.
Usage: make_registration.py"""
import sys, json, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, 'scripts')
from rural_registration import registration_pair
Image.MAX_IMAGE_PIXELS = None
D = 'docs/reviews/postal-route-2026-11-23/data'
W, E, N, S = 1416000, 1420000, 6680000, 6672000
SCANS = {1968: ('003415_101215', 'https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/0/0034/003415/003415_101215_1968.jpg'),
         1978: ('003415_101215', 'https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/0/0034/003415/003415_101215_1978.jpg'),
         1985: ('003415_101215', 'https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/0/0034/003415/003415_101215_1985.jpg'),
         1994: ('101203_101215', 'https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/1/1012/101203/101203_101215_1994.jpg')}
# one printed cross per mesh cell (west/east of 1 418 000, north of / at 6 676 000 and south of it), first available
CELLS = [[(1417, 6679), (1417, 6678), (1417, 6677)], [(1418, 6679), (1418, 6677), (1418, 6678)], [(1417, 6675), (1417, 6674), (1417, 6673)], [(1418, 6674), (1418, 6673)]]
out = []
for year, (sheet, url) in SCANS.items():
    fit = json.load(open(f'{D}/data-reg-{year}.json')); M = np.array(fit['affine'])
    A = np.array([[M[0, 0], M[1, 0]], [M[0, 1], M[1, 1]]])
    px = lambda e, n: [round(float(v), 1) for v in np.linalg.solve(A, np.array([e, n]) - M[2])]
    grid = [[px(x, y) for x in (W, (W + E) // 2, E)] for y in (N, (N + S) // 2, S)]
    crosses = {tuple(c['km']): c['pixel'] for c in fit['crosses']}
    checks = [dict(pixel=crosses[k], metric=[k[0] * 1000, k[1] * 1000]) for k in (next(c for c in cell if c in crosses) for cell in CELLS)]
    path = f'data/map-scan-cache/{sheet}_{year}.jpg'; img = Image.open(path)
    src = dict(id=f'nls:101215:{year}', sheet=sheet, title=f'Lantmäteriverket · Skeppsvik/Eckerö 1012 15 · {year}', year=year, originalUrl=url,
               originalSha256=hashlib.sha256(open(path, 'rb').read()).hexdigest(), imageSize=list(img.size),
               registration=dict(method='printed-grid-mesh', crs='EPSG:2391', pixelFrame=[grid[0][0], grid[0][2], grid[2][2], grid[2][0]],
                                 metricFrame=[[W, N], [E, N], [E, S], [W, S]], pixelGrid=grid, checkPoints=checks,
                                 nodeBasis=f"Noderna är placerade med en affin anpassning av {len(fit['crosses'])} tryckta kilometerkryss (största avvikelse {max(c['residualMeters'] for c in fit['crosses'])} m); 1 420 000- och 6 680 000-linjerna ligger vid eller strax utanför kartramen."),
               license='CC BY 4.0', licenseUrl='https://www.maanmittauslaitos.fi/asioi-verkossa/vanhat-painetut-kartat',
               attribution=f'© Lantmäteriverket, grundkarta 1012 15, {year}. Manuella tolkningar.')
    fwd, inv = registration_pair(src)                     # raises if the mesh or a check fails
    errs = [float(np.linalg.norm(fwd(np.array(c['pixel'])) - np.array([c['km'][0] * 1000, c['km'][1] * 1000]))) for c in fit['crosses']
            if W < c['km'][0] * 1000 < E and S < c['km'][1] * 1000 < N]
    print(year, sheet, src['imageSize'], 'mesh ok; crosses inside the frame', len(errs), 'max error', round(max(errs), 2) if errs else None, 'm')
    out.append(src)
json.dump(dict(schemaVersion=1, note='Registreringar av grundkartblad 1012 15 för postvägsgranskningen; används av window.py och som kartkällor i data/postal-route-storby.json.', sources=out),
          open(f'{D}/registrations-101215.json', 'w'), ensure_ascii=False, indent=1)
