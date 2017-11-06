# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               SEC4QGIS v1.0.5
                             -------------------
                               (A QGIS plugin)
                             -------------------
 Funciones relativas a la Sede Electrónica del Catastro (SEC) para QGIS.
 Functions related to Spanish Cadastral Electronic Site (SEC) for QGIS.
                             -------------------
        begin                : 2016-06-30
        copyright            : (C) 2016 by Andrés V. O.
        website              : http://sec4qgis.tk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import datetime
import hashlib
import os
import codecs
import re
import zipfile
import shutil
from random import randint
from options_dialog import OptionsDialog
###########################################################################################################################
###########################################################################################################################
def run_script(self):
    """ Put your code here and remove the pass statement"""
    self.options_dialog = OptionsDialog()
    if QSettings().value('SEC4QGIS/default_import_to_new_layer') is None:
        default_import_to_new_layer = 0
    else:
        default_import_to_new_layer = QSettings().value('SEC4QGIS/default_import_to_new_layer')
    if default_import_to_new_layer == 1:
        self.options_dialog.radioButton_new_layer.setChecked(True)
    else: 
        self.options_dialog.radioButton_active_layer.setChecked(True)
    for valid_sec_crs in sorted(self.valid_sec_crs_list.keys()):
        self.options_dialog.comboBox_crs.addItem(valid_sec_crs+" = "+self.valid_sec_crs_list[valid_sec_crs])
    if QSettings().value('SEC4QGIS/default_crs') is None:
        default_crs = 1
    else:
        default_crs = QSettings().value('SEC4QGIS/default_crs')
    self.options_dialog.comboBox_crs.setCurrentIndex(default_crs)
    self.options_dialog.show()
    result = self.options_dialog.exec_()
    if not result:
        return 
    selected_crs = self.options_dialog.comboBox_crs.currentIndex()
    QSettings().setValue('SEC4QGIS/default_crs', selected_crs)
    if self.options_dialog.radioButton_new_layer.isChecked():
        QSettings().setValue('SEC4QGIS/default_import_to_new_layer', 1)
    else: 
        QSettings().setValue('SEC4QGIS/default_import_to_new_layer', 0)
    self.set_global_options()
###########################################################################################################################
###########################################################################################################################
def _translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)
