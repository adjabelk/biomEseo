#include <DFRobot_ID809.h>

#define COLLECT_NUMBER 3  // Nombre de fois pour la collecte d'empreintes, peut être réglé de 2 à 3

/* Utiliser le logiciel de série lors de l'utilisation d'UNO ou NANO */
#if ((defined ARDUINO_AVR_UNO) || (defined ARDUINO_AVR_NANO))
    #include <SoftwareSerial.h>
    SoftwareSerial Serial1(2, 3);  // RX, TX
    #define FPSerial Serial1
#else
    #define FPSerial Serial1
#endif

DFRobot_ID809 fingerprint;

void setup() {
  /* Initialiser le port série pour l'affichage */
  Serial.begin(9600);
  /* Initialiser FPSerial */
  FPSerial.begin(115200);
  /* Utiliser FPSerial comme port de communication du module */
  fingerprint.begin(FPSerial);
  /* Attendre l'ouverture du port série */
  while (!Serial);
  /* Tester si le dispositif peut communiquer correctement avec la carte principale
     Retourne true ou false
  */
  while (fingerprint.isConnected() == false) {
    Serial.println("La communication avec le module a échoué, veuillez vérifier la connexion");
    /* Obtenir les informations de code d'erreur */
    //desc = fingerprint.getErrorDescription();
    //Serial.println(desc);
    delay(1000);
  }
}

uint8_t ID, i, ret;

void loop() {
  /* Obtenir un ID non enregistré pour enregistrer l'empreinte digitale
     Retourne l'ID en cas de réussite
     Retourne ERR_ID809 en cas d'échec
  */
  if ((ID = fingerprint.getEmptyID()) == ERR_ID809) {
    while (1) {
      /* Obtenir les informations de code d'erreur */
      //desc = fingerprint.getErrorDescription();
      //Serial.println(desc);
      delay(1000);
    }
  }
  Serial.print("ID non enregistré, ID=");
  Serial.println(ID);
  i = 0;   // Réinitialiser le nombre de collectes
  /* Collecter l'empreinte digitale 3 fois */
  while (i < COLLECT_NUMBER) {
    /* Définir le mode, la couleur et le nombre de clignotements de la LED de l'empreinte digitale
       Peut être défini comme suit :
       Paramètre 1 : <LEDMode>
       eBreathing   eFastBlink   eKeepsOn    eNormalClose
       eFadeIn      eFadeOut     eSlowBlink
       Paramètre 2 : <LEDColor>
       eLEDGreen  eLEDRed      eLEDYellow   eLEDBlue
       eLEDCyan   eLEDMagenta  eLEDWhite
       Paramètre 3 : <Nombre de clignotements> 0 représente un clignotement continu
       Ce paramètre ne sera valide que dans les modes eBreathing, eFastBlink, eSlowBlink
    */
    fingerprint.ctrlLED(/*LEDMode = */fingerprint.eBreathing, /*LEDColor = */fingerprint.eLEDBlue, /*blinkCount = */0);
    Serial.print("La collecte de l'empreinte digitale ");
    Serial.print(i + 1);
    Serial.println("(ème) est en cours");
    Serial.println("Veuillez appuyer sur votre doigt");
    /* Capturer l'image de l'empreinte digitale, délai d'inactivité de 10 secondes, si timeout = 0, désactiver la fonction de délai de collecte
       SI réussi, retourne 0, sinon retourne ERR_ID809
    */
    if ((fingerprint.collectionFingerprint(/*timeout = */10)) != ERR_ID809) {
      /* Définir la LED de l'empreinte digitale en clignotement rapide en jaune 3 fois */
      fingerprint.ctrlLED(/*LEDMode = */fingerprint.eFastBlink, /*LEDColor = */fingerprint.eLEDYellow, /*blinkCount = */3);
      Serial.println("La collecte a réussi");
      i++;   // Incrémenter le nombre de collectes
    } else {
      Serial.println("La collecte a échoué");
      /* Obtenir les informations de code d'erreur */
      //desc = fingerprint.getErrorDescription();
      //Serial.println(desc);
    }
    Serial.println("Veuillez relâcher votre doigt");
    /* Attendre que le doigt soit relâché
       Retourne 1 lorsque le doigt est détecté, sinon retourne 0
    */
    while (fingerprint.detectFinger());
  }

  /* Enregistrer l'empreinte digitale dans un ID non enregistré */
  if (fingerprint.storeFingerprint(/*ID non enregistré = */ID) != ERR_ID809) {
    Serial.print("Enregistrement réussi, ID=");
    Serial.println(ID);
    Serial.println("-----------------------------");
    /* Définir la LED de l'empreinte digitale en mode toujours allumé en vert */
    fingerprint.ctrlLED(/*LEDMode = */fingerprint.eKeepsOn, /*LEDColor = */fingerprint.eLEDGreen, /*blinkCount = */0);
    delay(1000);
    /* Éteindre la LED de l'empreinte digitale */
    fingerprint.ctrlLED(/*LEDMode = */fingerprint.eNormalClose, /*LEDColor = */fingerprint.eLEDBlue, /*blinkCount = */0);
    delay(1000);
  } else {
    Serial.println("L'enregistrement a échoué");
    /* Obtenir les informations de code d'erreur */
    //desc = fingerprint.getErrorDescription();
    //Serial.println(desc);
  }
}
