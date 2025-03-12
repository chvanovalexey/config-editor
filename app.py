import streamlit as st
import json
from datetime import datetime
import streamlit.components.v1 as components
from database import ConfigDatabase
from config_generator import generate_config

# Initialize database
db = ConfigDatabase()

st.set_page_config(  
    page_title="Configuration Editor",  
    page_icon="🌙",  
    layout="wide",  
    initial_sidebar_state="expanded",  
    menu_items=None
    )

# Session state initialization
if 'current_config_id' not in st.session_state:
    st.session_state.current_config_id = None
if 'show_left_panel' not in st.session_state:
    st.session_state.show_left_panel = True
if 'formatted_json' not in st.session_state:
    st.session_state.formatted_json = ""
if 'formatted_edit_json' not in st.session_state:
    st.session_state.formatted_edit_json = ""
if 'formatted_edit_json_full' not in st.session_state:
    st.session_state.formatted_edit_json_full = ""
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

def validate_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

def format_json(json_str):
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return json_str

def clear_formatted_values():
    """Clear all formatted JSON values in session state"""
    st.session_state.formatted_json = ""
    st.session_state.formatted_edit_json = ""
    st.session_state.formatted_edit_json_full = ""

def change_tab(tab_index):
    """Change to a specific tab and clear formatted values"""
    st.session_state.active_tab = tab_index
    clear_formatted_values()

# Title
st.title("Configuration Editor")

# Navigation tabs
tab1, tab2, tab3 = st.tabs(["New Configuration", "Edit Configuration", "Load Configuration"])

# Tab 1: New Configuration
with tab1:
    st.header("Start New Configuration")
    
    # Description field
    description = st.text_input("Configuration Description", key="new_description")
    
    # JSON Editor with syntax highlighting using a custom component
    st.write("Enter your JSON configuration:")
    
    # Use a text area with reasonable height for JSON input
    # Use the formatted value from session state if available
    initial_value = st.session_state.formatted_json if st.session_state.formatted_json else ""
    json_input = st.text_area("JSON Configuration", value=initial_value, height=400, key="new_json_input")
    
    # Validate and format JSON on button click
    if st.button("Format JSON", key="format_button"):
        if validate_json(json_input):
            st.session_state.formatted_json = format_json(json_input)
            st.experimental_rerun()
        else:
            st.error("Invalid JSON format. Please check your input.")
    
    # Save initial configuration
    if st.button("Save Configuration", key="save_initial"):
        if not description:
            st.error("Please enter a description.")
        elif not json_input:
            st.error("Please enter a JSON configuration.")
        elif not validate_json(json_input):
            st.error("Invalid JSON format. Please check your input.")
        else:
            try:
                # Save to database
                config_id = db.save_initial_config(description, json_input)
                
                # Generate new config
                generated_config = generate_config(json_input)
                
                # Update database with generated config
                db.update_generated_configs(config_id, generated_config)
                
                # Update session state
                st.session_state.current_config_id = config_id
                
                # Clear the formatted JSON
                clear_formatted_values()
                
                # Success message and navigate to edit tab
                st.success("Configuration saved! You can now edit the generated configuration.")
                st.session_state.active_tab = 1  # Set to Edit Configuration tab
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error saving configuration: {str(e)}")

