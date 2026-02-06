"""
3decision Maestro Plugin v1.0

A plugin to search and load structures from 3decision database into Maestro.
"""
#Name: 3decision
#Command: pythonrun threedecision_maestro.run_plugin

# Plugin version
__version__ = "1.0"

def run_plugin():
    """
    Launch the 3decision plugin panel.
    This is the entry point called by Maestro's pythonrun command.
    """
    from .gui import ThreeDecisionPanel
    panel = ThreeDecisionPanel.panel(run=True)
    return panel
