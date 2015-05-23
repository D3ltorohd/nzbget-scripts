#!/usr/bin/env python
#
##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###
 
# NZBGet to Wizznab Script
#
# Dieses Script uploaded heruntergeladene NZB Files auf Wizznab
#
# NOTE: Dieses Script benoetigt python 2.7, python-requests und GitPython.
#
# NOTE: Dieses Script benoetigt unter umstaenden zusaetzlich das Script Logger.py!.
#
# NOTE: Bitte nicht das Originale Logger.py Skript Verwenden!!!!.
#
# NOTE: Hier sind die Neusten Skript Versionen zu finden: Logger.py und nzb2wizznab.py https://github.com/cytec/nzbget-scripts/tree/master/PostProcessing .
#
# NOTE: Version Beta: 3.9.
 
##############################################################################
### OPTIONS                                                                ###

## Wichtig fuer Versions Ueberpruefung.....

# Versions Ueberpruefung!.
#
# Bitte angaben ohne "".
# Hier muesst ihr bitte den Pfad eintragen in welchem Ordner sich dieses Skript befindet.
# Als Beispiel siehe oben!!!.
#SCRIPT_DIR=/volume1/01_public/nzbget2wizznab.py

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

# Das Skript Logger.py MUSS Aktiviert sein!!!! !!!!BETA!!!(ENABLED, DISABLED).
#
# Aktivierung oder Deaktivierung fuer die PasswortListe um PWs auslesen zu koennen.
#
# [Bei ENABLED]: Werden die NZBs mit dem Passwort von der PasswortListe bestueckt und hochgeladen.
# [Bei DISABLED]: Werden die NZBs unveraendert hochgeladen.
#
# [WICHTIG]: Das Skript Logger.py MUSS vor dem Wizznab Skript ausgefuehrt werden!!.
# [WICHTIG]: Dies kann man unter Settings-->EXTENSION SCRIPTS-->ScriptOrder einstellen.
# [WICHTIG]: Einfach mit den Entsprechenden Pfeilen verschieben bis Logger.py vor dem Wizznab Skript ist!.
#PASSWORD_LISTE=DISABLED

## Zwischenspeichern um Passwort verarbeiten zu Koennen

# Pfad fuer Passwort File.
#
# Bitte angaben ohne "".
# Hier bitte den Pfad eintragen wo das Passwort gespeichert werden kann.
# Dies dient nur als Zwischenspeicherung.
# Bitte wie im Beispiel oben angeben.
#PASSWORD_FILE=/volume1/01_public/PASSWORT.txt

## Logger.py Namen

# Datei Namen von Logger.py.
#
# Bitte angaben ohne "".
# Hier muesst ihr bitte den Namen von Logger.py angeben.
# Den Dateinamen!!.
# Als Beispiel.
# Das steht so in der Logger.py Datei im WEB INTERFACE: This script saves post-processing log of nzb-file into file [ _postprocesslog.txt ] in the destination directory.
# Also waehre der Namen in diesem Beispiel: _postprocesslog.txt.
# PLUS + den Pfad angeben wo ihr die .txt gesichert habt!.
#LOGGER_FILE_PATH_NAME=_postprocesslog.txt

## loeschen der TEMP Dateien

# NZB Dateien Loeschen (ENABLED, DISABLED).
#
# Aktivierung oder Deaktivierung fuer das loeschen der NZB Dateien in dem Ordner NZB_DIR_NEW.
#
# [Bei ENABLED]: Werden die NZB Dateien in dem Ordner NZB_DIR_NEW geloescht.
# [Bei DISABLED]: Werden die NZB Dateien in dem Ordner NZB_DIR_NEW gespeichert.
#DELETE_NZB=DISABLED

## loeschen der NZBs

# TEMP Dateien Loeschen (ENABLED, DISABLED).
#
# Aktivierung oder Deaktivierung fuer das loeschen der TEMP Dateien.
#
# [Bei ENABLED]: Werden die TEMP Dateien (.txt, etc ) von der Passwortliste in den jeweiligen Pfaden geloescht.
# [Bei DISABLED]: Werden die TEMP Dateien (.txt, etc ) von der Passwortliste in den jeweiligen Pfaden gespeichert.
#DELETE_TEMP=DISABLED

## NZB DIR NEW

# NZB DIR NEW.
#
# Bitte angaben ohne "".
# Hier wird der neue Pfad eingetragen fuer die NZBs.
# NZBs werden Dort auch gesichert.
# Bitte wie im Beispiel oben angeben.
#NZB_DIR_NEW=/volume1/NZBget/new

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################
 
import sys
import os
import gzip
import requests
import re
import shutil
from git import Repo

# Exit codes used by NZBGet
POSTPROCESS_SUCCESS=93
POSTPROCESS_ERROR=94

if not os.environ.has_key('NZBOP_SCRIPTDIR'):
    print "[ERROR] Dieses Skript kann nur von NZBGet (13.0 oder neuer) ausgefuehrt werden."
    sys.exit(POSTPROCESS_ERROR)  
  
if os.environ['NZBOP_VERSION'][0:5] < '13.0':
    print "[ERROR] NZBGet Version %s wird nicht unterstuetzt. Bitte NZBGet updaten." % (str(os.environ['NZBOP_VERSION']))
    sys.exit(POSTPROCESS_ERROR)
    
if ((os.environ['NZBPO_PASSWORD_LISTE']) == "ENABLED" and (os.environ['NZBOP_VERSION'][0:5] < '15.0')):
	print "[ERROR] NZBGet Version %s wird nicht unterstuetzt. Bitte NZBGet updaten." % (str(os.environ['NZBOP_VERSION']))
	sys.exit(POSTPROCESS_ERROR)

