import json,subprocess,sys,numpy as np,wave
S=sys.argv[1]; src=sys.argv[2]; out=sys.argv[3]
edl=json.load(open(f"{S}/v2/edl.json"))
import os; BGV=os.environ.get("BGV","0.55")
pops=[3.62,11.75,19.90,24.20]; END=1.8
# SE track
w=wave.open(f"{S}/se_pikon.wav"); P=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,2)/32768
sr=44100; tot=sum(e-s for _,s,e in edl)+END; tr=np.zeros((int((tot+2)*sr),2))
for t in pops: i=int((t-0.17)*sr); tr[i:i+len(P)]+=P
ww=wave.open(f"{S}/v2/se.wav","wb"); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(sr); ww.writeframes((np.clip(tr,-1,1)*32767).astype(np.int16).tobytes()); ww.close()
fc=[]; vs=[]; as_=[]
for i,(n,s,e) in enumerate(edl):
    z=1.0 if i%2==0 else 1.09
    fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,scale=w=2*trunc(720*{z}/2):h=-2,crop=720:1280:(iw-720)/2:(ih-1280)*0.3[v{i}]")
    fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={e-s-0.012:.3f}:d=0.012[a{i}]")
    vs.append(f"[v{i}][a{i}]")
fc.append("".join(vs)+f"concat=n={len(edl)}:v=1:a=1[vc][ac]")
Z="1"+"".join(f"+if(gte(t\\,{t})\\,0.07*exp(-(t-{t})*5)\\,0)" for t in pops)
fc.append(f"[vc]tpad=stop_mode=clone:stop_duration={END},scale=w='2*trunc(720*({Z})/2)':h='2*trunc(1280*({Z})/2)':eval=frame,crop=720:1280,setsar=1,"
          f"eq=saturation=1.08:contrast=1.04:brightness=0.015,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.45:t=fill:enable='gte(t,{tot-END:.2f})',"
          f"subtitles=subs.ass:fontsdir={S}/fonts[v]")
fc.append(f"[ac]apad=pad_dur={END},highpass=f=80,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,asplit=2[vo][sc]")
fc.append(f"[1:a]atrim=0:{tot:.2f},volume={BGV}[bg]")
fc.append("[bg][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[bgd]")
fc.append(f"[2:a]atrim=0:{tot:.2f}[se]")
fc.append("[vo][bgd][se]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1:LRA=9,aresample=44100[a]")
cmd=["ffmpeg","-v","error","-y","-i",src,"-i",f"{S}/v2/bgm.wav","-i",f"{S}/v2/se.wav","-filter_complex",";".join(fc),
     "-map","[v]","-map","[a]","-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-r","30",
     "-c:a","aac","-b:a","192k","-movflags","+faststart","-t",f"{tot:.2f}",out]
subprocess.run(cmd,check=True,cwd=f"{S}/v2")
print("total",tot)
