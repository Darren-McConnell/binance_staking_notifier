import csv
import json
import logging
import sys
from time import sleep
from urllib.request import urlopen
from urllib.error import URLError

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# local import
import config

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


class StakeCheck():
    def __init__(self):
        self.watch_file = {
            'locked': config.locked_watchlist, 
            'defi': config.defi_watchlist
            }
        self.endpoint = {
            'locked': config.locked_staking_endpoint,
            'defi': config.defi_staking_endpoint
            }

        logging.info('Instantiating slack client...')
        self.slack_client = WebClient(token=config.slackbot_token)
        self.channel_id = config.slack_channel_id
        
        self.staking_info = {}
        self.tracking = {'locked': [], 'defi': []}
        
        for stake_type in ('locked', 'defi'):
            self.staking_info[stake_type] = self.get_stake_status(stake_type)
            self.update_tracking(stake_type)

    @staticmethod
    def load_watchlist(filepath):
        with open(filepath, "r") as csv_file:
            return [
                f"{pair['coin']}_{pair['duration']}".lower() 
                for pair in csv.DictReader(csv_file)
                ]

    @staticmethod
    def printable_key(key):
        coin, dur = key.split('_')
        return f"{coin.title()} ({dur})"

    def update_tracking(self, stake_type):
        logging.info(f'Updating {stake_type} watchlist...')

        watchlist_file = self.watch_file[stake_type]
        products = self.load_watchlist(watchlist_file)

        for t in self.tracking[stake_type]:
            if t not in products:
                logging.info(
                    f"{self.printable_key(t)} has been removed from "
                    f"{stake_type} tracking"
                    )

        for p in products:
            if p not in self.tracking[stake_type]:
                if p in self.staking_info[stake_type].keys():
                    logging.info(f"Adding {self.printable_key(p)} to tracking")
                    # check if new pair is available for staking 
                    if self.staking_info[stake_type][p]:
                        self.send_update_msg(stake_type, p)
                else:
                    logging.warning(
                        f"{self.printable_key(p)} is not a valid {stake_type} "
                        f"pair. Consider removing from {watchlist_file}"
                        )

        self.tracking[stake_type] = products

    def check_status_change(self, stake_type):
        new = self.get_stake_status(stake_type)
        updated = [
            k for k in new.keys() 
            if new[k] != self.staking_info[stake_type][k]
            and k in self.tracking[stake_type]
            ]

        for pair in updated:
            self.send_update_msg(stake_type, pair)
        
        self.staking_info[stake_type] = new

    @staticmethod
    def parse_key(project_dict):
        return f'{project_dict["asset"].lower()}_{project_dict.get("duration", "flexible")}'

    def get_stake_status(self, stake_type):
        logging.info(f'Requesting {stake_type} staking info from binance...')
        try:
            with urlopen(self.endpoint[stake_type]) as resp:
               data = json.loads(resp.read())['data']
            logging.info('Request successful')
        except URLError as e:
            if hasattr(e, 'reason'):
                err_msg = f'Couldn\'t reach server. Reason: {e.reason}'
            elif hasattr(e, 'code'):
                err_msg = f'Server failed to fulfill the request. Error Code: {e.reason}'
            logging.exception(f'Binance request exception. {err_msg}')

        return {
            self.parse_key(project_dict): not project_dict['sellOut']
            for asset in data 
            for project_dict in asset['projects'] + asset['products'] 
            }

    def send_update_msg(self, stake_type, pair):
        available = self.staking_info[stake_type][pair]
        msg = (
            f'{self.printable_key(pair)} is '
            f'{"" if available else "no longer "}'
            'available for staking!'
            )
        logging.info(f'Posting update to slack: {msg}')
        try:
            self.slack_client.chat_postMessage(
                channel=self.channel_id, text=msg)
        except SlackApiError as e:
            logging.error(f"Slack API error posting message: {e}")


    def poll(self, sleep_time):
        while True:
            for stake_type in ('locked', 'defi'):
                self.update_tracking(stake_type)
                if self.tracking[stake_type]:
                    self.check_status_change(stake_type)
            logging.info(f'Sleeping for {sleep_time} seconds')
            sleep(sleep_time)


def main():
    stake_check = StakeCheck()
    logging.info(f'Sleeping for {config.poll_sleep} seconds')
    sleep(config.poll_sleep)
    stake_check.poll(config.poll_sleep)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Exiting...')
        sys.exit()
