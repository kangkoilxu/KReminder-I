#coding:utf-8
'''机器需要安装以下模块：
pygame,re,urlib2,beautifulsoup4,xlml,json,time
依赖模块：city.py,fetchnote.py,fetchweather.py'''
import pygame
from pygame.locals import *
from sys import exit
import threading

import fetchweather
import fetchnote
import time
import random


rootSourcePath = '/Users/kang/KReminder'
bgpSourcePath = rootSourcePath + '/Sources/bgp/%s.jpg'
wiconSourcePath = rootSourcePath + '/Sources/wicon/%s'


Linterval = 5


'''屏幕尺寸'''
windowWidth,windowHeight = 480,320
'''pygame '''
#第一步
pygame.init()
#实例化
window = pygame.display.set_mode((windowWidth,windowHeight),0,FULLSCREEN,32)  

def deco(func):
    def wrapper():
        print('/*--------------------------------*/')
        print('开始运行程序:{}'.format(str(func)))
        startTime = time.time()
        func()
        endTime = time.time()
        print('程序结束')
        ms = (endTime - startTime )
        print ('程序运行时间:{}s'.format(ms))
        print('/*--------------------------------*/')
    return wrapper

def deco1(func):
    def wrapper(a):
        print('/*--------------------------------*/')
        print('开始运行程序:{}'.format(str(func)))
        startTime = time.time()
        func(a)
        endTime = time.time()
        print('程序结束')
        ms = (endTime - startTime )
        print ('程序运行时间:{}s'.format(ms))
        print('/*--------------------------------*/')
    return wrapper

'''初始化'''
'''weather fetch'''
w1 = []

@deco
def getWeatherFunc():
    global w1
    w1 = fetchweather.fetch1weather()

def getWeatherThread():
    print (u'天气更新线程工作中...')
    t1 = threading.Thread(target=getWeatherFunc)
    t1.start()
    t1.join()







'''执行一次'''
weatherThreadInterval = 0

'''note'''
noteList = []
@deco1
def getLeanoteFunc(arg):
    global noteList
    noteList = fetchnote.fetchAllNotes(arg)
def getLeanoteThred(arg):
    print(u'云备忘更新线程工作中...')
    '''注意线程传入参数写法'''
    t = threading.Thread(target=getLeanoteFunc,args=(arg,))
    t.start()
    t.join()




'''执行一次'''
loginResults = fetchnote.loginP()
# print ("INFO1:",loginResults)
# getLeanoteThred(loginResults)
LeanoteThreadInterval = 0

'''计时'''
lastsecond = 0
lastsecond1 = 0
lastsecond2 = 0



'''默认壁纸为23'''
picNum = 23




def showBgp(picNum):
    global bgpSourcesPath
    background = pygame.image.load(bgpSourcePath%picNum).convert()
    background = pygame.transform.scale(background,(windowWidth,windowHeight))
    window.blit(background, (0, 0))

def changeBgp():
    global lastsecond2,picNum
    if time.clock() - lastsecond2 >= 30:
        picNum = random.randint(1, 23)
        print (u'现在是壁纸%d'%picNum)
        lastsecond2 = time.clock()
    showBgp(picNum)


def showStr(_window,_fontSize,text,x0,y0,(r,g,b)=(255,255,255),callback=None):
    _font = pygame.font.Font('1.ttf',_fontSize)
    _text_surface = _font.render(text,True,(r,g,b))
    _window.blit(_text_surface,(x0,y0))

def drawCircle(_window,(x0,y0),_radius = 3,_width = 1,(r,g,b)=(255,255,255)):
    pygame.draw.circle(_window,(r,g,b),(x0,y0),_radius,_width)

def createWindow(_size=(120,90),_mode=0,_depth=32):
    return pygame.display.set_mode(_size,_mode,_depth)

'''根据天气代码显示图片,首先尝试在本地代开文件，如果失败，则从网络下载该图片'''
def showWicon(picInfo,pos=(170,80)):
    try:
        wicon1 = pygame.image.load(wiconSourcePath%picInfo['picName']).convert_alpha()
        wicon1 = pygame.transform.scale(wicon1,(50,50))
        window.blit(wicon1,pos)
    except Exception as e:
        print ('function:showWicon():error:',e)
        fetchweather.picDownloader(picInfo['picUrl'],picInfo['picName'])  #download picIcon
        showWicon(picInfo)

'''显示网格，用于调试'''
def debug():
    for x in range(windowWidth / 10):
        pygame.draw.line(window, (205,92,92), (x * 10, 0), (x * 10, windowHeight))
    for y in range(windowHeight/10):
        pygame.draw.line(window,(205,92,92),(0,y*10),(windowWidth,y*10))

    showStr(window, 12, str(event), 0, windowHeight - 14)

