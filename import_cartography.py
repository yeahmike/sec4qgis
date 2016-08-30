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
import time
from random import randint
from import_cartography_dialog import ImportCartographyDialog
###########################################################################################################################
###########################################################################################################################
def run_script(self):
    """ Put your code here and remove the pass statement"""
    set_project_options(self)
    project_file_info = QFileInfo(QgsProject.instance().fileName())
    if project_file_info.absolutePath() == "":
        if QSettings().value('SEC4QGIS/last_folder_project') is None:
            last_folder_project = ""
        else:
            last_folder_project = QSettings().value('SEC4QGIS/last_folder_project')
        QMessageBox.warning(None, _translate("import_cartography", "WARNING"), _translate("import_cartography", "<b>You have to save your project before importing any cartography.</b><br/><br/>Please, select the name and path for your project on the next window.")) 
        project_file_name = QFileDialog.getSaveFileName(None, _translate("import_cartography", "Save project as"), last_folder_project, "*.qgs")
        if len(project_file_name)>0:
            last_folder_project = os.path.split(project_file_name)[0]
            QSettings().setValue('SEC4QGIS/last_folder_project', last_folder_project)
            project_saved_ok = QgsProject.instance().write(QFileInfo(project_file_name))
        else:
            QMessageBox.warning(None, _translate("import_cartography", "WARNING"), _translate("import_cartography", "The project has not been saved, ")+_translate("import_cartography", "so you cannot to import the cartography.")) 
            return
        if not project_saved_ok:
            QMessageBox.critical(None, "ERROR: SIC-0901: ", _translate("import_cartography", "The plugin could not save the project, ")+_translate("import_cartography", "so you cannot to import the cartography.")) 
            return
    self.import_cartography_dialog = ImportCartographyDialog()
    self.import_cartography_dialog.lineEdit_file_name.clear()
    current_project = QgsProject.instance()
    sequential_layer_number = current_project.readNumEntry('SEC4QGIS', 'sequential_layer_number')[0]
    sequential_layer_name = "CAPA_%04d"%(sequential_layer_number+1,)
    self.import_cartography_dialog.lineEdit_new_layer.setPlaceholderText(sequential_layer_name)
    project_file_info = QFileInfo(QgsProject.instance().fileName())
    project_file_name_without_extension = os.path.splitext(project_file_info.fileName())[0]
    directory_1 = project_file_info.absolutePath()+"/"+project_file_name_without_extension+"_CAPAS/"
    if (os.path.exists(directory_1)) and (len(self.iface.legendInterface().layers()) == 0):
        shutil.rmtree(directory_1, ignore_errors=True)
        time.sleep(0.1)
    if not os.path.exists(directory_1):
        for loop_1 in range(1, 100):
            try:
                os.makedirs(directory_1)
                break
            except OSError:
                time.sleep(0.1)
        if not os.path.exists(directory_1):
            self.show_and_log("EC", "ERROR: SIC-0903: "+_translate("import_cartography", "Could not create directory '")+directory_1+"'.")
    try:
        output_file = codecs.open(directory_1+"test_rw.txt", encoding='utf-8', mode='w')
    except IOError:
        self.show_and_log ("EC", "ERROR: SIC-0902: "+_translate("import_cartography", "Please, create a new project and try to import the cartography again, because the plugin could not write into this project's layer folder '")+directory_1+"'.") 
        return
    output_file.close()
    os.remove(directory_1+"test_rw.txt")
    layers_list = self.iface.legendInterface().layers()
    layers_names_list = []
    polygon_layers_list = []
    active_layer_index = -1
    index_1 = -1
    self.import_cartography_dialog.comboBox_crs.clear()
    for layer_1 in layers_list:
        if (layer_1.type() == QgsMapLayer.VectorLayer) and (layer_1.geometryType() == 2) and (layer_1.dataProvider().capabilities() & QgsVectorDataProvider.AddFeatures):
            layers_names_list.append(layer_1.name())
            polygon_layers_list.append(layer_1)
            index_1 += 1
            if (self.iface.activeLayer() != None) and (layer_1.id() == self.iface.activeLayer().id()):
                active_layer_index = index_1
    self.import_cartography_dialog.comboBox_existing_layers.addItems(layers_names_list)
    if active_layer_index != -1:
        self.import_cartography_dialog.comboBox_existing_layers.setCurrentIndex(active_layer_index)
    if QSettings().value('SEC4QGIS/default_import_to_new_layer') is None:
        default_import_to_new_layer = False
    else:
        default_import_to_new_layer = QSettings().value('SEC4QGIS/default_import_to_new_layer')
    if (len(polygon_layers_list)>0) and (default_import_to_new_layer != 1):
        self.import_cartography_dialog.radioButton_new_layer.setEnabled(True)
        self.import_cartography_dialog.lineEdit_new_layer.setEnabled(False)
        self.import_cartography_dialog.comboBox_crs.setEnabled(False)
        self.import_cartography_dialog.radioButton_existing_layers.setChecked(True)
        self.import_cartography_dialog.comboBox_existing_layers.setEnabled(True)
    else:
        self.import_cartography_dialog.radioButton_new_layer.setEnabled(True)
        self.import_cartography_dialog.comboBox_crs.setEnabled(True)
        self.import_cartography_dialog.radioButton_new_layer.setChecked(True)
        self.import_cartography_dialog.lineEdit_new_layer.setEnabled(True)
        if (len(polygon_layers_list) == 0):
            self.import_cartography_dialog.radioButton_existing_layers.setEnabled(False)
        self.import_cartography_dialog.comboBox_existing_layers.setEnabled(False)
    for valid_sec_crs in sorted(self.valid_sec_crs_list.keys()):
        self.import_cartography_dialog.comboBox_crs.addItem(valid_sec_crs+" = "+self.valid_sec_crs_list[valid_sec_crs])
    self.import_cartography_dialog.comboBox_crs.setCurrentIndex(1)
    self.import_cartography_dialog.show()
    result = self.import_cartography_dialog.exec_()
    if not result:
        return 
    files_names_string = self.import_cartography_dialog.lineEdit_file_name.text()
    if self.import_cartography_dialog.radioButton_new_layer.isChecked():
        selected_crs = sorted(self.valid_sec_crs_list.keys())[self.import_cartography_dialog.comboBox_crs.currentIndex()]
        if self.import_cartography_dialog.lineEdit_new_layer.text() == '':
            new_layer_name = sequential_layer_name
        else:
            new_layer_name = self.import_cartography_dialog.lineEdit_new_layer.text()
        memory_layer_1 = QgsVectorLayer("MultiPolygon?crs="+selected_crs+"&field="+self.field_localId+":string(14)&field="+self.field_nameSpace+":string(11)", new_layer_name, "memory")
        if not memory_layer_1.isValid():
            self.show_and_log("EC", "SIC-0201: "+_translate("import_cartography", "The memory layer '")+new_layer_name+_translate("import_cartography", "' could NOT be created with CRS '")+selected_crs+"'.")
            return
        shapefile_name = directory_1+self.fix_characters(new_layer_name)+"_"+self.fix_characters(str(datetime.datetime.now().isoformat())[:-7])+".shp"
        writer_1 = QgsVectorFileWriter.writeAsVectorFormat(memory_layer_1, shapefile_name, "UTF-8", QgsCoordinateReferenceSystem(int(selected_crs[5:]), QgsCoordinateReferenceSystem.EpsgCrsId), "ESRI Shapefile")
        destination_layer = QgsVectorLayer(shapefile_name, new_layer_name, "ogr")
        if not destination_layer.isValid():
            self.show_and_log("EC", "SIC-0202: "+_translate("import_cartography", "The Shapefile layer '")+new_layer_name+_translate("import_cartography", "' could NOT be created with CRS '")+selected_crs+"'.")
            return
        set_layer_options(self, destination_layer)
    elif self.import_cartography_dialog.radioButton_existing_layers.isChecked():
        selected_layer_index = self.import_cartography_dialog.comboBox_existing_layers.currentIndex()
        destination_layer = polygon_layers_list[selected_layer_index]
        selected_crs = destination_layer.crs().authid()
    else:
        self.show_and_log("EC", "SIC-0203: "+_translate("import_cartography", "You have not selected the layer type."))
        return    
    import_files(self, files_names_string, destination_layer, selected_crs, current_project)
