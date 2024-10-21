import sys
import os
import serial.tools.list_ports
import subprocess
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QComboBox

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
        for com_port in self.com_ports:
            if self.stop_execution:
                print("Execution stopped by user.")
                break
            subprocess.call([self.batch_file, str(com_port), str(self.selected_version)])
        self.gui.execution_complete()

class COMPortSelectionWidget(QWidget):
    def __init__(self, com_ports, versions):
        super().__init__()
        self.com_ports = com_ports
        self.versions = versions
        self.version_combo = QComboBox(self)  # Define version_combo as an instance variable
        self.initUI()
        self.execution_thread = None

    def initUI(self):
        self.setWindowTitle('AutoLoad v0.1')
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.comport_checkboxes = []
        select_all_checkbox = QCheckBox('Select All', self)
        select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        layout.addWidget(select_all_checkbox)

        for com_port in self.com_ports:
            checkbox = QCheckBox(f'COM{com_port}', self)
            self.comport_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        self.version_combo.addItems([f'Loader v{version}' for version in self.versions])
        layout.addWidget(self.version_combo)

        confirm_button = QPushButton('Confirm', self)
        confirm_button.clicked.connect(self.start_execution)
        layout.addWidget(confirm_button)

        stop_button = QPushButton('Stop', self)
        stop_button.clicked.connect(self.stop_execution_signal)
        layout.addWidget(stop_button)

        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(self.exit_application)
        layout.addWidget(exit_button)

        self.setLayout(layout)
        
    def toggle_select_all(self, state):
        for checkbox in self.comport_checkboxes:
            checkbox.setChecked(state == 2)

    def stop_execution_signal(self):
        if self.execution_thread:
            self.execution_thread.stop_execution = True

    def start_execution(self):
        selected_ports = [com_port for com_port, checkbox in zip(self.com_ports, self.comport_checkboxes) if checkbox.isChecked()]
        selected_version_text = self.version_combo.currentText()  # Get the selected version text
        selected_version = int(selected_version_text.split()[-1].lstrip('v'))

        if selected_ports and selected_version:
            for com_port in selected_ports:
                subprocess.Popen(['script.bat', str(com_port), str(selected_version)])
        else:
            print("No COM ports or loader version selected for update.")

    def execution_complete(self):
        self.execution_thread = None
        print("Loading complete.")

    def exit_application(self):
        sys.exit()

if __name__ == "__main__":
    available_ports = list(serial.tools.list_ports.comports())

    if not available_ports:
        print("No COM ports found.")
    else:
        keyword = "Exar"  # The keyword to search for in the description
        filtered_ports = filter_com_ports(available_ports, keyword)
        
        if not filtered_ports:
            print(f"No COM ports with '{keyword}' in description found.")
        else:
            com_port_numbers = sorted(get_com_port_numbers(filtered_ports))  # Sort by COM port numbers

            # Specify the available loader versions dynamically from the directory
            loader_versions = []
            loader_directory = "W:\\Sestavy_elektro\\Detektory\\Toy18_Baby18_serie\\Boards\\AMY17\\Rev_1\\Common\\Firmware\\MCU"
            for entry in os.listdir(loader_directory):
                if entry.startswith("v") and entry[1:].isdigit():
                    loader_versions.append(int(entry[1:]))

            # Sort the loader versions from highest to lowest
            loader_versions = sorted(loader_versions, reverse=True)

            app = QApplication(sys.argv)
            window = COMPortSelectionWidget(com_port_numbers, loader_versions)
            window.show()
            sys.exit(app.exec_())
