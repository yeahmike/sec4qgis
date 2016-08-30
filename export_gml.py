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
import codecs
import re
from export_gml_dialog import ExportGmlDialog
###########################################################################################################################
###########################################################################################################################
def run_script(self):
    self.export_gml_dialog = ExportGmlDialog()
    self.export_gml_dialog.lineEdit_ouput_file.clear()
    layers = self.iface.legendInterface().layers()
    layers_list = []
    polygon_layers = []
    self.export_gml_dialog.comboBox_layers.clear()
    active_layer_index = 0
    index_1 = 0
    for layer_1 in layers:
        if (layer_1.type() == QgsMapLayer.VectorLayer) and (layer_1.geometryType() == 2) and (layer_1.featureCount()>0) and (layer_1.fieldNameIndex(self.field_localId) != -1) and (layer_1.fieldNameIndex(self.field_nameSpace) != -1):
            layers_list.append(layer_1.name())
            polygon_layers.append(layer_1)
            if (self.iface.activeLayer() != None) and (layer_1.id() == self.iface.activeLayer().id()):
                active_layer_index = index_1
            else:
                index_1 += 1
    if len(layers_list) == 0:
        self.show_and_log("EC", "EXG-0101: "+_translate("export_gml", "There's nothing to export because there isn't any polygon non-empty layer, with fields '")+self.field_localId+_translate("export_gml","' and '")+self.field_nameSpace+"'.")
        return
    self.export_gml_dialog.comboBox_layers.addItems(layers_list)
    self.export_gml_dialog.comboBox_layers.setCurrentIndex(active_layer_index)
    self.export_gml_dialog.show()
    result = self.export_gml_dialog.exec_()
    if not result:
        return 
    file_name = self.export_gml_dialog.lineEdit_ouput_file.text()
    only_selected_parcels = self.export_gml_dialog.checkBox_onlySelected.isChecked()
    selected_layer_index = self.export_gml_dialog.comboBox_layers.currentIndex()
    selected_layer = polygon_layers[selected_layer_index]
    layer_1 = selected_layer
    number_of_parcels_OK = 0
    exported_parcel_number = 1
    sequential_parcel_number = 1
    crs_1 = layer_1.crs().authid()
    if crs_1.upper() not in self.valid_sec_crs_list.keys():
        valid_sec_crs_string = ""
        for valid_sec_crs in sorted(self.valid_sec_crs_list.keys()):
            valid_sec_crs_string = valid_sec_crs_string+valid_sec_crs+", "
        valid_sec_crs_string = valid_sec_crs_string[:-2] + "."
        self.show_and_log("EC", "EXG-0102: "+_translate("export_gml", "Layer [")+layer_1.name()+ _translate("export_gml", "] has CRS [")+str(crs_1)+_translate("export_gml", "], which is not valid. Cadastral Electronic Site (SEC) only admits the following: ")+valid_sec_crs_string)
        return
    if only_selected_parcels:
        if len(layer_1.selectedFeatures()) == 0:
            self.show_and_log("E", "EXG-0103: "+_translate("export_gml", "No parcels selected. Please export all, or select someones."), 5)
            return
        else:
            features_iterator_1 = layer_1.selectedFeatures()
    else:
        features_iterator_1 = layer_1.getFeatures()
    for feature_1 in features_iterator_1:
        geometry_1 = feature_1.geometry()
        if geometry_1 is None: 
            continue
        if (geometry_1.wkbType() == 3) or (geometry_1.wkbType() == 6):
            number_of_parcels_OK += 1
    if number_of_parcels_OK == 0:
        self.show_and_log("EC", "EXG-0104: "+_translate("export_gml", "Layer [")+layer_1.name()+_translate("export_gml", "] doesn't have any parcel (polygon or multipolygon object)."))
        return
    if only_selected_parcels:
        features_iterator_1 = layer_1.selectedFeatures()
    else:
        features_iterator_1 = layer_1.getFeatures()
    dgc_parcels_id_list = []
    invalid_dgc_parcels = False
    for feature_1 in features_iterator_1:
        if feature_1.geometry() is None: 
            continue
        if (feature_1.fieldNameIndex(self.field_nameSpace) != -1) and (feature_1[self.field_nameSpace] != NULL):
            if self.valid_dgc_nameSpace_list[0].upper() == feature_1[self.field_nameSpace].upper():
                if (feature_1.fieldNameIndex(self.field_localId) != -1):
                    if (feature_1[self.field_localId] != NULL) and (feature_1[self.field_localId] != ''):
                        if len(feature_1[self.field_localId]) != 14:
                            dgc_parcels_id_list.append(feature_1.id())
                            invalid_dgc_parcels = True
                    else:
                        dgc_parcels_id_list.append(feature_1.id())
                        invalid_dgc_parcels = True
    if invalid_dgc_parcels:
        self.show_and_log ("EC", "EXG-0105: "+_translate("export_gml", "The selected existing parcels at Cadastre (")+self.field_nameSpace+"="+self.valid_dgc_nameSpace_list[0]+_translate("export_gml", ") are not valid because their cadastral reference (")+self.field_localId+_translate("export_gml", ") do not have 14 characters. Please, check and fix them."), 0)
        layer_1.setSelectedFeatures(dgc_parcels_id_list)
        return
    if only_selected_parcels:
        features_iterator_1 = layer_1.selectedFeatures()
    else:
        features_iterator_1 = layer_1.getFeatures()
    inspireId_localId = {}
    duplicated_localId = False
    for feature_1 in features_iterator_1:
        if feature_1.geometry() is None: 
            continue
        if (feature_1.fieldNameIndex(self.field_localId) != -1) and (feature_1[self.field_localId] != NULL) and (feature_1[self.field_localId] != ''):
            localId_1 = feature_1[self.field_localId]
        else:
            localId_1 = ""
        nameSpace_1 = ''
        if (feature_1.fieldNameIndex(self.field_nameSpace) != -1) and (feature_1[self.field_nameSpace] != NULL) and (feature_1[self.field_nameSpace] != ''):
            for valid_dgc_nameSpace_item in self.valid_dgc_nameSpace_list:
                if valid_dgc_nameSpace_item.upper() in feature_1[self.field_nameSpace].upper():
                    nameSpace_1 = 'ES.SDGC.CP'
                    break
        else:
            nameSpace_1 = "ES.LOCAL.CP"
        if (localId_1 == ""):
            pass
        else:
            if inspireId_localId.has_key(localId_1):
                inspireId_localId[localId_1] += 1
                duplicated_localId = True
            else:
                inspireId_localId[localId_1] = 1
    if only_selected_parcels:
        features_iterator_1 = layer_1.selectedFeatures()
    else:
        features_iterator_1 = layer_1.getFeatures()
    duplicated_localId_list = []
    if duplicated_localId:
        for parcel_1 in features_iterator_1:
            try:
                inspireId_localId[parcel_1[self.field_localId]]
            except KeyError:
                continue
            if inspireId_localId[parcel_1[self.field_localId]] > 1:
                duplicated_localId_list.append(parcel_1.id())
        self.show_and_log ("EC", "EXG-0106: "+_translate("export_gml", "The selected parcels have their '")+self.field_localId+_translate("export_gml", "' duplicated, and this is not allowed. Please, merge them or change their '")+self.field_localId+"'.", 0)
        layer_1.setSelectedFeatures(duplicated_localId_list)
        return
    try:
        output_file = codecs.open(file_name, encoding='utf-8', mode='w')
    except IOError:
        self.show_and_log("EC", "EXG-0107: "+_translate("export_gml", "The file '")+file_name+_translate("export_gml", "' could not be written. Please, check that you have writing privileges for the selected file."))
        return
    if only_selected_parcels:
        features_iterator_1 = layer_1.selectedFeatures()
    else:
        features_iterator_1 = layer_1.getFeatures()
    print >>output_file, '''<?xml version="1.0" encoding="utf-8"?>
<!-- GML generado usando '''+self.plugin_name_and_version()+''' -->
<gml:FeatureCollection gml:id="ES.SDGC.CP" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:cp="urn:x-inspire:specification:gmlas:CadastralParcels:3.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:x-inspire:specification:gmlas:CadastralParcels:3.0 http://inspire.ec.europa.eu/schemas/cp/3.0/CadastralParcels.xsd">'''
    for feature_1 in features_iterator_1:
        timestamp_1 = datetime.datetime.now().isoformat()
        geometry_1=feature_1.geometry()
        if geometry_1 is None: continue
        if (feature_1.fieldNameIndex(self.field_localId) != -1) and (feature_1[self.field_localId] != NULL) and (feature_1[self.field_localId] != ''):
            localId_1 = feature_1[self.field_localId]
        else:
            while True:
                localId_1 = "PARCELA_%04d"%(sequential_parcel_number,)
                sequential_parcel_number += 1
                if not inspireId_localId.has_key(localId_1):
                    break
        localId_1 = self.fix_characters(localId_1)
        if (feature_1.fieldNameIndex(self.field_nameSpace) != -1) and (feature_1[self.field_nameSpace] != NULL) and (feature_1[self.field_nameSpace] != ''):
            for valid_dgc_nameSpace_item in self.valid_dgc_nameSpace_list:
                if valid_dgc_nameSpace_item.upper() in feature_1[self.field_nameSpace].upper():
                    nameSpace_1 = 'ES.SDGC.CP'
                    break
        else:
            nameSpace_1 = "ES.LOCAL.CP"
        print >>output_file, '    <!-- Parcela Catastral '+localId_1+' -->'
        print >>output_file, '''    <gml:featureMember>
        <cp:CadastralParcel gml:id="'''+nameSpace_1+'.'+localId_1+'">'
        print >>output_file, '            <cp:areaValue uom="m2">'+str(int(round(feature_1.geometry().area(),0)))+'</cp:areaValue>'
        print >>output_file, '''            <cp:beginLifespanVersion>'''+timestamp_1+'''</cp:beginLifespanVersion>
            <cp:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <cp:geometry>
                <gml:MultiSurface gml:id="MultiSurface_'''+nameSpace_1+'.'+localId_1+'" srsName="urn:ogc:def:crs:'+crs_1+'">'
        if geometry_1.wkbType() == 3:
            exported_parcel_number += 1
            describe_polygon(feature_1, localId_1, nameSpace_1, crs_1, output_file)
        elif geometry_1.wkbType() == 6:
            exported_parcel_number += 1
            describe_multipolygon(feature_1, localId_1, nameSpace_1, crs_1, output_file)
        print >>output_file, '''                </gml:MultiSurface>
            </cp:geometry>
            <cp:inspireId xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2">
                <base:Identifier>
                    <base:localId>'''+localId_1+'''</base:localId>
                    <base:namespace>'''+nameSpace_1+'''</base:namespace>
                </base:Identifier>
            </cp:inspireId>
            <cp:label>'''+"P%04d"%(exported_parcel_number-1,)+'''</cp:label>'''
        if nameSpace_1 == "ES.LOCAL.CP":
            print >>output_file, '            <cp:nationalCadastralReference/>'
        else:
            print >>output_file, '            <cp:nationalCadastralReference>'+localId_1+'</cp:nationalCadastralReference>'
        print >>output_file, '''            <cp:validFrom xsi:nil="true" nilReason="other:unpopulated"/>
            <cp:validTo xsi:nil="true" nilReason="other:unpopulated"/>
        </cp:CadastralParcel>
    </gml:featureMember>'''
    print >>output_file, '</gml:FeatureCollection>'
    output_file.close()
    if number_of_parcels_OK != exported_parcel_number-1:
        self.show_and_log("E", "EXG-0108: "+_translate("export_gml", "Oh no! ")+str(number_of_parcels_OK)+_translate("export_gml", " parcels should have been exported, but actually ")+str(exported_parcel_number-1)+_translate("export_gml", " parcels have been exported. Please report this bug."), 0)
        return
    if only_selected_parcels:
        if number_of_parcels_OK == 1:
            self.show_and_log("I", _translate("export_gml", "The selected parcel has been successfully exported."), 10)
        else:
            self.show_and_log("I", _translate("export_gml", "The ")+str(number_of_parcels_OK)+_translate("export_gml", " selected parcels have been successfully exported."), 10)
    else:
        if number_of_parcels_OK == 1:
            self.show_and_log("I", _translate("export_gml", "Layer [")+layer_1.name()+_translate("export_gml", "] has been successfully exported, creating 1 cadatastral parcel."), 10)
        else:
            self.show_and_log("I", _translate("export_gml", "Layer [")+layer_1.name()+_translate("export_gml", "] has been successfully exported, creating ")+str(number_of_parcels_OK)+_translate("export_gml", " cadatastral parcels."), 10)
