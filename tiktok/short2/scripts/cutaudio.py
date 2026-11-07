import json,sys,numpy as np
edl=json.load(open(sys.argv[1])); a=np.fromfile(sys.argv[2],dtype=np.float32); sr=16000
parts=[]
for n,s,e in edl:
    x=a[int(s*sr):int(e*sr)].copy(); f=int(0.01*sr); x[:f]*=np.linspace(0,1,f); x[-f:]*=np.linspace(1,0,f); parts.append(x)
np.concatenate(parts).tofile(sys.argv[3])
