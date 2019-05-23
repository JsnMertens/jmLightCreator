#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
jmLightCreator is a free tool in python I have written for easily creating lights in Maya with a templated name.
Feel free to use it in your own projects or in production. (Optimized for MtoA)
"""

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QWidget
from maya import OpenMayaUI as omui
from shiboken2 import getCppPointer
from functools import partial
import pymel.core as pm
import logging
import os
import sys

__author__      = 'Jason Mertens'
__copyright__   = 'Copyright (c) 2019 Jason Mertens'
__version__     = '1.1'
__license__     = 'MIT'
__email__       = 'mertens.jas@gmail.com'

_mainWindow = None
_logger = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from jmLightCreatorUI import Ui_widget_root


class JMLightCreator(MayaQWidgetDockableMixin, QWidget, Ui_widget_root):
    """ LightCreator Window. """
    # Constants
    PREFERRED_LAYOUT = "vertical"

    lgt_type_default = ["pointLight", "spotLight", "areaLight", "directionalLight"]
    lgt_type_arnold = ["aiAreaLight", "aiSkyDomeLight"]
    lgt_type = lgt_type_default + lgt_type_arnold

    lgt_function = ["key", "fil", "rim", "kck", "bnc", "spl"]
    lgt_suffix = ["POIT", "SPTL", "ARLT", "DIRL", "AIRL", "AISD"]

    lgt_root_grp = "light_C_001_GRUP"
    template_name = "{BASENAME}_{FUNCTION}_{AXE}_{INDEX}_{TYPE}"
    template_regex = r"^[a-zA-Z0-9]+_[a-z]{3}_[A-Z]_[0-9]{3}_[A-Z]{4}$"

    # Icons
    getIcon = lambda icon_name : QtGui.QIcon(os.path.join(PROJECT_DIR, "resources", "icons", icon_name))
    icon_illuminated_off = getIcon("icon_lightbulb_off.png")
    icon_illuminated_on = getIcon("icon_lightbulb_on.png")
    icon_select_off = getIcon("icon_select_off.png")
    icon_select_on = getIcon("icon_select_on.png")
    icon_spotlight = getIcon("spotLight.svg")
    icon_pointLight = getIcon("pointLight.svg")
    icon_directionalLight = getIcon("directionalLight.svg")
    icon_aiSkyDomeLight = getIcon("aiSkyDomeLight.svg")
    icon_aiAreaLight = getIcon("aiAreaLight.svg")
    default_stylesheet = "QPushButton::checked{background-color:rgb(97,97,97); color:rgb(255,255,255); border:none}"

    def __init__(self, parent=None):
        super(JMLightCreator, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)

        self.pushButton_illuminate.setIcon(self.icon_illuminated_on)
        self.pushButton_selected.setIcon(self.icon_select_off)
        self.pushButton_spotLight.setIcon(self.icon_spotlight)
        self.pushButton_pointLight.setIcon(self.icon_pointLight)
        self.pushButton_directionalLight.setIcon(self.icon_directionalLight)
        self.pushButton_aiSkyDomeLight.setIcon(self.icon_aiSkyDomeLight)
        self.pushButton_aiAreaLight.setIcon(self.icon_aiAreaLight)

        # Connect Methods to UI
        self.pushButton_illuminate.clicked.connect(self.__illuminateCSS)
        self.pushButton_selected.clicked.connect(self.__selectCSS)
        self.pushButton_spotLight.clicked.connect(partial(self.createLight, "spotLight"))
        self.pushButton_directionalLight.clicked.connect(partial(self.createLight, "directionalLight"))
        self.pushButton_pointLight.clicked.connect(partial(self.createLight, "pointLight"))
        self.pushButton_aiAreaLight.clicked.connect(partial(self.createLight, "aiAreaLight"))
        self.pushButton_aiSkyDomeLight.clicked.connect(partial(self.createLight, "aiSkyDomeLight"))
        self.comboBox_function.addItems(self.lgt_function)

        self.switchLayout(self.PREFERRED_LAYOUT)
        self.__selectCSS()

    def contextMenuEvent(self, event):
        """ Popup RMB menu. """
        self.menu = QtWidgets.QMenu(self)

        grid_layout_rmb = QtWidgets.QAction("Switch to Grid Layout", self)
        grid_layout_rmb.triggered.connect(partial(self.switchLayout, "grid"))
        self.menu.addAction(grid_layout_rmb)

        horizontal_layout_rmb = QtWidgets.QAction("Switch to Horizontal Layout", self)
        horizontal_layout_rmb.triggered.connect(partial(self.switchLayout, "horizontal"))
        self.menu.addAction(horizontal_layout_rmb)

        vertical_layout_rmb = QtWidgets.QAction("Switch to Vertical Layout", self)
        vertical_layout_rmb.triggered.connect(partial(self.switchLayout, "vertical"))
        self.menu.addAction(vertical_layout_rmb)

        self.menu.popup(QtGui.QCursor.pos())

    def switchLayout(self, layout):
        """ Switch btw Horizontal, vertical and grid layout. """
        if layout == "grid":
            self.gridLayout_button.addWidget(self.pushButton_illuminate, 0, 0)
            self.gridLayout_button.addWidget(self.lineEdit_basename, 0, 1)
            self.gridLayout_button.addWidget(self.comboBox_function, 0, 2, 1, 1)
            self.gridLayout_button.addWidget(self.pushButton_selected, 1, 0)
            self.gridLayout_button.addWidget(self.pushButton_spotLight, 1, 1)
            self.gridLayout_button.addWidget(self.pushButton_directionalLight, 1, 2)
            self.gridLayout_button.addWidget(self.pushButton_pointLight, 2, 0)
            self.gridLayout_button.addWidget(self.pushButton_aiAreaLight, 2, 1)
            self.gridLayout_button.addWidget(self.pushButton_aiSkyDomeLight, 2, 2)

        elif layout == "horizontal":
            self.gridLayout_button.addWidget(self.pushButton_illuminate, 0, 0)
            self.gridLayout_button.addWidget(self.pushButton_selected, 0, 1)
            self.gridLayout_button.addWidget(self.lineEdit_basename, 0, 2)
            self.gridLayout_button.addWidget(self.comboBox_function, 0, 3)
            self.gridLayout_button.addWidget(self.pushButton_spotLight, 0, 4)
            self.gridLayout_button.addWidget(self.pushButton_directionalLight, 0, 5)
            self.gridLayout_button.addWidget(self.pushButton_pointLight, 0, 6)
            self.gridLayout_button.addWidget(self.pushButton_aiAreaLight, 0, 7)
            self.gridLayout_button.addWidget(self.pushButton_aiSkyDomeLight, 0, 8)

        elif layout == "vertical":
            self.gridLayout_button.addWidget(self.pushButton_illuminate, 0, 0)
            self.gridLayout_button.addWidget(self.pushButton_selected, 1, 0)
            self.gridLayout_button.addWidget(self.lineEdit_basename, 2, 0)
            self.gridLayout_button.addWidget(self.comboBox_function, 3, 0)
            self.gridLayout_button.addWidget(self.pushButton_spotLight, 4, 0)
            self.gridLayout_button.addWidget(self.pushButton_directionalLight, 5, 0)
            self.gridLayout_button.addWidget(self.pushButton_pointLight, 6, 0)
            self.gridLayout_button.addWidget(self.pushButton_aiAreaLight, 7, 0)
            self.gridLayout_button.addWidget(self.pushButton_aiSkyDomeLight, 8, 0)

        else:
            _logger.error("Argument Error")
            return None

    def _wrapperUndoChunck(function):
        """ Create an undo Chunk and wrap it. """
        def wrapper(self, *args, **kwargs):
            try:
                pm.undoInfo(openChunk=True)
                function(self, *args, **kwargs)
            finally:
                pm.undoInfo(closeChunk=True)

        return wrapper

    @_wrapperUndoChunck
    def createLight(self, light_type):
        """ Create light. """
        # Check input
        if light_type not in self.lgt_type:
            _logger.error("Only accepted : %s" % self.lgt_type)
            return None

        # Check if MtoA is load if you try to create an Arnold light
        if light_type in self.lgt_type_arnold and not pm.pluginInfo("mtoa", q=True, loaded=True):
            _logger.warning("MtoA is not loaded.")
            return None

        out = []
        is_checked = self.pushButton_selected.isChecked()
        illuminate = self.pushButton_illuminate.isChecked()
        selected = pm.selected()

        # Check selection
        if not selected and is_checked:
            _logger.warning("Nothing selected.")
            return None

        lenght = len(selected) if is_checked else 1
        for i in range(lenght):
            # Create light
            light_shape = pm.shadingNode(light_type, asLight=True)
            light_transform = light_shape if light_shape.type() == "transform" else light_shape.getParent()

            # Break links
            if illuminate:
                output_ = pm.PyNode("%s.instObjGroups[0]" % light_transform)
                input_ = pm.PyNode(pm.connectionInfo(output_, dfs=True)[0])
                output_ // input_

            # Get suffix and function
            suffix = self.lgt_suffix[self.lgt_type.index(light_type)]
            function = self.comboBox_function.currentText()

            # Get basename
            basename = None
            if is_checked:
                basename = selected[i].split("_")[0]
            else:
                basename = self.lineEdit_basename.text()
                if not basename:
                    basename = light_type

            # Rename
            index = 1
            new_name = self.template_name.format(BASENAME=basename, FUNCTION=function, AXE="C", INDEX="%03d" % index, TYPE=suffix)
            while pm.objExists(new_name):
                index += 1
                new_name = self.template_name.format(BASENAME=basename, FUNCTION=function, AXE="C", INDEX="%03d" % index, TYPE=suffix)

            light_transform.rename(new_name)

            # Put light in group
            root_grp = pm.PyNode(self.lgt_root_grp) if pm.objExists(self.lgt_root_grp) else pm.group(n=self.lgt_root_grp, em=True)
            pm.parent(light_transform, root_grp)

            out.append(light_transform)

        pm.select(out)
        self.lineEdit_basename.clearFocus()
        _logger.info("Light(s) successfully created.")
        return light_transform

    def __illuminateCSS(self):
        """ Illuminate look. """
        if self.pushButton_illuminate.isChecked():
            self.pushButton_illuminate.setIcon(self.icon_illuminated_off)
            self.pushButton_illuminate.setStyleSheet(self.default_stylesheet)

        else:
            self.pushButton_illuminate.setIcon(self.icon_illuminated_on)
            self.pushButton_illuminate.setStyleSheet(self.default_stylesheet)

    def __selectCSS(self):
        """ Select look. """
        if self.pushButton_selected.isChecked():
            self.pushButton_selected.setIcon(self.icon_select_on)
            self.pushButton_selected.setStyleSheet(self.default_stylesheet)
            self.lineEdit_basename.setReadOnly(True)

        else:
            self.pushButton_selected.setIcon(self.icon_select_off)
            self.pushButton_selected.setStyleSheet(self.default_stylesheet)
            self.lineEdit_basename.setReadOnly(False)


def saveWindowState(editor, optionVar):
    windowState = editor.showRepr()
    cmds.optionVar(sv=(optionVar, windowState))

def mainWindowClosed():
    """ Hook up callback when the main window is closed. """
    global _mainWindow

    if _mainWindow:
        _mainWindow = None

def mainWindowChanged():
    """ Hook up callback when the main window is moved and resized. """
    global _mainWindow
    saveWindowState(_mainWindow, __name__ + "State")

def main(restore=False):
    """ Show main Window. """
    global _mainWindow

    if not restore:
        control = __name__ + "WorkspaceControl"
        if pm.workspaceControl(control, q=True, exists=True) and _mainWindow is None:
            pm.workspaceControl(control, e=True, close=True)
            pm.deleteUI(control)

    if restore:
        parent = omui.MQtUtil.getCurrentParent()

    if _mainWindow is None:
        _mainWindow = JMLightCreator()
        _mainWindow.setObjectName(__name__)

    if restore:
        mixinPtr = omui.MQtUtil.findControl(_mainWindow.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(long(mixinPtr), long(parent))

    else:
        _mainWindow.show(dockable=True,
            uiScript='import jmLightCreator\njmLightCreator.main(restore=True)',
            closeCallback='import jmLightCreator\njmLightCreator.mainWindowClosed()' )

    _mainWindow.setWindowTitle(__name__)
    return _mainWindow
