#!/usr/bin/env python2
#
##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# NZBGet to Wizznab Script
#
# Dieses Script uploaded heruntergeladene NZB Files auf Wizznab
#
# NOTE: Dieses Script benoetigt python 2.7 und python-requests.
#
# NOTE: Hier ist die Neuste Skript Versionen zu finden: https://github.com/cytec/nzbget-scripts/tree/master/PostProcessing .
#
# NOTE: Version: 4.6.

##############################################################################
### OPTIONS                                                                ###

## NZB Dir

# NZB Ordner.
#
# Bitte angaben ohne "".
# NZB Ordner von NZBget (Endung muss auf .queued enden).
#NZB_DIR=/volume1/01_NZBget/NzbDir

## API KEY

# API KEY.
#
# Bitte angaben ohne "".
# Api Key von Wizznab.
#APIKEY=APIKEY

## UPLOAD URL

# UPLOAD URL.
#
# Bitte angaben ohne "".
# Upload Url von Wizznab.
#UPLOAD_URL=UPLOAD URL

## Web Interface Pass

# WEB INTERFACE PWs (ENABLED, DISABLED).
#
# Aktivierung oder Deaktivierung fuer das WEB INTERFACE um PWs auslesen zu koennen.
#
# [Bei ENABLED]: Werden die NZBs mit dem Passwort vom WEB INTERFACE bestueckt und hochgeladen.
# [Bei DISABLED]: Werden die NZBs unveraendert hochgeladen.
#PASSWORD=DISABLED

## PasswortListe

# PasswortListe !!!!BETA!!!(ENABLED, DISABLED).
#
# Aktivierung oder Deaktivierung fuer die PasswortListe um PWs auslesen zu koennen.
#
# [Bei ENABLED]: Werden die NZBs mit dem Passwort von der PasswortListe bestueckt und hochgeladen.
# [Bei DISABLED]: Werden die NZBs unveraendert hochgeladen.
#PASSWORD_LISTE=DISABLED

## Logger zum erstellen von Logs (NUR FUER DAS PASSWORT)

# Logs Erstellen (ENABLED, DISABLED).
#
# Aktivierung oder Deaktivierung fuer das erstellen von Logs.
#
# [Bei ENABLED]: Wird das Passwort falls gewuenscht in eine Externe Datei gesichert.
# [Bei DISABLED]: Wird das Passwort nicht in eine Externe Datei gesichert.
#LOG_PW=DISABLED

## Pfad fuer das Log

# Logs Speichern.
#
# Bitte angaben ohne "".
# Hier Koennt ihr wenn gewuenscht den Pfad eintragen worin das Log gespeichert werden sollte.
# Es Handelt sich dabei NUR um das Passowrt was fuer das UNRAR verwendet wurde.
#
# [HINWEIS] Der Pafd muss nur angegeben werden wenn ihr das Passwort auch sichern wollt!! ( Also wenn LOG_PW Aktiviert wurde ).
#LOG_PATH=/volume1/test/passwort.txt

## loeschen der NZB Dateien

# NZB Dateien Loeschen (ENABLED, DISABLED).
#
# Aktivierung oder Deaktivierung fuer das loeschen der NZB Dateien in dem Ordner NZB_DIR_NEW.
#
# [Bei ENABLED]: Werden die NZB Dateien in dem Ordner NZB_DIR_NEW geloescht.
# [Bei DISABLED]: Werden die NZB Dateien in dem Ordner NZB_DIR_NEW gespeichert.
#DELETE_NZB=DISABLED

## NZB DIR NEW

# NZB DIR NEW.
#
# Bitte angaben ohne "".
# Hier wird der neue Pfad eingetragen fuer die NZBs.
# NZBs werden Dort auch gesichert.
# Bitte wie im Beispiel oben angeben.
#NZB_DIR_NEW=/volume1/NZBget/new

## .nzb ordner durchsuchen

