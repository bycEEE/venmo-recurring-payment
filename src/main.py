import argparse
import logging
import os
import sys
import yaml

from box import Box
from venmo_api import Client as VenmoClient

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


VENMO_ACCESS_TOKEN = os.environ.get('VENMO_ACCESS_TOKEN')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug logging")
    parser.add_argument('--dry_run', '--dry-run', action='store_true',
                        help="Enable dry run")
    return parser.parse_args()


def get_config():
    with open("../config.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

    return Box(data)


def get_user(client, user):
    if 'id' in user:
        return client.user.get_user(user.id)
    if 'username' in user:
        return client.user.get_user_by_username(user.username)
    return None


# def request_money(self, amount: float,
#                     note: str,
#                     target_user_id: int = None,
#                     privacy_setting: PaymentPrivacy = PaymentPrivacy.PRIVATE,
#                     target_user: User = None,
#                     callback=None) -> Union[bool, None]:
#     """
#     Request [amount] money with [note] from the ([target_user_id] or [target_user])
#     :param amount: <float> amount of money to be requested
#     :param note: <str> message/note of the transaction
#     :param privacy_setting: <PaymentPrivacy> PRIVATE/FRIENDS/PUBLIC (enum)
#     :param target_user_id: <str> the user id of the person you are asking the money from
#     :param target_user: <User> The user object or user_id is required
#     :param callback: callback function
#     :return: <bool> Either the transaction was successful or an exception will rise.
#     """
def request_payment(client, user, services, pricing):
    try:
        if not services:
            log.warning('[%s] No valid services found, skipping payment request...', user.name)
            return
        for service in services:
            log.info('[%s] Requesting %s for %s...', user.display_name, pricing.plex.cost, service)
            if service == 'plex':
                client.payment.request_money(
                    float(pricing.plex.cost),
                    service,
                    user.id
                )
            elif service == 'spotify':
                client.payment.request_money(
                    float(pricing.spotify.cost),
                    service,
                    user.id
                )
            else:
                log.error('[%s] Service %s not found, not requesting...', user.display_name, service)
                break
            log.info('[%s] Payment for %s successfully requested!', user.display_name, service)
    except Exception as e:
        log.error('[%s] Payment request failed: %s', user.display_name, e)


def main():
    args = parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)

    if not VENMO_ACCESS_TOKEN:
        log.critical('Venmo API token not found')
        sys.exit(1)

    config = get_config()
    venmo_client = VenmoClient(access_token=VENMO_ACCESS_TOKEN)

    for user in config.users:
        venmo_user = get_user(venmo_client, user)
        if not venmo_user:
            log.warning('[%s] Skipping, user not found - check username or userId...', user.name)
            break
        request_payment(venmo_client, venmo_user, user.services, config.pricing)


if __name__ == "__main__":
    main()
