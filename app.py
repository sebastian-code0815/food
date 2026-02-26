import streamlit as st
import pandas as pd
import plotly.express as px # NEU: Import für die Diagramme

# ==============================================================================
# DATENBANK LADEN
# ==============================================================================
@st.cache_data
def lade_datenbank():
    try:
        df = pd.read_excel('lebensmittel.xlsx')
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("FEHLER: 'lebensmittel.xlsx' nicht gefunden.")
        return None

df_lebensmittel = lade_datenbank()

# ==============================================================================
# LOGIK-FUNKTIONEN
# ==============================================================================
def berechne_grundumsatz(gewicht, groesse, alter, geschlecht):
    # ... (unverändert) ...
    geschlecht_klein = geschlecht.lower()
    if geschlecht_klein == "männlich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + 5
    elif geschlecht_klein == "weiblich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) - 161
    else: return 0
    return grundumsatz

def berechne_leistungsumsatz(grundumsatz, aktivitaetslevel):
    # ... (unverändert) ...
    level_klein = aktivitaetslevel.lower()
    if level_klein == "leicht": pal_faktor = 1.5
    elif level_klein == "mittel": pal_faktor = 1.7
    elif level_klein == "schwer": pal_faktor = 2.0
    else: pal_faktor = 1.2
    return grundumsatz * pal_faktor

# NEUE FUNKTION: MAKROS BERECHNEN
def berechne_makros(ziel_kalorien, gewicht):
    protein_gramm = 2 * gewicht
    protein_kcal = protein_gramm * 4
    
    fett_kcal = ziel_kalorien * 0.25
    fett_gramm = fett_kcal / 9
    
    rest_kcal = ziel_kalorien - protein_kcal - fett_kcal
    kohlenhydrate_gramm = rest_kcal / 4
    
    # Sicherstellen, dass keine negativen Werte entstehen
    if kohlenhydrate_gramm < 0: kohlenhydrate_gramm = 0
    
    return {
        "Protein (g)": round(protein_gramm),
        "Fett (g)": round(fett_gramm),
        "Kohlenhydrate (g)": round(kohlenhydrate_gramm)
    }

def finde_lebensmittel(name_teil, datenbank):
    # ... (unverändert) ...
    if datenbank is not None and name_teil:
        suchbegriff = name_teil.lower()
        ergebnisse = datenbank[datenbank['Lebensmittelname_Deutsch'].str.lower().str.contains(suchbegriff, na=False)]
        return ergebnisse
    return pd.DataFrame()

# ==============================================================================
# STREAMLIT OBERFLÄCHE
# ==============================================================================
st.set_page_config(layout="wide")
st.title("Dein persönlicher Ernährungsplan-Generator")

# --- TEIL 1: KALORIENRECHNER (ERWEITERT) ---
st.header("1. Berechne deinen Tagesbedarf und deine Makros")

col1, col2, col3 = st.columns(3) # Jetzt 3 Spalten
with col1:
    geschlecht = st.selectbox("Geschlecht", ("männlich", "weiblich"))
    gewicht = st.number_input("Gewicht (in kg)", 30.0, 250.0, 85.0, 0.5)
with col2:
    groesse = st.number_input("Größe (in cm)", 120, 230, 180)
    alter = st.slider("Alter (in Jahren)", 16, 100, 37)
with col3: # NEUE SPALTE FÜR ZIEL
    aktivitaetslevel = st.selectbox("Aktivitätslevel", ("leicht", "mittel", "schwer"))
    ziel = st.selectbox("Dein Ziel:", ("Gewicht reduzieren", "Gewicht halten", "Gewicht zunehmen"))

if st.button("Bedarf berechnen"):
    # Grund- und Leistungsumsatz berechnen
    grundumsatz = berechne_grundumsatz(gewicht, groesse, alter, geschlecht)
    leistungsumsatz = berechne_leistungsumsatz(grundumsatz, aktivitaetslevel)

    # Ziel-Kalorien berechnen
    if ziel == "Gewicht reduzieren":
        ziel_kalorien = leistungsumsatz - 300
    elif ziel == "Gewicht zunehmen":
        ziel_kalorien = leistungsumsatz + 300
    else: # Gewicht halten
        ziel_kalorien = leistungsumsatz

    # Makros berechnen
    makros = berechne_makros(ziel_kalorien, gewicht)

    # Ergebnisse anzeigen
    st.subheader("Deine Zielwerte:")
    
    # Metriken in Spalten anzeigen
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Ziel-Kalorien pro Tag", f"{round(ziel_kalorien)} kcal")
    m_col2.metric("Protein", f"{makros['Protein (g)']} g")
    m_col3.metric("Fett", f"{makros['Fett (g)']} g")
    m_col4.metric("Kohlenhydrate", f"{makros['Kohlenhydrate (g)']} g")

    # Kuchendiagramm erstellen
    makro_df = pd.DataFrame.from_dict(makros, orient='index', columns=['Gramm'])
    makro_df = makro_df.reset_index().rename(columns={'index': 'Makronährstoff'})
    
    fig = px.pie(makro_df, values='Gramm', names='Makronährstoff', title='Deine Makro-Verteilung in Gramm',
                 color_discrete_map={
                     "Protein (g)": "#1f77b4",
                     "Fett (g)": "#ff7f0e",
                     "Kohlenhydrate (g)": "#2ca02c"
                 })
    st.plotly_chart(fig, use_container_width=True)

# --- TEIL 2: LEBENSMITTEL-SUCHER (unverändert) ---
st.divider()
st.header("2. Finde Lebensmittel in der Datenbank")
# ... (der Rest des Codes bleibt gleich) ...
