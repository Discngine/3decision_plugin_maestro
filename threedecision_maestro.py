#Name: Discngine 3decision
#Command: pythonrun threedecision_maestro.run_plugin
"""
3decision Maestro Plugin

Search and load structures from 3decision database into Maestro.
"""

__version__ = "1.0"
_panel = None


def run_plugin():
    """Launch the 3decision plugin panel."""
    global _panel
    import sys
    import os

    # The plugin files are in threedecision_maestro_dir/ next to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.join(script_dir, "threedecision_maestro_dir")

    # Fallback: check if files are in the same directory (development mode)
    if not os.path.exists(os.path.join(plugin_dir, "gui.py")):
        plugin_dir = script_dir

    if plugin_dir not in sys.path:
        sys.path.insert(0, plugin_dir)

    try:
        from gui import ThreeDecisionPanel
        _panel = ThreeDecisionPanel.panel(run=True)
        return _panel
    except ImportError as e:
        msg = (
            f"Failed to load 3decision plugin: {e}\n\n"
            "The plugin folder must contain: gui.py, api_client.py\n\n"
            f"Current location: {plugin_dir}"
        )
        print(f"ERROR: {msg}")
        try:
            from schrodinger.Qt.QtWidgets import QMessageBox
            QMessageBox.critical(None, "3decision Plugin Error", msg)
        except:
            pass
        return None


def open_panel():
    """
    Alternative entry point for opening the panel.

    This can be used from the Maestro Python console:
        import threedecision_maestro
        threedecision_maestro.open_panel()
    """
    return run_plugin()


if __name__ == "__main__":
    # Allow running the script directly for testing
    run_plugin()
