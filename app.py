import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Oldal beállítása
st.set_page_config(page_title="Csírakert Admin", page_icon="🌱")

# --- NYELV VÁLASZTÓ ---
# Zászlós választó az oldal tetején
nyelv = st.radio("Nyelv / Jezik:", ["🇭🇺 Magyar", "🇷🇸 Srpski"], horizontal=True)

# Szótár az app szövegeihez
szovegek = {
    "🇭🇺 Magyar": {
        "cim": "🌱 Csírakert Rendelés Kezelő",
        "alcim": "Új rendelés hozzáadása",
        "nev": "Vásárló neve",
        "termek": "Termék",
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
        "termek": "Proizvod",
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

# Aktuális szövegek kiválasztása
t = szovegek[nyelv]

st.title(t["cim"])

# Kapcsolat létrehozása a Google Táblázattal
conn = st.connection("gsheets", type=GSheetsConnection)

# --- RENDELÉS FELVÉTELE ---
with st.form("rendeles_form"):
    st.subheader(t["alcim"])
    
    vasarlo = st.text_input(t["nev"])
    termek = st.selectbox(t["termek"], ["Retek Mix", "Brokkoli", "Búzafű", "Vajrépa", "Lucerna", "Repce", "Vöröslencse", "Mungóbab", "Szendvics Mix", "Lila Karalábé", "Fodros Kel", "Vöröshere", "Vöröskáposzta"])
    db = st.number_input(t["db"], min_value=1, value=1)
    egysegar = st.number_input(t["ar"], min_value=0, value=200)
    statusz = st.radio(t["statusz"], t["statusz_opciok"])
    
    submit = st.form_submit_button(t["mentes"])

if submit:
    if vasarlo:
        # Új sor előkészítése
        most = datetime.now().strftime("%Y-%m-%d")
        vegosszeg = db * egysegar
        
        uj_adat = pd.DataFrame([{
            "Dátum": most,
            "Vásárló": vasarlo,
            "Termék": termek,
            "Mennyiség": db,
            "Összeg": vegosszeg,
            "Állapot": statusz
        }])
        
        try:
            # Meglévő adatok lekérése a "Munkalap1" fülről
            regi_adatok = conn.read(worksheet="Munkalap1", ttl=0)
            
            # Adatok összefűzése
            friss_adatok = pd.concat([regi_adatok, uj_adat], ignore_index=True)
            
            # Mentés vissza a táblázatba
            conn.update(worksheet="Munkalap1", data=friss_adatok)
            
            st.success(f"{t['siker']}: {vasarlo} -> {vegosszeg} RSD")
            st.balloons()
        except Exception as e:
            st.error(f"Hiba / Greška: {e}")
    else:
        st.warning(t["figyelmeztetes"])

# --- ELŐZMÉNYEK ---
st.divider()
st.subheader(t["elozmeny"])

try:
    # Adatok frissítése és megjelenítése
    megjelenitendo_adatok = conn.read(worksheet="Munkalap1", ttl=0)
    if not megjelenitendo_adatok.empty:
        st.dataframe(megjelenitendo_adatok.tail(10)) 
    else:
        st.info(t["nincs_adat"])
except:
    st.info(t["hiba_betoltes"])
