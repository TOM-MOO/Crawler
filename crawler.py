# encoding=utf-8
import requests
import time

wp_path = 'C:/Users/Tom/Desktop/%s'  # 保存待观看的路径
db_path = 'D:/ProgramData/PyCharmProjects/crawler/%s'  # 数据库(文件)路径

up_url = 'https://api.bilibili.com/x/space/arc/search?mid=%s&ps=%d'  # UP主视频. mid为用户ID, ps为返回视频数
pop_url = 'https://api.bilibili.com/x/web-interface/popular?pn=%d'  # 综合热门. pn为页数(每页20条视频)
rank_url = 'https://api.bilibili.com/x/web-interface/ranking?rid=%d'  # 排行榜. rid为分区ID

link_pt = '<a href="https://www.bilibili.com/video/%s">%s: %s</a>\n'  # 链接原型

videos = 3
All = [0, 3, 36, 188]  # 0总站 3音乐 36知识 188数码

new = []  # 待更新
todo = []  # 待观看


# 不要嵌套with语句，否则使用计划任务时总是出现一些莫名奇妙的异常
def read(file):
    with open(file, 'r', encoding='utf-8') as f:
        return f.readlines()


def append(bvid, author, title, db):
    link = link_pt % (bvid, author, title)
    new.append(link)
    if link not in db:  # 将新增或修改的视频加入待观看
        todo.append(link + '<br>\n')


def write(todo_file, new_file):
    if todo:  # 仅在有新增或修改视频时才更新数据库和待观看
        with open(todo_file, 'w', encoding='utf-8') as f:
            f.writelines(todo)
        with open(new_file, 'w', encoding='utf-8') as f:
            f.writelines(new)


ups = read(db_path % 'ups')
hot = read(db_path % 'hot')

with open(db_path % 'uid', 'r', encoding='utf-8') as u:
    for uid in u:
        r = requests.get(up_url % (uid.split()[1], videos))
        # r.encoding = 'utf-8'
        vlist = r.json()['data']['list']['vlist']
        for v in vlist:
            append(v['bvid'], v['author'], v['title'], ups)

write(wp_path % ('UPS_%d.html' % int(time.time())), db_path % 'ups')
# 清除前一条爬虫残留数据
todo.clear()
new.clear()

for i in range(0, 12):  # 不止10页???与网页不同???
    r = requests.get(pop_url % (i + 1))
    vlist = r.json()['data']['list']
    for v in vlist:
        append(v['bvid'], v['owner']['name'], v['title'], hot)

for a in All:
    r = requests.get(rank_url % a)
    vlist = r.json()['data']['list']
    for v in vlist:
        append(v['bvid'], v['author'], v['title'], hot)

# 简单去重
new = set(new)
todo = set(todo)

write(wp_path % ('HOT_%d.html' % int(time.time())), db_path % 'hot')

with open(wp_path % ('TOP_%d.html' % int(time.time())), 'w', encoding='utf-8') as t:
    t.writelines('<a href="https://s.weibo.com/top/summary">WEIBO</a>\n<br>\n'
                 '<a href="https://www.zhihu.com/hot?list=digital">ZHIHU</a>\n')
