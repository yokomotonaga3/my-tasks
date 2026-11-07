import numpy as np, wave, sys
sr=44100; rng=np.random.default_rng(3)
BPM=92; beat=60/BPM; bar=4*beat
dur=float(sys.argv[2]); N=int((dur+2)*sr)
L=np.zeros(N); R=np.zeros(N)
def add(x,t,pan=0.0,g=1.0):
    i=int(t*sr); n=min(len(x),N-i)
    if n<=0: return
    L[i:i+n]+=x[:n]*g*(1-pan)*0.5*2**0.5*(1 if pan<=0 else 1-pan) if False else x[:n]*g*np.sqrt((1-pan)/2)*1.414
    R[i:i+n]+=x[:n]*g*np.sqrt((1+pan)/2)*1.414
def mtof(m): return 440*2**((m-69)/12)
def epiano(f,d=1.8):
    n=int(d*sr); t=np.arange(n)/sr
    x=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)*np.exp(-t*6)+0.08*np.sin(2*np.pi*3*f*t)*np.exp(-t*9)
    x*=np.exp(-t*1.6)*np.minimum(t/0.006,1)*(1+0.12*np.sin(2*np.pi*4.5*t))
    return x
def pluck(f,d=0.5):
    n=int(d*sr); t=np.arange(n)/sr
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*np.exp(-t*9)*np.minimum(t/0.003,1)
def bass(f,d):
    n=int(d*sr); t=np.arange(n)/sr
    return np.sin(2*np.pi*f*t)*np.minimum(t/0.01,1)*np.minimum(1,(d-t)/0.05)
def kick():
    n=int(0.35*sr); t=np.arange(n)/sr; f=45+90*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t*9)
def lp(x,a): # one-pole lowpass
    y=np.empty_like(x); s=0.0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
def snap():
    n=int(0.18*sr); t=np.arange(n)/sr; x=rng.normal(0,1,n)
    x=x-lp(x,0.15); return x*np.exp(-t*28)*0.5
def hat():
    n=int(0.05*sr); t=np.arange(n)/sr; x=rng.normal(0,1,n); x=x-lp(x,0.5)
    return x*np.exp(-t*80)*0.25
# 王道進行 IV-V-iii-vi in C : F G Em Am  (voicings with 7ths for emo feel)
chords=[[53,57,60,64],[55,59,62,65],[52,55,59,62],[57,60,64,67]]
roots=[41,43,40,45]
arp_pat=[0,1,2,3,2,1,3,2]
nbars=int(np.ceil((dur+1)/bar))
K=kick(); Sn=snap(); Hh=hat()
for b in range(nbars):
    c=chords[b%4]; t0=b*bar
    for k,m in enumerate(c): add(epiano(mtof(m)),t0+0.012*k,pan=(-0.3+0.2*k),g=0.16)
    add(epiano(mtof(c[0]),1.0),t0+2.5*beat,pan=0.2,g=0.08)
    add(bass(mtof(roots[b%4]),bar*0.95),t0,g=0.30)
    for i in range(8):
        add(pluck(mtof(c[arp_pat[i]]+12)),t0+i*beat/2,pan=0.45 if i%2 else -0.45,g=0.07)
    if b>=1:  # drums come in after intro bar
        add(K,t0,g=0.55); add(K,t0+2*beat,g=0.5); add(K,t0+2.75*beat,g=0.25)
        add(Sn,t0+beat,pan=0.1,g=0.35); add(Sn,t0+3*beat,pan=0.1,g=0.35)
        for i in range(8): add(Hh,t0+i*beat/2+(0.02 if i%2 else 0),pan=0.3,g=0.3 if i%2 else 0.5)
# vinyl crackle
cr=np.zeros(N); idx=rng.integers(0,N,int(dur*6)); cr[idx]=rng.normal(0,0.04,len(idx)); cr=lp(cr,0.3)
L+=cr; R+=cr
x=np.stack([L,R],1)[:int(dur*sr)]
# fade in/out
fi=int(0.3*sr); fo=int(1.5*sr); x[:fi]*=np.linspace(0,1,fi)[:,None]; x[-fo:]*=np.linspace(1,0,fo)[:,None]
x/=np.abs(x).max()*1.12
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x*32767).astype(np.int16).tobytes())
