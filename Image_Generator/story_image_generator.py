import os
import torch
import gc
from diffusers import AutoPipelineForText2Image
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import json
from datetime import datetime
from config_loader import ConfigLoader
import argparse

class MinmalAmmuImageBuilder:
    def __init__(self, config: Dict[str, Dict]):
        """
        Initialize the image builder with configurations
        
        Args:
            config: Dictionary containing all configurations from config.ini
        """
        self.config = config
        self.model_path = config['model']['path']
        self.default_size = config['model']['default_size']
        
        # Load universe data first
        self.universe_data = self._load_universe_data(config['data']['universe_data_path'])
        
        # Pipeline is initialized only when needed
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_universe_data(self, universe_data_path: str) -> Dict:
        """
        Load the universe data from JSON file
        
        Args:
            universe_data_path: Path to the universe data JSON file
            
        Returns:
            Dict containing universe data
        """
        try:
            with open(universe_data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load universe data: {str(e)}")

    def validate_story_exists(self, story_id: str) -> bool:
        """
        Check if story exists in universe data
        
        Args:
            story_id: Unique identifier for the story
            
        Returns:
            bool: True if story exists, False otherwise
        """
        return any(story["id"] == story_id for story in self.universe_data.get("stories", []))

    def _initialize_pipeline(self):
        """Initialize the text-to-image pipeline if not already initialized"""
        if self.pipeline is None:
            try:
                self.pipeline = AutoPipelineForText2Image.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                    local_files_only=True
                ).to(self.device)
            except Exception as e:
                raise Exception(f"Failed to initialize pipeline: {str(e)}")

    def _cleanup_memory(self):
        """Clean up GPU/CPU memory"""
        gc.collect()
        if self.device == "cuda":
            torch.cuda.empty_cache()

    def _get_story(self, story_id: str) -> Dict:
        """
        Get story details from universe data
        
        Args:
            story_id: Unique identifier for the story
            
        Returns:
            Dict containing story details
        """
        for story in self.universe_data.get("stories", []):
            if story["id"] == story_id:
                return story
        raise Exception(f"Story {story_id} not found in universe data")

    def _get_character_details(self, character_ids: List[str]) -> List[Dict]:
        """Get character details from universe data"""
        characters = []
        for char_id in character_ids:
            char = self.universe_data["characters"].get(char_id)
            if not char:
                for name, details in self.universe_data["characters"].items():
                    if details["id"] == char_id:
                        char = details
                        break
            
            if char:
                characters.append({
                    "name": char_id if char_id in self.universe_data["characters"] else name,
                    "description": char["description"],
                    "powers": char.get("powers", [])
                })
        return characters

    def _get_location_details(self, location_ids: List[str]) -> List[Dict]:
        """Get location details from universe data"""
        locations = []
        for loc_id in location_ids:
            loc = self.universe_data["locations"].get(loc_id)
            if not loc:
                for name, details in self.universe_data["locations"].items():
                    if details["id"] == loc_id:
                        loc = details
                        break
            
            if loc:
                locations.append({
                    "name": loc_id if loc_id in self.universe_data["locations"] else name,
                    "description": loc["description"]
                })
        return locations

    def _get_main_character_features(self, char: Dict) -> str:
        """Extract only essential character features"""
        main_features = []
        
        if "indian" in char['description'].lower():
            main_features.append("Indian")
        if "brown skin" in char['description'].lower():
            main_features.append("brown skin")
        
        if char.get('powers'):
            power = char['powers'][0]
            if "fly" in power:
                main_features.append("can fly")
            elif "run" in power:
                main_features.append("super fast")
        
        return ", ".join(main_features)

    def _get_scene_details(self, story: Dict) -> str:
        """Get additional scene details"""
        content = story["content"].lower()
        
        time_of_day = "daytime"
        if "night" in content or "evening" in content:
            time_of_day = "nighttime"
        elif "sunset" in content:
            time_of_day = "sunset"
        elif "morning" in content:
            time_of_day = "morning"
            
        weather = "clear sky"
        if "rain" in content:
            weather = "rainy"
        elif "storm" in content:
            weather = "stormy"
        elif "cloud" in content:
            weather = "cloudy"
            
        return f"{time_of_day}, {weather}, detailed background"

    def _create_prompt(self, story: Dict) -> str:
        """Create an AI prompt based on story and universe details"""
        character_ids = story["metadata"]["characters_used"]
        location_ids = story["metadata"]["locations_used"]
        
        characters = self._get_character_details(character_ids)
        locations = self._get_location_details(location_ids)

        content = story["content"].replace("Story:", "").strip().split(". ")
        key_scene = content[0] if content else ""
        
        elements = []
        
        if characters:
            main_char = characters[0]
            char_desc = f"{main_char['name']}, {self._get_main_character_features(main_char)}"
            elements.append(char_desc)
        
        if locations:
            elements.append(f"at {locations[0]['name']}")
        
        return f"children's illustration, {', '.join(elements)}"

    def _validate_image_size(self, size: int) -> int:
        """Validate and adjust image size to meet model requirements"""
        if size < self.config['model']['min_size']:
            return self.config['model']['min_size']
        if size > self.config['model']['max_size']:
            return self.config['model']['max_size']
            
        step = self.config['model']['size_step']
        return (size // step) * step

    def generate_image(self, story_id: str, image_size: Optional[int] = None) -> Tuple[str, float]:
        """Generate an image for the given story"""
        try:
            # First check if story exists before initializing the pipeline
            if not self.validate_story_exists(story_id):
                raise Exception(f"Story {story_id} not found in universe data")

            # Initialize pipeline only when we know we'll use it
            self._initialize_pipeline()
            
            # Get story and create prompt
            story = self._get_story(story_id)
            prompt = self._create_prompt(story)
            size = self._validate_image_size(image_size or self.default_size)
            
            # Generate image with weighted prompts
            start_time = time.time()
            
            style_config = self.config['style']
            weights = style_config['weights']
            
            weighted_prompts = [
                (prompt, weights['main_prompt']),
                (f"Style: {style_config['base_style']}", weights['style']),
                (f"Scene details: {self._get_scene_details(story)}", weights['scene']),
                (f"Quality: {style_config['quality_boost']}", weights['quality'])
            ]
            
            combined_prompt = " AND ".join([f"({p[0]}:{p[1]})" for p in weighted_prompts])
            
            print(f"-------> Generating image for story {story_id} with prompt: {combined_prompt} <-------")
            # Generate image
            pipeline_config = self.config['pipeline']
            image = self.pipeline(
                prompt=combined_prompt,
                num_inference_steps=pipeline_config['num_inference_steps'],
                height=size,
                width=size,
                guidance_scale=pipeline_config['guidance_scale'],
                num_images_per_prompt=pipeline_config['num_images_per_prompt']
            ).images[0]
            
            generation_time = time.time() - start_time
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_dir = Path(self.config['output']['story_images_dir']) / story_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / f"story_image_{story_id}_{timestamp}.png"
            image.save(output_path)
            
            # Cleanup
            self._cleanup_memory()
            
            return str(output_path), generation_time
            
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Generate story images using MinmalAmmu Image Builder')
    parser.add_argument('--story_id', type=str, help='Story ID for image generation')
    parser.add_argument('--size', type=int, help='Image size (optional)', default=512)
    parser.add_argument('--config', type=str, help='Path to config file', default='config.ini')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = ConfigLoader(args.config).get_all_config()
        
        # Initialize builder with configuration
        builder = MinmalAmmuImageBuilder(config)
        
        # First validate if story exists
        if not builder.validate_story_exists(args.story_id):
            print(f"Error: Story {args.story_id} not found in universe data")
            return 1
        
        # Generate image only if story exists
        image_path, gen_time = builder.generate_image(args.story_id, image_size=args.size)
        
        print(f"Image generated successfully in {gen_time:.2f} seconds")
        print(f"Image saved at: {image_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())