###########################################################################################################################
###########################################################################################################################
def import_files(self, files_names_string, destination_layer, selected_crs, current_project):
    number_of_parcels_imported = 0
    files_names_list = re.findall(r'"(.+?)"', files_names_string)
    if len(files_names_list) == 0:
        files_names_list = [files_names_string]
    for file_name in files_names_list:
        if not os.path.isfile(file_name):
            self.show_and_log ("EC", "ERROR: SIC-0204: "+_translate("import_cartography", "File '")+file_name+_translate("import_cartography", "' does not exists.")) 
            return
        file_extension = os.path.splitext(file_name)[1].upper()
        if file_extension == ".DXF":
            import_result = import_dxf(self, file_name, selected_crs, destination_layer)
            if import_result == -1:
                number_of_parcels_imported = -1
                break
            number_of_parcels_imported += import_result
        elif file_extension in [".GML", ".SHP"]:
            import_result = import_gml_and_shp(self, file_name, selected_crs, destination_layer)
            if import_result == -1:
                number_of_parcels_imported = -1
                break
            number_of_parcels_imported += import_result
        elif file_extension == ".ZIP":
            import_result = import_zip(self, file_name, selected_crs, destination_layer)
            if import_result == -1:
                number_of_parcels_imported = -1
                break
            number_of_parcels_imported += import_result
        else:
            self.show_and_log("EC", "SIC-0205: "+_translate("import_cartography", "File extension unknown '")+file_name+"'")
            return 
    if number_of_parcels_imported == -1:
        return
    elif number_of_parcels_imported == 0:
        self.show_and_log("EC", "SIC-0206: "+_translate("import_cartography", "The cartography has NOT been imported to layer '")+destination_layer.name()+_translate("import_cartography","'. No cadastral parcels have been created."), 10)
        return
    elif number_of_parcels_imported == 1:
        self.show_and_log("I", _translate("import_cartography", "The cartography has been successfully imported to layer '")+destination_layer.name()+_translate("import_cartography","'. The plugin has created 1 cadastral parcel."), 10)
    elif number_of_parcels_imported > 1:
        self.show_and_log("I", _translate("import_cartography", "The cartography has been successfully imported to layer '")+destination_layer.name()+_translate("import_cartography", "'. The plugin has created ")+str(number_of_parcels_imported)+_translate("import_cartography", " cadastral parcels."), 10)
    else:
        self.show_and_log("EC", "SIC-0207: "+_translate("import_cartography", "The cartography has NOT been imported to layer '")+destination_layer.name()+_translate("import_cartography","'. Unknown number of cadastral parcels."), 10)
        return
    if self.import_cartography_dialog.radioButton_new_layer.isChecked():
        QgsMapLayerRegistry.instance().addMapLayer(destination_layer, 0)
        layers_root_node = QgsProject.instance().layerTreeRoot()
        destination_layer_node = QgsLayerTreeLayer(destination_layer)
        layers_root_node.insertChildNode(0, destination_layer_node)
        sequential_layer_number = current_project.readNumEntry('SEC4QGIS', 'sequential_layer_number')[0]
        current_project.writeEntry('SEC4QGIS', 'sequential_layer_number', sequential_layer_number+1)
    canvas_1 = self.iface.mapCanvas()
    destination_layer.updateExtents()
    destination_layer_extent = destination_layer.extent()
    canvas_1.setExtent(destination_layer_extent)
    self.iface.mapCanvas().refresh()
    self.iface.mapCanvas().refresh()
