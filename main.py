# -*- coding: utf-8 -*-
import time

import requests

from collections import namedtuple
from multiprocessing import Process, Lock

from bs4 import BeautifulSoup
from torrequest import TorRequest

from libs.pymongodb import pymongodb
from libs import utils
from libs import decorators


class Parser(object):
    def __init__(self):
        self.tor_proxies = {
            'http': "socks5://127.0.0.1:9050",
            'https': "socks5://127.0.0.1:9050"
        }
        self.client = requests.Session()
        self.url_with_all_crypto = 'https://coinmarketcap.com/all/views/all/'
        self.page_url = 'https://coinmarketcap.com/{}'
        self.market_url = 'https://coinmarketcap.com{}#markets'
        self.lock = Lock()
        self.processes_num = 1      # Desired number of processes (Set your val, but need proxy)
        self.drop_db()

    @staticmethod
    def drop_db():
        mongo = pymongodb.MongoDB('cmc')
        mongo.drop_database()

    def get_html(self, url, tor=False):
        """
        Method which send GET request to specific url and return html.
        :param url:
        :param tor:
        :return:
        """
        time.sleep(3)
        html = None
        proxies = None

        if tor:
            with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:
                tr.reset_identity()

            proxies = self.tor_proxies

        try:
            html = self.client.get(url, proxies=proxies, timeout=(3.05, 27), stream=True)
        except Exception as e:
            print(e)
            self.get_html(url)

        return html.content

    @decorators.write_log
    def write_data(self, **kwargs):
        """
        Method which insert data in specific collection.
        :param kwargs: dict of data.
        :return:
        """
        self.lock.acquire()

        try:
            mongo = pymongodb.MongoDB('cmc')
            mongo.insert_one(kwargs, 'currencies')
        finally:
            self.lock.release()

    @staticmethod
    def parse_current_amount(html):
        """
        Parse current amount of currencies.
        :param html:
        :return:
        """
        bs_obj = BeautifulSoup(html, 'lxml')
        index = bs_obj.findAll('td', {'class': 'text-center'})[-1].text.strip()

        return index

    @decorators.log
    def parse_range(self, range_):
        """
        Parse range of pages.
        :param range_:
        :return:
        """
        count = 1 if range_[0] == 0 else range_[0]

        while count != range_[1]:
            self.parse(self.get_html(self.page_url.format(count)))
            count += 1

    @staticmethod
    def parse_markets(html):
        """
        Parse markets for specific currency.
        :param html:
        :return:
        """
        bs_obj = BeautifulSoup(html, 'lxml')

        table = bs_obj.find('table', {'id': 'markets-table'})
        markets = table.findAll('a', {'class': 'link-secondary'})
        markets = list(set([market.text for market in markets]))
        Data = namedtuple('markets', ['markets', 'amount'])

        return Data(markets, len(markets))

    def parse(self, html):
        """
        Parse specific page.
        :param html:
        :return:
        """
        bs_obj = BeautifulSoup(html, 'lxml')

        # Find currencies.
        links = bs_obj.findAll('a', {'class': 'currency-name-container'})
        currencies_names = [name.text.strip() for name in links]

        # Find links on full description page.
        full_desc_links = [link['href'] for link in links]
        full_desc_links = list(map(lambda x: self.market_url.format(x.strip()), full_desc_links))

        # Find markets for all found currencies.
        markets = [self.parse_markets(self.get_html(url)) for url in full_desc_links]

        for i in range(len(currencies_names)):
            self.write_data(currency=currencies_names[i], markets=markets[i].markets,
                            markets_count=markets[i].amount)

    def run(self):
        """
        1. Get html with currencies on one page.
        2. Find current currencies amount , then split this number on rages (need for multiprocessing).
        3. Start processes.
        :return:
        """
        html = self.get_html(self.url_with_all_crypto)
        current_crypto_amount = self.parse_current_amount(html)
        ranges = utils.split_on_ranges((lambda x: (x / 100).__round__())(int(current_crypto_amount)),
                                       self.processes_num)

        for range_ in ranges:
            Process(target=self.parse_range, args=(range_,)).start()


if __name__ == '__main__':
    try:
        Parser().run()
    except:
        utils.logger('Success status: %s' % 'ERROR', 'aki_adagaki.log')
