"""
3decision Plugin GUI v1.0

Main panel and interface components for the 3decision Maestro plugin.

Version: 1.0
"""

import os
import sys
import json
import tempfile
from typing import Optional, Dict, List, Any

# Import Schrodinger modules
try:
    from schrodinger.ui.qt.appframework2 import af2
    from schrodinger.ui.qt import swidgets
    from schrodinger.Qt import QtWidgets, QtCore, QtGui
    from schrodinger.Qt.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
        QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QHeaderView,
        QProgressBar, QCheckBox, QAbstractItemView, QTabWidget, QWidget,
        QFormLayout, QComboBox, QFrame, QDialogButtonBox
    )
    from schrodinger.Qt.QtCore import Qt, QThread, pyqtSignal
    from schrodinger.Qt.QtGui import QPixmap, QIcon
    from schrodinger import maestro, structure
    MAESTRO_AVAILABLE = True
    SWIDGETS_AVAILABLE = True
except ImportError:
    # Fallback for testing outside Maestro
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
        QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QHeaderView,
        QProgressBar, QCheckBox, QAbstractItemView, QTabWidget, QWidget,
        QFormLayout, QComboBox, QFrame, QDialogButtonBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QPixmap, QIcon
    MAESTRO_AVAILABLE = False
    SWIDGETS_AVAILABLE = False
    af2 = None
    swidgets = None

# Import api_client - try relative import first, then absolute
try:
    from .api_client import ThreeDecisionAPIClient, is_logging_enabled, get_private_structure_naming_attribute
except ImportError:
    from api_client import ThreeDecisionAPIClient, is_logging_enabled, get_private_structure_naming_attribute


# Dark theme stylesheet matching Maestro's dark UI
DARK_STYLESHEET = """
    * {
        background-color: #444444;
        color: #ECECEC;
    }
    QWidget, QFrame, QDialog {
        background-color: #444444;
        color: #ECECEC;
    }
    QLabel {
        background-color: transparent;
        color: #ECECEC;
    }
    QStatusBar {
        background-color: #3a3a3a;
        color: #ECECEC;
        border-top: 1px solid #555555;
    }
    QLineEdit {
        background-color: #3a3a3a;
        color: #ECECEC;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 4px 6px;
        selection-background-color: #60B0DC;
    }
    QLineEdit:focus {
        border: 1px solid #60B0DC;
    }
    QLineEdit:disabled {
        background-color: #383838;
        color: #888888;
    }
    QLineEdit::placeholder {
        color: #888888;
    }
    QComboBox {
        background-color: #3a3a3a;
        color: #ECECEC;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 4px 6px;
    }
    QComboBox:hover, QComboBox:focus {
        border: 1px solid #60B0DC;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #ECECEC;
        margin-right: 6px;
    }
    QComboBox QAbstractItemView {
        background-color: #3a3a3a;
        color: #ECECEC;
        selection-background-color: #60B0DC;
        border: 1px solid #555555;
    }
    QPushButton {
        background-color: #505050;
        color: #ECECEC;
        border: 1px solid #606060;
        border-radius: 3px;
        padding: 5px 12px;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #585858;
        border: 1px solid #60B0DC;
    }
    QPushButton:pressed {
        background-color: #404040;
    }
    QPushButton:disabled {
        background-color: #3a3a3a;
        color: #666666;
        border: 1px solid #4a4a4a;
    }
    QCheckBox {
        background-color: transparent;
        color: #ECECEC;
        spacing: 6px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #555555;
        border-radius: 2px;
        background-color: #3a3a3a;
    }
    QCheckBox::indicator:checked {
        background-color: #60B0DC;
        border-color: #60B0DC;
    }
    QCheckBox::indicator:hover {
        border-color: #60B0DC;
    }
    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #444444;
        border-radius: 3px;
    }
    QTabBar::tab {
        background-color: #3a3a3a;
        color: #ABABAB;
        border: 1px solid #555555;
        border-bottom: none;
        padding: 6px 16px;
        margin-right: 2px;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }
    QTabBar::tab:selected {
        background-color: #444444;
        color: #ECECEC;
        border-bottom: 1px solid #444444;
    }
    QTabBar::tab:hover:!selected {
        background-color: #404040;
        color: #ECECEC;
    }
    QTableWidget {
        background-color: #3a3a3a;
        color: #ECECEC;
        gridline-color: #555555;
        border: 1px solid #555555;
        selection-background-color: #60B0DC;
        selection-color: #FFFFFF;
    }
    QTableWidget::item {
        padding: 4px;
    }
    QTableWidget::item:selected {
        background-color: #60B0DC;
        color: #FFFFFF;
    }
    QHeaderView::section {
        background-color: #4a4a4a;
        color: #ECECEC;
        padding: 5px;
        border: none;
        border-right: 1px solid #555555;
        border-bottom: 1px solid #555555;
    }
    QHeaderView::section:hover {
        background-color: #555555;
    }
    QProgressBar {
        background-color: #3a3a3a;
        border: 1px solid #555555;
        border-radius: 3px;
        text-align: center;
        color: #ECECEC;
    }
    QProgressBar::chunk {
        background-color: #60B0DC;
        border-radius: 2px;
    }
    QScrollBar:vertical {
        background-color: #3a3a3a;
        width: 12px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #606060;
        min-height: 20px;
        border-radius: 3px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #707070;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        background-color: #3a3a3a;
        height: 12px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background-color: #606060;
        min-width: 20px;
        border-radius: 3px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #707070;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    QDialogButtonBox QPushButton {
        min-width: 70px;
    }
    QFrame[frameShape="4"], QFrame[frameShape="5"] {
        background-color: #555555;
    }
"""


class NumericTableWidgetItem(QTableWidgetItem):
    """Custom QTableWidgetItem that sorts numerically instead of alphabetically"""
    def __init__(self, text, numeric_value):
        super().__init__(text)
        self.numeric_value = numeric_value

    def __lt__(self, other):
        """Override less-than comparison for sorting"""
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        return super().__lt__(other)


def log_debug(message):
    """Log a debug message if logging is enabled"""
    if is_logging_enabled():
        print(f"DEBUG: {message}")

def log_error(message):
    """Log an error message if logging is enabled"""
    if is_logging_enabled():
        print(f"ERROR: {message}")

def log_info(message):
    """Log an info message if logging is enabled"""
    if is_logging_enabled():
        print(f"INFO: {message}")


class SearchThread(QThread):
    """Thread for handling search operations"""
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, api_client: ThreeDecisionAPIClient, search_query: str):
        super().__init__()
        self.api_client = api_client
        self.search_query = search_query

    def run(self):
        try:
            self.status_update.emit("Submitting search...")
            job_response = self.api_client.submit_search(self.search_query)

            if not job_response:
                self.error_occurred.emit("Failed to submit search")
                return

            if 'structures_info' in job_response:
                structures = job_response['structures_info']
                self.status_update.emit(f"Search completed. Found {len(structures)} structures.")
                self.results_ready.emit(structures)
                return

            if job_response.get('polling_needed'):
                job_id = job_response.get('id')
                queue_name = job_response.get('queue', 'basicSearch')

                if not job_id:
                    self.error_occurred.emit("No job ID received from search")
                    return

                self.status_update.emit(f"Job submitted (ID: {job_id}). Waiting for completion...")

                max_attempts = 60
                attempt = 0

                while attempt < max_attempts:
                    try:
                        result = self.api_client.get_job_status(queue_name, job_id)

                        if result:
                            progress = result.get('progress', 0)
                            self.status_update.emit(f"Search progress: {progress}%")

                            structure_ids = []
                            if 'returnvalue' in result and 'STRUCTURE_ID' in result['returnvalue']:
                                structure_ids = result['returnvalue']['STRUCTURE_ID']

                            if progress == 100 or (isinstance(structure_ids, list) and len(structure_ids) == 0 and progress > 0):
                                if structure_ids:
                                    self.status_update.emit("Fetching structure details...")
                                    structures = self.api_client.get_structures_info(structure_ids)
                                    self.results_ready.emit(structures)
                                else:
                                    self.status_update.emit("Search completed with no results.")
                                    self.results_ready.emit([])
                                return
                            elif result.get('status') == 'failed':
                                self.error_occurred.emit("Search job failed")
                                return

                        self.msleep(2000)
                        attempt += 1

                    except Exception as e:
                        log_error(f"Polling error: {e}")
                        attempt += 1
                        self.msleep(2000)

                self.error_occurred.emit("Search timed out waiting for completion")
                return

            job_id = job_response.get('id')
            queue_name = job_response.get('queue', 'basicSearch')

            if not job_id:
                self.error_occurred.emit("No job ID received from search")
                return

            if job_response.get('status') == 'completed':
                structure_ids = job_response.get('result', [])
                if structure_ids:
                    self.status_update.emit("Fetching structure details...")
                    structures = self.api_client.get_structures_info(structure_ids)
                    self.results_ready.emit(structures)
                else:
                    self.results_ready.emit([])
                return

            self.status_update.emit(f"Polling for results (Job ID: {job_id})...")

            if job_id == 'direct':
                return

            max_attempts = 30
            attempt = 0

            while attempt < max_attempts:
                try:
                    result = self.api_client.get_job_status(queue_name, job_id)

                    if result and result.get('status') == 'completed':
                        structure_ids = result.get('result', [])
                        if structure_ids:
                            self.status_update.emit("Fetching structure details...")
                            structures = self.api_client.get_structures_info(structure_ids)
                            self.results_ready.emit(structures)
                        else:
                            self.results_ready.emit([])
                        return
                    elif result and result.get('status') == 'failed':
                        self.error_occurred.emit("Search job failed")
                        return

                except Exception as e:
                    log_error(f"Polling attempt {attempt + 1} failed: {e}")

                attempt += 1
                self.msleep(2000)

            self.error_occurred.emit("Search timed out")

        except Exception as e:
            self.error_occurred.emit(f"Search error: {str(e)}")