print "[INFO] Skript wird von NZBGet Version [%s] ausgefuehrt." % (str(os.environ['NZBOP_VERSION']))

if not os.path.isdir(os.environ['NZBPO_NZB_DIR']):
	print "[ERROR] Der Pfad von [%s] ist nicht vorhanden. Bitte kontrollieren!..." % (os.environ['NZBPO_NZB_DIR'])
	sys.exit(POSTPROCESS_ERROR)

if not 'NZBPP_TOTALSTATUS' in os.environ:
	print('[ERROR] *** NZBGet post-processing script ***')
	print('[ERROR] Das Skript wird nicht gestartet da Status: [%s].') % (os.environ(['NZBPP_TOTALSTATUS']))
	sys.exit(POSTPROCESS_ERROR)

print('[INFO] Script nzbget2wizznab erfolgreich gestartet')
 
if os.environ.has_key('NZBPP_TOTALSTATUS'):
    if not os.environ['NZBPP_TOTALSTATUS'] == 'SUCCESS':
        print "[ERROR] Skript Abbruch wegen: [Total Status] [%s]." % (os.environ['NZBPP_STATUS'])
        if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
		print "[INFO] TEMP Dateien loeschen aktiviert"
		if os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] TEMP Dateien gefunden und werden geloescht"
			try:
				remove = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
				os.remove(remove)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_ERROR)
			except OSError, e:
					print ("Error: %s - %s." % (e.filename,e.strerror))
					sys.exit(POSTPROCESS_ERROR)
			
		elif not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
			sys.exit(POSTPROCESS_ERROR)
		else:
			print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
			sys.exit(POSTPROCESS_ERROR)
	elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
		print "[INFO] TEMP Dateien loeschen deaktiviert"
		sys.exit(POSTPROCESS_ERROR)
        
if os.environ.has_key('NZBPP_SCRIPTSTATUS'):
    if not ((os.environ['NZBPP_SCRIPTSTATUS'] == 'SUCCESS') or (os.environ['NZBPP_SCRIPTSTATUS'] == 'NONE')):
        print "[ERROR] Skript Abbruch wegen: [Script Status] [%s]." % (os.environ['NZBPP_SCRIPTSTATUS'])
        if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
		print "[INFO] TEMP Dateien loeschen aktiviert"
		if os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] TEMP Dateien gefunden und werden geloescht"
			try:
				remove = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
				os.remove(remove)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_ERROR)
			except OSError, e:
					print ("Error: %s - %s." % (e.filename,e.strerror))
					sys.exit(POSTPROCESS_ERROR)
			
		elif not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
			sys.exit(POSTPROCESS_ERROR)
		else:
			print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
			sys.exit(POSTPROCESS_ERROR)
	elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
		print "[INFO] TEMP Dateien loeschen deaktiviert"
		sys.exit(POSTPROCESS_ERROR)
        
Skript_dir = (os.path.dirname(os.path.abspath(os.environ['NZBPO_SCRIPT_DIR'])))
git_repo = (os.path.join(Skript_dir, 'nzbget-scripts'))
Repo.clone_from("https://github.com/cytec/nzbget-scripts", git_repo)
Skript = (os.path.join(git_repo, 'PostProcessing', 'nzb2wizznab.py'))
Version = "Version Beta: 3.9"
with open(Skript , "r") as Skript_lines:
	lines = Skript_lines.readlines()[17]
	if Version in lines:
		print "[INFO] Das Skript wird mit der Neusten Version Gestartet: [%s]" % (Version)
		try:
			shutil.rmtree(os.path.join(git_repo))
		except OSError, e:
			print ("Error: %s - %s." % (e.filename,e.strerror))
			sys.exit(POSTPROCESS_ERROR)
	else:
		print "[WARNING] Bitte UPDATEN unter [ https://github.com/cytec/nzbget-scripts/tree/master/PostProcessing ] die Neuste Version Downloaden"
		try:
			shutil.rmtree(os.path.join(git_repo))
		except OSError, e:
			print ("Error: %s - %s." % (e.filename,e.strerror))
			sys.exit(POSTPROCESS_ERROR)
        
#Einlesen der Parameter
NZB_DIR = (os.environ['NZBPO_NZB_DIR'])
APIKEY = (os.environ['NZBPO_APIKEY'])
UPLOAD_URL = (os.environ['NZBPO_UPLOAD_URL'])
    
