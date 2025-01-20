import json
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import glob
import sys

class StoryComposer:
    def __init__(self, script_dir):
        """
        Initialize StoryComposer with base directory path
        
        Args:
            script_dir (str): Directory where the script is located
        """
        # Set up directory paths relative to script location
        self.base_dir = os.path.dirname(script_dir)  # Go up one level to MinnalAmmu folder
        
        # Define paths relative to MinnalAmmu folder
        self.universe_file_path = os.path.join(
            self.base_dir, 
            "MinnalAmmu_Universe", 
            "universe", 
            "universe_data.json"
        )
        self.base_image_path = os.path.join(self.base_dir, "outputs", "story_images")
        self.output_dir = os.path.join(self.base_dir, "outputs", "story_pdfs")
        
        # Print paths for debugging
        print(f"Base directory: {self.base_dir}")
        print(f"Universe file path: {self.universe_file_path}")
        print(f"Image path: {self.base_image_path}")
        print(f"Output directory: {self.output_dir}")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Validate that universe file exists
        if not os.path.exists(self.universe_file_path):
            raise FileNotFoundError(f"Universe data file not found at: {self.universe_file_path}")
            
    def load_universe_data(self):
        """Load and parse the universe JSON data"""
        with open(self.universe_file_path, 'r') as file:
            return json.load(file)
            
    def find_story(self, story_id):
        """Find a story by its ID in the universe data"""
        universe_data = self.load_universe_data()
        for story in universe_data['stories']:
            if story['id'] == story_id:
                return story
        return None
        
    def get_latest_story_image(self, story_id):
        """Find the most recent image for a given story ID"""
        story_image_dir = os.path.join(self.base_image_path, story_id)
        if not os.path.exists(story_image_dir):
            return None
            
        # Get all image files in the directory
        image_files = glob.glob(os.path.join(story_image_dir, f"story_image_{story_id}*.png"))
        
        if not image_files:
            return None
            
        # Sort by creation time and get the most recent
        latest_image = max(image_files, key=os.path.getctime)
        return latest_image
        
    def create_story_pdf(self, story_id):
        """
        Create a PDF with the story content and image
        
        Args:
            story_id (str): ID of the story to process
            
        Returns:
            str: Path to the created PDF file
        """
        # Find the story
        story = self.find_story(story_id)
        if not story:
            raise ValueError(f"Story with ID {story_id} not found")
            
        # Get the latest story image - Exit if no image found
        image_path = self.get_latest_story_image(story_id)
        if not image_path:
            print(f"Error: No image found for story {story_id}")
            print("Story Composer requires both story and image to complete its task.")
            sys.exit(1)
            
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"story_{story_id}_{timestamp}.pdf"
        output_path = os.path.join(self.output_dir, output_filename)
            
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Use built-in fonts instead of DejaVu
        pdf.set_font('Helvetica', '', 12)
        
        # Add title
        pdf.set_font('Helvetica', 'B', 24)
        pdf.cell(0, 20, story['title'], ln=True, align='C')
        
        # Add metadata
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 10, f"Theme: {story['metadata']['theme']}", ln=True)
        pdf.cell(0, 10, f"Age Group: {story['metadata']['target_age']}", ln=True)
        
        # Add image (we know it exists at this point)
        try:
            # Get image dimensions
            with Image.open(image_path) as img:
                width, height = img.size
            # Scale image to fit page while maintaining aspect ratio
            max_width = 190  # Max width in mm for A4
            scale = max_width / width
            image_height = height * scale
            
            pdf.image(image_path, x=10, y=pdf.get_y() + 10, w=max_width)
            pdf.ln(image_height + 20)  # Add space after image
        except Exception as e:
            print(f"Error processing image: {e}")
            print("Story Composer requires both story and valid image to complete its task.")
            sys.exit(1)
        
        # Add story content
        pdf.set_font('Helvetica', '', 12)
        content = story['content'].replace('Story:\n', '').strip()
        pdf.multi_cell(0, 10, content)
        
        # Add moral lesson
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, "Moral Lesson:", ln=True)
        pdf.set_font('Helvetica', '', 12)
        pdf.multi_cell(0, 10, story['moral_lesson'])
        
        # Add footer with metadata
        pdf.ln(10)
        pdf.set_font('Helvetica', '', 10)
        generated_date = datetime.fromisoformat(story['metadata']['generated_date'])
        pdf.cell(0, 10, f"Generated: {generated_date.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, f"Word Count: {story['metadata']['word_count']}", ln=True)
        
        # Save the PDF
        try:
            pdf.output(output_path)
            print(f"PDF created successfully: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error creating PDF: {e}")
            sys.exit(1)

def main():
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Script directory: {script_dir}")
        
        # Initialize composer with script directory
        composer = StoryComposer(script_dir)
        
        # Create PDF for a story
        story_id = "STORY2025010101100"
        pdf_path = composer.create_story_pdf(story_id)
        print(f"PDF saved to: {pdf_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()