# Ordner Suche (ENABLED, DISABLED).
# Aktivierung oder Deaktivierung fuer die nzb suche in "Ordnern".
#
# Bitte Angaben ohne "".
# Hier koennt ihr Ordner angeben die auf nzbs ueberprueft werden sollten.
# Ich habe 5 Ordner mit eingepflegt ich denke das sollte fuer nzb datein reichen.
# Je "ordner" nur eine angabe das ist wichtig!!.
# Bitte wie im Beispiel unten angeben.
#
# [HINWEIS] Die "NZB_ORDNER1-5" die ihr nicht benoetigt koennt ihr leer lassen!.
#NZB_ORDNER_SUCHE=DISABLED
#NZB_ORDNER1=music
#NZB_ORDNER2=movie
#NZB_ORDNER3=tv
#NZB_ORDNER4=
#NZB_ORDNER5=

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################

import sys
import os
import gzip
import requests
import re
import datetime
from xmlrpclib import ServerProxy

# Exit codes used by NZBGet
POSTPROCESS_SUCCESS=93
POSTPROCESS_ERROR=94
POSTPROCESS_NONE=95

# Ueberpruefung ob ausgefuehr von NZBGet
if not os.environ.has_key('NZBOP_SCRIPTDIR'):
    print "[ERROR] Dieses Skript kann nur von NZBGet (13.0 oder neuer) ausgefuehrt werden."
    sys.exit(POSTPROCESS_ERROR)

# Ueberpruefung ob NZBGet version >_ 13
if os.environ['NZBOP_VERSION'][0:5] < '13.0':
    print "[ERROR] NZBGet Version %s wird nicht unterstuetzt. Bitte NZBGet updaten." % (str(os.environ['NZBOP_VERSION']))
    sys.exit(POSTPROCESS_ERROR)

# Ueberpruefung ob Passworliste Aktiv wenn ja NZBGet version muss >_ 15.0 sein
if os.environ.get('NZBPO_PASSWORD_LISTE') == "ENABLED" and os.environ['NZBOP_VERSION'][0:5] < '15.0':
	print "[ERROR] NZBGet Version %s wird nicht unterstuetzt. Bitte NZBGet updaten." % (str(os.environ['NZBOP_VERSION']))
	sys.exit(POSTPROCESS_ERROR)

print "[INFO] Skript wird von NZBGet Version [%s] ausgefuehrt." % (str(os.environ['NZBOP_VERSION']))

# Ueberpruefung ob Totalstatus vorhanden!
if not 'NZBPP_TOTALSTATUS' in os.environ:
	print "[ERROR] *** NZBGet post-processing script ***"
	print "[ERROR] Das Skript wird nicht gestartet da Status: [%s]." % os.environ.get('NZBPP_TOTALSTATUS')
	sys.exit(POSTPROCESS_ERROR)

# Ueberpruefung ob Totalstatus Erfolgreich war!
if os.environ.has_key('NZBPP_TOTALSTATUS'):
    if not os.environ.get('NZBPP_TOTALSTATUS') == 'SUCCESS':
        print "[ERROR] Skript Abbruch wegen: [Total Status] [%s]." % os.environ.get('NZBPP_TOTALSTATUS')
        sys.exit(POSTPROCESS_ERROR)

# Ueberpruefung des ScriptStatus
#if os.environ.has_key('NZBPP_SCRIPTSTATUS'):
#    if not os.environ.get('NZBPP_SCRIPTSTATUS') == 'SUCCESS' or os.environ.get('NZBPP_SCRIPTSTATUS') == 'NONE':
#        print "[ERROR] Skript Abbruch wegen: [Script Status] [%s]." % os.environ.get('NZBPP_SCRIPTSTATUS')
#        sys.exit(POSTPROCESS_ERROR)

print "[INFO] Script nzbget2wizznab erfolgreich gestartet"

# uploads releases nach wizznab
def upload_release(releasename, filepath):
	''' upload des releases '''
	UPLOAD_URL = os.environ.get('NZBPO_UPLOAD_URL')
	APIKEY = os.environ.get('NZBPO_APIKEY')

	if not UPLOAD_URL:
		print "[ERROR] Bitte Upload URL angeben: [%s]." % (os.environ.get('NZBPO_UPLOAD_URL'))
		sys.exit(POSTPROCESS_ERROR)

	if not APIKEY:
		print "[ERROR] Bitte ApiKey angeben: [%s]." % (os.environ.get('NZBPO_APIKEY'))
		sys.exit(POSTPROCESS_ERROR)

	if releasename.endswith('.queued'):
		releasename=releasename.replace('.queued', '')

	f = open(filepath)
	file_content = f.read()
	f.close()

	print "[INFO] uploading file [%s]..." % (filepath)
	post_data = {
		"apikey": APIKEY,
	}
	myfile = {"Filedata": (releasename, file_content)}

	print requests.post(UPLOAD_URL, data=post_data, files=myfile).text.decode("utf8")

