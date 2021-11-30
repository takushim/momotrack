#!/usr/bin/env python

import sys, re
import numpy as np
from pathlib import Path

plugin_name = 'Dummy'
priority = 100
record_suffix = '_track.json'

def with_suffix (filename, suffix = record_suffix):
    name = Path(filename).stem
    name = re.sub('\.ome$', '', name, flags = re.IGNORECASE)
    if name == name + suffix:
        raise Exception('Empty suffix. May overwrite the original file. Exiting.')
    return name + suffix