###########################################################################################################################
###########################################################################################################################
def import_zip(self, file_name, selected_crs, destination_layer):
    unzip_directory = unzip_cartography(self, file_name)
    if unzip_directory == "":
        return -1
    number_of_parcels_imported = 0
    for root_1, dirs_names, files_names_list in os.walk(unzip_directory):
        for file_name in files_names_list:
            file_extension = os.path.splitext(file_name)[1].upper()
            if file_extension == ".DXF":
                number_of_parcels_imported += import_dxf(self, unzip_directory+'/'+file_name, selected_crs, destination_layer)
            elif file_extension in [".GML", ".SHP"]:
                number_of_parcels_imported += import_gml_and_shp(self, unzip_directory+'/'+file_name, selected_crs, destination_layer)
            else:
                pass
    return number_of_parcels_imported
###########################################################################################################################
###########################################################################################################################
def import_gml_and_shp(self, file_name, selected_crs, destination_layer):
    source_layer = QgsVectorLayer(file_name, "source_layer", "ogr")
    file_crs = ""
    if not source_layer.isValid():
        self.show_and_log("EC", "SIC-1001: "+_translate("import_cartography", "The file '")+file_name+_translate("import_cartography", "' has NOT been imported."), 10)
        return -1
    self.iface.messageBar().clearWidgets()
    file_extension = (os.path.splitext(file_name)[1].upper())[1:]
    if file_extension == "GML":
        localId_file_field = 'inspireId_localId'
        nameSpace_file_field = 'inspireId_namespace'
        for line_1 in open(file_name):
            if "EPSG:" in line_1:
                file_crs = "EPSG:"+re.findall(r'EPSG:+(\d+)', line_1)[0]
                break
    elif file_extension == "SHP":
        localId_file_field = 'localId'
        nameSpace_file_field = 'namespace'
        file_crs = source_layer.crs().authid()
    if selected_crs != file_crs:
        self.show_and_log("EC", "SIC-1002: "+_translate("import_cartography", "The CRS of the file '")+file_crs+_translate("import_cartography", "' does NOT match the CRS of destination layer '")+selected_crs+_translate("import_cartography", "'. File '")+file_name+_translate("import_cartography", "' has NOT been imported."), 10)
        return -1
    start_time = datetime.datetime.now()
    number_of_parcels_imported = 0
    destination_parcel = QgsFeature()
    for source_parcel in source_layer.getFeatures():
        if source_parcel.geometry() is None: 
            continue
        if (source_parcel.geometry().wkbType() != 3) and (source_parcel.geometry().wkbType() != 6):
            continue
        destination_parcel.setGeometry(source_parcel.geometry())
        destination_parcel.initAttributes(2)
        if file_extension == "GML":
            if source_parcel.fieldNameIndex(localId_file_field) != -1:
                destination_parcel.setAttribute(0, source_parcel[localId_file_field])
            if source_parcel.fieldNameIndex(nameSpace_file_field) != -1:
                if source_parcel[nameSpace_file_field].upper() == "ES.SDGC.CP":
                    destination_parcel.setAttribute(1, self.valid_dgc_nameSpace_list[0])
                else:
                    destination_parcel.setAttribute(1, source_parcel[nameSpace_file_field])
        elif file_extension == "SHP":
            if source_parcel.fieldNameIndex(localId_file_field) != -1:
                destination_parcel.setAttribute(0, source_parcel[localId_file_field])
            if source_parcel.fieldNameIndex(nameSpace_file_field) != -1:
                if source_parcel[nameSpace_file_field].upper() == self.valid_dgc_nameSpace_list[0]:
                    destination_parcel.setAttribute(1, self.valid_dgc_nameSpace_list[0])
                else:
                    destination_parcel.setAttribute(1, source_parcel[nameSpace_file_field])
        destination_layer.dataProvider().addFeatures([destination_parcel])
        number_of_parcels_imported += 1
    stop_time = datetime.datetime.now()
    return number_of_parcels_imported
