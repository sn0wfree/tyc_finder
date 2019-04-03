# -*- coding: utf-8 -*-
import time, gevent
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.support.wait import WebDriverWait
from collections import OrderedDict
from tyc_finder.utils import WriterJson

from tyc_finder.spider_body import SpiderSession


class Tianyancha_Session(object):

    def __init__(self, executable_path, core='Chrome', headless=False, adaptive=True):
        self.driver = SpiderSession.create_session(executable_path, core=core, headless=headless, adaptive=adaptive)
        # self.username = username
        # self.password = password

    # 常量定义

    # def __init__(self, username, password, headless=False):
    #     self.username = username
    #     self.password = password
    #     self.headless = headless
    #     self.driver = self.login(text_login='请输入11位手机号码', text_password='请输入登录密码')

    def login_process(self, username, password, login_url='https://www.tianyancha.com/login', ):
        self.driver.get(login_url)
        gevent.sleep(10)


if __name__ == '__main__':
    Tianyancha_Session(executable_path='tyc_finder/drivers/chromedriver_mac')
    pass
