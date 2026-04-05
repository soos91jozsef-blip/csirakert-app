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
        "termekek": list(termek_forditas.keys()),
        "valuta_cim": "Fizetés pénzneme",
        "db": "Mennyiség (db)",
        "ar": "Egységár",
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
        "termekek": list(termek_forditas.values()),
        "valuta_cim": "Valuta plaćanja",
        "db": "Količina (kom)",
        "ar": "Jedinična cena",
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

# Kapcsolat létrehozása a Google Táblázattal
conn = st.connection("gsheets", type=GSheetsConnection)

# --- RENDELÉS FELVÉTELE ---
# A formon KÍVÜLRE tesszük a valuta választót, hogy azonnal frissíthesse az árat
valuta = st.radio(t["valuta_cim"], ["RSD", "HUF"], horizontal=True)
alap_ar = 200 if valuta == "RSD" else 650

with st.form("rendeles_form"):
    st.subheader(t["alcim"])
    
    vasarlo = st.text_input(t["nev"])
    valasztott_termek_megjelenites = st.selectbox(t["termek_cim"], t["termekek"])
    
    # Az egységár most már az 'alap_ar' változót használja, ami követi a választót
    egysegar = st.number_input(f"{t['ar']} ({valuta})", min_value=0, value=alap_ar)

    # Terméknév visszafordítása a mentéshez (hogy a táblázat egységes maradjon)
    if nyelv == "🇷🇸 Srpski":
        termek_mentesre = [k for k, v in termek_forditas.items() if v == valasztott_termek_megjelenites][0]
    else:
        termek_mentesre = valasztott_termek_megjelenites

    db = st.number_input(t["db"], min_value=1, value=1)
    statusz = st.radio(t["statusz"], t["statusz_opciok"])
    
    submit = st.form_submit_button(t["mentes"])

if submit:
    if vasarlo:
        # Új sor előkészítése
        most = datetime.now().strftime("%Y-%m-%d")
        vegosszeg = db * egysegar
        osszeg_szoveg = f"{vegosszeg} {valuta}"
        
        uj_adat = pd.DataFrame([{
            "Dátum": most,
            "Vásárló": vasarlo,
            "Termék": termek_mentesre,
            "Mennyiség": db,
            "Összeg": osszeg_szoveg,
            "Állapot": statusz
        }])
        
        try:
            # Meglévő adatok lekérése (hibás create rész nélkül)
            regi_adatok = conn.read(worksheet="Munkalap1", ttl=0)
            
            # Adatok összefűzése
            friss_adatok = pd.concat([regi_adatok, uj_adat], ignore_index=True)
            
            # Mentés vissza a táblázatba
            conn.update(worksheet="Munkalap1", data=friss_adatok)
            
            st.success(f"{t['siker']}: {vasarlo} -> {osszeg_szoveg}")
            st.balloons()
        except Exception as e:
            st.error(f"Hiba / Greška: {e}")
    else:
        st.warning(t["figyelmeztetes"])

# --- ELŐZMÉNYEK ---
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
