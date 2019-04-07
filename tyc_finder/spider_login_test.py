# -*- coding: utf-8 -*-
import time, gevent
import re
import pandas as pd
from bs4 import BeautifulSoup

from collections import OrderedDict
from tyc_finder.tools.utils import WriterJson

from tyc_finder.spider_body import SpiderSession, Spider


class Tianyancha_login(object):

    def __init__(self, driver, username, password, login_url='https://www.tianyancha.com/login'):
        self.driver = driver
        self.login_url = login_url

        self.username = username
        self.password = password

    def get_url(self, url):
        self.driver.get(url)
        gevent.sleep(1)

    # 常量定义

    # 登录天眼查
    def login(self, text_login='请输入11位手机号码', text_password='请输入登录密码'):
        time_start = time.time()

        # driver = SpiderSession.create_driver(executable_path, core='Chrome', headless=self.headless, adaptive=True)

        print('the username and password will autofill, please do not move cursor or use keyboards !')
        self.driver.get(self.login_url)

        # 模拟登陆：Selenium Locating Elements by Xpath
        time.sleep(1)

        # 关闭底栏
        self.driver.find_element_by_xpath("//img[@id='tyc_banner_close']").click()

        self.driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']").click()
        # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符
        self.driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_login))[-2].send_keys(self.username)
        self.driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_password))[-1].send_keys(
            self.password)
        # click //*[@id="web-content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/div[5]
        # click login in bottom
        self.driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin.Login']").click()
        # 手工登录，完成滑块验证码
        print('请现在开始操作键盘鼠标，在15s内点击登录并手工完成滑块验证码。批量爬取只需一次登录。')
        time.sleep(10)
        print('还剩5秒。')
        time.sleep(5)
        # s = input('s')
        from tyc_finder.tools.slide_block.slide_block3 import ParseImages
        time_end = time.time()
        print('您的本次登录共用时{}秒。'.format(int(time_end - time_start)))
        return driver


if __name__ == '__main__':
    url = 'https://www.tianyancha.com/login'

    username = '16672839203'
    password = '***********'
    chromedriver_mac_path = '/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac'

    driver = Spider(chromedriver_mac_path, headless=False).driver
    Tl = Tianyancha_login(driver, username, password)
    Tl.login()
    pass
