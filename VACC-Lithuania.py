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
import webbrowser
import pandas as pd
import psutil
from bs4 import BeautifulSoup

URL = "https://vacc-lithuania.lima-city.at/Installer/"
FIR = "EYVL"
Packagename = "Installer"
Testing = False  # Change the base path to Meipass for exe file



FIR_fullname = os.path.basename(__file__).split(".")[0]

if Testing == True:
    logo_path = 'Logo.png'
    exe_path = FIR_fullname + ".py"
    proc_path = 'procedure_generation.py'
else:
    base_path = sys._MEIPASS
    logo_path = os.path.join(base_path, 'Logo.png')
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
        "sectorfile_version": "ACHTUNG!\n\nAufgrund von Änderungen beim Navdata-Anbieter müssen Sie die Sektor-Datei manuell herunterladen. Wenn diese Nachricht geschlossen wird, öffnet Ihr Webbrowser die entsprechende AeroNav GNG-Seite.\nBitte melden Sie sich mit Ihren Navigraph- und VATSIM-Konten an, laden Sie die Datei herunter und extrahieren Sie deren Inhalt in den ebenfalls geöffneten Ordner.\nAnschließend können Sie im Hauptfenster erneut auf Starten drücken.",
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
        "sectorfile_version": "LET OP!\n\nVanwege wijzigingen bij de navdata-provider moet u het sectorbestand handmatig downloaden. Wanneer dit bericht wordt gesloten, opent uw webbrowser de relevante AeroNav GNG-pagina.\nLog in met uw Navigraph- en VATSIM-accounts, download het bestand en pak de inhoud uit in de map die ook geopend zal worden.\nVervolgens kunt u opnieuw op Starten drukken in het hoofdvenster.",
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
        "sectorfile_version": "ATTENTION!\n\nDue to navdata provider changes, you must manually download the sectorfile. When this message is closed, your web browser will open the relevant AeroNav GNG page.\nPlease log in with your Navigraph and VATSIM accounts, download the file and extract its contents in the folder that will also be opened.\nYou may then press Start in the main window again.",
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
        "sectorfile_version": "ATTENTION!\n\nEn raison de changements du fournisseur de navdata, vous devez télécharger manuellement le fichier de secteur. Lorsque ce message sera fermé, votre navigateur web ouvrira la page AeroNav GNG correspondante.\nVeuillez vous connecter avec vos comptes Navigraph et VATSIM, télécharger le fichier et extraire son contenu dans le dossier qui sera également ouvert.\nVous pourrez ensuite appuyer à nouveau sur Démarrer dans la fenêtre principale.",
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
        "sectorfile_version": "ATTENZIONE!\n\nA causa di modifiche al fornitore dei dati di navigazione, è necessario scaricare manualmente il file del settore. Quando questo messaggio sarà chiuso, il tuo browser web aprirà la pagina AeroNav GNG pertinente.\nAccedi con i tuoi account Navigraph e VATSIM, scarica il file ed estrai il suo contenuto nella cartella che verrà anch'essa aperta.\nPoi, puoi premere nuovamente Start nella finestra principale.",
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
        "sectorfile_version": "Dėmesio!\n\nDėl navigacinių duomenų tiekėjo pasiketimo, sektoriaus failas privalo būti atnaujintas rankiniu būdu. Kai ši žinutė bus uždaryta, jūsų naršyklėje bus atvertas atitinkamas AeroNav GNG puslapis.\nPrašome prisijungti su savo Navigraph ir VATSIM paskyromis, parsisiūsti failą ir išarchyvuoti jo turinį į aplanką kuris taip pat bus atvertas.\nTada galite dar kartą paspausti Pradėti pagrindiniame lange.",
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
        "sectorfile_version": "POZOR!\n\nVzhľadom na zmeny u poskytovateľa navdata musíte sektorový súbor stiahnuť manuálne. Po zatvorení tejto správy sa vo vašom webovom prehliadači otvorí príslušná stránka AeroNav GNG.\nPrihláste sa pomocou svojich účtov Navigraph a VATSIM, stiahnite súbor a rozbaľte jeho obsah do priečinka, ktorý sa taktiež otvorí.\nNásledne môžete opäť stlačiť tlačidlo Start v hlavnom okne.",
    }
}

