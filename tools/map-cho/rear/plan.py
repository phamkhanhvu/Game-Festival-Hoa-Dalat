# Thông số mặt bằng khu sau lưng chợ, theo hệ trục riêng của chợ: s dọc tường sau (về đông bắc), t vuông góc (dương về phía Khu Hòa Bình)
import sys, numpy as np
from fr import *
def W(pts): return [tuple(L(s,t)) for s,t in pts]
WING  = [(35.8,-0.5),(78,-0.5),(78,-19),(30.0,-19)]
ANNEX = [(36.5,-19),(78,-19),(78,-24.3),(36.5,-31.0)]
TOWER = [(78,-2.0),(84.5,-2.0),(84.5,-10.5),(78,-10.5)]
WEND  = [(78,-10.5),(84.5,-10.5),(84.5,-22.5),(78,-22.5)]
BLKB  = [(90,13.5),(132,13.5),(132,-11.5),(90,-11.5)]
PARK  = [(9.0,18.0),(36,17.5),(36,44),(12,40)]
SHOPS = [(39.5,18.5),(57,21.0),(57,41),(39.5,41)]
if __name__=='__main__':
    from PIL import Image, ImageDraw
    im=Image.open(sys.argv[1]).convert('RGB'); d=ImageDraw.Draw(im); X0,Z0,S=-70,-165,4      # sys.argv[1]: ảnh mặt bằng 4 px/m, gốc (-70,-165)
    for nm,poly,c in [('WING',WING,(255,0,0)),('ANNEX',ANNEX,(255,128,0)),('TOWER',TOWER,(255,0,255)),('WEND',WEND,(255,128,0)),('BLKB',BLKB,(255,0,0)),('PARK',PARK,(0,255,0)),('SHOPS',SHOPS,(0,255,255))]:
        w=W(poly); d.polygon([((x-X0)*S,(z-Z0)*S) for x,z in w],outline=c,width=3); print(nm,[(round(x,1),round(z,1)) for x,z in w])
    lp=np.load('loop.npy'); d.line([((p[0]-X0)*S,(p[1]-Z0)*S) for p in lp]+[((lp[0][0]-X0)*S,(lp[0][1]-Z0)*S)],fill=(0,255,255),width=1)
    for s in range(-10,140,10):
        x,z=L(s,0); d.text(((x-X0)*S,(z-Z0)*S),str(s),fill=(255,255,0))
    im.crop((150,60,960,760)).save(sys.argv[2])
