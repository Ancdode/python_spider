#coding=utf-8

from Crypto.Cipher import AES
import base64
import requests
import json, execjs,codecs

#https://blog.csdn.net/weixin_44530979/article/details/87925950
#https://blog.csdn.net/weixin_40444270/article/details/81260638
#zhihu.com/question/36081767/answer/386606315

first_param ='''{"rid":"R_SO_4_5271025","threadId":"R_SO_4_5271025","pageNo":"1","pageSize":"20","cursor":"-1","offset":"0","orderType":"1","csrf_token":""}'''
#first_param = "{csrf_token:\"\",cursor:\"-1\",offset:\"0\",orderType:\"1\",pageNo:\"1\",pageSize:\"20\",rid:\"R_SO_4_31311140\",threadId:\"R_SO_4_31311140\"}"
second_param = "010001"
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
forth_param = "0CoJUm6Qyw8W8jud"
iv = '0102030405060708'
headers={
        'Host': 'music.163.com',
        'Connection': 'keep-alive',
        'Content-Length': '484',
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

def get_json(url, params, encSecKey):
    data = {
         "params": params,
         "encSecKey": encSecKey
    }
    response = requests.post(url, headers=headers, data=data)
    return response.content

# 获取评网易云评论  解密需要的第一个参数
def get_comment_first_param(songid, page):

    key_dict = dict({
        "rid": "R_SO_4_5271025",
        "threadId": "R_SO_4_5271025",
        "pageNo": "1",
        "pageSize": "20",
        "cursor": "-1",
        "offset": "0",
        "orderType": "1",
        "csrf_token": ""
    })
    key_dict["rid"] = "R_SO_4_" + str(songid)
    key_dict["threadId"] = "R_SO_4_" + str(songid)
    key_dict['pageNo'] = str(page)
    return str(key_dict)

# 获取网易云关键参数
class GetMusicKeyParameter():
    def __init__(self, a, b, c, d, iv):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.iv = iv
        self.i = self.get_16str()

    def get_16str(self):  # 16位随机字符串
        js = '''function a(a) {
            var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            c = "";
            for (d = 0; a > d; d += 1) e = Math.random() * b.length,
            e = Math.floor(e),
            c += b.charAt(e);
            return c
        }'''
        js_data = execjs.compile(js)
        return js_data.call('a', 16)

    def to_16(self, key):
        while len(key) % 16 != 0:
            key += '\0'
        return str.encode(key)

    def get_params(self):  #获取两次AES加密后的密文
        # a -- 明文  d -- 密钥  iv --偏移量
        first_aes = self.AES_encrypt(self.a, self.d, self.iv)  # 第一次加密
        return self.AES_encrypt(first_aes, self.i, self.iv)

    def AES_encrypt(self, text, key, iv): #text为需加密的明文，key为密钥，iv为偏移量
        bs = AES.block_size   # 16位  text, key, iv都必须为16位
        pad2 = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)  # 填充方式：pcks7padding
        encryptor = AES.new(self.to_16(key), AES.MODE_CBC, self.to_16(iv))  # 加密模式为 CBC
        encrypt_aes = encryptor.encrypt(str.encode(pad2(text)))
        encrypt_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
        return encrypt_text

    def get_encSecKey(self):
        encSecKey = self.RSA_encrypt(self.i, self.b, self.c)
        return encSecKey

    def RSA_encrypt(self, text, pubKey, modulus):  # RSA加密
        text = text[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pubKey, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)


if __name__ == "__main__":
    url = "https://music.163.com/weapi/comment/resource/comments/get?csrf_token="
    first_param = get_comment_first_param('26305527', 1)
    getkey = GetMusicKeyParameter(first_param,second_param,third_param,forth_param,iv)
    params = getkey.get_params()
    encSecKey = getkey.get_encSecKey()
    json_text = get_json(url, params, encSecKey)
    json_dict = json.loads(json_text)
    print(json_dict['data']['totalCount'])
