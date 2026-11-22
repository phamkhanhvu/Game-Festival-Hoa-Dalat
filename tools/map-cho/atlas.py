# Mở rộng atlas 1024x1024 -> 1024x2048: nửa trên giữ nguyên atlas cũ, nửa dưới là 16 ô mới cho khu cầu thang chợ
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FC='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
T=256
rng=np.random.RandomState(7)
def noise(img,amt=5):
    a=np.asarray(img).astype(np.int16); n=rng.randint(-amt,amt+1,a.shape[:2])[:,:,None]
    return Image.fromarray(np.clip(a+n,0,255).astype(np.uint8))
def tile(bg=(236,232,224)):
    return Image.new('RGB',(T,T),bg)
WALL=(236,232,224); GLASS1=(70,96,128); GLASS2=(98,128,160); FR=(250,250,248)
def glass(d,x0,y0,x1,y1,dark=GLASS1,light=GLASS2):
    d.rectangle([x0,y0,x1,y1],fill=dark)
    w=x1-x0; d.polygon([(x0,y0),(x0+w*0.55,y0),(x0,y0+(y1-y0)*0.6)],fill=light)
def fit(d,text,box,fill,font=F,maxsize=120,stroke=0,sfill=None):
    x0,y0,x1,y1=box; s=maxsize
    while s>6:
        f=ImageFont.truetype(font,s); b=d.textbbox((0,0),text,font=f,stroke_width=stroke)
        if b[2]-b[0]<=x1-x0 and b[3]-b[1]<=y1-y0: break
        s-=2
    d.text(((x0+x1)/2-(b[0]+b[2])/2,(y0+y1)/2-(b[1]+b[3])/2),text,font=f,fill=fill,stroke_width=stroke,stroke_fill=sfill)
tiles={}
# (0,4) cửa sổ khách sạn hiện đại + bồn hoa
t=tile(); d=ImageDraw.Draw(t)
d.rectangle([44,46,212,196],fill=FR); glass(d,52,54,124,188); glass(d,132,54,204,188)
d.rectangle([36,196,220,210],fill=(206,200,190)); d.rectangle([40,210,216,216],fill=(170,164,154))
for x in range(46,214,12): d.ellipse([x-7,186,x+7,200],fill=(74,128,60))
for x in range(52,214,24): d.ellipse([x-3,184,x+3,190],fill=(214,74,96))
d.rectangle([0,244,T,T],fill=(222,217,208))
tiles[(0,4)]=noise(t,4)
# (1,4) cửa vòm có ban công sắt
t=tile(); d=ImageDraw.Draw(t)
d.pieslice([70,26,186,142],180,360,fill=FR); d.rectangle([70,84,186,214],fill=FR)
d.pieslice([78,34,178,134],180,360,fill=GLASS1); glass(d,78,84,124,214); glass(d,132,84,178,214)
d.rectangle([124,34,132,214],fill=FR); d.rectangle([78,80,178,88],fill=FR)
d.rectangle([40,214,216,226],fill=(196,190,180))
d.rectangle([44,150,212,156],fill=(52,52,58))
for x in range(46,214,11): d.rectangle([x,150,x+2,214],fill=(52,52,58))
d.rectangle([0,244,T,T],fill=(222,217,208))
tiles[(1,4)]=noise(t,4)
# (2,4) vách kính có đố
t=Image.new('RGB',(T,T),(84,112,144)); d=ImageDraw.Draw(t)
for i in range(T):
    c=int(30*(1-i/T)); d.line([(0,i),(T,i)],fill=(78+c,106+c,138+c))
