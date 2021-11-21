#!/usr/bin/env python

import sys, re, tifffile
import numpy as np
from pathlib import Path

def stem (filename):
    name = Path(filename).stem
    name = re.sub('\.ome$', '', name, flags = re.IGNORECASE)
    return name

def with_suffix (filename, suffix):
    name = stem(filename)
    if name == name + suffix:
        raise Exception('Empty suffix. May overwrite the original file. Exiting.')
    return name + suffix
