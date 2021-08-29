# -*- coding:utf-8 -*-  
import socket
import tkinter as tk
from email.header import Header
from ftplib import FTP
import time,tarfile,os
import time
import tkinter.filedialog
from tkinter.filedialog import *
from tkinter import scrolledtext
import threading
import os
from tkinter import *
import tkinter.font
import cv2
from time import sleep
import numpy as np
import struct
import PIL
from PIL import ImageGrab
from PIL import Image,ImageTk
from tkinter import StringVar, IntVar
import tkinter.font
import urllib.request
import gzip
import json
import requests
import urllib.parse
from tkinter import END
from PyQt5.Qt import *
from tkinter.messagebox import * 
from traceback import print_tb 

import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from 邮件窗口 import *
# -*- coding: utf-8 -*-
#界面
def chatClient(serversocket):
    data=text.get("0.0", "end")[:-1]
    def Get_File(filename):
        fpath,tempfilename=os.path.split(filename)
        fname,extension=os.path.splitext(tempfilename)
        return fpath,fname,extension
    fpath,fname,extension=Get_File(data)
    if str(extension) in ('.py','.txt','.doc'):
        f=open(data,'rb')
        data2=f.read(1024)
        data3=data2.decode('utf-8')
        if str(data2)!="b''":
            serversocket.send(("file"+","+str(data3)).encode("utf-8"))
            listbox.insert(tk.INSERT,'系统提醒：文件' + fname + '已发送\n','red')
            listbox.see(END)
            text.delete('0.0','end')
        else:
            serversocket.send('end'.encode("utf-8"))
    elif str(extension) in ('.png','.jpg','gif'):
        serversocket.send(("photo"+","+str(data)).encode("utf-8"))
        img = cv2.imread(data)
        img_encode = cv2.imencode('.png', img)[1]
        data_encode = np.array(img_encode)
        str_encode=data_encode.tostring()
        data = str_encode
        fhead=struct.pack('l',len(data))
        print('开始发送文件头')
        serversocket.send(fhead)
        print('开始发送图片数据')
        if str(data)!="b''":
            for i in range(len(data)//1024+1):
                if 1024*(i+1)>len(data):
                    serversocket.send(data[1024*i:])
                    print('第'+str(i)+'次发送数据')
                else:
                    serversocket.send(data[1024*i:1024*(i+1)])
                    print('第'+str(i)+'次发送数据')
            listbox.insert(tk.INSERT,'系统提醒：图片' + fname + '已发送\n','red')
            listbox.see(END)
            text.delete('0.0','end')
        else:
            serversocket.send('end'.encode("utf-8"))
    elif str(extension) in ('.mp4', '.avi'):
        print("视频")
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        listbox['state'] = NORMAL
        listbox.insert(INSERT, "客户端({})：\n成功发送视频{}!\n".format(now, fname + extension))
        listbox['state'] = DISABLED
        text.delete("0.0", "end")
        listbox.see(END)
        cap = cv2.VideoCapture(r"{}".format(data))
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        serversocket.sendto(("vedio" + "," + "{}".format(fname + extension) + "," + str(size[0]) + "," + str(size[1])).encode(),("127.0.0.1", 8000))
        while True:
            flag, img = cap.read()  # 返回两个值，第一个flag=True,False;img每次读到的图片
            if flag == True:
                time.sleep(0.01)
                img_encode = cv2.imencode('.jpg', img)[1]
                data_encode = np.array(img_encode)
                data = data_encode.tobytes()
                # 定义文件头
                fhead = struct.pack('l', len(data))
                # 发送文件头、数据:
                serversocket.sendto(fhead, ('127.0.0.1', 8000))
                for i in range(len(data) // 1024 + 1):
                    if 1024 * (i + 1) > len(data):
                        serversocket.sendto(data[1024 * i:], ('127.0.0.1', 8000))
                    else:
                        serversocket.sendto(data[1024 * i:1024 * (i + 1)], ('127.0.0.1', 8000))
                    print('第' + str(i) + '次发送数据')
            else:
                serversocket.sendto('END'.encode('utf-8'), ('127.0.0.1', 8000))
                break

    else:    
        serversocket.send(data.encode('utf-8'))
        data = data.rstrip()
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        listbox.insert(tk.INSERT,'服务器 ' + theTime +' 说：\n')
        listbox.insert(tk.INSERT,'  ' + data + '\n')
        listbox.see(END)
        text.delete('0.0','end')
def receivedata(serversocket):

    while True:
        data = serversocket.recv(1024)
        receive=(data.decode("utf-8")).split(',')
        print(data)
        print(receive)
        if receive[0]=='file':
            filename='server.txt'
            f=open(filename,'wb')
            if str(receive[1].encode('utf-8'))!="b'end'":
                f.write(receive[1].encode('utf-8'))
                f.close()
                listbox.insert(tk.INSERT,'系统提醒：客户端发来的文件已另存为' + filename + '\n','red')
                listbox.see(END)
            else:
                continue
        elif receive[0]=='photo':
            if str(receive[1].encode('utf-8'))!="b'end'":
                print('开始接收图片')
                fhead_size=struct.calcsize('l')
                buf=serversocket.recv(fhead_size)
                if buf:
                    data_size=struct.unpack('l',buf)[0]
                    print('图片数据大小为'+str(data_size))
                recvd_size=0
                data_total=b''
                j=0
                while not recvd_size == data_size:
                    if data_size -recvd_size >1024:
                        data = serversocket.recv(1024)
                        recvd_size += len(data)
        
                    else:
                        data= serversocket.recv(1024)
                        recvd_size = data_size
        
                    data_total += data
                    print('第'+str(j)+'次收到数据')
                    j=j+1
                nparr = np.frombuffer(data_total, np.uint8)
                img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imwrite('server.png',img_decode)
                jieshou= tk.PhotoImage(file='./server.png')
                listbox.insert(tk.INSERT,'系统提醒：客户端发来的图片已另存为server.png \n','red')
                listbox.image_create(tk.INSERT,image=jieshou)
                listbox.insert(END,'\n')
                listbox.see(END)
                cv2.waitKey()
                cv2.destroyAllWindows()    
            else:
                continue
        elif receive[0] == 'vedio':
            print("视频")
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            listbox['state'] = NORMAL
            listbox.insert(tk.INSERT, "服务端（{}）：\n正在接收视频{}...\n".format(now, receive[1]))
            listbox['state'] = DISABLED
            listbox.see(END)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            size = (int(receive[2]), int(receive[3]))
            out = cv2.VideoWriter(r'发送视频/{}'.format(receive[1]), fourcc, 10.0, size)
            while 1:
                receive, addr = serversocket.recvfrom(1024)
                if str(receive) == "b'END'":
                    break
                else:
                    if len(receive) == 4:
                        print(receive)
                        data_size = struct.unpack('l', receive)[0]
                        print('图片数据大小为' + str(data_size))
                        recvd_size = 0
                        data_total = b''
                    while not recvd_size == data_size:
                        if data_size - recvd_size > 1024:
                            data, addr = serversocket.recvfrom(1024)
                            recvd_size += len(data)
                        else:
                            data, addr = serversocket.recvfrom(1024)
                            recvd_size = data_size
                        data_total += data
                    print('Received')
                    nparr = np.frombuffer(data_total, np.uint8)
                    img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    out.write(img_decode)
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            listbox['state'] = NORMAL
            listbox.insert(INSERT, "服务端（{}）：\n成功保存视频{}\n".format(now, data[1]))
            listbox['state'] = DISABLED
            listbox.see(END)
        elif receive[0]=='emoji':
            print(receive)
            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            listbox.insert(END, '客户端 ' + theTime +' 说：\n')
            listbox.image_create(END,image=receive[1].encode('utf-8'))
            listbox.insert(END,'\n')
            listbox.see(END)
        else:
            data = data.rstrip()
            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            listbox.insert(tk.INSERT, '客户端 ' + theTime +' 说：\n')
            listbox.insert(tk.INSERT,'  ' + data.decode('utf-8') + '\n')
            listbox.see(END)
def leave(serversocket):
    root.destroy()
def openfile(serversocket):
    text.delete('0.0','end')
    r=askopenfilename(title='打开文件')
    fp=open(r,'r',encoding="utf-8")
    filename=r
    text.insert(tk.INSERT,r)
    fp.close()
def openpic(serversocket):
    text.delete('0.0','end')
    r=askopenfilename(title='打开图片',filetypes=[('图像文件','*.jpg *.png *.gif')])
    fp=open(r,'rb')
    filename=r
    text.insert(tk.INSERT,r)
    fp.close()



# 截屏函数如下所示
class MyCapture:
    def __init__(self, png):
        # 变量X和Y用来记录鼠标左键按下的位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)
        # 屏幕尺寸
        screenWidth = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()
        # 创建顶级组件容器
        self.top = tkinter.Toplevel(root, width=screenWidth, height=screenHeight)
        # 不显示最大化、最小化按钮
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top, bg='white', width=screenWidth, height=screenHeight)
        # 显示全屏截图，在全屏截图上进行区域截图
        self.image = tkinter.PhotoImage(file=png)
        self.canvas.create_image(screenWidth/2, screenHeight/2, image=self.image)
        self.sel = None

        # 鼠标左键按下的位置

        def onLeftButtonDown(event):
            self.X.set(event.x)
            self.Y.set(event.y)
            # 开始截图
            self.sel = True

        self.canvas.bind('<Button-1>', onLeftButtonDown)

        # 鼠标左键移动，显示选取的区域
        def onLeftButtonMove(event):
            if not self.sel:
                return
            global lastDraw
            try:
                # 删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
                self.canvas.delete(lastDraw)
            except Exception as e:
                print(e)
            lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='black')

        self.canvas.bind('<B1-Motion>', onLeftButtonMove)

        # 获取鼠标左键抬起的位置，保存区域截图
        def onLeftButtonUp(event):
            self.sel = False
            try:
                self.canvas.delete(lastDraw)
            except Exception as e:
                print(e)
            sleep(0.1)
            # 考虑鼠标左键从右下方按下而从左上方抬起的截图
            left, right = sorted([self.X.get(), event.x])
            top, bottom = sorted([self.Y.get(), event.y])
            pic = ImageGrab.grab((left + 1, top + 1, right, bottom))
            # 弹出保存截图对话框
            fileName = tkinter.filedialog.asksaveasfilename(title='Save screenshot',
                                                            filetypes=[('image', '*.jpg *.png')])
            if fileName:
                pic.save(fileName+'.jpg')
            # 关闭当前窗口
            self.top.destroy()

        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
        # 让canvas充满窗口，并随窗口自动适应大小
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)