def get_object_name(external_code: str, label: str = None, source: str = None, title: str = None, internal_id: str = None) -> str:
    """
    Determine the best object name for a structure.

    Naming logic:
    - For public domain structures (RCSB PDB, PDB, AlphaFold, etc.): use external_code
    - For private/internal structures: use the attribute configured in settings
    """
    public_sources = [
        'rcsb', 'pdb', 'alphafold', 'uniprot', 'chembl', 'drugbank',
        'pubchem', 'zinc', 'emdb', 'wwpdb'
    ]

    is_public = False
    if source:
        source_lower = source.lower()
        is_public = any(ps in source_lower for ps in public_sources)

    if is_public:
        name = external_code
    else:
        naming_attr = get_private_structure_naming_attribute()

        if naming_attr == 'label' and label and label.strip() and label.lower() not in ['n/a', 'null', 'none', '']:
            name = label.strip()
        elif naming_attr == 'title' and title and title.strip() and title.lower() not in ['n/a', 'null', 'none', '']:
            name = title.strip()
        elif naming_attr == 'internal_id' and internal_id and internal_id.strip() and internal_id.lower() not in ['n/a', 'null', 'none', '']:
            name = internal_id.strip()
        else:
            name = external_code

    if name.lower().startswith('3dec_'):
        name = name[5:]

    # Sanitize name (alphanumeric with underscores)
    sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)

    if not sanitized:
        sanitized = external_code if external_code else 'structure'

    return sanitized


class LoadStructureThread(QThread):
    """Thread for loading structures into Maestro"""
    structure_loaded = pyqtSignal(str, str)  # structure_id, object_name
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)
    all_structures_loaded = pyqtSignal()
    pdb_content_ready = pyqtSignal(str, str, dict)  # pdb_content, object_name, metadata

    def __init__(self, api_client: ThreeDecisionAPIClient, structure_data: List[Dict[str, str]]):
        super().__init__()
        self.api_client = api_client
        self.structure_data = structure_data

    def run(self):
        try:
            has_matrices = any(s.get('matrix') is not None for s in self.structure_data)

            if has_matrices:
                log_debug("Loading structures with transformation matrices using batch export")
                self.status_update.emit("Loading structures with transformations...")

                structures_with_transforms = []
                for structure_info in self.structure_data:
                    structure_id = int(structure_info['structure_id'])
                    external_code = structure_info['external_code']
                    matrix = structure_info.get('matrix')

                    identity_matrix = [
                        1.0, 0.0, 0.0, 0.0,
                        0.0, 1.0, 0.0, 0.0,
                        0.0, 0.0, 1.0, 0.0,
                        0.0, 0.0, 0.0, 1.0
                    ]

                    if matrix:
                        if isinstance(matrix, list) and len(matrix) == 4:
                            flat_matrix = []
                            for row in matrix:
                                if isinstance(row, list) and len(row) == 4:
                                    flat_matrix.extend(row)
                                else:
                                    log_error(f"Invalid matrix row format for structure {structure_id}")
                                    flat_matrix = None
                                    break

                            if flat_matrix and len(flat_matrix) == 16:
                                structures_with_transforms.append({
                                    "structure_id": structure_id,
                                    "external_code": external_code,
                                    "transform": flat_matrix
                                })
                            else:
                                structures_with_transforms.append({
                                    "structure_id": structure_id,
                                    "external_code": external_code,
                                    "transform": identity_matrix
                                })
                        else:
                            structures_with_transforms.append({
                                "structure_id": structure_id,
                                "external_code": external_code,
                                "transform": identity_matrix
                            })
                    else:
                        structures_with_transforms.append({
                            "structure_id": structure_id,
                            "external_code": external_code,
                            "transform": identity_matrix
                        })

                pdb_files_dict = self.api_client.export_structures_with_transforms(structures_with_transforms)

                if pdb_files_dict:
                    loaded_count = 0

                    for structure_info in self.structure_data:
                        structure_id = structure_info['structure_id']
                        external_code = structure_info['external_code']
                        label = structure_info.get('label')
                        source = structure_info.get('source')
                        title = structure_info.get('title')

                        internal_id = None
                        if get_private_structure_naming_attribute() == 'internal_id':
                            internal_id = self.api_client.get_structure_internal_id(structure_id)

                        object_name = get_object_name(external_code, label, source, title, internal_id)

                        pdb_content = None
                        for filename, content in pdb_files_dict.items():
                            filename_lower = filename.lower()
                            code_lower = external_code.lower()
                            if code_lower in filename_lower or filename_lower.replace('3dec_', '').startswith(code_lower):
                                pdb_content = content
                                log_debug(f"Matched {external_code} to file {filename}")
                                break

                        if not pdb_content and len(pdb_files_dict) == 1:
                            pdb_content = list(pdb_files_dict.values())[0]
                            log_debug(f"Using single PDB file for {external_code}")

                        if pdb_content:
                            metadata = {
                                '3decision_structure_id': structure_id,
                                '3decision_external_code': external_code,
                                '3decision_label': label or '',
                                '3decision_source': source or 'unknown'
                            }
                            self.pdb_content_ready.emit(pdb_content, object_name, metadata)
                            self.structure_loaded.emit(structure_id, object_name)
                            loaded_count += 1
                        else:
                            log_error(f"Could not find PDB content for {external_code}")
                            self.error_occurred.emit(f"Could not find PDB content for {external_code}")

                    if loaded_count == 0:
                        self.error_occurred.emit("Failed to load any structures")
                else:
                    self.error_occurred.emit("Failed to load structures with transformations")
            else:
                log_debug("Loading structures individually without transformations")
                for structure_info in self.structure_data:
                    structure_id = structure_info['structure_id']
                    external_code = structure_info['external_code']
                    label = structure_info.get('label')
                    source = structure_info.get('source')
                    title = structure_info.get('title')

                    self.status_update.emit(f"Loading structure {external_code} ({structure_id})...")

                    pdb_content = self.api_client.export_structure_pdb(structure_id)

                    if pdb_content:
                        internal_id = None
                        if get_private_structure_naming_attribute() == 'internal_id':
                            internal_id = self.api_client.get_structure_internal_id(structure_id)

                        object_name = get_object_name(external_code, label, source, title, internal_id)

                        metadata = {
                            '3decision_structure_id': structure_id,
                            '3decision_external_code': external_code,
                            '3decision_label': label or '',
                            '3decision_source': source or 'unknown'
                        }
                        self.pdb_content_ready.emit(pdb_content, object_name, metadata)
                        log_info(f"3decision Plugin: Loaded {object_name} with structure_id: {structure_id}")
                        self.structure_loaded.emit(structure_id, object_name)
                    else:
                        self.error_occurred.emit(f"Failed to load structure {external_code} ({structure_id})")

            self.all_structures_loaded.emit()

        except Exception as e:
            self.error_occurred.emit(f"Loading error: {str(e)}")


class SettingsDialog(QDialog):
    """Settings dialog for configuring 3decision API"""

    def __init__(self, api_client: ThreeDecisionAPIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.test_thread = None
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("3decision API Settings")
        self.setModal(True)
        self.setMinimumSize(500, 250)

        # Apply shared dark theme stylesheet
        self.setStyleSheet(DARK_STYLESHEET)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://your-3decision-api-url.discngine.cloud")
        self.url_input.setMinimumWidth(300)
        form_layout.addRow("3decision URL:", self.url_input)

        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Your API key")
        self.api_key_input.setMinimumWidth(300)
        form_layout.addRow("API Key:", self.api_key_input)

        # Log events checkbox
        self.log_events_checkbox = QCheckBox("Log events")
        self.log_events_checkbox.setToolTip("Enable logging of plugin events to console")
        form_layout.addRow("", self.log_events_checkbox)

        # Private structure naming attribute dropdown
        self.naming_attribute_combo = QComboBox()
        self.naming_attribute_combo.addItems(["label", "title", "external_code", "internal_id"])
        self.naming_attribute_combo.setToolTip(
            "Choose which attribute to use for naming private structures.\n"
            "Public structures (PDB, AlphaFold, etc.) always use external_code."
        )
        form_layout.addRow("Private structure name:", self.naming_attribute_combo)

        main_layout.addLayout(form_layout)

        # Test connection button
        test_layout = QHBoxLayout()
        test_layout.addStretch()

        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_button)

        main_layout.addLayout(test_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def load_current_settings(self):
        """Load current settings into the form"""
        if self.api_client.base_url:
            self.url_input.setText(self.api_client.base_url)
        if self.api_client.api_key:
            self.api_key_input.setText(self.api_client.api_key)

        try:
            from .api_client import is_logging_enabled, get_private_structure_naming_attribute
        except ImportError:
            from api_client import is_logging_enabled, get_private_structure_naming_attribute
        self.log_events_checkbox.setChecked(is_logging_enabled())

        naming_attr = get_private_structure_naming_attribute()
        index = self.naming_attribute_combo.findText(naming_attr)
        if index >= 0:
            self.naming_attribute_combo.setCurrentIndex(index)

    def test_connection(self):
        """Test the API connection"""
        url = self.url_input.text().strip()
        api_key = self.api_key_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a 3decision URL")
            return

        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key")
            return

        self.test_button.setEnabled(False)
        self.status_label.setText("Testing connection...")
        self.status_label.setStyleSheet("color: #60B0DC;")

        # Configure and test
        old_url = self.api_client.base_url
        old_key = self.api_client.api_key
        old_token = self.api_client.token

        self.api_client.configure(url, api_key)

        if self.api_client.test_connection():
            self.status_label.setText("Connection successful!")
            self.status_label.setStyleSheet("color: #7FBA7A; font-weight: bold;")
        else:
            self.status_label.setText("Connection failed. Please check your URL and API key.")
            self.status_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
            # Restore old settings
            self.api_client.base_url = old_url
            self.api_client.api_key = old_key
            self.api_client.token = old_token

        self.test_button.setEnabled(True)

    def save_settings(self):
        """Save the settings"""
        url = self.url_input.text().strip()
        api_key = self.api_key_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a 3decision URL")
            return

        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key")
            return

        # Configure and save API settings
        self.api_client.configure(url, api_key)
        self.api_client.save_config()

        # Save logging setting
        log_enabled = self.log_events_checkbox.isChecked()
        try:
            from .api_client import set_logging_enabled, set_private_structure_naming_attribute
        except ImportError:
            from api_client import set_logging_enabled, set_private_structure_naming_attribute
        set_logging_enabled(log_enabled)
        self.api_client.save_logging_setting(log_enabled)

        # Save private structure naming attribute setting
        naming_attr = self.naming_attribute_combo.currentText()
        set_private_structure_naming_attribute(naming_attr)
        self.api_client.save_naming_attribute_setting(naming_attr)

        # Try to login
        if self.api_client.login():
            QMessageBox.information(self, "Success", "Settings saved and login successful!")
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Warning",
                "Settings saved but login failed. Please check your credentials."
            )


