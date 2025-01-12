import streamlit as st
import json
import os
from datetime import datetime
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

class StoryGenerator:
    def __init__(self):
        self.universe_file = "universe/universe_data.json"
        self.setup_ai()
        self.load_universe()
        # Initialize stories section if not exists
        if 'stories' not in self.universe_data:
            self.universe_data['stories'] = []

    def setup_ai(self):
        st.write("Setting up AI components...")
        try:
            self.llm = Ollama(model="mistral")
            st.write("✅ Ollama model initialized")
            print("✅ Ollama model initialized")
        except Exception as e:
            st.error(f"Failed to initialize Ollama: {str(e)}")
            raise e
        
        # Story generation prompt template
        self.story_prompt = PromptTemplate(
            input_variables=["characters", "locations", "theme", "target_age", "word_count"],
            template="""
            Create a superhero story with exactly {word_count} words using these elements:
            
            Characters: {characters}
            Locations: {locations}
            Theme: {theme}
            Target Age: {target_age}

            Requirements:
            1. Story should be EXACTLY {word_count} words long
            2. Story should be engaging and appropriate for the target age
            3. Include descriptions of super power usage
            4. Have a clear moral lesson
            5. Include character interactions
            6. Create an exciting conflict and resolution
            
            Format the story as:
            Title: [Story Title]
            
            Story:
            [Main story content]
            
            Moral Lesson:
            [The moral lesson of the story]

            Word Count: [Include actual word count at the end]
            """
        )
        st.write("✅ Prompt template created")
        print("✅ Prompt template created")

    def load_universe(self):
        """Load universe data"""
        st.write(f"Loading universe data from {self.universe_file}")
        if os.path.exists(self.universe_file):
            try:
                with open(self.universe_file, 'r') as f:
                    self.universe_data = json.load(f)
                st.write(f"✅ Universe data loaded successfully")
                print(f"✅ Universe data loaded successfully")
                st.write(f"Found {len(self.universe_data.get('characters', {}))} characters")
                print(f"Found {len(self.universe_data.get('characters', {}))} characters")
                st.write(f"Found {len(self.universe_data.get('locations', {}))} locations")
                print(f"Found {len(self.universe_data.get('locations', {}))} locations")
            except Exception as e:
                st.error(f"Error loading universe data: {str(e)}")
                self.universe_data = {'characters': {}, 'locations': {}}
        else:
            st.error("Universe data not found. Please create universe first using universe_builder.py")
            self.universe_data = {'characters': {}, 'locations': {}}

    def get_available_characters(self):
        """Get list of available characters"""
        return list(self.universe_data.get('characters', {}).keys())

    def get_available_locations(self):
        """Get list of available locations"""
        return list(self.universe_data.get('locations', {}).keys())

    def count_words(self, text):
        """Count words in text"""
        return len(text.split())

    def generate_story(self, selected_characters, selected_locations, theme, target_age, word_count):
        """Generate a story using the selected elements"""
        st.write("Starting story generation...")
        try:
            # Get character details
            st.write("Processing character details...")
            character_details = []
            for char in selected_characters:
                powers = self.universe_data['characters'][char].get('powers', [])
                desc = self.universe_data['characters'][char].get('description', '')
                character_details.append(f"{char} ({', '.join(powers)})")
            st.write(f"✅ Processed {len(character_details)} characters")
            print(f"✅ Processed {len(character_details)} characters")

            # Get location details
            st.write("Processing location details...")
            location_details = []
            for loc in selected_locations:
                desc = self.universe_data['locations'][loc].get('description', '')
                location_details.append(f"{loc}: {desc}")
            st.write(f"✅ Processed {len(location_details)} locations")
            print(f"✅ Processed {len(location_details)} locations")

            # Generate story
            st.write("Preparing prompt...")
            prompt = self.story_prompt.format(
                characters="\n".join(character_details),
                locations="\n".join(location_details),
                theme=theme,
                target_age=target_age,
                word_count=word_count
            )
            st.write("✅ Prompt prepared")
            print("✅ Prompt prepared")

            st.write("Sending prompt to Ollama...")
            # Test Ollama connection before generating
            # test_response = self.llm("Hello")
            # st.write("✅ Ollama test response received")
            # print("✅ Ollama test response received")
            
            # Generate actual story
            st.write("Generating story...")
            story = self.llm(prompt)
            st.write("✅ Story generated successfully")
            print("✅ Story generated successfully")
            print(story)
            return story

        except Exception as e:
            st.error(f"Error generating story: {str(e)}")
            st.error("Full error details:", exc_info=True)
            return None
        
    def save_story_to_universe(self, story_data, metadata):
        """Save generated story to universe"""
        st.write("Saving story to universe...")
        
        # Generate story ID
        story_id = self.generate_id("STORY")
        
        story_entry = {
            'id': story_id,
            'title': story_data.get('title', '').strip(),
            'content': story_data.get('story', '').strip(),
            'moral_lesson': story_data.get('moral', '').strip(),
            'metadata': {
                'generated_date': datetime.now().isoformat(),
                'theme': metadata['theme'],
                'target_age': metadata['target_age'],
                'word_count': metadata['word_count'],
                'characters_used': [self.universe_data['characters'][char]['id'] for char in metadata['characters']],
                'locations_used': [self.universe_data['locations'][loc]['id'] for loc in metadata['locations']]
            }
        }
        
        print(f"Created story entry with ID: {story_id}")
        
        # Add to universe data
        if 'stories' not in self.universe_data:
            self.universe_data['stories'] = []
        
        # Only save if we have actual content
        if story_entry['title'] and story_entry['content']:
            self.universe_data['stories'].append(story_entry)
            
            # Update character references with story ID
            for char in metadata['characters']:
                char_data = self.universe_data['characters'][char]
                if 'story_appearances' not in char_data:
                    char_data['story_appearances'] = []
                char_data['story_appearances'].append(story_id)
            
            # Update location references with story ID
            for loc in metadata['locations']:
                loc_data = self.universe_data['locations'][loc]
                if 'story_appearances' not in loc_data:
                    loc_data['story_appearances'] = []
                loc_data['story_appearances'].append(story_id)
            
            # Save updated universe
            try:
                with open(self.universe_file, 'w') as f:
                    json.dump(self.universe_data, f, indent=2)
                st.write("✅ Story saved to universe successfully")
                return story_id  # Return story_id instead of True
            except Exception as e:
                st.error(f"Error saving to file: {str(e)}")
                return None  # Return None instead of False
        else:
            st.warning("Story not saved: Missing title or content")
            return False

    def get_character_stories(self, character_name):
        """Get all stories featuring a character"""
        if character_name in self.universe_data['characters']:
            return self.universe_data['characters'][character_name].get('story_appearances', [])
        return []

    def get_location_stories(self, location_name):
        """Get list of stories featuring a location"""
        if location_name in self.universe_data['locations']:
            return self.universe_data['locations'][location_name].get('story_appearances', [])
        return []
    
    def get_character_by_id(self, char_id):
        """Get character name by ID"""
        for name, data in self.universe_data['characters'].items():
            if data.get('id') == char_id:
                return name
        return None

    def get_location_by_id(self, loc_id):
        """Get location name by ID"""
        for name, data in self.universe_data['locations'].items():
            if data.get('id') == loc_id:
                return name
        return None

    def get_story_by_id(self, story_id):
        """Get story by ID"""
        for story in self.universe_data['stories']:
            if story.get('id') == story_id:
                return story
        return None

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


