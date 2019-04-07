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
from tyc_finder.tools.utils import conn_try_again

class Test_spider(object):

    # 初始化
    def __init__(self, driver_path, username, password):
        # 定义为全局变量，方便其他模块使用

        browser, wait = self._get_browser(driver_path=driver_path)

        self.browser = browser
        self.wait = wait

        # 登录界面的url
        # 用户名
        self.username = username
        # 密码
        self.password = password

    @staticmethod
    def _get_browser(driver_path='/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac',
                     wait_time=20):
        # 实例化一个chrome浏览器
        browser = webdriver.Chrome(driver_path)
        # 设置等待超时
        wait = WebDriverWait(browser, wait_time)
        return browser, wait

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


class ParseImages(object):

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

    @staticmethod
    @conn_try_again(max_retries=10, default_retry_delay=2)
    def get_img_url_re(imgs):
        img_url = re.findall('url\(\"(.*)\"\);', imgs[0].get('style'))[0].replace('webp', 'jpg')
        return img_url

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
        time.sleep(5.015)  # waiting
        # img_url = re.findall('url\(\"(.*)\"\);', imgs[0].get('style'))[0].replace('webp', 'jpg')
        img_url = cls.get_img_url_re(imgs)
        # 使用urlretrieve()方法根据url下载缺口图片对象
        urlretrieve(url=img_url, filename=img + '.jpg')
        # 生成缺口图片对象
        image = Image.open(img + '.jpg')
        # 获取组成他们的小图片的位置信息
        position = cls.get_position(imgs)
        # 返回图片对象及其位置信息
        return image, position

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
        if (abs(bg_pixel[0] - fullbg_pixel[0] < threshold) and abs(
                bg_pixel[1] - fullbg_pixel[1] < threshold) and abs(
            bg_pixel[2] - fullbg_pixel[2] < threshold)):
            # 如果差值在判断值之内，返回是相同像素
            return True

        else:
            # 如果差值在判断值之外，返回不是相同像素
            return False

    pass


class CrackSlideVerification(object):
    @staticmethod
    def get_slider(wait, slider_label='gt_slider_knob'):
        slider = wait.until(EC.presence_of_element_located((By.CLASS_NAME, slider_label)))
        return slider

    @staticmethod
    def cal_tracks(distance, algo='ease_out_expo'):
        offsets, trace = easing.get_tracks(distance, 12, algo)
        return offsets, trace

    @staticmethod
    def mock_grab_and_move(browser, slider, trace):
        # 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
        ActionChains(browser).click_and_hold(slider).perform()

        for x in trace:
            time.sleep(0.015)
            # 使用move_by_offset()方法拖动滑块，perform()方法用于执行
            ActionChains(browser).move_by_offset(xoffset=x, yoffset=0).perform()

        # 释放滑块
        # 小范围震荡一下，进一步迷惑极验后台，这一步可以极大地提高成功率
        ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(browser).move_by_offset(xoffset=3, yoffset=0).perform()
        # 模拟人类对准时间
        ActionChains(browser).pause(0.68).release().perform()


def test(browser, wait):
    # 获取缺口图片及其位置信息
    bg, bg_position = ParseImages.get_image_info('bg', browser)

    # 获取完整图片及其位置信息
    fullbg, fullbg_position = ParseImages.get_image_info('fullbg', browser)
    # 将混乱的缺口图片裁剪成小图，获取两行的位置信息
    bg_first_line_img, bg_second_line_img = ParseImages.Corp(bg, bg_position)
    # 将混乱的完整图片裁剪成小图，获取两行的位置信息
    fullbg_first_line_img, fullbg_second_line_img = ParseImages.Corp(fullbg, fullbg_position)
    # 根据两行图片信息拼接出缺口图片正确排列的图片
    bg_image = ParseImages.put_imgs_together(bg_first_line_img, bg_second_line_img, 'bg.jpg')
    # 根据两行图片信息拼接出完整图片正确排列的图片
    fullbg_image = ParseImages.put_imgs_together(fullbg_first_line_img, fullbg_second_line_img, 'fullbg.jpg')
    # 计算滑块移动距离
    distance = ParseImages.get_distance(bg_image, fullbg_image)
    # 计算移动轨迹
    offsets, trace = CrackSlideVerification.cal_tracks(distance - 10)

    slider = CrackSlideVerification.get_slider(wait, slider_label='gt_slider_knob')
    # 移动滑块
    CrackSlideVerification.mock_grab_and_move(browser, slider, trace)


if __name__ == '__main__':
    url = 'https://www.tianyancha.com/login'

    username = '***********'
    password = '***********'
    driver_path = '/Users/sn0wfree/Documents/GitHub/tyc_finder/tyc_finder/drivers/chromedriver_mac'
    Ts = Test_spider(driver_path, username, password)
    Ts.login(url)
    browser = Ts.browser
    wait = Ts.wait

    test(browser, wait)
    pass
