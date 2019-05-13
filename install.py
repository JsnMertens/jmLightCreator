#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Install jmLightCreator. """

import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import logging

logger = logging.getLogger(__name__)


def onMayaDroppedPythonFile(*args, **kwargs):
    """ Dragging and dropping one into the scene automatically executes it. """
    # Get icon
    icon_path = os.path.join(os.path.dirname(__file__), 'src', 'resources', 'icons', 'logo_jmLightCreator.png')
    icon_path = os.path.normpath(icon_path)

    # Check if icon exist
    if not os.path.exists(icon_path):
        logger.error("Cannot find %s" % icon_path)
        return None

    # Check PYTHONPATH
    try:
        import jmLightCreator
    except ImportError:
        logger.error("'jmLightCreator' not found in PYTHON_PATH")
        return None

    # Create Shelf
    command  = "import jmLightCreator;"
    command += "jmLightCreator.main();"
    shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = cmds.tabLayout(shelf, query=True, selectTab=True)

    cmds.shelfButton(
        command=command,
        annotation='jmLightCreator',
        sourceType='Python',
        image=icon_path,
        image1=icon_path,
        parent=parent )
