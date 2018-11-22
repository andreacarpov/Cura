// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.1

import UM 1.1 as UM
import Cura 1.0 as Cura

Button
{
    id: machineSelectorButton

    width: parent.width
    height: UM.Theme.getSize("action_button").height
    leftPadding: Math.round(1.5 * UM.Theme.getSize("default_margin").width)
    rightPadding: Math.round(1.5 * UM.Theme.getSize("default_margin").width)
    checkable: true

    property var outputDevice: null
    property var printerTypesList: []

    function setPrinterTypesList()
    {
        printerTypesList = (checked && (outputDevice != null)) ? outputDevice.uniquePrinterTypes : []
    }

    contentItem: Item
    {
        width: machineSelectorButton.width - machineSelectorButton.leftPadding
        height: UM.Theme.getSize("action_button").height

        Label
        {
            id: buttonText
            anchors
            {
                left: parent.left
                right: printerTypes.left
                verticalCenter: parent.verticalCenter
            }
            text: machineSelectorButton.text
            color: UM.Theme.getColor("text")
            font: UM.Theme.getFont("action_button")
            visible: text != ""
            renderType: Text.NativeRendering
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        Row
        {
            id: printerTypes
            width: childrenRect.width

            anchors
            {
                right: parent.right
                verticalCenter: parent.verticalCenter
            }
            spacing: UM.Theme.getSize("narrow_margin").width

            Repeater
            {
                model: printerTypesList
                delegate: Cura.PrinterTypeLabel
                {
                    text: Cura.MachineManager.getAbbreviatedMachineName(modelData)
                }
            }
        }
    }

    background: Rectangle
    {
        id: backgroundRect
        color: machineSelectorButton.hovered ? UM.Theme.getColor("action_button_hovered") : "transparent"
        radius: UM.Theme.getSize("action_button_radius").width
        border.width: UM.Theme.getSize("default_lining").width
        border.color: machineSelectorButton.checked ? UM.Theme.getColor("primary") : "transparent"
    }

    onClicked:
    {
        togglePopup()
        Cura.MachineManager.setActiveMachine(model.id)
    }

    MouseArea
    {
        id: mouseArea
        anchors.fill: parent
        onPressed: mouse.accepted = false
        hoverEnabled: true
    }

    Connections
    {
        target: outputDevice
        onUniqueConfigurationsChanged: setPrinterTypesList()
    }

    Connections
    {
        target: Cura.MachineManager
        onOutputDevicesChanged: setPrinterTypesList()
    }

    Component.onCompleted: setPrinterTypesList()
}