def translate(key):
    return translations[selected_language].get(key, key)


# Funktion zum Laden der Konfiguration
def load_config():
    if os.path.exists("temp/config.json"):
        with open("temp/config.json", "r") as f:
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
            "selected_language": "English"
        }


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


def version_tuple(version):
    return tuple(map(int, (version.split("."))))

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
            # copy_folder(src_path, dst_path)  # Rekursiver Aufruf
        else:
            # Dateien kopieren
            shutil.copy2(src_path, dst_path)


def installercheck():
    config = load_config()
    try:
        ####################################
        # get the online Installer version #
        ####################################
        response = urllib.request.urlopen(URL + "installerversion.txt")
        data = response.read().decode('utf-8').splitlines()
        online_installer_version = data[0].strip()

        file_path = FIR_fullname + ".exe"
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

def check_installed_versions():
    config = load_config()

    #####################################################
    # überprüfen welche versionen online verfügbar sind #
    #####################################################
    try:
        response = requests.get(URL + "Euroscope.zip", stream=True)
        last_modified = response.headers['Last-Modified']
        date_obj = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        formatted_date = date_obj.strftime('%Y.%m.%d.%H.%M.%S')
        online_euroscope_version = formatted_date.strip()
        print(f"online {online_euroscope_version}")
        print(f"Local {config["euroscope_version"]}")

        url = "https://files.aero-nav.com/" + FIR
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="table table-striped table-hover table-bordered")



        for row in table.find_all("tr")[1:]:  # Header überspringen
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if not cols:
                continue
            if Packagename in cols[1]:
                airac = cols[2]
                version = cols[3]
                version = version.zfill(4)
                online_airac = airac.translate(str.maketrans("", "", " /"))+"-"+version
                print(f"online Sectorfile " + online_airac)
                break

    except requests.exceptions.RequestException as e:
        messagebox.showwarning(translate("error_title"), translate("error installercheck"))

    if version_tuple(config["euroscope_version"]) < version_tuple(online_euroscope_version):
        if os.path.exists("Euroscope"):
            shutil.rmtree("Euroscope")
        installation_euroscope()

    candidates = []

    # Alle Dateien im Ordner durchgehen
    if os.path.exists("Sectorfile"):
        for filename in os.listdir("Sectorfile"):
            if filename.endswith(".ese"):
                basename = os.path.splitext(filename)[0]
                last11 = basename[-11:]
                candidates.append(last11)

        if candidates:
            # höchste "Nummer" wählen
            installed_airac = max(candidates)
        else:
            installed_airac = "000000-0000"
    else:
        installed_airac = "000000-0000"
    print(f"installed Sectorfile " + installed_airac)

    if installed_airac < online_airac:
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


def installation_sectorfile():
    print("Start installing Sectorfile")
    if os.path.exists("Sectorfile"):
        shutil.rmtree("Sectorfile")
    if not os.path.exists("temp"):
        os.makedirs("temp")
    if not os.path.exists("Customfiles"):
        os.makedirs("Customfiles")
    if not os.path.exists(fr"Customfiles/{FIR}"):
        os.makedirs(fr"Customfiles/{FIR}")
    if not os.path.exists(fr"Customfiles/{FIR}/Alias"):
        os.makedirs(fr"Customfiles/{FIR}/Alias")
    if not os.path.exists(fr"Customfiles/{FIR}/ASR"):
        os.makedirs(fr"Customfiles/{FIR}/ASR")
    if not os.path.exists(fr"Customfiles/{FIR}/Plugins"):
        os.makedirs(fr"Customfiles/{FIR}/Plugins")
    if not os.path.exists(fr"Customfiles/{FIR}/Settings"):
        os.makedirs(fr"Customfiles/{FIR}/Settings")
    if not os.path.exists(fr"Customfiles/{FIR}/Sounds"):
        os.makedirs(fr"Customfiles/{FIR}/Sounds")
    if not os.path.exists("Sectorfile"):
        os.makedirs("Sectorfile")
    messagebox.showinfo("Hinweis", translate("sectorfile_version"))
    webbrowser.open(fr"https://files.aero-nav.com/{FIR}")
    if os.path.exists("Sectorfile") and os.path.isdir("Sectorfile"):
        # Ordner im Windows Explorer öffnen
        subprocess.run(['explorer', "Sectorfile"])
    else:
        print(f"Der Ordner Sectorfile existiert nicht.")
    print("Finished Installation Sectorfile.")


