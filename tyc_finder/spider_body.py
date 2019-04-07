# -*- coding: utf-8 -*-
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import OrderedDict

__author__ = 'sn0wfree'


class Spider(object):
    def __init__(self, driver_path, headless=True):
        self.driver = SpiderSession.create_driver(driver_path, core='Chrome', headless=headless, adaptive=False)
        pass


class SpiderSession(object):
    @staticmethod
    def _adaptive(driver, adaptive=True):
        if adaptive:
            driver.set_window_position(0, 0)
            driver.set_window_size(1024, 768)
        else:
            pass
        return driver

    @staticmethod
    def create_driver_Chrome(executable_path, headless=True, *other_arguements):
        if headless:
            option = webdriver.ChromeOptions()
            option.add_argument('headless')
            if other_arguements is not None:
                for v in other_arguements:
                    option.add_argument(v)
            driver = webdriver.Chrome(executable_path, chrome_options=option)
        else:
            driver = webdriver.Chrome(executable_path)

        return driver

    @classmethod
    def create_driver(cls, executable_path, core='Chrome', headless=True, adaptive=True):
        if core == 'Chrome':
            driver = cls.create_driver_Chrome(executable_path, headless=headless)
            driver = cls._adaptive(driver, adaptive=adaptive)
        else:
            raise ValueError('unsupported driver!')
        return driver


if __name__ == '__main__':
    # SpiderSession.create_session(executable_path='tyc_finder/drivers/chromedriver_mac')
    chromedriver_mac_path = '/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac'
    spider = Spider(chromedriver_mac_path, headless=False)

    pass
