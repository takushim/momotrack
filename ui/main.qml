import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

ApplicationWindow {
    title: "Hello World!"
    width: 640
    height: 480
    visible: true

    // menu 
    menuBar: MenuBar {
        Menu {
            title: "File"
            Action {text: "&Open"}
            Action {text: "&Exit"}
        }
    }

    RowLayout {
        spacing: 0
        margins: 5
        anchors.fill: parent
        Slider {
            orientation: Qt.Vertical
            from: 0
            to: 100
            value: 0
        }
        Canvas {
            width: 400
        }
        ColumnLayout {
            spacing: 0
            Layout.preferredWidth: 20
            Rectangle {
                implicitHeight: 20
                Layout.fillHeight: true
                Layout.fillWidth: true
                color: "darkGreen"
            }
            Rectangle {
                implicitHeight: 80
                Layout.fillHeight: true
                Layout.fillWidth: true
                color: "lightGreen"
            }
        }
    }
}
