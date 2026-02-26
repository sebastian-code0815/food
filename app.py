import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================================================================
# SEITEN-KONFIGURATION
# ==============================================================================
st.set_page_config(layout="wide", page_title="Ernährungsplan-Generator")

# ==============================================================================
# SESSION STATE INITIALISIERUNG (Das "Gedächtnis" der App)
# ==============================================================================
if 'tagesplan' not in st.session_state:
    st.session_state.tagesplan = []
if 'ziel_werte' not in st.session_state:
    st.session_state.ziel_werte = {}
# NEU: Eine Liste für benutzerdefinierte Lebensmittel
if 'user_lebensmittel' not in st.session_state:
    st.session_state.user_lebensmittel = []

# ==============================================================================
# DATENBANK LADEN & KOMBINIEREN
# ==============================================================================
@st.cache_data
def lade_bls_datenbank():
    try:
        df = pd.read_excel('lebensmittel.xlsx')
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("FEHLER: 'lebensmittel.xlsx' nicht gefunden.")
        return pd.DataFrame()

# Lade die Haupt-Datenbank
df_bls = lade_bls_datenbank()

# Erstelle einen DataFrame aus den benutzerdefinierten Lebensmitteln
df_user = pd.DataFrame(st.session_state.user_lebensmittel)

# Kombiniere beide Datenbanken zu einer großen, durchsuchbaren Datenbank
# Nur kombinieren, wenn beide existieren
if not df_bls.empty and not df_user.empty:
    df_lebensmittel = pd.concat([df_bls, df_user], ignore_index=True)
elif not df_bls.empty:
    df_lebensmittel = df_bls
elif not df_user.empty:
    df_lebensmittel = df_user
else:
    # Fallback, wenn gar keine Daten da sind
    df_lebensmittel = pd.DataFrame(columns=['Lebensmittelname_Deutsch', 'Energie_kcal', 'Protein_g', 'Fett_g', 'Kohlenhydrate_g'])


# ==============================================================================
# LOGIK-FUNKTIONEN (bleiben fast unverändert)
# ==============================================================================
# ... (berechne_grundumsatz, berechne_leistungsumsatz, berechne_makros bleiben gleich) ...
def finde_lebensmittel(name_teil, datenbank):
    # ... (Ihre intelligente Suchfunktion von vorhin bleibt hier unverändert) ...
    if not datenbank.empty and name_teil:
        suchbegriff = name_teil.lower()
        ergebnisse = datenbank[datenbank['Lebensmittelname_Deutsch'].str.lower().str.contains(suchbegriff, na=False)].copy()
        def sortier_prioritaet(name):
            name_lower = name.lower()
            if name_lower == suchbegriff: return 1
            elif name_lower.startswith(suchbegriff): return 2
            else: return 3
        if not ergebnisse.empty:
            ergebnisse['sort_prio'] = ergebnisse['Lebensmittelname_Deutsch'].apply(sortier_prioritaet)
            ergebnisse = ergebnisse.sort_values(by=['sort_prio', 'Lebensmittelname_Deutsch'])
        return ergebnisse
    return pd.DataFrame()


# ==============================================================================
# STREAMLIT OBERFLÄCHE
# ==============================================================================
st.title("Dein persönlicher Ernährungsplan-Generator")

# --- TEIL 1: ZIELSETZUNG (bleibt unverändert) ---
# ...

st.divider()

# --- NEU: TEIL 2: EIGENE LEBENSMITTEL HINZUFÜGEN ---
with st.expander("Schritt 2: Eigenes Lebensmittel zur Datenbank hinzufügen"):
    with st.form("neues_lebensmittel_form"):
        st.write("Fülle die Nährwerte pro 100g aus:")
        
        # Formular-Eingabefelder in Spalten
        form_col1, form_col2, form_col3, form_col4, form_col5 = st.columns(5)
        with form_col1:
            lm_name = st.text_input("Name des Lebensmittels*")
        with form_col2:
            lm_kcal = st.number_input("Kalorien (kcal)*", min_value=0)
        with form_col3:
            lm_protein = st.number_input("Protein (g)*", min_value=0.0, format="%.1f")
        with form_col4:
            lm_fett = st.number_input("Fett (g)*", min_value=0.0, format="%.1f")
        with form_col5:
            lm_kh = st.number_input("Kohlenhydrate (g)*", min_value=0.0, format="%.1f")
            
        # Der "Submit"-Button für das Formular
        submitted = st.form_submit_button("Lebensmittel speichern")
        
        if submitted:
            # Validierung: Name darf nicht leer sein
            if not lm_name:
                st.error("Bitte gib einen Namen für das Lebensmittel ein.")
            else:
                neues_lm = {
                    "Lebensmittelname_Deutsch": lm_name,
                    "Energie_kcal": lm_kcal,
                    "Protein_g": lm_protein,
                    "Fett_g": lm_fett,
                    "Kohlenhydrate_g": lm_kh
                }
                # Füge das neue Lebensmittel zur Session-Liste hinzu
                st.session_state.user_lebensmittel.append(neues_lm)
                st.success(f"'{lm_name}' wurde zu deiner persönlichen Datenbank hinzugefügt!")

st.divider()

# --- TEIL 3: TAGESPLAN ERSTELLEN (vorher Teil 2) ---
st.header("Schritt 3: Stelle deinen Tagesplan zusammen")
# ... (der Rest des Codes für die Suche und den Tagesplan bleibt exakt gleich!) ...

