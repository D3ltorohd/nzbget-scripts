#!/usr/bin/env python

import git
import sys
import os
import gzip
import requests
import re
import shutil
import stat
 
DIR_NAME = (os.path.dirname(os.path.abspath("/volume1/01_public/nzb2wizznab.py")))
PIKO = (os.path.join(DIR_NAME, 'nzbget-scripts'))
REMOTE_URL = "https://github.com/cytec/nzbget-scripts"

repo = git.Repo.init(REMOTE_URL)
origin = repo.create_remote('origin', PIKO)
origin.fetch()           
repo.head.ref.set_tracking_branch(origin.refs.master)
origin.pull()

#repo = git.Repo("https://github.com/cytec/nzbget-scripts", PIKO)
#print head.name
#print repo.commits()

#new_repo = Repo.clone_from("https://github.com/cytec/nzbget-scripts", "./TEST")


#BASE_PATH = os.path.dirname(os.path.abspath("/volume1/01_public/nzb2wizznab.py"))
#PIKO = (os.path.join(BASE_PATH, 'nzbget-scripts'))
#git.clone("https://github.com/cytec/nzbget-scripts", PIKO)
#Pruefung = (os.path.join(PIKO, 'PostProcessing', 'nzb2wizznab.py'))

#for dirpath, dirnames, filenames in os.walk(PIKO):
#    for filename in filenames:
#        path = os.path.join(dirpath, filename)
#        print path
#        print "---------------------------"
        #os.chmod(path, 0o777)
#tests machen

#dir_nzbget = "/volume1/01_public/Smallville.S05.COMPLETE.German.Dubbed.DL.720p.HDDVD.x264-TVS{{usenet-4all.info_T$I11-a49J%W4H$$b%)d2cLSeUNd07NV}}.nzb"
#name_nzbget = "Smallville.S05.COMPLETE.German.Dubbed.DL.720p.HDDVD.x264-TVS"
#NZB_DIR = "/volume1/01_public/"
#NEW = (os.path.basename(dir_nzbget))
#TEST = (os.path.join(NZB_DIR, name_nzbget))
#print TEST
#fwp = "Smallville.S05.COMPLETE.German.Dubbed.DL.720p.HDDVD.x264-TVS {{usenet-4all.info_T$I11-a49J%W4H$$b%)d2cLSeUNd07NV}}.nzb"

#p = re.match( r'^.*?\{\{[ ]?(.*?)[ ]?\}\}', dir_nzbget)
#f = re.sub( r'[ .]?{\{[ ]?(.*?)[ ]?\}\}', '', dir_nzbget)


#TEST = (os.listdir(NZB_DIR))
#for liste in TEST:
#	if (name_nzbget) in (liste):
#		print "ja"
		
	
	