###########################################################################################################################
###########################################################################################################################
def import_dxf(self, file_name, selected_crs, destination_layer):
    number_of_parcels_imported = 0
    file_hash_127 = dxf_header_hash(self, file_name, 127)
    file_hash_009 = dxf_header_hash(self, file_name, 9)
    if file_hash_127 == -1:
        return -1
    elif file_hash_127 == "305b2eb973210df65e34488b08cca09e0b39772c2bdf0bb35848bc35e6f4c103": 
        number_of_parcels_imported += import_dxf_sec_zone(self, file_name, selected_crs, destination_layer)
    elif file_hash_009 == "da1a135bf425e97b727b79f639d6d8a22a21e40e171f7785704fcf6cd4196a78": 
        number_of_parcels_imported += import_dxf_sec_parcel(self, file_name, selected_crs, destination_layer)
    else:
        self.show_and_log("EC", "SIC-0301: "+_translate("import_cartography", "File format unknown for '")+file_name+_translate("import_cartography", "'. No cadastral parcels have been created."))
        return -1
    return number_of_parcels_imported
###########################################################################################################################
###########################################################################################################################
def import_dxf_sec_zone(self, file_name, selected_crs, destination_layer):
    layer_dxf_lines = QgsVectorLayer(file_name+"|layername=entities|geometrytype=LineString", "layer_dxf_lines", "ogr")
    if not layer_dxf_lines.isValid():
        self.show_and_log("EC", "SIC-0401: "+_translate("import_cartography", "Could NOT load the DXF lines layer from '")+file_name+"'.")
        return -1
    layer_dxf_points = QgsVectorLayer(file_name+"|layername=entities|geometrytype=Point", "layer_dxf_points", "ogr")
    if not layer_dxf_points.isValid():
        self.show_and_log("EC", "SIC-0402: "+_translate("import_cartography", "Could NOT load the DXF points layer from '")+file_name+"'.")
        return -1
    self.iface.messageBar().clearWidgets() 
    start_time = datetime.datetime.now()
    layer_dxf_polygon = QgsVectorLayer("MultiPolygon?crs="+selected_crs+"&field="+self.field_localId+":string(14)&field="+self.field_nameSpace+":string(11)", destination_layer.name()+"-DXFpoligonos", "memory")
    if not layer_dxf_polygon.isValid():
        self.show_and_log("EC", "SIC-0403: "+_translate("import_cartography", "Could NOT create the layer '")+destination_layer.name()+"-DXFpoligonos'")
        return -1
    in_feat = QgsFeature()
    out_feat = QgsFeature()
    layer_dxf_polygon_provider = layer_dxf_polygon.dataProvider()
    layer_dxf_lines_features = layer_dxf_lines.getFeatures()
    while layer_dxf_lines_features.nextFeature(in_feat):
        out_geom_list = []
        if in_feat.geometry().isMultipart():
            out_geom_list = in_feat.geometry().asMultiPolyline()
        else:
            out_geom_list.append(in_feat.geometry().asPolyline())
        poly_geom = trash_wrong_lines(self, out_geom_list)
        if (len(poly_geom) != 0) and (in_feat['Layer'] == 'Parcela'):
            out_feat.setGeometry(QgsGeometry.fromPolygon(poly_geom))
            in_feat_attributes = in_feat.attributes()
            out_feat.setAttributes(in_feat_attributes)
            layer_dxf_polygon_provider.addFeatures([out_feat])
    layer_dxf_polygon_unique = QgsVectorLayer("MultiPolygon?crs="+selected_crs+"&field="+self.field_localId+":string(14)&field="+self.field_nameSpace+":string(11)", destination_layer.name()+"-DXFsinDup", "memory")
    if not layer_dxf_polygon_unique.isValid():
        self.show_and_log("EC", "SIC-0404: "+_translate("import_cartography", "Could NOT create the layer '")+destination_layer.name()+"-DXFsinDup'")
        return -1
    for poligono_1 in layer_dxf_polygon.getFeatures():
        duplicated_1 = False
        for poligono_2 in layer_dxf_polygon.getFeatures():
            if poligono_1.id() == poligono_2.id():
                continue
            if (abs(poligono_1.geometry().intersection(poligono_2.geometry()).area() - poligono_1.geometry().area()) < 0.01) and (poligono_1.id() < poligono_2.id()):
                duplicated_1 = True
                break
        if not duplicated_1:
            layer_dxf_polygon_unique.dataProvider().addFeatures([poligono_1])
    layer_dxf_polygon_holes = QgsVectorLayer("MultiPolygon?crs="+selected_crs+"&field="+self.field_localId+":string(14)&field="+self.field_nameSpace+":string(11)", destination_layer.name()+"-DXFhuecos", "memory")
    if not layer_dxf_polygon_holes.isValid():
        self.show_and_log("EC", "SIC-0405: "+_translate("import_cartography", "Could NOT create the layer '")+destination_layer.name()+"-DXFhuecos'")
        return -1
    for parcel_1 in layer_dxf_polygon_unique.getFeatures():
        parcel_temp = QgsFeature()
        geometry_temp = QgsGeometry()
        modified_1 = False
        for parcel_2 in layer_dxf_polygon_unique.getFeatures():
            if parcel_1.id() == parcel_2.id():
                continue
            if parcel_2.geometry().within(parcel_1.geometry()):
                if not modified_1:
                    pass
                if geometry_temp.area() <= 0.01:
                    geometry_temp = QgsGeometry(parcel_1.geometry().difference(parcel_2.geometry()))
                else:
                    geometry_temp = QgsGeometry(geometry_temp.difference(parcel_2.geometry()))
                parcel_temp.setGeometry(geometry_temp)
                modified_1 = True
        if modified_1:
            parcel_temp.setAttributes(parcel_1.attributes())
            if geometry_temp.area() > 0.01:
                layer_dxf_polygon_holes.dataProvider().addFeatures([parcel_temp])
        else:
            layer_dxf_polygon_holes.dataProvider().addFeatures([parcel_1])
    stop_time = datetime.datetime.now()
    start_time = datetime.datetime.now()
    points_list = layer_dxf_points.getFeatures()
    points_rc_list = []
    for point_1 in points_list:
        if point_1['Layer'] == 'RefCatastral':
            points_rc_list.append(point_1)
    parcels_list = layer_dxf_polygon_holes.getFeatures()
    for parcela_1 in parcels_list:
        for point_1 in points_rc_list:
            if point_1.geometry().within(parcela_1.geometry()):
                cadastral_reference = point_1['Text']
                attributes_1 = { 0 : cadastral_reference, 1 : self.valid_dgc_nameSpace_list[0] }
                layer_dxf_polygon_holes.dataProvider().changeAttributeValues({ parcela_1.id() : attributes_1 })
                points_rc_list.remove(point_1)
                break
    stop_time = datetime.datetime.now()
    number_of_parcels_imported = 0
    parcels_list = []
    for parcel_1 in layer_dxf_polygon_holes.getFeatures():
        parcels_list.append(parcel_1)
    for index_1, parcel_1 in enumerate(parcels_list):
        parcel_temp = QgsFeature()
        duplicates_indexes_list = []
        for index_2, parcel_2 in enumerate(parcels_list):
            if index_2<=index_1:
                continue
            if parcel_1[0] == parcel_2[0]:
                duplicates_indexes_list.append(index_2)
        geometry_temp = parcel_1.geometry()
        for duplicates_index in duplicates_indexes_list:
            geometry_temp = geometry_temp.combine(parcels_list[duplicates_index].geometry())
            parcel_temp.setGeometry(geometry_temp)
        duplicates_indexes_list.reverse()
        for duplicates_index in duplicates_indexes_list:
            del parcels_list[duplicates_index]
        parcel_temp.setGeometry(geometry_temp)
        parcel_temp.setAttributes(parcel_1.attributes())
        number_of_parcels_imported += 1
        destination_layer.dataProvider().addFeatures([parcel_temp])
    return number_of_parcels_imported