# Main Panel Class
if MAESTRO_AVAILABLE and af2:
    class ThreeDecisionPanel(af2.App):
        """Main 3decision plugin panel for Maestro"""

        def setPanelOptions(self):
            """Set panel options"""
            super().setPanelOptions()
            self.title = "3decision Structure Search v1.0"
            self.maestro_dockable = True
            self.help_topic = ""
            self.ui = None

        def setup(self):
            """Set up the panel"""
            super().setup()
            self.api_client = ThreeDecisionAPIClient()
            self.search_thread = None
            self.load_thread = None
            self.all_results = []
            self.projects_data = []
            self.current_project_structures = []
            self.projects_loaded = False
            self.current_structure = None
            self.current_structure_id = None
            self.current_external_code = None
            self.current_transform_matrix = None

        def layOut(self):
            """Lay out the panel widgets"""
            super().layOut()
            main_layout = self.main_layout

            # Apply dark theme stylesheet to main panel
            self.setStyleSheet(DARK_STYLESHEET)

            # Force dark background using palette
            dark_palette = QtGui.QPalette()
            dark_color = QtGui.QColor(68, 68, 68)  # #444444
            dark_palette.setColor(QtGui.QPalette.Window, dark_color)
            dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(58, 58, 58))
            dark_palette.setColor(QtGui.QPalette.AlternateBase, dark_color)
            dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(80, 80, 80))
            dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(236, 236, 236))
            dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(236, 236, 236))
            dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(236, 236, 236))
            dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(96, 176, 220))
            dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
            dark_palette.setColor(QtGui.QPalette.PlaceholderText, QtGui.QColor(136, 136, 136))  # #888888
            self.setPalette(dark_palette)
            self.setAutoFillBackground(True)

            # Also style the af2 status bar if it exists
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar.setStyleSheet("""
                    QStatusBar {
                        background-color: #3a3a3a;
                        color: #ECECEC;
                        border-top: 1px solid #555555;
                    }
                    QLabel {
                        color: #ECECEC;
                        background-color: transparent;
                    }
                    QPushButton, QToolButton {
                        background-color: #505050;
                        color: #ECECEC;
                        border: 1px solid #606060;
                        border-radius: 3px;
                        padding: 3px 8px;
                    }
                    QPushButton:hover, QToolButton:hover {
                        background-color: #585858;
                        border: 1px solid #60B0DC;
                    }
                    QProgressBar {
                        background-color: #3a3a3a;
                        border: 1px solid #555555;
                        border-radius: 3px;
                        text-align: center;
                        color: #ECECEC;
                    }
                    QProgressBar::chunk {
                        background-color: #60B0DC;
                    }
                """)

            # Also style the bottom bar if it exists
            if hasattr(self, 'bottom_bar') and self.bottom_bar:
                self.bottom_bar.setStyleSheet("""
                    QWidget {
                        background-color: #3a3a3a;
                        color: #ECECEC;
                    }
                    QPushButton, QToolButton {
                        background-color: #505050;
                        color: #ECECEC;
                        border: 1px solid #606060;
                        border-radius: 3px;
                        padding: 4px 10px;
                    }
                    QPushButton:hover, QToolButton:hover {
                        background-color: #585858;
                        border: 1px solid #60B0DC;
                    }
                    QLabel {
                        color: #ECECEC;
                        background-color: transparent;
                    }
                """)

            # Style the bottom_line separator if it exists
            if hasattr(self, 'bottom_line') and self.bottom_line:
                self.bottom_line.setStyleSheet("background-color: #555555;")

            # Settings button
            settings_layout = QHBoxLayout()
            settings_layout.addStretch()

            self.settings_button = QPushButton("Settings")
            self.settings_button.clicked.connect(self.open_settings)
            settings_layout.addWidget(self.settings_button)

            main_layout.addLayout(settings_layout)

            # Tab widget
            self.tab_widget = QTabWidget()

            # Search tab
            self.search_widget = self._create_search_tab()
            self.tab_widget.addTab(self.search_widget, "Search")

            # Projects tab
            self.projects_widget = self._create_projects_tab()
            self.tab_widget.addTab(self.projects_widget, "Projects")

            # Associated Files tab
            self.files_widget = self._create_files_tab()
            self.tab_widget.addTab(self.files_widget, "Associated Files")

            main_layout.addWidget(self.tab_widget)

            # Status label
            self.status_label = QLabel("Not logged in")
            self.status_label.setStyleSheet("color: #FF6B6B; padding: 5px; background-color: #444444;")
            self.status_label.setAutoFillBackground(True)
            main_layout.addWidget(self.status_label)

            # Apply dark palette to all child widgets recursively
            self._apply_dark_palette_recursive(self)

            # Check login status
            self.check_login_status()

        def _apply_dark_palette_recursive(self, widget):
            """Apply dark palette to widget and all its children"""
            dark_palette = QtGui.QPalette()
            dark_color = QtGui.QColor(68, 68, 68)
            dark_palette.setColor(QtGui.QPalette.Window, dark_color)
            dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(58, 58, 58))
            dark_palette.setColor(QtGui.QPalette.AlternateBase, dark_color)
            dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(80, 80, 80))
            dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(236, 236, 236))
            dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(236, 236, 236))
            dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(236, 236, 236))
            dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(96, 176, 220))
            dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
            dark_palette.setColor(QtGui.QPalette.PlaceholderText, QtGui.QColor(136, 136, 136))  # #888888

            widget.setPalette(dark_palette)
            widget.setAutoFillBackground(True)

            for child in widget.findChildren(QWidget):
                child.setPalette(dark_palette)
                child.setAutoFillBackground(True)

        def _create_search_tab(self):
            """Create the search tab content"""
            widget = QWidget()
            layout = QVBoxLayout()

            # Search section
            search_layout = QHBoxLayout()

            search_layout.addWidget(QLabel("Search:"))
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Enter search term (e.g., ABL1)")
            self.search_input.returnPressed.connect(self.submit_search)
            search_layout.addWidget(self.search_input)

            self.submit_button = QPushButton("Submit")
            self.submit_button.clicked.connect(self.submit_search)
            self.submit_button.setEnabled(False)
            search_layout.addWidget(self.submit_button)

            layout.addLayout(search_layout)

            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            layout.addWidget(self.progress_bar)

            # Column filters
            filters_label = QLabel("Filter Results:")
            filters_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #ECECEC;")
            layout.addWidget(filters_label)

            filters_layout = QHBoxLayout()

            self.filter_external_code = QLineEdit()
            self.filter_external_code.setPlaceholderText("External Code")
            self.filter_external_code.textChanged.connect(self.apply_filters)
            filters_layout.addWidget(self.filter_external_code)

            self.filter_label = QLineEdit()
            self.filter_label.setPlaceholderText("Label")
            self.filter_label.textChanged.connect(self.apply_filters)
            filters_layout.addWidget(self.filter_label)

            self.filter_title = QLineEdit()
            self.filter_title.setPlaceholderText("Title")
            self.filter_title.textChanged.connect(self.apply_filters)
            filters_layout.addWidget(self.filter_title)

            self.filter_method = QLineEdit()
            self.filter_method.setPlaceholderText("Method")
            self.filter_method.textChanged.connect(self.apply_filters)
            filters_layout.addWidget(self.filter_method)

            self.filter_resolution = QLineEdit()
            self.filter_resolution.setPlaceholderText("Resolution (e.g., <2.0)")
            self.filter_resolution.textChanged.connect(self.apply_filters)
            filters_layout.addWidget(self.filter_resolution)

            self.filter_source = QLineEdit()
            self.filter_source.setPlaceholderText("Source")
            self.filter_source.textChanged.connect(self.apply_filters)
            filters_layout.addWidget(self.filter_source)

            clear_filters_btn = QPushButton("Clear")
            clear_filters_btn.clicked.connect(self.clear_filters)
            filters_layout.addWidget(clear_filters_btn)

            layout.addLayout(filters_layout)

            # Results table
            self.results_table = QTableWidget()
            self.results_table.setColumnCount(6)
            self.results_table.setHorizontalHeaderLabels([
                "External Code", "Label", "Title", "Method", "Resolution", "Source"
            ])
            self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.results_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.results_table.setAlternatingRowColors(True)
            self.results_table.setSortingEnabled(True)

            layout.addWidget(self.results_table)

            # Load button
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            self.load_button = QPushButton("Load Selected in Maestro")
            self.load_button.clicked.connect(self.load_selected_structures)
            self.load_button.setEnabled(False)
            button_layout.addWidget(self.load_button)

            layout.addLayout(button_layout)

            widget.setLayout(layout)
            return widget

        def _create_projects_tab(self):
            """Create the projects tab content"""
            widget = QWidget()
            layout = QVBoxLayout()

            layout.addWidget(QLabel("Browse and load structures from your 3decision projects"))

            # Projects table
            layout.addWidget(QLabel("Projects:"))

            # Projects filters
            projects_filters_layout = QHBoxLayout()

            self.projects_filter_name = QLineEdit()
            self.projects_filter_name.setPlaceholderText("Project Name")
            self.projects_filter_name.textChanged.connect(self.apply_projects_filters)
            projects_filters_layout.addWidget(self.projects_filter_name)

            self.projects_filter_owner = QLineEdit()
            self.projects_filter_owner.setPlaceholderText("Owner")
            self.projects_filter_owner.textChanged.connect(self.apply_projects_filters)
            projects_filters_layout.addWidget(self.projects_filter_owner)

            self.projects_filter_structures = QLineEdit()
            self.projects_filter_structures.setPlaceholderText("Structures (e.g., >10)")
            self.projects_filter_structures.textChanged.connect(self.apply_projects_filters)
            projects_filters_layout.addWidget(self.projects_filter_structures)

            self.projects_filter_id = QLineEdit()
            self.projects_filter_id.setPlaceholderText("Project ID")
            self.projects_filter_id.textChanged.connect(self.apply_projects_filters)
            projects_filters_layout.addWidget(self.projects_filter_id)

            clear_projects_filters_btn = QPushButton("Clear")
            clear_projects_filters_btn.clicked.connect(self.clear_projects_filters)
            projects_filters_layout.addWidget(clear_projects_filters_btn)

            layout.addLayout(projects_filters_layout)

            self.projects_table = QTableWidget()
            self.projects_table.setColumnCount(4)
            self.projects_table.setHorizontalHeaderLabels([
                "Project Name", "Owner", "Structures", "Project ID"
            ])

            header = self.projects_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.resizeSection(0, 200)
            header.resizeSection(1, 120)
            header.resizeSection(2, 80)
            header.resizeSection(3, 150)

            self.projects_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.projects_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.projects_table.setAlternatingRowColors(True)
            self.projects_table.setSortingEnabled(True)
            self.projects_table.itemSelectionChanged.connect(self.on_project_selection_changed)

            layout.addWidget(self.projects_table)

            # Projects buttons
            projects_buttons = QHBoxLayout()
            refresh_button = QPushButton("Refresh Projects")
            refresh_button.clicked.connect(self.load_projects_for_tab)
            projects_buttons.addWidget(refresh_button)
            projects_buttons.addStretch()
            layout.addLayout(projects_buttons)

            # Project structures list
            layout.addWidget(QLabel("Project Structures:"))

            # Project structures filters
            project_filters_layout = QHBoxLayout()

            self.project_filter_external_code = QLineEdit()
            self.project_filter_external_code.setPlaceholderText("External Code")
            self.project_filter_external_code.textChanged.connect(self.apply_project_filters)
            project_filters_layout.addWidget(self.project_filter_external_code)

            self.project_filter_label = QLineEdit()
            self.project_filter_label.setPlaceholderText("Label")
            self.project_filter_label.textChanged.connect(self.apply_project_filters)
            project_filters_layout.addWidget(self.project_filter_label)

            self.project_filter_title = QLineEdit()
            self.project_filter_title.setPlaceholderText("Title")
            self.project_filter_title.textChanged.connect(self.apply_project_filters)
            project_filters_layout.addWidget(self.project_filter_title)

            self.project_filter_method = QLineEdit()
            self.project_filter_method.setPlaceholderText("Method")
            self.project_filter_method.textChanged.connect(self.apply_project_filters)
            project_filters_layout.addWidget(self.project_filter_method)

            clear_project_filters_btn = QPushButton("Clear")
            clear_project_filters_btn.clicked.connect(self.clear_project_filters)
            project_filters_layout.addWidget(clear_project_filters_btn)

            layout.addLayout(project_filters_layout)

            self.project_structures_table = QTableWidget()
            self.project_structures_table.setColumnCount(5)
            self.project_structures_table.setHorizontalHeaderLabels([
                "External Code", "Label", "Title", "Method", "Files"
            ])
            self.project_structures_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.project_structures_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.project_structures_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            header = self.project_structures_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setSectionResizeMode(4, QHeaderView.Fixed)  # Files column fixed width
            self.project_structures_table.setColumnWidth(4, 80)
            self.project_structures_table.setAlternatingRowColors(True)
            self.project_structures_table.setSortingEnabled(True)

            layout.addWidget(self.project_structures_table)

            # Structure selection buttons
            structure_buttons = QHBoxLayout()
            select_all_btn = QPushButton("Select All")
            select_all_btn.clicked.connect(self.select_all_project_structures)
            structure_buttons.addWidget(select_all_btn)

            select_none_btn = QPushButton("Select None")
            select_none_btn.clicked.connect(self.select_none_project_structures)
            structure_buttons.addWidget(select_none_btn)

            structure_buttons.addStretch()

            self.load_project_structures_button = QPushButton("Load Selected Structures")
            self.load_project_structures_button.clicked.connect(self.load_selected_project_structures)
            self.load_project_structures_button.setEnabled(False)
            structure_buttons.addWidget(self.load_project_structures_button)

            layout.addLayout(structure_buttons)

            widget.setLayout(layout)
            return widget

        def _create_files_tab(self):
            """Create the associated files tab"""
            widget = QWidget()
            layout = QVBoxLayout()

            # Header with current structure info
            self.files_header_label = QLabel("Associated Files - Select a structure from the Projects tab to view its files")
            self.files_header_label.setStyleSheet("font-weight: bold; padding: 5px; color: #ECECEC;")
            layout.addWidget(self.files_header_label)

            # Checkbox to apply transformation matrix
            transform_layout = QHBoxLayout()
            self.apply_transform_checkbox = QCheckBox("Apply transformation matrix to associated files (if available)")
            self.apply_transform_checkbox.setToolTip("When enabled, associated files will be transformed using the structure's reference transformation matrix")
            self.apply_transform_checkbox.setChecked(True)
            transform_layout.addWidget(self.apply_transform_checkbox)
            transform_layout.addStretch()
            layout.addLayout(transform_layout)

            # Files table
            self.files_table = QTableWidget()
            self.files_table.setColumnCount(5)
            self.files_table.setHorizontalHeaderLabels(["File Name", "Type", "Size", "Format", "Description"])
            self.files_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.files_table.setAlternatingRowColors(True)
            self.files_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.files_table.setSortingEnabled(True)

            header = self.files_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.Interactive)
            self.files_table.setColumnWidth(0, 200)
            self.files_table.setColumnWidth(1, 100)
            self.files_table.setColumnWidth(2, 80)
            self.files_table.setColumnWidth(3, 100)

            self.files_table.itemSelectionChanged.connect(self._on_file_selection_changed)
            layout.addWidget(self.files_table)

            # Buttons for file operations
            files_buttons = QHBoxLayout()

            self.refresh_files_button = QPushButton("Refresh Files")
            self.refresh_files_button.clicked.connect(self.refresh_associated_files)
            self.refresh_files_button.setEnabled(False)
            files_buttons.addWidget(self.refresh_files_button)

            files_buttons.addStretch()

            self.open_file_button = QPushButton("Open in Maestro")
            self.open_file_button.clicked.connect(self.open_selected_file)
            self.open_file_button.setEnabled(False)
            files_buttons.addWidget(self.open_file_button)

            self.open_system_button = QPushButton("Download && Open")
            self.open_system_button.setToolTip("Download the file and open it with the system's default application")
            self.open_system_button.clicked.connect(self.download_and_open_with_system)
            self.open_system_button.setEnabled(False)
            files_buttons.addWidget(self.open_system_button)

            layout.addLayout(files_buttons)

            # Status label for file operations
            self.files_status_label = QLabel("")
            self.files_status_label.setStyleSheet("color: #ABABAB; padding: 5px;")
            layout.addWidget(self.files_status_label)

            widget.setLayout(layout)
            return widget

        def check_login_status(self):
            """Check if user is logged in and update UI accordingly"""
            if self.api_client.is_configured() and self.api_client.test_connection():
                self.status_label.setText("Logged in successfully")
                self.status_label.setStyleSheet("color: #7FBA7A;")
                self.submit_button.setEnabled(True)

                if hasattr(self, 'projects_table') and not self.projects_loaded:
                    try:
                        self.load_projects_for_tab()
                        self.projects_loaded = True
                    except Exception as e:
                        log_error(f"Failed to auto-load projects: {e}")
            else:
                self.status_label.setText("Not logged in - click Settings to configure")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                self.submit_button.setEnabled(False)

        def open_settings(self):
            """Open the settings dialog"""
            dialog = SettingsDialog(self.api_client, self)
            if dialog.exec() == QDialog.Accepted:
                self.check_login_status()

        def submit_search(self):
            """Submit search query"""
            query = self.search_input.text().strip()
            if not query:
                QMessageBox.warning(self, "Warning", "Please enter a search term")
                return

            if not self.api_client.is_configured():
                QMessageBox.warning(self, "Warning", "Please configure API settings first")
                return

            self.search_thread = SearchThread(self.api_client, query)
            self.search_thread.results_ready.connect(self.display_results)
            self.search_thread.error_occurred.connect(self.handle_search_error)
            self.search_thread.status_update.connect(self.update_status)

            self.submit_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)

            self.search_thread.start()

        def update_status(self, message: str):
            """Update status message"""
            self.status_label.setText(message)

        def display_results(self, structures: List[Dict[str, Any]]):
            """Display search results in the table"""
            self.progress_bar.setVisible(False)
            self.submit_button.setEnabled(True)
            self.check_login_status()

            self.all_results = structures
            self.populate_results_table(structures)

            if len(structures) == 0:
                QMessageBox.information(self, "Search Results", "No structures found for your search query.")
            else:
                QMessageBox.information(self, "Search Results", f"Found {len(structures)} structures.")

        def populate_results_table(self, structures: List[Dict[str, Any]]):
            """Populate the results table with given structures"""
            self.results_table.setSortingEnabled(False)
            self.results_table.setRowCount(len(structures))

            for row, structure in enumerate(structures):
                general = structure.get('general', {})

                external_code = general.get('external_code', 'N/A')
                item = QTableWidgetItem(external_code)
                item.setData(Qt.UserRole, general.get('structure_id'))
                self.results_table.setItem(row, 0, item)

                label = general.get('label', 'N/A')
                self.results_table.setItem(row, 1, QTableWidgetItem(label))

                title = general.get('title', 'N/A')
                self.results_table.setItem(row, 2, QTableWidgetItem(title))

                method = general.get('method', 'N/A')
                self.results_table.setItem(row, 3, QTableWidgetItem(method))

                resolution = general.get('resolution')
                resolution_text = f"{resolution:.2f} A" if resolution else "N/A"
                numeric_value = resolution if resolution is not None else float('inf')
                resolution_item = NumericTableWidgetItem(resolution_text, numeric_value)
                self.results_table.setItem(row, 4, resolution_item)

                source = general.get('source', 'N/A')
                self.results_table.setItem(row, 5, QTableWidgetItem(source))

            self.results_table.setSortingEnabled(True)
            self.load_button.setEnabled(len(structures) > 0)

        def handle_search_error(self, error_message: str):
            """Handle search errors"""
            self.progress_bar.setVisible(False)
            self.submit_button.setEnabled(True)
            self.check_login_status()
            QMessageBox.critical(self, "Search Error", error_message)

        def load_selected_structures(self):
            """Load selected structures into Maestro"""
            selected_structures = []

            selected_rows = self.results_table.selectionModel().selectedRows()
            log_debug(f"Found {len(selected_rows)} selected rows in search results")

            for index in selected_rows:
                row = index.row()
                item = self.results_table.item(row, 0)
                if item:
                    structure_id = item.data(Qt.UserRole)
                    external_code = item.text()

                    label_item = self.results_table.item(row, 1)
                    title_item = self.results_table.item(row, 2)
                    source_item = self.results_table.item(row, 5)
                    label = label_item.text() if label_item else None
                    title = title_item.text() if title_item else None
                    source = source_item.text() if source_item else None

                    if structure_id:
                        selected_structures.append({
                            'structure_id': str(structure_id),
                            'external_code': external_code,
                            'label': label,
                            'title': title,
                            'source': source
                        })

            if not selected_structures:
                QMessageBox.warning(self, "Warning", "Please select at least one structure to load")
                return

            self.load_thread = LoadStructureThread(self.api_client, selected_structures)
            self.load_thread.pdb_content_ready.connect(self.load_pdb_into_maestro)
            self.load_thread.structure_loaded.connect(self.handle_structure_loaded)
            self.load_thread.error_occurred.connect(self.handle_load_error)
            self.load_thread.status_update.connect(self.update_status)
            self.load_thread.all_structures_loaded.connect(self.handle_all_structures_loaded)

            self.load_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)

            self.load_thread.start()

        def load_pdb_into_maestro(self, pdb_content: str, object_name: str, metadata: dict):
            """Load PDB content into Maestro"""
            try:
                # Save PDB to temporary file
                temp_dir = tempfile.gettempdir()
                pdb_filename = f"{object_name}.pdb"
                pdb_path = os.path.join(temp_dir, pdb_filename)

                with open(pdb_path, 'w') as f:
                    f.write(pdb_content)

                log_debug(f"Saved PDB to: {pdb_path}")

                # Read structure using Schrodinger's structure module
                st = structure.StructureReader.read(pdb_path)

                # Add metadata as properties
                for key, value in metadata.items():
                    st.property[f's_user_{key}'] = str(value)

                # Set the structure title
                st.title = object_name

                # Import into Maestro project
                if MAESTRO_AVAILABLE:
                    pt = maestro.project_table_get()
                    pt.importStructure(st)
                    log_info(f"Imported structure {object_name} into Maestro project")
                else:
                    log_debug(f"Would import structure {object_name} into Maestro (not in Maestro environment)")

                # Clean up temp file
                try:
                    os.remove(pdb_path)
                except:
                    pass

            except Exception as e:
                log_error(f"Error loading PDB into Maestro: {e}")

        def handle_structure_loaded(self, structure_id: str, object_name: str):
            """Handle successful structure loading"""
            log_info(f"Loaded structure {structure_id} as {object_name}")

        def handle_all_structures_loaded(self):
            """Handle completion of all structure loading"""
            self.progress_bar.setVisible(False)
            self.load_button.setEnabled(True)
            if hasattr(self, 'load_project_structures_button'):
                self.load_project_structures_button.setEnabled(True)
            self.check_login_status()

        def handle_load_error(self, error_message: str):
            """Handle structure loading errors"""
            self.progress_bar.setVisible(False)
            self.load_button.setEnabled(True)
            if hasattr(self, 'load_project_structures_button'):
                self.load_project_structures_button.setEnabled(True)
            QMessageBox.critical(self, "Load Error", error_message)

        # Filter methods for search results
        def clear_filters(self):
            """Clear all filter inputs without triggering filtering"""
            self.filter_external_code.blockSignals(True)
            self.filter_label.blockSignals(True)
            self.filter_title.blockSignals(True)
            self.filter_method.blockSignals(True)
            self.filter_resolution.blockSignals(True)
            self.filter_source.blockSignals(True)

            self.filter_external_code.clear()
            self.filter_label.clear()
            self.filter_title.clear()
            self.filter_method.clear()
            self.filter_resolution.clear()
            self.filter_source.clear()

            self.filter_external_code.blockSignals(False)
            self.filter_label.blockSignals(False)
            self.filter_title.blockSignals(False)
            self.filter_method.blockSignals(False)
            self.filter_resolution.blockSignals(False)
            self.filter_source.blockSignals(False)

            # Show all results
            if hasattr(self, 'all_results') and self.all_results:
                self.populate_results_table(self.all_results)
                self.status_label.setText(f"Showing all {len(self.all_results)} results")

        def apply_filters(self):
            """Apply column filters to the results table"""
            if not hasattr(self, 'all_results') or not self.all_results:
                return

            filter_ext_code = self.filter_external_code.text().strip().lower()
            filter_lbl = self.filter_label.text().strip().lower()
            filter_ttl = self.filter_title.text().strip().lower()
            filter_mth = self.filter_method.text().strip().lower()
            filter_res = self.filter_resolution.text().strip()
            filter_src = self.filter_source.text().strip().lower()

            res_min, res_max, res_operator = self.parse_resolution_filter(filter_res)

            filtered_structures = []
            for struct in self.all_results:
                general = struct.get('general', {})

                if filter_ext_code and filter_ext_code not in general.get('external_code', '').lower():
                    continue
                if filter_lbl and filter_lbl not in general.get('label', '').lower():
                    continue
                if filter_ttl and filter_ttl not in general.get('title', '').lower():
                    continue
                if filter_mth and filter_mth not in general.get('method', '').lower():
                    continue
                if filter_src and filter_src not in general.get('source', '').lower():
                    continue

                if filter_res:
                    resolution = general.get('resolution')
                    if not self.check_resolution_filter(resolution, res_min, res_max, res_operator):
                        continue

                filtered_structures.append(struct)

            self.populate_results_table(filtered_structures)

            if len(filtered_structures) < len(self.all_results):
                self.status_label.setText(f"Showing {len(filtered_structures)} of {len(self.all_results)} results")
            else:
                self.status_label.setText(f"Showing all {len(self.all_results)} results")

        def parse_resolution_filter(self, filter_text: str):
            """
            Parse resolution filter string.
            Supports formats: <2.0, >1.5, <=2.0, >=1.5, 1.5-3.0, 2.0
            Returns: (min_value, max_value, operator)
            """
            if not filter_text:
                return None, None, None

            filter_text = filter_text.strip()

            # Range format: 1.5-3.0
            if '-' in filter_text and not filter_text.startswith('-'):
                parts = filter_text.split('-')
                if len(parts) == 2:
                    try:
                        min_val = float(parts[0].strip())
                        max_val = float(parts[1].strip())
                        return min_val, max_val, 'range'
                    except ValueError:
                        return None, None, None

            # Operator formats: <, >, <=, >=
            if filter_text.startswith('<='):
                try:
                    val = float(filter_text[2:].strip())
                    return None, val, '<='
                except ValueError:
                    return None, None, None
            elif filter_text.startswith('>='):
                try:
                    val = float(filter_text[2:].strip())
                    return val, None, '>='
                except ValueError:
                    return None, None, None
            elif filter_text.startswith('<'):
                try:
                    val = float(filter_text[1:].strip())
                    return None, val, '<'
                except ValueError:
                    return None, None, None
            elif filter_text.startswith('>'):
                try:
                    val = float(filter_text[1:].strip())
                    return val, None, '>'
                except ValueError:
                    return None, None, None

            # Exact value
            try:
                val = float(filter_text)
                return val, val, '='
            except ValueError:
                return None, None, None

        def check_resolution_filter(self, resolution, min_val, max_val, operator):
            """Check if resolution value passes the filter"""
            if resolution is None:
                return False

            if operator == 'range':
                return min_val <= resolution <= max_val
            elif operator == '<':
                return resolution < max_val
            elif operator == '<=':
                return resolution <= max_val
            elif operator == '>':
                return resolution > min_val
            elif operator == '>=':
                return resolution >= min_val
            elif operator == '=':
                return abs(resolution - min_val) < 0.01

            return True

        # Projects tab methods
        def load_projects_for_tab(self):
            """Load projects when Projects tab is accessed"""
            try:
                if not self.api_client.is_authenticated():
                    log_debug("Not authenticated, attempting to authenticate")
                    if self.api_client.test_connection():
                        log_debug("Successfully authenticated")
                        self.check_login_status()
                    else:
                        reply = QMessageBox.question(
                            self,
                            "Authentication Required",
                            "You need to be logged in to view projects.\n\n"
                            "Would you like to open settings to configure your API token?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.Yes
                        )

                        if reply == QMessageBox.Yes:
                            self.open_settings()
                        return

                projects = self.api_client.get_projects()

                # Filter out the "3decision" project
                filtered_projects = []
                for project in projects:
                    project_label = project.get('project_label', '').lower()
                    project_name = project.get('project_name', '').lower()

                    if project_label != '3decision' and project_name != '3decision':
                        filtered_projects.append(project)

                self.projects_data = filtered_projects
                self.populate_projects_table()

            except Exception as e:
                log_error(f"Failed to load projects: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load projects: {str(e)}")

        def populate_projects_table(self):
            """Populate the projects table with data"""
            self.projects_table.setSortingEnabled(False)
            self.projects_table.setRowCount(len(self.projects_data))

            for row, project in enumerate(self.projects_data):
                name_item = QTableWidgetItem(project.get('project_label', ''))
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                name_item.setData(Qt.UserRole, project)
                self.projects_table.setItem(row, 0, name_item)

                owner = ''
                for field in ['owner', 'project_owner', 'created_by', 'owner_username', 'creator', 'author', 'username']:
                    if project.get(field):
                        owner = project.get(field)
                        break

                owner_item = QTableWidgetItem(str(owner))
                owner_item.setFlags(owner_item.flags() & ~Qt.ItemIsEditable)
                self.projects_table.setItem(row, 1, owner_item)

                count = project.get('count_structures_in_project', 0)
                count_item = NumericTableWidgetItem(str(count), count)
                count_item.setFlags(count_item.flags() & ~Qt.ItemIsEditable)
                self.projects_table.setItem(row, 2, count_item)

                id_item = QTableWidgetItem(str(project.get('project_id', '')))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.projects_table.setItem(row, 3, id_item)

            self.projects_table.setSortingEnabled(True)

        def clear_projects_filters(self):
            """Clear all projects filter inputs without triggering filtering"""
            self.projects_filter_name.blockSignals(True)
            self.projects_filter_owner.blockSignals(True)
            self.projects_filter_structures.blockSignals(True)
            self.projects_filter_id.blockSignals(True)

            self.projects_filter_name.clear()
            self.projects_filter_owner.clear()
            self.projects_filter_structures.clear()
            self.projects_filter_id.clear()

            self.projects_filter_name.blockSignals(False)
            self.projects_filter_owner.blockSignals(False)
            self.projects_filter_structures.blockSignals(False)
            self.projects_filter_id.blockSignals(False)

            self.apply_projects_filters()

        def apply_projects_filters(self):
            """Apply column filters to the projects table"""
            if not hasattr(self, 'projects_data') or not self.projects_data:
                return

            filter_name = self.projects_filter_name.text().strip().lower()
            filter_owner = self.projects_filter_owner.text().strip().lower()
            filter_structures = self.projects_filter_structures.text().strip()
            filter_id = self.projects_filter_id.text().strip().lower()

            struct_min, struct_max, struct_operator = self.parse_resolution_filter(filter_structures)

            filtered_projects = []
            for project in self.projects_data:
                project_name = str(project.get('project_label', '')).lower()

                owner = ''
                for field in ['owner', 'project_owner', 'created_by', 'owner_username', 'creator', 'author', 'username']:
                    if project.get(field):
                        owner = str(project.get(field)).lower()
                        break

                structures_count = project.get('count_structures_in_project', 0)
                project_id = str(project.get('project_id', '')).lower()

                if filter_name and filter_name not in project_name:
                    continue
                if filter_owner and filter_owner not in owner:
                    continue
                if filter_id and filter_id not in project_id:
                    continue

                if filter_structures:
                    if not self.check_resolution_filter(structures_count, struct_min, struct_max, struct_operator):
                        continue

                filtered_projects.append(project)

            self.projects_table.setSortingEnabled(False)
            self.projects_table.setRowCount(len(filtered_projects))

            for row, project in enumerate(filtered_projects):
                name_item = QTableWidgetItem(project.get('project_label', ''))
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                name_item.setData(Qt.UserRole, project)
                self.projects_table.setItem(row, 0, name_item)

                owner = ''
                for field in ['owner', 'project_owner', 'created_by', 'owner_username', 'creator', 'author', 'username']:
                    if project.get(field):
                        owner = project.get(field)
                        break

                owner_item = QTableWidgetItem(str(owner))
                owner_item.setFlags(owner_item.flags() & ~Qt.ItemIsEditable)
                self.projects_table.setItem(row, 1, owner_item)

                count = project.get('count_structures_in_project', 0)
                count_item = NumericTableWidgetItem(str(count), count)
                count_item.setFlags(count_item.flags() & ~Qt.ItemIsEditable)
                self.projects_table.setItem(row, 2, count_item)

                id_item = QTableWidgetItem(str(project.get('project_id', '')))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.projects_table.setItem(row, 3, id_item)

            self.projects_table.setSortingEnabled(True)

        def on_project_selection_changed(self):
            """Handle project table selection change"""
            selected_rows = self.projects_table.selectionModel().selectedRows()
            if selected_rows:
                self.load_project_structures_button.setEnabled(False)
                row = selected_rows[0].row()
                project_data = self.projects_table.item(row, 0).data(Qt.UserRole)
                project_id = project_data.get('project_id')
                self.load_project_structures_in_tab(project_id)

        def load_project_structures_in_tab(self, project_id):
            """Load structures for the selected project"""
            try:
                structures = self.api_client.get_project_structures(project_id)

                log_debug(f"Received {len(structures)} structures from get_project_structures")

                if not structures:
                    self.current_project_structures = []
                    self.populate_project_structures_table([])
                    return

                structure_ids = []
                for s in structures:
                    structure_id = s.get('STRUCTURE_ID') or s.get('structure_id')
                    if structure_id:
                        structure_ids.append(int(structure_id))

                log_debug(f"Fetching details for {len(structure_ids)} structures...")

                detailed_structures = self.api_client.get_structures_info(structure_ids)

                details_map = {}
                for detail in detailed_structures:
                    sid = detail.get('structure_id') or detail.get('general', {}).get('structure_id')
                    if sid:
                        details_map[int(sid)] = detail

                enriched_structures = []
                for s in structures:
                    structure_id = s.get('STRUCTURE_ID') or s.get('structure_id')
                    if structure_id and int(structure_id) in details_map:
                        enriched = details_map[int(structure_id)].copy()
                        matrix = None
                        ref_transforms = s.get('ReferenceTransforms')
                        if ref_transforms and isinstance(ref_transforms, dict):
                            transform = ref_transforms.get('transform')
                            if transform and isinstance(transform, list) and len(transform) == 16:
                                matrix = [
                                    transform[0:4],
                                    transform[4:8],
                                    transform[8:12],
                                    transform[12:16]
                                ]
                        enriched['TRANSFORM_MATRIX'] = matrix
                        enriched_structures.append(enriched)
                    else:
                        enriched_structures.append(s)

                self.current_project_structures = enriched_structures
                self.populate_project_structures_table(enriched_structures)

            except Exception as e:
                log_error(f"Failed to load project structures: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load project structures: {str(e)}")

        def populate_project_structures_table(self, structures):
            """Populate the project structures table"""
            self.project_structures_table.setSortingEnabled(False)
            self.project_structures_table.setRowCount(len(structures))

            for row, structure in enumerate(structures):
                external_code = (structure.get('EXTERNAL_CODE') or
                               structure.get('external_code') or
                               structure.get('general', {}).get('external_code', 'N/A'))

                item = QTableWidgetItem(external_code)

                structure_id = (structure.get('STRUCTURE_ID') or
                              structure.get('structure_id') or
                              structure.get('general', {}).get('structure_id'))

                transform_matrix = (structure.get('TRANSFORM_MATRIX') or
                                  structure.get('matrix') or
                                  structure.get('MATRIX'))

                source = (structure.get('SOURCE') or
                         structure.get('source') or
                         structure.get('general', {}).get('source'))

                item.setData(Qt.UserRole, {
                    'structure_id': structure_id,
                    'matrix': transform_matrix,
                    'source': source
                })
                self.project_structures_table.setItem(row, 0, item)

                label = (structure.get('LABEL') or
                        structure.get('label') or
                        structure.get('PROJECT_LABEL') or
                        structure.get('project_label') or
                        structure.get('general', {}).get('label', external_code))
                self.project_structures_table.setItem(row, 1, QTableWidgetItem(label))

                title = (structure.get('TITLE') or
                        structure.get('title') or
                        structure.get('general', {}).get('title', external_code))
                self.project_structures_table.setItem(row, 2, QTableWidgetItem(title))

                method = (structure.get('METHOD') or
                         structure.get('method') or
                         structure.get('general', {}).get('method', 'N/A'))
                self.project_structures_table.setItem(row, 3, QTableWidgetItem(method))

                # Files button
                files_button = QPushButton("View")
                files_button.setProperty('structure_data', structure)
                files_button.clicked.connect(lambda checked, s=structure: self.view_structure_files(s))
                self.project_structures_table.setCellWidget(row, 4, files_button)

            self.project_structures_table.setSortingEnabled(True)
            self.load_project_structures_button.setEnabled(len(structures) > 0)

        def clear_project_filters(self):
            """Clear all project structure filter inputs without triggering filtering"""
            self.project_filter_external_code.blockSignals(True)
            self.project_filter_label.blockSignals(True)
            self.project_filter_title.blockSignals(True)
            self.project_filter_method.blockSignals(True)

            self.project_filter_external_code.clear()
            self.project_filter_label.clear()
            self.project_filter_title.clear()
            self.project_filter_method.clear()

            self.project_filter_external_code.blockSignals(False)
            self.project_filter_label.blockSignals(False)
            self.project_filter_title.blockSignals(False)
            self.project_filter_method.blockSignals(False)

            self.apply_project_filters()

        def apply_project_filters(self):
            """Apply column filters to the project structures table"""
            if not hasattr(self, 'current_project_structures') or not self.current_project_structures:
                return

            filter_ext_code = self.project_filter_external_code.text().strip().lower()
            filter_lbl = self.project_filter_label.text().strip().lower()
            filter_ttl = self.project_filter_title.text().strip().lower()
            filter_mth = self.project_filter_method.text().strip().lower()

            filtered_structures = []
            for struct in self.current_project_structures:
                external_code = (struct.get('EXTERNAL_CODE') or
                               struct.get('external_code') or
                               struct.get('general', {}).get('external_code', 'N/A'))

                label = (struct.get('LABEL') or
                        struct.get('label') or
                        struct.get('PROJECT_LABEL') or
                        struct.get('project_label') or
                        struct.get('general', {}).get('label', external_code))

                title = (struct.get('TITLE') or
                        struct.get('title') or
                        struct.get('general', {}).get('title', external_code))

                method = (struct.get('METHOD') or
                         struct.get('method') or
                         struct.get('general', {}).get('method', 'N/A'))

                external_code_lower = str(external_code).lower() if external_code else ''
                label_lower = str(label).lower() if label else ''
                title_lower = str(title).lower() if title else ''
                method_lower = str(method).lower() if method else ''

                if filter_ext_code and filter_ext_code not in external_code_lower:
                    continue
                if filter_lbl and filter_lbl not in label_lower:
                    continue
                if filter_ttl and filter_ttl not in title_lower:
                    continue
                if filter_mth and filter_mth not in method_lower:
                    continue

                filtered_structures.append(struct)

            self.populate_project_structures_table(filtered_structures)

        def select_all_project_structures(self):
            """Select all structures in the project structures table"""
            self.project_structures_table.selectAll()

        def select_none_project_structures(self):
            """Deselect all structures in the project structures table"""
            self.project_structures_table.clearSelection()

        def load_selected_project_structures(self):
            """Load selected structures from the project"""
            selected_structures = []

            selected_rows = self.project_structures_table.selectionModel().selectedRows()
            log_debug(f"Found {len(selected_rows)} selected rows")

            for index in selected_rows:
                row = index.row()
                item = self.project_structures_table.item(row, 0)
                if item:
                    data = item.data(Qt.UserRole)
                    external_code = item.text()

                    label_item = self.project_structures_table.item(row, 1)
                    label = label_item.text() if label_item else None

                    title_item = self.project_structures_table.item(row, 2)
                    title = title_item.text() if title_item else None

                    if isinstance(data, dict):
                        structure_id = data.get('structure_id')
                        matrix = data.get('matrix')
                        source = data.get('source')
                    else:
                        structure_id = data
                        matrix = None
                        source = None

                    if structure_id:
                        selected_structures.append({
                            'structure_id': str(structure_id),
                            'external_code': external_code,
                            'label': label,
                            'title': title,
                            'source': source,
                            'matrix': matrix
                        })

            if not selected_structures:
                QMessageBox.warning(self, "Warning", "Please select at least one structure to load")
                return

            self.load_thread = LoadStructureThread(self.api_client, selected_structures)
            self.load_thread.pdb_content_ready.connect(self.load_pdb_into_maestro)
            self.load_thread.structure_loaded.connect(self.handle_structure_loaded)
            self.load_thread.error_occurred.connect(self.handle_load_error)
            self.load_thread.status_update.connect(self.update_status)
            self.load_thread.all_structures_loaded.connect(self.handle_all_structures_loaded)

            self.load_project_structures_button.setEnabled(False)
            self.status_label.setText("Loading structures...")

            self.load_thread.start()

        # =============================================
        # Associated Files functionality
        # =============================================

        def view_structure_files(self, structure):
            """View associated files for a structure"""
            if not structure:
                return

            structure_id = str(structure.get('STRUCTURE_ID') or structure.get('structure_id') or
                             structure.get('general', {}).get('structure_id', ''))
            external_code = (structure.get('EXTERNAL_CODE') or structure.get('external_code') or
                            structure.get('general', {}).get('external_code', structure_id))

            # Store current structure for file operations
            self.current_structure = structure
            self.current_structure_id = structure_id
            self.current_external_code = external_code

            # Extract and store transformation matrix if available
            self.current_transform_matrix = None
            matrix = structure.get('TRANSFORM_MATRIX')
            if not matrix:
                ref_transforms = structure.get('ReferenceTransforms')
                if ref_transforms and isinstance(ref_transforms, dict):
                    transform = ref_transforms.get('transform')
                    if transform and isinstance(transform, list) and len(transform) == 16:
                        matrix = [
                            transform[0:4],
                            transform[4:8],
                            transform[8:12],
                            transform[12:16]
                        ]
            self.current_transform_matrix = matrix

            # Update header and switch to files tab
            matrix_status = " (with transformation matrix)" if matrix else ""
            self.files_header_label.setText(f"Associated Files for {external_code} (ID: {structure_id}){matrix_status}")
            self.tab_widget.setCurrentIndex(2)  # Switch to Associated Files tab

            # Enable refresh button
            self.refresh_files_button.setEnabled(True)

            # Load files using external_code
            self.load_associated_files(external_code)

        def load_associated_files(self, external_code):
            """Load associated files for a structure using external code"""
            try:
                self.files_status_label.setText("Loading associated files...")

                files = self.api_client.get_associated_files(external_code)

                if files:
                    self.populate_files_table(files)
                    self.files_status_label.setText(f"Loaded {len(files)} associated files")
                else:
                    self.files_table.setRowCount(0)
                    self.files_status_label.setText("No associated files found")

            except Exception as e:
                log_error(f"Failed to load associated files: {e}")
                self.files_status_label.setText(f"Error loading files: {str(e)}")
                self.files_table.setRowCount(0)

        def populate_files_table(self, files):
            """Populate the files table with file data"""
            self.files_table.setRowCount(len(files))

            for row, file_info in enumerate(files):
                filename = file_info.get('file_name', 'Unknown')
                file_type = file_info.get('file_type_label', 'Unknown')
                file_size = "N/A"
                file_extension = file_info.get('file_type_extension', '')
                file_format = self._get_file_format_from_extension(file_extension, filename)
                description = file_info.get('file_desc', '') or ''

                name_item = QTableWidgetItem(filename)
                name_item.setData(Qt.UserRole, file_info)
                self.files_table.setItem(row, 0, name_item)
                self.files_table.setItem(row, 1, QTableWidgetItem(str(file_type)))
                self.files_table.setItem(row, 2, QTableWidgetItem(str(file_size)))
                self.files_table.setItem(row, 3, QTableWidgetItem(file_format))
                self.files_table.setItem(row, 4, QTableWidgetItem(description))

        def _get_file_format_from_extension(self, extension, filename=""):
            """Determine file format from extension and filename"""
            if not extension:
                if filename and '.' in filename:
                    extension = filename.lower().split('.')[-1]
                else:
                    return "Unknown"

            extension = extension.lower()

            # Maestro-supported formats and other common formats
            format_map = {
                'pdb': 'PDB Structure',
                'cif': 'mmCIF Structure',
                'mmcif': 'mmCIF Structure',
                'mae': 'Maestro File',
                'maegz': 'Maestro File (compressed)',
                'sdf': 'SDF Molecule',
                'mol2': 'MOL2 Molecule',
                'mol': 'MOL Molecule',
                'xyz': 'XYZ Coordinates',
                'mtz': 'MTZ Reflection',
                'mrc': 'MRC Map',
                'map': 'CCP4 Map',
                'ccp4': 'CCP4 Map',
                'dsn6': 'DSN6 Map',
                'xplor': 'XPLOR Map',
                'dx': 'DX Map',
                'smi': 'SMILES File',
                'csv': 'CSV File',
                'txt': 'Text File',
                'pdf': 'PDF File',
                'png': 'PNG Image',
                'jpg': 'JPG Image',
                'jpeg': 'JPEG Image',
                'tif': 'TIF Image',
                'tiff': 'TIFF Image',
                'doc': 'DOC File',
                'docx': 'DOCX File',
                'xls': 'XLS File',
                'xlsx': 'XLSX File',
            }

            return format_map.get(extension, f"{extension.upper()} File" if extension else "Unknown")

        def _on_file_selection_changed(self):
            """Handle file selection change"""
            selected_items = self.files_table.selectedItems()
            has_selection = len(selected_items) > 0

            self.open_file_button.setEnabled(has_selection)
            self.open_system_button.setEnabled(has_selection)

        def refresh_associated_files(self):
            """Refresh the associated files list"""
            if hasattr(self, 'current_external_code') and self.current_external_code:
                self.load_associated_files(self.current_external_code)

        def open_selected_file(self):
            """Open the selected file in Maestro"""
            selected_row = self.files_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Warning", "Please select a file to open")
                return

            file_item = self.files_table.item(selected_row, 0)
            if not file_item:
                return

            file_info = file_item.data(Qt.UserRole)
            filename = file_item.text()
            file_format = self.files_table.item(selected_row, 3).text()

            # Maestro-supported structure formats
            structure_formats = ['PDB Structure', 'mmCIF Structure', 'Maestro File', 'Maestro File (compressed)',
                               'SDF Molecule', 'MOL2 Molecule', 'MOL Molecule', 'XYZ Coordinates']
            # Map/density formats that can be directly imported via visimport
            supported_map_formats = ['CCP4 Map', 'MRC Map']
            # Map formats that are NOT supported for direct import
            unsupported_map_formats = {
                'DSN6 Map': 'DSN6 format is not supported by Maestro.',
                'MTZ Reflection': 'MTZ files contain reflection data, not real-space maps.\nThey must be converted to CCP4 format first using tools like sf2map.',
                'XPLOR Map': 'XPLOR map format is not supported for direct import.',
                'DX Map': 'DX map format is not supported for direct import.'
            }

            supported_formats = structure_formats + supported_map_formats

            # Check for unsupported map formats first
            if file_format in unsupported_map_formats:
                QMessageBox.warning(self, "Unsupported Map Format",
                                  f"{unsupported_map_formats[file_format]}\n\n"
                                  f"Use the 'Download & Open' button to save the file locally.")
                return

            if file_format not in supported_formats:
                QMessageBox.information(self, "Use System Application",
                                      f"'{file_format}' files cannot be opened directly in Maestro.\n\n"
                                      f"Use the 'Download & Open' button to open this file "
                                      f"with your system's default application.")
                return

            try:
                self.files_status_label.setText(f"Opening {filename} in Maestro...")

                file_data = self.api_client.download_file(file_info)

                if file_data:
                    temp_dir = tempfile.gettempdir()
                    file_path = os.path.join(temp_dir, filename)

                    with open(file_path, 'wb') as f:
                        f.write(file_data)

                    log_debug(f"Saved file to: {file_path}")

                    if MAESTRO_AVAILABLE:
                        if file_format in structure_formats:
                            # Load structure into Maestro
                            st = structure.StructureReader.read(file_path)
                            obj_name = os.path.splitext(filename)[0]
                            st.title = obj_name

                            # Apply transformation matrix if enabled
                            if self.apply_transform_checkbox.isChecked() and self.current_transform_matrix:
                                try:
                                    self._apply_transform_to_structure(st, self.current_transform_matrix)
                                    self.files_status_label.setText(f"Opened {filename} with transformation applied")
                                except Exception as matrix_error:
                                    log_error(f"Could not apply transformation matrix: {matrix_error}")
                                    self.files_status_label.setText(f"Opened {filename} (could not apply transformation)")
                            else:
                                self.files_status_label.setText(f"Opened {filename} in Maestro")

                            pt = maestro.project_table_get()
                            pt.importStructure(st)
                            log_info(f"Imported file {filename} into Maestro project")
                        else:
                            # Map files - try to import onto currently selected workspace entry
                            pt = maestro.project_table_get()
                            included_rows = list(pt.included_rows)

                            if included_rows:
                                # Get the first included entry's ID
                                entry_row = included_rows[0]
                                entry_id = entry_row.entry_id

                                # Determine map type - CCP4 and MRC are both read as ccp4 format
                                # file_format here is the display name like 'CCP4 Map' or 'MRC Map'
                                map_type = 'ccp4'  # Both CCP4 and MRC use ccp4 map type

                                # Use visimport command to load the map onto the entry
                                surface_name = os.path.splitext(filename)[0]
                                cmd = f'visimport entry={entry_id} map_type={map_type} isovalue=1.0 "{file_path}":::{surface_name}'
                                log_debug(f"Importing map with command: {cmd}")

                                try:
                                    maestro.command(cmd)
                                    self.files_status_label.setText(f"Imported {filename} onto entry {entry_id}")
                                    log_info(f"Imported map file {filename} onto entry {entry_id}")
                                except Exception as cmd_error:
                                    log_error(f"visimport command failed: {cmd_error}")
                                    self.files_status_label.setText(f"Map file saved to temp folder")
                                    QMessageBox.warning(
                                        self, "Map Import",
                                        f"Could not automatically import map: {cmd_error}\n\n"
                                        f"Map file saved to:\n{file_path}\n\n"
                                        "Try using File > Import Structures/Volumes manually."
                                    )
                            else:
                                # No entry selected in workspace
                                self.files_status_label.setText(f"No entry selected - map saved to temp folder")
                                QMessageBox.information(
                                    self, "Map File",
                                    f"Map file '{filename}' has been downloaded to:\n{file_path}\n\n"
                                    "To automatically import map files:\n"
                                    "1. First include a structure in the Workspace\n"
                                    "2. Then click 'Open in Maestro' for the map\n\n"
                                    "Or use File > Import Structures/Volumes manually."
                                )
                    else:
                        self.files_status_label.setText("Maestro not available")
                        QMessageBox.warning(self, "Warning", "Maestro is not available. Cannot open file.")

                    # Clean up temp files for structure formats (map files may be needed if not auto-imported)
                    if file_format in structure_formats:
                        try:
                            os.remove(file_path)
                        except:
                            pass

                else:
                    self.files_status_label.setText("Failed to download file")
                    QMessageBox.warning(self, "Error", "Failed to download file for opening")

            except Exception as e:
                log_error(f"Error opening file: {e}")
                self.files_status_label.setText(f"Error opening file: {str(e)}")
                QMessageBox.critical(self, "Open Error", str(e))

        def _apply_transform_to_structure(self, st, matrix):
            """Apply a 4x4 transformation matrix to a Schrodinger structure"""
            import numpy as np

            # Convert matrix to flat list if needed
            if isinstance(matrix, list) and len(matrix) == 4 and isinstance(matrix[0], list):
                flat_matrix = []
                for row in matrix:
                    flat_matrix.extend(row)
                matrix = flat_matrix

            if len(matrix) != 16:
                raise ValueError(f"Invalid matrix length: {len(matrix)}, expected 16")

            # Convert to 4x4 numpy array
            transform = np.array(matrix).reshape(4, 4)

            # Apply transformation to all atoms
            for atom in st.atom:
                coords = np.array([atom.x, atom.y, atom.z, 1.0])
                new_coords = transform @ coords
                atom.x, atom.y, atom.z = new_coords[:3]

            log_debug(f"Applied transformation matrix to structure")

        def download_and_open_with_system(self):
            """Download the selected file and open it with the system's default application."""
            selected_row = self.files_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Warning", "Please select a file to download")
                return

            file_item = self.files_table.item(selected_row, 0)
            if not file_item:
                return

            file_info = file_item.data(Qt.UserRole)
            filename = file_item.text()

            try:
                self.files_status_label.setText(f"Downloading {filename}...")

                file_data = self.api_client.download_file(file_info)

                if file_data:
                    import subprocess

                    temp_dir = os.path.join(tempfile.gettempdir(), '3decision_downloads')
                    os.makedirs(temp_dir, exist_ok=True)
                    file_path = os.path.join(temp_dir, filename)

                    with open(file_path, 'wb') as f:
                        f.write(file_data)

                    self.files_status_label.setText(f"Opening {filename} with system application...")

                    self._open_file_with_system(file_path)

                    self.files_status_label.setText(f"Downloaded and opened {filename}")

                else:
                    self.files_status_label.setText("Failed to download file")
                    QMessageBox.warning(self, "Error", "Failed to download file")

            except Exception as e:
                log_error(f"Error downloading file: {e}")
                self.files_status_label.setText(f"Error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to download and open file: {str(e)}")

        def _open_file_with_system(self, file_path: str):
            """Open a file with the system's default application."""
            import subprocess

            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            elif sys.platform == 'win32':  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)