def installation_euroscope():
    config = load_config()
    print("Start installing Euroscope")
    config["euroscope_version"] = "0.0.0.0.0.0"
    with open("temp/config.json", "w") as f:
        json.dump(config, f)
    #####################################################
    # überprüfen welche versionen online verfügbar sind #
    #####################################################
    try:
        response = requests.get(URL + "Euroscope.zip", stream=True)
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
    if not os.path.exists(fr"Customfiles/{FIR}"):
        os.makedirs(fr"Customfiles/{FIR}")
    if not os.path.exists(fr"Customfiles/{FIR}/Alias"):
        os.makedirs(fr"Customfiles/{FIR}/Alias")
    if not os.path.exists(fr"Customfiles/{FIR}/ASR"):
        os.makedirs(fr"Customfiles/{FIR}/ASR")
    if not os.path.exists(fr"Customfiles/{FIR}/Plugins"):
        os.makedirs(fr"Customfiles/{FIR}/Plugins")
    if not os.path.exists(fr"Customfiles/{FIR}/Settings"):
        os.makedirs(fr"Customfiles/{FIR}/Settings")
    if not os.path.exists(fr"Customfiles/{FIR}/Sounds"):
        os.makedirs(fr"Customfiles/{FIR}/Sounds")
    euroscope_zip = os.path.join("temp", "Euroscope.zip")
    urllib.request.urlretrieve(URL + "Euroscope.zip", euroscope_zip)
    with zipfile.ZipFile(euroscope_zip, 'r') as zip_ref:
        zip_ref.extractall("Euroscope")
    if os.path.exists(euroscope_zip):
        os.remove(euroscope_zip)
    # check if Euroscope font is installed
    system_font_path = os.path.join("C:\\Windows\\Fonts\\EuroScope.ttf")
    if os.path.exists(system_font_path):
        print("'Euroscope' ist bereits im Systemverzeichnis installiert.")
    else:
        response = requests.get(URL + "EuroScope.ttf")
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
    config = load_config()
    config["euroscope_version"] = online_euroscope_version
    with open("temp/config.json", "w") as f:
        json.dump(config, f)
    print("Finished Installation Euroscope.")


def show_restart():
    global restart_screen
    restart_screen = tk.Tk()
    restart_screen.title("Restart required")
    restart_screen.geometry("300x100")
    ttk.Label(restart_screen, text="Language is changed after Restarting the program ").pack(pady=20)


def button_fresh_install():
    if internet == 1:
        installation_euroscope()
        installation_sectorfile()


def button_start():
    config = load_config()
    check_installed_versions()
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
        with open("temp/config.json", "w") as f:
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
if not os.path.exists("Customfiles/" + FIR):
    os.makedirs("Customfiles/" + FIR)
if not os.path.exists("Customfiles/" + FIR + "/Alias"):
    os.makedirs("Customfiles/" + FIR + "/Alias")
if not os.path.exists("Customfiles/" + FIR + "/ASR"):
    os.makedirs("Customfiles/" + FIR + "/ASR")
if not os.path.exists("Customfiles/" + FIR + "/Plugins"):
    os.makedirs("Customfiles/" + FIR + "/Plugins")
if not os.path.exists("Customfiles/" + FIR + "/Settings"):
    os.makedirs("Customfiles/" + FIR + "/Settings")
if not os.path.exists("Customfiles/" + FIR + "/Sounds"):
    os.makedirs("Customfiles/" + FIR + "/Sounds")

def check_internet(url="https://www.google.com", timeout=3):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

if check_internet():
    internet=1
else:
    internet=0


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