# 开始截图
def buttonCaptureClick(serversocket):
    # 最小化主窗口
    #root.state('icon')
    #sleep(0.2)
    filename = 'temp.png'
    # grab()方法默认对全屏幕进行截图
    im = ImageGrab.grab()
    im.save(filename)
    im.close()
    # 显示全屏幕截图
    w = MyCapture(filename)
    b5.wait_window(w.top)
    # 截图结束，恢复主窗口，并删除临时的全屏幕截图文件
    root.state('normal')
    os.remove(filename)


# 发送表情图标记的函数, 在按钮点击事件中调用


def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    serversocket.send(("emoji"+","+str(exp)).encode("utf-8"))
    theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
    listbox.insert(END, '服务器 ' + theTime +' 说：\n')
    listbox.image_create(END,image=exp)
    listbox.insert(END,'\n')
    listbox.see(END)
    emoji1.destroy()
    emoji2.destroy()
    emoji3.destroy()
    emoji4.destroy()
    ee = 0


# 四个对应的函数
def bb1():
    mark(p1)


def bb2():
    mark(p2)


def bb3():
    mark(p3)


def bb4():
    mark(p4)


def express(serversocket):
    global emoji1, emoji2, emoji3, emoji4, ee
    if ee == 0:
        ee = 1
        emoji1 = tk.Button(root, command=bb1, image=p1,
                            relief=tk.FLAT, bd=0)
        emoji2 = tk.Button(root, command=bb2, image=p2,
                            relief=tk.FLAT, bd=0)
        emoji3 = tk.Button(root, command=bb3, image=p3,
                            relief=tk.FLAT, bd=0)
        emoji4 = tk.Button(root, command=bb4, image=p4,
                            relief=tk.FLAT, bd=0)

        emoji1.place(x=5, y=248)
        emoji2.place(x=75, y=248)
        emoji3.place(x=145, y=248)
        emoji4.place(x=215, y=248)
    else:
        ee = 0
        emoji1.destroy()
        emoji2.destroy()
        emoji3.destroy()
        emoji4.destroy()

