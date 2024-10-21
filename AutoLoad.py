import sys
import os
import serial.tools.list_ports
import subprocess
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QComboBox, QTextEdit, QScrollArea

NAME_AUTOLOAD = 'AutoLoad'
VERSION_AUTOLOAD = '0.3.4'
TEST_MODE = False

TEST_FIRMWARE_VERSIONS = {
	1: "137", 2: "137", 3: "137", 4: "137", 5: "137", 6: "137", 7: "137", 8: "137",
	9: "138", 10: "138", 11: "138", 12: "138", 13: "138", 14: "138", 15: "138", 16: "138",
	17: "139", 18: "139", 19: "139", 20: "139", 21: "139", 22: "139", 23: "139", 24: "139"
}

class COMPortSelectionWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.versions = []
		self.comport_checkboxes = []
		self.version_labels = []
		self.unused_device_count = 0
		self.unused_device_label = QLabel()
		self.log_text_edit = QTextEdit()
		self.log_text_edit.setReadOnly(True)
		self.initial_scan_done = False
		self.initUI()

	def initUI(self):
		self.setWindowTitle(f'{NAME_AUTOLOAD} v{VERSION_AUTOLOAD}')
		self.setGeometry(100, 100, 800, 600)

		main_layout = QHBoxLayout()
		left_layout = QVBoxLayout()
		right_layout = QVBoxLayout()

		select_all_checkbox = QCheckBox('Select All', self)
		select_all_checkbox.stateChanged.connect(self.toggle_select_all)
		left_layout.addWidget(select_all_checkbox)

		hbox = QHBoxLayout()
		self.version_combo = QComboBox(self)
		hbox.addWidget(self.version_combo)

		scan_button = QPushButton('Scan Firmware Versions', self)
		scan_button.clicked.connect(self.scan_firmware_versions)
		hbox.addWidget(scan_button)

		left_layout.addLayout(hbox)
		left_layout.addWidget(self.unused_device_label)

		scroll_area = QScrollArea()
		scroll_widget = QWidget()
		scroll_layout = QVBoxLayout(scroll_widget)

		for com_port in self.scan_firmware_versions():
			hbox = QHBoxLayout()
			checkbox = QCheckBox(f'COM{com_port}', self)
			hbox.addWidget(checkbox)
			self.comport_checkboxes.append(checkbox)
			version_label = QLabel()
			hbox.addWidget(version_label)
			self.version_labels.append(version_label)
			scroll_layout.addLayout(hbox)

		scroll_area.setWidget(scroll_widget)
		scroll_area.setWidgetResizable(True)
		left_layout.addWidget(scroll_area)

		right_layout.addWidget(QLabel("Log:"))
		right_layout.addWidget(self.log_text_edit)

		confirm_button = QPushButton('Update', self)
		confirm_button.clicked.connect(self.start_execution)
		right_layout.addWidget(confirm_button)

		exit_button = QPushButton('Exit', self)
		exit_button.clicked.connect(self.exit_application)
		right_layout.addWidget(exit_button)

		main_layout.addLayout(left_layout, 2)
		main_layout.addLayout(right_layout, 1)

		self.setLayout(main_layout)

	def log(self, message):
		self.log_text_edit.append(message)
		self.log_text_edit.verticalScrollBar().setValue(self.log_text_edit.verticalScrollBar().maximum())

	def toggle_select_all(self, state):
		for checkbox in self.comport_checkboxes:
			checkbox.setChecked(state == 2)

	def scan_firmware_versions(self):
		self.unused_device_count = 0
		current_version = self.version_combo.currentText()
		if TEST_MODE:
			com_port_numbers = list(range(1, 25))
			loader_versions = [137, 138, 139]
			if not self.initial_scan_done:
				self.log("Test Mode: Simulating 24 COM ports and 3 firmware versions")
		else:
			keyword = "Exar"
			available_ports = list(serial.tools.list_ports.comports())
			filtered_ports = filter_com_ports(available_ports, keyword)
			com_port_numbers = sorted(get_com_port_numbers(filtered_ports))
			
			loader_versions = []
			loader_directory = "W:\\Sestavy_elektro\\Detektory\\Toy18_Baby18_serie\\Boards\\AMY17\\Firmware\\MCU"
			try:
				for entry in os.listdir(loader_directory):
					if entry.startswith("v") and entry[1:].isdigit():
						loader_versions.append(int(entry[1:]))

				loader_versions = sorted(loader_versions, reverse=True)
			
			except FileNotFoundError:
				self.log(f"Warning: Directory '{loader_directory}' not found.")
			except Exception as e:
				self.log(f"Error loading firmware versions: {str(e)}")

		if not self.initial_scan_done:
			self.version_combo.clear()
			if not loader_versions:
				self.version_combo.addItem("No versions found")
				if not self.initial_scan_done:
					self.log("No firmware versions found.")
			else:
				self.version_combo.addItems([f'Loader v{version}' for version in loader_versions])
				if not self.initial_scan_done:
					self.log(f"Found {len(loader_versions)} firmware versions.")
		
		index = self.version_combo.findText(current_version)
		if index >= 0:
			self.version_combo.setCurrentIndex(index)

		for com_port, version_label in zip(com_port_numbers, self.version_labels):
			threading.Thread(target=self.get_firmware_version, args=(f"COM{com_port}", version_label, loader_versions)).start()

		self.versions = loader_versions
		self.unused_device_label.setText(f"Unused Devices: {self.unused_device_count}")
		self.initial_scan_done = True
		return com_port_numbers

	def get_firmware_version(self, com_port, version_label, loader_versions):
		if TEST_MODE:
			port_number = int(com_port.replace("COM", ""))
			firmware_version = TEST_FIRMWARE_VERSIONS.get(port_number, "Unknown")
			self.unused_device_count += 1
		else:
			try:
				ser = serial.Serial(com_port, baudrate=57600, bytesize=8, parity='N', stopbits=1, timeout=1)
				ser.write("#SWr\r\n".encode())
				response = ser.readline().decode().strip()
				ser.close()
				firmware_version = response[3:] if response.startswith("SWr") else "Unknown"
				if firmware_version != "Unknown":
					self.unused_device_count += 1
			except PermissionError:
				firmware_version = "In Use"
				self.log(f"Error: {com_port} is in use and cannot be accessed.")
			except Exception as e:
				firmware_version = "Access Denied"
				self.log(f"Error accessing {com_port}: {e}")

		version_label.setText(f'Firmware: {firmware_version}')
		self.unused_device_label.setText(f"Unused Devices: {self.unused_device_count}")

	def start_execution(self):
		self.log("Updating firmware...")
		selected_ports = [com_port for com_port, checkbox in zip(self.scan_firmware_versions(), self.comport_checkboxes) if checkbox.isChecked()]
		selected_version_text = self.version_combo.currentText()
		
		try:
			selected_version = int(selected_version_text.split()[-1].lstrip('v'))
		except ValueError:
			self.log("Unable to get firmware version. Update will not start.")
			return

		if selected_ports and selected_version:
			if TEST_MODE:
				self.log(f"Test Mode: Simulating update for ports: {selected_ports} with version {selected_version}")
				for port in selected_ports:
					TEST_FIRMWARE_VERSIONS[port] = str(selected_version)
					self.log(f"Simulating update for COM{port}...")
					self.log(f"COM{port} update completed successfully.")
				self.log("All updates completed.")
			else:
				self.execution_thread = BatchExecutionThread(selected_ports, "script.bat", selected_version, self)
				self.execution_thread.start()
		else:
			self.log("No COM ports or loader version selected for update.")

	def execution_complete(self):
		self.log("Execution completed.")
		self.execution_thread = None

	def exit_application(self):
		self.log("Closing AutoLoad...")
		sys.exit()

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
			process.wait()  

		self.gui.execution_complete()

def print_version():
	print(f"{NAME_AUTOLOAD} v{VERSION_AUTOLOAD}")

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] == '--version':
			print_version()
			sys.exit(0)
		elif sys.argv[1] == '--test':
			TEST_MODE = True
		else:
			print(f"Unknown argument: {sys.argv[1]}")
			print("Usage: python AutoLoad.py [--version] [--test]")
			sys.exit(1)
	
	app = QApplication(sys.argv)
	window = COMPortSelectionWidget()
	window.show()
	sys.exit(app.exec_())