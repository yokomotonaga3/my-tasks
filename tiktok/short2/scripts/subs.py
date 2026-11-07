import sys
P="{\\c&H00A04FFF&}"; Y="{\\c&H004DE1FF&}"; W="{\\c&H00FFFFFF&}"
def k(s): return s.replace("[",P).replace("]",W).replace("<",Y).replace(">",W)
def ts(t): h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h}:{m:02d}:{s:05.2f}"
head="""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Rounded Mplus 1c,48,&H00FFFFFF,&H00FFFFFF,&H00201010,&H64000000,1,0,0,0,100,100,1,0,1,5,2,2,60,60,285,1
Style: Pop,Noto Sans JP,96,&H00A04FFF,&H00FFFFFF,&H00FFFFFF,&H50000000,1,0,0,0,100,100,2,0,1,7,4,5,20,20,0,1
Style: HookS,Rounded Mplus 1c,40,&H00FFFFFF,&H00FFFFFF,&H00A04FFF,&H00A04FFF,1,0,0,0,100,100,2,0,3,10,0,5,20,20,0,1
Style: HookB,Noto Sans JP,86,&H00FFFFFF,&H00FFFFFF,&H00A04FFF,&H60000000,1,0,0,0,100,100,2,0,1,8,5,5,20,20,0,1
Style: End,Noto Sans JP,78,&H00FFFFFF,&H00FFFFFF,&H00A04FFF,&H60000000,1,0,0,0,100,100,2,0,1,7,4,5,20,20,0,1
Style: EndS,Rounded Mplus 1c,40,&H00FFFFFF,&H00FFFFFF,&H00201010,&H00000000,1,0,0,0,100,100,1,0,1,4,0,5,20,20,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
caps=[(0.30,2.15,"YouTubeのホスト動画見て"),(2.15,3.45,"[爆笑]してる子"),(3.55,4.95,"[稼ぐ側]に\\Nなりませんか？"),
(4.98,7.30,"画面の向こうで\\N楽しむだけじゃなくて"),(7.38,8.80,"今度は あなたが"),(8.80,10.90,"[稼ぐ側]で\\N最高に<チヤホヤ>されて"),
(10.95,13.08,"<ガッツリ>稼ぐ\\N[主人公]になれませんか？"),(13.12,15.55,"[見る側]から\\N[稼ぐ側]に回れば"),(15.58,17.62,"欲しかったものが\\N<ガッツリ>買えたり"),
(17.66,19.82,"欲しかったブランドや\\N[推し活]も"),(19.86,21.92,"<全部自分の力で>\\N叶えられます"),(21.98,23.42,"[見る専]を [卒業]して"),
(23.48,25.76,"自分史上\\N[一番輝く]スタート"),(25.80,27.27,"<僕がサポートします>")]
pops=[(3.62,"稼ぐ側に"),(11.75,"主人公に"),(19.90,"全部自分の力で"),(24.20,"一番輝く")]
anim="{\\fad(60,200)\\fscx40\\fscy40\\t(0,110,\\fscx118\\fscy118)\\t(110,220,\\fscx100\\fscy100)}"
ev=[]
for s,e,t in caps: ev.append(f"Dialogue: 1,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\fad(40,40)}}{k(t)}")
for s,t in pops:
    sz=96 if len(t)<=5 else 74
    ev.append(f"Dialogue: 2,{ts(s)},{ts(s+1.25)},Pop,,0,0,0,,{{\\pos(360,745)\\fs{sz}\\1c&H00A04FFF&\\3c&HFFFFFF&}}{anim}{t}")
# hook / thumbnail (0-2.1s)
ev.append(f"Dialogue: 3,{ts(0)},{ts(2.1)},HookS,,0,0,0,,{{\\pos(360,150)\\fad(0,150)}} “見る専”の女の子へ ")
ev.append(f"Dialogue: 3,{ts(0)},{ts(2.1)},HookB,,0,0,0,,{{\\pos(360,275)\\fad(0,150)}}推し活のお金\\N{P}{{\\3c&HFFFFFF&}}自分で稼げたら？")
# end card
E=27.27; F=float(sys.argv[2])
ev.append(f"Dialogue: 3,{ts(E)},{ts(F)},End,,0,0,0,,{{\\pos(360,560)\\fad(150,0)}}気になったら\\N{P}{{\\3c&HFFFFFF&}}DMまってます")
ev.append(f"Dialogue: 3,{ts(E+0.25)},{ts(F)},EndS,,0,0,0,,{{\\pos(360,740)\\fad(150,0)}}話を聞くだけでもOK")
open(sys.argv[1],"w").write(head+"\n".join(ev)+"\n")
