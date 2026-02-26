import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================================================================
# SEITEN-KONFIGURATION (muss ganz am Anfang sein)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Ernährungsplan-Generator")

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
        return None

df_lebensmittel = lade_datenbank()
if df_lebensmittel is None:
    st.error("FATALER FEHLER: 'lebensmittel.xlsx' nicht gefunden. Die App kann nicht starten.")
    st.stop() # Beendet die App, wenn die Datenbank fehlt

# ==============================================================================
# LOGIK-FUNKTIONEN
# ==============================================================================
# ... (alle Ihre Berechnungs- und Suchfunktionen bleiben hier unverändert) ...
def berechne_grundumsatz(gewicht, groesse, alter, geschlecht):
    geschlecht_klein = geschlecht.lower()
    if geschlecht_klein == "männlich": grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + 5
    elif geschlecht_klein == "weiblich": grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) - 161
    else: return 0
    return grundumsatz

def berechne_leistungsumsatz(grundumsatz, aktivitaetslevel):
    level_klein = aktivitaetslevel.lower()
    if level_klein == "leicht": pal_faktor = 1.5
    elif level_klein == "mittel": pal_faktor = 1.7
    elif level_klein == "schwer": pal_faktor = 2.0
    else: pal_faktor = 1.2
    return grundumsatz * pal_faktor

def berechne_makros(ziel_kalorien, gewicht):
    protein_gramm = 2 * gewicht
    protein_kcal = protein_gramm * 4
    fett_kcal = ziel_kalorien * 0.25
    fett_gramm = fett_kcal / 9
    rest_kcal = ziel_kalorien - protein_kcal - fett_kcal
    kohlenhydrate_gramm = rest_kcal / 4
    if kohlenhydrate_gramm < 0: kohlenhydrate_gramm = 0
    return {"Protein (g)": round(protein_gramm), "Fett (g)": round(fett_gramm), "Kohlenhydrate (g)": round(kohlenhydrate_gramm)}

def finde_lebensmittel(name_teil, datenbank):
    if name_teil:
        suchbegriff = name_teil.lower()
        ergebnisse = datenbank[datenbank['Lebensmittelname_Deutsch'].str.lower().str.contains(suchbegriff, na=False)]
        return ergebnisse
    return pd.DataFrame()

# ==============================================================================
# SESSION STATE INITIALISIERUNG (Das "Gedächtnis" der App)
# ==============================================================================
if 'tagesplan' not in st.session_state:
    st.session_state.tagesplan = [] # Eine leere Liste für unsere Mahlzeiten

if 'ziel_werte' not in st.session_state:
    st.session_state.ziel_werte = {} # Ein leeres Dictionary für die Ziel-Kalorien/Makros

# ==============================================================================
# STREAMLIT OBERFLÄCHE
# ==============================================================================
st.title("Dein persönlicher Ernährungsplan-Generator")