###########################################################################################################################
###########################################################################################################################
def import_dxf_sec_parcel(self, file_name, selected_crs, destination_layer):
    fragments_list = []
    if "Fragment".upper() in file_name.upper():
        if "Fragment0001".upper() in file_name.upper():
            (fragments_directory, file_name_only) = os.path.split(file_name)
            for root_1, dirs_names, files_names_list in os.walk(fragments_directory):
                for file_name in files_names_list:
                    if (file_name[:14] == file_name_only[:14]) and (file_name[-4:].upper() == '.DXF'):
                        fragments_list.append(fragments_directory+'/'+file_name)
        else:
            return 0
    else:
        fragments_list = [file_name]
    start_time = datetime.datetime.now()
    layer_dxf_polyline = QgsVectorLayer("MultiLineString?crs="+selected_crs+"&field="+self.field_localId+":string(14)&field="+self.field_nameSpace+":string(11)", destination_layer.name()+"-DXFpolilinea", "memory")
    if not layer_dxf_polyline.isValid():
        self.show_and_log("EC", "SIC-0501: "+_translate("import_cartography", "Could NOT create the layer '")+destination_layer.name()+"-DXFpolilinea'")
        return -1
    lines_list=[]
    geometry_temp1 = QgsGeometry()
    object_temp1 = QgsFeature()
    for file_name in fragments_list:
        layer_dxf_lines = QgsVectorLayer(file_name+"|layername=entities|geometrytype=LineString", "layer_dxf_lines", "ogr")
        if not layer_dxf_lines.isValid():
            self.show_and_log("EC", "SIC-0502: "+_translate("import_cartography", "Could NOT load the DXF lines layer from '")+file_name+"'.")
            return -1
        layer_dxf_points = QgsVectorLayer(file_name+"|layername=entities|geometrytype=Point", "layer_dxf_points", "ogr")
        if not layer_dxf_points.isValid():
            self.show_and_log("EC", "SIC-0503: "+_translate("import_cartography", "Could NOT load the DXF points layer from '")+file_name+"'.")
            return -1
        self.iface.messageBar().clearWidgets() 
        for line_1 in layer_dxf_lines.getFeatures():
            if line_1['Layer'] == 'PG-LP':
                lines_list.append(line_1)
        geometry_temp1 = lines_list[0].geometry()
        for line_1 in lines_list[1:]:
            geometry_temp1 = geometry_temp1.combine(line_1.geometry())
        object_temp1.setGeometry(geometry_temp1)
    layer_dxf_polyline.dataProvider().addFeatures([object_temp1])
    layer_dxf_polygon = QgsVectorLayer("MultiPolygon?crs="+selected_crs+"&field="+self.field_localId+":string(14)&field="+self.field_nameSpace+":string(11)", destination_layer.name()+"-DXFpoligonos", "memory")
    if not layer_dxf_polyline.isValid():
        self.show_and_log("EC", "SIC-0504: "+_translate("import_cartography", "Could NOT create the layer '")+destination_layer.name()+"-DXFpoligonos'")
        return -1
    lines_list = re.findall(r'\(([^\(\)]+)\)', geometry_temp1.exportToWkt()) 
    for line_1 in lines_list:
        line_coordinates_array = re.findall(r'^([^,]+?), ((.+), )*([^,]+)$', line_1)
        if line_coordinates_array[0][0] == line_coordinates_array[0][3]:
            polygon_coordinates_string = line_coordinates_array[0][0]+', '+line_coordinates_array[0][2]+', '+line_coordinates_array[0][3]
        else:
            polygon_coordinates_string = line_coordinates_array[0][0]+', '+line_coordinates_array[0][2]+', '+line_coordinates_array[0][3]+', '+line_coordinates_array[0][0]  
        object_temp2 = QgsFeature()
        object_temp2.setGeometry(QgsGeometry.fromWkt('Polygon (('+polygon_coordinates_string+'))'))
        layer_dxf_polygon.dataProvider().addFeatures([object_temp2])
    layer_dxf_polygon_holes = QgsVectorLayer("MultiPolygon?crs="+selected_crs+"&field="+self.field_localId+":string(14)&field="+self.field_nameSpace+":string(11)", destination_layer.name()+"-DXFpoligonosHuecos", "memory")
    if not layer_dxf_polyline.isValid():
        self.show_and_log("EC", "SIC-0505: "+_translate("import_cartography", "Could NOT create the layer '")+destination_layer.name()+"-DXFpoligonosHuecos'")
        return -1
    polygons_holes_list = []
    for parcel_1 in layer_dxf_polygon.getFeatures():
        parcel_temp = QgsFeature()
        geometry_temp = QgsGeometry()
        is_a_hole = False
        modified_1 = False
        for parcel_2 in layer_dxf_polygon.getFeatures():
            if parcel_1.id() == parcel_2.id():
                continue
            if parcel_1.geometry().within(parcel_2.geometry()):
                is_a_hole = True
                break
            if parcel_2.geometry().within(parcel_1.geometry()):
                if not modified_1:
                    pass
                if geometry_temp.area() <= 0.01:
                    geometry_temp = QgsGeometry(parcel_1.geometry().difference(parcel_2.geometry()))
                else:
                    geometry_temp = QgsGeometry(geometry_temp.difference(parcel_2.geometry()))
                parcel_temp.setGeometry(geometry_temp)
                modified_1 = True
        if modified_1:
            parcel_temp.setAttributes(parcel_1.attributes())
            if geometry_temp.area() > 0.01:
                layer_dxf_polygon_holes.dataProvider().addFeatures([parcel_temp])
                polygons_holes_list.append(parcel_temp)
        elif not is_a_hole:
            layer_dxf_polygon_holes.dataProvider().addFeatures([parcel_1])
            polygons_holes_list.append(parcel_1)
    object_temp4 = QgsFeature()
    geometry_temp4 = polygons_holes_list[0].geometry()
    for poligono4 in polygons_holes_list[1:]:
        geometry_temp4 = geometry_temp4.combine(poligono4.geometry())
    object_temp4.setGeometry(geometry_temp4)
    cadastral_reference = os.path.split(file_name)[1][:14]
    object_temp4.initAttributes(2)
    object_temp4.setAttribute(0, cadastral_reference)
    object_temp4.setAttribute(1, self.valid_dgc_nameSpace_list[0])
    destination_layer.dataProvider().addFeatures([object_temp4])
    stop_time = datetime.datetime.now()
    return 1
