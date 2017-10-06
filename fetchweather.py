#coding=utf-8
import urllib2
from bs4 import BeautifulSoup
from city import citycode
import time
import re
import urllib

picFilePath = '/Users/kang/KReminder/Sources/wicon/%s' #



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

'''从中国气象局获取7天天气预报，但其天气图标非png无法使用，故此函数为使用'''
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


'''从百度搜索天气页面中获取天气信息，包含实时天气和未来4天的天气预报'''
def fetch1weather():
    '''百度搜索天气信息返回页面不需要js处理即可显示实时天气信息，其他网站实时天气信息均需要实时js处理，所以使用此方法'''
    '''改进措施：处理其他天气网站的js'''
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

    #fetch4daysWeatherInfo
    '''中国天气网的天气图标是png，没法用，所有只能舍弃7天预报，转而使用百度搜索天气结果中的信息，后期需做大量的改进'''
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
        except Exception,e:
            pass
        windInfo = weather4Info.find(class_='op_weather4_twoicon_wind').getText().strip()
        weatherInfoDic ={'week':weekInfo,'date':dateInfo,'picInfo':picUrlInfo,'picUrl':picUrlInfo['picUrl'],'picName':picUrlInfo['picName'],
                        'tempHigh':tempHigh,'tempLow':tempLow,'wind':windInfo,'wText':wTextInfo}
        weatherInfoList.append(weatherInfoDic)
        '''下载未来4天天气图标'''
        picDownloader(picUrlInfo['picUrl'],picUrlInfo['picName'])

    return weatherInfoList



'''判断上下午'''
def isam(time):
    now = time
    if time.tm_hour<12 :
        return True
    else:
        return False

if __name__ == "__main__":

    timenow = time.localtime()
    isam = isam(timenow)
    w1 = fetch1weather()
    if isam :
        text = u'上'
    else :
        text = u'下'
    wt1 = u'%s午好，现在的实时天气为%s,温度为%s摄氏度，PM2.5为%s。' % (text,w1[0]['wtext'][0:w1[0]['wtext'].find('(')],w1[0]['tempnow'],w1[0]['pm25'])
    tm = w1[0]['date']
    print tm
    print wt1
    print w1[0]['sg']
    # text2voice(wt1)
