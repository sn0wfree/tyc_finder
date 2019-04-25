# -*- coding: utf-8 -*-
import time
from tyc_finder.spider_body import SpiderSession, Spider
from tyc_finder.base import BasicFuncs
from tyc_finder.searchtool import SearchTool
from tyc_finder.login import TycLogin
from bs4 import BeautifulSoup
from lxml.etree import HTML, _Comment
from tyc_finder.cookies.cookies import CookieParser
import pandas as pd

from tyc_finder.mi import other_scraper, Tianyancha


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


class ParseCompanyBackGroundInfo(object):
    @staticmethod
    def test123(trs):
        for tr in trs:
            for t in tr.xpath("""td"""):
                if t.getchildren():  # if not []
                    tag = t.getchildren()[0].tag
                    if tag == 'img':
                        yield t.getchildren()[0].attrib
                    else:
                        yield t.getchildren()[0].text
                else:
                    yield t.text

    @staticmethod
    def parse_table(tr):
        for t in tr.xpath("""td"""):
            t_getchildren = t.getchildren()
            if t_getchildren:  # if not []
                tag = t_getchildren[0].tag
                if tag == 'img':
                    yield dict(t_getchildren[0].attrib)
                else:
                    yield t_getchildren[0].text
            else:
                yield t.text

    @staticmethod
    def special_parse_table(tr):
        name, info = tr.getchildren()
        name_text = name.text
        if name_text == '注册地址':
            return [name_text, info.text]
        else:
            return [name_text, info.xpath("""*//text()""")]

    @classmethod
    def get_detail_info(cls, table2, special_list=["注册地址", "经营范围"]):

        hold = {}
        for row, tr in enumerate(table2.xpath("""tbody/tr""")):
            reuslt = list(cls.parse_table(tr))
            if reuslt[0] in special_list:
                hold[row] = cls.special_parse_table(tr)
            else:
                hold[row] = reuslt
        return hold

    @staticmethod
    def get_legal_representative(table1_lr):
        """

        company_count: 198
        name_dict : {'class': 'link-click', 'target': '_blank', 'title': '黄明端', 'href': 'https://www.tianyancha.com/human/2298666790-c68521782', 'onclick': 'common.stopPropagation(event)'}

        :param table1_lr:
        :return: name_dict,company_count
        """

        name_, company = table1_lr.xpath("""tbody/tr/td[1]//div[@class='humancompany']/div""")
        name_dict = dict(name_.xpath("""a""")[0].attrib)
        company_count = company.xpath("""span/text()""")[0]
        name_dict['own_company_count'] = company_count
        return name_dict

    @classmethod
    def parse_back_ground_info(cls, table1_lr, table2):
        name_dict = cls.get_legal_representative(table1_lr)
        detail_background_info = cls.get_detail_info(table2)
        return dict(name_dict=name_dict, detail_background_info=detail_background_info)

    pass


