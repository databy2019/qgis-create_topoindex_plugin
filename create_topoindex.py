# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CreateTopoindex
                                 A QGIS plugin
 Create Topoindex.ini file for TRIGRS Map
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-05-30
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Wawan Hendriawan Nur
        email                : wawanhn@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox, QToolTip
#Add QgsProject
from qgis.core import QgsProject, Qgis, QgsMapLayer, QgsMapLayerProxyModel
#Tambahan processing
from qgis import processing
from qgis.core import QgsCoordinateReferenceSystem

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .create_topoindex_dialog import CreateTopoindexDialog
import os.path

#for executable file
import subprocess


class CreateTopoindex:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CreateTopoindex_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Create Topoindex')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CreateTopoindex', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/create_topoindex/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Toolbar Create Topoindex'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Create Topoindex'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = CreateTopoindexDialog()
            self.dlg.pbCreateTopoindexIni1.clicked.connect(self.create_topoindex_ini)
            self.dlg.pbCalculateTopoindex1.clicked.connect(self.call_topoindex_exe_file)
            self.dlg.pbCreateTrigrsIni2.clicked.connect(self.create_trigrs_ini)
            self.dlg.pbCalculateTrigrs2.clicked.connect(self.call_trigrs_exe_file)
            self.dlg.leOutputFile1.hide()
            self.dlg.leOutputFile2.hide()
            self.dlg.pbCalculateTopoindex1.hide()
            self.dlg.pbCalculateTrigrs2.hide()
            # Mengatur tipe penyimpanan file ke direktori
            self.dlg.fwOutput1.setStorageMode(self.dlg.fwOutput1.StorageMode.GetDirectory)
            self.dlg.fwTopoindexFolder1.setStorageMode(self.dlg.fwTopoindexFolder1.StorageMode.GetDirectory)
            self.dlg.fwOutput2.setStorageMode(self.dlg.fwOutput2.StorageMode.GetDirectory)

            #self.dlg.mlcSlofil2.setLayer(None)
            self.dlg.mlcCfil2.setLayer(None)
            self.dlg.mlcPhifil2.setLayer(None)
            self.dlg.mlcZfil2.setLayer(None)
            self.dlg.mlcUwsfil2.setLayer(None)
            self.dlg.mlcDepfil2.setLayer(None)
            self.dlg.mlcDiffil2.setLayer(None)
            self.dlg.mlcKsfil2.setLayer(None)
            self.dlg.mlcRizerofil2.setLayer(None)
            self.dlg.mlcRifil2.setLayer(None)

            #set tool tip
            self.dlg.leProjectName1.setToolTip("Enter the project name.")
            self.dlg.fwDEM1.setToolTip("Select the DEM file to be used.")
            self.dlg.fwFlowDirection1.setToolTip("Select the Flow direction file to be used.")
            self.dlg.fwTopoindexFolder1.setToolTip("Specify a folder where the TopoIndex.ini file will be stored.")
            self.dlg.fwOutput1.setToolTip("Specify a folder where the files will be stored.")
            self.dlg.fwExeFile1.setToolTip("Select the TopoIndex.exe file.")


        #baca layer raster dan tampilkan di QMapLayerCombobox, dan panggil method saat QMapLayerCombobox dirubah
        #self.dlg.mlcDEM1.setFilters(QgsMapLayerProxyModel.RasterLayer)
        #self.dlg.mlcDEM1.currentTextChanged.connect(self.fill_rows_cols_dem_layer)
        #self.dlg.mlcFlowDirection1.setFilters(QgsMapLayerProxyModel.RasterLayer)
        #self.dlg.mlcFlowDirection1.currentTextChanged.connect(self.fill_rows_cols_dem_layer)

        self.dlg.fwDEM1.fileChanged.connect(self.fill_rows_cols_dem_file_layer)
        # Mengatur filter untuk menampilkan semua jenis file (semua ekstensi)
        #self.fwDEM1.setFilter("All files (*.*);;JPEG (*.jpg *.jpeg);;TIFF (*.tif)")
        self.dlg.fwDEM1.setFilter("ASCI (*.asc)")

        self.dlg.fwFlowDirection1.fileChanged.connect(self.fill_rows_cols_flow_file_layer)
        self.dlg.fwFlowDirection1.setFilter("ASCI (*.asc)")

        #
        self.dlg.fwSlofil2.fileChanged.connect(self.fill_imax_rows_cols_flow_layer)

        # baca layer raster dan tampilkan di QMapLayerCombobox, dan panggil method saat QMapLayerCombobox dirubah
        #self.dlg.mlcSlofil2.setFilters(QgsMapLayerProxyModel.RasterLayer)
        #self.dlg.mlcSlofil2.currentTextChanged.connect(self.fill_imax_rows_cols_flow_layer)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        
        # See if OK was pressed
        if result:
            pass
            #self.iface.messageBar().pushMessage("Berhasil", "Output file ditulis sebagai" + filename, level=Qgis.Success, duration=3)

            #subprocess.Popen("C:/TRIGRS/TopoIndex.exe")
            #subprocess.call(['C:\TRIGRS\TopoIndex.exe'])
            
            #subprocess.run(["C:/TRIGRS/TopoIndex.exe", "arg1", "arg2"])
            #subprocess.Popen(['C:/TRIGRS/TopoIndex.exe'], stdout=subprocess.PIPE)
            #subprocess.Popen(['TopoIndex.exe', r"cd C:/TRIGRS"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding = "ISO-8859-1", shell=True, text=True)

    #Fungsi membuat file topoindex.ini
    def create_topoindex_ini(self):
        #filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Pilih output file", "", '*.ini')
        #self.dlg.leOutputFile1.setText(self.dlg.fwTopoindexFolder1 + '\\TopoIndex.ini')

        filename = self.dlg.fwTopoindexFolder1.filePath() + '\\TopoIndex.ini'
        with open(filename, 'w') as output_file:
            line = "Name of project (up to 255 characters)" + '\n'
            output_file.write(line)

            project_name = self.dlg.leProjectName1.text()
            line = ''.join(project_name + '\n')
            output_file.write(line)

            line = "Rows, Columns, flow-direction numbering scheme (ESRI=1, TopoIndex=2)" + '\n'
            output_file.write(line)

            rows = self.dlg.leRows1.text()
            columns = self.dlg.leColumns1.text()
            line = ''.join(rows + ', ' + columns + ', 1' + '\n')
            output_file.write(line)

            line = "Exponent, Number of iterations" + '\n'
            output_file.write(line)

            exponent = self.dlg.spbExponent1.text()
            iteration = self.dlg.spbIteration1.text()
            line = ''.join(exponent + ', ' + iteration + '\n')
            output_file.write(line)

            line = "Name of elevation grid file" + '\n'
            output_file.write(line)
            DEM = self.dlg.fwDEM1.filePath()
            line = ''.join(DEM + '\n')
            output_file.write(line)

            line = "Name of direction grid" + '\n'
            output_file.write(line)
            flowDirection = self.dlg.fwFlowDirection1.filePath()
            line = ''.join(flowDirection + '\n')
            output_file.write(line)

            line = "Save listing of D8 downslope receptor cells?  Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            listingDownSlope = self.dlg.cmbListingDownSlope1.currentText()
            line = ''.join(listingDownSlope + '\n')
            output_file.write(line)

            line = "Save grid of D8 downslope receptor cells? Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            gridDownSlope = self.dlg.cmbGridDownSlope1.currentText()
            line = ''.join(gridDownSlope + '\n')
            output_file.write(line)

            line = "Save cell index number grid ? Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            cellIndex = self.dlg.cmbCellIndex1.currentText()
            line = ''.join(cellIndex + '\n')
            output_file.write(line)

            line = "Save list of cell number and corresponding index number?  Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            cellNumber = self.dlg.cmbCellNumber1.currentText()
            line = ''.join(cellNumber + '\n')
            output_file.write(line)

            line = "Save flow-direction grid remapped from ESRI to TopoIndex? Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            flowDirectionRemap = self.dlg.cmbFlowDirectionRemap1.currentText()
            line = ''.join(flowDirectionRemap + '\n')
            output_file.write(line)

            line = "Name of folder to store output?" + '\n'
            output_file.write(line)
            outputFolder = self.dlg.fwOutput1.filePath()
            line = ''.join(outputFolder + '\\'+ '\n')
            output_file.write(line)

            line = "ID code for output files? (8 characters or less)" + '\n'
            output_file.write(line)
            IdCode = self.dlg.leIdCode1.text()
            line = ''.join(IdCode + '\n')
            output_file.write(line)

        self.dlg.pbCalculateTopoindex1.show()

        self.iface.messageBar().pushMessage("Berhasil", "Output file ditulis sebagai" + filename, level=Qgis.Success, duration=3)
        QMessageBox.information(self.dlg, "Informasi", "File Topoindex.ini berhasil dibuat")

    # Fungsi membuat file trigrs.ini
    def create_trigrs_ini(self):
        filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Pilih output file", "", '*.ini')
        self.dlg.leOutputFile2.setText(filename)

        filename = self.dlg.leOutputFile2.text()

        with open(filename, 'w') as output_file:
            line = "Name of project (up to 255 characters)" + '\n'
            output_file.write(line)

            project_name = self.dlg.leProjectName2.text()
            line = ''.join(project_name + '\n')
            output_file.write(line)

            line = "imax, row, col, nwf" + '\n'
            output_file.write(line)

            imax2 = self.dlg.leImax2.text()
            row2 = self.dlg.leRow2.text()
            column2 = self.dlg.leColumn2.text()
            nwf2 = self.dlg.leNwf2.text()
            line = ''.join(imax2 + ', ' + row2 + ', ' + column2 + ', ' + nwf2 +  '\n')
            output_file.write(line)

            line = "nzs, nmax, nper, zmin, uww, t" + '\n'
            output_file.write(line)

            nzs2 = self.dlg.spbNzs2.text()
            nmax2 = self.dlg.spbNmax2.text()
            nper2 = self.dlg.spbNper2.text()
            zmin2 = self.dlg.spbZmin2.text()
            uww2 = self.dlg.spbUww2.text()

            #Set T
            t2 = self.dlg.leT2.text()
            line = ''.join(nzs2 + ', ' + nmax2 + ', ' + nper2 + ', ' + zmin2 + ', ' + uww2 + ', ' + t2 + '\n')
            output_file.write(line)

            line = "cc, cphi, czmax, cuws, crizero, cdep, cdif, cks" + '\n'
            output_file.write(line)

            cc2 = self.dlg.spbCc2.text()
            cphi2 = self.dlg.spbCphi2.text()
            czmax2 = self.dlg.spbCzmax2.text()
            cuws2 = self.dlg.spbCuws2.text()
            crizero2 = self.dlg.spbCrizero2.text()
            cdep2 = self.dlg.spbCdep2.text()
            cdif2 = self.dlg.leCdif2.text()
            cks2 = self.dlg.leCks2.text()
            line = ''.join(cc2 + ', ' + cphi2 + ', ' + czmax2 + ', ' + cuws2 + ', ' + crizero2 + ', ' + cdep2 + ', ' + cdif2 + ', ' + cks2 + '\n')
            output_file.write(line)

            line = "cri(1), cri(2), ... cri(nper)" + '\n'
            output_file.write(line)

            #tampilkan kriteria
            i = 0
            n = int(nper2)
            while (i < n):
                line = ''.join('1.2e-08' + ', ')
                output_file.write(line)
                i = i + 1
            line = ''.join('\n')
            output_file.write(line)

            line = "capt(1), capt(2), ... capt(n+1)" + '\n'
            output_file.write(line)

            # tampilkan capt
            i = 0
            capt2 = 0
            capt1 = 86400
            n = int(nper2)
            while (i <= n):
                if (i < n):
                    line = ''.join(str(capt2) + ', ')
                    output_file.write(line)
                elif (i == n):
                    line = ''.join(str(capt2))
                    output_file.write(line)
                capt2 = capt2 + capt1
                i = i + 1
            line = ''.join('\n')
            output_file.write(line)

            #Slofil
            line = "File name of slope angle grid (slofil)" + '\n'
            output_file.write(line)
            line = self.dlg.fwSlofil2.filePath()
            output_file.write(line + '\n')

            #Cfil
            line = "File name of cohesion grid (cfil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcCfil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Phifil
            line = "File name of Phi-angle grid (phifil) " + '\n'
            output_file.write(line)
            line = self.dlg.mlcPhifil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Zfil
            line = "File name of depth grid (zfil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcZfil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Uwsfil
            line = "File name of total unit weight of soil grid (uwsfil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcUwsfil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Depfil
            line = "File name of initial depth of water table grid   (depfil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcDepfil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Diffil
            line = "File name of diffusivity grid  (diffil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcDiffil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Ksfil
            line = "File name of saturated hydraulic conductivity grid   (ksfil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcKsfil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Rizerofil
            line = "File name of initial infiltration rate grid   (rizerofil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcRizerofil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Nxtfil
            line = "File name of grid of D8 runoff receptor cell numbers (nxtfil)" + '\n'
            output_file.write(line)
            line = self.dlg.mlcNxtfil2.currentText()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')

            #Ndxfil
            line = "File name of list of defining runoff computation order (ndxfil)" + '\n'
            output_file.write(line)
            line = self.dlg.fwNdxfil2.filePath()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write(line + '\n')

            #Dscfil
            line = "File name of list of all runoff receptor cells  (dscfil)" + '\n'
            output_file.write(line)
            line = self.dlg.fwDscfil2.filePath()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write(line + '\n')

            #Wiffil
            line = "File name of list of runoff weighting factors  (wffil)" + '\n'
            output_file.write(line)
            line = self.dlg.fwWffil2.filePath()
            if line == '':
                output_file.write("none" + "\n")
            else:
                output_file.write(line + '\n')

            #Rifil
            line = "List of file name(s) of rainfall intensity for each period, (rifil())" + '\n'
            output_file.write(line)
            #line = self.dlg.mlcRifil2.currentText()
            #output_file.write("c:\\TRIGRS\\data\\" + line + '.asc' + '\n')
            i = 0
            n = int(nper2)
            while (i < n):
                line = ''.join('none' + '\n')
                output_file.write(line)
                i = i + 1
            #line = ''.join('\n')
            #output_file.write(line)

            #Folder result
            line = "Folder where output grid files will be stored  (folder)" + '\n'
            output_file.write(line)
            outputFolder2 = self.dlg.fwOutput2.filePath()
            output_file.write(outputFolder2 + "\\" + '\n')

            # ID Suffix
            line = "Identification code to be added to names of output files (suffix)" + '\n'
            output_file.write(line)
            idCode2 = self.dlg.leIdCode3.text()
            output_file.write(idCode2+ '\n')

            #Save Runoff
            line = "Save grid files of runoff? Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            runoff2 = self.dlg.cmbRunoff2.currentText()
            output_file.write(runoff2 + '\n')

            #Save grid Safety Max
            line = "Save grid of factor of safety at maximum depth, zmax? Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            safetyMax2 = self.dlg.cmbSafetyMax2.currentText()
            output_file.write(safetyMax2 + '\n')

            #Pore pressure
            line = "Save grid of pore pressure at maximum depth, zmax? Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            safetyMax2 = self.dlg.cmbPressureMax2.currentText()
            output_file.write(safetyMax2 + '\n')

            #minimum factor of safety
            line = "Save grid of minimum factor of safety? Enter Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            safetyMin2 = self.dlg.cmbSafetyMin2.currentText()
            output_file.write(safetyMin2 + '\n')

            #Depth of minimum factor
            line = "Save grid of depth of minimum factor of safety? Enter Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            depthSafety2 = self.dlg.cmbDepthSafety2.currentText()
            output_file.write(depthSafety2 + '\n')

            #pore pressure at depth of minimum factor of safety
            line = "Save grid of pore pressure at depth of minimum factor of safety? Enter Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            porePressure2 = self.dlg.cmbPorePressure2.currentText()
            output_file.write(porePressure2 + '\n')

            #actual infiltration rate
            line = "Save grid files of actual infiltration rate? Enter T (.true.) or F (.false.)" + '\n'
            output_file.write(line)
            infiltration2 = self.dlg.cmbInfiltration2.currentText()
            output_file.write(infiltration2 + '\n')

            #Flag
            line = "Save listing of pressure head and factor of safety (\"flag\")? (Enter -2 detailed, -1 normal, 0 none)" + '\n'
            output_file.write(line)
            flag2 = self.dlg.cmbFlag2.currentText()
            output_file.write(flag2 + '\n')

        self.dlg.pbCalculateTrigrs2.show()
        self.iface.messageBar().pushMessage("Berhasil", "Output file ditulis sebagai" + filename, level=Qgis.Success, duration=3)
        QMessageBox.information(self.dlg, "Informasi", "File Trigrs.ini berhasil dibuat")

    def fill_rows_cols_dem_layer(self):
        # read layer
        layer = self.dlg.mlcDEM1.currentText()
        rlayer = QgsProject.instance().mapLayersByName(layer)[0]

        cols = rlayer.width()
        rows = rlayer.height()
        self.dlg.leRows1.setText(str(rows))
        self.dlg.leColumns1.setText(str(cols))

    def fill_rows_cols_flow_layer(self):
        # read layer
        layer = self.dlg.mlcFlowDirection1.currentText()
        rlayer = QgsProject.instance().mapLayersByName(layer)[0]

        cols = rlayer.width()
        rows = rlayer.height()
        self.dlg.leRows1.setText(str(rows))
        self.dlg.leColumns1.setText(str(cols))

    # Method menampilkan nilai row col dari file DEM yang dibuka
    def fill_rows_cols_dem_file_layer(self):
        # read layer path
        layer_path = self.dlg.fwDEM1.filePath()
        # Check if a layer with the given name exists in the current project
        layer_name = 'DEM_file'
        layers = QgsProject.instance().mapLayersByName(layer_name)
        exists = bool(layers)
        print(exists)

        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == "DEM_file":
                QgsProject.instance().removeMapLayers([layer.id()])
        raster_layer = self.iface.addRasterLayer(layer_path, 'DEM_file')
        if raster_layer.isValid():
            print("Layer was loaded successfully!")
            cols = raster_layer.width()
            rows = raster_layer.height()
            self.dlg.leRows1.setText(str(rows))
            self.dlg.leColumns1.setText(str(cols))
        else:
            print("Unable to read basename and file path - Your string is probably invalid")

    #Method menampilkan nilai row col dari file flow direction yang dibuka
    def fill_rows_cols_flow_file_layer(self):
        # read layer path
        layer_path = self.dlg.fwFlowDirection1.filePath()
        # Check if a layer with the given name exists in the current project
        layer_name = 'Flow_Direction_file'
        layers = QgsProject.instance().mapLayersByName(layer_name)
        exists = bool(layers)
        print(exists)

        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == "Flow_Direction_file":
                QgsProject.instance().removeMapLayers([layer.id()])
        raster_layer = self.iface.addRasterLayer(layer_path, 'Flow_Direction_file')
        if raster_layer.isValid():
            print("Layer was loaded successfully!")
            cols = raster_layer.width()
            rows = raster_layer.height()
            self.dlg.leRows1.setText(str(rows))
            self.dlg.leColumns1.setText(str(cols))
        else:
            print("Unable to read basename and file path - Your string is probably invalid")

    def fill_imax_rows_cols_flow_layer(self):
        # read layer path
        layer_path = self.dlg.fwSlofil2.filePath()
        # Check if a layer with the given name exists in the current project
        layer_name = 'Slope_file'
        layers = QgsProject.instance().mapLayersByName(layer_name)
        exists = bool(layers)
        print(exists)

        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == "Slope_file":
                QgsProject.instance().removeMapLayers([layer.id()])
        raster_layer = self.iface.addRasterLayer(layer_path, 'Slope_file')
        if raster_layer.isValid():
            print("Layer was loaded successfully!")
            column2 = raster_layer.width()
            row2 = raster_layer.height()
            imax2 = 844278
            nwf2 = 844278
            self.dlg.leImax2.setText(str(imax2))
            self.dlg.leRow2.setText(str(row2))
            self.dlg.leColumn2.setText(str(column2))
            self.dlg.leNwf2.setText(str(nwf2))
        else:
            print("Unable to read basename and file path - Your string is probably invalid")

    def call_topoindex_exe_file(self):
        try:
            new_working_directory = self.dlg.fwTopoindexFolder1.filePath()
            os.chdir(new_working_directory)
            #print(f"Current working directory: {os.getcwd()}")
            #QMessageBox.information(self.dlg, f"Informasi", "File Trigrs.ini berhasil dibuat {os.getcwd()}" , os.getcwd())
            # Replace with the actual path to your external program
            external_program_path = self.dlg.fwExeFile1.filePath()
            subprocess.call([external_program_path, "arg1", "arg2"])
            #self.dlg.pbCalculateTopoindex1.hide()
        except Exception as e:
            print(f"Error running external program: {e}")

    def call_trigrs_exe_file(self):
        try:
            # Replace with the actual path to your external program
            external_program_path = "C:/TRIGRS/TRIGRS.exe"
            subprocess.call([external_program_path, "arg1", "arg2"])
        except Exception as e:
            print(f"Error running external program: {e}")



