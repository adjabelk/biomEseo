import subprocess
import time
import os
import pyautogui

# Get image file path relatively
def getPath(imfile, ipath="interface"):
    # Get the current directory of the script
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # Get the parent directory (one level up)
    project_directory = os.path.dirname(current_directory)
    # Now you can use this to construct relative paths
    image_path = os.path.join(project_directory, ipath, imfile)
    return image_path

def enroll_fingerptint():
    # Chemin vers l'exécutable Arduino IDE sur votre système
    chemin_arduino_ide = fr"{getPath('utils/Arduino IDE.exe', 'code')}" 

    # Chemin vers le fichier Arduino que vous souhaitez téléverser
    chemin_fichier_arduino = fr"{getPath('code_enregistrement.ino', 'code')}"

    # Nom de la carte Arduino
    nom_carte_arduino = "arduino:avr:uno"

    # Port de la carte Arduino
    port_arduino = "COM3"

    try:
        # Lancer Arduino IDE et ouvrir le fichier
        arduino_command = f'start "" "{chemin_arduino_ide}" "{chemin_fichier_arduino}"'
        arduino_process = subprocess.Popen(arduino_command, shell=True)

        # Attendre quelques secondes
        time.sleep(15)

        # Utiliser pyautogui pour simuler l'action de téléversement
        pyautogui.hotkey("Ctrl", "U")

        # Attendre quelques secondes après le téléversement
        time.sleep(10)

        # Utiliser pyautogui pour simuler l'action d'ouvrir le moniteur série
        pyautogui.hotkey("Ctrl", "Shift", "M")
        print("serial monitor")

        # Attendre quelques secondes
        time.sleep(5)

    except KeyboardInterrupt:
        # Terminer le processus Arduino IDE si l'utilisateur interrompt le script
        if arduino_process:
            arduino_process.terminate()
            arduino_process.wait()