def on_enter(event):
    #Lab2.configure(text="Hello world")
    city_name = city.get()#获取输入框的内容
    url1 = 'http://wthrcdn.etouch.cn/weather_mini?city='+urllib.parse.quote(city_name)
    weather_data = urllib.request.urlopen(url1).read()
    #读取网页数据
    weather_data = gzip.decompress(weather_data).decode('utf-8')
    #解压网页数据
    weather_dict = json.loads(weather_data)
    #将json数据转换为dict数据
    if weather_dict.get('desc') == 'invilad-citykey':
        weather.insert(END,'你输入的城市名有误，或者天气中心未收录你所在城市')
    elif weather_dict.get('desc') =='OK':
        forecast = weather_dict.get('data').get('forecast')#获取数据块
        #设置日期列表
        weather.insert(END,'今天的'+weather_dict.get('data').get('city')+'天气'+forecast[0].get('type')+'，温度是'+weather_dict.get('data').get('wendu')+'℃ '+'\n')
        weather.insert(END,forecast[0].get('high')+'\n')
        weather.insert(END,forecast[0].get('low')+'\n')
        weather.insert(END,'温馨提示：'+weather_dict.get('data').get('ganmao')+'\n')


def on_leave(enter):
    weather.delete('0.0','end')
def button_down(event):
    Lab2.configure(text="")
    start.set(listbox.index('@%s,%s' % (event.x, event.y)))
    text.insert(END,start.get()+',','white')
    
