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
        """Load universe data"""
        if os.path.exists(self.universe_file):
            try:
                with open(self.universe_file, 'r') as f:
                    self.universe_data = json.load(f)
                st.write(f"✅ Universe data loaded successfully")
                st.write(f"Found {len(self.universe_data.get('characters', {}))} characters")
                st.write(f"Found {len(self.universe_data.get('locations', {}))} locations")
                st.write(f"Found {len(self.universe_data.get('stories', []))} stories")
            except Exception as e:
                st.error(f"Error loading universe data: {str(e)}")
                self.universe_data = {'characters': {}, 'locations': {}, 'stories': []}
        else:
            st.error("Universe data not found. Creating new universe.")
            self.universe_data = {
                'characters': {},
                'locations': {},
                'relationships': {},
                'events': [],
                'stories': [],
                'last_updated': None
            }

    def save_universe(self):
        """Save universe data"""
        self.universe_data['last_updated'] = datetime.now().isoformat()
        with open(self.universe_file, 'w') as f:
            json.dump(self.universe_data, f, indent=2)

    def generate_id(self, prefix, year=None, month=None, day=None, sequence=None):
        """Generate ID with specified format"""
        if not year:
            now = datetime.now()
            year = now.year
            month = now.month
            day = now.day
            
        # Get latest sequence number for the day
        if not sequence:
            existing_ids = []
            if prefix == "CHAR":
                existing_ids = [char_data['id'] for char_data in self.universe_data['characters'].values()]
            elif prefix == "LOC":
                existing_ids = [loc_data['id'] for loc_data in self.universe_data['locations'].values()]
            elif prefix == "STORY":
                existing_ids = [story.get('id', '') for story in self.universe_data['stories']]
            
            # Filter IDs for the current day
            today_prefix = f"{prefix}{year}{month:02d}{day:02d}"
            today_ids = [id for id in existing_ids if id.startswith(today_prefix)]
            
            if today_ids:
                # Get the highest sequence number
                sequence = max([int(id[-5:]) for id in today_ids]) + 1
            else:
                sequence = 1

        return f"{prefix}{year}{month:02d}{day:02d}{sequence:05d}"

    def add_character(self, name, attributes):
        """Add or update character"""
        name_lower = name.lower()
        existing_char = None
        
        # Check for existing character
        for char_name, char_data in self.universe_data['characters'].items():
            if char_name.lower() == name_lower:
                existing_char = char_data
                st.warning(f"Character {name} already exists! Updating instead.")
                break
        
        if existing_char:
            # Update existing character but keep the ID
            char_id = existing_char['id']
            attributes['id'] = char_id
            attributes['created_date'] = existing_char['created_date']
            if 'story_appearances' in existing_char:
                attributes['story_appearances'] = existing_char['story_appearances']
        else:
            # Generate new ID for new character
            char_id = self.generate_id("CHAR")
            attributes['id'] = char_id
            attributes['created_date'] = datetime.now().isoformat()
            attributes['story_appearances'] = []

        attributes['last_updated'] = datetime.now().isoformat()
        self.universe_data['characters'][name] = attributes
        self.save_universe()
        return True

    def add_location(self, name, details):
        """Add or update location"""
        name_lower = name.lower()
        existing_loc = None
        
        # Check for existing location
        for loc_name, loc_data in self.universe_data['locations'].items():
            if loc_name.lower() == name_lower:
                existing_loc = loc_data
                st.warning(f"Location {name} already exists! Updating instead.")
                break

        if existing_loc:
            # Update existing location but keep the ID
            loc_id = existing_loc['id']
            details['id'] = loc_id
            details['created_date'] = existing_loc['created_date']
            if 'story_appearances' in existing_loc:
                details['story_appearances'] = existing_loc['story_appearances']
        else:
            # Generate new ID for new location
            loc_id = self.generate_id("LOC")
            details['id'] = loc_id
            details['created_date'] = datetime.now().isoformat()
            details['story_appearances'] = []

        details['last_updated'] = datetime.now().isoformat()
        self.universe_data['locations'][name] = details
        self.save_universe()
        return True

    def get_character_by_id(self, char_id):
        """Get character details by ID"""
        for name, data in self.universe_data['characters'].items():
            if data.get('id') == char_id:
                return name, data
        return None, None

    def get_location_by_id(self, loc_id):
        """Get location details by ID"""
        for name, data in self.universe_data['locations'].items():
            if data.get('id') == loc_id:
                return name, data
        return None, None

    def get_story_by_id(self, story_id):
        """Get story details by ID"""
        for story in self.universe_data['stories']:
            if story.get('id') == story_id:
                return story
        return None

