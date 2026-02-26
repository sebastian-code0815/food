import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ==============================================================================
# SEITEN-KONFIGURATION (muss ganz am Anfang sein)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Ernährungsplan-Generator")

# ==============================================================================
# SESSION STATE INITIALISIERUNG (Das "Gedächtnis" der App)
# ==============================================================================
if 'ziel_werte' not in st.session_state:
    st.session_state.ziel_werte = {}
if 'user_lebensmittel' not in st.session_state:
    st.session_state.user_lebensmittel = []
if 'wochenplan' not in st.session_state:
    st.session_state.wochenplan = {
        "Montag": [], "Dienstag": [], "Mittwoch": [],
        "Donnerstag": [], "Freitag": [], "Samstag": [], "Sonntag": []
    }

# ==============================================================================
# DATENBANK LADEN & KOMBINIEREN
# ==============================================================================
@st.cache_data
def lade_datenbank():
    try:
        df = pd.read_excel('lebensmittel.xlsx')
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("FEHLER: 'lebensmittel.xlsx' nicht im Repository gefunden. Bitte hochladen!")
        return pd.DataFrame()

df_bls = lade_datenbank()
df_user = pd.DataFrame(st.session_state.user_lebensmittel)
df_lebensmittel = pd.concat([df_bls, df_user], ignore_index=True) if not df_bls.empty or not df_user.empty else pd.DataFrame(columns=['Lebensmittelname_Deutsch', 'Energie_kcal', 'Protein_g', 'Fett_g', 'Kohlenhydrate_g'])

# ==============================================================================
# LOGIK-FUNKTIONEN (Der "Motor" der App)
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
# STREAMLIT OBERFLÄCHE (Das "Cockpit" der App)
# ==============================================================================
st.title("Dein persönlicher Ernährungsplan-Generator")

# --- Tabs für eine bessere Struktur ---
tab1, tab2, tab3 = st.tabs(["🎯 Zielsetzung", "➕ Lebensmittel hinzufügen", "📅 Wochenplan"])

# --- TAB 1: ZIELSETZUNG ---
with tab1:
    st.header("Schritt 1: Berechne deinen Tagesbedarf und deine Makros")
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
        st.session_state.ziel_werte = {"Kalorien": round(ziel_kalorien), "Protein (g)": makros["Protein (g)"], "Fett (g)": makros["Fett (g)"], "Kohlenhydrate (g)": makros["Kohlenhydrate (g)"]}
        st.success("Ziele erfolgreich gespeichert!")

    if st.session_state.ziel_werte:
        st.subheader("Deine gespeicherten Zielwerte:")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Ziel-Kalorien", f"{st.session_state.ziel_werte['Kalorien']} kcal")
        m_col2.metric("Ziel-Protein", f"{st.session_state.ziel_werte['Protein (g)']} g")
        m_col3.metric("Ziel-Fett", f"{st.session_state.ziel_werte['Fett (g)']} g")
        m_col4.metric("Ziel-Kohlenhydrate", f"{st.session_state.ziel_werte['Kohlenhydrate (g)']} g")
        
        makro_df = pd.DataFrame.from_dict(st.session_state.ziel_werte, orient='index', columns=['Wert']).iloc[1:]
        makro_df = makro_df.reset_index().rename(columns={'index': 'Makronährstoff'})
        fig = px.pie(makro_df, values='Wert', names='Makronährstoff', title='Deine Makro-Verteilung in Gramm')
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: EIGENE LEBENSMITTEL HINZUFÜGEN ---
with tab2:
    st.header("Hier kannst du Lebensmittel zur Datenbank hinzufügen")
    with st.form("neues_lebensmittel_form", clear_on_submit=True):
        st.write("Fülle die Nährwerte pro 100g aus:")
        form_col1, form_col2, form_col3, form_col4, form_col5 = st.columns(5)
        with form_col1: lm_name = st.text_input("Name des Lebensmittels*")
        with form_col2: lm_kcal = st.number_input("Kalorien (kcal)*", min_value=0)
        with form_col3: lm_protein = st.number_input("Protein (g)*", min_value=0.0, format="%.1f")
        with form_col4: lm_fett = st.number_input("Fett (g)*", min_value=0.0, format="%.1f")
        with form_col5: lm_kh = st.number_input("Kohlenhydrate (g)*", min_value=0.0, format="%.1f")
        submitted = st.form_submit_button("Lebensmittel speichern")
        if submitted:
            if not lm_name:
                st.error("Bitte gib einen Namen für das Lebensmittel ein.")
            else:
                neues_lm = {"Lebensmittelname_Deutsch": lm_name, "Energie_kcal": lm_kcal, "Protein_g": lm_protein, "Fett_g": lm_fett, "Kohlenhydrate_g": lm_kh}
                st.session_state.user_lebensmittel.append(neues_lm)
                st.success(f"'{lm_name}' wurde zu deiner persönlichen Datenbank hinzugefügt!")

    st.subheader("Deine persönlich hinzugefügten Lebensmittel:")
    st.dataframe(df_user)

