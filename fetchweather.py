#coding=utf-8
import urllib2
from bs4 import BeautifulSoup
from city import citycode
import time
import re
import urllib

picFilePath = 'your-path' #

def set_SourcesPath(path):
    '''
    wicon path 
    '/home/pi/KReminder '
    '''
    global picFilePath
    picFilePath = path + '/Sources/wicon/%s'
    print('picFile path:',picFilePath)
    return True

def htmldownloader(url):
    res = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'})
    page = urllib2.urlopen(res).read().decode('utf-8')
    return page

'''获取实际ip地址，并获得城市id,城市名称,返回字典'''
def fetchIp():
    infolist = []
    page = htmldownloader('http://www.ip.cn')
    soup = BeautifulSoup(page,'lxml')
    res = soup.find(class_='well')
    pinf = res.find_all('p')
    for p in pinf:
        if not p.code is None:
            infolist.append(p.code.getText())
    ip = infolist[0]
    provinceIndex = int(infolist[1].find(u'省'))
    province = infolist[1][0:provinceIndex]
    cityIndex = int(infolist[1].find(u'市'))
    city = infolist[1][provinceIndex + 1:cityIndex]
    cityid =  citycode.get(city.encode('utf-8'))
    return {'ip':ip,'city':city,'province':province,'id':cityid}

'''从中国气象局获取7天天气预报'''
def fetchWeather(cityid):
    wlist = []
    url = 'http://www.weather.com.cn/weather/%s.shtml'%cityid
    page = htmldownloader(url)
    soup = BeautifulSoup(page,'lxml')
    res1 = soup.find(class_ = 't clearfix')#t clearfix  c7d
    res2 = res1.find_all('li')
    for li in res2:
        res3 =   li.find(class_ = 'tem')
        wlist.append({'date':li.h1.getText(),'wtext':li.find(class_ = 'wea').get_text(),
                      'temph':res3.span.getText(),'templ':res3.i.getText()})
    return wlist

'''解析图片地址'''
def parsePicUrl(page):
    '''将picPath转化为str，再用字符串查找的方法找到图片地址'''
    picPathStr = page.encode('utf-8')

    x = picPathStr.index('url(')
    y = picPathStr.rindex(');')
    picUrl =  picPathStr[x+4:y]

    x = picPathStr.index('icon/')
    y = picPathStr.index('.png')
    picName = picPathStr[x+5:y] +'.png'

    return {'picUrl':picUrl,'picName':picName}


'''下载图片'''
def picDownloader(picUrl,picName,fileSavePath=picFilePath):  #/home/pi//Downloads/PycharmProjects/1_weather/pygame/
    filename = fileSavePath%picName
    urllib.urlretrieve(picUrl,filename)


'''获取天气信息，包含实时天气和未来4天的天气预报'''
def fetch1weather():
    page = htmldownloader('http://www.baidu.com/s?wd=实时天气')
    soup = BeautifulSoup(page,'lxml')
    '''获取今日实时天气信息'''
    res = soup.find(class_ = 'opr-personinfo-info')
    res1 = res.find_all('tr')
    sg = ''  #sugest
    for ind in res1:
        res2 = ind.find_all('td')
        str = ''
        for ind1 in res2:
            str += ind1.getText().strip()
        sg += str + ','
    res2 = soup.find(class_='op_weather4_twoicon_today OP_LOG_LINK')
    _wind = res2.find(class_='op_weather4_twoicon_wind').getText().strip()

    weatherInfoList = []

    '''下载实时天气图标并存储'''
    res3 = soup.find(class_= 'op_weather4_twoicon_shishi')
    picPath  =  res3.find(class_='op_weather4_twoicon_icon')
    tdPicInfo = parsePicUrl(picPath)
    picDownloader(tdPicInfo['picUrl'],tdPicInfo['picName'])
    '''获取实时天气信息，并放在weatherInfoList的头部'''
    weathertdInfoDic= {'date': soup.find(class_='op_weather4_twoicon_date').getText().strip(),
            'pm25': soup.find(class_='op_weather4_twoicon_date op_weather4_twoicon_pm25').b.getText().strip(),
            'tempnow': soup.find(class_='op_weather4_twoicon_shishi_title').getText().strip(),
            'wtext': soup.find(class_='op_weather4_twoicon_shishi_sub').getText().strip(),
            'wind': _wind,
            'sg': sg,
            'picInfo':tdPicInfo
                       }
    weatherInfoList.append(weathertdInfoDic)

    weather4Infos = soup.find_all(class_='op_weather4_twoicon_day OP_LOG_LINK')
    for weather4Info in weather4Infos:
        weatherInfoDic = {}
        weekInfo = weather4Info.find(class_='op_weather4_twoicon_date').getText().strip()
        dateInfo = weather4Info.find(class_='op_weather4_twoicon_date_day').getText().strip()
        picIconInfo = weather4Info.find(class_='op_weather4_twoicon_icon')
        picUrlInfo = parsePicUrl(picIconInfo)
        tempInfo = weather4Info.find(class_='op_weather4_twoicon_temp').getText().strip()
        tempLow = tempInfo[:tempInfo.index(' ~ ')]
        tempHigh = tempInfo[tempInfo.index(u' ~ ')+3:tempInfo.index(u'℃')]
        wTextInfo = weather4Info.find(class_='op_weather4_twoicon_weath').getText().strip()
        '''把--小雨到中雨--转换成--小到中雨--'''
        try:
            turnTextIndex = wTextInfo.index(u'转')
            '''舍弃一部分信息,便于显示'''
            wTextInfo = wTextInfo[:turnTextIndex]
        except Exception as e:
            pass
        windInfo = weather4Info.find(class_='op_weather4_twoicon_wind').getText().strip()
        weatherInfoDic ={'week':weekInfo,'date':dateInfo,'picInfo':picUrlInfo,'picUrl':picUrlInfo['picUrl'],'picName':picUrlInfo['picName'],
                        'tempHigh':tempHigh,'tempLow':tempLow,'wind':windInfo,'wText':wTextInfo}
        weatherInfoList.append(weatherInfoDic)
        '''下载未来4天天气图标'''
        picDownloader(picUrlInfo['picUrl'],picUrlInfo['picName'])

    return weatherInfoList


