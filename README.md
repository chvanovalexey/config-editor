# Configuration Editor

A Streamlit web interface for creating, editing, and managing configurations in JSON format.

## Features

- Create new configurations in JSON format with description
- Side-by-side viewing and editing of configurations
- Toggle view to show/hide original generated configuration
- JSON validation and formatting
- History of configurations with timestamp and description
- Simple database storage in SQLite

## Setup and Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:

```bash
streamlit run app.py
```

## Usage

### Creating a New Configuration

1. Navigate to the "New Configuration" tab
2. Enter a description for your configuration
3. Input your JSON configuration in the text area
4. Click "Format JSON" to validate and format your input (optional)
5. Click "Save Configuration" to store your configuration

### Editing a Configuration

1. After creating or loading a configuration, go to the "Edit Configuration" tab
2. View the generated configuration on the left (read-only)
3. Edit the configuration on the right
4. Use the "Toggle Original Config View" button to show/hide the original configuration
5. Click "Format JSON" to validate and format your edited configuration
6. Click "Save Edited Configuration" to store your changes

### Loading a Saved Configuration

1. Navigate to the "Load Configuration" tab
2. View all saved configurations in the table
3. Select a configuration from the dropdown
4. Click "Load Selected Configuration" to load it for viewing/editing

## Extending the Application

### Custom Configuration Generator

Replace the placeholder in `config_generator.py` with your actual configuration generation logic:

```python
def generate_config(original_config):
    # Your custom logic here to transform the original_config
    # Return the transformed config as a JSON string
    return transformed_config
``` 