# --- TAB 3: WOCHENPLAN ---
with tab3:
    st.header("Schritt 2: Stelle deinen Wochenplan zusammen")
    wochentag = st.selectbox("Wähle einen Tag zum Bearbeiten:", list(st.session_state.wochenplan.keys()))
    search_col, plan_col = st.columns([0.6, 0.4])

    with search_col:
        st.subheader(f"Lebensmittel für {wochentag} suchen & hinzufügen")
        suchbegriff = st.text_input("Suche nach einem Lebensmittel:", key=f"suche_{wochentag}")
        if suchbegriff:
            such_ergebnisse = finde_lebensmittel(suchbegriff, df_lebensmittel)
            if not such_ergebnisse.empty:
                for index, row in such_ergebnisse.head(10).iterrows():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([0.5, 0.3, 0.2])
                        c1.text(row['Lebensmittelname_Deutsch'])
                        menge = c2.number_input("Menge (g)", 1, 2000, 100, key=f"menge_{wochentag}_{index}")
                        if c3.button("➕", key=f"add_{wochentag}_{index}"):
                            faktor = menge / 100.0
                            hinzugefuegt = {"Name": row['Lebensmittelname_Deutsch'], "Menge (g)": menge, "Kalorien": round(row['Energie_kcal'] * faktor), "Protein (g)": round(row['Protein_g'] * faktor, 1), "Fett (g)": round(row['Fett_g'] * faktor, 1), "Kohlenhydrate (g)": round(row['Kohlenhydrate_g'] * faktor, 1)}
                            st.session_state.wochenplan[wochentag].append(hinzugefuegt)
                            st.success(f"{menge}g {row['Lebensmittelname_Deutsch']} zu {wochentag} hinzugefügt!")
            else:
                st.warning("Keine passenden Lebensmittel gefunden.")

    with plan_col:
        st.subheader(f"Dein Plan für {wochentag}")
        if st.session_state.wochenplan[wochentag]:
            plan_df = pd.DataFrame(st.session_state.wochenplan[wochentag])
            st.dataframe(plan_df)
            total_kcal = plan_df['Kalorien'].sum()
            st.metric("Gesamtkalorien des Tages", f"{round(total_kcal)} kcal")
            if st.session_state.ziel_werte:
                kcal_progress = min(total_kcal / st.session_state.ziel_werte['Kalorien'], 1.0) if st.session_state.ziel_werte['Kalorien'] > 0 else 0
                st.progress(kcal_progress)
            if st.button(f"Plan für {wochentag} zurücksetzen", key=f"reset_{wochentag}"):
                st.session_state.wochenplan[wochentag] = []
                st.rerun()
        else:
            st.info(f"Der Plan für {wochentag} ist noch leer.")

    st.divider()

    # --- DOWNLOAD-FUNKTION ---
    st.header("Schritt 3: Lade deinen kompletten Wochenplan herunter")
    if any(st.session_state.wochenplan.values()):
        def erstelle_excel_download():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for tag, mahlzeiten in st.session_state.wochenplan.items():
                    if mahlzeiten:
                        tages_df = pd.DataFrame(mahlzeiten)
                        summen_zeile = tages_df[['Kalorien', 'Protein (g)', 'Fett (g)', 'Kohlenhydrate (g)']].sum().to_frame().T
                        summen_zeile.index = ['GESAMT']
                        tages_df = pd.concat([tages_df, summen_zeile])
                        tages_df.to_excel(writer, sheet_name=tag, index=True)
            processed_data = output.getvalue()
            return processed_data

        excel_file = erstelle_excel_download()
        st.download_button(label="📥 Wochenplan als Excel herunterladen", data=excel_file, file_name="mein_wochenplan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

