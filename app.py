# --- Funktion 1: Grundumsatz (war bereits korrekt) ---
def berechne_grundumsatz(gewicht, groesse, alter, geschlecht):
  geschlecht_klein = geschlecht.lower()
  if geschlecht_klein == "m" or geschlecht_klein == "männlich":
    grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + 5
  elif geschlecht_klein == "w" or geschlecht_klein == "weiblich":
    grundumsatz = (10 * gewicht) + (6.25 * groesse) - (5 * alter) - 161
  else:
    return "Ungültiges Geschlecht angegeben."
  return grundumsatz


# --- Funktion 2: Leistungsumsatz (korrigierte Version) ---
def berechne_leistungsumsatz(grundumsatz, aktivitaetslevel):
  """
  Berechnet den Leistungsumsatz basierend auf dem Grundumsatz und einem Aktivitätslevel.
  """
  level_klein = aktivitaetslevel.lower() # Macht die Eingabe robust

  if level_klein == "liegend":
    pal_faktor = 1.2
  elif level_klein == "leicht":
    pal_faktor = 1.45
  elif level_klein == "moderat":
    pal_faktor = 1.65
  elif level_klein == "mittel":
    pal_faktor = 1.85
  elif level_klein == "schwer":
    pal_faktor = 2.2
  else:
    return "Ungültiges Aktivitätslevel. Bitte 'liegend', 'leicht', 'mittel', 'moderat' oder 'schwer' verwenden."

  # Diese Zeilen müssen eingerückt sein, um zur Funktion zu gehören!
  leistungsumsatz = grundumsatz * pal_faktor
  return leistungsumsatz


# === JETZT RUFEN WIR ALLES AUF ===

# 1. Grundumsatz berechnen
mein_grundumsatz = berechne_grundumsatz(85, 180, 37, "männlich")
print(f"Mein berechneter Grundumsatz beträgt: {round(mein_grundumsatz)} kcal")

# 2. Leistungsumsatz berechnen (Gesamtbedarf)
# Wir übergeben das Ergebnis der ersten Funktion an die zweite
mein_tagesbedarf = berechne_leistungsumsatz(mein_grundumsatz, "mittel")
print(f"Mein täglicher Kalorienbedarf (Leistungsumsatz) beträgt: {round(mein_tagesbedarf)} kcal")

import pandas as pd

# Der Dateiname Ihrer Excel-Datei
datei_pfad = 'lebensmittel.xlsx' # Endung auf .xlsx geändert!

try:
    # Wir verwenden jetzt pd.read_excel()
    # Hier brauchen wir keinen 'sep' Parameter mehr
    df_lebensmittel = pd.read_excel(datei_pfad)

    # Schauen wir uns die ersten Zeilen an, um zu prüfen, ob es geklappt hat
    print("--- Erfolgreich eingelesen! Erste 5 Lebensmittel: ---")
    print(df_lebensmittel.head())

    # Welche Spalten haben wir?
    print("\n--- Verfügbare Spalten: ---")
    print(df_lebensmittel.columns)

except FileNotFoundError:
    print(f"FEHLER: Die Datei '{datei_pfad}' wurde nicht gefunden. Bitte hochladen und sicherstellen, dass der Name exakt stimmt!")
except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")

def finde_lebensmittel(name_teil, datenbank):
    """
    Sucht in der Lebensmittel-Datenbank nach einem Lebensmittel, das den Suchbegriff enthält.
    Gibt die ersten 5 Treffer zurück.
    """
    # Suchbegriff in Kleinbuchstaben umwandeln für eine unempfindliche Suche
    suchbegriff = name_teil.lower()

    # Filtere den DataFrame: Die Spalte 'Lebensmittelname_Deutsch' (in Kleinbuchstaben) soll den Suchbegriff enthalten
    # .str.contains() ist die Pandas-Methode für die Textsuche
    # na=False behandelt fehlende Werte sauber
    ergebnisse = datenbank[datenbank['Lebensmittelname_Deutsch'].str.lower().str.contains(suchbegriff, na=False)]

    # Wir geben nur die ersten 5 Ergebnisse zurück, um die Liste kurz zu halten
    return ergebnisse.head()

# Nur ausführen, wenn das Einlesen geklappt hat
if 'df_lebensmittel' in locals():
    # --- Testen wir unsere Suchfunktion ---
    print("\n--- Suche nach 'hähnchenbrust': ---")
    suche1 = finde_lebensmittel("hähnchenbrust", df_lebensmittel)
    print(suche1[['Lebensmittelname_Deutsch', 'Energie_kcal', 'Protein_g']]) # Zeige nur relevante Spalten

    print("\n--- Suche nach 'haferflocken': ---")
    suche2 = finde_lebensmittel("haferflocken", df_lebensmittel)
    print(suche2[['Lebensmittelname_Deutsch', 'Energie_kcal', 'Protein_g', 'Fett_g', 'Kohlenhydrate_g']])
