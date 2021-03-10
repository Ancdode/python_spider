from selenium import webdriver
from selenium.webdriver.support.select import Select
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib import request, error
import socket

import sys

# 显示下载进度
def progressbar(cur, total=100):
    percent = '{:.2%}'.format(cur / total)
    sys.stdout.write('\r')
    # sys.stdout.write("[%-50s] %s" % ('=' * int(math.floor(cur * 50 / total)),percent))
    sys.stdout.write("[%-100s] %s" % ('=' * int(cur), percent))
    sys.stdout.flush()


def schedule(blocknum,blocksize,totalsize):
    """
    blocknum:当前已经下载的块
    blocksize:每次传输的块大小
    totalsize:网页文件总大小
    """
    if totalsize == 0:
        percent = 0
    else:
        percent = blocknum * blocksize / totalsize
    if percent > 1.0:
        percent = 1.0
    percent = percent * 100
    print("download : %.2f%%" %(percent))
    progressbar(percent)

#每页的第（filename+1)条微博
def download_video(final_url, page_number, filename):
    try:
        request.urlretrieve(final_url, '{}{}_{}.mp4'.format(
            'D:\\programming\\python\\spider\\weibo\\data\\', page_number, filename),
                            schedule
                            )
    except error.HTTPError as e:
        print(e)
        print('\r\n' + final_url + ' download failed!' + '\r\n')
    else:
        print('\r\n' + final_url + ' download successfully!')


#每页的第（filename+1)条微博的第（nine+1）张图片
def download_picture(url,page_number , filename, nine):
    # 下载不下来 程序会暂停？ 停在这？
    # urllib.request.urlretrieve() 下载文件经常会出现卡死的问题
    # 解决办法：https://blog.csdn.net/snailzzw/article/details/109550759
    # 设置超时时间
    socket.setdefaulttimeout(10)
    try:
        request.urlretrieve(url, '{}{}_{}_{}.jpg'.format(
            'D:\\programming\\python\\spider\\weibo\\data\\', page_number, filename, nine)
                            )
    except socket.timeout:
        count = 1
        while count <= 5:
            try:
                request.urlretrieve(url, '{}{}_{}_{}.jpg'.format(
                    'D:\\programming\\python\\spider\\weibo\\data\\', page_number, filename, nine)
                                    )
                break
            except socket.timeout:
                err_info = 'Reloading for %d time' % count if count == 1 else 'Reloading for %d times' % count
                print(err_info)
                count += 1
        if count > 5:
            print("download job failed!")
        else:
            print("download successfully!")
    else:
        print("download successfully!")



# 存发微博的时间 和内容及 转发链接
def save_weibotimeandcontent(page_number, filename, weibo_time, content, url):
    file = open('D:\\programming\\python\\spider\\weibo\\data\\a.txt', 'a', encoding='utf-8')
    file.write('{}_{}: {}    {}    {} \n'.format(page_number, filename, weibo_time, content, url))
    file.close()

driver = webdriver.Chrome()
driver.maximize_window()
# 使用find_elements 找元素，未找到返回空列表
# 而find_element 找元素，未找到会弹出NoSuchElementException异常

driver.get('https://weibo.com/')
time.sleep(7)
nickname = 'yournickname'
password = '************'
#def login(nickname,password):
driver.find_element_by_id('loginname').clear()
driver.find_element_by_id('loginname').send_keys(nickname)
time.sleep(2)
driver.find_element_by_name('password').clear()
driver.find_element_by_name('password').send_keys(password)
time.sleep(5)
driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
time.sleep(2)
print("等待人工扫码验证:")
time.sleep(10)