class GetContainer(object):
    @staticmethod
    def get_container_left_tabline(container):
        """
        parse container
        :param container:
        :return:
        """
        header, detail_list = \
            container.xpath("""//div[@class='container-left tabline']/div[@class='box-container -main']""")[
                0].getchildren()

        return header, detail_list

    @classmethod
    def get_back_ground_info(cls, back_ground_info):

        ele = back_ground_info.xpath("""*""")[1]

        # data_header, data_content = GetBaseInfoDetail._getchildren_without_comment(ele)

        back_ground_info_dict = GetContainer._parser_nae_main_sector_info_router(ele)
        return back_ground_info_dict

    @staticmethod
    def _parse_nav_main_baseInfo(data_header, data_content):

        data_title = data_header.xpath("""span[@class='data-title']/text()""")[0]
        industry_commerce_snapshot = dict(data_header.xpath("""span[@class='tips-block-data']/a""")[0].attrib)

        table1, table2 = GetBaseInfoDetail._getchildren_without_comment(data_content)

        back_ground_info_dict = ParseCompanyBackGroundInfo.parse_back_ground_info(table1, table2)
        back_ground_info_dict[data_title] = industry_commerce_snapshot
        return back_ground_info_dict

        pass

    @classmethod
    def _parser_nae_main_sector_info_router(cls, ele, conditions=['nav-main-baseInfo']):

        conditions_all = ['nav-main-baseInfo',
                          'nav-main-riskInfo',  # nav-main-riskInfo  <!--天眼风险-->
                          'nav-main-graphTreeInfo',  # nav-main-graphTreeInfo <!--股权穿透图-->
                          'nav-main-staffCount',  # nav-main-staffCount <!--[高管信息]-->
                          'nav-main-holderCount',  # nav-main-holderCount <!--[股东信息]-->
                          'nav-main-inverstCount',  # nav-main-inverstCount <!--[对外投资]-->
                          'nav-main-shouyirenCount',  # nav-main-shouyirenCount  <!-- [最终受益人]-->
                          'nav-main-realHoldingCount',  # nav-main-realHoldingCount 实际控制权
                          'nav-main-graphInfo',  # nav-main-graphInfo <!-- graph 企业关系 -->
                          'nav-main-changeCount',  # nav-main-changeCount  <!--变更信息oocss-->
                          'nav-main-graphTimeInfo',  # nav-main-graphTimeInfo  <!-- graph 历史沿革 -->
                          'nav-main-reportCount',  # nav-main-reportCount <!--企业年报OOCSS-->
                          'nav-main-branchCount'  # nav-main-branchCount <!--[分支机构]-->
                          ]

        data_header, data_content = GetBaseInfoDetail._getchildren_without_comment(ele)

        if 'id' in ele.attrib.keys():
            nav_main_sector_name = ele.attrib['id']

        elif 'id' in data_header.attrib.keys():
            nav_main_sector_name = data_header.attrib['id']

        else:
            raise ValueError('cannot find id label! ')

        if nav_main_sector_name in conditions:
            ## TODO to parse more
            return getattr(cls, '_parse_{}'.format(nav_main_sector_name.replace('-', '_')))(data_header, data_content)
        else:
            return "[Error] {} is not supported yet!".format(nav_main_sector_name)

        pass

    @classmethod
    def get_basic_info_1(cls, element):
        for ele in element.xpath("""*"""):
            """
            <class 'list'>: [
            <Element div at 0x10de2ab48>, <!-- 基本信息 -->
            <Element div at 0x10de2ae08>, <!--天眼风险-->
            <Element div at 0x10de2af08>, <!--股权穿透图--> {'class': 'block-data', 'tyc-event-click': '', 'tyc-event-ch': 'CompangyDetail.guquanchuantou'}
            <Element div at 0x10d8edc08>, <!--[高管信息]-->
            <Element div at 0x10d8ed608>, <!--[股东信息]-->
            ... maybe have other sectors
            <Element div at 0x10db654c8>, <!-- [最终受益人]-->
            <Element div at 0x10db65548>, <!--[实际控制权]-->
            <Element div at 0x10dbbef08>, <!-- graph 企业关系 -->
            <Element div at 0x10dbbec48>, <!--变更信息oocss-->
            <Element div at 0x10db65248>, <!-- graph 历史沿革 -->
            <Element div at 0x10dd7c1c8>, <!--企业年报OOCSS-->
            <Element div at 0x10dd7cb48>, <!--[分支机构]-->
            
            <Element div at 0x10dd7c4c8>]
            """
            if ele.attrib['class'] == 'block-data':
                yield cls._parser_nae_main_sector_info_router(ele)



            # table1, table2 = cls._parse_tables(ele)
            # table1 : header
            # table2 : data-content
            # yield table1, table2
            else:
                pass

        pass

    @staticmethod
    def get_table_info(table):
        tab = table.find_element_by_tag_name('table')
        df = pd.read_html('<table>' + tab.get_attribute('innerHTML') + '</table>')
        if isinstance(df, list):
            df = df[0]
        if '操作' in df.columns:
            df = df.drop(columns='操作')
        # TODO：加入更多标准的表格处理条件
        return df

    @classmethod
    def get_detail_list(cls, detail_list):

        unspported_list = ['nav-main-manageDangerous', 'nav-main-develope', 'nav-main-manageStatus', 'nav-main-past']

        for row, element in enumerate(detail_list.xpath("""//div[@class='block-data-group']""")):
            # yield element
            element_attrib_keys = list(element.attrib.keys())
            length = len(element_attrib_keys)
            # basic
            if length == 1 and 'id' not in element_attrib_keys and 'tyc-event-ch' not in element_attrib_keys and 'class' in element_attrib_keys:
                # basic
                yield list(cls.get_basic_info_1(element))
                pass
            elif 'id' in element_attrib_keys:
                # 司法风险
                if element.attrib['id'] == 'nav-main-lawDangerous':

                    "block-data table-col-warp"
                    '开庭公告', """[@tyc-event-ch='CompangyDetail.kaitinggonggao']"""
                    kaitinggonggao = element.xpath("""*[@tyc-event-ch='CompangyDetail.kaitinggonggao']""")[0]

                    data_header, data_content = GetBaseInfoDetail._getchildren_without_comment(kaitinggonggao)
                    # 开庭公告
                    announcementCount = data_header.xpath("""span[@class='data-count -warn']""")[0].text

                    # =data_content.xpath("""*""")

                    table_xpath = """//*[@id="_container_announcementcourt"]/table"""

                    thead = data_content.xpath("""//*[@id="_container_announcementcourt"]/table/thead""")[0]

                    header = thead.xpath("""tr/th/text()""")

                    tr0 = data_content.xpath("""//*[@id="_container_announcementcourt"]/table/tbody/tr""")[0]

                    """//*[@id="_container_announcementcourt"]/div/ul"""
                    """//*[@id="_container_announcementcourt"]/div/ul/li"""

                    # last_page = driver.find_elements_by_xpath("""//*[@id="_container_announcementcourt"]/div/ul/li""")[
                    #     -1].find_elements_by_xpath("""a""")[0].get_attribute('class')
                    while 1:
                        last_page = \
                            driver.find_elements_by_xpath("""//*[@id="_container_announcementcourt"]/div/ul/li""")[
                                -1].find_elements_by_xpath("""a""")[0].get_attribute('class')
                        if last_page == 'num -current':
                            break

                        else:

                            # parse_table()

                            driver.find_elements_by_xpath("""//*[@id="_container_announcementcourt"]/div/ul/li""")[
                                -1].click()

                    # {'class': 'block-data-group', 'id': 'nav-main-lawDangerous'}
                    pass

                elif element.attrib['id'] == 'nav-main-knowledgeProperty':

                    # knowledgeProperty = detail_list.xpath("""//div[@class='block-data-group']""")[5]
                    # {'class': 'block-data-group', 'id': 'nav-main-knowledgeProperty'}
                    pass

                elif element.attrib['id'] in unspported_list:  # == 'nav-main-manageDangerous':

                    yield "[error] {} is not supported yet!".format(element.attrib['id'])

                    # {'class': 'block-data-group', 'id': 'nav-main-manageDangerous'}

                # elif element.attrib['id'] == 'nav-main-develope':
                #     # {'class': 'block-data-group', 'id': 'nav-main-develope'}
                #     pass
                # elif element.attrib['id'] == 'nav-main-manageStatus':
                #     # {'class': 'block-data-group', 'id': 'nav-main-manageStatus'}
                #     pass

                # elif element.attrib['id'] == 'nav-main-past':
                #     # {'class': 'block-data-group', 'id': 'nav-main-past'}
                #     pass
                else:
                    pass
            elif 'id' not in element_attrib_keys and 'tyc-event-ch' in element_attrib_keys:
                pass
                # {'class': 'block-data-group', 'tyc-event-click': '', 'tyc-event-ch': 'CompanyDetail.Wenda'}
            else:
                pass

    # <!--上市信息-->
    @staticmethod
    def info_dict(element):
        ids = ['nav-main-lawDangerous', 'nav-main-manageDangerous', 'nav-main-develope',
               'nav-main-manageStatus', 'nav-main-knowledgeProperty', 'nav-main-past']
        var = [{'class': 'block-data-group', 'id': 'nav-main-lawDangerous'},
               {'class': 'block-data-group', 'id': 'nav-main-manageDangerous'},
               {'class': 'block-data-group', 'id': 'nav-main-develope'},
               {'class': 'block-data-group', 'id': 'nav-main-manageStatus'},
               {'class': 'block-data-group', 'id': 'nav-main-knowledgeProperty'},
               {'class': 'block-data-group', 'id': 'nav-main-past'},
               {'class': 'block-data-group', 'tyc-event-click': '', 'tyc-event-ch': 'CompanyDetail.Wenda'}]


