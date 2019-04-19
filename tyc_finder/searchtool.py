# -*- coding: utf-8 -*-
from tyc_finder.base import BasicFuncs


class SearchTool(object):

    @staticmethod
    def click_search_bar_old(driver, stype='company'):
        params = {'company': 'CompanySearch',
                  'boss': 'HumanSearch',
                  'relationship': 'RelationSearch'}
        parents = '//*[@id="web-content"]'
        class_name = '*'
        key_name = 'tyc-event-ch'
        special = "shouye.{Search}.Tab".format(Search=params[stype])

        key_value_dict = {key_name: special}

        BasicFuncs.locate_element(driver, parents, class_name, key_value_dict).click()

    @staticmethod
    def click_search_bar(driver, stype='company',
                         params={'company': 'CompanySearch',
                                 'boss': 'HumanSearch',
                                 'relationship': 'RelationSearch'}):
        """

        :param driver:
        :param stype:
        :param params:
        :return:
        """

        xpath = '//*[@id="web-content"]//*[@tyc-event-ch="shouye.{Search}.Tab"]'.format(Search=params[stype])

        driver.find_element_by_xpath(xpath).click()

    @staticmethod
    def enter_input(driver, msg):
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format('请输入公司名称、老板姓名、品牌名称等'))[-1].send_keys(msg)

    @staticmethod
    def submit_and_search(driver,
                          parents='',
                          class_name='div',
                          stype='company',
                          params=None):
        if params is None:
            params = {'company': 'CompanySearch',
                      'boss': 'HumanSearch',
                      'relationship': 'RelationSearch'}
        search_type = params[stype]
        key_value_dict = {'class': "input-group-btn btn -xl", 'tyc-event-ch': f"shouye.{search_type}.Search"}
        BasicFuncs.locate_element(driver, parents, class_name, key_value_dict)[-1].click()
        # driver.find_elements_by_xpath(f"""{parents}//{class_name}[@{key_name}='{special}']""")[-1].click()

    @classmethod
    def _search(cls, driver, msg, stype='company'):
        print(f'select search type: {stype}')
        cls.click_search_bar(driver, stype=stype)
        print(f'enter msg: {msg}')
        cls.enter_input(driver, msg)
        cls.submit_and_search(driver)
