# -*- coding: utf-8 -*-

from tyc_finder.spider_body import SpiderSession, Spider
from tyc_finder.base import BasicFuncs
from tyc_finder.searchtool import SearchTool
from tyc_finder.login import TycLogin
from bs4 import BeautifulSoup
from lxml.etree import HTML, _Comment
from tyc_finder.cookies.cookies import CookieParser


class ParseSinglePage(object):
    @staticmethod
    def obtain_driver(driver):
        return driver

    @staticmethod
    def test_url():
        url = "https://www.tianyancha.com/company/68521782"
        return url

    @staticmethod
    def _temp_driver(
            chromedriver_mac_path='/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac'):
        # url = "https://www.tianyancha.com/company/68521782"

        driver = Spider(chromedriver_mac_path, headless=False).driver
        return driver
        # driver.get(url)

    @staticmethod
    def test():
        url = ParseSinglePage.test_url()
        driver = ParseSinglePage._temp_driver()
        driver.get(url)

        CookieParser.load_refresh_cookies(driver, cookies_file='cookies.json', public='cookies/', refresh=False)

        page_source = driver.page_source.encode('utf-8')
        soup1 = HTML(page_source)
        base = """//*[@id="web-content"]//div[@class="company-warp -public"]"""
        holder = soup1.xpath(base + '/*')
        print(len(holder))
        same_path = base + """/div[@class='{}'"""

        l0 = holder[0]  # same_path.format("company-tabwarp -abs")
        basic_info = l1 = holder[1]  # same_path.format("tabline") # basic info
        tyc_risk = l2 = holder[2]  # same_path.format("tabline")

        l3 = holder[3]  # same_path.format("tabline")
        detail_info = l4 = holder[4]  # same_path.format("container")
        print(1)


class BasicInfoParser(object):
    # TODO: 改善Base_info稳健性
    @staticmethod
    def get_base_info(basic_info):
        hold = basic_info.xpath("""//div[@class='box -company-box ']/*""")
        if len(hold) == 3:
            logo, content, triangle_xcx = hold
            logo_img = logo.find_elements_by_xpath("""/*""")

        base_table = {}

        # TODO:抽象化：频繁变换点
        def parse_content(content):
            company_name = content.find_element_by_xpath("//div[@class='header']/h1[@class='name']").text
            return company_name

        def base_info_tag_list_content():
            # < !--开业状态 -->
            pass

        def base_info_detail(content):
            base_info2 = content.xpath("""//div[@class='detail ']""")[0]

            def getchildren_without_comment(f00):
                return [child for child in f00.getchildren() if not isinstance(child, _Comment)]

            def parse_small(a):
                a_span = a.xpath("span[@class='label']")[0]
                if '地址' in a_span.text:
                    address = a_span.getparent().xpath("//*[@id='company_base_info_address']/text()")[0].strip()
                    return a_span.text.rstrip('：')[:2], address
                else:

                    return a_span.text.rstrip('：')[:2], a_span.getnext().text

            f00, f01, summary, claim_opt = getchildren_without_comment(base_info2)
            # f00, f01, summary, claim_opt = [child for child in base_info2.getchildren() if
            #                                 not isinstance(child, _Comment)]
            # a, b = getchildren_without_comment(f00)
            # hs = {}

            r = dict([parse_small(x) for s in [f00, f01] for x in getchildren_without_comment(s)])
            ss = summary.xpath("div/div/span[@class='label']")[0]
            r[ss.text.rstrip('：')[:2]] = ss.tail

            """//*[@id="company_web_top"]/div[2]/div[2]/div[3]/div[3]/div/div/text()"""

            return r

            # a, b = [child for child in f00.getchildren() if not isinstance(child, _Comment)]

            ## 爬取数据不完整,要支持展开和多项合并
            # base_table['电话'] = base_info2.text.split('电话：')[1].split('邮箱：')[0].split('查看')[0]
            # base_table['邮箱'] = base_info2.text.split('邮箱：')[1].split('\n')[0].split('查看')[0]
            # base_table['网址'] = base_info2.text.split('网址：')[1].split('地址')[0]
            # base_table['地址'] = base_info2.text.split('地址：')[1].split('\n')[0]


        def base_info_card(content):
            pass

        # try:
        #     abstract = driver.find_element_by_xpath("//div[@class='summary']/script")  # @class='sec-c2 over-hide'
        #     base_table['简介'] = driver.execute_script("return arguments[0].textContent", abstract).strip()
        # except:
        #     abstract = driver.find_element_by_xpath("//div[@class='summary']")
        #     base_table['简介'] = driver.execute_script("return arguments[0].textContent", abstract).strip()[3:]
        #
        # # 处理工商信息的两个tables
        # tabs = driver.find_elements_by_xpath("//div[@id='_container_baseInfo']/table")
        #
        # # 处理第一个table
        # rows1 = tabs[0].find_elements_by_tag_name('tr')
        # if len(rows1[1].find_elements_by_tag_name('td')[0].text.split('\n')[0]) < 2:
        #     base_table['法人代表'] = rows1[1].find_elements_by_tag_name('td')[0].text.split('\n')[1]
        # else:
        #     base_table['法人代表'] = rows1[1].find_elements_by_tag_name('td')[0].text.split('\n')[0]
        #
        # # 处理第二个table
        # rows2 = tabs[1].find_elements_by_tag_name('tr')
        #
        # # 使用循环批量爬取base_table_2
        # base_table_2 = pd.DataFrame(columns=['Row_Index', 'Row_Content'])
        #
        # for rows2_row in range(len(rows2)):
        #     for element_unit in rows2[rows2_row].find_elements_by_tag_name('td'):
        #         if element_unit.text != '':
        #             base_table_2 = base_table_2.append({'Row_Index': rows2_row, 'Row_Content': element_unit.text},
        #                                                ignore_index=True)
        #
        # if len(base_table_2) % 2 == 0:
        #     for i in range(int(len(base_table_2) / 2)):
        #         base_table[base_table_2.iloc[2 * i, 1]] = base_table_2.iloc[
        #             2 * i + 1, 1]  # 将base_table_2的数据装回base_table
        # else:
        #     print('base_table_2（公司基本信表2）行数不为偶数，请检查代码！')
        #
        # return pd.DataFrame([base_table])

        # pass


if __name__ == '__main__':
    ParseSinglePage.test()

    print(1)
    pass