class GetBaseInfoDetail(object):

    @staticmethod
    def _parse_small(a):
        a_span = a.xpath("span[@class='label']")[0]
        if '地址' in a_span.text:
            address = a_span.getparent().xpath("//*[@id='company_base_info_address']/text()")[0].strip()
            return a_span.text.rstrip('：')[:2], address
        else:
            return a_span.text.rstrip('：')[:2], a_span.getnext().text

    @staticmethod
    def _getchildren_without_comment(f00):
        return [child for child in f00.getchildren() if not isinstance(child, _Comment)]

    @classmethod
    def base_info_detail(cls, content):
        """
        <class 'dict'>: {'电话': '021-26108008', '邮箱': 'fw03@mail.rt-mart.com.cn', '网址': 'www.rt-mart.com.cn', '地址': '上海市共和新路3318号', '简介': '康成投资（中国）有限公司于2005年3月23日在上海市工商局登记成立。法定代表人黄明端，公司经营范围包括一、在国家允许外商投资的领域依法进行投资等。'}

        :param content:
        :return:
        """
        base_info2 = content.xpath("""//div[@class='detail ']""")[0]

        f00, f01, summary, claim_opt = cls._getchildren_without_comment(base_info2)
        # f00, f01, summary, claim_opt = [child for child in base_info2.getchildren() if
        #                                 not isinstance(child, _Comment)]
        # a, b = getchildren_without_comment(f00)
        # hs = {}

        r = dict([cls._parse_small(x) for s in [f00, f01] for x in cls._getchildren_without_comment(s)])
        ss = summary.xpath("div/div/span[@class='label']")[0]
        r[ss.text.rstrip('：')[:2]] = ss.tail

        """//*[@id="company_web_top"]/div[2]/div[2]/div[3]/div[3]/div/div/text()"""

        return r


