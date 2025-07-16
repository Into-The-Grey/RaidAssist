# RaidAssist OAuth Setup Guide

This guide explains how to set up Bungie OAuth authentication for RaidAssist.

## Prerequisites

You need a Bungie.net account to create an OAuth application.

## Step 1: Create a Bungie OAuth Application

1. Go to [Bungie Application Portal](https://www.bungie.net/en/Application)
2. Click "Create New App" or use an existing application
3. Fill in the application details:
   - **Application Name**: RaidAssist (or your preferred name)
   - **Website**: Your website URL (can be GitHub repo URL)
   - **Application Status**: Private
   - **OAuth Client Type**: Confidential
   - **Redirect URL**: `http://localhost:7777/callback` (exactly as shown)
   - **Scope**: Select the permissions you need (typically User Profile and Character Data)
   - **Origin Header**: Leave blank for desktop applications

4. Click "Create App"

## Step 2: Get Your API Credentials

After creating the app, you'll see:

- **API Key**: A long string of characters (this is your BUNGIE_API_KEY)
- **OAuth Client ID**: A shorter numeric ID (this is your BUNGIE_CLIENT_ID)
- **OAuth Client Secret**: Not needed for PKCE flow (keep it secret anyway)

## Step 3: Configure Environment Variables

### Option A: Environment Variables (Recommended)

Set these environment variables on your system:

**Windows (Command Prompt):**

```cmd
set BUNGIE_API_KEY=your_api_key_here
set BUNGIE_CLIENT_ID=your_client_id_here
set BUNGIE_REDIRECT_URI=http://localhost:7777/callback
```

**Windows (PowerShell):**

```powershell
$env:BUNGIE_API_KEY="your_api_key_here"
$env:BUNGIE_CLIENT_ID="your_client_id_here"
$env:BUNGIE_REDIRECT_URI="http://localhost:7777/callback"
```

**macOS/Linux:**

```bash
export BUNGIE_API_KEY=your_api_key_here
export BUNGIE_CLIENT_ID=your_client_id_here
export BUNGIE_REDIRECT_URI=http://localhost:7777/callback
```

### Option B: .env File (Development)

Create a `.env` file in the project root:

```env
BUNGIE_API_KEY=your_api_key_here
BUNGIE_CLIENT_ID=your_client_id_here
BUNGIE_REDIRECT_URI=http://localhost:7777/callback
```

## Step 4: Test Your Configuration

Run RaidAssist and try to authenticate. The application should:

1. Open your browser to Bungie's login page
2. Ask you to authorize the application
3. Redirect back to a success page
4. Complete authentication in RaidAssist

## Troubleshooting

### "Application is not configured for user authorization"

- Verify your redirect URL is exactly: `http://localhost:7777/callback`
- Check that OAuth Client Type is set to "Confidential"
- Ensure your BUNGIE_CLIENT_ID matches the OAuth Client ID from Bungie

### "Invalid API Key"

- Double-check your BUNGIE_API_KEY environment variable
- Make sure there are no extra spaces or characters
- Verify the API key is from the same application as the Client ID

### "Connection refused" or "Port 7777 in use"

- Make sure port 7777 is not being used by another application
- You can change the port by setting BUNGIE_REDIRECT_URI to use a different port
- Remember to update the redirect URL in your Bungie application settings too

### Browser doesn't open automatically

- The application will display the URL for manual browser navigation
- Copy and paste the URL into your browser manually

## Security Notes

- **Never share your API Key or Client Secret publicly**
- The API Key and Client ID can be safely included in environment variables
- Keep your OAuth Client Secret private (though PKCE flow doesn't require it)
- The redirect URL must exactly match what's configured in your Bungie application

## Advanced Configuration

### Using Custom Ports

If port 7777 is not available, you can use a different port:

1. Set `BUNGIE_REDIRECT_URI=http://localhost:8080/callback` (or your preferred port)
2. Update the redirect URL in your Bungie application settings
3. Make sure the port is not blocked by your firewall

### Production Deployment

For production deployments, consider:

- Using HTTPS redirect URLs for security
- Setting up proper domain-based redirect URLs
- Using secure environment variable management
- Implementing proper error handling and logging

## References

- [Bungie API Documentation](https://bungie-net.github.io/multi/index.html)
- [OAuth 2.0 PKCE Specification](https://tools.ietf.org/html/rfc7636)
- [RaidAssist GitHub Repository](https://github.com/Into-The-Grey/RaidAssist)
