# -*- coding: utf-8 -*-
import time, gevent

from tyc_finder.spider_body import Spider


class Tianyancha_login(object):

    def __init__(self, driver, username, password, login_url='https://www.tianyancha.com/login'):
        self.driver = driver
        self.login_url = login_url
        self.username = username
        self.password = password

    def get_url(self, url):
        self.driver.get(url)
        gevent.sleep(1)

    def get_login_url(self):
        self.driver.get(self.login_url)

    # 常量定义

    # def __init__(self, username, password, headless=False):
    #     self.username = username
    #     self.password = password
    #     self.headless = headless
    #     self.driver = self.login(text_login='请输入11位手机号码', text_password='请输入登录密码')

    def login_process(self, text_login='请输入11位手机号码', text_password='请输入登录密码',
                      login_url='https://www.tianyancha.com/login'):
        time_start = time.time()
        # 操作行为提示
        print('the username and password will autofill, please do not move cursor or use keyboards !')
        # open login_url
        self.get_url(login_url)

        # 模拟登陆：Selenium Locating Elements by Xpath
        time.sleep(1)

        # 关闭底栏
        self.driver.find_element_by_xpath("//img[@id='tyc_banner_close']").click()
        # 切换至账号登录
        self.driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']").click()
        # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符

        self.driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_login))[-2].send_keys(self.username)
        self.driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_password))[-1].send_keys(
            self.password)

        # 手工登录，完成滑块验证码
        print('请现在开始操作键盘鼠标，在15s内点击登录并手工完成滑块验证码。批量爬取只需一次登录。')
        time.sleep(10)
        print('还剩5秒。')
        time.sleep(5)

        time_end = time.time()
        print('您的本次登录共用时{}秒。'.format(int(time_end - time_start)))
        return self


def test():
    chromedriver_mac_path = '/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac'

    username = '16621278541'
    password = 'Imsn0wfree'
    account_info = dict(username=username, password=password)

    spider = Spider(chromedriver_mac_path, headless=False)
    T = Tianyancha_login(spider.driver, username, password)
    T.login_process()


if __name__ == '__main__':
    chromedriver_mac_path = '/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac'

    browser = Spider(chromedriver_mac_path, headless=False).driver
    browser.get('https://account.ch.com/NonRegistrations-Regist')
    from tyc_finder.tools.slide_block import Wait, Expect, By

    Wait(browser, 60).until(
        Expect.visibility_of_element_located((By.CSS_SELECTOR, "div[data-target='account-login']"))
    )
    email = browser.find_element_by_css_selector("div[data-target='account-login']")
    email.click()

    pass
