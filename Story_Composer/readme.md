# StoryComposer Documentation

## Overview
StoryComposer is a Python class that creates PDF documents from stories stored in a universe JSON file, combining story text with generated images. It's designed to work within the MinnalAmmu project structure.

## Directory Structure
```
MinnalAmmu/
├── MinnalAmmu_Universe/
│   └── universe/
│       └── universe_data.json
├── outputs/
│   ├── story_images/
│   │   └── [STORY_ID]/
│   └── story_pdfs/
└── Story_Composer/
    └── story_composer.py
```

## Key Features
* Reads story data from universe JSON file
* Finds and uses the most recent story image
* Creates formatted PDF with story content
* Maintains consistent directory structure
* Includes error handling and validation

## Main Functions

### `load_universe_data()`
* Loads and parses the universe JSON file
* Returns parsed JSON data

### `find_story(story_id)`
* Searches for a story by ID in universe data
* Returns story data if found, None if not found

### `get_latest_story_image(story_id)`
* Finds the most recent image for a given story ID
* Returns path to latest image file

### `create_story_pdf(story_id)`
* Creates PDF with following components:
  - Title
  - Theme and age group
  - Story image
  - Story content
  - Moral lesson
  - Metadata (generation date, word count)

## PDF Format
The generated PDF includes:
* Story title in large bold font
* Metadata (theme and age group)
* Story image scaled to fit page
* Story content in readable format
* Moral lesson section
* Footer with generation date and word count

## Error Handling
* Validates existence of story data
* Requires both story and image to be present
* Handles image processing errors
* Provides clear error messages
