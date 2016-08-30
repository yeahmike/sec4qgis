# -*- coding: utf-8 -*-
"""
/***************************************************************************
                               SEC4QGIS v1.0.2
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
import os
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'export_gml_dialog.ui'))
class ExportGmlDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ExportGmlDialog, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit_ouput_file.textChanged.connect(self.lineEdit_text_changed)
        self.pushButton_select.clicked.connect(self.file_select_export_gml)
    def lineEdit_text_changed(self, text):
        if text:  
            self.pushButton_accept.setEnabled(True)
        else:
            self.pushButton_accept.setEnabled(False)
    def file_select_export_gml(self):
        if QSettings().value('SEC4QGIS/last_folder_export') is None:
            last_folder_export = ""
        else:
            last_folder_export = QSettings().value('SEC4QGIS/last_folder_export')
        file_name = QFileDialog.getSaveFileName(self, _translate("export_gml", "Ouput GML file:"), last_folder_export, "*.gml")
        self.lineEdit_ouput_file.setText(file_name)
        if len(file_name)>0:
            last_folder_export = os.path.split(file_name)[0]
            QSettings().setValue('SEC4QGIS/last_folder_export', last_folder_export)
###########################################################################################################################
###########################################################################################################################
def _translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)
