import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# App beállítások
st.set_page_config(page_title="Csírakert Admin", page_icon="🌱")
st.title("🌱 Csírakert Menedzser")

# Kapcsolódás a Google Táblázathoz (a Secrets-ben megadott link alapján)
conn = st.connection("gsheets", type=GSheetsConnection)

# Fix adatok
AR_PER_DOBOZ = 200
termekek = ["Retek csíra", "Lucerna csíra", "Búzafű", "Mix csomag", "Mustár csíra", "Brokkoli csíra"]

# Rendelés felvétele
with st.form("rendeles_form", clear_on_submit=True):
    st.subheader("Új eladás rögzítése")
    vasarlo = st.text_input("Vásárló neve")
    termek = st.selectbox("Csíra fajtája", termekek)
    db = st.number_input("Hány doboz?", min_value=1, step=1, value=1)
    
    vegosszeg = db * AR_PER_DOBOZ
    st.write(f"### Fizetendő: **{vegosszeg} RSD**")
    
    statusz = st.radio("Fizetés", ["Kifizetve", "Hitelbe"])
    mentes = st.form_submit_button("Rendelés Mentése")

if mentes:
    # Új sor előkészítése
    uj_adat = pd.DataFrame([{
        "Dátum": date.today().strftime("%Y-%m-%d"),
        "Vásárló": vasarlo,
        "Termék": termek,
        "Mennyiség": db,
        "Összeg": vegosszeg,
        "Állapot": statusz
    }])
    
    # Meglévő adatok lekérése és az új hozzáadása
    regi_adatok = conn.read(worksheet="Sheet1") # Ha a fül neve más, írd át!
    friss_adatok = pd.concat([regi_adatok, uj_adat], ignore_index=True)
    
    # Mentés vissza a Google Táblázatba
    conn.update(worksheet="Sheet1", data=friss_adatok)
    
    st.success(f"Mentve a táblázatba! {vasarlo} -> {vegosszeg} RSD")
    st.balloons()

# Előzmények mutatása
st.divider()
st.subheader("Utolsó rendelések")
try:
    adatok = conn.read(worksheet="Sheet1")
    st.dataframe(adatok.tail(5)) # Csak az utolsó 5 sort mutatja
except:
    st.info("Még nincs mentett adat a táblázatban.")