def main():
    st.set_page_config(page_title="MinnalAmmu Story Generator", layout="wide")
    st.title("⚡ MinnalAmmu Story Generator")

    # Initialize story generator
    generator = StoryGenerator()
    
    # Check if universe has content
    if not generator.get_available_characters():
        st.warning("No characters found in the universe. Please add characters using the Universe Builder first.")
        st.stop()

    # Story Generation Interface
    st.header("Create New Story")

    # Story parameters
    with st.form("story_form"):
        # Character selection
        available_characters = generator.get_available_characters()
        selected_characters = st.multiselect(
            "Select Characters",
            options=available_characters,
            default=[available_characters[0]] if available_characters else None
        )

        # Location selection
        available_locations = generator.get_available_locations()
        selected_locations = st.multiselect(
            "Select Locations",
            options=available_locations,
            default=[available_locations[0]] if available_locations else None
        )

        # Theme selection
        theme = st.selectbox(
            "Story Theme",
            ["Friendship", "Courage", "Responsibility", "Teamwork", "Family", 
             "Innovation", "Environmental Protection", "Helping Others"]
        )

        # Target age
        target_age = st.select_slider(
            "Target Age Group",
            options=["6-8", "8-10", "10-12"]
        )

        # Word count selection
        word_count = st.number_input(
            "Number of Words",
            min_value=100,
            max_value=1000,
            value=200,
            step=50,
            help="Choose how many words you want in your story"
        )

        # Generate button
        generate_story = st.form_submit_button("Generate Story")

    # Story generation and display
    if generate_story:
        if not selected_characters or not selected_locations:
            st.error("Please select at least one character and one location!")
        else:
            with st.spinner("Generating your story..."):
                story = generator.generate_story(
                    selected_characters,
                    selected_locations,
                    theme,
                    target_age,
                    word_count
                )

                # story = """
                #         Title: "Minnal Ammu's Sunny Playdate"

                #             Story:
                #             On a sunny day, Minnal Ammu found kids huddled under trees at the playground. Seeing their frowns, she moved clouds to block the sun and made gentle rainfall. The children cheered! But when rain turned into a downpour, they scrambled for cover again.

                #             Minnal, feeling sad, decided to fix her mistake. She dashed through the park, swift as lightning, and stopped the rain by moving the clouds back. A friendless Minnal now had friends who shared their laughter and games.

                #             Moral Lesson:
                #             Good intentions may sometimes lead to misunderstandings. But it's important to listen, learn, and make amends when things go wrong. With a little effort, we can turn frowns into smiles!

                #         Word Count: 100
                #         """
                
                if story:
                    # Initialize variables
                    title = ""
                    story_text = ""
                    moral = ""
                    
                    # Parse story sections
                    sections = story.split('\n\n')
                    
                    # Extract title, story, and moral first
                    story_section = False
                    story_content = []
                    
                    print(f"************** Story sections: {sections}")
                    for section in sections:
                        section = section.strip()
                        print(f"------- Processing section: {section}")
                        print(f"------- Processing section: {section.strip()}")
                        if section.strip().startswith('Title:'):
                            print(f"---Found title section")
                            title = section.replace('Title:', '').strip()
                            print(f"---Title: {title}")
                        elif section.startswith('Story:'):
                            print(f"---Found story section")
                            print(f"---Story section: {section}")
                            story_section = True
                            #continue
                            #story_text = section.replace('Story:', '').strip()
                        elif section.startswith('Moral Lesson:'):
                            print(f"---Found moral section")
                            story_section = False
                            moral = section.replace('Moral Lesson:', '').strip()
                            print(f"---Moral: {moral}")
                        
                        if story_section:
                            print(f"---Adding to story content: {section}")
                            story_content.append(section)

                    story_text = '\n\n'.join(story_content)

                    # Create tabs for different viewing options
                    story_tab, raw_tab = st.tabs(["📖 Formatted Story", "🔍 Raw Output"])
                    
                    with story_tab:
                        # Display title
                        if title:
                            st.title(title)
                            
                        # Create columns FIRST
                        left_col, right_col = st.columns([2,1])
                        
                        # Save story to universe
                        story_data = {
                            'title': title,  # Make sure to strip whitespace
                            'story': story_text,  # Clean the story text
                            'moral': moral  # Clean the moral lesson
                        }

                        # Add debug prints
                        print(f"Prepared story data:")
                        print(f"Title: {story_data['title']}")
                        print(f"Story length: {len(story_data['story'])}")
                        print(f"Moral length: {len(story_data['moral'])}")
                        
                        metadata = {
                            'theme': theme,
                            'target_age': target_age,
                            'word_count': word_count,
                            'characters': selected_characters,
                            'locations': selected_locations
                        }

                        with left_col:
                            # Display main story
                            st.markdown("### Story")
                            st.markdown(story_text)
                            
                            # Display word count
                            actual_word_count = generator.count_words(story_text)
                            st.caption(f"Story Word Count: {actual_word_count}")
                            
                            # Add download button
                            if title and story_text:
                                download_text = f"# {title}\n\n{story_text}"
                                if moral:
                                    download_text += f"\n\nMoral Lesson:\n{moral}"
                                    
                                st.download_button(
                                    label="Download Story",
                                    data=download_text,
                                    file_name=f"{title.lower().replace(' ', '_')}.txt",
                                    mime="text/plain"
                                )

                        with right_col:
                            # Display story details
                            st.markdown("### Story Details")
                            st.markdown("**Characters:**")
                            for char in selected_characters:
                                st.write(f"- {char}")
                            
                            st.markdown("**Locations:**")
                            for loc in selected_locations:
                                st.write(f"- {loc}")
                            
                            st.markdown("**Theme:**")
                            st.write(theme)
                            
                            st.markdown("**Target Age:**")
                            st.write(target_age)
                            
                            # Display moral lesson
                            if moral:
                                st.markdown("### Moral Lesson")
                                st.info(moral)