# loeschen der NZB Datein nur im Ordner "NZB_DIR_NEW"
def cleanup_nzb(releasepath, releasename):
	''' cleanup NZB files '''
	if os.environ.get('NZBPO_DELETE_NZB') == "ENABLED":
		print "[INFO] NZB Dateien loeschen aktiviert"
		releasepath_nzb = "%s/%s" % (releasepath, releasename)

		if os.path.isfile(releasepath_nzb):
			print "[INFO] NZB Datei gefunden und wird geloescht"
			try:
				os.remove(releasepath_nzb)
				print "[INFO] NZB Datei erfolgreich geloescht"
			except OSError, e:
				print "[ERROR] Failed: [%s - %s]." % (e.filename,e.strerror)
				sys.exit(POSTPROCESS_ERROR)

		elif not os.path.isfile(releasepath_nzb):
			print "[INFO] Keine NZB Datei gefunden zum loeschen: [%s]...." % (releasepath_nzb)
			sys.exit(POSTPROCESS_ERROR)

		else:
			print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich NZB Datei Loeschen....."
			sys.exit(POSTPROCESS_ERROR)

	elif os.environ.get('NZBPO_DELETE_NZB') == "DISABLED":
		print "[INFO] NZB Dateien loeschen deaktiviert"

	else:
		print "[ERROR] Fehler bei der Ausfuehrung im bezug aufs loeschen...."
		sys.exit(POSTPROCESS_ERROR)

# upload ablauf fuer neue abfolge!!
def auto_release(RELEASENAME_PASSWORD, releasename, filepath, releasepath):
	# Ueberpruefung ob Passwort in File Name vorhanden ist.... ( hier ist es vorhanden )
	if RELEASENAME_PASSWORD in releasename:
		print "[INFO] Passwort von Web Ui: [%s] ist im NZB Namen erhalten keine erweiterte Umbenennung noetig...." % (os.environ.get('NZBPR_*Unpack:Password'))

		upload_release(releasename, filepath)
		cleanup_nzb(releasepath, releasename)
		sys.exit(POSTPROCESS_SUCCESS)

	# Ueberpruefung ob Passwort in File Name vorhanden ist.... ( hier ist es nicht vorhanden )
	elif not RELEASENAME_PASSWORD in releasename:
		print "[INFO] Passwort von Web Interface: [%s] stimmt nicht mit dem Passwort im NZB Namen ueberein: [%s] erweiterte Umbenennung wird eingeleitet...." % (PASSWORD_WEB_UI, releasename)

		# Hier wird nach vorhandenen passwoertern gesucht ( Hier ist eines vorhanden )
		if (('{{' in releasename) and ('}}' in releasename)):
			print "[INFO] Passwort im NZB Namen gefunden Entfernung und Umbenennung wird eingeleitet..."

			if not os.environ.get('NZBPO_NZB_DIR_NEW'):
				print "[ERROR] Bitte den Pfad ueberpruefen worin die umbenannten NZBs gesichert werden sollten: [%s]" % (os.environ.get('NZBPO_NZB_DIR_NEW'))
				sys.exit(POSTPROCESS_ERROR)

			altes_passwort = re.match( r'^.*?\{\{[ ]?(.*?)[ ]?\}\}', releasename)
			passwort_alt = "{{%s}}" % (altes_passwort.group(1))
			ohne_passwort_zwi = releasename.replace(passwort_alt, "").rstrip()
			ohne_passwort = ohne_passwort_zwi.replace(".nzb.queued", "")
			nzb_dir_alt = os.environ.get('NZBPO_NZB_DIR')
			releasename_old = releasename
			releasename = "%s {{%s}}.nzb" % (ohne_passwort, PASSWORD_WEB_UI.rstrip())
			filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
			releasepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'))
			print "[INFO] NZB File wird umbenannt in [ %s ]" % (releasename)
			os.rename(os.path.join(nzb_dir_alt, releasename_old), filepath)

			upload_release(releasename, filepath)
			cleanup_nzb(releasepath, releasename)
			sys.exit(POSTPROCESS_SUCCESS)

			# Hier wird nach vorhandenen passwoertern gesucht ( Hier ist keines vorhanden )
		elif not (('{{' in releasename) and ('}}' in releasename)):
			print "[INFO] Kein Passwort im NZB Namen gefunden Umbenennung wird eingeleitet!!"
			releasename_old = releasename
			releasename = "%s {{%s}}.nzb" % (NZB_NAME, PASSWORD_WEB_UI.rstrip())
			filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
			releasepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'))
			print "[INFO] NZB Datei wird umbenannt in: [ %s ]." % (releasename)
			nzb_dir_alt = os.environ.get('NZBPO_NZB_DIR')
			os.rename(os.path.join(nzb_dir_alt, releasename_old), filepath)

			upload_release(releasename, filepath)
			cleanup_nzb(releasepath, releasename)
			sys.exit(POSTPROCESS_SUCCESS)

		else:
			print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... '{{' - '}}'"
			sys.exit(POSTPROCESS_ERROR)

	else:
		print "[ERROR] Fehler bei der Namens Ueberpruefung....!!"
		sys.exit(POSTPROCESS_ERROR)

