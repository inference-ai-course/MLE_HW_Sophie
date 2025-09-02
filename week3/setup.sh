#!/bin/bash
# Setup script for Voice Assistant

echo "Setting up Voice Assistant environment..."

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "WARNING: OPENAI_API_KEY environment variable is not set!"
    echo "Please set it by running:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or create a .env file with:"
    echo "OPENAI_API_KEY=your-api-key-here"
    echo ""
fi

echo "Setup complete!"
echo ""
echo "To run the Voice Assistant:"
echo "python week_3_assignment_voice_agent_development.py"
echo ""
echo "Or directly with uvicorn:"
echo "uvicorn week_3_assignment_voice_agent_development:app --reload"