if (os.environ['NZBPO_PASSWORD']) == "ENABLED" and ('NZBPR_*Unpack:Password' in os.environ):
	print "[INFO] Passwort suche ist aktiviert, Passwort wurde in der Web Ui: [%s] gefunden und wird verarbeitet...." % (os.environ['NZBPR_*Unpack:Password'])
	if not os.path.isdir(os.environ['NZBPO_NZB_DIR_NEW']):
		print "[ERROR] Der Pfad von [%s] ist nicht vorhanden. Bitte kontrollieren!..." % (os.environ['NZBPO_NZB_DIR'])
		sys.exit(POSTPROCESS_ERROR)
	PASSWORD = (os.environ['NZBPR_*Unpack:Password'])
	file_name_zur_pruefung_password = "{{%s}}.nzb" % (PASSWORD.rstrip())
	name_nzbget = (os.environ['NZBPP_NZBNAME'])
	list_nzb_dir = (os.listdir(NZB_DIR))
	for liste_nzb_dir in list_nzb_dir:
		if (name_nzbget) in (liste_nzb_dir):
			nzb_filename = (os.path.join(NZB_DIR, liste_nzb_dir))
			if (file_name_zur_pruefung_password) in (nzb_filename):
				print "[INFO] Passwort von Web Ui: [%s] ist im NZB Namen erhalten keine erweiterte Umbenennung noetig...." % (os.environ['NZBPR_*Unpack:Password'])
				nzb_filepath = os.path.join(NZB_DIR, nzb_filename)
				f = open(nzb_filepath)
				file_content = f.read()
				f.close()
				print "[INFO] uploading file [%s]..." % nzb_filepath
				post_data = {
					"apikey": APIKEY,
				}
				myfile = {"Filedata": (nzb_filename, file_content)}
				print requests.post(UPLOAD_URL, data=post_data, files=myfile).text
				if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
					print "[INFO] TEMP Dateien loeschen aktiviert"
					if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
						print "[INFO] TEMP Dateien gefunden und werden geloescht"
						try:
							remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
							remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
							os.remove(remove)
							os.remove(remove1)
							print "[INFO] TEMP Dateien erfolgreich geloescht"
							sys.exit(POSTPROCESS_SUCCESS)
						except OSError, e:
							print ("Error: %s - %s." % (e.filename,e.strerror))
							sys.exit(POSTPROCESS_ERROR)
					elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
						try:
							remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
							os.remove(remove1)
							print "[INFO] TEMP Dateien erfolgreich geloescht"
							sys.exit(POSTPROCESS_SUCCESS)
						except OSError, e:
							print ("Error: %s - %s." % (e.filename,e.strerror))
							sys.exit(POSTPROCESS_ERROR)
					elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
						print "[INFO] TEMP Dateien gefunden und werden geloescht"
						try:
							remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
							os.remove(remove)
							print "[INFO] TEMP Dateien erfolgreich geloescht"
							sys.exit(POSTPROCESS_SUCCESS)
						except OSError, e:
							print ("Error: %s - %s." % (e.filename,e.strerror))
							sys.exit(POSTPROCESS_ERROR)
					elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
						print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
						print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
						sys.exit(POSTPROCESS_SUCCESS)
					else:
						print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
						sys.exit(POSTPROCESS_ERROR)
				elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
					print "[INFO] TEMP Dateien loeschen deaktiviert"
					sys.exit(POSTPROCESS_SUCCESS)
			elif not (file_name_zur_pruefung_password) in (nzb_filename):
				print "[INFO] Passwort von Web Ui stimmt nicht mit dem Passwort im NZB Namen ueberein erweiterte Umbenennung wird eingeleitet...."
				for liste_nzb_dir in list_nzb_dir:
					if (name_nzbget) in (liste_nzb_dir):
						nzb_filename = (os.path.join(NZB_DIR, liste_nzb_dir))
						PASSWORD = (os.environ['NZBPR_*Unpack:Password'])
						nzb_filepath = os.path.join(NZB_DIR, nzb_filename)
						nzb_new_file_path_web_interface = (os.environ['NZBPO_NZB_DIR_NEW'])
						file_old = (os.path.basename(nzb_filepath))
						if (('{{' in nzb_filename) and ('}}' in nzb_filename)):
							print "[INFO] Passwort im NZB Namen gefunden Entfernung und Umbenennung wird eingeleitet..."
							altes_passwort_suchen = re.match( r'^.*?\{\{[ ]?(.*?)[ ]?\}\}', file_old)
							passwort_alt = "{{%s}}" % (altes_passwort_suchen.group(1))
							ohne_passwort = file_old.replace(passwort_alt, "").rstrip()
							newname = "%s {{%s}}" % (ohne_passwort, PASSWORD.rstrip())
							nzb_new_file_path = os.path.join(nzb_new_file_path_web_interface, newname)
							print "[INFO] NZB File wird umbenannt in[%s {{%s}}]" % (ohne_passwort, PASSWORD.rstrip())
							os.rename(os.path.join(NZB_DIR, file_old), os.path.join(nzb_new_file_path_web_interface, newname))
							f = open(nzb_new_file_path)
							file_content = f.read()
							f.close()
							print "[INFO] uploading file [%s]..." % nzb_new_file_path 
							post_data = {
								"apikey": APIKEY,
							}
							myfile = {"Filedata": (newname, file_content)}
							print requests.post(UPLOAD_URL, data=post_data, files=myfile).text
							if (os.environ['NZBPO_DELETE_NZB']) == "ENABLED":
								print "[INFO] NZB Dateien loeschen aktiviert"
								os_path_isfile = "%s/%s" % (nzb_new_file_path_web_interface, newname)
								if os.path.isfile(os_path_isfile):
									print "[INFO] NZB Dateien gefunden und werden geloescht..."
									try:
										remove = ("%s/%s") % (nzb_new_file_path_web_interface, newname)
										os.remove(remove)
										print "[INFO] NZB Dateien erfolgreich geloescht"
									except OSError, e:
										print ("Error: %s - %s." % (e.filename,e.strerror))
										sys.exit(POSTPROCESS_ERROR)
									if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
										print "[INFO] TEMP Dateien loeschen aktiviert"
										if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove)
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											try:
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												os.remove(remove)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
											print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											sys.exit(POSTPROCESS_SUCCESS)
										else:
											print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
											sys.exit(POSTPROCESS_ERROR)
									elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
										print "[INFO] TEMP Dateien loeschen deaktiviert"
										sys.exit(POSTPROCESS_SUCCESS)
								elif not os.path.isfile(os_path_isfile):
									print "[WARNING] Keine NZB Dateien gefunden....."
									if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
										print "[INFO] TEMP Dateien loeschen aktiviert"
										if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove)
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											try:
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												os.remove(remove)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
											print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											sys.exit(POSTPROCESS_SUCCESS)
										else:
											print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
											sys.exit(POSTPROCESS_ERROR)
									elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
										print "[INFO] TEMP Dateien loeschen deaktiviert"
										sys.exit(POSTPROCESS_SUCCESS)
									else:
										print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Ueberpruefung der Pfade Fehlerhaft: [%s] - [%s]" % (os_path_isfile, (os.environ['NZBPO_NZB_DIR_NEW']))
										sys.exit(POSTPROCESS_ERROR)
							elif (os.environ['NZBPO_DELETE_NZB']) == "DISABLED":
								print "[INFO] NZB Dateien loeschen deaktiviert"
								if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
									print "[INFO] TEMP Dateien loeschen aktiviert"
									if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
										print "[INFO] TEMP Dateien gefunden und werden geloescht"
										try:
											remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
											remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											os.remove(remove)
											os.remove(remove1)
											print "[INFO] TEMP Dateien erfolgreich geloescht"
											sys.exit(POSTPROCESS_SUCCESS)
										except OSError, e:
											print ("Error: %s - %s." % (e.filename,e.strerror))
											sys.exit(POSTPROCESS_ERROR)
									elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
										try:
											remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											os.remove(remove1)
											print "[INFO] TEMP Dateien erfolgreich geloescht"
											sys.exit(POSTPROCESS_SUCCESS)
										except OSError, e:
											print ("Error: %s - %s." % (e.filename,e.strerror))
											sys.exit(POSTPROCESS_ERROR)
									elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
										print "[INFO] TEMP Dateien gefunden und werden geloescht"
										try:
											remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
											os.remove(remove)
											print "[INFO] TEMP Dateien erfolgreich geloescht"
											sys.exit(POSTPROCESS_SUCCESS)
										except OSError, e:
											print ("Error: %s - %s." % (e.filename,e.strerror))
											sys.exit(POSTPROCESS_ERROR)
									elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
										print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
										print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
										sys.exit(POSTPROCESS_SUCCESS)
									else:
										print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
										sys.exit(POSTPROCESS_ERROR)
								elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
									print "[INFO] TEMP Dateien loeschen deaktiviert"
									sys.exit(POSTPROCESS_SUCCESS)
								else:
									print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Loeschen Fehler NZB: [%s]" % (os.environ['NZBPO_DELETE_NZB'])
									sys.exit(POSTPROCESS_ERROR)
						elif not (('{{' in nzb_filename) and ('}}' in nzb_filename)):
							print "[INFO] Passwort von Web Ui nicht im NZB Namen gefunden Umbenennung wird eingeleitet!!"
							newname = "%s {{%s}}.nzb" % (nzb_without_extension, PASSWORD.rstrip())
							nzb_new_file_path = os.path.join(nzb_new_file_path_web_interface, newname)
							print "[INFO] NZB File wird umbenannt in: [%s {{%s}}.nzb]" % (nzb_without_extension, PASSWORD.rstrip())
							os.rename(os.path.join(NZB_DIR, file_old), os.path.join(nzb_new_file_path_web_interface, newname))
							f = open(nzb_new_file_path)
							file_content = f.read()
							f.close()
							print "[INFO] uploading file [%s]..." % nzb_new_file_path 
							post_data = {
								"apikey": APIKEY,
							}
							myfile = {"Filedata": (newname, file_content)}
							print requests.post(UPLOAD_URL, data=post_data, files=myfile).text
							if (os.environ['NZBPO_DELETE_NZB']) == "ENABLED":
								print "[INFO] NZB Dateien loeschen aktiviert"
								os_path_isfile = "%s/%s" % (nzb_new_file_path_web_interface, newname)
								if os.path.isfile(os_path_isfile):
									print "[INFO] NZB Dateien gefunden und werden geloescht..."
									try:
										remove = ("%s/%s") % (nzb_new_file_path_web_interface, newname)
										os.remove(remove)
										print "[INFO] NZB Dateien erfolgreich geloescht"
									except OSError, e:
										print ("Error: %s - %s." % (e.filename,e.strerror))
										sys.exit(POSTPROCESS_ERROR)
									if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
										print "[INFO] TEMP Dateien loeschen aktiviert"
										if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove)
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											try:
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												os.remove(remove)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
											print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											sys.exit(POSTPROCESS_SUCCESS)
										else:
											print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
											sys.exit(POSTPROCESS_ERROR)
									elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
										print "[INFO] TEMP Dateien loeschen deaktiviert"
										sys.exit(POSTPROCESS_SUCCESS)
								elif not os.path.isfile(os_path_isfile):
									print "[WARNING] Keine NZB Dateien gefunden....."
									if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
										print "[INFO] TEMP Dateien loeschen aktiviert"
										if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove)
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											try:
												remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
												os.remove(remove1)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
											print "[INFO] TEMP Dateien gefunden und werden geloescht"
											try:
												remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
												os.remove(remove)
												print "[INFO] TEMP Dateien erfolgreich geloescht"
												sys.exit(POSTPROCESS_SUCCESS)
											except OSError, e:
												print ("Error: %s - %s." % (e.filename,e.strerror))
												sys.exit(POSTPROCESS_ERROR)
										elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
											print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
											print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											sys.exit(POSTPROCESS_SUCCESS)
										else:
											print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
											sys.exit(POSTPROCESS_ERROR)
									elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
										print "[INFO] TEMP Dateien loeschen deaktiviert"
										sys.exit(POSTPROCESS_SUCCESS)
									else:
										print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... TEMP Loeschung [%s] FEHLER!!!" % (os.environ['NZBPO_DELETE_TEMP'])
										sys.exit(POSTPROCESS_ERROR)
								else:
									print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Ueberpruefung der Pfade Fehlerhaft: [%s] - [%s]" % (os_path_isfile, (os.environ['NZBPO_NZB_DIR_NEW']))
									sys.exit(POSTPROCESS_ERROR)
							elif (os.environ['NZBPO_DELETE_NZB']) == "DISABLED":
								print "[INFO] NZB Dateien loeschen deaktiviert"
								if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
									print "[INFO] TEMP Dateien gefunden und werden geloescht"
									if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
										print "[INFO] TEMP Dateien gefunden und werden geloescht"
										try:
											remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
											remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											os.remove(remove)
											os.remove(remove1)
											print "[INFO] TEMP Dateien erfolgreich geloescht"
											sys.exit(POSTPROCESS_SUCCESS)
										except OSError, e:
											print ("Error: %s - %s." % (e.filename,e.strerror))
											sys.exit(POSTPROCESS_ERROR)
									elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
										try:
											remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
											os.remove(remove1)
											print "[INFO] TEMP Dateien erfolgreich geloescht"
											sys.exit(POSTPROCESS_SUCCESS)
										except OSError, e:
											print ("Error: %s - %s." % (e.filename,e.strerror))
											sys.exit(POSTPROCESS_ERROR)
									elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
										print "[INFO] TEMP Dateien gefunden und werden geloescht"
										try:
											remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
											os.remove(remove)
											print "[INFO] TEMP Dateien erfolgreich geloescht"
											sys.exit(POSTPROCESS_SUCCESS)
										except OSError, e:
											print ("Error: %s - %s." % (e.filename,e.strerror))
											sys.exit(POSTPROCESS_ERROR)
									elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
										print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
										print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
										sys.exit(POSTPROCESS_SUCCESS)
									else:
										print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
										sys.exit(POSTPROCESS_ERROR)
								elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
									print "[INFO] TEMP Dateien loeschen deaktiviert"
									sys.exit(POSTPROCESS_SUCCESS)
								else:
									print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Loeschen Fehler TEMP: [%s]" % (os.environ['NZBPO_DELETE_TEMP'])
									sys.exit(POSTPROCESS_ERROR)
							else:
								print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Loeschen Fehler NZB: [%s]" % (os.environ['NZBPO_DELETE_NZB'])
								sys.exit(POSTPROCESS_ERROR)
						else:
							print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Ueberpruefung ob Passwort vorhanden '{{' - '}}': [%s]" % (nzb_filename)
							sys.exit(POSTPROCESS_ERROR)
			else:
				print "[ERROR] Fehler bei der Ausfuehrung des Skripts!! Ueberpruefung ob Passwort vorhanden Allgemein: [%s] - [%s]...." % (file_name_zur_pruefung_password, nzb_filename)
				sys.exit(POSTPROCESS_ERROR)