def main():
    st.set_page_config(page_title="MinnalAmmu Universe Builder", layout="wide")
    st.title("🌟 MinnalAmmu Universe Builder")

    # Initialize UniverseBuilder
    builder = UniverseBuilder()

    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose Action",
        ["View Universe", "Add Character", "Add Location", "View Story References"]
    )

    if page == "View Universe":
        st.header("Current Universe Status")
        
        # Display Characters
        st.subheader("Characters")
        if builder.universe_data['characters']:
            for name, attrs in builder.universe_data['characters'].items():
                with st.expander(f"🦸‍♂️ {name} (ID: {attrs['id']})"):
                    st.write("Powers:", ", ".join(attrs.get('powers', [])))
                    st.write("Description:", attrs.get('description', ''))
                    st.write("ID:", attrs.get('id', 'No ID'))
                    
                    # Display linked stories
                    if 'story_appearances' in attrs and attrs['story_appearances']:
                        st.write("Appears in stories:")
                        for story_id in attrs['story_appearances']:
                            story = builder.get_story_by_id(story_id)
                            if story:
                                st.write(f"- {story['title']} ({story_id})")
                    
                    st.write("Created:", attrs.get('created_date', 'Unknown'))
                    st.write("Last Updated:", attrs.get('last_updated', 'Unknown'))
        else:
            st.info("No characters added yet.")
        
        # Display Locations
        st.subheader("Locations")
        if builder.universe_data['locations']:
            for name, details in builder.universe_data['locations'].items():
                with st.expander(f"🏢 {name} (ID: {details['id']})"):
                    st.write("Description:", details.get('description', ''))
                    st.write("ID:", details.get('id', 'No ID'))
                    
                    # Display linked stories
                    if 'story_appearances' in details and details['story_appearances']:
                        st.write("Appears in stories:")
                        for story_id in details['story_appearances']:
                            story = builder.get_story_by_id(story_id)
                            if story:
                                st.write(f"- {story['title']} ({story_id})")
                    
                    st.write("Created:", details.get('created_date', 'Unknown'))
                    st.write("Last Updated:", details.get('last_updated', 'Unknown'))
        else:
            st.info("No locations added yet.")

    elif page == "Add Character":
        st.header("Add New Character")
        
        # Show existing characters
        if builder.universe_data['characters']:
            st.subheader("Existing Characters")
            st.write(", ".join([f"{name} ({data['id']})" for name, data in builder.universe_data['characters'].items()]))
        
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
            st.write(", ".join([f"{name} ({data['id']})" for name, data in builder.universe_data['locations'].items()]))
        
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

    elif page == "View Story References":
        st.header("Story References")
        
        # Display stories and their references
        for story in builder.universe_data.get('stories', []):
            with st.expander(f"📚 {story['title']} (ID: {story['id']})"):
                st.write("Content:", story['content'])
                st.write("Moral:", story['moral_lesson'])
                st.write("\nMetadata:")
                st.write("- Theme:", story['metadata']['theme'])
                st.write("- Target Age:", story['metadata']['target_age'])
                st.write("- Word Count:", story['metadata']['word_count'])
                st.write("\nCharacters:")
                for char in story['metadata']['characters_used']:
                    char_name, char_data = builder.get_character_by_id(char) if char.startswith('CHAR') else (char, None)
                    if char_name:
                        st.write(f"- {char_name}")
                st.write("\nLocations:")
                for loc in story['metadata']['locations_used']:
                    loc_name, loc_data = builder.get_location_by_id(loc) if loc.startswith('LOC') else (loc, None)
                    if loc_name:
                        st.write(f"- {loc_name}")

if __name__ == "__main__":
    main()