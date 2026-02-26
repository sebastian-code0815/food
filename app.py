
import streamlit as st
import pandas as pd

# ==============================================================================
# PHASE 1: DIE LOGIK (Unsere Funktionen von vorhin)
# ==============================================================================

def berechne_grundumsatz(gewicht, groesse, alter, geschlecht):
    geschlecht_klein = geschlecht.lower()
    if geschlecht_klein == "m" or geschlecht_klein == "männlich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + 5
    elif geschlecht_klein == "w" or geschlecht_klein == "weiblich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) - 161
    else:
        return 0
    return grundumsatz

def berechne_leistungsumsatz(grundumsatz, aktivitaetslevel):
    level_klein = aktivitaetslevel.lower()
    if level_klein == "leicht":
        pal_faktor = 1.5
    elif level_klein == "mittel":
        pal_faktor = 1.7
    elif level_klein == "schwer":
        pal_faktor = 2.0
    else:
        pal_faktor = 1.2 # Standardwert
    leistungsumsatz = grundumsatz * pal_faktor
    return leistungsumsatz

# ==============================================================================
# PHASE 3: DIE STREAMLIT-OBERFLÄCHE
# ==============================================================================

# Titel der Web-App
st.title("Dein persönlicher Kalorienrechner")
st.write("Gib deine Daten ein, um deinen täglichen Kalorienbedarf zu berechnen.")

# --- Eingabefelder in zwei Spalten anordnen für ein schöneres Layout ---
col1, col2 = st.columns(2)

with col1:
    gewicht = st.number_input("Gewicht (in kg)", min_value=30.0, value=85.0, step=0.5)
    alter = st.slider("Alter (in Jahren)", min_value=16, max_value=100, value=37)
    geschlecht = st.selectbox("Geschlecht", ("männlich", "weiblich"))

with col2:
    groesse = st.number_input("Größe (in cm)", min_value=120, value=180)
    aktivitaetslevel = st.selectbox("Aktivitätslevel", ("leicht", "mittel", "schwer"))

# --- Berechnung und Ausgabe ---
if st.button("Bedarf berechnen"):
    # Berechnungen durchführen
    grundumsatz = berechne_grundumsatz(gewicht, groesse, alter, geschlecht)
    leistungsumsatz = berechne_leistungsumsatz(grundumsatz, aktivitaetslevel)

    # Ergebnisse anzeigen
    st.subheader("Dein Ergebnis:")
    st.success(f"Dein täglicher Kalorienbedarf beträgt: **{round(leistungsumsatz)} kcal**")
    st.info(f"Dein Grundumsatz (Ruhebedarf) beträgt: {round(grundumsatz)} kcal")
