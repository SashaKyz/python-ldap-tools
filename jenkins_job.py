#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import io

commit = 'commit'
changed = '+'
with io.open('file.txt') as file:
    for line in file:
        if commit in line:
            print(line, end='')
        if changed in line:
            print(line, end='')