####
                            # Save and show detailed statistics
                            story_id = generator.save_story_to_universe(story_data, metadata)
                            if story_id:  # Check for story_id instead of True
                                st.success(f"✨ Story saved to universe! (ID: {story_id})")
                                
                                # Create statistics tabs
                                stats_tab1, stats_tab2 = st.tabs(["📊 Character Stats", "🌍 Location Stats"])
                                
                                with stats_tab1:
                                    st.markdown("### Character Statistics")
                                    for char in selected_characters:
                                        char_data = generator.universe_data['characters'][char]
                                        char_stories = generator.get_character_stories(char)
                                        
                                        # Character section
                                        st.markdown(f"#### 📚 {char}")
                                        st.write(f"Character ID: {char_data['id']}")
                                        st.write(f"Total appearances: {len(char_stories)}")
                                        
                                        # Powers display
                                        if char_data.get('powers'):
                                            st.write("Powers:")
                                            for power in char_data['powers']:
                                                st.write(f"  • {power}")
                                        
                                        # Story appearances
                                        if char_stories:
                                            st.write("Story Appearances:")
                                            for story_id in char_stories:
                                                story = generator.get_story_by_id(story_id)
                                                if story:
                                                    st.markdown(f"**{story['title']}** ({story_id})")
                                                    st.markdown(f"""
                                                        - Theme: {story['metadata']['theme']}
                                                        - Target Age: {story['metadata']['target_age']}
                                                        - Word Count: {story['metadata']['word_count']}
                                                        - Generated: {story['metadata']['generated_date']}
                                                    """)
                                        st.markdown("---")  # Add separator between characters
                                
                                with stats_tab2:
                                    st.markdown("### Location Statistics")
                                    for loc in selected_locations:
                                        loc_data = generator.universe_data['locations'][loc]
                                        loc_stories = generator.get_location_stories(loc)
                                        
                                        # Location section
                                        st.markdown(f"#### 🏢 {loc}")
                                        st.write(f"Location ID: {loc_data['id']}")
                                        st.write(f"Total appearances: {len(loc_stories)}")
                                        
                                        # Description
                                        if loc_data.get('description'):
                                            st.write("Description:")
                                            st.write(loc_data['description'])
                                        
                                        # Story appearances
                                        if loc_stories:
                                            st.write("Featured in Stories:")
                                            for story_id in loc_stories:
                                                story = generator.get_story_by_id(story_id)
                                                if story:
                                                    st.markdown(f"**{story['title']}** ({story_id})")
                                                    st.markdown("Characters in this story:")
                                                    for char_id in story['metadata']['characters_used']:
                                                        char_name = generator.get_character_by_id(char_id)
                                                        if char_name:
                                                            st.write(f"  • {char_name}")
                                        st.markdown("---")  # Add separator between locations

                                    # Overall location statistics
                                    st.markdown("### Location Overview")
                                    total_stories = len(set([story_id for loc in selected_locations 
                                                           for story_id in generator.get_location_stories(loc)]))
                                    st.write(f"Total unique stories featuring selected locations: {total_stories}")
####
                    with raw_tab:
                        # Display raw output
                        st.markdown("### Raw Generated Output")
                        st.text_area("Raw Story Output", story, height=400)
                        
                        # Add copy button
                        if st.button("Copy Raw Output"):
                            st.code(story)  # Shows in a copyable format

if __name__ == "__main__":
    main()