elif (os.environ['NZBPO_PASSWORD_LISTE']) == "ENABLED" and not ('NZBPR_*Unpack:Password' in os.environ):
	print "[INFO] In der WEB UI wurde keine Passwort angegeben..."
	print "[INFO] Suche Passwort in: [%s].... und vergleiche mit der Passwortliste: [%s]" % ((os.environ['NZBPO_LOGGER_FILE_PATH_NAME']), (os.environ['NZBOP_UNPACKPASSFILE']))
	if not os.path.isfile(os.environ['NZBOP_UNPACKPASSFILE']):
		print "[ERROR] Der Pfad von [%s] ist nicht vorhanden. Bitte kontrollieren!..." % (os.environ['NZBOP_UNPACKPASSFILE'])
		sys.exit(POSTPROCESS_ERROR)
	if not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
		print "[ERROR] Der Pfad von [%s] ist nicht vorhanden. Bitte kontrollieren!..." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
		sys.exit(POSTPROCESS_ERROR)
	with open(os.environ['NZBPO_LOGGER_FILE_PATH_NAME'], "r") as Log_file_mit_PW:
		with open(os.environ['NZBOP_UNPACKPASSFILE'], "r") as passwort_liste:
			for liste1 in passwort_liste:
				liste = (liste1.rstrip())
				for log1 in Log_file_mit_PW:
					log = (log1.rstrip())
					if liste in log:
						with open(os.environ['NZBPO_PASSWORD_FILE'], "w") as Passwort_only:
							Passwort_only.write(liste)
							print "[INFO] Passwort wurde gefunden und gespeichert: [%s]" % (liste)
	if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
		print "[INFO] Passwort File gefunden wird vortgefahren mit Passwort Umbennenung..."
		with open(os.environ['NZBPO_PASSWORD_FILE'], "r") as Passwort1:
			for Passwort in Passwort1:
				print "[INFO] Das Passwort: [%s] wird eingelesen und verarbeitet...." % (Passwort)
				nzb_without_extension = os.environ['NZBPP_NZBNAME']
				nzb_new_file_path_web_interface = os.environ['NZBPO_NZB_DIR_NEW']
				file_old = "%s.nzb.queued" % (nzb_without_extension)
				newname = "%s {{%s}}.nzb" % (nzb_without_extension, Passwort)
				nzb_new_file_path = os.path.join(nzb_new_file_path_web_interface, newname)
				print "[INFO] NZB File wird umbenannt in: [%s {{%s}}.nzb]" % (nzb_without_extension, Passwort)
				os.rename(os.path.join(NZB_DIR, file_old), os.path.join(nzb_new_file_path_web_interface, newname))
				f = open(nzb_new_file_path)
				file_content = f.read()
				f.close()
				print "[INFO] uploading file [%s]..." % nzb_new_file_path 
				post_data = {
					"apikey": APIKEY,
				}
				myfile = {"Filedata": (newname, file_content)}
				print requests.post(UPLOAD_URL, data=post_data, files=myfile).text
			passwort_liste.close()
		Passwort1.close()
		Log_file_mit_PW.close()
		if (os.environ['NZBPO_PASSWORD_LISTE']) == "ENABLED" and (os.environ['NZBPO_DELETE_NZB']) == "ENABLED" or (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
			print "[INFO] NZB Loeschen oder TEMP loeschen aktiviert"
			if (os.environ['NZBPO_DELETE_NZB']) == "ENABLED":
				print "[INFO] NZB Dateien loeschen aktiviert"
				os_path_isfile = "%s/%s" % (nzb_new_file_path_web_interface, newname)
				if os.path.isfile(os_path_isfile):
					print "[INFO] NZB Dateien gefunden und werden geloescht..."
					try:
						remove = ("%s/%s") % (nzb_new_file_path_web_interface, newname)
						os.remove(remove)
						print "[INFO] NZB Dateien erfolgreich geloescht"
					except OSError, e:
						print ("Error: %s - %s." % (e.filename,e.strerror))
						sys.exit(POSTPROCESS_ERROR)
					if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
						print "[INFO] TEMP Dateien loeschen aktiviert"
						if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
							print "[INFO] TEMP Dateien gefunden und werden geloescht"
							try:
								remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
								remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
								os.remove(remove)
								os.remove(remove1)
								print "[INFO] TEMP Dateien erfolgreich geloescht"
								sys.exit(POSTPROCESS_SUCCESS)
							except OSError, e:
								print ("Error: %s - %s." % (e.filename,e.strerror))
								sys.exit(POSTPROCESS_ERROR)
						elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
							try:
								remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
								os.remove(remove1)
								print "[INFO] TEMP Dateien erfolgreich geloescht"
								sys.exit(POSTPROCESS_SUCCESS)
							except OSError, e:
								print ("Error: %s - %s." % (e.filename,e.strerror))
								sys.exit(POSTPROCESS_ERROR)
						elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
							print "[INFO] TEMP Dateien gefunden und werden geloescht"
							try:
								remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
								os.remove(remove)
								print "[INFO] TEMP Dateien erfolgreich geloescht"
								sys.exit(POSTPROCESS_SUCCESS)
							except OSError, e:
								print ("Error: %s - %s." % (e.filename,e.strerror))
								sys.exit(POSTPROCESS_ERROR)
						elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
							print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
							print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
							sys.exit(POSTPROCESS_SUCCESS)
						else:
							print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
							sys.exit(POSTPROCESS_ERROR)
					elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
						print "[INFO] TEMP Dateien loeschen deaktiviert"
						sys.exit(POSTPROCESS_SUCCESS)
				elif not os.path.isfile(os_path_isfile):
					print "[WARNING] Keine NZB Dateien gefunden....."
					if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
						print "[INFO] TEMP Dateien loeschen aktiviert"
						if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
							print "[INFO] TEMP Dateien gefunden und werden geloescht"
							try:
								remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
								remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
								os.remove(remove)
								os.remove(remove1)
								print "[INFO] TEMP Dateien erfolgreich geloescht"
								sys.exit(POSTPROCESS_SUCCESS)
							except OSError, e:
								print ("Error: %s - %s." % (e.filename,e.strerror))
								sys.exit(POSTPROCESS_ERROR)
						elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
							try:
								remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
								os.remove(remove1)
								print "[INFO] TEMP Dateien erfolgreich geloescht"
								sys.exit(POSTPROCESS_SUCCESS)
							except OSError, e:
								print ("Error: %s - %s." % (e.filename,e.strerror))
								sys.exit(POSTPROCESS_ERROR)
						elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
							print "[INFO] TEMP Dateien gefunden und werden geloescht"
							try:
								remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
								os.remove(remove)
								print "[INFO] TEMP Dateien erfolgreich geloescht"
								sys.exit(POSTPROCESS_SUCCESS)
							except OSError, e:
								print ("Error: %s - %s." % (e.filename,e.strerror))
								sys.exit(POSTPROCESS_ERROR)
						elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
							print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
							print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
							sys.exit(POSTPROCESS_SUCCESS)
						else:
							print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
							sys.exit(POSTPROCESS_ERROR)
					elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
						print "[INFO] TEMP Dateien loeschen deaktiviert"
						sys.exit(POSTPROCESS_SUCCESS)
					else:
						print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... TEMP Loeschung [%s] FEHLER!!!" % (os.environ['NZBPO_DELETE_TEMP'])
						sys.exit(POSTPROCESS_ERROR)
				else:
					print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Ueberpruefung der Pfade Fehlerhaft: [%s] - [%s]" % (os_path_isfile, (os.environ['NZBPO_NZB_DIR_NEW']))
					sys.exit(POSTPROCESS_ERROR)
			elif (os.environ['NZBPO_DELETE_NZB']) == "DISABLED":
				print "[INFO] NZB Dateien loeschen deaktiviert"
				if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
					print "[INFO] TEMP Dateien gefunden und werden geloescht"
					if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
						print "[INFO] TEMP Dateien gefunden und werden geloescht"
						try:
							remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
							remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
							os.remove(remove)
							os.remove(remove1)
							print "[INFO] TEMP Dateien erfolgreich geloescht"
							sys.exit(POSTPROCESS_SUCCESS)
						except OSError, e:
							print ("Error: %s - %s." % (e.filename,e.strerror))
							sys.exit(POSTPROCESS_ERROR)
					elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
						try:
							remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
							os.remove(remove1)
							print "[INFO] TEMP Dateien erfolgreich geloescht"
							sys.exit(POSTPROCESS_SUCCESS)
						except OSError, e:
							print ("Error: %s - %s." % (e.filename,e.strerror))
							sys.exit(POSTPROCESS_ERROR)
					elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
						print "[INFO] TEMP Dateien gefunden und werden geloescht"
						try:
							remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
							os.remove(remove)
							print "[INFO] TEMP Dateien erfolgreich geloescht"
							sys.exit(POSTPROCESS_SUCCESS)
						except OSError, e:
							print ("Error: %s - %s." % (e.filename,e.strerror))
							sys.exit(POSTPROCESS_ERROR)
					elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
						print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
						print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
						sys.exit(POSTPROCESS_SUCCESS)
					else:
						print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
						sys.exit(POSTPROCESS_ERROR)
				elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
					print "[INFO] TEMP Dateien loeschen deaktiviert"
					sys.exit(POSTPROCESS_SUCCESS)
				else:
					print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Loeschen Fehler TEMP: [%s]" % (os.environ['NZBPO_DELETE_TEMP'])
					sys.exit(POSTPROCESS_ERROR)
			else:
				print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Loeschen Fehler NZB: [%s]" % (os.environ['NZBPO_DELETE_NZB'])
				sys.exit(POSTPROCESS_ERROR)
		elif (os.environ['NZBPO_PASSWORD_LISTE']) == "ENABLED" and (os.environ['NZBPO_DELETE_NZB']) == "DISABLED" or (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
			print "[INFO] NZB Loeschen und TEMP loeschen deaktiviert"
			sys.exit(POSTPROCESS_SUCCESS)
		else:
			print "[ERROR] Fehler bei der Ausfuehrung des Skripts!!.... Passwort_liste: [%s] - Loeschen NZB: [%s] - Loeschen TEMP [%s]" % ((os.environ['NZBPO_PASSWORD_LISTE']), (os.environ['NZBPO_DELETE_NZB']), (os.environ['NZBPO_DELETE_TEMP']))
			sys.exit(POSTPROCESS_ERROR)
	elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
		print "[INFO] Kein Passwort File gefunden: [%s] wird vortgefahren ohne Passwort Umbennenung..." % (os.environ['NZBPO_PASSWORD_FILE'])
		nzb_filename = os.environ['NZBPP_NZBFILENAME']
		nzb_filepath = os.path.join(NZB_DIR, nzb_filename)
	 
		f = open(nzb_filepath + '.queued', 'rb')
		file_content = f.read()
		f.close()
 
		print "[INFO] uploading file %s..." % nzb_filepath
		 
		post_data = {
			"apikey": APIKEY,
		}
		myfile = {"Filedata": (nzb_filename, file_content)}
		print requests.post(UPLOAD_URL, data=post_data, files=myfile).text
		if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
			print "[INFO] TEMP Dateien loeschen aktiviert"
			if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
				print "[INFO] TEMP Dateien gefunden und werden geloescht"
				try:
					remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
					remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
					os.remove(remove)
					os.remove(remove1)
					print "[INFO] TEMP Dateien erfolgreich geloescht"
					sys.exit(POSTPROCESS_SUCCESS)
				except OSError, e:
					print ("Error: %s - %s." % (e.filename,e.strerror))
					sys.exit(POSTPROCESS_ERROR)
			elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
				try:
					remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
					os.remove(remove1)
					print "[INFO] TEMP Dateien erfolgreich geloescht"
					sys.exit(POSTPROCESS_SUCCESS)
				except OSError, e:
					print ("Error: %s - %s." % (e.filename,e.strerror))
					sys.exit(POSTPROCESS_ERROR)
			elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
				print "[INFO] TEMP Dateien gefunden und werden geloescht"
				try:
					remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
					os.remove(remove)
					print "[INFO] TEMP Dateien erfolgreich geloescht"
					sys.exit(POSTPROCESS_SUCCESS)
				except OSError, e:
					print ("Error: %s - %s." % (e.filename,e.strerror))
					sys.exit(POSTPROCESS_ERROR)
			elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
				print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
				print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
				sys.exit(POSTPROCESS_SUCCESS)
			else:
				print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
				sys.exit(POSTPROCESS_ERROR)
		elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
			print "[INFO] TEMP Dateien loeschen deaktiviert"
			sys.exit(POSTPROCESS_SUCCESS)
		
elif (os.environ['NZBPO_PASSWORD_LISTE']) == "DISABLED" or (os.environ['NZBPO_PASSWORD']) == "DISABLED" and ('NZBPR_*Unpack:Password' in os.environ):
	print "[INFO] Passwort: [%s] oder Passwort_Liste: [%s] deaktiviert, aber Passwort in Web Ui gegeben: [%s]" % ((os.environ['NZBPO_PASSWORD']) ,(os.environ['NZBPO_PASSWORD_LISTE']), ('NZBPR_*Unpack:Password' in os.environ))
	nzb_filename = os.environ['NZBPP_NZBFILENAME']
	nzb_filepath = os.path.join(NZB_DIR, nzb_filename)
 
	f = open(nzb_filepath + '.queued', 'rb')
	file_content = f.read()
	f.close()
 
	print "[INFO] uploading file %s..." % nzb_filepath
	 
	post_data = {
		"apikey": APIKEY,
	}
	myfile = {"Filedata": (nzb_filename, file_content)}
	print requests.post(UPLOAD_URL, data=post_data, files=myfile).text
	if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
		print "[INFO] TEMP Dateien loeschen aktiviert"
		if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] TEMP Dateien gefunden und werden geloescht"
			try:
				remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
				remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
				os.remove(remove)
				os.remove(remove1)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_SUCCESS)
			except OSError, e:
				print ("Error: %s - %s." % (e.filename,e.strerror))
				sys.exit(POSTPROCESS_ERROR)
		elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			try:
				remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
				os.remove(remove1)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_SUCCESS)
			except OSError, e:
				print ("Error: %s - %s." % (e.filename,e.strerror))
				sys.exit(POSTPROCESS_ERROR)
		elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
			print "[INFO] TEMP Dateien gefunden und werden geloescht"
			try:
				remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
				os.remove(remove)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_SUCCESS)
			except OSError, e:
				print ("Error: %s - %s." % (e.filename,e.strerror))
				sys.exit(POSTPROCESS_ERROR)
		elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
			print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
			sys.exit(POSTPROCESS_SUCCESS)
		else:
			print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
			sys.exit(POSTPROCESS_ERROR)
	elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
		print "[INFO] TEMP Dateien loeschen deaktiviert"
		sys.exit(POSTPROCESS_SUCCESS)

