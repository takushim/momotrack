#!/usr/bin/env python

import textwrap
from datetime import datetime
from logging import getLogger
from plugin.particle import SPT
from plugin.base import PluginBase

logger = getLogger(__name__)

plugin_name = 'Particle Tracking with Gaussian Fit'
class_name = 'SPT_Gfit'
priority = 20

class SPT_Gfit (SPT):
    def __init__ (self):
        super().__init__()
        self.plugin_name = str(plugin_name)

    def init_widgets (self, vlayout):
        super().init_widgets(vlayout)
    def help_message (self):
        message = textwrap.dedent('''\
        <b>Single-particle tracking with Gaussian fitting</b>
        <ul>
        <li> See the original plugin.</li>
        </ul>
        ''')
        return message
