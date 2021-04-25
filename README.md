# Binance Staking Notifier (Slack Bot)
Slack bot to publish availability updates for Binance staking products

## Requirements
- Python 3.6 or higher

## Setup

Clone repo & install third party requirements:
- `git clone https://github.com/Darren-McConnell/lbxd_slack_bot.git` 
- `pip3 install -r requirements.txt`

Install bot to slack workspace:
1. Open https://api.slack.com/
2. Select "Create a custom app" -> "Create New App"
3. Under "Features" -> "OAuth & Permissions" -> "Scopes" -> "Bot Token Scopes": Add the permissions scopes `chat:write` & `chat:write:public`
4. Select "Features" -> "OAuth & Permissions" -> "OAuth Tokens for Your Workspace" -> "Install to Workspace"

Python config (`config.py`):
- slackbot_token = Slack app "Bot User OAuth Token"
- slack_channel_id = https://www.wikihow.com/Find-a-Channel-ID-on-Slack-on-PC-or-Mac

## Usage
`python3 BinanceLockedStakingCheck.py`