def button_up(event):
    end.set(listbox.index('@%s,%s' % (event.x, event.y)))
    text.insert(END,end.get()+'\n','white')
    zuobiao1=text.get("0.0", "end")
    zuobiao2=zuobiao1.split(',')
    tou=zuobiao2[0]
    wei=zuobiao2[1]
    text.delete('0.0','end')
    url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
    data = {}
    data['i']= listbox.get(tou, wei)
    data['from']= 'AUTO'
    data['to']= 'AUTO'
    data['smartresult']= 'dict'
    data['client']= 'fanyideskweb'
    data['salt']= '15476224241590'
    data['sign']= '483fc67fc2bc252fcf81147f1ab6b3ed'
    data['ts']= '1547622424159'
    data['bv']= '87d648e10a4c1b783bfbb388b232ba69'
    data['doctype']= 'json'
    data['version']= '2.1'
    data['keyfrom']= 'fanyi.web'
    data['action']= 'FY_BY_REALTIME'
    data['typoResult']= 'false'
    data = urllib.parse.urlencode(data).encode("utf-8")
    response = urllib.request.urlopen(url, data)
    html = response.read().decode("utf-8")
    page = json.loads(html)

    Lab2.configure(text=page['translateResult'][0][0]['tgt'])
def Email():
    if __name__ == '__main__':
        wind = EmailSend()
        pass