###########################################################################################################################
###########################################################################################################################
def trash_wrong_lines(self, lines_list):
    geometry_temp1 = []
    if len(lines_list) == 1:
        if len(lines_list[0]) > 2:
            geometry_temp1 = lines_list
        else:
            geometry_temp1 = []
    else:
        geometry_temp1 = [line_1 for line_1 in lines_list if len(line_1) > 2]
    return geometry_temp1
###########################################################################################################################
###########################################################################################################################
def get_map_layer_by_name(layer_name):
    layer_map = QgsMapLayerRegistry.instance().mapLayers()
    for name_1, layer_1 in layer_map.iteritems():
        if layer_1.name().upper() == layer_name.upper():
            if layer_1.isValid():
                return layer_1
            else:
                return None
###########################################################################################################################
###########################################################################################################################
def dxf_header_hash(self, file_name, lines_number=127):
    try:
        file_1 = open(file_name, "r")
    except IOError:
        self.show_and_log("EC", "SIC-0601: "+_translate("import_cartography", "Error opening file '")+file_name+"'.", 10)
        return -1
    dxf_header_hash = hashlib.sha256()
    for loop_1 in range(1, lines_number):
        dxf_header_hash.update(file_1.readline())
    file_1.close()
    return dxf_header_hash.hexdigest()
