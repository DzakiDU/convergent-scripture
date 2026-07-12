#!/usr/bin/env python3
"""Bangun korpus ayat muamalah lintas-ASEAN (teks bersih, tanpa OCR).
Sumber: QuranEnc API (id/th/tl + footnote) & Quran.com API (Melayu Basmeih=39).
Output: data/economic_verses_aligned.csv
"""
import urllib.request, json, time, csv, re, os

UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120 Safari/537.36"}

# --- Peta konsep muamalah -> ayat jangkar ---
DOMAIN = {
 "riba": ["2:275","2:276","2:277","2:278","2:279","2:280","3:130","30:39","4:161"],
 "bay-jualbeli": ["2:282","4:29","62:9"],
 "gharar-maysir-judi": ["2:219","5:90","5:91"],
 "uqud-akad-janji": ["5:1","17:34","16:91","23:8"],
 "amanah-trust": ["4:58","8:27","2:283"],
 "mizan-timbangan-adil": ["55:9","83:1","83:2","83:3","17:35","6:152","7:85","11:84","11:85"],
 "harta-batil-suap": ["2:188"],
 "zakat-infaq": ["2:43","2:110","2:261","2:267","9:60","9:103"],
 "distribusi-kekayaan": ["59:7"],
 "penimbunan-kanz": ["9:34","9:35"],
 "harta-anak-yatim": ["4:2","4:5","4:6","4:10"],
 "wasiat": ["2:180"],
 "warisan-faraid": ["4:7","4:11","4:12","4:176"],
 "infaq-etika": ["2:262","2:264","2:271","63:10"],
 "rezeki-kerja-halal": ["62:10","67:15"],
}
tema={v:d for d,vs in DOMAIN.items() for v in vs}
verses=list(tema.keys())

def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=25) as r: return json.load(r)

def qenc(key,s,a):
    try:
        d=fetch(f"https://quranenc.com/api/v1/translation/aya/{key}/{s}/{a}")["result"]
        return d.get("translation",""), d.get("footnotes",""), d.get("arabic_text","")
    except Exception as e:
        return f"[ERR {e}]","",""

def clean(html):
    html=re.sub(r"<sup[^>]*>.*?</sup>","",html); html=re.sub(r"<[^>]+>","",html)
    return html.strip()

def qcom(tid,key):
    try:
        d=fetch(f"https://api.quran.com/api/v4/quran/translations/{tid}?verse_key={key}")
        return clean(d["translations"][0]["text"])
    except Exception as e:
        return f"[ERR {e}]"

rows=[]
for v in sorted(verses,key=lambda x:(int(x.split(':')[0]),int(x.split(':')[1]))):
    s,a=v.split(":")
    tid,fid,ar=qenc("indonesian_affairs",s,a)
    ttl,ftl,_=qenc("tagalog_rwwad",s,a)
    tth,_,_ =qenc("thai_rwwad",s,a)
    tms=qcom(39,v)  # Melayu Basmeih (= basis JAKIM)
    rows.append({"surah_ayat":v,"tema":tema[v],"arabic":ar,
                 "terjemah_id":tid,"footnote_id":fid,"terjemah_ms":tms,
                 "terjemah_th":tth,"terjemah_tl":ttl,"footnote_tl":ftl})
    time.sleep(0.15)

cols=["surah_ayat","tema","arabic","terjemah_id","footnote_id","terjemah_ms",
      "terjemah_th","terjemah_tl","footnote_tl"]
here=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out=os.path.join(here,"data","economic_verses_aligned.csv")
with open(out,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
errs=sum(1 for r in rows for k in r if str(r[k]).startswith("[ERR"))
print(f"SAVED {out}\n  ayat={len(rows)} domain={len(DOMAIN)} error_cells={errs}")
