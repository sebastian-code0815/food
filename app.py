import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================================================================
# DATENBANK LADEN (am Anfang der App)
# ==============================================================================
@st.cache_data
def lade_datenbank():
    """
    Lädt die Lebensmittel-Datenbank aus der Excel-Datei.
    Die @st.cache_data Anweisung sorgt für hohe Performance.
    """
    try:
        df = pd.read_excel('lebensmittel.xlsx')
        # Wichtig: Bereinigt Spaltennamen von unsichtbaren Leerzeichen
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("FEHLER: Die Datei 'lebensmittel.xlsx' wurde nicht im Repository gefunden. Bitte hochladen!")
        return None

df_lebensmittel = lade_datenbank()


# ==============================================================================
# LOGIK-FUNKTIONEN (Der "Motor" der App)
# ==============================================================================

def berechne_grundumsatz(gewicht, groesse, alter, geschlecht):
    """
    Berechnet den Grundumsatz nach der Mifflin-St Jeor-Formel.
    """
    geschlecht_klein = geschlecht.lower()
    if geschlecht_klein == "männlich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + 5
    elif geschlecht_klein == "weiblich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) - 161
    else:
        return 0 # Fallback
    return grundumsatz

def berechne_leistungsumsatz(grundumsatz, aktivitaetslevel):
    """
    Berechnet den Leistungsumsatz basierend auf dem Grundumsatz und einem PAL-Faktor.
    """
    level_klein = aktivitaetslevel.lower()
    if level_klein == "leicht":
        pal_faktor = 1.5
    elif level_klein == "mittel":
        pal_faktor = 1.7
    elif level_klein == "schwer":
        pal_faktor = 2.0
    else:
        pal_faktor = 1.2 # Standardwert, falls etwas schiefgeht
    leistungsumsatz = grundumsatz * pal_faktor
    return leistungsumsatz

def berechne_makros(ziel_kalorien, gewicht):
    """
    Berechnet die Makronährstoffverteilung in Gramm.
    """
    # Regel: 2g Protein pro kg Körpergewicht
    protein_gramm = 2 * gewicht
    protein_kcal = protein_gramm * 4
    
    # Regel: 25% der Kalorien aus Fett
    fett_kcal = ziel_kalorien * 0.25
    fett_gramm = fett_kcal / 9
    
    # Der Rest sind Kohlenhydrate
    rest_kcal = ziel_kalorien - protein_kcal - fett_kcal
    kohlenhydrate_gramm = rest_kcal / 4
    
    # Sicherstellen, dass keine negativen Werte entstehen (z.B. bei extremen Diäten)
    if kohlenhydrate_gramm < 0:
        kohlenhydrate_gramm = 0
    
    return {
        "Protein (g)": round(protein_gramm),
        "Fett (g)": round(fett_gramm),
        "Kohlenhydrate (g)": round(kohlenhydrate_gramm)
    }

def finde_lebensmittel(name_teil, datenbank):
    """
    Sucht in der Lebensmittel-Datenbank nach passenden Einträgen.
    """
    if datenbank is not None and name_teil:
        suchbegriff = name_teil.lower()
        ergebnisse = datenbank[datenbank['Lebensmittelname_Deutsch'].str.lower().str.contains(suchbegriff, na=False)]
        return ergebnisse
    return pd.DataFrame() # Gibt einen leeren DataFrame zurück, wenn keine Suche stattfindet


# ==============================================================================
# STREAMLIT OBERFLÄCHE (Das "Cockpit" der App)
# ==============================================================================

# Seiten-Konfiguration (Titel und Layout)
st.set_page_config(layout="wide", page_title="Ernährungsplan-Generator")
st.title("Dein persönlicher Ernährungsplan-Generator")

# --- TEIL 1: KALORIENRECHNER UND MAKRO-VERTEILUNG ---
st.header("1. Berechne deinen Tagesbedarf und deine Makros")

# Eingabefelder in Spalten anordnen für ein sauberes Layout
col1, col2, col3 = st.columns(3)
with col1:
    geschlecht = st.selectbox("Geschlecht", ("männlich", "weiblich"), key="geschlecht")
    gewicht = st.number_input("Gewicht (in kg)", min_value=30.0, max_value=250.0, value=85.0, step=0.5, key="gewicht")
with col2:
    groesse = st.number_input("Größe (in cm)", min_value=120, max_value=230, value=180, key="groesse")
    alter = st.slider("Alter (in Jahren)", min_value=16, max_value=100, value=37, key="alter")
with col3:
    aktivitaetslevel = st.selectbox("Aktivitätslevel", ("leicht", "mittel", "schwer"), key="aktivitaet")
    ziel = st.selectbox("Dein Ziel:", ("Gewicht reduzieren", "Gewicht halten", "Gewicht zunehmen"), key="ziel")

# Berechnung wird durch den Button ausgelöst
if st.button("Bedarf berechnen"):
    # Berechnungen durchführen
    grundumsatz = berechne_grundumsatz(gewicht, groesse, alter, geschlecht)
    leistungsumsatz = berechne_leistungsumsatz(grundumsatz, aktivitaetslevel)

    # Ziel-Kalorien basierend auf Auswahl berechnen
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
    
    # Metriken (KPIs) in Spalten anzeigen
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Ziel-Kalorien pro Tag", f"{round(ziel_kalorien)} kcal")
    m_col2.metric("Protein", f"{makros['Protein (g)']} g")
    m_col3.metric("Fett", f"{makros['Fett (g)']} g")
    m_col4.metric("Kohlenhydrate", f"{makros['Kohlenhydrate (g)']} g")

    # Kuchendiagramm erstellen und anzeigen
    makro_df = pd.DataFrame.from_dict(makros, orient='index', columns=['Gramm'])
    makro_df = makro_df.reset_index().rename(columns={'index': 'Makronährstoff'})
    
    fig = px.pie(makro_df, values='Gramm', names='Makronährstoff', title='Deine Makro-Verteilung in Gramm',
                 color_discrete_map={
                     "Protein (g)": "#1f77b4",
                     "Fett (g)": "#ff7f0e",
                     "Kohlenhydrate (g)": "#2ca02c"
                 })
    st.plotly_chart(fig, use_container_width=True)

# --- Trennlinie ---
st.divider()

# --- TEIL 2: LEBENSMITTEL-SUCHER ---
st.header("2. Finde Lebensmittel in der Datenbank")

suchbegriff = st.text_input("Suche nach einem Lebensmittel (z.B. 'hähnchen' oder 'quark'):", key="suche")

# Nur ausführen, wenn die Datenbank geladen wurde
if df_lebensmittel is not None:
    # Nur suchen, wenn der Benutzer etwas eingegeben hat
    if suchbegriff:
        such_ergebnisse = finde_lebensmittel(suchbegriff, df_lebensmittel)
        
        st.write(f"Gefunden: **{len(such_ergebnisse)}** Einträge für '{suchbegriff}'")

        # Nur anzeigen, wenn Ergebnisse vorhanden sind, um Fehler zu vermeiden
        if not such_ergebnisse.empty:
            anzuzeigende_spalten = ['Lebensmittelname_Deutsch', 'Energie_kcal', 'Protein_g', 'Fett_g', 'Kohlenhydrate_g']
            st.dataframe(such_ergebnisse[anzuzeigende_spalten])
        else:
            st.warning("Keine passenden Lebensmittel gefunden.")
    else:
        st.info("Bitte gib einen Suchbegriff ein, um die Datenbank zu durchsuchen.")

