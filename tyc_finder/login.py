# -*- coding: utf-8 -*-

import time
import gevent
import random


# from tyc_finder.tools.slide_block.slide_block3 import ParseImages

class TycLogin(object):
    """

    """

    def __init__(self, driver, username, password, login_url='https://www.tianyancha.com/login'):
        """

        :param driver:
        :param username:
        :param password:
        :param login_url:
        """
        self.driver = driver
        self.login_url = login_url

        self.username = username
        self.password = password

    @staticmethod
    def get_url(driver, url):
        driver.get(url)
        gevent.sleep(1)
        return driver

    # 常量定义
    # 登录天眼查
    def login(self, text_login='请输入11位手机号码', text_password='请输入登录密码'):
        return self._login(self.driver, self.username, self.password, self.login_url,
                           text_login=text_login, text_password=text_password)

    # 登录天眼查
    @staticmethod
    def _login(driver, username, password, login_url='https://www.tianyancha.com/login',
               text_login='请输入11位手机号码', text_password='请输入登录密码'):
        """

        :param driver:
        :param username:
        :param password:
        :param login_url:
        :param text_login:
        :param text_password:
        :return:
        """
        time_start = time.time()

        # driver = SpiderSession.create_driver(executable_path, core='Chrome', headless=self.headless, adaptive=True)

        print('the username and password will autofill, please do not move cursor or use keyboards !')
        driver.get(login_url)

        # 模拟登陆：Selenium Locating Elements by Xpath
        time.sleep(random.random())

        # 关闭底栏
        # driver.find_element_by_xpath("//img[@id='tyc_banner_close']").click()

        driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']").click()
        # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_login))[-2].send_keys(username)
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_password))[-1].send_keys(password)
        # click //*[@id="web-content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/div[5]
        # click login in bottom
        driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin.Login']").click()
        # 手工登录，完成滑块验证码
        print('请现在开始操作键盘鼠标，在15s内点击登录并手工完成滑块验证码。批量爬取只需一次登录。')
        time.sleep(10)
        print('还剩5秒。')
        time.sleep(5)
        # s = input('s')

        time_end = time.time()
        print('您的本次登录共用时{}秒。'.format(int(time_end - time_start)))
        return driver


class TycLoginVIP(TycLogin):
    def __init__(self, driver, username, password, login_url):
        super(TycLoginVIP, self).__init__(driver, username, password, login_url)


if __name__ == '__main__':
    pass
