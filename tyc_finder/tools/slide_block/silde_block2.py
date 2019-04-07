# coding=utf8
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import re
import time
from PIL import Image
from tyc_finder.tools.slide_block import easing


class Tes(object):
    # 初始化
    def __init__(self, url, username, password):
        # 定义为全局变量，方便其他模块使用
        self.url = url
        # 登录界面的url
        # 用户名
        self.username = username
        # 密码
        self.password = password

        # 实例化一个chrome浏览器
        self.browser = webdriver.Chrome(
            '/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac'
        )

        # 设置等待超时
        self.wait = WebDriverWait(self.browser, 20)

    # 登录
    def login(self, url):
        # 打开登录页面
        self.browser.get(url)
        # 获取用户名输入框
        user = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        # 获取密码输入框
        passwd = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        # 输入用户名
        user.send_keys(self.username)
        # 输入密码
        passwd.send_keys(self.password)

    # 获取小图片位置
    @staticmethod
    def get_position(img):
        '''
        :param img: (List)存放多个小图片的标签
        :return: (List)每个小图片的位置信息
        '''

        img_position = []
        for small_img in img:
            position = {}
            # 获取每个小图片的横坐标
            position['x'] = int(re.findall('background-position: (.*)px (.*)px;', small_img.get('style'))[0][0])
            # 获取每个小图片的纵坐标
            position['y'] = int(re.findall('background-position: (.*)px (.*)px;', small_img.get('style'))[0][1])
            img_position.append(position)
        return img_position

    # 获取图片信息
    @classmethod
    def get_image_info(cls, img, browser):
        '''
        :param img: (Str)想要获取的图片类型：带缺口、原始
        :return: 该图片(Image)、位置信息(List)
        '''

        # 将网页源码转化为能被解析的lxml格式
        soup = BeautifulSoup(browser.page_source, 'lxml')
        # 获取验证图片的所有组成片标签
        imgs = soup.find_all('div', {'class': 'gt_cut_' + img + '_slice'})
        # 用正则提取缺口的小图片的url，并替换后缀
        time.sleep(5.015)
        img_url = re.findall('url\(\"(.*)\"\);', imgs[0].get('style'))[0].replace('webp', 'jpg')
        # 使用urlretrieve()方法根据url下载缺口图片对象
        urlretrieve(url=img_url, filename=img + '.jpg')
        # 生成缺口图片对象
        image = Image.open(img + '.jpg')
        # 获取组成他们的小图片的位置信息
        position = cls.get_position(imgs)
        # 返回图片对象及其位置信息
        return image, position

    # 裁剪图片
    @classmethod
    def Corp(cls, image, position):
        '''
        :param image:(Image)被裁剪的图片
        :param position: (List)该图片的位置信息
        :return: (List)存放裁剪后的每个图片信息
        '''

        # 第一行图片信息
        first_line_img = []
        # 第二行图片信息
        second_line_img = []
        for pos in position:
            if pos['y'] == -58:
                first_line_img.append(image.crop((abs(pos['x']), 58, abs(pos['x']) + 10, 116)))
            if pos['y'] == 0:
                second_line_img.append(image.crop((abs(pos['x']), 0, abs(pos['x']) + 10, 58)))
        return first_line_img, second_line_img

    # 拼接大图
    @staticmethod
    def put_imgs_together(first_line_img, second_line_img, img_name):
        '''
        :param first_line_img: (List)第一行图片位置信息
        :param second_line_img: (List)第二行图片信息
        :return: (Image)拼接后的正确顺序的图片
        '''

        # 新建一个图片，new()第一个参数是颜色模式，第二个是图片尺寸
        image = Image.new('RGB', (260, 116))
        # 初始化偏移量为0
        offset = 0
        # 拼接第一行
        for img in first_line_img:
            # past()方法进行粘贴，第一个参数是被粘对象，第二个是粘贴位置
            image.paste(img, (offset, 0))
            # 偏移量对应增加移动到下一个图片位置,size[0]表示图片宽度
            offset += img.size[0]
        # 偏移量重置为0
        x_offset = 0
        # 拼接第二行
        for img in second_line_img:
            # past()方法进行粘贴，第一个参数是被粘对象，第二个是粘贴位置
            image.paste(img, (x_offset, 58))
            # 偏移量对应增加移动到下一个图片位置，size[0]表示图片宽度
            x_offset += img.size[0]
        # 保存图片
        image.save(img_name)
        # 返回图片对象
        return image

    # 获取小图片位置
    @staticmethod
    def get_position(img):
        '''
        :param img: (List)存放多个小图片的标签
        :return: (List)每个小图片的位置信息
        '''

        img_position = []
        for small_img in img:
            position = {}
            # 获取每个小图片的横坐标
            position['x'] = int(re.findall('background-position: (.*)px (.*)px;', small_img.get('style'))[0][0])
            # 获取每个小图片的纵坐标
            position['y'] = int(re.findall('background-position: (.*)px (.*)px;', small_img.get('style'))[0][1])
            img_position.append(position)
        return img_position

    # 裁剪图片
    @staticmethod
    def Corp(image, position):
        '''
        :param image:(Image)被裁剪的图片
        :param position: (List)该图片的位置信息
        :return: (List)存放裁剪后的每个图片信息
        '''

        # 第一行图片信息
        first_line_img = []
        # 第二行图片信息
        second_line_img = []
        for pos in position:
            if pos['y'] == -58:
                first_line_img.append(image.crop((abs(pos['x']), 58, abs(pos['x']) + 10, 116)))
            if pos['y'] == 0:
                second_line_img.append(image.crop((abs(pos['x']), 0, abs(pos['x']) + 10, 58)))
        return first_line_img, second_line_img

    # 计算滑块移动距离
    @classmethod
    def get_distance(cls, bg_image, fullbg_image):
        '''
        :param bg_image: (Image)缺口图片
        :param fullbg_image: (Image)完整图片
        :return: (Int)缺口离滑块的距离
        '''

        # 滑块的初始位置
        distance = 57
        # 遍历像素点横坐标
        for i in range(distance, fullbg_image.size[0]):
            # 遍历像素点纵坐标
            for j in range(fullbg_image.size[1]):
                # 如果不是相同像素
                if not cls.is_pixel_equal(fullbg_image, bg_image, i, j):
                    # 返回此时横轴坐标就是滑块需要移动的距离
                    return i

    # 判断像素是否相同
    @staticmethod
    def is_pixel_equal(bg_image, fullbg_image, x, y):
        """
        :param bg_image: (Image)缺口图片
        :param fullbg_image: (Image)完整图片
        :param x: (Int)位置x
        :param y: (Int)位置y
        :return: (Boolean)像素是否相同
        """

        # 获取缺口图片的像素点(按照RGB格式)
        bg_pixel = bg_image.load()[x, y]
        # 获取完整图片的像素点(按照RGB格式)
        fullbg_pixel = fullbg_image.load()[x, y]
        # 设置一个判定值，像素值之差超过判定值则认为该像素不相同
        threshold = 60
        # 判断像素的各个颜色之差，abs()用于取绝对值
        if (abs(bg_pixel[0] - fullbg_pixel[0] < threshold) and abs(bg_pixel[1] - fullbg_pixel[1] < threshold) and abs(
                bg_pixel[2] - fullbg_pixel[2] < threshold)):
            # 如果差值在判断值之内，返回是相同像素
            return True

        else:
            # 如果差值在判断值之外，返回不是相同像素
            return False

    @staticmethod
    def get_tracks2(distance):
        distance += 20  # 先滑过一点，最后再反着滑动回来
        v = 0
        t = 0.2
        forward_tracks = []

        current = 0
        mid = distance * 3 / 5
        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3

            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            current += s
            forward_tracks.append(round(s))

        # 反着滑动到准确位置
        back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]  # 总共等于-20

        return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}

    # 构造滑动轨迹
    @staticmethod
    def get_trace(distance):
        '''
        :param distance: (Int)缺口离滑块的距离
        :return: (List)移动轨迹
        '''

        # 创建存放轨迹信息的列表
        trace = []
        # 设置加速的距离
        faster_distance = distance * (3 / 4)
        # 设置初始位置、初始速度、时间间隔
        start, v0, t = 0, 0, random.randint(2, 3) / 10
        # 当尚未移动到终点时
        while start < distance:
            # 如果处于加速阶段
            if start < faster_distance:
                # 设置加速度为2
                a = 2
            # 如果处于减速阶段
            else:
                # 设置加速度为-3
                a = -3
            # 移动的距离公式
            move = v0 * t + 1 / 2 * a * t * t
            # 此刻速度
            v = v0 + a * t
            # 重置初速度
            v0 = v
            # 重置起点
            start += move
            # 将移动的距离加入轨迹列表
            trace.append(round(move))
        # 返回轨迹信息
        # over_move = round(sum(trace) / len(trace))
        # trace.append(round(over_move))
        #
        # trace.append(-over_move)

        return trace

    @staticmethod
    def drag_and_drop(browser, offset):
        # 得到滑块标签
        knob = browser.find_element_by_class_name("gt_slider_knob")
        offsets, tracks = easing.get_tracks(offset, 12, 'ease_out_expo')
        ActionChains(browser).click_and_hold(knob).perform()
        for x in tracks:
            ActionChains(browser).move_by_offset(x, 0).perform()
        ActionChains(browser).pause(0.5).release().perform()

    def move_to_gap2(self, tracks):
        # 得到滑块标签
        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_slider_knob')))
        # 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
        ActionChains(self.browser).click_and_hold(slider).perform()
        # 正常人类总是自信满满地开始正向滑动，自信地表现是疯狂加速
        for track in tracks['forward_tracks']:
            time.sleep(0.015)
            ActionChains(self.browser).move_by_offset(xoffset=track, yoffset=0).perform()

        # 结果傻逼了，正常的人类停顿了一下，回过神来发现，卧槽，滑过了,然后开始反向滑动
        time.sleep(0.5)
        for back_track in tracks['back_tracks']:
            time.sleep(0.015)
            ActionChains(self.browser).move_by_offset(xoffset=back_track, yoffset=0).perform()

        # 小范围震荡一下，进一步迷惑极验后台，这一步可以极大地提高成功率
        ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()

        # 成功后，骚包人类总喜欢默默地欣赏一下自己拼图的成果，然后恋恋不舍地松开那只脏手
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    # 模拟拖动
    def move_to_gap(self, trace):
        # 得到滑块标签
        slider = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_slider_knob')))
        # 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in trace:
            time.sleep(0.015)
            # 使用move_by_offset()方法拖动滑块，perform()方法用于执行
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        # 模拟人类对准时间
        time.sleep(0.68)
        # 释放滑块
        ActionChains(self.browser).release().perform()

    # 主程序


