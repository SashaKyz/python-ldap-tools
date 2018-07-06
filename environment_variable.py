#!/usr/bin/env python

import os
import re

for root, dirs, files in os.walk(".."):
    for file in files:
        if (((file.find("docker-compose")!=-1) and (file.endswith(".yml")))or(file=='.env')):
            appl=re.search("roles/(apptier/){,1}([\w,-]*)",root)
            #appl=re.search("roles(/apptier)",root)
            #print("Scan file: ",os.path.join(root, file),"Appplication: ",appl.group(2))
            if appl:
                print("Environment variable for: ",appl.group(2))
                shakes = open(os.path.join(root, file), "r")
                for line in shakes:
                    sub_line=re.match("^\s*-\s(\w*)=.*",line)
                    if sub_line:
                        print (sub_line.group(1))