def log_password():
	# Ob das Passwort von dem Log gespeichert werden soll oder nicht
	if os.environ.get('NZBPO_LOG_PW') == "ENABLED":
		print "[INFO] Die Speicherung des Passwortes wird nun eingeleitet"

		if not os.environ.get('NZBPO_LOG_PATH'):
			print "[ERROR] Fehler bei der Eingabe des LOG_PATH.. Bitte Ueberpruefen!"
			sys.exit(POSTPROCESS_ERROR)

		with open(os.environ['NZBPO_LOG_PATH'], "w") as SAVE_PASSWORD:
			SAVE_PASSWORD.write(PASSWORD_FILE)
			SAVE_PASSWORD.close()
			sys.exit(POSTPROCESS_SUCCESS)

	elif os.environ.get('NZBPO_LOG_PW') == "DISABLED":
		print "[INFO] Die Speicherung des Passwortes ist deaktiviert"
		sys.exit(POSTPROCESS_SUCCESS)

	else:
		print "[ERROR] Fehler bei der Speicherung des Passwortes...!!"
		sys.exit(POSTPROCESS_ERROR)

# Uberpruefung ob Passwort Korrekt im NZB Namen = verglichen mit NZBGet Passwort
if os.environ.get('NZBPO_PASSWORD') == "ENABLED" and ('NZBPR_*Unpack:Password' in os.environ):

	if not os.environ.get('NZBPO_PASSWORD'):
		print "[ERROR] Passwort angabe von Enabled und Disabled falsch gegeben!: [%s]." % (os.environ.get('NZBPO_PASSWORD'))
		sys.exit(POSTPROCESS_ERROR)

	if not os.environ.get('NZBPR_*Unpack:Password'):
		print "[ERROR] Kein Passwort in Web Interface gefunden oder kann nicht verwendet werden!: [%s]" % (os.environ.get('NZBPR_*Unpack:Password'))

	if not os.environ.get('NZBPO_NZB_DIR_NEW'):
		print "[ERROR] Bitte angabe Ueberpruefen zu NZB Dir!: [%s]" % (os.environ.get('NZBPO_NZB_DIR_NEW'))
		sys.exit(POSTPROCESS_ERROR)

	if not os.path.isdir(os.environ.get('NZBPO_NZB_DIR_NEW')):
		print "[ERROR] Der Pfad von [%s] ist nicht vorhanden. Bitte kontrollieren!..." % (os.environ.get('NZBPO_NZB_DIR'))
		sys.exit(POSTPROCESS_ERROR)

	print "[INFO] Passwort suche ist aktiviert, Passwort wurde in der Web Ui gefunden und wird verwendet: [%s]...." % (os.environ.get('NZBPR_*Unpack:Password'))

	PASSWORD_WEB_UI = os.environ.get('NZBPR_*Unpack:Password')
	NZB_NAME = os.environ.get('NZBPP_NZBNAME')
	RELEASENAME_PASSWORD = "{{%s}}" % (PASSWORD_WEB_UI)
	releasepath = os.environ.get('NZBPO_NZB_DIR')

	if not releasepath:
		print "[ERROR] Bitte NzbDir von NZBGet angeben: [%s]." % (os.environ.get('NZBPO_NZB_DIR'))
		sys.exit(POSTPROCESS_ERROR)

	# Ordner suche Aktvi oder Deaktiv fuer die nzb suche in verschiedenen unterordnern
	if os.environ.get('NZBPO_NZB_ORDNER_SUCHE') == "ENABLED":
		print "[INFO] NZB Ordner Suche ist Aktiviert"

		# Hier wird das Verzeichnis aufgelistet mit den vorhandenen NZBs
		list_dir_nzb = os.listdir(releasepath)
		list_ordner_nzb = next(os.walk(releasepath))[1]
		ordner_name1 = os.environ.get('NZBPO_NZB_ORDNER1')
		ordner_name2 = os.environ.get('NZBPO_NZB_ORDNER2')
		ordner_name3 = os.environ.get('NZBPO_NZB_ORDNER3')
		ordner_name4 = os.environ.get('NZBPO_NZB_ORDNER4')
		ordner_name5 = os.environ.get('NZBPO_NZB_ORDNER5')

		for ordner in ordner_name1, ordner_name2, ordner_name3, ordner_name4, ordner_name5:
			if ordner in list_ordner_nzb:
				ordner_path = os.path.join(releasepath, ordner)
				ordner_list = os.listdir(ordner_path)
				for release_name in ordner_list:
					for releasename in list_dir_nzb:
						# Hier wird der Nzb Name mit dem Verzeichnis abgeglichen
						if NZB_NAME in releasename:
							filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR'), releasename)

							# Upload ablauf
							auto_release(RELEASENAME_PASSWORD, releasename, filepath, releasepath)

						elif NZB_NAME in release_name:
							releasename = release_name
							filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR'), ordner, releasename)
							only_filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR'), ordner)
							releasepath = only_filepath

							# Upload ablauf
							auto_release(RELEASENAME_PASSWORD, releasename, filepath, releasepath)

	elif os.environ.get('NZBPO_NZB_ORDNER_SUCHE') == "DISABLED":
		print "[INFO] NZB Ordner Suche ist deaktiviert"

		# Hier wird das Verzeichnis aufgelistet mit den vorhandenen NZBs
		list_dir_nzb = os.listdir(releasepath)
		for releasename in list_dir_nzb:
			# Hier wird der Nzb Name mit dem Verzeichnis abgeglichen
			if NZB_NAME in releasename:
				filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR'), releasename)

				# Upload ablauf
				auto_release(RELEASENAME_PASSWORD, releasename, filepath, releasepath)