else:
    # Fallback for when Maestro is not available (testing outside Maestro)
    class ThreeDecisionPanel(QDialog):
        """Standalone dialog for testing outside Maestro"""

        _instance = None

        @classmethod
        def panel(cls, run=True):
            """Return or create a singleton instance"""
            if cls._instance is None:
                cls._instance = cls()
            if run:
                cls._instance.show()
            return cls._instance

        def __init__(self, parent=None):
            super().__init__(parent)
            self.api_client = ThreeDecisionAPIClient()
            self.search_thread = None
            self.load_thread = None
            self.all_results = []
            self.projects_data = []
            self.current_project_structures = []
            self.projects_loaded = False

            self.setWindowTitle("3decision Structure Search v1.0 (Standalone)")
            self.setMinimumSize(800, 600)
            self.init_ui()
            self.check_login_status()

        def init_ui(self):
            """Initialize the user interface"""
            main_layout = QVBoxLayout()

            # Settings button
            settings_layout = QHBoxLayout()
            settings_layout.addStretch()

            self.settings_button = QPushButton("Settings")
            self.settings_button.clicked.connect(self.open_settings)
            settings_layout.addWidget(self.settings_button)

            main_layout.addLayout(settings_layout)

            # Tab widget
            self.tab_widget = QTabWidget()

            # Search tab (simplified)
            search_widget = QWidget()
            search_layout = QVBoxLayout()

            search_row = QHBoxLayout()
            search_row.addWidget(QLabel("Search:"))
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Enter search term")
            search_row.addWidget(self.search_input)

            self.submit_button = QPushButton("Submit")
            self.submit_button.setEnabled(False)
            search_row.addWidget(self.submit_button)

            search_layout.addLayout(search_row)

            self.results_table = QTableWidget()
            self.results_table.setColumnCount(6)
            self.results_table.setHorizontalHeaderLabels([
                "External Code", "Label", "Title", "Method", "Resolution", "Source"
            ])
            search_layout.addWidget(self.results_table)

            self.load_button = QPushButton("Load Selected")
            self.load_button.setEnabled(False)
            search_layout.addWidget(self.load_button)

            search_widget.setLayout(search_layout)
            self.tab_widget.addTab(search_widget, "Search")

            main_layout.addWidget(self.tab_widget)

            # Status
            self.status_label = QLabel("Not logged in")
            self.status_label.setStyleSheet("color: #FF6B6B;")
            main_layout.addWidget(self.status_label)

            self.setLayout(main_layout)

        def check_login_status(self):
            if self.api_client.is_configured() and self.api_client.test_connection():
                self.status_label.setText("Logged in successfully")
                self.status_label.setStyleSheet("color: #7FBA7A;")
                self.submit_button.setEnabled(True)
            else:
                self.status_label.setText("Not logged in - click Settings")
                self.status_label.setStyleSheet("color: #FF6B6B;")
                self.submit_button.setEnabled(False)

        def open_settings(self):
            dialog = SettingsDialog(self.api_client, self)
            if dialog.exec() == QDialog.Accepted:
                self.check_login_status()
