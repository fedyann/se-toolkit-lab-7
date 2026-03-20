# Bot Development Plan

## Overview
This bot provides a Telegram interface to the LMS backend, allowing students to check scores, lab status, and backend health via simple commands.

## Architecture
The bot uses a layered architecture: handlers contain pure business logic with no Telegram dependency, services handle API communication, and bot.py wires everything together. This makes handlers fully testable without Telegram.

## Task 1: Scaffold
Create the project structure with testable handlers, --test CLI mode, and pyproject.toml with uv.

## Task 2: Backend Integration
Implement /health, /scores, and /labs by calling the LMS REST API using httpx. Parse responses and format them for Telegram messages.

## Task 3: Intent Routing
Add natural language understanding using the Qwen LLM API. Route free-text messages to the appropriate handler based on detected intent.

## Task 4: Deployment
Deploy the bot on the VM using nohup, configure .env.bot.secret, and verify all commands work end-to-end in Telegram.

## Testing Strategy
Use --test mode for offline verification of all handlers. Each command must print non-empty output and exit with code 0.