elif (os.environ['NZBPO_PASSWORD_LISTE']) == "DISABLED" or (os.environ['NZBPO_PASSWORD']) == "DISABLED" and not ('NZBPR_*Unpack:Password' in os.environ):
	print "[INFO] Passwort: [%s] oder Passwort_Liste: [%s] deaktiviert, aber Passwort in Web Ui nicht gegeben: [%s]" % ((os.environ['NZBPO_PASSWORD']) ,(os.environ['NZBPO_PASSWORD_LISTE']), ('NZBPR_*Unpack:Password' in os.environ))
	nzb_filename = os.environ['NZBPP_NZBFILENAME']
	nzb_filepath = os.path.join(NZB_DIR, nzb_filename)
 
	f = open(nzb_filepath + '.queued', 'rb')
	file_content = f.read()
	f.close()
 
	print "[INFO] uploading file %s..." % nzb_filepath
	 
	post_data = {
		"apikey": APIKEY,
	}
	myfile = {"Filedata": (nzb_filename, file_content)}
	print requests.post(UPLOAD_URL, data=post_data, files=myfile).text
	if (os.environ['NZBPO_DELETE_TEMP']) == "ENABLED":
		print "[INFO] TEMP Dateien loeschen aktiviert"
		if os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] TEMP Dateien gefunden und werden geloescht"
			try:
				remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
				remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
				os.remove(remove)
				os.remove(remove1)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_SUCCESS)
			except OSError, e:
				print ("Error: %s - %s." % (e.filename,e.strerror))
				sys.exit(POSTPROCESS_ERROR)
		elif os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			try:
				remove1 = ("%s") % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
				os.remove(remove1)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_SUCCESS)
			except OSError, e:
				print ("Error: %s - %s." % (e.filename,e.strerror))
				sys.exit(POSTPROCESS_ERROR)
		elif os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']):
			print "[INFO] TEMP Dateien gefunden und werden geloescht"
			try:
				remove = ("%s") % (os.environ['NZBPO_PASSWORD_FILE'])
				os.remove(remove)
				print "[INFO] TEMP Dateien erfolgreich geloescht"
				sys.exit(POSTPROCESS_SUCCESS)
			except OSError, e:
				print ("Error: %s - %s." % (e.filename,e.strerror))
				sys.exit(POSTPROCESS_ERROR)
		elif not os.path.isfile(os.environ['NZBPO_PASSWORD_FILE']) and not os.path.isfile(os.environ['NZBPO_LOGGER_FILE_PATH_NAME']):
			print "[INFO] Keine Passwort Datei gefunden zum Loeschen: [%s]...." % (os.environ['NZBPO_PASSWORD_FILE'])
			print "[INFO] Keine Datei von Logger.py gefunden zum loeschen: [%s]...." % (os.environ['NZBPO_LOGGER_FILE_PATH_NAME'])
			sys.exit(POSTPROCESS_SUCCESS)
		else:
			print "[WARNING] Fehler bei der ausfuehrung des Skripts bezueglich des Loeschens....."
			sys.exit(POSTPROCESS_ERROR)
	elif (os.environ['NZBPO_DELETE_TEMP']) == "DISABLED":
		print "[INFO] TEMP Dateien loeschen deaktiviert"
		sys.exit(POSTPROCESS_SUCCESS)

else:
	print "[ERROR] Fehler bei der Ausfuehrung des Skripts!! [Passwort:[%s] - Passwort_WEB_UI:[%s]]...." % ((os.environ['NZBPO_PASSWORD']), (os.environ['NZBPR_*Unpack:Password']))
	sys.exit(POSTPROCESS_ERROR)