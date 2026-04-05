import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Oldal beállítása
st.set_page_config(page_title="Csírakert Admin", page_icon="🌱")

# --- NYELV VÁLASZTÓ ---
nyelv = st.radio("Nyelv / Jezik:", ["🇭🇺 Magyar", "🇷🇸 Srpski"], horizontal=True)

# Termék szótár (Magyar név: Szerb név)
termek_forditas = {
    "Retek Mix": "Miks rotkvica",
    "Brokkoli": "Brokoli",
    "Búzafű": "Pšenična trava",
    "Vajrépa": "Bela repa",
    "Lucerna": "Lucerka",
    "Repce": "Repica",
    "Vöröslencse": "Crvena sočiva",
    "Mungóbab": "Mungo pasulj",
    "Szendvics Mix": "Sendvič miks",
    "Lila Karalábé": "Ljubičasti kolerabi",
    "Fodros Kel": "Kovrdžavi kelj",
    "Vöröshere": "Crvena detelina",
    "Vöröskáposzta": "Crveni kupus"
}

# Szótár az app szövegeihez
szovegek = {
    "🇭🇺 Magyar": {
        "cim": "🌱 Csírakert Rendelés Kezelő",
        "alcim": "Új rendelés hozzáadása",
        "nev": "Vásárló neve",
        "termek_cim": "Válassz terméket",
        "termekek": list(termek_forditas.keys()), # Eredeti magyar nevek
        "db": "Mennyiség (db)",
        "ar": "Egységár (RSD)",
        "statusz": "Állapot",
        "statusz_opciok": ["Kifizetve", "Hitelbe"],
        "mentes": "Rendelés Mentése",
        "figyelmeztetes": "Kérlek, írd be a vásárló nevét!",
        "siker": "Mentve",
        "elozmeny": "Utolsó rendelések",
        "nincs_adat": "Még nincs mentett adat a táblázatban.",
        "hiba_betoltes": "Nem sikerült betölteni az előzményeket."
    },
    "🇷🇸 Srpski": {
        "cim": "🌱 Upravljanje porudžbinama",
        "alcim": "Dodaj novu porudžbinu",
        "nev": "Ime kupca",
        "termek_cim": "Izaberi proizvod",
        "termekek": list(termek_forditas.values()), # Lefordított szerb nevek
        "db": "Količina (kom)",
        "ar": "Jedinična cena (RSD)",
        "statusz": "Status",
        "statusz_opciok": ["Plaćeno", "Na dug"],
        "mentes": "Sačuvaj porudžbinu",
        "figyelmeztetes": "Molim vas, unesite ime kupca!",
        "siker": "Sačuvano",
        "elozmeny": "Poslednje porudžbine",
        "nincs_adat": "Još nema sačuvanih podataka u tabeli.",
        "hiba_betoltes": "Nije uspelo učitavanje prethodnih porudžbina."
    }
}

t = szovegek[nyelv]

st.title(t["cim"])

conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("rendeles_form"):
    st.subheader(t["alcim"])
    
    vasarlo = st.text_input(t["nev"])
    # Itt a választott nyelven jelennek meg a termékek
    valasztott_termek_megjelenites = st.selectbox(t["termek_cim"], t["termekek"])
    
    # TRÜKK: Ha szerbül van, keressük vissza a magyar nevét a mentéshez
    if nyelv == "🇷🇸 Srpski":
        # Megkeressük, melyik magyar névhez tartozik a szerb választás
        termek_mentesre = [k for k, v in termek_forditas.items() if v == valasztott_termek_megjelenites][0]
    else:
        termek_mentesre = valasztott_termek_megjelenites

    db = st.number_input(t["db"], min_value=1, value=1)
    egysegar = st.number_input(t["ar"], min_value=0, value=200)
    statusz = st.radio(t["statusz"], t["statusz_opciok"])
    
    submit = st.form_submit_button(t["mentes"])

if submit:
    if vasarlo:
        most = datetime.now().strftime("%Y-%m-%d")
        vegosszeg = db * egysegar
        
        uj_adat = pd.DataFrame([{
            "Dátum": most,
            "Vásárló": vasarlo,
            "Termék": termek_mentesre, # A táblázatba a fix magyar név kerül
            "Mennyiség": db,
            "Összeg": vegosszeg,
            "Állapot": statusz
        }])
        
        try:
            regi_adatok = conn.read(worksheet="Munkalap1", ttl=0)
            friss_adatok = pd.concat([regi_adatok, uj_adat], ignore_index=True)
            conn.update(worksheet="Munkalap1", data=friss_adatok)
            
            st.success(f"{t['siker']}: {vasarlo} -> {vegosszeg} RSD")
            st.balloons()
        except Exception as e:
            st.error(f"Hiba / Greška: {e}")
    else:
        st.warning(t["figyelmeztetes"])

st.divider()
st.subheader(t["elozmeny"])

try:
    megjelenitendo_adatok = conn.read(worksheet="Munkalap1", ttl=0)
    if not megjelenitendo_adatok.empty:
        st.dataframe(megjelenitendo_adatok.tail(10)) 
    else:
        st.info(t["nincs_adat"])
except:
    st.info(t["hiba_betoltes"])
