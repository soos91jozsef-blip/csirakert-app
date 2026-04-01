import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Oldal beállítása
st.set_page_config(page_title="Csírakert Admin", page_icon="🌱")

st.title("🌱 Csírakert Rendelés Kezelő")

# Kapcsolat létrehozása a Google Táblázattal
# A Secrets-ben lévő linket használjuk
conn = st.connection("gsheets", type=GSheetsConnection)

# --- RENDELÉS FELVÉTELE ---
with st.form("rendeles_form"):
    st.subheader("Új rendelés hozzáadása")
    
    vasarlo = st.text_input("Vásárló neve")
    termek = st.selectbox("Termék", ["Retek csíra", "Brokkoli csíra", "Búzafű", "Vegyes csomag"])
    db = st.number_input("Mennyiség (db)", min_value=1, value=1)
    egysegar = st.number_input("Egységár (RSD)", min_value=0, value=200)
    statusz = st.radio("Állapot", ["Kifizetve", "Hitelbe"])
    
    submit = st.form_submit_button("Rendelés Mentése")

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
            # Közvetlenül a munkalap végére fűzzük az új adatot
            conn.create(worksheet="Munkalap1", data=uj_adat)
            
            st.success(f"Rendelés sikeresen mentve: {vasarlo}!")
            st.balloons()
        except Exception as e:
            st.error(f"Hiba történt a mentéskor: {e}")
        try:
            # Meglévő adatok lekérése a "Munkalap1" fülről
            regi_adatok = conn.read(worksheet="Munkalap1", ttl=0)
            
            # Adatok összefűzése
            friss_adatok = pd.concat([regi_adatok, uj_adat], ignore_index=True)
            
            # Mentés vissza a táblázatba
            conn.update(worksheet="Munkalap1", data=friss_adatok)
            
            st.success(f"Mentve: {vasarlo} -> {vegosszeg} RSD")
            st.balloons()
        except Exception as e:
            st.error(f"Hiba történt a mentéskor: {e}")
    else:
        st.warning("Kérlek, írd be a vásárló nevét!")

# --- ELŐZMÉNYEK ---
st.divider()
st.subheader("Utolsó rendelések")

try:
    # Adatok frissítése és megjelenítése
    megjelenitendo_adatok = conn.read(worksheet="Munkalap1", ttl=0)
    if not megjelenitendo_adatok.empty:
        st.dataframe(megjelenitendo_adatok.tail(10)) # Az utolsó 10 rendelés
    else:
        st.info("Még nincs mentett adat a táblázatban.")
except:
    st.info("Nem sikerült betölteni az előzményeket.")
