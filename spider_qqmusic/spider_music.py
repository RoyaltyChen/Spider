# -*- coding:utf-8 -*-

import json
import requests
from lxml import etree
from urllib import parse
import os 
import re

'''
1.爬取操作
获取歌曲songmid参数

发现排行榜首页,源码不包含歌曲列表元素，即动态加载生成。
https://y.qq.com/n/yqq/toplist/27.html#stat=y_new.toplist.menu.27

对比每个page的链接,发现参数song_begin、song_num会发生规律性变化。
https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date=2018-10-25&topid=27&type=top&song_begin=0&song_num=100&g_tk=625809127&loginUin=849625804&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0

此程序为了方便操作，直接将song_num设置为100，即获取新歌排行榜所有歌曲数目。
2.构造音乐参数链接 
https://u.y.qq.com/cgi-bin/musicu.fcg?
callback=getplaysongvkey586825165521649  #  可以删除
&g_tk=625809127
&jsonpCallback=getplaysongvkey586825165521649  #  可以删除
&loginUin=849625804
&hostUin=0
&format=jsonp
&inCharset=utf8
&outCharset=utf-8
&notice=0
&platform=yqq
&needNewCode=0
&data={
"req_0":{
"module":"vkey.GetVkeyServer",
"method":"CgiGetVkey",
"param":{
    "guid":"1500674286",
    "songmid":["004R2ZVY1Xt5oN"], # 每个音乐文件对应各自的songmid
    "songtype":[0],
    "uin":"849625804",
    "loginflag":1,
    "platform":"20"
    }
},
"comm":{
    "uin":849625804,
    "format":"json",
    "ct":20,
    "cv":0
    }
}
3.构造音乐资源链接
4.获取音乐资源并保存。

'''


def get_song_pages(url):
    #获取page
    pass

def get_song_list_each_page(url,header):
    # 获取每一页歌曲列表
    response = requests.get(url=url_song_list,headers=headers)
    r = response.content.decode('utf-8')
    # 1.获取songmid、歌曲名称、歌手信息
    songs = json.loads(r)['songlist']
    song_list = []
    for song in songs:
        song_ = {}
        song_id = song['data']['songmid']
        song_['mid'] = song_id
        song_name = song['data']['songname']
        song_['name'] = song_name
        song_singer = song['data']['singer'][0]['name']
        song_['singer'] = song_singer
        song_list.append(song_)
    return song_list

def generate_song_param_url(song_list): 
    '''
    2.构造音乐参数链接
    '''
    url_song_param ='https://u.y.qq.com/cgi-bin/musicu.fcg?g_tk=625809127&loginUin=849625804&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&'
    data={"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"1500674286","songmid":["004R2ZVY1Xt5oN"],"songtype":[0],"uin":"849625804","loginflag":1,"platform":"20"}},"comm":{"uin":849625804,"format":"json","ct":20,"cv":0}}
    # 注意data字典双引号问题以及是否包含多余的空格，如若不然导致HTML编码不符合原网页要求。
    for song in song_list:
        data['req_0']['param']['songmid'] = [song['mid']]
        url_param = url_song_param + 'data=' +parse.quote(str(data).replace(' ','').replace('\'','\"'))
        song['paramurl'] = url_param
    return song_list

def generate_song_source_url(song_list):
    '''
    3.构造音乐资源链接
    '''
    for song in song_list:
        res = requests.get(song['paramurl'],headers=headers)
        data = res.content.decode('utf-8')
        data = json.loads(data)
        file = data['req_0']['data']['midurlinfo'][0]['filename']
        purl = data['req_0']['data']['midurlinfo'][0]['purl']
        sip = data['req_0']['data']['sip']
        song['filename'] = file
        song['sourceurl'] = purl
        song['sip'] = sip
    return song_list

def save_song(song_list):
    '''
    4.获取音乐资源并保存
    -- 创建music目录,用来保存歌曲文件
    '''
    cwd = os.getcwd()
    music_dir = cwd + '\\music'
    if (not os.path.exists(music_dir)) or (not os.path.isdir(music_dir)):
        os.mkdir(music_dir)
    print('歌曲保存中。。。')
    for song in song_list:
        r = requests.get(song['sip'][0]+song['sourceurl'],headers=headers) 
        song_dir = music_dir + '\\'+ re.sub(r'\:*\?*','',song['name']).replace('  ',' ')
        if (not os.path.exists(song_dir)) or (not os.path.isdir(song_dir)):
            os.mkdir(song_dir)
        f = open(song_dir + '\\'+song['name'] + '.m4a','wb')
        f.write(r.content)
        print('歌曲"%s"保存成功！'% song['name'])
        f.close()
    print('歌曲全部保存完毕！') 

if __name__ == '__main__':
    '''
     - 发现页面(https://y.qq.com/n/yqq/toplist/27.html#stat=y_new.toplist.menu.27)源码不包含歌曲列表元素，即动态加载生成。 
     - 对比每个page的链接，发现参数song_begin、song_num会发生规律性变化。
     - 此程序直接将song_num设置为100，即获取新歌排行榜所有歌曲数目。  
    '''
    #url地址
    url_song_list = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date=2018-10-25&topid=27&type=top&song_begin=0&song_num=100&g_tk=625809127&loginUin=849625804&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
    #添加请求头
    headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    song_list = get_song_list_each_page(url_song_list,headers)
    song_list = generate_song_param_url(song_list)
    song_list = generate_song_source_url(song_list)
    save_song(song_list)