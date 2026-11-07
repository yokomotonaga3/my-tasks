import numpy as np, wave
sr=44100; rng=np.random.default_rng(7)
def env(n,a,d): t=np.arange(n)/sr; return np.minimum(t/a,1)*np.exp(-t/d)
def tone(f,dur,a=0.003,d=0.25,harm=((1,1),(2,.35),(3,.12),(4.2,.08))):
    n=int(dur*sr); t=np.arange(n)/sr
    return sum(g*np.sin(2*np.pi*f*h*t)*np.exp(-t/(d/(h**0.5))) for h,g in harm)*np.minimum(t/a,1)
def place(buf,x,t0):
    i=int(t0*sr); buf[i:i+len(x)]+=x[:max(0,len(buf)-i)]
def sparkle(dur=0.7,count=14,lo=3500,hi=9000,start=0.0):
    b=np.zeros(int((dur+0.5)*sr))
    for k in range(count):
        t0=start+dur*(k/count)+rng.uniform(0,0.03)
        f=rng.uniform(lo,hi); x=tone(f,0.35,0.001,0.06,((1,1),))*rng.uniform(0.25,0.6)*(1-0.6*k/count)
        place(b,x,t0)
    return b
def stereo(m,width=0.0):
    # tiny haas for width
    d=int(0.008*sr); r=np.concatenate([np.zeros(d),m])[:len(m)]
    return np.stack([m*(1-width)+m*width, m*(1-width)+r*width],1)
def pikon():  # ひらめき「ピコーン！」: whoosh up + two-note bell + sparkle tail
    L=int(1.6*sr); b=np.zeros(L)
    # rising whoosh (filtered noise sweep)
    n=int(0.18*sr); t=np.arange(n)/sr
    glide=np.sin(2*np.pi*np.cumsum(np.geomspace(500,1500,n))/sr)
    place(b,glide*0.18*np.sin(np.pi*t/t[-1])**2,0.0)
    place(b,tone(1567.98,1.2,0.002,0.10)*0.55,0.17)   # G6 「ピ」
    place(b,tone(2093.0,1.0,0.002,0.28)*0.65,0.255)   # C7 「コーン」
    place(b,tone(3135.96,1.0,0.002,0.25)*0.18,0.255)
    place(b,sparkle(0.4,6,4000,9000,0.0)*0.3,0.28)
    return stereo(b,0.6)
def kira():  # 軽い「キラッ」: quick upward 3-note arpeggio + sparkle
    L=int(1.0*sr); b=np.zeros(L)
    for i,f in enumerate((2637.0,3135.96,3951.07)):
        place(b,tone(f,0.6,0.001,0.12,((1,1),(2,.25)))*0.32,i*0.035)
    place(b,sparkle(0.35,8,5000,11000)*0.35,0.06)
    return stereo(b,0.6)
def norm(x,peak): return x/np.abs(x).max()*peak
def save(p,x):
    w=wave.open(p,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes())
P=norm(pikon(),0.3); K=norm(kira(),0.32)
save('se_pikon.wav',P); save('se_kira.wav',K)
dur=23.75; tr=np.zeros((int(dur*sr)+sr,2))
big=[2.44,8.50,16.96,20.16,22.45]
small=[]
lead=0.17  # pikon's bell hits 0.17s after its start -> align bell to caption change
for t in big: place(tr[:,0],P[:,0],max(0,t-lead)); place(tr[:,1],P[:,1],max(0,t-lead))
for t in small: place(tr[:,0],K[:,0],t); place(tr[:,1],K[:,1],t)
save('se_track.wav',tr[:int(dur*sr)])
