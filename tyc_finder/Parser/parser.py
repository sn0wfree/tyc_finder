# -*- coding: utf-8 -*-


class ParseResultHolder(object):
    @staticmethod
    def parse(driver):
        return driver

    @staticmethod
    def search_filter_params():
        search_filter_parents = """//*[@id="search-filter"][@class="search-filter"]"""
        search_filter_dict = dict(locate_search_filter_holder=search_filter_parents,
                                  header=f"""{search_filter_parents}/div[@class="filter-type]""",
                                  body=f"""{search_filter_parents}/div[@class="filter-body]""",
                                  search_expand_btn=f"""{search_filter_parents}/div[@class="search-expand-btn]""")

        return search_filter_dict

    @staticmethod
    def search_result_params():
        search_result_parents = """//*[@id="web-content"]//div[@class="search-block header-block-container"]"""
        search_result_dict = dict(search_result_dict_holder=search_result_parents,
                                  result_tips=f"""{search_result_parents}//div[@class="result-tips"]""",
                                  result_list=f"""{search_result_parents}//div[@class="result-list sv-search-container"]""",
                                  result_footer=f"""{search_result_parents}//div[@class="result-footer"]""")
        return search_result_dict

    @classmethod
    def xpath_list(cls):
        search_filter_dict = cls.search_filter_params()
        search_result_dict = cls.search_result_params()
        return {"search_filter": search_filter_dict, "search_result_dict": search_result_dict}




