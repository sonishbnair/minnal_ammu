# AI Storytelling System

A system for generating and managing a superhero story universe using AI. The system consists of three main components:
- Universe Builder (universe_builder.py)
- Story Generator (story_generator_app.py)
- Universe Integration (universe_integration.py)

## Prerequisites

- Python 3.9 or higher
- Homebrew (for Mac)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MinnalAmmu_Universe
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Setting up Ollama

1. Install Ollama:
```bash
# On macOS:
brew install ollama
```

2. Start Ollama service:
```bash
# Start Ollama service
brew services start ollama

# Verify service is running
brew services list
```

3. Pull the Mistral model:
```bash
ollama pull mistral
```

4. Verify model installation:
```bash
ollama list
# Expected output:
# NAME              ID              SIZE      MODIFIED
# mistral:latest    [ID]            4.1 GB    [timestamp]
```

## Project Structure

```
MinnalAmmu_Universe/
├── README.md
├── requirements.txt
├── universe/
│   └── universe_data.json
├── universe_builder.py
├── story_generator_app.py
└── universe_integration.py
```

## Requirements

Minimal requirements for running the system:
```
streamlit==1.32.2
langchain==0.1.12
ollama==0.1.7
python-dotenv==1.0.1
```

## Running the Application

1. Ensure Ollama service is running:
```bash
brew services list
# Should show ollama as "started"
```

2. Start the Universe Builder:
```bash
streamlit run universe_builder.py
```

3. Create your superhero universe by adding:
- Characters
- Locations
- Relationships
- Events

4. Generate stories:
```bash
streamlit run story_generator_app.py
```

## Stopping the Service

When you're done using the application:
```bash
# Stop Ollama service
brew services stop ollama

# Verify service is stopped
brew services list
```

## Common Issues and Solutions

1. "Error: could not connect to ollama app, is it running?"
   - Solution: Run `brew services start ollama`
   - Verify with `brew services list`

2. "Error: pull model manifest: file does not exist"
   - Solution: Use `ollama pull mistral` instead of version-specific tags

3. Model verification:
   - Use `ollama list` to check installed models
   - Should see mistral:latest (approximately 4.1 GB)


