import streamlit as st
import pandas as pd

# ==============================================================================
# DATENBANK LADEN (am Anfang der App)
# ==============================================================================

# @st.cache_data ist ein "Decorator", der dafür sorgt, dass die große
# Excel-Datei nur einmal geladen wird und nicht bei jeder Interaktion.
# Das macht die App viel schneller.
@st.cache_data
def lade_datenbank():
    try:
        df = pd.read_excel('lebensmittel.xlsx')
        return df
    except FileNotFoundError:
        st.error("FEHLER: Die Datei 'lebensmittel.xlsx' wurde nicht im Repository gefunden. Bitte hochladen!")
        return None

df_lebensmittel = lade_datenbank()


# ==============================================================================
# LOGIK-FUNKTIONEN
# ==============================================================================

def berechne_grundumsatz(gewicht, groesse, alter, geschlecht):
    # ... (Ihre Funktion von vorhin, keine Änderung nötig) ...
    geschlecht_klein = geschlecht.lower()
    if geschlecht_klein == "männlich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + 5
    elif geschlecht_klein == "weiblich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) - 161
    else:
        return 0
    return grundumsatz

def berechne_leistungsumsatz(grundumsatz, aktivitaetslevel):
    # ... (Ihre Funktion von vorhin, keine Änderung nötig) ...
    level_klein = aktivitaetslevel.lower()
    if level_klein == "leicht": pal_faktor = 1.5
    elif level_klein == "mittel": pal_faktor = 1.7
    elif level_klein == "schwer": pal_faktor = 2.0
    else: pal_faktor = 1.2
    leistungsumsatz = grundumsatz * pal_faktor
    return leistungsumsatz

def finde_lebensmittel(name_teil, datenbank):
    # ... (Ihre Suchfunktion von vorhin, leicht angepasst) ...
    if datenbank is not None and name_teil:
        suchbegriff = name_teil.lower()
        # WICHTIG: Der Spaltenname muss exakt mit Ihrer Excel-Datei übereinstimmen!
        # Prüfen Sie, ob es 'name' oder 'Lebensmittelname_Deutsch' ist.
        ergebnisse = datenbank[datenbank['Lebensmittelname_Deutsch'].str.lower().str.contains(suchbegriff, na=False)]
        return ergebnisse
    return pd.DataFrame() # Leeren DataFrame zurückgeben, wenn keine Suche


# ==============================================================================
# STREAMLIT OBERFLÄCHE
# ==============================================================================

st.set_page_config(layout="wide") # Macht die App breiter
st.title("Dein persönlicher Ernährungsplan-Generator")

# --- TEIL 1: KALORIENRECHNER ---
st.header("1. Berechne deinen Tagesbedarf")

col1, col2 = st.columns(2)
with col1:
    geschlecht = st.selectbox("Geschlecht", ("männlich", "weiblich"))
    gewicht = st.number_input("Gewicht (in kg)", min_value=30.0, value=85.0, step=0.5)
    groesse = st.number_input("Größe (in cm)", min_value=120, value=180)
with col2:
    alter = st.slider("Alter (in Jahren)", 16, 100, 37)
    aktivitaetslevel = st.selectbox("Aktivitätslevel", ("leicht", "mittel","moderat", "schwer"))

if st.button("Bedarf berechnen"):
    grundumsatz = berechne_grundumsatz(gewicht, groesse, alter, geschlecht)
    leistungsumsatz = berechne_leistungsumsatz(grundumsatz, aktivitaetslevel)
    st.success(f"Dein täglicher Kalorienbedarf: **{round(leistungsumsatz)} kcal**")
    st.info(f"Dein Grundumsatz: {round(grundumsatz)} kcal")


# --- Trennlinie ---
st.divider()


# --- TEIL 2: LEBENSMITTEL-SUCHER ---
st.header("2. Finde Lebensmittel in der Datenbank")

# Ein Texteingabefeld für die Suche
suchbegriff = st.text_input("Suche nach einem Lebensmittel (z.B. 'hähnchen' oder 'quark'):")

# Nur suchen, wenn die Datenbank geladen wurde
if df_lebensmittel is not None:
    # Die Suchfunktion aufrufen
    such_ergebnisse = finde_lebensmittel(suchbegriff, df_lebensmittel)

    # Die Ergebnisse als Tabelle anzeigen
    st.write(f"Gefunden: **{len(such_ergebnisse)}** Einträge")
    
    # Nur relevante Spalten anzeigen
    st.dataframe(such_ergebnisse[['Lebensmittelname_Deutsch', 'Energie_kcal', 'Protein_g', 'Fett_g', 'Kohlenhydrate_g']])