elif os.environ.get('NZBPO_PASSWORD_LISTE') == "ENABLED" and not ('NZBPR_*Unpack:Password' in os.environ):
	print "[INFO] In dem WEB Interface wurde kein Passwort angegeben..."
	print "[INFO] Suche Passwort mittels Logger.... und vergleiche mit der Passwortliste: [%s]" % (os.environ.get('NZBOP_UNPACKPASSFILE'))

	if not os.environ.get('NZBOP_UNPACKPASSFILE'):
		print "[ERROR] Keine Passwortlist in dem Web Interface angegeben.... Bitte Aendern...!"
		sys.exit(POSTPROCESS_ERROR)

	if not os.path.isfile(os.environ.get('NZBOP_UNPACKPASSFILE')):
		print "[ERROR] Der Pfad von [%s] ist nicht vorhanden. Bitte kontrollieren!..." % (os.environ['NZBOP_UNPACKPASSFILE'])
		sys.exit(POSTPROCESS_ERROR)

	if not os.environ.get('NZBPO_NZB_DIR_NEW'):
		print "[ERROR] Bitte angabe Ueberpruefen zu NZB Dir!: [%s]" % (os.environ.get('NZBPO_NZB_DIR_NEW'))
		sys.exit(POSTPROCESS_ERROR)

	if not os.path.isdir(os.environ.get('NZBPO_NZB_DIR_NEW')):
		print "[ERROR] Der Pfad von [%s] ist nicht vorhanden. Bitte kontrollieren!..." % (os.environ.get('NZBPO_NZB_DIR_NEW'))
		sys.exit(POSTPROCESS_ERROR)

	if not os.environ.get('NZBPO_LOG_PW'):
		print "[ERROR] Fehler bei der angabe des LOG_PWs.... Bitte ueberpruefen...."
		sys.exit(POSTPROCESS_ERROR)

	if not os.environ.get('NZBPO_NZB_DIR'):
		print "[ERROR] Fehler bei der angabe des NZB_DIR.... Bitte ueberpruefen"
		sys.exit(POSTPROCESS_ERROR)

	if not os.path.isdir(os.environ.get('NZBPO_NZB_DIR')):
		print "[ERROR] Der angegebene Pfad is kein Verzeichnis... Bitte ueberprufen!"
		sys.exit(POSTPROCESS_ERROR)

	# Logger um das Passwort fest zu stellen!!
	host = os.environ['NZBOP_CONTROLIP']
	port = os.environ['NZBOP_CONTROLPORT']
	username = os.environ['NZBOP_CONTROLUSERNAME']
	password = os.environ['NZBOP_CONTROLPASSWORD']
	rpcUrl = 'http://%s:%s@%s:%s/xmlrpc' % (username, password, host, port)
	server = ServerProxy(rpcUrl)
	postqueue = server.postqueue(10000)
	log = postqueue[0]['Log']
	print "[INFO] Messages von der NZB Datei werden eingelesen und verarbeitet."
	print "[INFO] Passwortliste wird eingelesen und verarbeitet."
	if len(log) > 0:
		for entry in log:
			log_content = ((u'%s\n' % (entry['Text'])).encode('utf8'))

			# Eilesen der Passwortlist welche in NZBGet hinterlegt wurde als Pfad angabe
			with open(os.environ['NZBOP_UNPACKPASSFILE'], "r") as passwort_liste:
				for liste1 in passwort_liste:
					liste = (liste1.rstrip())
					if liste in log_content:
						passwort_liste.close()

						if os.environ.get('NZBPO_NZB_ORDNER_SUCHE') == "ENABLED":
							print "[INFO] NZB Ordner Suche ist Aktiviert"

							# Hier wird das Verzeichnis aufgelistet mit den vorhandenen NZBs
							list_dir_nzb = os.listdir(os.environ.get('NZBPO_NZB_DIR'))
							list_ordner_nzb = next(os.walk(os.environ.get('NZBPO_NZB_DIR')))[1]
							ordner_name1 = os.environ.get('NZBPO_NZB_ORDNER1')
							ordner_name2 = os.environ.get('NZBPO_NZB_ORDNER2')
							ordner_name3 = os.environ.get('NZBPO_NZB_ORDNER3')
							ordner_name4 = os.environ.get('NZBPO_NZB_ORDNER4')
							ordner_name5 = os.environ.get('NZBPO_NZB_ORDNER5')

							for ordner in ordner_name1, ordner_name2, ordner_name3, ordner_name4, ordner_name5:
								if ordner in list_ordner_nzb:
									ordner_path = os.path.join(os.environ.get('NZBPO_NZB_DIR'), ordner)
									ordner_list = os.listdir(ordner_path)
									for release_name in ordner_list:
										for releasename in list_dir_nzb:
											# Hier wird der Nzb Name mit dem Verzeichnis abgeglichen
											NZB_NAME = os.environ.get('NZBPP_NZBNAME')
											if NZB_NAME in releasename:

												# Passwort von Passwortliste was fuer das entpacken erfolgreich verwendet wurde
												PASSWORD_FILE = liste
												print "[INFO] Passwort wurde gefunden und kann nun weiter verwendet werden: [ %s ]." % (PASSWORD_FILE)
												path_old = os.environ.get('NZBPO_NZB_DIR')
												releasepath = os.environ.get('NZBPO_NZB_DIR_NEW')
												nzb_without_extension = os.environ.get('NZBPP_NZBNAME')
												file_old = "%s.nzb.queued" % (nzb_without_extension)
												releasename = "%s {{%s}}.nzb" % (nzb_without_extension, PASSWORD_FILE)
												filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
												print "[INFO] NZB File wird umbenannt in: [%s {{%s}}.nzb]" % (nzb_without_extension, PASSWORD_FILE)
												os.rename(os.path.join(path_old, file_old), os.path.join(filepath))

												# Upload ablauf
												upload_release(releasename, filepath)
												cleanup_nzb(releasepath, releasename)
												log_password()

											elif NZB_NAME in release_name:

												# Passwort von Passwortliste was fuer das entpacken erfolgreich verwendet wurde
												PASSWORD_FILE = liste
												print "[INFO] Passwort wurde gefunden und kann nun weiter verwendet werden: [ %s ]." % (PASSWORD_FILE)
												path_old = os.environ.get('NZBPO_NZB_DIR')
												releasepath = os.environ.get('NZBPO_NZB_DIR_NEW')
												nzb_without_extension = os.environ.get('NZBPP_NZBNAME')
												file_old = "%s.nzb.queued" % (nzb_without_extension)
												releasename = "%s {{%s}}.nzb" % (nzb_without_extension, PASSWORD_FILE)
												filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
												print "[INFO] NZB File wird umbenannt in: [%s {{%s}}.nzb]" % (nzb_without_extension, PASSWORD_FILE)
												os.rename(os.path.join(path_old, ordner, file_old), os.path.join(filepath))

												# Upload ablauf
												upload_release(releasename, filepath)
												cleanup_nzb(releasepath, releasename)
												log_password()

						elif os.environ.get('NZBPO_NZB_ORDNER_SUCHE') == "DISABLED":
							print "[INFO] NZB Ordner Suche ist deaktiviert"

							# Passwort von Passwortliste was fuer das entpacken erfolgreich verwendet wurde
							PASSWORD_FILE = liste
							print "[INFO] Passwort wurde gefunden und kann nun weiter verwendet werden: [ %s ]." % (PASSWORD_FILE)
							path_old = os.environ.get('NZBPO_NZB_DIR')
							releasepath = os.environ.get('NZBPO_NZB_DIR_NEW')
							nzb_without_extension = os.environ.get('NZBPP_NZBNAME')
							file_old = "%s.nzb.queued" % (nzb_without_extension)
							releasename = "%s {{%s}}.nzb" % (nzb_without_extension, PASSWORD_FILE)
							filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
							print "[INFO] NZB File wird umbenannt in: [%s {{%s}}.nzb]" % (nzb_without_extension, PASSWORD_FILE)
							os.rename(os.path.join(path_old, file_old), os.path.join(filepath))

							# Upload ablauf
							upload_release(releasename, filepath)
							cleanup_nzb(releasepath, releasename)
							log_password()
	else:
		print "[ERROR] Fehler bei der Log ausfuehrung...."

	if os.environ.get('NZBPO_NZB_ORDNER_SUCHE') == "ENABLED":
		print "[INFO] NZB Ordner Suche ist Aktiviert"

		# Hier wird das Verzeichnis aufgelistet mit den vorhandenen NZBs
		list_dir_nzb = os.listdir(os.environ.get('NZBPO_NZB_DIR'))
		list_ordner_nzb = next(os.walk(os.environ.get('NZBPO_NZB_DIR')))[1]
		ordner_name1 = os.environ.get('NZBPO_NZB_ORDNER1')
		ordner_name2 = os.environ.get('NZBPO_NZB_ORDNER2')
		ordner_name3 = os.environ.get('NZBPO_NZB_ORDNER3')
		ordner_name4 = os.environ.get('NZBPO_NZB_ORDNER4')
		ordner_name5 = os.environ.get('NZBPO_NZB_ORDNER5')

		for ordner in ordner_name1, ordner_name2, ordner_name3, ordner_name4, ordner_name5:
			if ordner in list_ordner_nzb:
				ordner_path = os.path.join(os.environ.get('NZBPO_NZB_DIR'), ordner)
				ordner_list = os.listdir(ordner_path)
				for release_name in ordner_list:
					for releasename in list_dir_nzb:
						# Hier wird der Nzb Name mit dem Verzeichnis abgeglichen
						NZB_NAME = os.environ.get('NZBPP_NZBNAME')
						if NZB_NAME in releasename:

							# Passwort von Passwortliste was fuer das entpacken erfolgreich verwendet wurde
							path_old = os.environ.get('NZBPO_NZB_DIR')
							releasepath = os.environ.get('NZBPO_NZB_DIR_NEW')
							nzb_without_extension = os.environ.get('NZBPP_NZBNAME')
							file_old = "%s.nzb.queued" % (nzb_without_extension)
							releasename = "%s.nzb" % (nzb_without_extension)
							filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
							print "[INFO] NZB File wird umbenannt in: [%s.nzb]" % (nzb_without_extension)
							os.rename(os.path.join(path_old, file_old), os.path.join(filepath))

							# Upload ablauf
							upload_release(releasename, filepath)
							cleanup_nzb(releasepath, releasename)
							log_password()

						elif NZB_NAME in release_name:

							# Passwort von Passwortliste was fuer das entpacken erfolgreich verwendet wurde
							path_old = os.environ.get('NZBPO_NZB_DIR')
							releasepath = os.environ.get('NZBPO_NZB_DIR_NEW')
							nzb_without_extension = os.environ.get('NZBPP_NZBNAME')
							file_old = "%s.nzb.queued" % (nzb_without_extension)
							releasename = "%s.nzb" % (nzb_without_extension)
							filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
							print "[INFO] NZB File wird umbenannt in: [%s.nzb]" % (nzb_without_extension)
							os.rename(os.path.join(path_old, ordner, file_old), os.path.join(filepath))

							# Upload ablauf
							upload_release(releasename, filepath)
							cleanup_nzb(releasepath, releasename)
							log_password()

	elif os.environ.get('NZBPO_NZB_ORDNER_SUCHE') == "DISABLED":
		print "[INFO] NZB Ordner Suche ist deaktiviert"

		# Passwort von Passwortliste was fuer das entpacken erfolgreich verwendet wurde
		path_old = os.environ.get('NZBPO_NZB_DIR')
		releasepath = os.environ.get('NZBPO_NZB_DIR_NEW')
		nzb_without_extension = os.environ.get('NZBPP_NZBNAME')
		file_old = "%s.nzb.queued" % (nzb_without_extension)
		releasename = "%s.nzb" % (nzb_without_extension)
		filepath = os.path.join(os.environ.get('NZBPO_NZB_DIR_NEW'), releasename)
		print "[INFO] NZB File wird umbenannt in: [%s.nzb]" % (nzb_without_extension)
		os.rename(os.path.join(path_old, file_old), os.path.join(filepath))

		# Upload ablauf
		upload_release(releasename, filepath)
		cleanup_nzb(releasepath, releasename)
		log_password()