class GetCompanyName(object):
    # TODO:抽象化：频繁变换点
    @staticmethod
    def _parse_company_name(content):
        company_name = content.find_element_by_xpath("//div[@class='header']/h1[@class='name']").text
        return company_name


class BasicInfoParser(object):
    # TODO: 改善Base_info稳健性

    @staticmethod
    def get_base_info(basic_info):
        hold = basic_info.xpath("""//div[@class='box -company-box ']/*""")
        if len(hold) == 3:
            logo, content, triangle_xcx = hold
            return logo, content, triangle_xcx
        else:
            raise ValueError('Basic Information cannot be parsed normally !')

    @staticmethod
    def get_simple_info(content):
        """
        <class 'dict'>: {'电话': '021-26108008', '邮箱': 'fw03@mail.rt-mart.com.cn', '网址': 'www.rt-mart.com.cn', '地址': '上海市共和新路3318号', '简介': '康成投资（中国）有限公司于2005年3月23日在上海市工商局登记成立。法定代表人黄明端，公司经营范围包括一、在国家允许外商投资的领域依法进行投资等。'}


        :param content:
        :return:
        """
        return GetBaseInfoDetail.base_info_detail(content)

    @staticmethod
    def get_logo(logo):
        """
        return logo info and data src
        :param logo:
        :return:
        """

        logo_img = logo.xpath("""div[1]/*/img[@class='img']""")[0]

        visitor_count = logo.xpath("""div[@class='visitor-content']/*//span[@class='pv-txt']/text()""")[0]
        logo_dict = dict(logo_img.attrib)
        logo_dict['visitor_count'] = visitor_count
        return logo_dict

    @staticmethod
    def base_info_tag_list_content():
        # < !--开业状态 -->
        pass

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

        pass