def main(url, username, password):
    # 初始化
    T = Tes(url, username, password)
    # 登录
    T.login(url)
    # 获取缺口图片及其位置信息
    bg, bg_position = T.get_image_info('bg', T.browser)
    # 获取完整图片及其位置信息
    fullbg, fullbg_position = T.get_image_info('fullbg', T.browser)
    # 将混乱的缺口图片裁剪成小图，获取两行的位置信息
    bg_first_line_img, bg_second_line_img = T.Corp(bg, bg_position)
    # 将混乱的完整图片裁剪成小图，获取两行的位置信息
    fullbg_first_line_img, fullbg_second_line_img = T.Corp(fullbg, fullbg_position)
    # 根据两行图片信息拼接出缺口图片正确排列的图片
    bg_image = T.put_imgs_together(bg_first_line_img, bg_second_line_img, 'bg.jpg')
    # 根据两行图片信息拼接出完整图片正确排列的图片
    fullbg_image = T.put_imgs_together(fullbg_first_line_img, fullbg_second_line_img, 'fullbg.jpg')
    # 计算滑块移动距离
    distance = T.get_distance(bg_image, fullbg_image)
    # 计算移动轨迹

    trace = T.get_trace(distance - 10)
    # 移动滑块
    T.move_to_gap(trace)

    # tracks = T.get_tracks2(distance-10)
    # 7、按照行动轨迹先正向滑动，后反滑动

    # # 移动滑块
    # T.move_to_gap(d['forward_tracks'])
    # T.move_to_gap2(tracks)

    time.sleep(5)

    # 程序入口


if __name__ == '__main__':
    url = 'https://passport.bilibili.com/login'
    username = '***********'
    password = '***********'

    main(url, username, password)
