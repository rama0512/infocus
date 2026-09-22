# Productivity Monitor Platform

## Architecture Overview

Privacy-first productivity monitoring with webcam gaze detection and screenshot analysis.

## Components

1. **Frontend** - Browser-based capture with client-side encryption
2. **Backend** - AWS serverless architecture
3. **ML/AI** - MediaPipe (gaze), Bedrock Claude (VLM)

## Privacy Features

- Client-side encryption before upload
- User-controlled encryption keys
- Server-side encryption at rest (S3, DynamoDB)
- TLS in transit
- Optional: User can keep encryption keys locally (zero-knowledge)

## Setup Instructions

1. Deploy AWS infrastructure: `cd infrastructure && terraform apply`
2. Configure frontend: Update `frontend/config.js` with API endpoints
3. Run locally: `cd frontend && python -m http.server 8000`

## Cost Estimate (Basic Usage)

- Bedrock Claude Haiku: ~$0.25 per 1M input tokens
- Lambda: Free tier covers basic usage
- S3: ~$0.023/GB
- DynamoDB: Free tier covers basic usage
