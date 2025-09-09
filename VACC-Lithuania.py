import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import shutil
import urllib.request
import zipfile
import sys
import subprocess
import ctypes
import pefile
import requests
from datetime import datetime
from win32com.client import Dispatch
import logging
import re
from typing import List, Optional
import pandas as pd
import psutil



URL = "https://vacc-lithuania.lima-city.at/Installer/"
FIR = "EYVL"
Testing = False #Change the base path to Meipass for exe file




FIR_fullname = os.path.basename(__file__).split(".")[0]

if Testing==True:
    logo_path = 'Logo.png'
    exe_path = FIR_fullname + ".py"
    proc_path = 'procedure_generation.py'
else:
    base_path = sys._MEIPASS
    logo_path=os.path.join(base_path, 'Logo.png')
    exe_path = FIR_fullname + ".exe"
    proc_path = os.path.join(base_path, 'procedure_generation.py')


# Language dictionaries
translations = {
    "Deutsch": {
        "custom_files": "Benutzerdefinierte Dateien ",
        "setting": "Einstellungen",
        "language": "Sprache",
        "name": "Name:",
        "vatsim_id": "Vatsim ID:",
        "vatsim_password": "Vatsim Passwort:",
        "rating": "Bewertung:",
        "hoppie_code": "Hoppie-Code:",
        "afv_path": "Pfad für das Audio Tool von Vatsim:",
        "browse": "Durchsuchen",
        "save": "Speichern",
        "missing_data_title": "Fehlende Daten",
        "missing_data": "Mindestens Name, Vatsim ID, Vatsim Passwort und Bewertung müssen festgelegt werden.",
        "update_available": "Update verfügbar",
        "installer_version": "Eine neuere Version des Installers ist verfügbar.",
        "error_title": "Fehler",
        "error installercheck": "Keine Internetverbindung oder Online-Version nicht gefunden.",
        "fresh_install": "Neuinstallation",
        "Choose_a_profile": "Profil auswählen",
        "start": "Starten",
        "airac_msg":"Deine AIRAC-Daten stimmen nicht mit der Online-Konfiguration überein.",
        "airac_Navdatapro_notfound":"Es wurden keine AIRAC-Dateien gefunden. Bitte installiere die AIRAC-Daten <Global Air Traffic Control> in das Verzeichnis des Programms.",
        "airac_Navigator_notfound":"Es wurden keine AIRAC-Dateien gefunden. Bitte installiere die AIRAC-Daten <FS-Navigator 4.x> in das Verzeichnis des Programms.",
    },
    "Dutch": {
        "custom_files": "Aangepaste Bestanden",
        "setting": "Instelling",
        "language": "Taal",
        "name": "Naam:",
        "vatsim_id": "Vatsim ID:",
        "vatsim_password": "Vatsim wachtwoord:",
        "rating": "Beoordeling:",
        "hoppie_code": "Hoppie-code:",
        "afv_path": "Pad voor de audiotool van Vatsim:",
        "browse": "Bladeren",
        "save": "Opslaan",
        "missing_data_title": "Ontbrekende gegevens",
        "missing_data": "Ten minste naam, Vatsim ID, Vatsim wachtwoord en beoordeling moeten worden ingesteld.",
        "update_available": "Update beschikbaar",
        "installer_version": "Er is een nieuwere versie van de installer beschikbaar.",
        "error_title": "Fout",
        "error installercheck": "Geen internetverbinding of online versie niet gevonden.",
        "fresh_install": "Schone installatie",
        "Choose_a_profile": "Kies een profiel",
        "start": "Starten",
        "airac_msg":"Jouw AIRAC-gegevens komen niet overeen met de online configuratie.",
        "airac_Navdatapro_notfound":"Er zijn geen AIRAC-bestanden gevonden. Installeer de AIRAC-gegevens <Global Air Traffic Control> in de programmamap",
        "airac_Navigator_notfound":"Er zijn geen AIRAC-bestanden gevonden. Installeer de AIRAC-gegevens <FS-Navigator 4.x> in de programmamap",
    },
    "English": {
        "custom_files": "Custom Files",
        "setting": "Setting",
        "language": "Language",
        "name": "Name:",
        "vatsim_id": "Vatsim ID:",
        "vatsim_password": "Vatsim password:",
        "rating": "Rating:",
        "hoppie_code": "Hoppie code:",
        "afv_path": "Path for the audio tool from Vatsim:",
        "browse": "Browse",
        "save": "Save",
        "missing_data_title": "Missing data",
        "missing_data": "At least name, Vatsim ID, Vatsim password, and rating must be set.",
        "update_available": "Update available",
        "installer_version": "A newer version of the installer is available.",
        "error_title": "Error",
        "error installercheck": "No internet connection, or online version not found.",
        "fresh_install": "Fresh install",
        "Choose_a_profile": "Choose a profile",
        "start": "Start",
        "airac_msg":"Your AIRAC data doesn't match the online config.",
        "airac_Navdatapro_notfound":"No AIRAC files were found. Please install the AIRAC data <Global Air Traffic Control> into the program directory.",
        "airac_Navigator_notfound":"No AIRAC files were found. Please install the AIRAC data <FS-Navigator 4.x> into the program directory.",
    },
    "French": {
        "custom_files": "Fichiers Personnalisés",
        "setting": "Paramètre",
        "language": "Langue",
        "name": "Nom:",
        "vatsim_id": "ID Vatsim:",
        "vatsim_password": "Mot de passe Vatsim:",
        "rating": "Évaluation:",
        "hoppie_code": "Code Hoppie:",
        "afv_path": "Chemin pour l'outil audio de Vatsim:",
        "browse": "Parcourir",
        "save": "Sauvegarder",
        "missing_data_title": "Données manquantes",
        "missing_data": "Au moins le nom, l'ID Vatsim, le mot de passe Vatsim et l'évaluation doivent être définis.",
        "update_available": "Mise à jour disponible",
        "installer_version": "Une nouvelle version de l'installateur est disponible.",
        "error_title": "Erreur",
        "error installercheck": "Pas de connexion Internet ou version en ligne introuvable.",
        "fresh_install": "Nouvelle installation",
        "Choose_a_profile": "Choisissez un profil",
        "start": "Démarrer",
        "airac_msg":"Vos données AIRAC ne correspondent pas à la configuration en ligne.",
        "airac_Navdatapro_notfound":"Aucun fichier AIRAC n’a été trouvé. Veuillez installer les données AIRAC <Global Air Traffic Control> dans le répertoire du programme.",
        "airac_Navigator_notfound":"Aucun fichier AIRAC n’a été trouvé. Veuillez installer les données AIRAC <FS-Navigator 4.x> dans le répertoire du programme.",
    },
    "Italian": {
        "custom_files": "File Personalizzati",
        "setting": "Impostazione",
        "language": "Lingua",
        "name": "Nome:",
        "vatsim_id": "ID Vatsim:",
        "vatsim_password": "Password Vatsim:",
        "rating": "Valutazione:",
        "hoppie_code": "Codice Hoppie:",
        "afv_path": "Percorso per lo strumento audio di Vatsim:",
        "browse": "Sfoglia",
        "save": "Salva",
        "missing_data_title": "Dati mancanti",
        "missing_data": "Devono essere impostati almeno nome, ID Vatsim, password Vatsim e valutazione.",
        "update_available": "Aggiornamento disponibile",
        "installer_version": "È disponibile una versione più recente dell'installer.",
        "error_title": "Errore",
        "error installercheck": "Nessuna connessione a Internet o versione online non trovata.",
        "fresh_install": "Nuova installazione",
        "Choose_a_profile": "Scegli un profilo",
        "start": "Avvia",
        "airac_msg":"I tuoi dati AIRAC non corrispondono alla configurazione online.",
        "airac_Navdatapro_notfound":"Nessun file AIRAC trovato. Si prega di installare i dati AIRAC <Global Air Traffic Control> nella directory del programma.",
        "airac_Navigator_notfound":"Nessun file AIRAC trovato. Si prega di installare i dati AIRAC <FS-Navigator 4.x> nella directory del programma.",
    },
    "Lithuanian": {
        "custom_files": "Pritaikyti Failai",
        "setting": "Nustatymas",
        "language": "Kalba",
        "name": "Vardas:",
        "vatsim_id": "Vatsim ID:",
        "vatsim_password": "Vatsim slaptažodis:",
        "rating": "Įvertinimas:",
        "hoppie_code": "Hoppie kodas:",
        "afv_path": "Kelias į garso įrankį iš Vatsim:",
        "browse": "Naršyti",
        "save": "Išsaugoti",
        "missing_data_title": "Trūksta duomenų",
        "missing_data": "Turi būti nustatyta bent jau vardas, Vatsim ID, Vatsim slaptažodis ir įvertinimas.",
        "update_available": "Galimas atnaujinimas",
        "installer_version": "Galima naujesnė diegimo programos versija.",
        "error_title": "Klaida",
        "error installercheck": "Nėra interneto ryšio arba nerasta internetinė versija.",
        "fresh_install": "Šviežia diegimas",
        "Choose_a_profile": "Pasirinkite profilį",
        "start": "Pradėti",
        "airac_msg":"Jūsų AIRAC duomenys neatitinka internetinės konfigūracijos.",
        "airac_Navdatapro_notfound":"AIRAC failų nerasta. Prašome įdiegti AIRAC duomenis <Global Air Traffic Control> į programos katalogą.",
        "airac_Navigator_notfound":"AIRAC failų nerasta. Prašome įdiegti AIRAC duomenis <FS-Navigator 4.x> į programos katalogą.",
    },
    "Slovak": {
        "custom_files": "Vlastné Súbory",
        "setting": "Nastavenie",
        "language": "Jazyk",
        "name": "Meno:",
        "vatsim_id": "Vatsim ID:",
        "vatsim_password": "Vatsim heslo:",
        "rating": "Hodnotenie:",
        "hoppie_code": "Hoppie kód:",
        "afv_path": "Cesta k zvukovému nástroju od Vatsimu:",
        "browse": "Prehľadávať",
        "save": "Uložiť",
        "missing_data_title": "Chýbajúce údaje",
        "missing_data": "Musí byť nastavené minimálne meno, Vatsim ID, Vatsim heslo a hodnotenie.",
        "update_available": "K dispozícii je aktualizácia",
        "installer_version": "Je dostupná novšia verzia inštalátora.",
        "error_title": "Chyba",
        "error installercheck": "Žiadne pripojenie na internet alebo nebola nájdená online verzia.",
        "fresh_install": "Nová inštalácia",
        "Choose_a_profile": "Vyberte profil",
        "start": "Štart",
        "airac_msg":"Vaše AIRAC údaje sa nezhodujú s online konfiguráciou.",
        "airac_Navdatapro_notfound":"Neboli nájdené žiadne súbory AIRAC. Nainštalujte prosím údaje AIRAC <Global Air Traffic Control> do adresára programu.",
        "airac_Navigator_notfound":"Neboli nájdené žiadne súbory AIRAC. Nainštalujte prosím údaje AIRAC <FS-Navigator 4.x> do adresára programu.",
    }
}
def translate(key):
    return translations[selected_language].get(key, key)



