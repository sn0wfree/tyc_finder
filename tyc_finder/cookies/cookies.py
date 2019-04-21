# -*- coding: utf-8 -*-
import json


class CookieParser(object):

    @staticmethod
    def get_drive(driver):
        return driver

    @staticmethod
    def save_cookies(driver, cookies_file='cookies.json', public='tyc_finder/cookies/'):
        cookies = driver.get_cookies()

        with open(public + cookies_file, 'w') as f:
            f.write(json.dumps(cookies))
        print('cookies saved at {} '.format(public + cookies_file))

    @staticmethod
    def read_cookies(cookies_file, public='tyc_finder/cookies/'):
        # self.browser.get(self.start_url)
        # self.browser.delete_all_cookies()

        print('will load cookies at {} '.format(public + cookies_file))
        with open(public + cookies_file, 'r', encoding='utf-8') as f:
            list_cookies = json.loads(f.read())

        return list_cookies

    @classmethod
    def insert_cookies(cls, driver, list_cookies):
        for cookie in list_cookies:
            driver.add_cookie(cookie)
            #    {
            #     'domain': cookie['domain'],
            #     'name': cookie['name'],
            #     'value': cookie['value'],
            #     'path': '/',
            #     'expires': None
            # })
        return driver

    @classmethod
    def read_insert_cookies(cls, driver, cookies_file, public='tyc_finder/cookies/'):
        list_cookies = cls.read_cookies(cookies_file, public=public)
        cls.insert_cookies(driver, list_cookies)
        driver.refresh()

    @classmethod
    def load_refresh_cookies(cls, driver, cookies_file, public='tyc_finder/cookies/', refresh=True):
        if refresh:
            cls.save_cookies(driver, cookies_file, public)
        else:
            cls.read_insert_cookies(driver, cookies_file, public=public)

