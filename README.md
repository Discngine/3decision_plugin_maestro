# 3decision Maestro Plugin

A Maestro plugin to search and load structures from the 3decision database.

## Features

- **Search**: Search for structures by keyword, PDB code, target name, or other criteria
- **Column Filters**: Filter results by any column (supports numeric filters like `<2.0` for resolution)
- **Projects**: Browse and load structures from your 3decision projects
- **Transformation Matrices**: Structures from projects are loaded with their alignment transformations
- **Associated Files**: View and open associated files (CCP4, MTZ, PDB, CIF, etc.)
- **Metadata**: Structure properties are preserved in the Maestro Project Table

## Installation

1. In Maestro, go to **Scripts > Install Custom Scripts...**

2. Navigate to the `3decision_plugin_maestro` folder and select `threedecision_maestro.py`

3. Click **Install**

4. Restart Maestro

5. The plugin appears in **Scripts > 3decision**

**Note:** The installer automatically copies both `threedecision_maestro.py` and the `threedecision_maestro_dir/` folder containing the plugin files.

## Configuration

1. Open the plugin from **Scripts > 3decision**
2. Click **Settings**
3. Enter your 3decision API URL (e.g., `https://your-instance.discngine.cloud`)
4. Enter your API Key
5. Click **Test Connection** to verify
6. Click **Save**

Configuration is saved to `~/.3decision_maestro_config`.

## Usage

### Search Tab
- Enter a search term and click **Submit**
- Use the filter fields below the search to narrow results
- Resolution filter supports: `<2.0`, `>1.5`, `1.5-3.0`, `<=2.0`
- Select structures and click **Load Selected in Maestro**

### Projects Tab
- Click **Refresh Projects** to load your projects
- Click a project to see its structures
- Use filters to narrow down structures
- Click **View** to see associated files for a structure
- Select structures and click **Load Selected Structures**

### Associated Files Tab
- Shows files for the selected structure (CCP4 maps, MTZ, etc.)
- **Open in Maestro**: Import structure/map files directly
- **Download & Open**: Open with system default application

## Loaded Structure Properties

Structures imported into Maestro include these properties:
- `s_user_3decision_structure_id`
- `s_user_3decision_external_code`
- `s_user_3decision_label`
- `s_user_3decision_source`

## Requirements

- Maestro 2020-1 or later
- Network access to your 3decision server

## Troubleshooting

**Plugin doesn't appear in Scripts menu:**
- Restart Maestro after installation

**Connection failed:**
- Verify your API URL includes `https://`
- Check that your API key is valid
- Check network/proxy settings
