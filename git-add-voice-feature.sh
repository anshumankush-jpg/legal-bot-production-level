#!/bin/bash
# Git commands to add voice feature files

# Add backend voice service and routes
git add backend/app/services/voice_service.py
git add backend/app/api/routes/voice.py
git add backend/app/main.py
git add backend/requirements.txt

# Add frontend modifications
git add frontend/src/app/components/chat/chat.component.ts

# Add documentation
git add docs/voice.md
git add VOICE_FEATURE_IMPLEMENTATION_SUMMARY.md

# Commit
git commit -m "Add ChatGPT-style voice feature: STT/TTS with Google Cloud integration

- Backend: Voice service with Google Cloud Speech-to-Text and Text-to-Speech
- Backend: Voice API routes (/api/voice/stt, /api/voice/tts, /api/voice/voices)
- Frontend: Updated chat component to load personalization for auto-read
- Documentation: Complete voice feature docs with setup instructions
- Features: Voice input button, speech-to-text, text-to-speech, auto-read responses"

# Push
git push origin main
