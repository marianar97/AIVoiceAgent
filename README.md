# AI Voice Assistant for Debt Collection Simulation

This project implements an AI voice assistant that simulates debt collection conversations using LiveKit for real-time audio communication and OpenAI's GPT-4 for natural language processing.

## Features

- Real-time audio communication using LiveKit
- Speech-to-text conversion using OpenAI Whisper
- Natural language processing using GPT-4
- Text-to-speech conversion using OpenAI's TTS
- Professional debt collection conversation simulation

## Prerequisites

- Python 3.8 or higher
- LiveKit account and credentials
- OpenAI API key
- Microphone and speakers

## Setup

1. Clone this repository
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   LIVEKIT_URL=your_livekit_url
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

## Usage

1. Run the script:

   ```bash
   python debt_collector_assistant.py
   ```

2. The assistant will create a LiveKit room and wait for connections
3. Connect to the room using a LiveKit client
4. Start speaking - the assistant will:
   - Convert your speech to text
   - Generate a response using GPT-4
   - Convert the response to speech and play it back

## Notes

- The assistant is configured to maintain a professional and respectful tone while discussing debt collection
- The conversation history is maintained during the session
- Press Ctrl+C to exit the program

## Security Considerations

- Never commit your `.env` file or expose your API keys
- The LiveKit room is configured with a 5-minute timeout when empty
- Maximum of 2 participants per room for privacy

## License

MIT License
