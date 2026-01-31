# Browser MCP Integration

This project includes integration with **Browser MCP** to allow AI tools (like Claude Desktop, Cursor, etc.) to automate your web browser.

## Setup Instructions

### 1. Requirements
- **Google Chrome** (or Chromium-based browser)
- **Browser MCP Extension**: You will be prompted to install this when you first run the server, or get it from the [Chrome Web Store](https://chrome.google.com/webstore/detail/browser-mcp/...).

### 2. Run the Server
Use the included npm script to start the MCP server:

```sh
npm run mcp:browser
```

### 3. Configure Your AI Client
Add the following configuration to your AI tool's settings (e.g., `claude_desktop_config.json` or Cursor settings):

```json
{
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["@browsermcp/mcp@latest"]
    }
  }
}
```

### 4. How it Works
- The server runs locally on your machine.
- It connects to your existing Chrome browser instance via the extension.
- This allows the AI to see what you see, click buttons, and navigate websites using your logged-in session.
