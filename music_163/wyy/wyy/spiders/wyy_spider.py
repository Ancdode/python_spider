# coding=utf-8
import scrapy

from scrapy_splash import  SplashRequest
from scrapy.loader import ItemLoader
from wyy.items import WyyItem
import gzip
import zlib
import requests, json
from wyy.spiders import Decrypt
'''  js=string.format([[x=document.getElementsByClassName('nm nm-icn f-thide s-fc0');x[%d].click()]],args.same_az_id)
  splash:evaljs(js)'''
script = '''
function main(splash, args)
  splash.images_enabled= false
  local header=assert(splash:go{args.url,headers=args.headers})
  assert(splash:wait(args.wait))
  return header.headers

end
'''
class WyySpiderSpider(scrapy.Spider):
    name = 'wyy_spider'
    allowed_domains = ['music.163.com']
    country_id = {1, 2, 6, 7, 4}  # 分别代表 华语、欧美、日本、韩国、其他
    gender_id = {1, 2, 3}   # 分别代表男歌手、女歌手、组合
    cookies = {
        '_ntes_nnid': '7eced19b27ffae35dad3f8f2bf5885cd, 1476521011210',
        '_ntes_nuid': '7eced19b27ffae35dad3f8f2bf5885cd',
        'usertrack': 'c+5+hlgB7TgnsAmACnXtAg==',
        'Province': '025',
        'City': '025',
        'NTES_PASSPORT': '6n9ihXhbWKPi8yAqG.i2kETSCRa.ug06Txh8EMrrRsliVQXFV_orx5HffqhQjuGHkNQrLOIRLLotGohL9s10wcYSPiQfI2wiPacKlJ3nYAXgM',
        'P_INFO': 'hourui93@163.com|1476523293|1|study|11&12|jis&1476511733&mail163#jis&320100#10#0#0|151889&0|g37_client_check&mailsettings&mail163&study&blog|hourui93@163.com',
        'NTES_SESS': 'Fa2uk.YZsGoj59AgD6tRjTXGaJ8_1_4YvGfXUkS7C1NwtMe.tG1Vzr255TXM6yj2mKqTZzqFtoEKQrgewi9ZK60ylIqq5puaG6QIaNQ7EK5MTcRgHLOhqttDHfaI_vsBzB4bibfamzx1.fhlpqZh_FcnXUYQFw5F5KIBUmGJg7xdasvGf_EgfICWV',
        'S_INFO': '1476597594|1|0&80##|hourui93',
        'NETEASE_AUTH_SOURCE': 'space',
        'NETEASE_AUTH_USERNAME': 'hourui93',
        '_ga': 'GA1.2.1405085820.1476521280',
        'JSESSIONID-WYYY': 'cbd082d2ce2cffbcd5c085d8bf565a95aee3173ddbbb00bfa270950f93f1d8bb4cb55a56a4049fa8c828373f630c78f4a43d6c3d252c4c44f44b098a9434a7d8fc110670a6e1e9af992c78092936b1e19351435ecff76a181993780035547fa5241a5afb96e8c665182d0d5b911663281967d675ff2658015887a94b3ee1575fa1956a5a%3A1476607977016',
        '_iuqxldmzr_': '25',
        '__utma': '94650624.1038096298.1476521011.1476595468.1476606177.8',
        '__utmb': '94650624.20.10.1476606177',
        '__utmc': '94650624',
        '__utmz': '94650624.1476521011.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',

    }
    def start_requests(self):
        for country in self.country_id:
            for gender in self.gender_id:
                for i in range(65, 91):
                    url = 'https://music.163.com/discover/artist/cat?id={}00{}&initial={}'.format(
                            country, gender, i) #获取所有国家所有类型所有姓氏的url
                    yield scrapy.Request(url=url, headers=self.settings.get('HEADERS'), callback=self.parse,
                                        cookies=self.cookies,meta={'dont_merge_cookies':True,'url':url})

    # def parse(self, response):
    #     item = WyyItem()
    #     html = response.body.decode('utf-8')
    #     singers = response.xpath('''.//a[@class='nm nm-icn f-thide s-fc0']''')
    #     for same_az_id,singer in enumerate(singers):
    #         yield SplashRequest(response.meta['url'], callback=self.singer_parse, endpoint='execute', args={
    #             'lua_source': script, 'same_az_id': same_az_id, 'wait': 1,'headers':self.settings.get('HEADERS')
    #         })
    # def singer_parse(self, response):
    #     # 有的不需要解压 加个判断就好了
    #     html = response.body.decode('utf-8')
    #     try:
    #         decode_data = gzip.decompress(response.body.decode('utf-8')).decode('utf-8')
    #         #decode_data = zlib.decompress(response.body, 16 + zlib.MAX_WBITS)
    #         # print('用了gzip啊：{}'.format(decode_data))
    #     except:  # 请求失败的链接返回的是json 不能用gzip
    #         decode_data = response.body.decode()
    #     music_list = decode_data.xpath('''.//table[@class='m-table m-table-1 m-table-4']/tbody//tr''')
    #     for music in music_list:
    #         music_name = music.xpath('./td[2]//a/b/@title').extract_first('没拿到歌名?')
    #         music_url = music.xpath('./td[2]//a/@href').extract_first('没拿到song的herf?')
    #         music_id = music_url.replace('/song?id=', '').strip()
    #         real_music_url = 'https://music.163.com/song?id={}&limit=200'.format(music_id)



    def parse(self, response):
        item = WyyItem()
        html = response.body.decode('utf-8')
        singers = response.xpath('''.//a[@class='nm nm-icn f-thide s-fc0']''')
        for i,singer in enumerate(singers):
            #if i == 0:   #调试只拿一个歌手
                singer_name = singer.xpath('./text()').extract_first('没拿到name')
                singer_url = singer.xpath('./@href').extract_first('没拿到singer的herf?')
                singer_id = singer_url .replace('/artist?id=', '').strip()  # 获取歌手ID
                real_singer_url = 'https://music.163.com/artist?id={}'.format(singer_id)

                item['singer_name'] = singer_name
                item['singer_id'] = singer_id

                yield scrapy.Request(url=real_singer_url, callback=self.singer_parse,
                                     headers=self.settings.get('HEADERS'), cookies=self.cookies,
                                     meta={'dont_merge_cookies':True,'item':item})

    def singer_parse(self, response):
        item = response.meta['item']
        html = response.body.decode('utf-8')
        music_list = response.xpath('''.//ul[@class='f-hide']//li''')
        for i, music in enumerate(music_list):
            #if i==0:   #调试只取一首歌
                music_name = music.xpath('./a/text()').extract_first('没拿到歌名?')
                music_url = music.xpath('./a/@href').extract_first('没拿到song的herf?')
                music_id = music_url.replace('/song?id=', '').strip()
                real_music_url = 'https://music.163.com/song?id={}'.format(music_id)
                music_comment_url = "https://music.163.com/weapi/comment/resource/comments/get?csrf_token="
                item['music_name'] = music_name
                item['music_id'] = music_id
                item['music_url'] = real_music_url
                first_param = Decrypt.get_comment_first_param(music_id, 1)
                getkey = Decrypt.GetMusicKeyParameter(first_param, Decrypt.second_param,
                                                      Decrypt.third_param, Decrypt.forth_param, Decrypt.iv)
                params = getkey.get_params()
                encSecKey = getkey.get_encSecKey()
                data = {
                    "params": params,
                    "encSecKey": encSecKey
                }
                headers = {
                    'Host': 'music.163.com',
                    'Connection': 'keep-alive',
                    #'Content-Length': '484',
                    'Cache-Control': 'max-age=0',
                    'Origin': 'http://music.163.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': '*/*',
                    'DNT': '1',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
                    'Cookie': 'JSESSIONID-WYYY=b66d89ed74ae9e94ead89b16e475556e763dd34f95e6ca357d06830a210abc7b685e82318b9d1d5b52ac4f4b9a55024c7a34024fddaee852404ed410933db994dcc0e398f61e670bfeea81105cbe098294e39ac566e1d5aa7232df741870ba1fe96e5cede8372ca587275d35c1a5d1b23a11e274a4c249afba03e20fa2dafb7a16eebdf6%3A1476373826753; _iuqxldmzr_=25; _ntes_nnid=7fa73e96706f26f3ada99abba6c4a6b2,1476372027128; _ntes_nuid=7fa73e96706f26f3ada99abba6c4a6b2; __utma=94650624.748605760.1476372027.1476372027.1476372027.1; __utmb=94650624.4.10.1476372027; __utmc=94650624; __utmz=94650624.1476372027.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
                }
                # json_text = Decrypt.get_json(music_comment_url, params, encSecKey)
                # json_dict = json.loads(json_text)
                # print(json_dict['data']['totalCount'])

                # 在headers 中加入Content-Length 会400 Bad Request
                yield scrapy.FormRequest(url=music_comment_url, callback=self.song_parse, headers=headers,
                                         formdata=data,meta={'dont_merge_cookies':True,'item':item})
                # yield scrapy.Request(url=music_comment_url, callback=self.song_parse,method='POST',
                #                      headers=headers, cookies=self.cookies,
                #                      meta={'dont_merge_cookies':True,'item':item},body=json.dumps(body_data))

    def song_parse(self, response):
        item = response.meta['item']
        json_text = response.body
        json_dict = json.loads(json_text)
        music_comment_num = json_dict['data']['totalCount']
        item['music_comment_num'] = music_comment_num
        yield item