d.polygon([(0,0),(150,0),(0,170)],fill=(112,142,172)); d.polygon([(170,0),(210,0),(40,T),(0,T),(0,220)],fill=(100,130,162))
for x in [0,85,170,253]: d.rectangle([x,0,x+3,T],fill=(232,234,236))
for y in [0,125,252]: d.rectangle([0,y,T,y+3],fill=(232,234,236))
tiles[(2,4)]=noise(t,3)
# (3,4) lan can kính
t=Image.new('RGB',(T,T),(196,216,226)); d=ImageDraw.Draw(t)
d.polygon([(0,40),(120,40),(0,200)],fill=(214,230,238)); d.polygon([(150,40),(200,40),(70,T),(20,T)],fill=(208,226,234))
d.rectangle([0,0,T,26],fill=(238,238,236)); d.rectangle([0,26,T,34],fill=(150,156,160))
for x in [0,126,250]: d.rectangle([x,26,x+6,T],fill=(168,174,178))
d.rectangle([0,244,T,T],fill=(232,232,228))
tiles[(3,4)]=noise(t,3)
# (0,5) mái mansard đá xám + cửa sổ mái
t=Image.new('RGB',(T,T),(96,102,110)); d=ImageDraw.Draw(t)
for r in range(0,T,20):
    off=10 if (r//20)%2 else 0
    d.line([(0,r),(T,r)],fill=(74,80,88),width=2)
    for x in range(-20+off,T,20): d.line([(x,r),(x,r+20)],fill=(82,88,96),width=1)
d.polygon([(74,70),(128,30),(182,70)],fill=(70,76,84)); d.rectangle([80,70,176,214],fill=FR); glass(d,90,82,124,204); glass(d,132,82,166,204)
d.rectangle([0,236,T,T],fill=(222,217,208))
tiles[(0,5)]=noise(t,4)
# (1,5) mặt tiền cửa hàng hiện đại
t=tile((60,44,44)); d=ImageDraw.Draw(t)
d.rectangle([0,0,T,T],fill=(52,40,40))
d.rectangle([10,14,246,244],fill=(238,206,150))
for i in range(14,244): 
    c=int(40*(i-14)/230); d.line([(10,i),(246,i)],fill=(244-c//2,214-c,160-c))
for sy in [70,130,190]:
    d.rectangle([18,sy,238,sy+5],fill=(120,84,60))
    for x in range(24,236,22):
        col=[(196,60,60),(230,170,60),(96,150,84),(240,236,220),(150,90,60)][(x//22+sy)%5]
        d.rectangle([x,sy-26,x+14,sy],fill=col)
d.rectangle([122,14,134,244],fill=(52,40,40)); d.rectangle([0,0,T,14],fill=(40,30,30)); d.rectangle([0,244,T,T],fill=(88,84,82))
d.polygon([(10,14),(110,14),(10,150)],fill=(250,230,190))
tiles[(1,5)]=noise(t,3)
# (2,5) biển: KHÁCH SẠN / HOTEL
t=tile((30,84,160)); d=ImageDraw.Draw(t)
d.rectangle([0,0,T,127],fill=(28,86,170)); d.rectangle([4,4,T-5,123],outline=(255,255,255),width=3); fit(d,'KHÁCH SẠN',(16,22,240,106),(255,255,255),maxsize=60)
d.rectangle([0,128,T,T],fill=(20,40,92)); d.rectangle([4,132,T-5,T-5],outline=(240,200,90),width=3); fit(d,'HOTEL',(24,150,232,222),(250,224,140),maxsize=80)
tiles[(2,5)]=t
# (3,5) biển: NGÂN HÀNG / QUÀ LƯU NIỆM
t=tile((250,250,250)); d=ImageDraw.Draw(t)
d.rectangle([0,0,T,127],fill=(24,70,150)); d.rectangle([0,96,T,127],fill=(240,130,30)); fit(d,'NGÂN HÀNG',(14,14,242,88),(255,255,255),maxsize=60)
d.rectangle([0,128,T,T],fill=(196,30,36)); d.rectangle([5,133,T-6,T-6],outline=(255,236,200),width=2); fit(d,'QUÀ LƯU NIỆM',(14,150,242,236),(255,244,220),font=FC,maxsize=60)
tiles[(3,5)]=t
# (0,6) biển cửa hàng đặc sản
t=tile((74,28,30)); d=ImageDraw.Draw(t)
d.rectangle([0,0,T,127],fill=(72,26,30)); fit(d,'ĐẶC SẢN ĐÀ LẠT',(10,26,246,100),(250,244,232),font=FC,maxsize=60); d.rectangle([0,118,T,127],fill=(196,150,80))
d.rectangle([0,128,T,T],fill=(84,32,34)); fit(d,'mứt · trà · cà phê',(16,160,240,224),(236,206,150),font=FC,maxsize=40)
tiles[(0,6)]=t
# (1,6) chữ nổi sân thượng
t=tile((244,244,242)); d=ImageDraw.Draw(t)
fit(d,'SÂN THƯỢNG',(8,18,248,110),(120,126,134),maxsize=60)
d.rectangle([0,128,T,T],fill=(244,244,242)); fit(d,'CÀ PHÊ',(30,150,226,236),(120,126,134),maxsize=70)
tiles[(1,6)]=t
# (2,6) logo tròn cam + hoa trắng
t=tile((248,244,236)); d=ImageDraw.Draw(t)
d.ellipse([20,20,236,236],fill=(238,124,36)); d.ellipse([34,34,222,222],outline=(255,236,210),width=5)
for k in range(8):
    a=k*math.pi/4; cx=128+math.cos(a)*48; cy=128+math.sin(a)*48
    d.ellipse([cx-24,cy-24,cx+24,cy+24],fill=(255,250,240))
d.ellipse([104,104,152,152],fill=(250,206,70))
tiles[(2,6)]=t
# (3,6) bảng quảng cáo xanh trên mái
t=tile((40,150,90)); d=ImageDraw.Draw(t)
for i in range(T): d.line([(0,i),(T,i)],fill=(36+i//10,146+i//8,84+i//12))
d.polygon([(40,200),(70,110),(100,200)],fill=(22,100,60)); d.polygon([(48,150),(70,70),(92,150)],fill=(22,100,60)); d.rectangle([66,200,74,226],fill=(60,44,30))
fit(d,'ĐÀ LẠT',(112,70,244,150),(255,255,255),maxsize=60); fit(d,'thành phố ngàn hoa',(112,156,244,200),(236,250,236),font=FC,maxsize=26)
d.rectangle([3,3,T-4,T-4],outline=(250,250,250),width=4)
tiles[(3,6)]=t
# (0,7) tán bách tán
t=Image.new('RGB',(T,T),(44,84,52)); d=ImageDraw.Draw(t)
for k in range(520):
    x=rng.randint(0,T); y=rng.randint(0,T); L=rng.randint(10,26); a=rng.uniform(-0.5,0.5)+math.pi/2
    g=rng.randint(0,3); col=[(30,66,40),(58,104,62),(40,78,48)][g]
    d.line([(x,y),(x+math.cos(a)*L,y+math.sin(a)*L)],fill=col,width=3)
tiles[(0,7)]=t.filter(ImageFilter.GaussianBlur(0.6))
# (1,7) tán liễu rủ
t=Image.new('RGB',(T,T),(132,168,74)); d=ImageDraw.Draw(t)
for k in range(420):
    x=rng.randint(-10,T+10); y=rng.randint(-30,T); L=rng.randint(40,110)
    col=[(104,146,60),(150,186,86),(120,160,66),(168,198,104)][rng.randint(0,4)]
    d.line([(x,y),(x+rng.randint(-5,6),y+L)],fill=col,width=3)
tiles[(1,7)]=t.filter(ImageFilter.GaussianBlur(0.7))
# (2,7) bê tông bậc thang (hạt nhỏ, mép bậc sẫm)
a=np.full((T,T,3),226,np.int16)+rng.randint(-9,10,(T,T,1)); a[:,:,2]-=6
t=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)); d=ImageDraw.Draw(t)
for k in range(90):
    x=rng.randint(0,T); y=rng.randint(0,T); r=rng.randint(1,3); c=rng.randint(196,214); d.ellipse([x-r,y-r,x+r,y+r],fill=(c,c,c-6))
tiles[(2,7)]=t
# (3,7) tường kè đá hộc
t=Image.new('RGB',(T,T),(120,112,100)); d=ImageDraw.Draw(t)
y=0; row=0
while y<T:
    hgt=rng.randint(34,48); x=-rng.randint(0,40)
    while x<T:
        w=rng.randint(44,84); c=rng.randint(-14,15); col=(196+c,188+c,172+c)
        d.rounded_rectangle([x+3,y+3,x+w-3,y+hgt-3],radius=8,fill=col)
        x+=w
    y+=hgt
tiles[(3,7)]=noise(t.filter(ImageFilter.GaussianBlur(0.5)),5)

# ================= Ô mới cho khu đầu cầu Khu Hòa Bình (cột 4..7; atlas rộng 2048) =================
def streaks(img,n=26,amt=26,seed=3):
    r=np.random.RandomState(seed); a=np.asarray(img).astype(np.int16).copy()
    for _ in range(n):
        x=r.randint(0,T); w=r.randint(3,14); y0=r.randint(0,T//2); ln=r.randint(40,200); k=r.randint(6,amt)
        for yy in range(y0,min(T,y0+ln)):
            f=1-(yy-y0)/ln; a[yy,max(0,x-w//2):x+w//2]-=int(k*f)
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def greywall():
    t=Image.new('RGB',(T,T),(178,178,172)); d=ImageDraw.Draw(t)
    for y in range(0,T,32): d.line([(0,y),(T,y)],fill=(150,150,146),width=2); d.line([(0,y+2),(T,y+2)],fill=(192,192,186),width=1)
    return t
# (5,0) tường xám cũ có cửa sổ hai cánh ô kính nhỏ và ô văng
t=greywall(); d=ImageDraw.Draw(t)
d.rectangle([54,50,202,60],fill=(200,200,194)); d.rectangle([54,60,202,64],fill=(120,120,116))
d.rectangle([68,66,188,198],fill=(214,214,206)); d.rectangle([62,198,194,206],fill=(196,196,190)); d.rectangle([62,206,194,209],fill=(126,126,122))
for lx in (74,131):
    d.rectangle([lx,72,lx+51,192],fill=(232,232,226))
    for cx in range(2):
        for cy in range(3):
            x0=lx+4+cx*24; y0=76+cy*39; glass(d,x0,y0,x0+20,y0+34,(84,100,114),(124,142,156))
tiles[(5,0)]=noise(streaks(t,30,30,5).filter(ImageFilter.GaussianBlur(0.4)),5)
# (6,0) tường xám cũ trơn
tiles[(6,0)]=noise(streaks(greywall(),34,30,9).filter(ImageFilter.GaussianBlur(0.4)),5)
# (7,0) mảng lam đứng giữa mặt tiền: nền vàng, năm thanh lam xám
t=Image.new('RGB',(T,T),(206,172,84)); d=ImageDraw.Draw(t)
for k in range(5):
    x=22+k*46; d.rectangle([x,0,x+24,T],fill=(176,176,170)); d.rectangle([x+24,0,x+30,T],fill=(124,112,70)); d.line([(x,0),(x,T)],fill=(206,206,200),width=2)
d.rectangle([0,0,T,8],fill=(170,170,164)); d.rectangle([0,T-8,T,T],fill=(170,170,164))
tiles[(7,0)]=noise(streaks(t,22,26,11).filter(ImageFilter.GaussianBlur(0.4)),5)
# (4,1) băng ô thoáng trên mái hiên: dãy khe đứng
t=Image.new('RGB',(T,T),(108,106,100)); d=ImageDraw.Draw(t)
d.rectangle([0,0,T,40],fill=(128,126,120)); d.rectangle([0,T-44,T,T],fill=(88,86,82))
for x in range(8,T,22): d.rectangle([x,56,x+11,T-60],fill=(28,28,30)); d.line([(x+11,56),(x+11,T-60)],fill=(150,148,142),width=1)
tiles[(4,1)]=noise(t,5)
# (5,1) tường tấm bê tông màu be (khối rạp)
t=Image.new('RGB',(T,T),(214,200,168)); d=ImageDraw.Draw(t)
for i in range(2):
    for j in range(2):
        c=rng.randint(-7,8); d.rectangle([i*128+2,j*128+2,i*128+125,j*128+125],fill=(214+c,200+c,168+c))
for v in (0,128,255): d.line([(v,0),(v,T)],fill=(150,138,112),width=3); d.line([(0,v),(T,v)],fill=(150,138,112),width=3)
tiles[(5,1)]=noise(streaks(t,18,18,13).filter(ImageFilter.GaussianBlur(0.4)),4)
# (6,1) mặt bồn hoa: lá xanh, hoa tím hồng vàng
t=Image.new('RGB',(T,T),(64,124,58)); d=ImageDraw.Draw(t)
for _ in range(260):
    x=rng.randint(0,T); y=rng.randint(0,T); r=rng.randint(4,10); c=rng.randint(-18,19); d.ellipse([x-r,y-r,x+r,y+r],fill=(64+c,124+c,58+c))
for _ in range(210):
    x=rng.randint(0,T); y=rng.randint(0,T); r=rng.randint(3,7); col=[(150,92,196),(232,120,172),(244,214,84),(250,246,240),(196,74,150)][rng.randint(0,5)]
    d.ellipse([x-r,y-r,x+r,y+r],fill=col)
tiles[(6,1)]=noise(t,4)
# (4,0) biển chữ chung: TIỆM ẢNH (nền xanh), GIẢI KHÁT (nền kem), CÀ PHÊ và KI-ỐT SỐ 1 (nền than)
t=Image.new('RGB',(T,T),(30,64,150)); d=ImageDraw.Draw(t)
d.rectangle([3,3,T-4,72],outline=(236,236,244),width=2)
fit(d,'TIỆM ẢNH',(18,8,238,46),(255,214,90),F,60)
fit(d,'chụp ảnh thẻ · chân dung · phục hồi ảnh',(12,48,244,68),(240,240,248),FC,20)
d.rectangle([0,76,T,127],fill=(246,236,214)); d.rectangle([2,78,T-3,125],outline=(196,40,40),width=2)
fit(d,'GIẢI KHÁT · CÀ PHÊ',(10,82,246,122),(196,40,40),FC,44)
d.rectangle([0,128,T,T],fill=(34,34,38)); d.line([(0,191),(T,191)],fill=(70,70,76),width=2)
fit(d,'CÀ PHÊ',(40,134,216,186),(246,244,236),F,60)
fit(d,'KI-ỐT SỐ 1',(24,198,232,250),(246,244,236),F,56)
tiles[(4,0)]=t
# (4,2) biển BÃI ĐẬU XE
t=Image.new('RGB',(T,T),(28,84,170)); d=ImageDraw.Draw(t)
d.rectangle([4,4,T-5,80],outline=(240,240,248),width=3); fit(d,'BÃI ĐẬU XE',(16,12,240,74),(255,255,255),F,60)
d.rectangle([0,86,T,T],fill=(236,232,224))
tiles[(4,2)]=t
def build(old_path,out_path):
    old=Image.open(old_path).convert('RGB'); assert old.size==(1024,1024)
    A=Image.new('RGB',(2048,2048),(236,232,224)); A.paste(old,(0,0))
    for (c,r),im in tiles.items(): A.paste(im.resize((T,T)),(c*T,r*T))
    A.save(out_path,quality=88,optimize=True)
    return A
if __name__=='__main__':
    A=build('/home/claude/work/atlas.jpg','/home/claude/work/build/atlas2.jpg')
    import os; print(os.path.getsize('/home/claude/work/build/atlas2.jpg'))
    A.crop((1024,0,2048,768)).save('/home/claude/work/build/atlas_new_cols.png')
