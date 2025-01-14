
# Story/Scene Image Builder


The Story/Image Image Builder is a Python-based tool that automatically generates illustrations for children's stories featuring Minnal Ammu, a super-powered girl with lightning abilities. 
The SDXL-Turbo AI model runs locally to generate the story/scene images

The tool:
1. Takes a story ID as input
2. Reads story details, characters, and locations from a universe data JSON file
3. Crafts optimized prompts that capture the story's essence
4. Uses the SDXL-Turbo AI model(run locally) to generate child-friendly illustrations
5. Supports configurable image sizes (default 256x256)
6. Uses weighted prompts to handle CLIP's token limits while maintaining story context
7. Automatically manages system resources and cleans up memory

Key features:
- Optimized for children's book illustrations
- Handles character powers and descriptions
- Maintains consistent art style across stories
- Efficient memory management for both CPU and GPU
- Organized output storage by story ID

The builder is specifically tuned for the Minnal Ammu universe, ensuring generated images match the story's themes and character descriptions while maintaining a child-friendly, vibrant art style.


# SDXL Turbo Model Setup Guide for Intel Mac

This guide provides step-by-step instructions for setting up Stable Diffusion XL Turbo on Intel-based Mac systems.

## System Requirements

- Intel-based MacBook Pro
- Minimum 16GB RAM
- At least 8GB free disk space
- macOS 10.15 or later
- Python 3.10 or later

## Installation Steps

### 1. Create Project Directory
```bash
# Create and enter project directory
mkdir sdxl-project
cd sdxl-project
```

### 2. Set Up Python Environment
```bash
# Install Miniconda if not already installed
brew install --cask miniconda

# Initialize conda (restart terminal after this)
conda init zsh  # or 'conda init bash' if using bash

# Create new environment
conda create -n sdxl-env python=3.10
conda activate sdxl-env
```

### 3. Install Dependencies
```bash
# Install git-lfs for model download
brew install git-lfs
git lfs install
```

### 4. Create and Install Requirements
Create a file named `requirements.txt` with the following content:
```txt
# PyTorch and related packages
torch==2.2.0
torchvision==0.17.0
torchaudio==2.2.0

# Stable Diffusion essentials
diffusers==0.24.0
transformers==4.36.2
accelerate==0.25.0
safetensors==0.4.1

# Required dependencies
Pillow==10.1.0
numpy==1.26.4
huggingface-hub==0.20.1
scipy==1.11.4
```

Install the requirements:
```bash
pip install -r requirements.txt
```

### 5. Download SDXL Turbo Model
```bash
# Create models directory
mkdir -p models
cd models

# Clone the model repository
git lfs install
git clone https://huggingface.co/stabilityai/sdxl-turbo
cd ..
```

## Project Structure
Your final project structure should look like this:
```

models/
│   └── sdxl-turbo/  # Downloaded model files
------------------------------------------
sdxl-project/
├── generated_images/
├── requirements.txt
├── setup.md
└── generate_images.py
```

## Testing the Setup

Create a test script `test_model_setup.py`:

Run the test:
```bash
python test_setup.py
```
