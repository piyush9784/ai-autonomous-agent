# AI Agent - Google Search & Task Automation

A LangChain-powered AI agent that can search Google and automate various tasks.

## Features

- 🔍 **Google Search** - Search the web using Tavily
- 📧 **Email Automation** - Send emails via SMTP
- 📁 **File Operations** - Read, write, list files
- 💻 **System Commands** - Run safe system commands
- ⏰ **Utilities** - Get current time/date

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Get required keys:**
   - [OpenAI API Key](https://platform.openai.com/api-keys)
   - [Tavily API Key](https://tavily.com/) (free tier available)

4. **Run the agent:**
   ```bash
   python agent.py
   ```

## Usage

Example commands:
```
Search for Python tutorials
Write hello world to test.txt  
List files in Downloads
What time is it?
Send email to user@example.com with subject Test and body Hello
Run ls command
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| OPENAI_API_KEY | Yes | OpenAI API key |
| TAVILY_API_KEY | Yes | For Google search |
| SMTP_SERVER | No | Email SMTP server |
| SMTP_PORT | No | SMTP port |
| SMTP_USER | No | Email address |
| SMTP_PASSWORD | No | Email password |
