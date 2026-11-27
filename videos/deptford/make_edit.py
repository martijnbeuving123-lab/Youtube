import json, sys
C="assets/cards/"; I="assets/img/"
V={ "01":(C+"c01","in"), "02":(I+"deptford_hs","in",C+"c02"), "03":(C+"print","in"), "04":(C+"c04","still"),
"05":(C+"title","still"), "06":(C+"map","in"), "07":(C+"c07","in"), "08":(C+"c08","in"), "09":(C+"c09","in"),
"10":(C+"c10","in"), "11":(C+"c11","in"), "12":(C+"c12","in"), "13":(C+"house","in"), "14":(C+"c14","in"),
"15":(C+"masks","in"), "16":(C+"c16","in"), "17":(C+"c17","in"), "18":(C+"c18","in"), "19":(C+"c19","in"),
"20":(C+"bertillon","in"), "21":(I+"faulds","in",C+"c45"), "22":(I+"henry_vf","in",C+"c58"), "23":(I+"fp_book","left",C+"c23"),
"24":(C+"c24","in"), "25":(C+"cashbox","in"), "26":(C+"c26","in"), "27":(C+"c27","in"), "28":(C+"c28","in"),
"29":(C+"c29","in"), "30":(C+"c30","in"), "31":(C+"print","out"), "32":(C+"c32","in"), "33":(C+"c33","in"),
"34":(C+"c34","in"), "35":(C+"c35","in"), "36":(C+"c36","in"), "37":(C+"c37","in"), "38":(C+"c38","in"),
"39":(C+"compare","in"), "40":(C+"match","in"), "41":(C+"c41","in"), "42":(C+"c42","in"), "43":(C+"c43","in"),
"44":(C+"c44","in"), "45":(C+"c45","in"), "46":(C+"c46","in"), "47":(C+"c47","still"), "48":(C+"c48","in"),
"49":(C+"points","in"), "50":(C+"c50","in"), "51":(C+"letters","in"), "52":(C+"c52","still"), "53":(C+"c53","in"),
"54":(C+"c54","in"), "55":(C+"c55","in"), "56":(C+"c56","in"), "57":(I+"henry_vf","out",C+"c23"), "58":(C+"c58","in"),
"59":(C+"c59","in"), "60":(I+"faulds","out",C+"c60"), "61":(C+"c61","in"), "62":(C+"c62","still"), "63":(C+"end","still")}
CAP={"02":"Deptford High Street today","06":"I  ·  The shop on the High Street","18":"II  ·  The smudge on the tray",
"21":"Henry Faulds","22":"Sir Edward Henry, 'Vanity Fair', 1905","23":"Henry's classification manual",
"32":"III  ·  Two brothers","42":"IV  ·  Fingerprints on trial","54":"V  ·  The verdict"}
ACT={"06","18","32","42","54"}
beats=[]
for k,v in V.items():
    ext=".jpg" if v[0].startswith(I) else ".png"
    b={"id":k,"visual":v[0]+ext,"motion":v[1]}
    if len(v)>2: b["fallback"]=v[2]+".png"
    if k in CAP: b["caption"]=CAP[k]
    if k in ACT: b["pause_before"]=1.4
    beats.append(b)
json.dump({"music_db":-23,"chapters":{"01":"Deptford High Street, 27 March 1905","06":"The shop on the High Street","18":"The smudge on the tray","32":"Two brothers","42":"Fingerprints on trial","54":"The verdict and the legacy"},"beats":beats},open(sys.argv[1]+"/edit.json","w"),indent=1)
