import json,sys
v=[float(x) for x in open(sys.argv[1]).read().split()]
sil=[(v[i],v[i+1] if i+1<len(v) else 1e9) for i in range(0,len(v),2)]
takes=[("A",2.45,6.0),("B",6.6,8.1),("C",31.15,33.8),("D",36.7,41.6),("E",47.9,50.1),("F",64.8,67.7),
       ("G",67.8,71.2),("H",79.5,81.75),("I",82.9,85.7),("J",90.2,92.0),("K",96.3,99.1),("L",99.25,100.9)]
PAD=0.10; MAXGAP=0.18
out=[]
for name,a,b in takes:
    segs=[[a,b]]
    for s,e in sil:
        if e-s<=MAXGAP+2*PAD: continue
        ns=[]
        for x,y in segs:
            cs,ce=s+PAD,e-PAD
            if ce<=x or cs>=y: ns.append([x,y]); continue
            if cs>x: ns.append([x,cs])
            if ce<y: ns.append([ce,y])
        segs=ns
    segs=[sg for sg in segs if sg[1]-sg[0]>0.12]
    for sg in segs: out.append((name,round(sg[0],3),round(sg[1],3)))
json.dump(out,open(sys.argv[2],'w'))
t=0
for n,a,b in out: print(n,a,b,f"-> {t:.2f}-{t+b-a:.2f}"); t+=b-a
print("total",round(t,2))