###########################################################################################################################
###########################################################################################################################
def describe_multipolygon(feature_multipolygon, localId_1, nameSpace_1, crs_1, output_file):
    geometry_1=feature_multipolygon.geometry()
    for polygon_1 in range(len(geometry_1.asMultiPolygon())):
        print >>output_file, '''                    <gml:surfaceMember>
                        <gml:Surface gml:id="Surface_'''+nameSpace_1+'.'+localId_1+'.'+"Polygon_%04d"%(polygon_1+1, )+'" srsName="urn:ogc:def:crs:'+crs_1+'''">
                            <gml:patches>
                                <gml:PolygonPatch>'''
        for ring_1 in range(len(geometry_1.asMultiPolygon()[polygon_1])):
                if ring_1==0:
                    print >>output_file, '''                                    <gml:exterior>'''
                else:
                    print >>output_file, '''                                    <gml:interior>'''
                points_number = len(geometry_1.asMultiPolygon()[polygon_1][ring_1])
                print >>output_file, '''                                        <gml:LinearRing>
                                            <gml:posList srsDimension="2" count="'''+str(points_number)+'''">''',
                for point_1 in range(points_number):
                    print >>output_file, "%f %f"%(geometry_1.asMultiPolygon()[polygon_1][ring_1][point_1].x(), geometry_1.asMultiPolygon()[polygon_1][ring_1][point_1].y()),
                    if point_1 != points_number-1:
                        print >>output_file, ("   "),
                print >>output_file, '''</gml:posList>
                                        </gml:LinearRing>'''
                if ring_1==0:
                    print >>output_file, '''                                    </gml:exterior>'''
                else:
                    print >>output_file, '''                                    </gml:interior>'''
        print >>output_file, '''                                </gml:PolygonPatch>
                            </gml:patches>
                        </gml:Surface>
                    </gml:surfaceMember>'''
###########################################################################################################################
###########################################################################################################################
def describe_polygon(feature_polygon, localId_1, nameSpace_1, crs_1, output_file):
    geometry_multipolygon = QgsGeometry.fromMultiPolygon([feature_polygon.geometry().asPolygon()])
    feature_multipolygon = QgsFeature()
    feature_multipolygon.setGeometry(geometry_multipolygon)
    describe_multipolygon(feature_multipolygon, localId_1, nameSpace_1, crs_1, output_file)
###########################################################################################################################
###########################################################################################################################
def _translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)