def mail():
    root1 = tk.Tk()
    root1.title('邮箱')

    def fsh():

        def filea(fp):
            # print(data)
            fpath, tempfilename = os.path.split(fp)
            fn, extension = os.path.splitext(tempfilename)
            return fpath, fn, str(extension)

        fyj = entryfy.get()  # 发送者邮箱
        print(fyj)
        frj = entryfr.get()  # 发件人
        print(frj)
        yzj = entryyz.get()  # 邮箱主题
        print(yzj)
        yfj = entryyf.get()  # 邮箱服务地址
        print(yfj)
        sqj = entrysq.get()  # 授权码
        print(sqj)
        syj = entrysy.get()  # 收件者邮箱
        print(syj)
        fjj = entryfj.get(0.0, END)  # 附件
        print(fjj)
        ynj = entryyn.get(0.0, END)  # 邮件内容
        print(ynj)

        mail1 = MIMEText(ynj)
        # fjj1=fjj
        image_list = fjj.split('\n')
        print(1)
        print(image_list)
        h = 0
        a = len(image_list)
        print(a)
        mail = MIMEMultipart()
        mail.attach(mail1)
        while h < a - 2:
            image_list1 = image_list[h].strip('.').split('.')
            print(image_list[h])
            print(image_list1)
            print(image_list1[1])
            f, fn, ex = filea(image_list[h])
            if image_list1[1] == "jpg":
                print(1)
                imageFile = str(image_list[h])
                imageApart = MIMEApplication(open(imageFile, 'rb').read(), imageFile.split('.')[-1])
                imageApart.add_header('Content-Disposition', 'attachment', filename=fn + ex)
                mail.attach(imageApart)
            else:
                print(2)
                print(image_list[h])
                textFile = image_list[h]
                textApart = MIMEApplication(open(textFile, 'rb').read())
                textApart.add_header('Content-Disposition', 'attachment', filename=fn + ex)
                mail.attach(textApart)
            h = h + 1

        mail['Subject'] = Header(yzj, 'utf-8')  # 邮箱主题
        mail['From'] = Header(frj, 'utf-8')  # 发件人
        mail['To'] = syj  # 收件人

        smtp = smtplib.SMTP(yfj, port=25)  # 连接邮箱服务器，smtp的端口号是25
        smtp.login(fyj, sqj)  # 登录邮箱
        smtp.sendmail(fyj, syj, mail.as_string())  # 参数分别是发送者，接收者，第三个是把上面的发送邮件的内容变成字符串
        smtp.quit()  # 发送完毕后退出smtp
        showinfo("提示", "发送成功！")

    def dkh():
        r = askopenfilename(title='打开文件')
        print(r)
        f1 = open(r, 'r', encoding='utf-8')
        entryfj.insert(INSERT, '{}\n'.format(r))  # 大写INSERT为在当前光标写入
        f1.close()

    def qxh():
        root1.destroy()

    fy = tk.Label(root1, text='发送者邮箱')
    fr = tk.Label(root1, text='发件人')
    yz = tk.Label(root1, text='邮箱主题')
    yf = tk.Label(root1, text='邮箱服务地址')
    sq = tk.Label(root1, text='授权码')
    sy = tk.Label(root1, text='收件者邮箱')
    fj = tk.Label(root1, text='附件')
    yn = tk.Label(root1, text='邮件内容')

    fs = tk.Button(root1, text="发送", command=fsh)
    qx = tk.Button(root1, text="取消", command=qxh)
    dk = tk.Button(root1, text="打开文件", command=dkh)

    fy.grid(row=0, column=0, sticky=tk.E)
    fr.grid(row=1, column=0, sticky=tk.E)
    yz.grid(row=2, column=0, sticky=tk.E)
    yf.grid(row=3, column=0, sticky=tk.E)
    sq.grid(row=4, column=0, sticky=tk.E)
    sy.grid(row=5, column=0, sticky=tk.E)
    fj.grid(row=6, column=0, sticky=tk.E)
    yn.grid(row=7, column=0, sticky=tk.E)
    fs.grid(row=8, column=1)
    qx.grid(row=8, column=1, sticky=tk.E)
    dk.grid(row=6, column=3, sticky=tk.E)

    entryfy = tk.Entry(root1)
    entryfr = tk.Entry(root1)
    entryyz = tk.Entry(root1)
    entryyf = tk.Entry(root1)
    entrysq = tk.Entry(root1, show='*')
    entrysy = tk.Entry(root1)
    entryfj = scrolledtext.ScrolledText(root1, width=40, height=2, font=('隶书', 10))
    entryyn = scrolledtext.ScrolledText(root1, width=20, height=10, font=('隶书', 18))

    entryfy.grid(row=0, column=1)
    entryfr.grid(row=1, column=1)
    entryyz.grid(row=2, column=1)
    entryyf.grid(row=3, column=1)
    entrysq.grid(row=4, column=1)
    entrysy.grid(row=5, column=1)
    entryfj.grid(row=6, column=1)
    entryyn.grid(row=7, column=1)
    root1.mainloop()