#driver.get('https://weibo.com/rmrb?refer_flag=1005055013_&is_all=1')  #人民日报主页
#driver.get('https://weibo.com/u/1931732580?is_all=1')
driver.get('https://weibo.com/u/1931732580?is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page=5#_rnd1615187652584')
time.sleep(7)
scroll_js = "window.scrollTo(0,document.body.scrollHeight);var lenOfPage = document.body.scrollHeight;return lenOfPage;"
def update_page():
    page_more = True
    page_number = 1   #第一页''
    user_nickname = driver.find_element_by_xpath(".//h1[@class='username']").text  #用户昵称
    while(page_more):
        for i in range(3):
            time.sleep(5)
            driver.execute_script(scroll_js)
        # webcontent = driver.page_source  获取页面源码

        pagelist = driver.find_elements_by_xpath("//*[contains(@node-type,'feed_list_page')]//a")
        #print(type(pagelist), type(driver))
        if pagelist:  # 已刷新至页面底部标签
            page_weibo = driver.find_elements_by_xpath("//*[@class='WB_detail']")   #一页的所有微博
            for filename, weibo in enumerate(page_weibo):
                if weibo.find_elements_by_xpath(".//div[@class='WB_feed_expand']"):  # 如果该条内容转发其他人微博
                    # 还需排除原文已经删除，url则无法获取
                    webelement_retweet_list = weibo.find_elements_by_xpath(".//div[@class='WB_handle W_fr']//ul/li[2]//a")
                    if webelement_retweet_list:
                        one_weibo_retweet_url = webelement_retweet_list[0].get_attribute('href')
                    else:
                        one_weibo_retweet_url = '原文已删除或者不可见'
                    one_weibo_text = weibo.find_element_by_xpath(".//div[@class='WB_text W_f14']").text  # 获取转发的评价内容
                    one_weibo_time = weibo.find_element_by_xpath(".//div[@class='WB_from S_txt2']/a[1]").get_attribute(
                        'title')  # 获取时间
                    print("one_weibo_time:", one_weibo_time)
                    print("one_weibo_text:", one_weibo_text)
                    save_weibotimeandcontent(page_number, filename, one_weibo_time, one_weibo_text, one_weibo_retweet_url)
                    continue      # 不获取其他内容 直接遍历下一条微博
                elif weibo.find_element_by_xpath("./div[@class='WB_info']/a[1]").text != user_nickname: #点赞其他人的微博
                    #目前少考虑点赞微博被删除的情况
                    one_weibo_text = '这是条点赞微博'
                    one_weibo_time = weibo.find_element_by_xpath("../../div[1]//h4/span[2]/a").text
                    one_weibo_retweet_url = '暂时没有找到获取点赞微博链接的办法'
                    print("one_weibo_time:", one_weibo_time)
                    print("one_weibo_text:", one_weibo_text)
                    save_weibotimeandcontent(page_number, filename, one_weibo_time, one_weibo_text, one_weibo_retweet_url)
                    continue  # 不获取其他内容 直接遍历下一条微博
                else:
                    one_weibo_retweet_url = ''
                one_weibo_time = weibo.find_element_by_xpath(".//div[@class='WB_from S_txt2']/a[1]").get_attribute('title')  # 获取时间
                print("one_weibo_time:", one_weibo_time)
                content_islong = False
                final_url = ''
                try:
                    weibo.find_element_by_xpath(".//div[@class='WB_text W_f14']/a[@class='WB_text_opt']")
                    content_islong = True
                except NoSuchElementException as e:
                    content_islong = False
                    print("字数少，不需展开全文")
                if(content_islong):
                    all_content_url = weibo.find_element_by_xpath(".//div[@class='WB_text W_f14']/a[@class='WB_text_opt']").get_attribute('href')
                    driver.execute_script('window.open("{all_content_url}")'.format(all_content_url = all_content_url))
                    time.sleep(2)
                    driver.switch_to_window(driver.window_handles[1])
                    one_weibo_text = driver.find_element_by_xpath(".//div[@class='WB_text W_f14']").text  # 获取所有内容
                    one_weibo_video = driver.find_elements_by_xpath(".//div[@class='WB_text W_f14']/a[contains(@action-type,'feed_list_url')]")
                    if one_weibo_video:   # 视频 或正直播、微博故事
                        full_video_url = one_weibo_video[0].get_attribute('href')
                        driver.execute_script('window.open("{full_video_url}")'.format(full_video_url=full_video_url))
                        time.sleep(2)
                        driver.switch_to_window(driver.window_handles[2])
                        #视频、微博故事最终链接
                        isvideo = driver.find_elements_by_xpath(".//div[@class='PlayInfo_videoplayer_28YqA']//video | .//div[@class='video-box']//video ")
                        if isvideo:
                            final_url = isvideo[0].get_attribute('src')
                            download_video(final_url, page_number, filename)
                        else:  # 正在直播 或是其他文章
                            final_url = ''
                        driver.close()
                        driver.switch_to_window(driver.window_handles[1])
                    driver.close() #关闭当前标签页
                    #关闭浏览器全部标签页 driver.quit()
                    driver.switch_to_window(driver.window_handles[0])
                else:
                    one_weibo_text = weibo.find_element_by_xpath(".//div[@class='WB_text W_f14']").text   # 获取所有内容
                    one_weibo_video = weibo.find_elements_by_xpath(".//a[contains(@action-type,'feed_list_url')]")
                    if one_weibo_video:  # 视频 或正直播
                        full_video_url = one_weibo_video[0].get_attribute('href')
                        driver.execute_script('window.open("{full_video_url}")'.format(full_video_url=full_video_url))
                        time.sleep(2)
                        driver.switch_to_window(driver.window_handles[1])
                        isvideo = driver.find_elements_by_xpath(".//div[@class='PlayInfo_videoplayer_28YqA']//video | .//div[@class='video-box']//video ")
                        if isvideo:
                            final_url = isvideo[0].get_attribute('src')
                            download_video(final_url, page_number, filename)
                        else:  # 正在直播 或是其他文章
                            final_url = ''
                        driver.close()
                        driver.switch_to_window(driver.window_handles[0])
                    # one_weibo_video = weibo.find_elements_by_xpath(".//div[@class='WB_story_video_box']//video")
                    # if one_weibo_video:  # 微博故事
                    #     final_url = one_weibo_video[0].get_attribute('src')
                    #     download_video(final_url, page_number, filename)
                print("one_weibo_text:", one_weibo_text)
                one_weibo_minpics = weibo.find_elements_by_xpath(".//ul[contains(@node-type,'fl_pic_list')]//li")
                one_weibo_maxpics_url = []
                if one_weibo_minpics : #带图片的微博---且图片为多张
                    for i, pic in enumerate(one_weibo_minpics):
                        #图片与视图（容器）顶部对齐效果不好，时常出现图片太小无法元素（图片）点击中心的问题
                        driver.execute_script("arguments[0].scrollIntoView(false);", pic)
                        #imgshow = pic.find_element_by_xpath("..").click()

                        pic.click()
                        time.sleep(1)
                        bigimg_xpath = ".//div[contains(@node-type,'imgSpanBox')]/img"
                        webelementbigimg = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, bigimg_xpath)))
                        src = webelementbigimg.get_attribute('src')
                        print(src)
                        #tosamall = driver.find_element_by_xpath("//a[contains(@action-type,widget_photoview)]")
                        #tosamall.click()
                        # 在元素中心点点击
                        ActionChains(driver).move_to_element(webelementbigimg).click().perform()
                        time.sleep(1)
                        download_picture(src, page_number, filename, len(one_weibo_maxpics_url))
                        one_weibo_maxpics_url.append(src)


                            #".//div[contains(@node-type,'imgSpanBox')]/img[{index}]".format(index=i)), 1, 1).click().perform()
                        #one_weibo_maxpics_url.append(weibo.find_element_by_xpath(".//div[contains(@node-type,'imgSpanBox')]/img").get_attribute('src'))
                one_weibo_minpics = weibo.find_elements_by_xpath(".//li[contains(@action-type,'feed_list_media_img')]")
                if one_weibo_minpics:    #带图片的微博 --- 且只有一张(微博视频的时候也有一张图片)
                    # 排除微博视频情况下的一张图片的情况  微博视频封面是在 li/div/img
                    if(weibo.find_elements_by_xpath(".//li[contains(@action-type,'feed_list_media_img')]/img")):
                        driver.execute_script("arguments[0].scrollIntoView(false);", one_weibo_minpics[0])
                        one_weibo_minpics[0].click()
                        time.sleep(1)
                        bigimg_xpath = ".//div[contains(@action-type,'feed_list_media_bigimg')]/img"
                        webelementbigimg = WebDriverWait(driver, 50).until(
                            EC.presence_of_element_located((By.XPATH, bigimg_xpath)))
                        src = webelementbigimg.get_attribute('src')
                        print(src)
                        ActionChains(driver).move_to_element(webelementbigimg).click().perform()  # 在元素中心点点击
                        time.sleep(1)
                        download_picture(src, page_number, filename, len(one_weibo_maxpics_url))
                        one_weibo_maxpics_url.append(src)
                print(len(one_weibo_maxpics_url))
                save_weibotimeandcontent(page_number, filename, one_weibo_time, one_weibo_text, one_weibo_retweet_url)


            if driver.find_elements_by_xpath(".//a[contains(text(),'下一页')]"):
                page_more = True
                driver.find_element_by_xpath(".//a[contains(text(),'下一页')]").click() #跳转至下一页
                page_number += 1
                time.sleep(5)
            else:   # 没有下一页
                page_more = False
                driver.quit()


update_page()