###########################################################################################################################
###########################################################################################################################
def set_layer_options(self, layer_1):
    current_project = QgsProject.instance()
    layer_options_new = dict ([
            ('active', True),
            ('mode', 0), 
            ('units', 1), 
            ('tolerance', 10.0), 
            ('avoid_intersections', False)
        ])
    layer_options_new_list=(layer_options_new['active'], layer_options_new['mode'], layer_options_new['units'], layer_options_new['tolerance'], layer_options_new['avoid_intersections'])
    layer_options_current_list=current_project.snapSettingsForLayer(layer_1.id())[1:]
    if layer_options_current_list != layer_options_new_list:
        current_project.setSnapSettingsForLayer(layer_1.id(), layer_options_new['active'], layer_options_new['mode'], layer_options_new['units'], layer_options_new['tolerance'], layer_options_new['avoid_intersections'])
###########################################################################################################################
###########################################################################################################################
def set_project_options(self):
    current_project = QgsProject.instance()
    project_parameters_new = dict([
            ('Digitizing|DefaultSnapToleranceUnit|Num', 1),
            ('Digitizing|DefaultSnapType|String', 'to_vertex'),
            ('Digitizing|DefaultSnapTolerance|Num', 10),
            ('Digitizing|IntersectionSnapping|Bool', True),
            ('Digitizing|TopologicalEditing|Num', 1),
            ('Digitizing|SnappingMode|String', 'advanced'),
            ('PositionPrecision|DecimalPlaces|Num', 3),
            ('PositionPrecision|Automatic|Bool', False)
        ])
    project_parameters_changed = []
    for project_parameters_key in sorted(project_parameters_new.keys()):
        [project_parameter_plugin, project_parameter_section, project_parameter_type] = project_parameters_key.split("|")
        if project_parameter_type == "Bool":
            project_parameter_current_value = current_project.readBoolEntry(project_parameter_plugin, project_parameter_section)[0]
        elif project_parameter_type == "Num":
            project_parameter_current_value = current_project.readNumEntry(project_parameter_plugin, project_parameter_section)[0]
        elif project_parameter_type == "String":
            project_parameter_current_value = current_project.readEntry(project_parameter_plugin, project_parameter_section)[0]
        else: 
            self.show_and_log("E", "SIC-0701: "+_translate("import_cartography", "Project parameter type unknown: ")+str(project_parameters_key), 0) 
            return
        project_parameter_new_value = project_parameters_new[project_parameters_key]
        if project_parameter_current_value != project_parameter_new_value:
            current_project.writeEntry(project_parameter_plugin, project_parameter_section, project_parameter_new_value)
            project_parameters_changed.append(project_parameters_key+"="+str(project_parameter_new_value))
        else:
            pass
    if len(project_parameters_changed) > 0:
        pass
