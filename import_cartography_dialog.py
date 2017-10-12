# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               SEC4QGIS v1.0.4
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

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QSettings
import datetime
import sys
import os
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'import_cartography_dialog.ui'))
class ImportCartographyDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ImportCartographyDialog, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit_file_name.textChanged.connect(self.lineEdit_file_name_text_changed)
        self.pushButton_select.clicked.connect(self.select_files_to_import)
        self.radioButton_new_layer.clicked.connect(self.new_layer)
        self.radioButton_existing_layers.clicked.connect(self.existing_layer)
    def lineEdit_file_name_text_changed(self, text):
        if text:  
            self.pushButton_accept.setEnabled(True)
        else:
            self.pushButton_accept.setEnabled(False)
    def select_files_to_import(self):
        if QSettings().value('SEC4QGIS/last_folder_import') is None:
            last_folder_import = ""
        else:
            last_folder_import = QSettings().value('SEC4QGIS/last_folder_import')
        file_names = QFileDialog.getOpenFileNames(self, _translate("import_cartography", "File to import:"), last_folder_import, "*.dxf;*.gml;*.shp;*.zip")
        if len(file_names)>0:
            last_folder_import = os.path.split(file_names[0])[0]
            QSettings().setValue('SEC4QGIS/last_folder_import', last_folder_import)
        files_names_string = ""
        for fichero in file_names:
            files_names_string += '"'+fichero+'" '
        self.lineEdit_file_name.setText(files_names_string)
    def new_layer(self):
        self.lineEdit_new_layer.setEnabled(True)
        self.comboBox_crs.setEnabled(True)
        self.comboBox_existing_layers.setEnabled(False)
    def existing_layer(self):
        self.lineEdit_new_layer.setEnabled(False)
        self.comboBox_crs.setEnabled(False)
        self.comboBox_existing_layers.setEnabled(True)
###########################################################################################################################
###########################################################################################################################
def _translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)