class Test(object):
    @staticmethod
    def split_five_parts(html_source_code, base="""//*[@id="web-content"]//div[@class="company-warp -public"]"""):
        holder = html_source_code.xpath(base + '/*')
        # print(len(holder))
        same_path = base + """/div[@class='{}'"""

        l0 = holder[0]  # same_path.format("company-tabwarp -abs")
        basic_info = l1 = holder[1]  # same_path.format("tabline") # basic info
        tyc_risk = l2 = holder[2]  # same_path.format("tabline")

        l3 = holder[3]  # same_path.format("tabline")
        container = l4 = holder[4]  # same_path.format("container")
        # print(1)
        return l0, basic_info, tyc_risk, l3, container

    @classmethod
    def test(cls, keyword, url=None):
        url = ParseSinglePage.test_url() if url is None else url
        driver = ParseSinglePage._temp_driver()

        driver.get(url)
        time.sleep(1)
        CookieParser.load_refresh_cookies(driver, cookies_file='cookies.json', public='cookies/', refresh=False)

        url_search = 'http://www.tianyancha.com/search?key=%s&checkFrom=searchBox' % keyword
        driver.get(url)

        table_dict = Tianyancha.tianyancha_scraper(driver, keyword)
        return table_dict

    @classmethod
    def main_path(cls, url=None, public='cookies/', ):
        url = ParseSinglePage.test_url() if url is None else url
        driver = ParseSinglePage._temp_driver()

        driver.get(url)
        time.sleep(1)
        CookieParser.load_refresh_cookies(driver, cookies_file='cookies.json', public=public, refresh=False)
        driver.get(url)

        # load cookies

        # get source code
        page_source = driver.page_source.encode('utf-8')
        html_source_code = HTML(page_source)

        # holder = html_source_code.xpath(base + '/*')
        # # print(len(holder))
        # same_path = base + """/div[@class='{}'"""
        #
        # l0 = holder[0]  # same_path.format("company-tabwarp -abs")
        # basic_info = l1 = holder[1]  # same_path.format("tabline") # basic info
        # tyc_risk = l2 = holder[2]  # same_path.format("tabline")
        #
        # l3 = holder[3]  # same_path.format("tabline")
        # container = l4 = holder[4]  # same_path.format("container")
        # # print(1)
        l0, basic_info, tyc_risk, l3, container = cls.split_five_parts(html_source_code)

        return l0, basic_info, tyc_risk, l3, container, driver

    @staticmethod
    def parse_basic_info(basic_info):
        logo, content, triangle_xcx = BasicInfoParser.get_base_info(basic_info)

        # parse logo
        logo_dict = BasicInfoParser.get_logo(logo)

        # parse content
        simple_info = BasicInfoParser.get_simple_info(content)

        return logo_dict, simple_info

    @staticmethod
    def parse_container(container):
        header, detail_list = GetContainer.get_container_left_tabline(container)

        container_info_list = detail_list.xpath("""//div[@class='block-data-group']""")
        # detail_list.xpath("""//div[@class='block-data-group']""")

        back_ground_info = container_info_list[0]  # <!--上市信息-->

        back_ground_info_dict = GetContainer.get_back_ground_info(back_ground_info)
        # ele = back_ground_info.xpath("""*""")[1]
        #
        # data_header, data_content = GetBaseInfoDetail._getchildren_without_comment(ele)
        #
        # back_ground_info_dict = GetContainer._parser_nae_main_sector_info_router(ele)

        lawDangerous = container_info_list[1]  ##  <!--=========司法风险=============-->

        knowledgeProperty = container_info_list[5]  ## <!--=========知识产权=============-->

        # GetContainer.get_detail_list(detail_list)
        return back_ground_info_dict, lawDangerous, knowledgeProperty
        pass


class ParselawDangerous(object):
    @staticmethod
    def get_lawDangerous(lawDangerous):
        pass


class ParseTable(object):
    @staticmethod
    def get_tables(driver):
        tables = driver.find_elements_by_xpath("//div[contains(@id,'_container_')]")

        list_exception = ['recruit', 'tmInfo', 'holdingCompany', 'invest', 'bonus', 'firmProduct', 'jingpin',
                          'bid', 'taxcredit', 'certificate', 'patent', 'copyright', 'product',
                          'importAndExport',
                          'copyrightWorks', 'wechat', 'icp', 'announcementcourt', 'lawsuit', 'court',
                          'branch', 'touzi', 'judicialSale', 'bond', 'teamMember', 'check']

        # 获取每个表格的名字
        c = '_container_'
        name = [0] * (len(tables) - 2)
        # 生成一个独一无二的十六位参数作为公司标记，一个公司对应一个，需要插入多个数据表

        table_dict = {}
        for x in range(len(tables) - 2):
            name[x] = tables[x].get_attribute('id')
            name[x] = name[x].replace(c, '')  # 可以用这个名称去匹配数据库
        # print(name)
        # 判断是表格还是表单
        # TODO: Deprecated if being tested not useful anymore.
        # num = tables[x].find_elements_by_tag_name('table')

        # 排除列表：不同业务可以设置不同分类，实现信息的精准爬取
        # if name[x] in list_exception:
        #     pass
        #
        # # 基本信息表：baseInfo，table有两个
        # elif (name[x] == 'baseInfo') and (('baseInfo' in table) or (table == ['all'])):
        #     print('正在爬取' + 'baseInfo')
        #     try:
        #         table_dict[name[x]] = get_base_info(driver)
        #     except:
        #         print('baseInfo表格为特殊格式，使用了标准表格爬取函数。')
        #         table_dict[name[x]] = get_base_info(driver)
        #
        # # # 公司高管的特殊处理
        # # elif name[x] == 'staff':
        # #     table_dict[name[x]] = get_staff_info(driver)
        #
        # # 公告的特殊处理：加入URL
        # elif (name[x] == 'announcement') and (('announcement' in table) or (table == ['all'])):
        #     print('正在爬取' + 'announcement')
        #     try:
        #         table_dict[name[x]] = get_announcement_info(driver)
        #     except:
        #         print('announcement表格为特殊格式，使用了标准表格爬取函数。')
        #         table_dict[name[x]] = get_base_info(driver)
        #
        # # 单纯的表格进行信息爬取
        # # TODO: 含头像的行未对齐
        # elif ((name[x] in table) or (table == ['all'])):
        #     # 检查用
        #     print('正在爬取' + str(name[x]))
        #
        #     df = get_table_info(tables[x])
        #     onclickflag = tryonclick(tables[x])
        #     ontapflag = tryontap(tables[x])
        #     # 判断此表格是否有翻页功能
        #     if onclickflag == 1:
        #         df = change_page(tables[x], df, driver)
        #     #  if ontapflag == 1:
        #     #      df = change_tap(tables[x], df)
        #     table_dict[name[x]] = df
        #
        # else:
        #     pass