def sendmail(serversocket):
    window=tk.Toplevel()
    window.geometry("350x150")#定义窗口尺寸本例定义大小
    window.resizable(width=False,height=False)#3，定义窗口拉伸权限,默认为可拉伸，此时将其设定为不可拉伸
    window.configure(bg='#CCFFFF')
    window.iconbitmap('邮件.ico')
    window.title("邮件发送")#增加标题
 
 
    lable=tkinter.Label(window,text="邮箱主题",bg='#CCFFFF')#在窗口中添加文本标签 label
    lable.grid(row = 1,column=1)
    title_input=tkinter.Entry(window,width="30")#在窗口中添加一个文本框
    title_input.grid(row = 1,column=2)
 
    lable = tkinter.Label(window, text="邮箱内容",bg='#CCFFFF')
    lable.grid(row = 2,column=1)
    content_input = tkinter.Entry(window, width="30")
    content_input.grid(row = 2,column=2)
 
 
    lable = tkinter.Label(window, text="收件人邮箱",bg='#CCFFFF')
    lable.grid(row = 3,column=1)
    to_input = tkinter.Entry(window, width="30")
    to_input.grid(row = 3,column=2)

    lable = tkinter.Label(window, text="添加附件",bg='#CCFFFF')
    lable.grid(row = 4,column=1)
    fujian=StringVar()   
    file_input = tkinter.Entry(window, width="30",textvariable=fujian)
    file_input.grid(row = 4,column=2)

    def openattach():
        r=askopenfilename(title='打开文件')
        fp=open(r,'r',encoding="utf-8")
        filename=r
        fujian.set(r)
        fp.close()
 
    def send():
        # 打印输入框信息
        # 发件人
        user = '1798630348@qq.com'
        # 收件人
        to = to_input.get()
        # 密码
        pwd = 'fegyjeetquobhcji'
        # 邮箱内容
        content = content_input.get()
        textApart = MIMEText(content)
        # 邮箱主题
        title = title_input.get()
        file=fujian.get()
        fileApart = MIMEApplication(open(file, 'rb').read())
        fileApart.add_header('Content-Disposition', 'attachment', filename=file)

        # 定义邮箱服务
        try:
            server = "smtp.qq.com"
            msg = MIMEMultipart()
            msg.attach(fileApart)
            msg.attach(textApart)
            msg["subject"] = title
            msg["From"] = user
            send = smtplib.SMTP(server, 25)
            send.login(user=user, password=pwd)
            send.sendmail(from_addr=user, to_addrs=to, msg=msg.as_string())
        except(socket.gaierror,socket.error,socket.herror,smtplib.SMTPException) as e:
            showinfo(title='提示',message='邮件发送失败，请重试')
            print(e)
            sys.exit(1)
        else:
            showinfo(title='提示',message='邮件发送成功')

#按钮
    pfile=tk.PhotoImage(file='文件1.png')
    btn1=tkinter.Button(window,text="发送",command=send,bg = "white")
    btn1.grid(row = 5,column=2)
    btn2=tkinter.Button(window,text="打开文件",command=openattach,image=pfile,bg = "white")
    btn2.grid(row = 4,column=3)
    window.mainloop()    
    
root=tk.Tk()
root.title("chatroom-server")
root.iconbitmap('消息.ico')
root.configure(bg='white')
#ftp
ftp = FTP()
# 打开调试级别2，显示详细信息
# ftp.set_debuglevel(2)
ftp.connect('127.0.0.1', 8001)
ftp.login('user', '12345')
# 返回一个文件名列表
filename_list = ftp.nlst()
print(filename_list)
j=len(filename_list)
h=0
#ftp函数

#ftp函数结束

#ftp界面
sw=tk.Button(root,text = "上传文件",width=10)
xw=tk.Button(root,text = "下载文件",width=10)
sx=tk.Button(root,text = "刷新",width=10)


def swh():
    print(1)
    r = askopenfilename(title='上传文件')
    print(r)
    image_list = r.rsplit('/', maxsplit=1)[1]
    print(image_list)
    ftp = FTP()
    # 打开调试级别2，显示详细信息
    # ftp.set_debuglevel(2)
    ftp.connect('127.0.0.1', 8001)
    ftp.login('user', '12345')

    localpath = r"{}".format(r)  # 等待上传的文件，fp
    remotepath = r"{}".format(image_list)  # 上传后，存在FTP中的名字

    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()
    showinfo("提示", "上传成功！")

def xwh():
    for i in lb.curselection():
        global h2
        h2=lb.get(i)

        print(lb.get(i))
    ftp = FTP()
    # 打开调试级别2，显示详细信息
    # ftp.set_debuglevel(2)
    ftp.connect('127.0.0.1', 8001)
    ftp.login('user', '12345')

    localpath = r"G:\FTP\upload1\{}".format(h2)  # 下载后，本机要存放的位置和名字
    remotepath = r"{}".format(h2)  # 从FTP服务器中，要下载内容
    bufsize = 1024

    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)  #

    ftp.set_debuglevel(0)  # 参数为0，关闭调试模式
    fp.close()
    showinfo("提示", "下载成功！")

