import sys
import os
import serial.tools.list_ports
import subprocess
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QComboBox

AL_VERSION = '0.2'

# Serial communication functions
def get_firmware_version(com_port, version_label):
    try:
        ser = serial.Serial(com_port, baudrate=57600, bytesize=8, parity='N', stopbits=1, timeout=1)
        ser.write("#SWr\r\n".encode())
        response = ser.readline().decode().strip()
        ser.close()
        firmware_version = response[3:] if response.startswith("SWr") else "Unknown"
        version_label.setText(f'Firmware: {firmware_version}')  # Update version label
    except PermissionError:
        version_label.setText("Firmware: In Use")
    except Exception as e:
        print(f"Error accessing COM port {com_port}: {e}")
        version_label.setText("Firmware: Access Denied")

# Utility functions
def filter_com_ports(ports, keyword):
    return [port for port in ports if keyword in port.description]

def get_com_port_numbers(ports):
    return [int(port.device.split('COM')[1]) for port in ports]

class BatchExecutionThread(threading.Thread):
    def __init__(self, com_ports, batch_file, selected_version, gui):
        super().__init__()
        self.com_ports = com_ports
        self.batch_file = batch_file
        self.selected_version = selected_version
        self.gui = gui
        self.stop_execution = False

    def run(self):
        processes = []
        for com_port in self.com_ports:
            if self.stop_execution:
                print("Execution stopped by user.")
                break
            process = subprocess.Popen([self.batch_file, str(com_port), str(self.selected_version)])
            processes.append(process)

        for process in processes:
            process.wait()  # Wait for each process to complete

        self.gui.execution_complete()

class COMPortSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.versions = []
        self.comport_checkboxes = []
        self.version_labels = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'AutoLoad v{AL_VERSION}')
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        select_all_checkbox = QCheckBox('Select All', self)
        select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        layout.addWidget(select_all_checkbox)

        hbox = QHBoxLayout()  # Horizontal layout for version selection
        self.version_combo = QComboBox(self)
        hbox.addWidget(self.version_combo)

        scan_button = QPushButton('Scan Firmware Versions', self)
        scan_button.clicked.connect(self.scan_firmware_versions)
        hbox.addWidget(scan_button)

        layout.addLayout(hbox)

        for com_port in self.scan_firmware_versions():
            hbox = QHBoxLayout()  # Horizontal layout for each COM port entry

            checkbox = QCheckBox(f'COM{com_port}', self)
            hbox.addWidget(checkbox)
            self.comport_checkboxes.append(checkbox)

            version_label = QLabel()  # Version label
            hbox.addWidget(version_label)
            self.version_labels.append(version_label)

            layout.addLayout(hbox)  # Add the horizontal layout to the main layout

        confirm_button = QPushButton('Update', self)
        confirm_button.clicked.connect(self.start_execution)
        layout.addWidget(confirm_button)

        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(self.exit_application)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def toggle_select_all(self, state):
        for checkbox in self.comport_checkboxes:
            checkbox.setChecked(state == 2)

    def scan_firmware_versions(self):
        keyword = "Exar"
        available_ports = list(serial.tools.list_ports.comports())
        filtered_ports = filter_com_ports(available_ports, keyword)
        com_port_numbers = sorted(get_com_port_numbers(filtered_ports))

        loader_versions = []
        loader_directory = "W:\\Sestavy_elektro\\Detektory\\Toy18_Baby18_serie\\Boards\\AMY17\\Rev_1\\Common\\Firmware\\MCU"
        for entry in os.listdir(loader_directory):
            if entry.startswith("v") and entry[1:].isdigit():
                loader_versions.append(int(entry[1:]))

        loader_versions = sorted(loader_versions, reverse=True)

        self.version_combo.addItems([f'Loader v{version}' for version in loader_versions])

        for com_port, version_label in zip(com_port_numbers, self.version_labels):
            threading.Thread(target=get_firmware_version, args=(f"COM{com_port}", version_label)).start()

        self.versions = loader_versions
        return com_port_numbers

    def start_execution(self):
        print("Updating firmware...")
        selected_ports = [com_port for com_port, checkbox in zip(self.scan_firmware_versions(), self.comport_checkboxes) if checkbox.isChecked()]
        selected_version_text = self.version_combo.currentText()
        selected_version = int(selected_version_text.split()[-1].lstrip('v'))

        if selected_ports and selected_version:
            self.execution_thread = BatchExecutionThread(selected_ports, "script.bat", selected_version, self)
            self.execution_thread.start()  # Start the execution thread
        else:
            print("No COM ports or loader version selected for update.")

    def execution_complete(self):
        self.execution_thread = None

    def exit_application(self):
        print("Closing AutoLoad...")
        sys.exit()


if __name__ == "__main__":
    print("Opening AutoLoad...")
    app = QApplication(sys.argv)
    window = COMPortSelectionWidget()
    window.show()
    sys.exit(app.exec_())
