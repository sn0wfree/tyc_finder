# -*- coding: utf-8 -*-
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import OrderedDict

__author__ = 'sn0wfree'


class SpiderHeader(object):
    pass


class SpiderSession(object):
    @staticmethod
    def _adpative(driver, adaptive=True):
        if adaptive:
            driver.set_window_position(0, 0)
            driver.set_window_size(1024, 768)
        else:

            pass
        return driver

    @staticmethod
    def create_driver_Chrome(headless):
        if headless:
            option = webdriver.ChromeOptions()
            option.add_argument('headless')
            driver = webdriver.Chrome(chrome_options=option)
        else:
            driver = webdriver.Chrome()

        return driver

    @classmethod
    def create_session(cls, core='Chrome', headless=True, adaptive=True):
        if core == 'Chrome':
            driver = cls.create_driver_Chrome(headless=headless)
            driver = cls._adpative(driver, adaptive=adaptive)
        else:
            raise ValueError('unsupported driver!')
        return driver





