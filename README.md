# AutoLoad
## for ECOM Flash Service
### Version: 0.3.4

**AutoLoad** is an automation tool designed to simplify the process of updating firmware on multiple devices using the ECOM Flash Service application. It provides an easy-to-use graphical user interface (GUI) for selecting COM ports and loader versions, enabling efficient and hassle-free firmware updates.

### Features:

1. **Intuitive GUI:** 
   - User-friendly interface with split-view layout
   - Real-time logging window for operation monitoring
   - Easy COM port selection with device status display
   - Simple loader version selection via dropdown menu

2. **Multi-Device Support:** 
   - Configure and update multiple devices simultaneously
   - Real-time device status monitoring
   - Automatic unused device detection
   - Parallel update execution in separate threads

3. **Dynamic Loader Versions:** 
   - Automatic detection of available loader versions
   - Support for new loader versions without application changes
   - Version compatibility checking

4. **Advanced Features:**
   - Test mode for simulation and debugging
   - Command-line interface for version display
   - Comprehensive error handling and reporting
   - Operation logging with detailed status updates

### Installation:

1. Download both `AutoLoad.exe` and `script.bat` from the latest release
2. Place both files in the same directory
3. Run `AutoLoad.exe`

### Usage:

1. Launch AutoLoad by running the executable
2. Select the COM ports to update by checking the corresponding checkboxes
3. Choose the desired loader version from the dropdown menu
4. Click the "Update" button to start the update process
5. Monitor the progress in the log window

Additional command-line options:
```bash
AutoLoad.exe --version  # Display version
AutoLoad.exe --test     # Run in test mode
```

### System Requirements:

- Windows operating system
- Network access to firmware repository location

### Feedback and Support:

For any questions, issues, or feedback, please contact [filip.balakovski@gmail.com](mailto:filip.balakovski@gmail.com).

Thank you for using AutoLoad! We hope it simplifies your firmware update process and enhances your user experience.

---

**AutoLoad** is brought to you by Filip Balakovski