elif os.environ.get('NZBPO_PASSWORD_LISTE') == "DISABLED" or os.environ.get('NZBPO_PASSWORD') == "DISABLED" and ('NZBPR_*Unpack:Password' in os.environ):
	print "[INFO] Passwort: [%s] oder Passwort_Liste: [%s] deaktiviert, aber Passwort im Web Interface gegeben: [%s]" % (os.environ.get('NZBPO_PASSWORD') ,os.environ.get('NZBPO_PASSWORD_LISTE'), ('NZBPR_*Unpack:Password' in os.environ))
	releasename = os.environ['NZBPP_NZBFILENAME']
	filepath = os.path.join(NZB_DIR, nzb_filename)
	releasepath = os.environ.get('NZBPO_NZB_DIR')

	upload_release(releasename, filepath)
	cleanup_nzb(releasepath, releasename)
	sys.exit(POSTPROCESS_SUCCESS)

elif os.environ.get('NZBPO_PASSWORD_LISTE') == "DISABLED" or os.environ.get('NZBPO_PASSWORD') == "DISABLED" and not ('NZBPR_*Unpack:Password' in os.environ):
	print "[INFO] Passwort: [%s] oder Passwort_Liste: [%s] deaktiviert, aber Passwort im Web Interface gegeben: [%s]" % (os.environ.get('NZBPO_PASSWORD') ,os.environ.get('NZBPO_PASSWORD_LISTE'), ('NZBPR_*Unpack:Password' in os.environ))
	releasename = os.environ['NZBPP_NZBFILENAME']
	filepath = os.path.join(NZB_DIR, nzb_filename)
	releasepath = os.environ.get('NZBPO_NZB_DIR')

	upload_release(releasename, filepath)
	cleanup_nzb(releasepath, releasename)
	sys.exit(POSTPROCESS_SUCCESS)

else:
	print "[ERROR] Skript ausfuehrung Fehler.... Skript wird nicht gestartet"
	sys.exit(POSTPROCESS_ERROR)
