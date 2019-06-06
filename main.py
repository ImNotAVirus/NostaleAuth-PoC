#!/bin/env python3
import binascii
import logging
import requests
import uuid


__author__ = 'DarkyZ/ImNotAVirus <https://github.com/ImNotAVirus>'
__credits__ = ['morsisko <https://github.com/morsisko>']
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'DarkyZ/ImNotAVirus <https://github.com/ImNotAVirus>'


URL_API_BASE = 'https://spark.gameforge.com/api/v1'
NOSTALE_PLATFORM_ID = 'dd4e22d6-00d1-44b9-8126-d8b40e0cd7c9'

class NostaleUser(object):
    '''
    Probably need to add some docs... Or maybe not
    '''

    username:str = None
    password:str = None
    lang:str = None
    locale:str = None
    platform_game_id:str = None
    token:str = None
    game_account_id:str = None
    installation_id:str = None

    def __init__(self, username:str, password:str, lang='fr', locale='fr_FR',
                 platform_game_id=NOSTALE_PLATFORM_ID, installation_id=None):
        self.username = username
        self.password = password
        self.lang = lang
        self.locale = locale
        self.platform_game_id = platform_game_id

        if not installation_id:
            self.installation_id = str(uuid.uuid4())
        else:
            self.installation_id = installation_id

    def __repr__(self):
        return '<NostaleUser {}>'.format(self.username)

    def __gen_token(self):
        url = '%s/auth/thin/sessions' % URL_API_BASE
        data = {
            'gfLang': self.lang,
            'identity': self.username,
            'locale': self.locale,
            'password': self.password,
            'platformGameId': self.platform_game_id
        }
        res = requests.post(url, json=data).json()

        if 'token' in res.keys():
            self.token = res['token']
        else:
            logging.error('Wrong credentials')
            return

        if 'platformGameAccountId' in res.keys():
            self.game_account_id = res['platformGameAccountId']
        else:
            logging.error('Unable to find the game account id (maybe you\'re using a new account)')

    def gen_token(self):
        if not self.token:
            self.__gen_token()

        if not self.game_account_id:
            return

        url = '%s/auth/thin/codes' % URL_API_BASE
        data = {'platformGameAccountId': self.game_account_id}
        headers = {
            'TNT-Installation-Id': self.installation_id,
            'User-Agent': 'TNTClientMS2/1.3.39',
            'Authorization': 'Bearer %s' % self.token
        }
        res = requests.post(url, headers=headers, json=data).json()
        code = res['code']

        logging.debug('Code received: %s' % code)
        return binascii.hexlify(code.encode()).decode()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('-l', '--lang', default='fr')
    parser.add_argument('-L', '--locale', default='fr_FR')
    parser.add_argument('-g', '--platform-game-id', default=NOSTALE_PLATFORM_ID)
    parser.add_argument('-i', '--installation-id', default=None, help='Check your Windows registry or randomize it')
    parser.add_argument('-v', '--verbosity', help='increase output verbosity', action='store_true')
    args = parser.parse_args()

    # Just set the logger config
    fmt = '[%(asctime)s][%(levelname)s] %(message)s'
    if args.verbosity:
        logging.basicConfig(format=fmt, level=logging.DEBUG)
    else:
        logging.basicConfig(format=fmt, level=logging.INFO)

    # # Log in and generate a token
    user = NostaleUser(args.username, args.password, lang=args.lang, locale=args.locale,
                       platform_game_id=args.platform_game_id, installation_id=args.installation_id)

    logging.debug('User: %s' % user)
    logging.info('Your hex encoded code: %s' % user.gen_token())
    logging.info('Another hex encoded code: %s' % user.gen_token())
