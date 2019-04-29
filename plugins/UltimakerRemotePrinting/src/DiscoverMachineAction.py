# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import os.path

from cura.CuraApplication import CuraApplication
from cura.MachineAction import MachineAction
from PyQt5.QtCore import pyqtSignal, pyqtProperty, pyqtSlot, QObject
from UM.i18n import i18nCatalog
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry
from typing import Optional, TYPE_CHECKING

catalog = i18nCatalog("cura")

# This class is responsible for creating the discovery pop up, but does no actual logic itself.
# It's just for exposing stuff to QML
# TODO: What is a machine action?
class DiscoverUM3Action(MachineAction):

    def __init__(self) -> None:
        super().__init__("DiscoverUM3Action", catalog.i18nc("@action","Connect via Network"))
        self._qml_url = "resources/qml/DiscoverMachineAction.qml"
        self._plugin = None #type: Optional[UlitmakerOutputDevicePlugin]
        self._app = CuraApplication.getInstance()
        self._devices = []

    ##  This is an internal-only signal which is emitted when the main plugin discovers devices.
    #   Its only purpose is to update properties exposed to QML. Do not connect it anywhere else!
    discoveredDevicesChanged = pyqtSignal()

    ##  Emit the discoveredDevicesChanged signal when the main plugin discovers devices.
    def _onDeviceDiscovered(self) -> None:
        self.discoveredDevicesChanged.emit()



    # QML Slots & Properties
    # ==============================================================================================

    ##  Trigger the plugin's startDiscovery method from QML.
    @pyqtSlot()
    def startDiscovery(self) -> None:
        Logger.log("d", "Starting device discovery.")
        
        if not self._plugin:
            self._plugin = self._app.getOutputDeviceManager().getOutputDevicePlugin("UltimakerRemotePrinting")
        self._plugin.deviceDiscovered.connect(self._onDeviceDiscovered)
        self._plugin.start()

    # TODO: From here on down, everything is just a wrapper for the main plugin, needlessly adding
    # complexity. The plugin itself should be able to expose these things to QML without using these
    # wrapper functions.

    ##  Associate the currently active machine with the given printer device. The network connection
    #   information will be stored into the metadata of the currently active machine.
    #   TODO: This should be an API call
    @pyqtSlot(QObject)
    def associateActiveMachineWithPrinterDevice(self, printer_device: Optional["PrinterOutputDevice"]) -> None:
        if self._plugin:
            self._plugin.associateActiveMachineWithPrinterDevice(printer_device)

    @pyqtSlot(result = str)
    def getLastManualEntryKey(self) -> str:
        if self._plugin:
            return self._plugin.getLastManualDevice()
        return ""
    
    ##  List of discovered devices.
    @pyqtProperty("QVariantList", notify = discoveredDevicesChanged)
    def discoveredDevices(self): # TODO: Typing!
        if not self._plugin:
            self._plugin = self._app.getOutputDeviceManager().getOutputDevicePlugin("UltimakerRemotePrinting")
        devices = list(self._plugin.getDiscoveredLocalDevices().values())
        devices.sort(key = lambda k: k.name)
        return devices
        # return []

    ##  Re-filters the list of devices.
    @pyqtSlot()
    def reset(self):
        Logger.log("d", "Reset the list of found devices.")
        # if self._plugin:
            # self._plugin.resetLastManualDevice()
        self.discoveredDevicesChanged.emit()

    @pyqtSlot(str, str)
    def removeManualDevice(self, key, address):
        if not self._plugin:
            return

        self._plugin.removeManualDevice(key, address)

    @pyqtSlot(str, str)
    def setManualDevice(self, key, address):
        if key != "":
            # This manual printer replaces a current manual printer
            self._plugin.removeManualDevice(key)

        if address != "":
            self._plugin.addManualDevice(address)

    @pyqtSlot()
    def loadConfigurationFromPrinter(self) -> None:
        machine_manager = self._app.getMachineManager()
        hotend_ids = machine_manager.printerOutputDevices[0].hotendIds
        for index in range(len(hotend_ids)):
            machine_manager.printerOutputDevices[0].hotendIdChanged.emit(index, hotend_ids[index])
        material_ids = machine_manager.printerOutputDevices[0].materialIds
        for index in range(len(material_ids)):
            machine_manager.printerOutputDevices[0].materialIdChanged.emit(index, material_ids[index])
    
    @pyqtSlot()
    def restartDiscovery(self):
        self.startDiscovery()