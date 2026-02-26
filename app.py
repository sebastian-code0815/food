import streamlit as st
import pandas as pd

# ==============================================================================
# DATENBANK LADEN (mit Spaltennamen-Bereinigung)
# ==============================================================================
@st.cache_data
def lade_datenbank():
    try:
        df = pd.read_excel('lebensmittel.xlsx')
        # === NEU: Spaltennamen bereinigen ===
        # Entfernt führende/nachfolgende Leerzeichen von allen Spaltennamen
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("FEHLER: Die Datei 'lebensmittel.xlsx' wurde nicht gefunden.")
        return None

df_lebensmittel = lade_datenbank()

# ==============================================================================
# LOGIK-FUNKTIONEN
# ==============================================================================
def berechne_grundumsatz(gewicht, groesse, alter, geschlecht):
    geschlecht_klein = geschlecht.lower()
    if geschlecht_klein == "männlich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + 5
    elif geschlecht_klein == "weiblich":
        grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) - 161
    else:
        return 0
    return grundumsatz

def berechne_leistungsumsatz(grundumsatz, aktivitaetslevel):
    level_klein = aktivitaetslevel.lower()
    if level_klein == "leicht": pal_faktor = 1.5
    elif level_klein == "mittel": pal_faktor = 1.7
    elif level_klein == "schwer": pal_faktor = 2.0
    else: pal_faktor = 1.2
    return grundumsatz * pal_faktor

# === KORRIGIERTE SUCHFUNKTION ===
def finde_lebensmittel(name_teil, datenbank):
    if datenbank is not None and name_teil:
        suchbegriff = name_teil.lower()
        # KORREKTUR: Wir verwenden den exakten Spaltennamen aus Ihrer Excel-Datei
        ergebnisse = datenbank[datenbank['Lebensmittelname_Deutsch'].str.lower().str.contains(suchbegriff, na=False)]
        return ergebnisse
    return pd.DataFrame()


def berechne_makros(ziel_kalorien, gewicht):
    # 1. Protein berechnen (in Gramm)
    protein_gramm = 2 * gewicht
    protein_kcal = protein_gramm * 4

    # 2. Fett berechnen (in Gramm)
    fett_kcal = ziel_kalorien * 0.25
    fett_gramm = fett_kcal / 9

    # 3. Kohlenhydrate berechnen (der Rest)
    rest_kcal = ziel_kalorien - protein_kcal - fett_kcal
    kohlenhydrate_gramm = rest_kcal / 4

    # Wir geben ein Dictionary mit den Ergebnissen zurück
    return {
        "Protein (g)": round(protein_gramm),
        "Fett (g)": round(fett_gramm),
        "Kohlenhydrate (g)": round(kohlenhydrate_gramm)
    }



# ==============================================================================
# STREAMLIT OBERFLÄCHE
# ==============================================================================
st.set_page_config(layout="wide")
st.title("Dein persönlicher Ernährungsplan-Generator")

# --- TEIL 1: KALORIENRECHNER ---
st.header("1. Berechne deinen Tagesbedarf")
# ... (dieser Teil bleibt unverändert) ...
col1, col2 = st.columns(2)
with col1:
    geschlecht = st.selectbox("Geschlecht", ("männlich", "weiblich"))
    gewicht = st.number_input("Gewicht (in kg)", min_value=30.0, value=85.0, step=0.5)
    groesse = st.number_input("Größe (in cm)", min_value=120, value=180)
with col2:
    alter = st.slider("Alter (in Jahren)", 16, 100, 37)
    aktivitaetslevel = st.selectbox("Aktivitätslevel", ("leicht", "mittel", "schwer"))

if st.button("Bedarf berechnen"):
    grundumsatz = berechne_grundumsatz(gewicht, groesse, alter, geschlecht)
    leistungsumsatz = berechne_leistungsumsatz(grundumsatz, aktivitaetslevel)
    st.success(f"Dein täglicher Kalorienbedarf: **{round(leistungsumsatz)} kcal**")
    st.info(f"Dein Grundumsatz: {round(grundumsatz)} kcal")
    
# --- TEIL 2: LEBENSMITTEL-SUCHER ---
st.divider()

st.header("2. Finde Lebensmittel in der Datenbank")

suchbegriff = st.text_input("Suche nach einem Lebensmittel (z.B. 'hähnchen' oder 'quark'):")

if df_lebensmittel is not None:
    # Nur suchen, wenn der Benutzer etwas eingegeben hat
    if suchbegriff:
        such_ergebnisse = finde_lebensmittel(suchbegriff, df_lebensmittel)
        
        st.write(f"Gefunden: **{len(such_ergebnisse)}** Einträge für '{suchbegriff}'")

        # === NEUE PRÜFUNG: Nur anzeigen, wenn der DataFrame nicht leer ist ===
        if not such_ergebnisse.empty:
            # Spalten definieren, die wir anzeigen wollen
            anzuzeigende_spalten = ['Lebensmittelname_Deutsch', 'Energie_kcal', 'Protein_g', 'Fett_g', 'Kohlenhydrate_g']
            
            # Sicherstellen, dass alle Spalten im DataFrame existieren
            existierende_spalten = [col for col in anzuzeigende_spalten if col in such_ergebnisse.columns]
            
            st.dataframe(such_ergebnisse[existierende_spalten])
        else:
            st.warning("Keine passenden Lebensmittel gefunden.")
    else:
        # Nachricht, wenn noch nichts eingegeben wurde
        st.info("Bitte gib einen Suchbegriff ein, um die Datenbank zu durchsuchen.")