def showWInfo(weatherInfo,(posX,poxY)):
    weatherSurface = pygame.Surface((60,215))
    weatherSurface.set_alpha(40)

    window.blit(weatherSurface, (posX, poxY))

    '''星期'''
    showStr(window,20,weatherInfo['week'],posX+12,poxY+0)
    '''日期'''
    showStr(window,16,weatherInfo['date'],posX+0,poxY+30)
    '''天气图标'''
    showWicon(weatherInfo['picInfo'],(posX+5,poxY+60))
    '''温度'''
    showStr(window,15,u'%s ~ %s ℃'%(weatherInfo['tempLow'],weatherInfo['tempHigh']),posX+0,poxY+120)
    '''天气文字'''
    wTextLen = len(weatherInfo['wText'])
    if wTextLen == 1:
        wTextPosx = 20
    elif wTextLen == 2:
        wTextPosx = 13
    else:
        wTextPosx = 20-wTextLen*2
    showStr(window, 20, weatherInfo['wText'], posX + wTextPosx, poxY + 150)

    '''风向'''
    showStr(window,14,weatherInfo['wind'],posX+3,poxY+180)



'''显示云笔记'''
def showCloudNotes(notelist):
    bsurface = pygame.Surface((190, 215))#, flags=255, depth=32)
    bsurface.set_alpha(40)

    '''画分隔线'''
    for i in range(1, 8):
        pygame.draw.line(bsurface, (255, 255, 255), (0, 30 * i), (190, 30 * i))

    '''文字写在window上画，因为在bsurface上的文字也会带有透明度'''
    notecnt = 0;
    # for note in notelist:
    #     showStr(window,14,note[:18],12,85+notecnt*22)
    #     notecnt += 1
    window.blit(bsurface,(5,100))

    '''小屏幕最多显示7条笔记'''
    try:
        for i in range(10):
            showStr(window,20,noteList[i][:20],12,105+i*30)
    except Exception,e:
        # print (e)
        showStr(window,16,u'云备忘更新中...',12,100)
'''主循环'''
while True:
    '''限制帧率'''
    clock = pygame.time.Clock()
    clock.tick(30)
    '''事件处理'''
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN:
            exit()

    '''每隔10分钟获取天气信息'''
    if time.clock() - lastsecond >= weatherThreadInterval:
        weatherThreadInterval = 600 #10min
        getWeatherThread()
        lastsecond = time.clock()


    '''定期获取笔记'''
    if time.clock() - lastsecond1 >= LeanoteThreadInterval:
        LeanoteThreadInterval = Linterval
        getLeanoteThred(loginResults)
        lastsecond1 = time.clock()


    '''自动换壁纸'''
    changeBgp()

    '''显示今日实时天气信息'''
    topSurface = pygame.Surface((windowWidth-10,90))
    topSurface.set_alpha(40)

    window.blit(topSurface,(5,5))
    #
    # '''显示天气图标'''
    showWicon(w1[0]['picInfo'],(windowWidth-140,10))
    #
    '''显示时间，日期'''
    timestamp = time.localtime()
    timeText =  '%.2d:%.2d'%(timestamp.tm_hour,timestamp.tm_min)
    dateText = '%d/%.2d/%.2d'%(timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday)
    showStr(window,56,timeText,5,5,(255,255,255))
    showStr(window,24,dateText,12,68)

    '''当期温度,及温度符号'''
    showStr(window,48,w1[0]['tempnow'],windowWidth-80,10)
    drawCircle(window, (windowWidth-30, 15), _radius=5, _width=3)

    '''风向，pm2.5显示'''
    windText = w1[0]['wind']
    windTextLen = windText.__len__()
    windTextFontSizeWidth = 14
    windTextStartPosX = windowWidth-(windTextLen+2)*windTextFontSizeWidth
    showStr(window,20,w1[0]['wind'],windTextStartPosX,68)

    pm25Text = 'pm2.5:%s' % (w1[0]['pm25'])
    pm25TextLen = pm25Text.__len__()
    pm25TextFontSizeWidth = 10
    pm25TextStartPosX = windTextStartPosX - (pm25TextLen+2)*pm25TextFontSizeWidth
    showStr(window, 24, pm25Text,pm25TextStartPosX, 68)

    '''显示预报天气'''
    for i in range(1,5):
        weatherInfo = w1[i]
        showWInfo(weatherInfo,(205+(i-1)*70,100))

    '''cloud note book'''
    showCloudNotes(noteList)

    '''debug '''
    # debug()

    pygame.display.update()