# Tab 2: Edit Configuration
with tab2:
    st.header("Edit Generated Configuration")
    
    if st.session_state.current_config_id:
        try:
            # Retrieve the current configuration
            config = db.get_config(st.session_state.current_config_id)
            
            # Display configuration description and timestamp
            st.write(f"**Description:** {config['description']}")
            st.write(f"**Created:** {config['created_at']}")
            
            # Toggle button for showing/hiding original configuration
            if st.button("Toggle Original Config View", key="toggle_view"):
                st.session_state.show_left_panel = not st.session_state.show_left_panel
                # Clear formatted values when toggling view
                clear_formatted_values()
                st.experimental_rerun()
            
            # Layout for side-by-side comparison
            if st.session_state.show_left_panel:
                col1, col2 = st.columns(2)
                
                # Left panel (original generated config - read-only)
                with col1:
                    st.write("**Generated Configuration (Read-only)**")
                    generated_config = config['generated_config'] or config['original_config']
                    st.text_area("", value=generated_config, height=500, key="generated_config_view", disabled=True)
                
                # Right panel (editable)
                with col2:
                    st.write("**Editable Configuration**")
                    modified_config = config['modified_config'] or config['generated_config'] or config['original_config']
                    # Use the formatted value if available
                    display_value = st.session_state.formatted_edit_json if st.session_state.formatted_edit_json else modified_config
                    edited_config = st.text_area("", value=display_value, height=500, key="edit_config_view")
            else:
                # Only show editable panel
                st.write("**Editable Configuration**")
                modified_config = config['modified_config'] or config['generated_config'] or config['original_config']
                # Use the formatted value if available
                display_value = st.session_state.formatted_edit_json_full if st.session_state.formatted_edit_json_full else modified_config
                edited_config = st.text_area("", value=display_value, height=600, key="edit_config_view_full")
            
            # Format JSON button
            if st.button("Format JSON", key="format_edit_button"):
                current_config = st.session_state.edit_config_view if st.session_state.show_left_panel else st.session_state.edit_config_view_full
                if validate_json(current_config):
                    formatted = format_json(current_config)
                    if st.session_state.show_left_panel:
                        st.session_state.formatted_edit_json = formatted
                    else:
                        st.session_state.formatted_edit_json_full = formatted
                    st.experimental_rerun()
                else:
                    st.error("Invalid JSON format. Please check your input.")
            
            # Save button
            if st.button("Save Edited Configuration", key="save_edited"):
                current_config = st.session_state.edit_config_view if st.session_state.show_left_panel else st.session_state.edit_config_view_full
                
                if not validate_json(current_config):
                    st.error("Invalid JSON format. Please check your input.")
                else:
                    try:
                        # Update the database with the modified config
                        db.update_generated_configs(
                            st.session_state.current_config_id, 
                            config['generated_config'] or config['original_config'], 
                            current_config
                        )
                        # Clear the formatted values after saving
                        clear_formatted_values()
                        st.success("Configuration updated successfully!")
                    except Exception as e:
                        st.error(f"Error saving configuration: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading configuration: {str(e)}")
    else:
        st.info("No active configuration. Start a new configuration or load an existing one.")

# Tab 3: Load Configuration
with tab3:
    st.header("Load Saved Configuration")
    
    # Get all configurations
    configs = db.get_all_configs()
    
    if not configs:
        st.info("No saved configurations found.")
    else:
        # Create a dataframe for display
        config_data = {
            "ID": [config['id'] for config in configs],
            "Description": [config['description'] for config in configs],
            "Date/Time": [config['created_at'] for config in configs]
        }
        
        # Display configurations
        selected_indices = st.dataframe(
            config_data, 
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Description": st.column_config.TextColumn("Description"),
                "Date/Time": st.column_config.DatetimeColumn("Date/Time", format="YYYY-MM-DD HH:mm:ss")
            },
            use_container_width=True,
            height=400
        )
        
        # Selection for loading
        if configs:  # Double-check to make sure we still have configs
            selected_config_id = st.selectbox(
                "Select configuration to load",
                options=[config['id'] for config in configs],
                format_func=lambda x: f"ID: {x} - {next((c['description'] for c in configs if c['id'] == x), '')}"
            )
            
            if st.button("Load Selected Configuration", key="load_config"):
                st.session_state.current_config_id = selected_config_id
                # Clear any formatted JSON values when loading a new configuration
                clear_formatted_values()
                st.success(f"Configuration ID {selected_config_id} loaded.")
                st.experimental_rerun()


# Add custom CSS for better JSON formatting
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True) 