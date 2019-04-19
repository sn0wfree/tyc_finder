# -*- coding: utf-8 -*-
import time, gevent
import re
import pandas as pd
from bs4 import BeautifulSoup

from collections import OrderedDict


class BasicFuncs(object):

    @staticmethod
    def locate_element(driver, parents='',
                       class_name='div',
                       key_value_dict={'onclick': "header.search(true,'#home-main-search')"}):
        conditions = [f"[@{key}='{value}']" for key, value in key_value_dict.items()]

        conditions_str = ''.join(conditions)

        xpath = f"""{parents}//{class_name}{conditions_str}"""
        print(xpath)

        return driver.find_elements_by_xpath(xpath)