# --- TEIL 1: ZIELSETZUNG ---
with st.expander("Schritt 1: Berechne deinen Tagesbedarf und deine Makros", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        geschlecht = st.selectbox("Geschlecht", ("männlich", "weiblich"))
        gewicht = st.number_input("Gewicht (in kg)", 30.0, 250.0, 85.0, 0.5)
    with col2:
        groesse = st.number_input("Größe (in cm)", 120, 230, 180)
        alter = st.slider("Alter (in Jahren)", 16, 100, 37)
    with col3:
        aktivitaetslevel = st.selectbox("Aktivitätslevel", ("leicht", "mittel", "schwer"))
        ziel = st.selectbox("Dein Ziel:", ("Gewicht reduzieren", "Gewicht halten", "Gewicht zunehmen"))

    if st.button("Ziele berechnen & speichern"):
        grundumsatz = berechne_grundumsatz(gewicht, groesse, alter, geschlecht)
        leistungsumsatz = berechne_leistungsumsatz(grundumsatz, aktivitaetslevel)
        if ziel == "Gewicht reduzieren": ziel_kalorien = leistungsumsatz - 300
        elif ziel == "Gewicht zunehmen": ziel_kalorien = leistungsumsatz + 300
        else: ziel_kalorien = leistungsumsatz
        makros = berechne_makros(ziel_kalorien, gewicht)
        
        # Speichere die Ziele im Session State, damit wir sie später verwenden können
        st.session_state.ziel_werte = {
            "Kalorien": round(ziel_kalorien),
            "Protein (g)": makros["Protein (g)"],
            "Fett (g)": makros["Fett (g)"],
            "Kohlenhydrate (g)": makros["Kohlenhydrate (g)"]
        }
        st.success("Ziele erfolgreich gespeichert!")

# Nur anzeigen, wenn Ziele berechnet wurden
if st.session_state.ziel_werte:
    st.subheader("Deine gespeicherten Zielwerte:")
    z_col1, z_col2, z_col3, z_col4 = st.columns(4)
    z_col1.metric("Ziel-Kalorien", f"{st.session_state.ziel_werte['Kalorien']} kcal")
    z_col2.metric("Ziel-Protein", f"{st.session_state.ziel_werte['Protein (g)']} g")
    z_col3.metric("Ziel-Fett", f"{st.session_state.ziel_werte['Fett (g)']} g")
    z_col4.metric("Ziel-Kohlenhydrate", f"{st.session_state.ziel_werte['Kohlenhydrate (g)']} g")

st.divider()

# --- TEIL 2: TAGESPLAN ERSTELLEN ---
st.header("Schritt 2: Stelle deinen Tagesplan zusammen")

# Layout mit zwei Spalten: links Suche, rechts Tagesplan
search_col, plan_col = st.columns([0.6, 0.4]) # linke Spalte ist etwas breiter

with search_col:
    st.subheader("Lebensmittel suchen & hinzufügen")
    suchbegriff = st.text_input("Suche nach einem Lebensmittel:")
    
    if suchbegriff:
        such_ergebnisse = finde_lebensmittel(suchbegriff, df_lebensmittel)
        
        if not such_ergebnisse.empty:
            # Für jede Zeile im Suchergebnis eine Eingabemöglichkeit erstellen
            for index, row in such_ergebnisse.head(5).iterrows(): # Zeige nur die Top 5
                with st.container():
                    c1, c2, c3 = st.columns([0.5, 0.3, 0.2])
                    c1.text(row['Lebensmittelname_Deutsch'])
                    menge = c2.number_input("Menge (g)", min_value=1, value=100, key=f"menge_{index}")
                    
                    if c3.button("➕", key=f"add_{index}"):
                        # Berechne Nährwerte für die angegebene Menge
                        faktor = menge / 100.0
                        hinzugefuegt = {
                            "Name": row['Lebensmittelname_Deutsch'],
                            "Menge (g)": menge,
                            "Kalorien": round(row['Energie_kcal'] * faktor),
                            "Protein (g)": round(row['Protein_g'] * faktor, 1),
                            "Fett (g)": round(row['Fett_g'] * faktor, 1),
                            "Kohlenhydrate (g)": round(row['Kohlenhydrate_g'] * faktor, 1),
                        }
                        # Füge das Lebensmittel zum Tagesplan im Session State hinzu
                        st.session_state.tagesplan.append(hinzugefuegt)
                        st.success(f"{menge}g {row['Lebensmittelname_Deutsch']} hinzugefügt!")

with plan_col:
    st.subheader("Dein aktueller Tagesplan")
    
    if st.session_state.tagesplan:
        # Erstelle einen DataFrame aus dem Tagesplan für einfache Berechnungen
        plan_df = pd.DataFrame(st.session_state.tagesplan)
        st.dataframe(plan_df)

        # Berechne die Summen
        total_kcal = plan_df['Kalorien'].sum()
        total_protein = plan_df['Protein (g)'].sum()
        total_fett = plan_df['Fett (g)'].sum()
        total_kh = plan_df['Kohlenhydrate (g)'].sum()

        st.subheader("Gesamtwerte deines Plans:")
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        p_col1.metric("Kalorien", f"{round(total_kcal)} kcal")
        p_col2.metric("Protein", f"{round(total_protein)} g")
        p_col3.metric("Fett", f"{round(total_fett)} g")
        p_col4.metric("Kohlenhydrate", f"{round(total_kh)} g")

        # Fortschrittsbalken anzeigen, wenn Ziele gesetzt sind
        if st.session_state.ziel_werte:
            st.subheader("Fortschritt zu deinen Zielen:")
            
            kcal_progress = min(total_kcal / st.session_state.ziel_werte['Kalorien'], 1.0)
            st.write("Kalorien:")
            st.progress(kcal_progress, text=f"{round(total_kcal)} / {st.session_state.ziel_werte['Kalorien']}")
            
            protein_progress = min(total_protein / st.session_state.ziel_werte['Protein (g)'], 1.0)
            st.write("Protein:")
            st.progress(protein_progress, text=f"{round(total_protein)} g / {st.session_state.ziel_werte['Protein (g)']} g")

        # Button zum Zurücksetzen des Plans
        if st.button("Tagesplan zurücksetzen"):
            st.session_state.tagesplan = []
            st.rerun() # Lädt die App neu, um die Anzeige zu aktualisieren
            
    else:
        st.info("Dein Tagesplan ist noch leer. Füge links Lebensmittel hinzu.")
