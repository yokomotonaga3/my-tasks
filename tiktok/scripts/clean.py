import numpy as np, wave, sys
from numpy.lib.stride_tricks import sliding_window_view as swv
def readwav(p):
    w=wave.open(p); n=w.getnframes(); sr=w.getframerate(); ch=w.getnchannels()
    return np.frombuffer(w.readframes(n),dtype=np.int16).reshape(-1,ch).astype(np.float64)/32768, sr
def writewav(p,x,sr):
    w=wave.open(p,'wb'); w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes()); w.close()
x,sr=readwav(sys.argv[1]); out=sys.argv[2]
N=2048;H=256;win=np.hanning(N)
pad=np.pad(x,((N,N),(0,0)))
nf=(len(pad)-N)//H+1
def stft(s): return np.array([np.fft.rfft(s[i*H:i*H+N]*win) for i in range(nf)])
X=[stft(pad[:,c]) for c in range(x.shape[1])]
mag=sum(np.abs(z) for z in X)/len(X)
f=np.fft.rfftfreq(N,1/sr); t=(np.arange(nf)*H-N+N/2)/sr
hf=10*np.log10((mag[:,(f>10000)&(f<15500)]**2).sum(1)+1e-12); med=np.median(hf)
burst=hf>med+16
bd=burst.copy()
for d in range(1,7): bd[d:]|=burst[:-d]; bd[:-d]|=burst[d:]
# event onsets: wide strong bursts
ons=[-0.2];i=0
while i<nf:
    if hf[i]>med+30:
        j=i
        while j<nf and hf[j]>med+20: j+=1
        if (j-i)*H/sr>=0.02 and (not ons or t[i]-ons[-1]>0.12): ons.append(t[i])
        i=j
    else: i+=1
print("events:",[round(o,2) for o in ons])
def fmed(m,w=25):  # median across frequency
    p=np.pad(m,((0,0),(w//2,w//2)),mode='edge'); return np.median(swv(p,w,axis=1),axis=-1)
gain=np.ones_like(mag)
for o in ons:
    a=max(0,np.searchsorted(t,o-0.05)); b=min(nf,np.searchsorted(t,o+1.8))
    pre=slice(max(0,a-12),a)
    seg=mag[a:b]; sm=fmed(seg)
    ref=np.median(fmed(mag[pre]),axis=0)
    # 1) bursts: cap broadband to max(local smooth before, smooth envelope of later speech)
    for k in range(a,b):
        if bd[k]:
            L=[q for q in range(k-1,max(0,k-80),-1) if not bd[q]][:4]
            R=[q for q in range(k+1,min(nf,k+80)) if not bd[q]][:4]
            parts=[np.median(fmed(mag[q]),axis=0) for q in (L,R) if q]
            r=np.mean(parts,axis=0)*1.1
            g=np.minimum(1,r/(mag[k]+1e-9))
            gain[k]=np.minimum(gain[k],g)
    # 2) stationary tones after onset (f>900Hz)
    w0=max(0,np.searchsorted(t,o+0.12)-a); w1=np.searchsorted(t,o+0.5)-a
    ratio=seg[w0:w1]/(sm[w0:w1]+1e-9)
    tonal=(np.mean(ratio>3.0,axis=0)>0.6)&(f>900)
    idx=np.where(tonal)[0]
    tb=np.zeros(len(f),bool)
    for d in range(-3,4): tb[np.clip(idx+d,0,len(f)-1)]=True
    g=np.where(tb[None,:], np.minimum(1,sm*1.1/(seg+1e-9)),1)
    gain[a:b]=np.minimum(gain[a:b],g)
# also suppress constant ~7.4kHz whine
gk=(f>7300)&(f<7500)
ratio=mag/(fmed(mag)+1e-9)
gain[:,gk]=np.minimum(gain[:,gk],np.minimum(1,1.0/np.maximum(ratio[:,gk],1e-9)))
# smooth gain in time a bit
from functools import reduce
gs=gain.copy()
for s in (1,2):
    gs[s:]=np.minimum(gs[s:],gain[:-s]**0.5*1+0) if False else gs[s:]
Y=[]
for c,Z in enumerate(X):
    Z=Z*gain
    y=np.zeros(len(pad)); wsum=np.zeros(len(pad))
    for i in range(nf):
        y[i*H:i*H+N]+=np.fft.irfft(Z[i],N)*win; wsum[i*H:i*H+N]+=win**2
    Y.append((y/np.maximum(wsum,1e-6))[N:N+len(x)])
writewav(out,np.stack(Y,1),sr)
np.save(out+'.ons.npy',np.array(ons))
