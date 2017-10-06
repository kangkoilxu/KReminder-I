#coding:utf-8
import urllib2
import json
'''测试'''
import time

'''无参数loogin'''
# @deco
def loginP():
    # global  usr
    usr={}
    usr['user'] = 'your-leanote-account-name'
    usr['pass'] = 'password'
    res = login(usr)
    res['user'] = usr['user']
    res['pass'] = usr['pass']
    
    return res

def htmldownloader(url):
    open = urllib2.Request(url,headers={'User-Agent': 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'})
    page = urllib2.urlopen(open)
    return page


def login(usr={}):
    # print ('INFO3:',usr)
    user = usr['user'].replace('@', '%40')
    pas =  usr['pass']

    url = 'https://www.leanote.com/api/auth/login?email=%s&pwd=%s' % (user, pas)
    page = htmldownloader(url)
    res = json.load(page)
    # print res
    '''登录成功会返回token,ok失败则返回msg,ok'''
    usr_default ={}
    usr_default['ok'] = res['Ok']

    if res['Ok'] == False:
        print ('Ok = false')
        usr_default['token'] = 0
        usr_default['msg'] = res['Msg']
        # return usr_default
    else:
        # print('ok != false')
        usr_default['token'] = res['Token']
        usr_default['msg'] = b''

    # print (usr_default['msg'],usr_default['ok'],usr_default['token'])
    return usr_default

def logout(usr={}):
    token = usr['token']
    url = 'https://leanote.com/auth/logout?token=%s' % token
    page = htmldownloader(url)
    # res = json.load(page)
    # return {'Ok':res['Ok'],'msg':res['Msg']}


def getnotebook(usr={}):

    notebooklist = []
    token = usr['token']
    url = 'http://leanote.com/api/notebook/getNotebooks?token=%s' % token
    page = htmldownloader(url)
    res = json.load(page)
    '''如果token失效，则会返回{u'Msg': u'NOTLOGIN', u'Ok': False},成功则返回List'''
    '''只要检测到notlogin，则重新登录以获取新token'''

    print type(res)
    if isinstance(res,dict):
        if res.has_key('Ok'):
            if res['Ok'] == False:
                res = loginP()
                '''回调'''
                print (u'获取笔记失败，重新登录')
                time.sleep(1)
                getnotebook(res)

    for notbook in res:
        notebookinfo ={}
        # print notbook
        notebookinfo['NotebookId'] = notbook['NotebookId']
        notebookinfo['Title'] = notbook['Title']
        notebookinfo['num'] = notbook['Usn']
        notebooklist.append(notebookinfo)

    return notebooklist

def getnotes(usr={},notebookinfo={}):
    notelist=[]
    token = usr['token']
    notebookid = notebookinfo['NotebookId']
    url = 'https://leanote.com/api/note/getNotes?token=%s&notebookId=%s' % (token,notebookid)
    page = htmldownloader(url)
    allnotes = json.load(page)
    # print 'allnotes', allnotes

    for note in allnotes:
        notedic={}
        notedic['noteId'] = note['NoteId']
        notedic['Title'] = note['Title']
        notedic['content'] =note['Content']
        notelist.append(notedic)
    return notelist

def getnotesandcontent(usr={},notedic={}):

    token = usr['token']
    url = 'https://leanote.com/api/note/getNoteContent?token=%s&noteId=%s' % (token,notedic['noteId'])
    page = htmldownloader(url)
    res = json.load(page)
    # print 'INFO4:',res
    return res['Content']


'''去除笔记中<>，&nbsp，等符号'''
def parseNote(notestr):
    # str1 = notestr.strip()
    # indexl = 0
    # try:
    #     indexl = str1.index('>')
    # except:
    #     pass
    # try:
    #     indexr = str1.index('&nbsp;', indexl)
    # except ValueError:
    #     try:
    #         indexr = str1.index('<', indexl)
    #     except:
    #         indexr = 0
    # str1 = str1[indexl + 1:indexr]
    # return str1
    pass


getnotebookOk = False
notebooklist = []

def fetchAllNotes(res={}):


    global getnotebookOk,notebooklist
    text = ''
    notebookcnt = 0
    allnotescnt = 0
    # res = login(usr)
    # print res
    if res['ok'] == True:

        if res['token'] == 0:
            return

        _allNoteList=[]
        '''全局变量usr包含了登录信息'''
        if  not getnotebookOk :
            notebooklist = getnotebook(res)
            getnotebookOk = True



        # notebook: work
        noteb = notebooklist[3]

        notes = getnotes(res,noteb)

        # print ('------------开始输出notes----------------')
        # cnt = 0
        # for item in notes:
        #     print(cnt,notes)
        #     cnt += 1


        notebookcnt += 1 #计算笔记本数量
        notecnt = 0
        text1 = ''
        for note in notes:
            # print('notes:',note)
            notecnt += 1 #计算某笔记本下笔记数量
            allnotescnt += 1
            # content = parseNote(getnotesandcontent(res, note))
            # content = getnotesandcontent(res, note)
            # _allNoteList.append(content)
            _allNoteList.append(note['Title'])#只显示标题
        #     text1 += u'第%d条笔记标题为%s，内容为%s。' % (notecnt,note['Title'],u'。。。')#content['content'])
        # text += u'第%d个笔记本为%s，下面有%d条笔记,%s' % (notebookcnt,noteb['Title'],notecnt,text1)


        # text2 = u'您共有%d个笔记本，%s' % (notebookcnt,text)
        # # print text2
        # text3 = u'您共有%d条笔记！' % allnotescnt
        # print text3
        # logout(res) #登出

        '''将所有笔记列表返回'''
    
        return _allNoteList
    else:

        print('登录失败！')
        return

if __name__ == "__main__":

    '''测试token有效期'''
    lastsecond = 0

    '''开机获取一次获得token'''
    res = loginP()


    while True:
        if res['ok'] == True:
            if(time.clock() - lastsecond >= 10):

                list = fetchAllNotes(res)
                for item in list:
                    print item
                lastsecond = time.clock()

        else:
            pass