'''tts'''
def text2voice(text):
    # tex 必填  合成的文本，使用UTF-8编码。小于512个中文字或者英文数字。（文本在百度服务器内转换为GBK后，长度必须小于1024字节）
    # tok 必填  开放平台获取到的开发者access_token（见上面的“鉴权认证机制”段落）
    # cuid必填  用户唯一标识，用来区分用户，计算UV值。建议填写能区分用户的机器 MAC 地址或 IMEI 码，长度为60字符以内
    # ctp 必填  客户端类型选择，web端填写固定值1
    # lan 必填  固定值zh。语言选择,目前只有中英文混合模式，填写固定值zh
    # spd 选填  语速，取值0-9，默认为5中语速
    # pit 选填  音调，取值0-9，默认为5中语调
    # vol 选填  音量，取值0-15，默认为5中音量
    # per 选填  发音人选择, 0为普通女声，1为普通男生，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女声
    url = 'http://tts.baidu.com/text2audio?idx=1&tok=your-token&tex=%s&cuid=baidu_speech_' \
          'demo&cod=2&lan=zh&ctp=1&pdt=1&spd=5&per=0&vol=15&pit=6'%(text)
    print (url)
    # 直接播放语音
    os.system('mplayer "%s"' % url)



'''判断上下午'''
def isam():
    #0-6点是凌晨,6-11.59点是上午12点是中午12-18是下午,18-24是晚上

    # now = time
    import time as tm
    time = tm.localtime()

    if 0<= time.tm_hour <6 :
        return '凌晨'
    elif 6<= time.tm_hour <12:
        return '上午'
    elif time.tm_hour == 12:
        return '中午'
    elif 12 < time.tm_hour <=18:
        return '下午'
    elif 18 < time.tm_hour <24:
        return '晚上'

def numtozh(num):
    num_dict = {1: u'一', 2: u'二', 3: u'三', 4: u'四', 5: u'五', 6: u'六', 7: u'七',
                8: u'八', 9: u'九', 0: u'零'}
    num = int(num)
    if 100 <= num < 1000:
        b_num = num // 100
        s_num = (num-b_num*100) // 10
        g_num = (num-b_num*100) % 10
        if g_num == 0 and s_num == 0:
            num = u'%s百' % (num_dict[b_num])
        elif s_num == 0:
            num = u'%s百%s%s' % (num_dict[b_num], num_dict.get(s_num, ''), num_dict.get(g_num, ''))
        elif g_num == 0:
            num = u'%s百%s十' % (num_dict[b_num], num_dict.get(s_num, ''))
        else:
            num = u'%s百%s十%s' % (num_dict[b_num], num_dict.get(s_num, ''), num_dict.get(g_num, ''))
    elif 10 <= num < 100:
        s_num = num // 10
        g_num = (num-s_num*10) % 10
        if g_num == 0:
            g_num = ''
        num = u'%s十%s' % (num_dict[s_num], num_dict.get(g_num, ''))
    elif 0 <= num < 10:
        g_num = num
        num = u'%s' % (num_dict[g_num])
    elif -10 < num < 0:
        g_num = -num
        num = u'零下%s' % (num_dict[g_num])
    elif -100 < num <= -10:
        num = -num
        s_num = num // 10
        g_num = (num-s_num*10) % 10
        if g_num == 0:
            g_num = ''
        num = u'零下%s十%s' % (num_dict[s_num], num_dict.get(g_num, ''))
    return num


def speakWeather():
    w1 = fetch1weather()    

    date = w1[0]['date']
    dateStr = date.replace(' ',',') #去空格
    dateS = dateStr.replace('廿','二十')#将廿换成二十

    temperature = w1[0]['tempnow']
    temperatureStr = numtozh(temperature)

    pm25Num = w1[0]['pm25']
    pm25Str = numtozh(pm25Num)

    
    wt1 = u'%s好,今天是%s,实时天气为%s,温度为%s摄氏度,PM2.5为%s' % (isam(),dateS,\
        w1[0]['wtext'][0:w1[0]['wtext'].find('(')], temperatureStr , pm25Str)

    # print (wt1)
    text2voice(wt1)
    
if __name__ == "__main__":


    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # helloStr = isam()
    # print ('{}好'.format(helloStr))
    speakWeather()

   