def sxh():
    lb.delete(0, END)
    filename_list1 = ftp.nlst()
    print(filename_list1)
    for item in filename_list1:
        lb.insert(END, item)

def qxh():
    root.destroy()

sw=tk.Button(root,text = "上传文件",command = swh,width=10)
xw=tk.Button(root,text = "下载文件",command = xwh,width=10)
sx=tk.Button(root,text = "刷新",command = sxh,width=10)
qx=tk.Button(root,text = "取消",command = qxh,width=10)



sw.grid(row=3,column=7,padx=1,pady=1)
xw.grid(row=4,column=7,padx=2,pady=2)
sx.grid(row=5,column=7,padx=3,pady=1)

filename_list1 = ftp.nlst()
print(filename_list1)
lb=Listbox(root,fg='blue')
for item in filename_list1:
    lb.insert(END,item)
lb.grid(row=4, column=6)
#ftp界面


listbox=scrolledtext.ScrolledText(root,width=56,height=15)
listbox.grid(row=1,column=1,columnspan=5,rowspan=2)
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')

text=scrolledtext.ScrolledText(root,width=56,height=6)
text.grid(row=4,column=1,columnspan=5)
text.tag_config('white', foreground='white')

city = Entry(root,width="10")
city.grid(row = 1,column=7)
city.insert(0, '厦门')

photo = tk.PhotoImage(file='./天气.png') 
tianqi= tk.Label(root,image=photo,bg = "white")
tianqi.grid(row = 1,column=6)#调整位置#设置主界面
weather=tk.Text(root,width=20,height=8)
weather.grid(row=2,column=6,columnspan=2)
tianqi.bind("<Enter>", on_enter)
tianqi.bind("<Leave>", on_leave)

start = tk.StringVar()
end = tk.StringVar()

#photo2 = tk.PhotoImage(file='./翻译.png')
#fanyi= tk.Label(root,image=photo2,bg = "white")

#fanyi.grid(row = 4,column=6)#调整位置#设置主界面
Lab2 = tk.Label(root, text="",bg='white')
Lab2.grid(row=4,column=7)


listbox.bind("<Button-1>", button_down)
listbox.bind("<ButtonRelease-1>", button_up)

pfile=tk.PhotoImage(file='文件1.png')
pphoto=tk.PhotoImage(file='图片文件1.png')
pcut=tk.PhotoImage(file='截图1.png')
pemoji=tk.PhotoImage(file='表情1.png')
pemail=tk.PhotoImage(file='邮件1.png')

b1=tk.Button(root,text="发送",bg = "white", command=lambda:chatClient(serversocket))
b1.grid(row=5,column=4)
b2=tk.Button(root,text="关闭",bg = "white",command=lambda:leave(serversocket))
b2.grid(row=5,column=5)
b3=tk.Button(root,text="打开文件",bg = "white",image=pfile,command=lambda:openfile(serversocket))
b3.grid(row=3,column=2)
b4=tk.Button(root,text="打开图片",bg = "white",image=pphoto,command=lambda:openpic(serversocket))
b4.grid(row=3,column=3)
b5=tk.Button(root,text="截屏",bg = "white",image=pcut,command=lambda:buttonCaptureClick(serversocket))
b5.grid(row=3,column=4)
b6=tk.Button(root,text="表情",bg = "white",image=pemoji,command=lambda:express(serversocket))
b6.grid(row=3,column=1)
b6=tk.Button(root,text="邮件",bg = "white",image=pemail,command=lambda:Email())
b6.grid(row=3,column=5)

# 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
emoji1 = ''
emoji2 = ''
emoji3 = ''
emoji4 = ''
# 将图片打开存入变量中
p1 = tk.PhotoImage(file='./blush.png')
p2 = tk.PhotoImage(file='./joy.png')
p3 = tk.PhotoImage(file='./smile.png')
p4 = tk.PhotoImage(file='./sob.png')
# 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
ee = 0  # 判断表情面板开关的标志


#连接
serversocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversocket.bind(('127.0.0.1',8000))
serversocket.listen(5)
serversocket,addr = serversocket.accept()
t = threading.Thread(target=receivedata,args=(serversocket,))
t.start()
tk.mainloop()
