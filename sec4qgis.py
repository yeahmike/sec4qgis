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
import resources
import os.path
import codecs
import re
import subprocess
import ConfigParser
import shutil
import import_cartography
import export_gml
import options
class Sec4Qgis:
    """QGIS Plugin Implementation."""
###########################################################################################################################
###########################################################################################################################
    def __init__(self, iface):
        """Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'sec4qgis_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.valid_sec_crs_list = dict([ 
                ('EPSG:25829', self.tr('Western Spanish peninsula')), 
                ('EPSG:25830', self.tr('Central Spanish peninsula, Ceuta, and Melilla')), 
                ('EPSG:25831', self.tr('Eastern Spanish peninsula and Balearic Islands')), 
                ('EPSG:32628', self.tr('Canary Islands')),
            ])
        self.field_localId = 'localId'
        self.field_nameSpace = 'nameSpace'
        self.valid_dgc_nameSpace_list = ['DGC', 'D']
        self.import_cartography_dialog = None
        self.export_gml_dialog = None
        self.options_dialog = None
        self.actions = []
        self.menu = '&SEC4QGIS'
        self.toolbar = self.iface.addToolBar('SEC4QGIS')
        self.toolbar.setObjectName('SEC4QGIS')
        self.set_global_options()
        unzip_directory = os.path.dirname(os.path.abspath(__file__))+"/tmp/"
        shutil.rmtree(unzip_directory, ignore_errors=True)
###########################################################################################################################
###########################################################################################################################
    def tr(self, text, disambiguate=None):
        return QCoreApplication.translate("Sec4Qgis", text, disambiguate)
###########################################################################################################################
###########################################################################################################################
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.
        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str
        :param text: Text that should be shown in menu items for this action.
        :type text: str
        :param callback: Function to be called when the action is triggered.
        :type callback: function
        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str
        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget
        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action
###########################################################################################################################
###########################################################################################################################
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.add_action(
            icon_path = ':/plugins/SEC/icon_importar.png',
            text=self.tr('Import cartography'),
            callback=self.import_cartography_main,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path = ':/plugins/SEC/icon_exportar.png',
            text=self.tr('Export vector layer as GML INSPIRE'),
            callback=self.export_gml_main,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path = ':/plugins/SEC/icon_opciones.png',
            text=self.tr('SEC4QGIS options'),
            callback=self.options_main,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path = ':/plugins/SEC/icon_ayuda.png',
            text=self.tr('SEC4QGIS user guide'),
            callback=self.help_main,
            parent=self.iface.mainWindow())
###########################################################################################################################
###########################################################################################################################
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                '&SEC4QGIS',
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar
###########################################################################################################################
###########################################################################################################################
    def import_cartography_main (self):
        if self.import_cartography_dialog is None:
            self.import_cartography_dialog = import_cartography.run_script(self)
        else:
            self.import_cartography_dialog.activateWindow()
###########################################################################################################################
###########################################################################################################################
    def export_gml_main(self):
        if self.export_gml_dialog is None:
            self.export_gml_dialog = export_gml.run_script(self)
        else:
            self.export_gml_dialog.activateWindow()
###########################################################################################################################
###########################################################################################################################
    def options_main(self):
        if self.options_dialog is None:
            self.options_dialog = options.run_script(self)
        else:
            self.options_dialog.activateWindow()
###########################################################################################################################
###########################################################################################################################
    def help_main(self):
        if QSettings().value('locale/userLocale')[0:2].upper() != "ES":
            QMessageBox.warning(None, self.tr("WARNING"), self.tr("This plugin is designed to work with the Spanish Cadastral Electronic Site (SEC), so it's expected to be used almost exclusively by Spanish citizens. That's why, by the moment, the user guide is written in Spanish only.<br/><br/>Sorry for any inconvenience this may cause you.")) 
        subprocess.Popen("xdg-open "+os.path.split(os.path.abspath(__file__))[0]+"/help/ayuda.pdf", shell=True)
        subprocess.Popen(os.path.split(os.path.abspath(__file__))[0]+"/help/ayuda.pdf", shell=True)
###########################################################################################################################
###########################################################################################################################
    def set_global_options(self):
        if QSettings().value('SEC/default_crs') is None:
            default_crs = 'EPSG:25830'
        else:
            default_crs = sorted(self.valid_sec_crs_list.keys())[QSettings().value('SEC/default_crs')]
        global_parameters_current = QSettings()
        global_parameters_new = dict([
                ('Projections/defaultBehaviour', 'useGlobal'),
                ('Projections/layerDefaultCrs', default_crs),
                ('Projections/otfTransformAutoEnable', 'True'),
                ('Projections/projectDefaultCrs', default_crs),
                ('Qgis/connections-wms/PNOA/url', 'http://www.ign.es/wms-inspire/pnoa-ma'),
                ('Qgis/connections-wms/SEC/url', 'http://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx?')
            ])
        global_parameters_changed = []
        for global_parameters_new_key in sorted(global_parameters_new.keys()):
            global_parameters_new_value = global_parameters_new[global_parameters_new_key]
            if global_parameters_current.value(global_parameters_new_key, "") != global_parameters_new_value:
                global_parameters_current.setValue(global_parameters_new_key, global_parameters_new_value)
                global_parameters_changed.append(global_parameters_new_key+"="+global_parameters_new_value)
            else:
                pass
        if len(global_parameters_changed) > 0:
            pass
###########################################################################################################################
###########################################################################################################################
    def show_and_log(self, level_1, message_1, time_out=5):
        if level_1 == "E":
            self.iface.messageBar().pushMessage(self.tr("ERROR"), message_1, level=QgsMessageBar.CRITICAL, duration=time_out)
            QgsMessageLog.logMessage("["+self.tr("ERROR")+"] "+message_1, 'SEC', QgsMessageLog.CRITICAL)
        elif level_1 == "EC":
            if time_out < 20:
                time_out = 20
            self.iface.messageBar().pushMessage(self.tr("CRITICAL-ERROR"), message_1, level=QgsMessageBar.CRITICAL, duration=time_out)
            QgsMessageLog.logMessage("["+self.tr("CRITICAL-ERROR")+"] "+message_1, 'SEC', QgsMessageLog.CRITICAL)
        elif (level_1 == "W") or (level_1 == "A"):
            self.iface.messageBar().pushMessage(self.tr("WARNING"), message_1, level=QgsMessageBar.WARNING, duration=time_out)
            QgsMessageLog.logMessage("["+self.tr("WARNING")+"] "+message_1, 'SEC', QgsMessageLog.WARNING)
        elif level_1 == "I":
            self.iface.messageBar().pushMessage(self.tr("INFO"), message_1, level=QgsMessageBar.INFO, duration=time_out)
            QgsMessageLog.logMessage("["+self.tr("INFO")+"] "+message_1, 'SEC', QgsMessageLog.INFO)
        else:
            QgsMessageLog.logMessage("["+self.tr("DEBUG")+"] "+message_1, 'SEC', QgsMessageLog.INFO)
###########################################################################################################################
###########################################################################################################################
    def fix_characters(self, string_1):
        return re.sub(r'[\ \!\"\#\%\\\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~]+', r'_', string_1)
###########################################################################################################################
###########################################################################################################################
    def plugin_name_and_version(self):
        self.plugin_path = os.path.dirname(os.path.abspath(__file__))
        self.plugin_metadata = ConfigParser.ConfigParser()
        self.plugin_metadata.readfp(open(os.path.join(self.plugin_path, 'metadata.txt')))
        plugin_name = self.plugin_metadata.get('general', 'name')
        plugin_version = self.plugin_metadata.get('general', 'version')
        plugin_name_and_version = plugin_name+" v"+plugin_version
        return plugin_name_and_version
