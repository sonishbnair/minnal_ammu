import streamlit as st
import json
import os
from datetime import datetime

class UniverseBuilder:
    def __init__(self):
        self.universe_file = "universe/universe_data.json"
        os.makedirs("universe", exist_ok=True)
        self.load_universe()

    def load_universe(self):
        if os.path.exists(self.universe_file):
            with open(self.universe_file, 'r') as f:
                self.universe_data = json.load(f)
        else:
            self.universe_data = {
                'characters': {},
                'locations': {},
                'relationships': {},
                'events': [],
                'last_updated': None
            }

    def save_universe(self):
        self.universe_data['last_updated'] = datetime.now().isoformat()
        with open(self.universe_file, 'w') as f:
            json.dump(self.universe_data, f, indent=2)

    def add_character(self, name, attributes):
        """Add or update character while preventing duplicates"""
        name_lower = name.lower()
        if name_lower in {k.lower() for k in self.universe_data['characters'].keys()}:
            st.warning(f"Character {name} already exists! Updating instead.")
        
        self.universe_data['characters'][name] = {
            **attributes,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        self.save_universe()
        return True

    def add_location(self, name, details):
        """Add or update location"""
        name_lower = name.lower()
        if name_lower in {k.lower() for k in self.universe_data['locations'].keys()}:
            st.warning(f"Location {name} already exists! Updating instead.")
        
        self.universe_data['locations'][name] = {
            **details,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        self.save_universe()
        return True

def main():
    st.set_page_config(page_title="MinnalAmmu Universe Builder", layout="wide")
    st.title("** MinnalAmmu Universe Builder **")

    # Initialize UniverseBuilder
    builder = UniverseBuilder()

    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose Action",
        ["View Universe", "Add Character", "Add Location"]
    )

    if page == "View Universe":
        st.header("Current Universe Status")
        
        # Display Characters
        st.subheader("Characters")
        if builder.universe_data['characters']:
            for name, attrs in builder.universe_data['characters'].items():
                with st.expander(f"🦸‍♂️ {name}"):
                    st.write("Powers:", ", ".join(attrs.get('powers', [])))
                    st.write("Description:", attrs.get('description', ''))
                    st.write("Created:", attrs.get('created_date', 'Unknown'))
                    st.write("Last Updated:", attrs.get('last_updated', 'Unknown'))
        else:
            st.info("No characters added yet.")
        
        # Display Locations
        st.subheader("Locations")
        if builder.universe_data['locations']:
            for name, details in builder.universe_data['locations'].items():
                with st.expander(f"🏢 {name}"):
                    st.write("Description:", details.get('description', ''))
                    st.write("Created:", details.get('created_date', 'Unknown'))
                    st.write("Last Updated:", details.get('last_updated', 'Unknown'))
        else:
            st.info("No locations added yet.")

    elif page == "Add Character":
        st.header("Add New Character")
        
        # Show existing characters
        if builder.universe_data['characters']:
            st.subheader("Existing Characters")
            st.write(", ".join(builder.universe_data['characters'].keys()))
        
        # Character input form
        with st.form("character_form"):
            name = st.text_input("Character Name")
            powers = st.text_area("Powers (one per line)")
            description = st.text_area("Character Description")
            
            if st.form_submit_button("Add Character"):
                if name:
                    character_data = {
                        'powers': [p.strip() for p in powers.split('\n') if p.strip()],
                        'description': description
                    }
                    if builder.add_character(name, character_data):
                        st.success(f"Added/Updated character: {name}")
                else:
                    st.error("Please enter a character name!")

    elif page == "Add Location":
        st.header("Add New Location")
        
        # Show existing locations
        if builder.universe_data['locations']:
            st.subheader("Existing Locations")
            st.write(", ".join(builder.universe_data['locations'].keys()))
        
        # Location input form
        with st.form("location_form"):
            name = st.text_input("Location Name")
            description = st.text_area("Location Description")
            
            if st.form_submit_button("Add Location"):
                if name:
                    location_data = {
                        'description': description
                    }
                    if builder.add_location(name, location_data):
                        st.success(f"Added/Updated location: {name}")
                else:
                    st.error("Please enter a location name!")

if __name__ == "__main__":
    main()