# Funktion zum Laden der Konfiguration
def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    else:
        return {
            "name": "",
            "vatsim_id": "",
            "vatsim_password": "",
            "rating": "",
            "hoppie_code": "",
            "afv_path": "",
            "euroscope_version": "0.0.0.0.0.0",
            "sectorfile_version": "0.0.0.0.0.0",
            "selected_language": "English"
        }

def fetch_settings():
    # CSV-Datei einlesen
    df = pd.read_csv("temp/setting.csv")

    # Sicherstellen, dass die benötigten Spalten existieren
    required_columns = ["minLat", "maxLat", "minLon", "maxLon", "SidStarAirports", "Airac"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Eine oder mehrere benötigte Spalten fehlen in der CSV-Datei.")

    # Erste Zeile als Dictionary zurückgeben
    setting = df.iloc[0].to_dict()
    return setting

def custom_files():
    # Relativer Pfad zum Ordner, den du öffnen möchtest
    relative_folder_path = 'Customfiles'

    # Umwandlung in absoluten Pfad
    absolute_folder_path = os.path.join(os.getcwd(), relative_folder_path, FIR)

    # Prüfen, ob der Ordner existiert
    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        # Ordner im Windows Explorer öffnen
        subprocess.run(['explorer', absolute_folder_path])
    else:
        print(f"Der Ordner {absolute_folder_path} existiert nicht.")

def dezimal_zu_dms(dezimalgrad, isLAT):
    dezimalgrad = float(dezimalgrad)
    # Bestimmen des Vorzeichens
    vorzeichen = 'S' if dezimalgrad < 0 else 'N' if isLAT == 'true' else 'W' if dezimalgrad < 0 else 'E'

    # Absolutwert des Dezimalgrads
    dezimalgrad = abs(dezimalgrad)

    # Berechnen der Grad, Minuten und Sekunden
    grad = int(dezimalgrad)
    minuten = (dezimalgrad - grad) * 60
    minuten_gerundet = int(minuten)
    sekunden = (minuten - minuten_gerundet) * 60

    # Formatieren der Werte auf die gewünschten Dezimalstellen
    grad_formatiert = f"{grad:03d}"
    minuten_formatiert = f"{minuten_gerundet:02d}"
    sekunden_formatiert = f"{sekunden:06.3f}"

    # Rückgabe im DMS-Format
    return f"{vorzeichen}{grad_formatiert}.{minuten_formatiert}.{sekunden_formatiert}"


def version_tuple(version):
    return tuple(map(int, (version.split("."))))

def process_VOR(settings, file_path="NavDataPro/Navaids.txt"):
    min_lat = settings['minLat']
    max_lat = settings['maxLat']
    min_lon = settings['minLon']
    max_lon = settings['maxLon']
    vor_lines = []
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(",")

            if len(parts) < 3:
                continue
            if not 108.0 <= float(parts[2]) <= 118.0:
                continue

            ident = parts[0].ljust(4)
            frequency = parts[2]
            lat = float(parts[6])
            lon = float(parts[7])

            if min_lat < lat < max_lat and min_lon < lon < max_lon:
                lat_dms = dezimal_zu_dms(lat, 'true')
                lon_dms = dezimal_zu_dms(lon, 'false')
                vor_lines.append(f"{ident} {frequency} {lat_dms} {lon_dms}\n")
    return vor_lines


def process_NDB(settings, file_path="NavDataPro/Navaids.txt"):
    min_lat = settings['minLat']
    max_lat = settings['maxLat']
    min_lon = settings['minLon']
    max_lon = settings['maxLon']
    ndb_lines = []
            
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(",")

            if len(parts) < 3:
                continue
            if not 190.0 <= float(parts[2]) <= 1750.0:
                continue

            ident = parts[0].ljust(4)
            frequency = parts[2]
            lat = float(parts[6])
            lon = float(parts[7])

            if min_lat < lat < max_lat and min_lon < lon < max_lon:
                lat_dms = dezimal_zu_dms(lat, 'true')
                lon_dms = dezimal_zu_dms(lon, 'false')
                ndb_lines.append(f"{ident} {frequency} {lat_dms} {lon_dms}\n")
    return ndb_lines



def process_Fixes(settings, file_path="NavDataPro/waypoints.txt"):
    min_lat = settings['minLat']
    max_lat = settings['maxLat']
    min_lon = settings['minLon']
    max_lon = settings['maxLon']
    fix_lines = []

    df = pd.read_csv("temp/waypoint.csv", dtype=str)  # Alles als String einlesen
    df = df.fillna('')  # NaN-Werte durch leere Strings ersetzen
    # Zeilen im gewünschten Format speichern
    fix_lines = [
        f"{row['Ident'].ljust(10)} {dezimal_zu_dms(row['LAT'], 'true')} {dezimal_zu_dms(row['LON'], 'false')}\n"
        for _, row in df.iterrows()
    ]


    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(",")

            if len(parts) < 3:
                continue

            ident = parts[0].ljust(10)
            lat = float(parts[1])
            lon = float(parts[2])

            if min_lat < lat < max_lat and min_lon < lon < max_lon:
                lat_dms = dezimal_zu_dms(lat, 'true')
                lon_dms = dezimal_zu_dms(lon, 'false')
                fix_lines.append(f"{ident} {lat_dms} {lon_dms}\n")
    return fix_lines

def process_AIRPORT(settings):
    airports = settings['SidStarAirports']
    airports = airports.replace(" ", "")
    # Die ICAO-Codes in eine Liste umwandeln
    valid_airports = set((airports.split(',')))
    df = pd.read_csv("temp/airport.csv")
    df = df.fillna('')  # NaN-Werte durch leere Strings ersetzen
    AIRPORT_lines=[]
    for index, row in df.iterrows():
        if not matches_airport(row['ICAO'], valid_airports):
            continue  # Überspringe die Datei, wenn der ICAO-Code nicht in der Liste enthalten ist
        AIRPORT_lines.append(f"{row['ICAO']} 000.000 {dezimal_zu_dms(row['LAT'], 'true')} {dezimal_zu_dms(row['LON'], 'false')} D\n")
    return AIRPORT_lines

def process_RUNWAY(settings):
    airports = settings['AirportRWY']
    airports = airports.replace(" ", "")
    # Die ICAO-Codes in eine Liste umwandeln
    valid_airports = set((airports.split(',')))
    df = pd.read_csv("temp/runway.csv")
    df = df.fillna('')  # NaN-Werte durch leere Strings ersetzen
    RWY_lines=[]
    for index, row in df.iterrows():
        if not matches_airport(row['ICAO'], valid_airports):
            continue  # Überspringe die Datei, wenn der ICAO-Code nicht in der Liste enthalten ist
        RWY_lines.append(f"{row['Ident1']} {row['Ident2']} {row['Course1']} {row['Course2']} {dezimal_zu_dms(row['LAT1'], 'true')} {dezimal_zu_dms(row['LON1'], 'false')} {dezimal_zu_dms(row['LAT2'], 'true')} {dezimal_zu_dms(row['LON2'], 'false')} {row['ICAO']}\n")
    return RWY_lines

def matches_airport(icao, valid_airports):
    for airport in valid_airports:
        if icao.startswith(airport):  # Entferne das '*' und prüfe auf den Präfix
            return True
    return False

def process_SID():
    df = pd.read_csv("temp/Procedure.csv")
    SID_lines=[]
    for index, row in df[df['Proctype'] == 'SID'].iterrows():
        first = 0
        if isinstance(row['Drawcoordinates'], str):
            coord_list = row['Drawcoordinates'].split()
            if len(coord_list) > 1:
                for i, coord in enumerate(coord_list):
                    part1, part2 = coord.split("|") if "|" in coord else (coord, None)
                    lat=float(part1)
                    lon=float(part2)
                    if first == 0:
                        header = fr"{row['ICAO']} {row['Proctype']} {row['Runway']} {row['Procident']}"
                        SID_lines.append(f"{header.ljust(41)}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
                        first = 1

                    elif i == len(coord_list) - 1:
                        SID_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n")
                    else:
                        SID_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n{" " * 41}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
    return SID_lines

def process_STAR():
    df = pd.read_csv("temp/Procedure.csv")
    STAR_lines=[]
    for index, row in df[df['Proctype'] == 'STAR'].iterrows():
            first = 0
            if isinstance(row['Drawcoordinates'], str):
                coord_list = row['Drawcoordinates'].split()
                if len(coord_list) > 1:
                    for i, coord in enumerate(coord_list):
                        part1, part2 = coord.split("|") if "|" in coord else (coord, None)
                        lat=float(part1)
                        lon=float(part2)
                        if first == 0:
                            header = fr"{row['ICAO']} {row['Proctype']} {row['Runway']} {row['Procident']}"
                            STAR_lines.append(f"{header.ljust(41)}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
                            first = 1

                        elif i == len(coord_list) - 1:
                            STAR_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n")
                        else:
                            STAR_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n{" " * 41}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
    return STAR_lines

def process_APP():
    df = pd.read_csv("temp/Procedure.csv")
    APP_lines=[]
    for index, row in df[(df['Proctype'] == 'APP') & (df['Routetype'] == 'A')].iterrows():
            first = 0
            if isinstance(row['Drawcoordinates'], str):
                coord_list = row['Drawcoordinates'].split()
                if len(coord_list) > 1:
                    for i, coord in enumerate(coord_list):
                        part1, part2 = coord.split("|") if "|" in coord else (coord, None)
                        lat=float(part1)
                        lon=float(part2)
                        if first == 0:
                            header = fr"{row['ICAO']} {row['Proctype']} {row['Runway']} {row['Procident']}"
                            APP_lines.append(f"{header.ljust(41)}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
                            first = 1

                        elif i == len(coord_list) - 1:
                            APP_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n")
                        else:
                            APP_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n{" " * 41}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
    return APP_lines

def process_FINAL():
    df = pd.read_csv("temp/Procedure.csv")
    FINAL_lines=[]
    for index, row in df[(df['Proctype'] == 'APP') & (df['Routetype'] != 'A')].iterrows():
            first = 0
            if isinstance(row['Drawcoordinates'], str):
                coord_list = row['Drawcoordinates'].split()
                if len(coord_list) > 1:
                    for i, coord in enumerate(coord_list):
                        part1, part2 = coord.split("|") if "|" in coord else (coord, None)
                        lat=float(part1)
                        lon=float(part2)
                        if first == 0:
                            header = fr"{row['ICAO']} FINAL {row['Runway']} {row['Procident']}"
                            FINAL_lines.append(f"{header.ljust(41)}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
                            first = 1

                        elif i == len(coord_list) - 1:
                            FINAL_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n")
                        else:
                            FINAL_lines.append(f" {dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}\n{" " * 41}{dezimal_zu_dms(lat, 'true')} {dezimal_zu_dms(lon, 'false')}")
    return FINAL_lines

#####################################################
##################SID/STAR COMBINER##################
#####################################################
logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("ProcedureGeneration")

class ResolvedProcedure:
    procecure_type: str
    icao: str
    runway: str
    full_id: str
    display_id: str
    waypoints: List[str]
    combiner: str

    def __init__(self, procedure_type: str, icao: str, runway: str, full_id: str, display_id: str,
                 waypoints: List[str]):
        self.procecure_type = procedure_type
        self.icao = icao
        self.runway = runway
        self.full_id = full_id
        self.display_id = display_id
        self.waypoints = remove_duplicate_waypoints(waypoints)

    def __eq__(self, other: object) -> bool | type(NotImplemented):
        if not isinstance(other, ResolvedProcedure):
            return NotImplemented
        return self.icao == other.icao and self.display_id == other.display_id and self.waypoints == other.waypoints

    def __hash__(self) -> int:
        return hash((self.icao, self.runway, self.display_id, tuple(self.waypoints)))

    def __repr__(self) -> str:
        return f"ResolvedProcedure(procedure_type={self.procecure_type}, icao={self.icao}, runway={self.runway} full_id={self.full_id}, display_id={self.display_id}, waypoints={self.waypoints})"

    def format(self):
        return f"{self.procecure_type}:{self.icao}:{self.runway}:{self.display_id}:{' '.join(self.waypoints)}; Combiner={self.combiner} | ID={self.full_id}"

def remove_duplicate_waypoints(waypoints: List[str]) -> List[str]:
    """Removes duplicates from the provided waypoints list while preserving order"""
    seen = set()
    return [x for x in waypoints if not (x in seen or seen.add(x))]

def remove_duplicate_procedures(procedures: List[ResolvedProcedure]) -> List[ResolvedProcedure]:
    """Removes duplicate procedures with identical ICAO codes, display IDs and waypoints (based on their hash)"""
    seen = set()
    return [x for x in procedures if not (x in seen or seen.add(x))]

def sort_procedures(procedures: List[ResolvedProcedure], name_sort_order: Optional[str]) -> List[ResolvedProcedure]:
    """Sort procedures based on provided name_sort_order, falling back to alphabetical sorting if missing"""
    if not name_sort_order:
        return sorted(procedures, key=lambda p: p.full_id)

    regex_patterns = name_sort_order.split(' ')
    categorized = {regex: [] for regex in regex_patterns}
    uncategorized = []

    for procedure in procedures:
        matched = False
        for regex in regex_patterns:
            if re.search(regex, procedure.full_id):
                categorized[regex].append(procedure)
                matched = True
                break
        if not matched:
            uncategorized.append(procedure)

    sorted_procedures = []
    for regex in regex_patterns:
        sorted_procedures.extend(sorted(categorized[regex], key=lambda p: p.full_id))
    sorted_procedures.extend(sorted(uncategorized, key=lambda p: p.full_id))

    return sorted_procedures

def resolve_combiner(combiner: List[str], icao: str, runway: str, proc_type: str,
                     current_last_waypoint: Optional[str] = None, combined_waypoints: Optional[List[str]] = None,
                     full_id: Optional[str] = None, display_id: Optional[str] = None,
                     should_skip_proc_ident: bool = False) -> List[ResolvedProcedure]:
    df = pd.read_csv("temp/Procedure.csv")
    if combined_waypoints is None:
        combined_waypoints = []
    if full_id is None:
        display_id = ""
    if display_id is None:
        display_id = ""

    if not combiner:  # Base care: no more route_types to process
        if runway == "ALL":
            df = pd.read_csv('temp/runway.csv')
            df_filtered = df[df['ICAO'] == icao]
            runways = df_filtered[['Ident1', 'Ident2']].to_dict(orient="records")

            all_runways = []
            for rwy in runways:
                all_runways.extend([rwy['Ident1'], rwy['Ident2']])
            all_runways.sort()

            results = []
            for rwy in all_runways:
                resolved_procedure = ResolvedProcedure(proc_type, icao, rwy, f"{rwy}x{full_id}", display_id,
                                                       combined_waypoints)
                logger.debug("Finished resolving with runway ALL: %s", resolved_procedure)
                results.append(resolved_procedure)

            return results
        else:
            resolved_procedure = ResolvedProcedure(proc_type, icao, runway, f"{runway}x{full_id}", display_id,
                                                   combined_waypoints)
            logger.debug("Finished resolving with runway %s: %s", runway, resolved_procedure)
            return [resolved_procedure]

    route_type = combiner[0]
    if route_type == '*':
        logger.debug("Skipping resolving of route_type *: %s, %s", full_id, combiner)
        return resolve_combiner(combiner[1:], icao, runway, proc_type, current_last_waypoint,
                                combined_waypoints,
                                full_id, display_id, True)

    logger.debug("Resolving route_type %s for runway %s: %s", route_type, runway, full_id)
    if current_last_waypoint:
        if proc_type == "STAR":
            filtered_df = df[
                (df["ICAO"] == icao) &
                (df["Routetype"] == route_type) &
                ((df["Runway"] == runway) | (df["Runway"] == "ALL") | (runway == "ALL")) &
                ((df["Proctype"] == "STAR") | (df["Proctype"] == "APP")) &
                (df["Waypoints"].str.startswith(current_last_waypoint, na=False))
                ]
        else:
            filtered_df = df[
                (df["ICAO"] == icao) &
                (df["Routetype"] == route_type) &
                ((df["Runway"] == runway) | (df["Runway"] == "ALL") | (runway == "ALL")) &
                (df["Proctype"] == "SID") &
                (df["Waypoints"].str.startswith(current_last_waypoint, na=False))
                ]
    else:
        if proc_type == "STAR":
            filtered_df = df[
                (df["ICAO"] == icao) &
                (df["Routetype"] == route_type) &
                ((df["Runway"] == runway) | (df["Runway"] == "ALL") | (runway == "ALL")) &
                ((df["Proctype"] == "STAR") | (df["Proctype"] == "APP"))
                ]
        else:
            filtered_df = df[
                (df["ICAO"] == icao) &
                (df["Routetype"] == route_type) &
                ((df["Runway"] == runway) | (df["Runway"] == "ALL") | (runway == "ALL")) &
                (df["Proctype"] == "SID")
                ]

    # Sortieren nach Procident
    procedures = filtered_df.to_dict(orient='records')

    if not procedures:
        logger.debug(
            "No matching procedures for ICAO: %s, combiner: %s, route_type: %s, runway: %s, proc_type: %s, current_last_waypoint: %s, display_id: %s, combined_waypoints: %s",
            icao, combiner, route_type, runway, proc_type, current_last_waypoint, display_id, combined_waypoints)
        return []

    all_results = []
    logger.debug("Starting to process %d procedures of route_type %s for %s: %s", len(procedures), route_type,
                 full_id, procedures)
    for procedure in procedures:
        waypoints: List[str] = procedure['Waypoints'].split(' ')
        new_combined_waypoints = combined_waypoints + waypoints
        new_last_waypoint = waypoints[-1]
        new_full_id = f"{full_id}x{procedure['Procident']}" if full_id else \
            procedure['Procident']
        if should_skip_proc_ident:
            new_display_id = display_id
        else:
            new_display_id = f"{display_id}x{procedure['Procident']}" if display_id else \
                procedure['Procident']
        new_runway = procedure['Runway'] if procedure['Runway'] and procedure['Runway'] != 'ALL' else runway

        logger.debug("Recursively resolving combiner %s for runway %s: %s", combiner[1:], new_runway, new_full_id)
        results = resolve_combiner(combiner[1:], icao, new_runway, proc_type, new_last_waypoint,
                                   new_combined_waypoints,
                                   new_full_id, new_display_id, False)
        all_results.extend(results)
        logger.debug("Finished recursively resolving remaining combiner %s for runway %s: %s", combiner[1:],
                     new_runway, new_full_id)

    logger.debug("Finished processing %s procedures of route_type %s for %s: %s", len(procedures), route_type,
                 full_id, procedures)
    return all_results


def parse_procedure_combiners(output_file):
    df = pd.read_csv("temp/ProceduresCombiner.csv", dtype=str)  # Alles als String einlesen
    df = df.fillna('')  # NaN-Werte durch leere Strings ersetzen

    # Nur aktive Einträge (Active = 1) auswählen und sortieren
    df_active = df[df["Active"] == "1"].sort_values(by=["Type", "ICAO", "Sortorder"])

    # Daten als Liste von Tupeln zurückgeben (wie fetchall())
    procedure_combiners = df_active.to_dict(orient="records")

    for procedure_combiner in procedure_combiners:
        procedure_include_regex = re.compile(procedure_combiner['Regex']) if procedure_combiner[
            'Regex'] else None
        procedure_exclude_regex = re.compile(procedure_combiner['Iregex']) if procedure_combiner[
            'Iregex'] else None

        combined_combiners: List[str] = procedure_combiner['Combine'].split(' ')
        combined_combiner_procedures: List[ResolvedProcedure] = []
        for combined_combiner in combined_combiners:
            combiner = list(combined_combiner)
            logger.debug("Resolving combiner %s", combiner)
            combiner_procedures = resolve_combiner(combiner, procedure_combiner['ICAO'],
                                                   procedure_combiner['Runway'],
                                                   procedure_combiner['Type'])
            logger.debug("Finished resolving combiner %s: %s", combiner, combiner_procedures)

            unique_combiner_procedures = remove_duplicate_procedures(combiner_procedures)
            logger.debug("%d/%d unique procedures for combiner %s: %s", len(unique_combiner_procedures),
                         len(combiner_procedures), combiner, unique_combiner_procedures)

            for procedure in unique_combiner_procedures:
                if procedure_include_regex:
                    if procedure_include_regex.search(procedure.full_id):
                        procedure.combiner = combined_combiner
                        combined_combiner_procedures.append(procedure)
                        logger.debug("Combiner %s: %s", combined_combiner, procedure)
                    else:
                        logger.info("Skipping due to include regex %s, combiner %s: %s",
                                    procedure_include_regex, combined_combiner, procedure)
                elif procedure_exclude_regex:
                    if procedure_exclude_regex.search(procedure.full_id):
                        logger.info("Skipping due to exclude regex %s, combiner %s: %s",
                                    procedure_exclude_regex,
                                    combined_combiner, procedure)
                    else:
                        procedure.combiner = combined_combiner
                        combined_combiner_procedures.append(procedure)
                        logger.debug("Combiner %s: %s", combined_combiner, procedure)

                else:
                    procedure.combiner = combined_combiner
                    combined_combiner_procedures.append(procedure)
                    logger.debug("Combiner %s: %s", combined_combiner, procedure)

        sorted_combiner_procedures = sort_procedures(combined_combiner_procedures,
                                                     procedure_combiner['Namesortorder'])

        for sorted_procedure in sorted_combiner_procedures:
            with open(output_file, 'a') as file:
                file.write(sorted_procedure.format() + '\n')


def copy_ownfolder(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            # Wenn der Zielordner existiert, rekursiv in ihn kopieren
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            #copy_folder(src_path, dst_path)  # Rekursiver Aufruf
        else:
            # Dateien kopieren
            shutil.copy2(src_path, dst_path)

def installercheck():
    config = load_config()
    try:
        ####################################
        # get the online Installer version #
        ####################################
        response = urllib.request.urlopen(URL +"installerversion.txt")
        data = response.read().decode('utf-8').splitlines()
        online_installer_version = data[0].strip()

        file_path = FIR_fullname+".exe"
        pe = pefile.PE(file_path)

        # Check if the file contains FileInfo
        if hasattr(pe, 'FileInfo'):
            for file_info in pe.FileInfo:
                # Ensure that file_info is a valid object with a Key attribute
                if hasattr(file_info, 'Key') and file_info.Key == b'StringFileInfo':
                    for st in file_info.StringTable:
                        for entry in st.entries.items():
                            # Looking for FileVersion or ProductVersion
                            if entry[0] == b'FileVersion' or entry[0] == b'ProductVersion':
                                return entry[1].decode('utf-8')

        # Fallback to VS_FIXEDFILEINFO if StringFileInfo was not found
        if hasattr(pe, 'VS_FIXEDFILEINFO'):
            fixed_file_info = pe.VS_FIXEDFILEINFO[0]
            version = f"{fixed_file_info.FileVersionMS >> 16}.{fixed_file_info.FileVersionMS & 0xFFFF}.{fixed_file_info.FileVersionLS >> 16}.{fixed_file_info.FileVersionLS & 0xFFFF}"


        if version_tuple(version) < version_tuple(online_installer_version): 
            # Erstelle ein neues Toplevel-Fenster
            custom_msg_box = tk.Toplevel()
            custom_msg_box.title(translate("update_available"))

            # Setze die Größe des Fensters
            custom_msg_box.geometry("300x100")

            # Label mit der Nachricht
            msg_label = tk.Label(custom_msg_box, text=translate("installer_version"))
            msg_label.pack(pady=10)
       
    except Exception as e:
        pass




def check_airac():
    airac = 0
    settings = fetch_settings()
    local_GlobalATC = "NavDataPro/Cycle.txt"
    local_Navigator = "Bin/cycle_info.txt"
    try:
        with open(local_GlobalATC, "r") as file:
            first_four_chars = file.read(4).strip()  # Entferne Whitespaces und Zeilenumbrüche
        # Stelle sicher, dass settings['Airac'] auch als String behandelt wird und getrimmt wird
        expected_airac = str(settings['Airac']).strip()
        if first_four_chars != expected_airac:
            airac+= 1
            messagebox.showerror("Airac", translate("airac_msg"))
    except:
        messagebox.showerror("Airac", translate("airac_Navdatapro_notfound"))
        airac += 1

    try:
        with open(local_Navigator, "r") as file:
            first_four_chars = file.read()[17:21].strip()  # Entferne Whitespaces und Zeilenumbrüche
        # Stelle sicher, dass settings['Airac'] auch als String behandelt wird und getrimmt wird
        expected_airac = str(settings['Airac']).strip()
        if first_four_chars != expected_airac:
            airac+= 1
            messagebox.showerror("Airac", translate("airac_msg"))
        else:
            print(f"Installed Airac {first_four_chars}")
        return airac
    except:
        messagebox.showerror("Airac", translate("airac_Navigator_notfound"))

def check_installed_versions():
    config = load_config()

    #####################################################
    # überprüfen welche versionen online verfügbar sind #
    #####################################################
    try:
        response = requests.get(URL +"Euroscope.zip", stream=True)
        last_modified = response.headers['Last-Modified']
        date_obj = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        formatted_date = date_obj.strftime('%Y.%m.%d.%H.%M.%S')
        online_euroscope_version = formatted_date.strip()
        print(f"online {online_euroscope_version}")
        print(f"Local {config["euroscope_version"]}")

        response = requests.get(URL +"Sectorfile.zip", stream=True)
        last_modified = response.headers['Last-Modified']
        date_obj = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        formatted_date = date_obj.strftime('%Y.%m.%d.%H.%M.%S')
        online_sectorfile_version = formatted_date.strip()
    except requests.exceptions.RequestException as e:
        messagebox.showwarning(translate("error_title"), translate("error installercheck"))

    if version_tuple(config["euroscope_version"]) < version_tuple(online_euroscope_version):
        if os.path.exists("Euroscope"):
            shutil.rmtree("Euroscope")
        installation_euroscope()

    if version_tuple(config["sectorfile_version"]) < version_tuple(online_sectorfile_version):
        if not os.path.exists("temp"):
            os.makedirs("temp")
        if os.path.exists(fr"Sectorfile\{FIR}\Plugins\Groundradar\GRpluginSettingsLocal.txt"):
            shutil.move(fr"Sectorfile\{FIR}\Plugins\Groundradar\GRpluginSettingsLocal.txt",
                        r"temp\GRpluginSettingsLocal.txt")
        if os.path.exists(fr"Sectorfile\{FIR}\Plugins\Topsky\TopSkySettingsLocal.txt"):
            shutil.move(fr"Sectorfile\{FIR}\Plugins\Topsky\TopSkySettingsLocal.txt", r"temp\TopSkySettingsLocal.txt")
        if os.path.exists(fr"Sectorfile\{FIR}\Alias\alias.txt"):
            shutil.move(fr"Sectorfile\{FIR}\Alias\alias.txt", r"temp\alias.txt")
        if os.path.exists("Sectorfile"):
            shutil.rmtree("Sectorfile")
        installation_sectorfile()



def installation_sectorfile():
    print("Start installing Sectorfile")

    config=load_config()
    config["sectorfile_version"] = "0.0.0.0.0.0"
    with open("config.json", "w") as f:
        json.dump(config, f)
    settings = fetch_settings()
    #####################################################
    # überprüfen welche versionen online verfügbar sind #
    #####################################################
    output_sctfilename = os.path.join('Sectorfile', 'temp.sct')
    output_esefilename = os.path.join('Sectorfile', 'temp.ese')
    try:
        response = requests.get(URL +"Sectorfile.zip", stream=True)
        last_modified = response.headers['Last-Modified']
        date_obj = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        formatted_date = date_obj.strftime('%Y.%m.%d.%H.%M.%S')
        online_sectorfile_version = formatted_date.strip()
    except requests.exceptions.RequestException as e:
        messagebox.showwarning(translate("error_title"), translate("error installercheck"))
    if os.path.exists("Sectorfile"):
        shutil.rmtree("Sectorfile")
    if not os.path.exists("temp"):
        os.makedirs("temp")
    if not os.path.exists("Customfiles"):
        os.makedirs("Customfiles")
    if not os.path.exists("Customfiles/EYVL"):
        os.makedirs("Customfiles/EYVL")
    if not os.path.exists("Customfiles/EYVL/Alias"):
        os.makedirs("Customfiles/EYVL/Alias")
    if not os.path.exists("Customfiles/EYVL/ASR"):
        os.makedirs("Customfiles/EYVL/ASR")
    if not os.path.exists("Customfiles/EYVL/Plugins"):
        os.makedirs("Customfiles/EYVL/Plugins")
    if not os.path.exists("Customfiles/EYVL/Settings"):
        os.makedirs("Customfiles/EYVL/Settings")
    if not os.path.exists("Customfiles/EYVL/Sounds"):
        os.makedirs("Customfiles/EYVL/Sounds")
    sectorfile_zip = os.path.join("temp", "Sectorfile.zip")
    urllib.request.urlretrieve(URL +"Sectorfile.zip", sectorfile_zip)
    with zipfile.ZipFile(sectorfile_zip, 'r') as zip_ref:
        zip_ref.extractall("Sectorfile")
    if os.path.exists(sectorfile_zip):
        os.remove(sectorfile_zip)

    # einfügen der gesicherten GRpluginSettingsLocal, TopSkySettingsLocal und alias
    if os.path.exists(r"temp\GRpluginSettingsLocal.txt"):
        shutil.move(r"temp\GRpluginSettingsLocal.txt",
                    fr"Sectorfile\{FIR}\Plugins\Groundradar\GRpluginSettingsLocal.txt")
    if os.path.exists(r"temp\TopSkySettingsLocal.txt"):
        shutil.move(r"temp\TopSkySettingsLocal.txt", fr"Sectorfile\{FIR}\Plugins\Topsky\TopSkySettingsLocal.txt")
    if os.path.exists(r"temp\alias.txt"):
        shutil.move(r"temp\alias.txt", fr"Sectorfile\{FIR}\Alias\alias.txt")
    # verschieben der eigenen Dateien
    if os.path.exists("Customfiles"):
        copy_ownfolder("Customfiles", "Sectorfile")
    if os.path.exists(r"temp\Procedure.csv"):
        os.remove(r"temp\Procedure.csv")
    if os.path.exists(r"temp\Procedures.csv"):
        os.remove(r"temp\Procedures.csv")
    if os.path.exists(r"temp\ProceduresCombiner.csv"):
        os.remove(r"temp\ProceduresCombiner.csv")
    if os.path.exists(r"temp\runway.csv"):
        os.remove(r"temp\runway.csv")
    if os.path.exists(r"temp\runways.csv"):
        os.remove(r"temp\runways.csv")
    if os.path.exists(r"temp\airport.csv"):
        os.remove(r"temp\airport.csv")
    if os.path.exists(r"temp\setting.csv"):
        os.remove(r"temp\setting.csv")
    if os.path.exists(r"temp\waypoint.csv"):
        os.remove(r"temp\waypoint.csv")

    config = load_config()
    config["sectorfile_version"] = online_sectorfile_version
    with open("config.json", "w") as f:
        json.dump(config, f)
    print("Finished Installation Sectorfile.")

def installation_euroscope():
    config=load_config()
    print("Start installing Euroscope")
    config["euroscope_version"] = "0.0.0.0.0.0"
    with open("config.json", "w") as f:
        json.dump(config, f)
    #####################################################
    # überprüfen welche versionen online verfügbar sind #
    #####################################################
    try:
        response = requests.get(URL +"Euroscope.zip", stream=True)
        last_modified = response.headers['Last-Modified']
        date_obj = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        formatted_date = date_obj.strftime('%Y.%m.%d.%H.%M.%S')
        online_euroscope_version = formatted_date.strip()
    except requests.exceptions.RequestException as e:
        messagebox.showwarning(translate("error_title"), translate("error installercheck"))
    if os.path.exists("Euroscope"):
        shutil.rmtree("Euroscope")
    if not os.path.exists("temp"):
        os.makedirs("temp")
    if not os.path.exists("Customfiles"):
        os.makedirs("Customfiles")
    if not os.path.exists("Customfiles/EYVL"):
        os.makedirs("Customfiles/EYVL")
    if not os.path.exists("Customfiles/EYVL/Alias"):
        os.makedirs("Customfiles/EYVL/Alias")
    if not os.path.exists("Customfiles/EYVL/ASR"):
        os.makedirs("Customfiles/EYVL/ASR")
    if not os.path.exists("Customfiles/EYVL/Plugins"):
        os.makedirs("Customfiles/EYVL/Plugins")
    if not os.path.exists("Customfiles/EYVL/Settings"):
        os.makedirs("Customfiles/EYVL/Settings")
    if not os.path.exists("Customfiles/EYVL/Sounds"):
        os.makedirs("Customfiles/EYVL/Sounds")
    euroscope_zip = os.path.join("temp", "Euroscope.zip")
    urllib.request.urlretrieve(URL +"Euroscope.zip", euroscope_zip)
    with zipfile.ZipFile(euroscope_zip, 'r') as zip_ref:
        zip_ref.extractall("Euroscope")
    if os.path.exists(euroscope_zip):
        os.remove(euroscope_zip)
    #check if Euroscope font is installed
    system_font_path = os.path.join("C:\\Windows\\Fonts\\EuroScope.ttf")
    if os.path.exists(system_font_path):
        print("'Euroscope' ist bereits im Systemverzeichnis installiert.")
    else:
        response = requests.get(URL +"EuroScope.ttf")
        if response.status_code == 200:
            # Sicherstellen, dass das Verzeichnis für benutzerdefinierte Schriften existiert
            os.makedirs(os.path.dirname(system_font_path), exist_ok=True)

            # Speichern der heruntergeladenen Schriftartdatei im Systemverzeichnis
            with open(system_font_path, "wb") as font_file:
                font_file.write(response.content)

            # Schriftart dem Font-Manager hinzufügen und Cache aktualisieren
            font_manager.fontManager.addfont(system_font_path)
            font_manager._rebuild()
            print("'Euroscope' wurde erfolgreich heruntergeladen und im Systemverzeichnis installiert.")
    config=load_config()
    config["euroscope_version"] = online_euroscope_version
    with open("config.json", "w") as f:
        json.dump(config, f)
    print("Finished Installation Euroscope.")

def show_restart():
    global restart_screen
    restart_screen = tk.Tk()
    restart_screen.title("Restart required")
    restart_screen.geometry("300x100")
    ttk.Label(restart_screen, text="Language is changed after Restarting the program ").pack(pady=20)



def button_fresh_install():
    if internet==1:
        setting_csv = os.path.join("temp", "setting.csv")
        urllib.request.urlretrieve(URL + "setting.csv", setting_csv)
        installation_euroscope()
        installation_sectorfile()


def button_start():
    config=load_config()
    if internet == 1:
        setting_csv = os.path.join("temp", "setting.csv")
        urllib.request.urlretrieve(URL + "setting.csv", setting_csv)
        wrongairac=check_installed_versions()
        if wrongairac=="wrongairac":
            return
    ###############################################
    # Überprüfen ob die mindestdaten gesetzt sind #
    ###############################################
    if not (config["name"] and config["vatsim_id"] and config["vatsim_password"] and config["rating"]):
        # Wenn einer der Werte nicht gesetzt ist, zeige eine Messagebox an
        messagebox.showwarning(translate("missing_data_title"), translate("missing_data"))
        return  # Beende die Funktion, wenn die Überprüfung fehlschlägt
    if os.path.exists(fr"Sectorfile\{FIR}\Plugins\Topsky\TopSkyCPDLChoppieCode.txt"):
        os.remove(fr"Sectorfile\{FIR}\Plugins\Topsky\TopSkyCPDLChoppieCode.txt")
    with open(fr"Sectorfile\{FIR}\Plugins\Topsky\TopSkyCPDLChoppieCode.txt", 'w') as file:
        file.write(config["hoppie_code"])
    if config['rating'] == "OBS":
        rating = 0
    if config['rating'] == "S1":
        rating = 1
    if config['rating'] == "S2":
        rating = 2
    if config['rating'] == "S3":
        rating = 3
    if config['rating'] == "C1":
        rating = 4
    if config['rating'] == "C3":
        rating = 6
    if config['rating'] == "I1":
        rating = 7
    if config['rating'] == "I3":
        rating = 9
    if config['rating'] == "SUP":
        rating = 10

    for root, dirs, files in os.walk("Sectorfile"):
        for file in files:
            if file.endswith(".prf"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    lines = f.readlines()
                with open(file_path, "w") as f:
                    for line in lines:
                        if not (line.startswith("LastSession	realname") or
                                line.startswith("LastSession	certificate") or
                                line.startswith("LastSession	password") or
                                line.startswith("LastSession	rating")):
                            f.write(line)
                    f.write(f"\nLastSession	realname	{config['name']}")
                    f.write(f"\nLastSession	certificate	{config['vatsim_id']}")
                    f.write(f"\nLastSession	password	{config['vatsim_password']}")
                    f.write(f"\nLastSession	rating	{rating}")


    def on_select(event=None):
        if event is not None:
            selected_file = listbox.get(listbox.curselection())
        else:
            # Wenn nur eine Datei existiert, wird der einzige Eintrag verwendet
            selected_file = prf_files[0]

        es_path = os.path.join(os.getcwd(), "Euroscope", "EuroScope.exe")
        lnk_path = os.path.join(os.getcwd(), "Euroscope", "EuroScope.lnk")

        # Verknüpfung erstellen, falls sie nicht existiert
        if not os.path.exists(lnk_path):
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(lnk_path)
            shortcut.TargetPath = es_path  # Setzt die .exe als Ziel
            shortcut.WorkingDirectory = os.path.dirname(es_path)  # Arbeitsverzeichnis setzen
            shortcut.Save()

        shortcut_path = os.path.join(os.getcwd(), "Euroscope", "EuroScope.lnk")
        command = fr'start "" "{shortcut_path}" "..\\Sectorfile\\{selected_file}.prf"'
        subprocess.Popen(command, shell=True)


        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False

        def is_process_running(exe_name):
            """Überprüft, ob der Prozess bereits läuft."""
            for process in psutil.process_iter(attrs=["name"]):
                if process.info["name"].lower() == exe_name.lower():
                    return True
            return False

        def run_as_admin(exe_path):
            exe_dir = os.path.dirname(exe_path)
            os.chdir(exe_dir)

            exe_name = os.path.basename(exe_path)
            print(exe_name)
            if is_process_running(exe_name):
                print(f"{exe_name} läuft bereits.")
                return

            if is_admin():
                # Wenn das Skript bereits als Admin ausgeführt wird
                subprocess.run([exe_path], check=True)
            else:
                # Erhöhte Rechte anfordern und das Programm mit Admin-Rechten ausführen
                try:
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, None, 1)
                except Exception as e:
                    print(translate("error_title"))

        # Pfad zur ausführbaren Datei
        if os.path.exists(config['afv_path']):
            exe_path = config["afv_path"]
            run_as_admin(exe_path)
        listbox.destroy()
        sys.exit()

    # Lade die .prf-Dateien
    prf_files = [os.path.splitext(f)[0] for f in os.listdir("Sectorfile") if f.endswith('.prf')]
    if len(prf_files) > 1:
        root = tk.Tk()
        root.title("PRF-Dateien")
        root.iconbitmap(exe_path)

        label = tk.Label(root, text=translate("Choose_a_profile"))
        label.pack(padx=10, pady=10)  # Abstand oben (10) und unten (0)
        # Erstelle eine Listbox, um die .prf-Dateien anzuzeigen
        listbox = tk.Listbox(root)
        listbox.pack(padx=10, pady=10)

        # Füge die .prf-Dateien zur Listbox hinzu
        for file in prf_files:
            listbox.insert(tk.END, file)

        # Binde die Auswahl eines Eintrags an eine Funktion
        listbox.bind("<<ListboxSelect>>", on_select)

        # Starte die Tkinter-Hauptschleife
        root.mainloop()
    else:
        on_select()


def button_setting():
    config = load_config()

    settings_window = tk.Toplevel(root)
    settings_window.title(translate("setting"))
    settings_window.iconbitmap(exe_path)

    tk.Label(settings_window, text=translate("language")).grid(row=0, column=0, padx=10, pady=10)
    selected_language_entry = tk.StringVar(settings_window)
    selected_language_entry.set(config.get("selected_language", "English"))
    selected_language_options = list(translations.keys())
    selected_language_menu = tk.OptionMenu(settings_window, selected_language_entry, *selected_language_options)
    selected_language_menu.grid(row=0, column=1, padx=10, pady=10)

    # Callback-Funktion zum Neustarten des Programms
    def on_language_change(*args):
        save_settings()
        show_restart()

    # Trace auf die Änderung von selected_language_entry setzen
    selected_language_entry.trace_add("write", on_language_change)

    tk.Label(settings_window, text=translate("name")).grid(row=1, column=0, padx=10, pady=10)
    name_entry = tk.Entry(settings_window)
    name_entry.grid(row=1, column=1, padx=10, pady=10)
    name_entry.insert(0, config["name"])

    tk.Label(settings_window, text=translate("vatsim_id")).grid(row=2, column=0, padx=10, pady=10)
    vatsim_id_entry = tk.Entry(settings_window)
    vatsim_id_entry.grid(row=2, column=1, padx=10, pady=10)
    vatsim_id_entry.insert(0, config["vatsim_id"])

    tk.Label(settings_window, text=translate("vatsim_password")).grid(row=3, column=0, padx=10, pady=10)
    vatsim_password_entry = tk.Entry(settings_window, show="*")
    vatsim_password_entry.grid(row=3, column=1, padx=10, pady=10)
    vatsim_password_entry.insert(0, config["vatsim_password"])

    tk.Label(settings_window, text=translate("rating")).grid(row=4, column=0, padx=10, pady=10)
    rating_entry = tk.StringVar(settings_window)
    rating_entry.set(config.get("rating", "S1"))
    rating_options = ["OBS", "S1", "S2", "S3", "C1", "C3", "SUP"]
    rating_menu = tk.OptionMenu(settings_window, rating_entry, *rating_options)
    rating_menu.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(settings_window, text=translate("hoppie_code")).grid(row=5, column=0, padx=10, pady=10)
    hoppie_code_entry = tk.Entry(settings_window, show="*")
    hoppie_code_entry.grid(row=5, column=1, padx=10, pady=10)
    hoppie_code_entry.insert(0, config["hoppie_code"])

    tk.Label(settings_window, text=translate("afv_path")).grid(row=6, column=0, padx=10, pady=10)
    afv_path_entry = tk.Entry(settings_window)
    afv_path_entry.grid(row=6, column=1, padx=10, pady=10)
    afv_path_entry.insert(0, config.get("afv_path", ""))

    def browse_afv_path():
        file_path = filedialog.askopenfilename(
            title="select AFV.exe",
            filetypes=[("Executable Files", "*.exe")]
        )
        if file_path:
            afv_path_entry.delete(0, tk.END)
            afv_path_entry.insert(0, file_path)
        settings_window.focus_set()

    tk.Button(settings_window, text=translate("browse"), command=browse_afv_path).grid(row=6, column=2, padx=10,
                                                                                       pady=10)

    def save_settings():
        config = load_config()
        config["name"] = name_entry.get()
        config["vatsim_id"] = vatsim_id_entry.get()
        config["vatsim_password"] = vatsim_password_entry.get()
        config["rating"] = rating_entry.get()
        config["hoppie_code"] = hoppie_code_entry.get()
        config["afv_path"] = afv_path_entry.get()
        config["selected_language"] = selected_language_entry.get()
        with open("config.json", "w") as f:
            json.dump(config, f)
        settings_window.destroy()

    tk.Button(settings_window, text=translate("save"), command=save_settings).grid(row=8, column=1, padx=10,
                                                                                   pady=10)



config = load_config()
selected_language = config["selected_language"]
if not os.path.exists("temp"):
    os.makedirs("temp")
if not os.path.exists("Customfiles"):
    os.makedirs("Customfiles")
if not os.path.exists("Customfiles/EYVL"):
    os.makedirs("Customfiles/EYVL")
if not os.path.exists("Customfiles/EYVL/Alias"):
    os.makedirs("Customfiles/EYVL/Alias")
if not os.path.exists("Customfiles/EYVL/ASR"):
    os.makedirs("Customfiles/EYVL/ASR")
if not os.path.exists("Customfiles/EYVL/Plugins"):
    os.makedirs("Customfiles/EYVL/Plugins")
if not os.path.exists("Customfiles/EYVL/Settings"):
    os.makedirs("Customfiles/EYVL/Settings")
if not os.path.exists("Customfiles/EYVL/Sounds"):
    os.makedirs("Customfiles/EYVL/Sounds")
setting_csv = os.path.join("temp", "setting.csv")
try:
    urllib.request.urlretrieve(URL + "setting.csv", setting_csv)
    settings = fetch_settings()
    own_navdata = settings['ownNavdata']
    internet = 1
except Exception as e:
    own_navdata = 0
    internet = 0


# Hauptfenster erstellen
root = tk.Tk()
root.title(FIR_fullname)
root.geometry("550x300")

# Logo in der Mitte anzeigen
logo_img = tk.PhotoImage(file=logo_path)
logo_label = tk.Label(root, image=logo_img)
logo_label.pack(pady=50)

# Buttons unten hinzufügen
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=20)

settings_button = tk.Button(button_frame, text=translate("setting"), command=button_setting)
settings_button.grid(row=0, column=0, padx=20)

install_button = tk.Button(button_frame, text=translate("custom_files"), command=custom_files)
install_button.grid(row=0, column=1, padx=20)

install_button = tk.Button(button_frame, text=translate("fresh_install"), command=button_fresh_install)
install_button.grid(row=0, column=2, padx=20)

start_button = tk.Button(button_frame, text=translate("start"), command=button_start)
start_button.grid(row=0, column=3, padx=20)



installercheck()
# Hauptfenster starten
root.iconbitmap(exe_path)
root.mainloop()
