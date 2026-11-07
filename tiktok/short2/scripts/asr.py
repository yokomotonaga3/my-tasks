import sys,json
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device="cpu",compute_type="int8")
import numpy as np
segs,_=m.transcribe(np.fromfile(sys.argv[2],dtype=np.float32),language="ja",word_timestamps=True,vad_filter=False,beam_size=5,condition_on_previous_text=False)
out=[]
for s in segs:
    w=[(x.start,x.end,x.word) for x in s.words]
    out.append({"s":s.start,"e":s.end,"t":s.text,"w":w}); print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}",flush=True)
json.dump(out,open(sys.argv[3],"w"),ensure_ascii=False)
