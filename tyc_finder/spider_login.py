# -*- coding: utf-8 -*-
import time, gevent
import re
import pandas as pd
from bs4 import BeautifulSoup

from collections import OrderedDict
from tyc_finder.tools.utils import WriterJson

from tyc_finder.spider_body import SpiderSession

username = '1'
password = '1'
account_info = dict(username=username, password=password)


class Tianyancha_login(object):

    def __init__(self, driver, login_url='https://www.tianyancha.com/login'):

        self.driver = driver
        self.login_url = login_url
        # self.username = username
        # self.password = password

    def get_url(self, url):
        self.driver.get(url)
        gevent.sleep(1)

    # 常量定义

    # def __init__(self, username, password, headless=False):
    #     self.username = username
    #     self.password = password
    #     self.headless = headless
    #     self.driver = self.login(text_login='请输入11位手机号码', text_password='请输入登录密码')

    def login_process(self, account_info, login_url='https://www.tianyancha.com/login'):
        time_start = time.time()
        # 操作行为提示
        print('the username and password will autofill, please do not move cursor or use keyboards !')
        # open login_url
        self.get_url(login_url)

        # self.driver WebDriverWait

    # 登录天眼查
    def login(self, executable_path, text_login, text_password):
        time_start = time.time()

        driver = SpiderSession.create_driver(executable_path, core='Chrome', headless=self.headless, adaptive=True)

        driver.get(self.url)

        # 模拟登陆：Selenium Locating Elements by Xpath
        time.sleep(1)

        # 关闭底栏
        driver.find_element_by_xpath("//img[@id='tyc_banner_close']").click()

        driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']").click()
        # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_login))[-2].send_keys(self.username)
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_password))[-1].send_keys(self.password)

        # 手工登录，完成滑块验证码
        print('请现在开始操作键盘鼠标，在15s内点击登录并手工完成滑块验证码。批量爬取只需一次登录。')
        time.sleep(10)
        print('还剩5秒。')
        time.sleep(5)

        time_end = time.time()
        print('您的本次登录共用时{}秒。'.format(int(time_end - time_start)))
        return driver

    # 定义天眼查爬虫
    def tianyancha_scraper(self,
                           keyword,
                           table='all',
                           use_default_exception=True,
                           change_page_interval=2,
                           export='xlsx',
                           quit_driver=True):
        """
        天眼查爬虫主程序。
        :param keyword: 公司名称，支持模糊或部分检索。比如"北京鸿智慧通实业有限公司"。
        :param table: 需要爬取的表格信息，默认为全部爬取。和官方的元素名称一致。常见的可以是'baseInfo', 'staff', 'invest'等，具体请参考表格名称中英文对照表。
        :param use_default_exception: 是否使用默认的排除列表，以忽略低价值表格为代价来加快爬取速度。
        :param change_page_interval: 爬取多页的时间间隔，默认2秒。避免频率过快IP地址被官方封禁。
        :param export: 输出保存格式，默认为Excel的`xlsx`格式，也支持`json`。
        :return:
        """

        # 公司搜索：顺带的名称检查功能，利用天眼查的模糊搜索能力
        # TODO：将借用模糊搜索的思路写进宣传文章。
        def search_company(driver, url1):
            driver.get(url1)
            time.sleep(1)
            content = driver.page_source.encode('utf-8')
            soup1 = BeautifulSoup(content, 'lxml')
            # TODO：是否要将登录状态监测统一到login函数中
            try:
                # TODO：'中信证券股份有限公司'无法正确检索
                try:
                    url2 = soup1.find('div', class_='header').find('a', class_="name ").attrs['href']
                except:
                    url2 = driver.find_element_by_xpath(
                        "//div[@class='content']/div[@class='header']/a[@class='name ']").get_attribute('href')
                print('登陆成功。')
            except:
                print('登陆过于频繁，请1分钟后再次尝试。')

            # TODO: 如果搜索有误，手工定义URL2地址。有无改善方案？
            driver.get(url2)
            return driver

        # TODO: 改善Base_info稳健性
        def get_base_info(driver):
            base_table = {}
            # TODO:抽象化：频繁变换点
            base_table['名称'] = driver.find_element_by_xpath("//div[@class='header']/h1").text
            base_info = driver.find_element_by_class_name('detail')

            ## 爬取数据不完整,要支持展开和多项合并
            base_table['电话'] = base_info.text.split('电话：')[1].split('邮箱：')[0].split('查看')[0]
            base_table['邮箱'] = base_info.text.split('邮箱：')[1].split('\n')[0].split('查看')[0]
            base_table['网址'] = base_info.text.split('网址：')[1].split('地址')[0]
            base_table['地址'] = base_info.text.split('地址：')[1].split('\n')[0]

            try:
                abstract = driver.find_element_by_xpath("//div[@class='summary']/script")  # @class='sec-c2 over-hide'
                base_table['简介'] = driver.execute_script("return arguments[0].textContent", abstract).strip()
            except:
                abstract = driver.find_element_by_xpath("//div[@class='summary']")
                base_table['简介'] = driver.execute_script("return arguments[0].textContent", abstract).strip()[3:]

            # 处理工商信息的两个tables
            tabs = driver.find_elements_by_xpath("//div[@id='_container_baseInfo']/table")

            # 处理第一个table
            rows1 = tabs[0].find_elements_by_tag_name('tr')
            if len(rows1[1].find_elements_by_tag_name('td')[0].text.split('\n')[0]) < 2:
                base_table['法人代表'] = rows1[1].find_elements_by_tag_name('td')[0].text.split('\n')[1]
            else:
                base_table['法人代表'] = rows1[1].find_elements_by_tag_name('td')[0].text.split('\n')[0]

            # 处理第二个table
            rows2 = tabs[1].find_elements_by_tag_name('tr')

            # 使用循环批量爬取base_table_2
            base_table_2 = pd.DataFrame(columns=['Row_Index', 'Row_Content'])

            for rows2_row in range(len(rows2)):
                for element_unit in rows2[rows2_row].find_elements_by_tag_name('td'):
                    if element_unit.text != '':
                        base_table_2 = base_table_2.append({'Row_Index': rows2_row, 'Row_Content': element_unit.text},
                                                           ignore_index=True)

            if len(base_table_2) % 2 == 0:
                for i in range(int(len(base_table_2) / 2)):
                    base_table[base_table_2.iloc[2 * i, 1]] = base_table_2.iloc[
                        2 * i + 1, 1]  # 将base_table_2的数据装回base_table
            else:
                print('base_table_2（公司基本信表2）行数不为偶数，请检查代码！')

            return pd.DataFrame([base_table])

        # 特殊处理：主要人员
        # TODO: staff_info定位不准？
        def get_staff_info(driver):
            staff_list = []
            staff_info = driver.find_elements_by_xpath(
                "//div[@class='in-block f14 new-c5 pt9 pl10 overflow-width vertival-middle new-border-right']")
            for i in range(len(staff_info)):
                position = driver.find_elements_by_xpath(
                    "//div[@class='in-block f14 new-c5 pt9 pl10 overflow-width vertival-middle new-border-right']")[
                    i].text
                person = \
                    driver.find_elements_by_xpath("//a[@class='overflow-width in-block vertival-middle pl15 mb4']")[
                        i].text
                staff_list.append({'职位': position, '人员名称': person})
            staff_table = pd.DataFrame(staff_list, columns=['职位', '人员名称'])
            return staff_table

        # 特殊处理:上市公告
        # TODO:加入类别搜索功能
        def get_announcement_info(driver):
            announcement_df = pd.DataFrame(columns=['序号', '日期', '上市公告', '上市公告网页链接'])  ## 子函数自动获取columns
            # TODO:可抽象，函数化
            content = driver.page_source.encode('utf-8')
            # TODO：能不能只Encode局部的driver
            soup = BeautifulSoup(content, 'lxml')
            announcement_info = soup.find('div', id='_container_announcement').find('tbody').find_all('tr')
            for i in range(len(announcement_info)):
                index = announcement_info[i].find_all('td')[0].get_text()
                date = announcement_info[i].find_all('td')[1].get_text()
                announcement = announcement_info[i].find_all('td')[2].get_text()
                announcement_url = 'https://www.tianyancha.com' + announcement_info[i].find_all('td')[2].find('a')[
                    'href']
                announcement_df = announcement_df.append(
                    {'序号': index, '日期': date, '上市公告': announcement, '上市公告网页链接': announcement_url}, ignore_index=True)

            ### 判断此表格是否有翻页功能:重新封装change_page函数
            announcement_table = driver.find_element_by_xpath("//div[contains(@id,'_container_announcement')]")
            onclickflag = tryonclick(announcement_table)
            if onclickflag == 1:
                PageCount = announcement_table.find_element_by_class_name('company_pager').text
                PageCount = re.sub("\D", "", PageCount)  # 使用正则表达式取字符串中的数字 ；\D表示非数字的意思
                for i in range(int(PageCount) - 1):
                    button = table.find_element_by_xpath(
                        ".//a[@class='num -next']")  # 历史class_name（天眼查的反爬措施）：'pagination-next  ',''
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(change_page_interval)
                    # TODO：函数化
                    content = driver.page_source.encode('utf-8')
                    # TODO：能不能只Encode局部的driver
                    soup = BeautifulSoup(content, 'lxml')
                    announcement_info = soup.find('div', id='_container_announcement').find('tbody').find_all('tr')
                    for i in range(len(announcement_info)):
                        index = announcement_info[i].find_all('td')[0].get_text()
                        date = announcement_info[i].find_all('td')[1].get_text()
                        announcement = announcement_info[i].find_all('td')[2].get_text()
                        announcement_url = 'https://www.tianyancha.com' + \
                                           announcement_info[i].find_all('td')[2].find('a')['href']
                        announcement_df = announcement_df.append(
                            {'序号': index, '日期': date, '上市公告': announcement, '上市公告网页链接': announcement_url},
                            ignore_index=True)
            return announcement_df

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
            except:
                print("没有时间切换页")  ## 声明表格名称: name[x] +
                ontapflag = 0
            return ontapflag

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

        # TODO：完善change_tap函数。
        def change_tap(table, df):
            TapCount = len(table.find_elements_by_tag_name('div'))
            for i in range(int(TapCount) - 3):
                button = table.find_elements_by_tag_name('div')[i + 3]
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                df2 = get_table_info(table)  ## 应该可以更换不同的get_XXXX_info
                # df2['日期'] = table.find_elements_by_tag_name('div')[i+3].text
                df = df.append(df2, ignore_index=True)
            # df = df.drop(columns=['序号'])
            return df

        def scrapy(driver, table, use_default_exception, quit_driver=quit_driver):
            # 强制确认table类型为list：当只爬取一个元素的时候很可能用户会只传入表明str
            if isinstance(table, str):
                list_table = []
                list_table.append(table)
                table = list_table

            # 定义排除列表
            # TODO:允许用户自主选择保留项目;帮助检查没有重复项
            if use_default_exception:
                list_exception = ['recruit', 'tmInfo', 'holdingCompany', 'invest', 'bonus', 'firmProduct', 'jingpin', \
                                  'bid', 'taxcredit', 'certificate', 'patent', 'copyright', 'product',
                                  'importAndExport', \
                                  'copyrightWorks', 'wechat', 'icp', 'announcementcourt', 'lawsuit', 'court', \
                                  'branch', 'touzi', 'judicialSale', 'bond', 'teamMember', 'check']
                # 两个List取差异部分，只排除不在爬取范围内的名单。参考：https://stackoverflow.com/questions/1319338/combining-two-lists-and-removing-duplicates-without-removing-duplicates-in-orig/1319353#1319353
                list_exception = list(set(list_exception) - set(table))
            else:
                list_exception = []

            # Waiting time for volatilityNum to load
            time.sleep(2)
            tables = driver.find_elements_by_xpath("//div[contains(@id,'_container_')]")

            # 获取每个表格的名字
            c = '_container_'
            name = [0] * (len(tables) - 2)
            # 生成一个独一无二的十六位参数作为公司标记，一个公司对应一个，需要插入多个数据表
            id = keyword
            table_dict = {}
            for x in range(len(tables) - 2):
                name[x] = tables[x].get_attribute('id')
                name[x] = name[x].replace(c, '')  # 可以用这个名称去匹配数据库
                # 判断是表格还是表单
                # TODO: Deprecated if being tested not useful anymore.
                # num = tables[x].find_elements_by_tag_name('table')

                # 排除列表：不同业务可以设置不同分类，实现信息的精准爬取
                if name[x] in list_exception:
                    pass

                # 基本信息表：baseInfo，table有两个
                elif (name[x] == 'baseInfo') and (('baseInfo' in table) or (table == ['all'])):
                    print('正在爬取' + 'baseInfo')
                    try:
                        table_dict[name[x]] = get_base_info(driver)
                    except:
                        print('baseInfo表格为特殊格式，使用了标准表格爬取函数。')
                        table_dict[name[x]] = get_base_info(driver)

                # # 公司高管的特殊处理
                # elif name[x] == 'staff':
                #     table_dict[name[x]] = get_staff_info(driver)

                # 公告的特殊处理：加入URL
                elif (name[x] == 'announcement') and (('announcement' in table) or (table == ['all'])):
                    print('正在爬取' + 'announcement')
                    try:
                        table_dict[name[x]] = get_announcement_info(driver)
                    except:
                        print('announcement表格为特殊格式，使用了标准表格爬取函数。')
                        table_dict[name[x]] = get_base_info(driver)

                # 单纯的表格进行信息爬取
                # TODO: 含头像的行未对齐
                elif ((name[x] in table) or (table == ['all'])):
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

                else:
                    pass

            # 退出浏览器
            if quit_driver:
                driver.quit()

            return table_dict

        def gen_excel(table_dict, keyword):
            with pd.ExcelWriter(keyword + '.xlsx') as writer:
                for sheet_name in table_dict:
                    table_dict[sheet_name].to_excel(writer, sheet_name=sheet_name, index=None)

        def gen_json(table_dict, keyword):
            list_dic = []
            for i in list(table_dict.keys()):
                list_dic.append((i, table_dict[i]))
            dic = OrderedDict(list_dic)
            list_json = WriterJson().odict_to_json(dic)
            WriterJson().write_json(json_list=list_json, file_name=keyword + '.json')

        time_start = time.time()

        url_search = 'http://www.tianyancha.com/search?key=%s&checkFrom=searchBox' % keyword
        self.driver = search_company(self.driver, url_search)
        table_dict = scrapy(self.driver, table, use_default_exception)
        if export == 'xlsx':
            gen_excel(table_dict, keyword)
        elif export == 'json':
            gen_json(table_dict, keyword)
        else:
            print("请选择正确的输出格式，支持'xlsx'和'json'。")

        time_end = time.time()
        print('您的本次爬取共用时{}秒。'.format(int(time_end - time_start)))
        return table_dict

    # 定义批量爬取爬虫
    def tianyancha_scraper_batch(self, input_template='input.xlsx', change_page_interval=2, export='xlsx'):
        df_input = pd.read_excel(input_template, encoding='gb18030').dropna(axis=1, how='all')
        list_dicts = []

        # 逐个处理输入信息
        for i in range(len(df_input)):
            keyword = df_input['公司名称'].iloc[i]
            tables = []
            for j in range(len(df_input.columns) - 2):
                if not pd.isna(df_input.iloc[i, j + 2]):
                    tables.append(df_input.iloc[i, j + 2])

            # 批量调取天眼查爬虫
            table_dict = self.tianyancha_scraper(keyword=keyword, table=tables,
                                                 change_page_interval=change_page_interval, export=export,
                                                 quit_driver=False)
            list_dicts.append(table_dict)

        # 全部运行完后退出浏览器
        self.driver.quit()
        return tuple(list_dicts)
