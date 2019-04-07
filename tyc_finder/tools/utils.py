# -*- coding: utf-8 -*-
import time
import json
import codecs


def conn_try_again(max_retries=5, default_retry_delay=1):
    def _conn_try_again(function):
        RETRIES = 0
        # 重试的次数
        count = {"num": RETRIES}

        def wrapped(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as err:
                print(repr(err))
                if count['num'] < max_retries:
                    time.sleep(default_retry_delay)
                    count['num'] += 1
                    return wrapped(*args, **kwargs)
                else:
                    status = 'Error'
                    error_type = eval(repr(err).split('(')[0])
                    raise error_type(err)

        return wrapped

    return _conn_try_again


class WriterJson:
    def __init__(self):
        pass

    # 将单个DataFrame保存为JSON，确保中文显示正确
    def df_to_json(self, df, orient: str = 'table'):
        return json.loads(df.to_json(orient, force_ascii=False))

    # 将多个DataFrames组成的字典批量保存为JSON，确保中文显示正确:服务于类似`金融产品信息表`这样的包含多
    def dfs_to_json(self, dic_dfs, orient: str = 'table'):
        pass

    # 将单个OrderedDict保存为JSON List
    def odict_to_json(self, odict):
        items = list(odict.items())
        list_JSONed = []

        # 把列表中的每个df通过list append变成json
        for i in range(len(items)):
            try:
                list_JSONed.append([items[i][0], json.loads(items[i][1].to_json(orient='table', force_ascii=False))])
            except:
                print(items[i][0] + '表为空，请检查。')
        # 记录版本信息
        list_JSONed.append({'version_date': time.strftime("%Y/%m/%d")})

        return list_JSONed

    # 从list_JSONed获取公司名称，用于设置JSON文件名称
    def get_company_name_from_JSON(self, items_JSONed):
        pass

    # 将一个json list或者json dict存入文件
    def write_json(self, json_list, file_name, indent=4, encoding='utf-8'):
        f_out = codecs.open(file_name, 'w', encoding=encoding)
        json_str = json.dumps(json_list, indent=indent, ensure_ascii=False)  # , encoding=encoding)
        f_out.write(json_str)
        f_out.close()
