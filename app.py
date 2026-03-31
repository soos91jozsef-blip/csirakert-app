import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Csírakert Admin", page_icon="🌱")
st.title("🌱 Csírakert Menedzser")

AR_PER_DOBOZ = 200
termekek = ["Retek csíra", "Lucerna csíra", "Búzafű", "Mix csomag", "Mustár csíra", "Brokkoli csíra"]

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
    st.success(f"Mentve! {vasarlo} -> {vegosszeg} RSD")
    st.balloons()
