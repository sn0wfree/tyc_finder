# -*- coding: utf-8 -*-
import time, gevent, random
import re
import pandas as pd
from bs4 import BeautifulSoup

from collections import OrderedDict
from tyc_finder.tools.utils import WriterJson

from tyc_finder.spider_body import SpiderSession, Spider
from tyc_finder.base import BasicFuncs
from tyc_finder.searchtool import SearchTool
from tyc_finder.login import TycLogin

from tyc_finder.cookies.cookies import CookieParser


def main_test(url='https://www.tianyancha.com/login',
              username='16621278541',
              password='Imsn0wfree',
              chromedriver_mac_path='/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac',
              init=True):
    driver = Spider(chromedriver_mac_path, headless=False).driver
    TycLogin(driver, username, password, url).login()
    if init:

        CookieParser.save_cookies(driver, cookies_file='cookies.json', public='cookies/')
    else:
        CookieParser.load_refresh_cookies(driver, cookies_file='cookies.json', public='cookies/')

    time.sleep(1 + random.random())

    SearchTool._search(driver, '大润发', stype='company')
    time.sleep(100)

    return driver


if __name__ == '__main__':
    main_test(init=True)
    pass