# 标准表格爬取函数
def get_table_info(table):
    tab = table.find_element_by_tag_name('table')
    df = pd.read_html('<table>' + tab.get_attribute('innerHTML') + '</table>')
    if isinstance(df, list):
        df = df[0]
    if '操作' in df.columns:
        df = df.drop(columns='操作')
    # TODO：加入更多标准的表格处理条件
    return df


def tryonclick(table):  # table实质上是selenium WebElement
    # 测试是否有翻页
    ## 把条件判断写进tryonclick中
    try:
        # 找到有翻页标记
        table.find_element_by_tag_name('ul')
        onclickflag = 1
    except Exception:
        print("没有翻页")  ## 声明表格名称: name[x] +
        onclickflag = 0
    return onclickflag


def tryontap(table):
    # 测试是否有翻页
    try:
        table.find_element_by_xpath("//div[contains(@class,'over-hide changeTabLine f14')]")
        ontapflag = 1
    except Exception as e:
        print(e)
        print("没有时间切换页")  ## 声明表格名称: name[x] +
        ontapflag = 0
    return ontapflag


change_page_interval = 10


def change_page(table, df, driver):
    # TODO:抽象化：频繁变换点
    # PageCount = table.find_element_by_class_name('company_pager').text #历史class_name（天眼查的反爬措施）：'total'
    # PageCount = re.sub("\D", "", PageCount)  # 使用正则表达式取字符串中的数字 ；\D表示非数字的意思
    PageCount = len(table.find_elements_by_xpath(".//ul[@class='pagination']/li")) - 1

    for _ in range(int(PageCount) - 1):
        # TODO:抽象化：频繁变换点
        button = table.find_element_by_xpath(
            ".//a[@class='num -next']")  # 历史class_name（天眼查的反爬措施）：'pagination-next  ',''
        driver.execute_script("arguments[0].click();", button)
        ####################################################################################
        time.sleep(change_page_interval)  # 更新换页时间间隔,以应对反爬虫
        ####################################################################################
        df2 = get_table_info(table)  ## 应该可以更换不同的get_XXXX_info
        df = df.append(df2)
    return df


def standard_table_extractor(name):
    # 检查用
    print('正在爬取' + str(name[x]))

    df = get_table_info(tables[x])
    onclickflag = tryonclick(tables[x])
    ontapflag = tryontap(tables[x])
    # 判断此表格是否有翻页功能
    if onclickflag == 1:
        df = change_page(tables[x], df, driver)
    #  if ontapflag == 1:
    #      df = change_tap(tables[x], df)
    table_dict[name[x]] = df


if __name__ == '__main__':
    l0, basic_info, tyc_risk, l3, container, driver = Test.main_path()
    logo_dict, simple_info = Test.parse_basic_info(basic_info)
    # header, detail_list = GetContainer.get_container_left_tabline(container)

    # knowledgeProperty = detail_list.xpath("""//div[@class='block-data-group']""")[5]  # knowledgeProperty
    # lawDangerous = detail_list.xpath("""//div[@class='block-data-group']""")[1]  # lawDangerous
    # element = detail_list.xpath("""//div[@class='block-data-group']""")[0]
    # ele = element.xpath("""*""")[1]
    #
    # data_header, data_content = GetBaseInfoDetail._getchildren_without_comment(ele)
    #
    # back_ground_info_dict = GetContainer._parser_nae_main_sector_info_router(ele)

    back_ground_info_dict, lawDangerous, knowledgeProperty = Test.parse_container(container)

    print(1)
    pass
