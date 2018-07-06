#!/usr/bin/env python

import os
import re

for root, dirs, files in os.walk(".."):
    for file in files:
        if ((file.find("docker-compose")!=-1) and (file.endswith(".yml"))):
            application=re.match("roles/([\w,-]*)",os.path.join(root, file))
            if application:
                print("Environment variable for: ",application.group(1))
                shakes = open(os.path.join(root, file), "r")
                for line in shakes:
                    sub_line=re.match("^\s*-\s(\w*)=.*",line)
                    if sub_line:
                        print (sub_line.group(1))