###########################################################################################################################
###########################################################################################################################
def round_geometry (feature_input, decimal_digits=2):
    feature_rounded = feature_input
    feature_rounded.setGeometry(QgsGeometry.fromWkt(feature_input.geometry().exportToWkt(decimal_digits)))
    return feature_rounded
###########################################################################################################################
###########################################################################################################################
def unzip_cartography (self, zip_file_name):
    extracted_files_number = 0
    timestamp_unzip = str(datetime.datetime.now().isoformat())[:-3]+("%04d" % randint(1,9999))
    year_1 = timestamp_unzip[:4]
    month_1 = timestamp_unzip[5:7]
    day_1 = timestamp_unzip[8:10]
    base_directory_name = os.path.dirname(os.path.abspath(__file__))+"/tmp/"
    unzip_directory = base_directory_name+self.fix_characters(timestamp_unzip)+"/"
    if not os.path.exists(unzip_directory):
        os.makedirs(unzip_directory)
    try:
        zip_file = zipfile.ZipFile(zip_file_name)
    except IOError:
        self.show_and_log ("E", "SIC-0801: "+_translate("import_cartography", "Error opening file '")+zip_file_name+"'", 10)
        return ""
    except zipfile.BadZipfile:
        self.show_and_log ("E", "SIC-0802: "+_translate("import_cartography", "ZIP file corrupted: '")+zip_file_name+"'", 10)
        return ""
    zip_info = zip_file.infolist()
    for zip_object in zip_info:
        source_name = unzip_directory+zip_object.filename
        (base_directory_name, file_1) = os.path.split(source_name)
        extension_1 = os.path.splitext(file_1)[1].upper()
        try:
            zip_file.extract(zip_object, unzip_directory)
        except IOError:
            self.show_and_log ("E", "SIC-0803: "+_translate("import_cartography", "ZIP file corrupted: '")+zip_file_name+"'", 10)
            return ""
        if extension_1 not in ['.DXF', '.GML']:
            continue
        extracted_files_number += 1
        for loop_1 in range(1,9999):
            suffix_1 = "_Fragment%04d" % loop_1
            destination_name = unzip_directory+file_1[:-4]+suffix_1+extension_1
            if not os.path.exists(destination_name):
                shutil.move(source_name, destination_name)
                break
    return unzip_directory
###########################################################################################################################
###########################################################################################################################
def _translate(context_1, text_1, disambig_1=None):
        return QtGui.QApplication.translate(context_1, text_1, disambig_1)
###########################################################################################################################
###########################################################################################################################
def layer_exists(layer_name_search):
    layermap_1 = QgsMapLayerRegistry.instance().mapLayers()
    for name_1, layer_1 in layermap_1.iteritems():
        if layer.name_1() == layer_name_search:
            if layer.isValid():
                return True
            else:
                return False
    return False
