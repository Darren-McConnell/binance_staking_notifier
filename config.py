from pathlib import Path

# binance config
locked_staking_endpoint = 'https://www.binance.com/gateway-api/v1/friendly/pos/union?pageSize=100&pageIndex=1&status=ALL'
defi_staking_endpoint = 'https://www.binance.com/bapi/earn/v1/friendly/defi-pos/union?pageSize=15&pageIndex=1&status=ALL'

# slack config
slackbot_token = ''
slack_channel_id = ''

# watchlist config
base = Path(__file__).parent.absolute()
defi_watchlist = base / 'watchlist_defi.csv'
locked_watchlist = base / 'watchlist_locked.csv'

# script config
poll_sleep = 30