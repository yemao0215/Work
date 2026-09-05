import turtle as tu
from turtle import *
import random as ra
import tkinter as tk
import math

word = "给阿萌的圣诞树🎄"  # 写字

def christmas():
    setup(1.0, 1.0, None, None)
    screensize(1.0, 1.0)    #设置画布大小
    bgcolor('black')  #设置画布颜色
    title("🎄")
    t = tu.Pen()
    t.ht()               #隐藏画笔

    def tree():   #圣诞树
        pencolor("#008500")
        pensize(10)
        penup()
        hideturtle()
        goto(0, 150)
        showturtle()
        pendown()
        shape(name="classic")

        seth(-120)
        for i in range(10):
            fd(12)
            right(2)
        penup()
        goto(0, 150)
        seth(-60)
        pendown()
        for i in range(10):
            fd(12)
            left(2)
        seth(-150)
        penup()
        fd(10)
        pendown()
        for i in range(5):
            fd(10)
            right(15)
        seth(-150)
        penup()
        fd(8)
        pendown()
        for i in range(5):
            fd(10)
            right(15)
        seth(-155)
        penup()
        fd(5)
        pendown()
        for i in range(5):
            fd(7)
            right(15)

        penup()
        goto(-55, 34)
        pendown()
        seth(-120)
        for i in range(10):
            fd(8)
            right(5)

        penup()
        goto(50, 35)
        seth(-60)
        pendown()
        for i in range(10):
            fd(8)
            left(5)
        seth(-120)
        penup()
        fd(10)
        seth(-145)
        pendown()
        for i in range(5):
            fd(10)
            right(15)
        penup()
        fd(10)
        seth(-145)
        pendown()
        for i in range(5):
            fd(12)
            right(15)
        penup()
        fd(8)
        seth(-145)
        pendown()
        for i in range(5):
            fd(10)
            right(15)
        penup()
        seth(-155)
        fd(8)
        pendown()
        for i in range(5):
            fd(11)
            right(15)

        penup()
        goto(-100, -40)
        seth(-120)
        pendown()
        for i in range(10):
            fd(6)
            right(3)
        penup()
        goto(80, -39)
        seth(-50)
        pendown()
        for i in range(10):
            fd(6)
            left(3)
        seth(-155)
        penup()
        fd(10)
        pendown()
        for i in range(5):
            fd(8)
            right(10)
        penup()
        fd(8)
        seth(-145)
        pendown()
        for i in range(7):
            fd(8)
            right(10)
        penup()
        fd(8)
        seth(-145)
        pendown()
        for i in range(7):
            fd(7)
            right(10)
        penup()
        fd(8)
        seth(-145)
        pendown()
        for i in range(7):
            fd(7)
            right(10)
        penup()
        fd(8)
        seth(-140)
        pendown()
        for i in range(7):
            fd(6)
            right(10)


        penup()
        goto(-120, -95)
        seth(-130)
        pendown()
        for i in range(7):
            fd(10)
            right(5)
        penup()
        goto(100, -95)
        seth(-50)
        pendown()
        for i in range(7):
            fd(10)
            left(5)
        penup()
        seth(-120)
        fd(10)
        seth(-155)
        pendown()
        for i in range(6):
            fd(8)
            right(10)
        penup()
        seth(-160)
        fd(10)
        seth(-155)
        pendown()
        for i in range(6):
            fd(8)
            right(10)
        penup()
        seth(-160)
        fd(10)
        seth(-155)
        pendown()
        for i in range(6):
            fd(8)
            right(10)
        penup()
        seth(-160)
        fd(10)
        seth(-160)
        pendown()
        for i in range(6):
            fd(8)
            right(10)
        penup()
        seth(-160)
        fd(10)
        seth(-160)
        pendown()
        for i in range(6):
            fd(8)
            right(10)
        penup()
        seth(-160)
        fd(10)
        seth(-165)
        pendown()
        for i in range(5):
            fd(10)
            right(11)

        penup()
        goto(-70, -165)
        seth(-85)
        pendown()
        for i in range(3):
            fd(5)
            left(3)
        penup()
        goto(70, -165)
        seth(-95)
        pendown()
        for i in range(3):
            fd(5)
            right(3)
        seth(-170)
        penup()
        fd(10)
        pendown()
        pendown()
        for i in range(10):
            fd(12)
            right(2)

        penup()
        goto(70, -165)
        pendown()
        seth(-90)
        pensize(8)
        pencolor("#00cc00")
        circle(-20, 90)

        penup()
        goto(30, -185)
        pendown()
        seth(-180)
        pensize(8)
        pencolor("#00cc00")
        fd(40)

        penup()
        goto(-5, -170)
        pendown()
        seth(-180)
        pensize(8)
        pencolor("#00cc00")
        fd(35)


        def guest(x, y, z):
            penup()
            goto(x, y)
            seth(-z)
            pendown()
            for angel in range(5):
                fd(10)
                right(10)


        def guet(x, y, z):
            penup()
            goto(x, y)
            seth(-z)
            pendown()
            for angel in range(5):
                fd(10)
                left(10)


        def qu(x, y, z):
            penup()
            goto(x, y)
            seth(-z)
            pendown()
            for angel in range(5):
                fd(6)
                right(10)
            seth(-150)
            fd(20)


        guest(-70, -150, 160)
        guest(100, -150, 160)
        guet(110, -110, 50)
        guest(160, -140, 150)
        qu(80, -120, 180)
        guest(70, -85, 165)
        guest(-40, -85, 165)
        guet(90, -50, 50)
        guest(130, -80, 150)
        pencolor("#00cc00")
        qu(-40, -60, 180)
        pencolor('#00cc00')
        qu(80, -30, 180)
        pencolor("#00cc00")
        qu(40, 10, 180)
        pencolor("#00cc00")
        guest(-60, 30, 120)
        guest(-20, -20, 150)
        guet(45, 40, 60)
        guest(-30, 40, 170)
        guest(-30, 110, 115)
        guet(40, 90, 60)
        guest(80, 50, 160)
        pencolor("red")


        def hdj(x, y):
            penup()
            goto(x, y)
            seth(80)
            pendown()
            pensize(2)
            circle(5)
            seth(10)
            fd(15)
            seth(120)
            fd(20)
            seth(240)
            fd(20)
            seth(180)
            fd(20)
            seth(-60)
            fd(20)
            seth(50)
            fd(20)
            seth(-40)
            fd(30)
            seth(-130)
            fd(5)
            seth(135)
            fd(30)
            seth(-60)
            fd(30)
            seth(-150)
            fd(6)
            seth(110)
            fd(30)


        def uit(x, y):
            penup()
            goto(x, y)
            pendown()
            pensize(2)
            circle(5)
            seth(-10)
            fd(15)
            seth(90)
            fd(15)
            seth(200)
            fd(15)
            seth(160)
            fd(15)
            seth(-90)
            fd(15)
            seth(10)
            fd(15)
            seth(-60)
            fd(20)
            seth(-180)
            fd(5)
            seth(110)
            fd(20)
            seth(-90)
            fd(20)
            seth(-180)
            fd(6)
            seth(70)
            fd(15)
            hideturtle()


        def yut(x, y, z):
            penup()
            goto(x, y)
            pendown()
            seth(z)
            for po in range(5):
                fd(4)
                left(36)


        def ytu(x, y, z):
            penup()
            goto(x, y)
            pendown()
            seth(z)
            for kk in range(5):
                fd(4)
                left(36)

        seth(0)
        uit(40, -160)
        hdj(-80, -120)
        yut(-67, -115, 120)
        yut(-86, -123, 150)
        hdj(40, -50)
        yut(52, -45, 130)
        yut(34, -55, 160)
        seth(0)
        pencolor("pink")
        uit(-20, -60)
        ytu(-4, -60, 100)
        ytu(-20, -60, 120)
        hdj(-30, 20)
        yut(-15, 25, 130)
        yut(-40, 20, 180)
        uit(30, 70)
        ytu(45, 70, 100)
        ytu(30, 70, 120)

        pencolor("yellow")
        pensize(5)
        penup()
        seth(0)
        goto(0, 150)
        pendown()
        circle(10)
        seth(-15)
        fd(40)
        seth(90)
        fd(40)
        seth(200)
        fd(40)
        seth(160)
        fd(40)
        seth(-90)
        fd(40)
        seth(15)
        fd(40)
        seth(-70)
        pencolor("yellow")
        pensize(4)
        fd(40)
        seth(-180)
        fd(10)
        seth(100)
        fd(40)
        seth(-100)
        fd(40)
        seth(-180)
        fd(10)
        seth(70)
        fd(40)
        penup()
        seth(0)
        goto(0, 130)
        pencolor("yellow")
        pendown()

        def iou(x, y, z):
            penup()
            goto(x, y)
            pencolor("yellow")
            pendown()
            seth(z)
            for po in range(10):
                fd(4)
                left(18)


        seth(0)
        iou(35, 145, 100)
        iou(-7, 145, 110)
        pencolor("red")
        pensize(7)
        penup()
        goto(-35, 135)
        pendown()

        seth(-20)
        pensize(2)
        penup()
        goto(-30, -120)
        pencolor("white")
        pendown()
        fillcolor("red")
        fd(30)
        circle(4, 180)
        fd(30)
        circle(4, 180)
        penup()
        goto(-25, -115)
        seth(75)
        pendown()
        begin_fill()
        for i in range(5):
            fd(6)
            right(20)
        seth(-10)
        for i in range(5):
            fd(8)
            right(15)
        seth(145)
        for i in range(5):
            fd(5)
            left(2)
        seth(90)
        for i in range(5):
            fd(1)
            left(2)
        seth(-90)
        for i in range(4):
            fd(4)
            right(6)
        seth(161)
        fd(30)
        end_fill()
        pensize(1)
        pencolor("white")


        def koc(x, y, size):
            pensize(2)
            pencolor("yellow")
            penup()
            goto(x, y)
            pendown()
            begin_fill()
            fillcolor("yellow")
            for i in range(5):
                left(72)
                fd(size)
                right(144)
                fd(size)
            end_fill()


        # 星星
        seth(-15)
        koc(-120, -70, 10)
        seth(10)
        koc(100, -20, 10)
        seth(-10)
        koc(10, 40, 10)
        seth(30)
        koc(-80, 60, 10)
        koc(100, -150, 10)
        koc(-140, -150, 10)
        koc(20, 120, 10)

        # 袜子
        seth(-20)
        pensize(2)
        penup()
        goto(-20, 80)
        pencolor("white")
        pendown()
        fillcolor("red")
        fd(25)
        circle(4, 180)
        fd(25)
        circle(4, 180)
        penup()
        goto(-15, 80)
        pendown()
        begin_fill()
        fillcolor("red")
        seth(-120)
        fd(20)
        seth(150)
        fd(5)
        circle(7, 180)
        fd(15)
        circle(5, 90)
        fd(30)
        seth(160)
        fd(18)
        end_fill()

        penup()
        seth(0)
        goto(0, 240)
        pendown()
        pencolor("yellow")
        write(word, align="center", font=("Comic Sans MS", 40, "bold"))

        penup()
        seth(0)
        goto(100, -251)
        pendown()

        pencolor("yellow")
        write("Merry Christmas To You！            ", align="center", font=("Comic Sans MS", 24, "bold"))

    class Hat():            #帽子类
        def __init__(self):   #初始化
            self.x=ra.randint(-1000,1000)      #帽子在画布中的x坐标位置
            self.y=ra.randint(-500,500)        #帽子在画布中的y坐标位置
            self.r=ra.uniform(0.5,1)
            self.k=ra.randint(-50,50)
            self.f = ra.uniform(-3.14, 3.14)
            self.speed = ra.randint(3, 8)

        def draw(self):
            t.penup()                  #提笔
            t.goto(self.x,self.y)      #设置帽子在画布中的初始坐标
            t.pendown()                #落笔
            t.seth(-20 + self.k)
            t.pensize(2)
            t.pencolor("white")
            t.begin_fill()
            t.fillcolor("white")
            t.fd(30 * self.r)
            t.circle(4 * self.r, 180)
            t.fd(30 * self.r)
            t.circle(4 * self.r, 180)
            t.end_fill()
            t.seth(75 + self.k)
            t.begin_fill()
            t.fillcolor("red")
            for i in range(5):
                t.fd(6 * self.r)
                t.right(20)
            t.seth(-10 + self.k)
            for i in range(5):
                t.fd(8 * self.r)
                t.right(15)
            t.seth(145 + self.k)
            for i in range(5):
                t.fd(5 * self.r)
                t.left(2)
            t.seth(90 + self.k)
            for i in range(5):
                t.fd(1 * self.r)
                t.left(2)
            t.seth(-90 + self.k)
            for i in range(4):
                t.fd(4 * self.r)
                t.right(6)
            t.seth(161 + self.k)
            t.fd(30 * self.r)
            t.end_fill()

        def change(self):
            if self.y >= -500:            #当帽子还在画布中时
                self.y -= self.speed     #设置上下移动速度
                self.x += self.speed * math.sin(self.f)    #设置左右移动速度
                self.f += 0.1            #可以理解成标志，改变左右移动的方向
            else:                        #当帽子漂出了画布时，重新生成一个袜子
                self.r = ra.uniform(0.5,1)
                self.x = ra.randint(-1000,1000)
                self.y = 500
                self.f = ra.uniform(-3.14,3.14)
                self.speed = ra.randint(3,8)
                self.k = ra.uniform(-50,50)



    class Sock():            #袜子类
        def __init__(self):   #初始化
            self.x = ra.randint(-1000,1000)      #袜子在画布中的x坐标位置
            self.y = ra.randint(-500,500)                            #袜子在画布中的y坐标位置
            self.r = ra.uniform(0.5,1)
            self.s = ra.randint(-50,50)
            self.f = ra.uniform(-3.14, 3.14)
            self.speed = ra.randint(3, 8)

        def draw(self):
            t.penup()                  #提笔
            t.goto(self.x,self.y)      #设置袜子在画布中的初始坐标
            t.pendown()                #落笔
            t.seth(self.s)
            t.pensize(2)
            t.pencolor("white")
            t.begin_fill()
            t.fillcolor("white")
            t.fd(25 * self.r)
            t.circle(4 * self.r, 180)
            t.fd(25 * self.r)
            t.circle(4 * self.r, 180)
            t.end_fill()
            t.begin_fill()
            t.fillcolor("red")
            t.right(90)
            t.fd(20 * self.r)
            t.left(-100)
            t.fd(5 * self.r)
            t.circle(7 * self.r, 180)
            t.fd(15 * self.r)
            t.circle(5 * self.r, 90)
            t.fd(30 * self.r)
            t.end_fill()

        def change(self):
            if self.y >= -500:            #当袜子还在画布中时
                self.y -= self.speed     #设置上下移动速度
                self.x += self.speed * math.sin(self.f)    #设置左右移动速度
                self.f += 0.1            #可以理解成标志，改变左右移动的方向
            else:                        #当袜子漂出了画布时，重新生成一个袜子
                self.r = ra.uniform(0.5,1)
                self.x = ra.randint(-1000,1000)
                self.y = 500
                self.f = ra.uniform(-3.14,3.14)
                self.speed = ra.randint(3,8)

    class Star():            #星星类
        def __init__(self):   #初始化
            self.r=1       #星星的初始大小
            self.x=ra.randint(-1000,1000)      #星星在画布中的x坐标位置
            self.y=ra.randint(-500,500)        #星星在画布中的y坐标位置
            self.c="gold"           #在星星的颜色列表中随机选择一个颜色
        def draw(self):                        #画星星的函数
            t.pensize(1)               #设置画笔大小
            t.penup()                  #提笔
            t.goto(self.x,self.y)      #设置星星在画布中的初始坐标
            t.pendown()                #落笔
            t.color(self.c)            #设置星星的外框颜色
            for i in range(5):         #循环画星星
                t.forward(self.r)
                t.right(144)
                t.forward(self.r)
                t.left(72)
        def change(self):              #改变星星的大小（星星不断增大）
            if self.r<=10:             #星星的最大大小不超过10
                self.r+=0.5          #递增
            else:                      #超过最大大小就重新画星星
                self.r = 1
                self.x = ra.randint(-1000, 1000)
                self.y = ra.randint(-500, 500)
                self.c = "gold"

    class Snow():    #雪花类
        def __init__(self):
            self.r = ra.uniform(2,3)       #雪花的半径
            self.x = ra.randint(-1000,1000)   #雪花的横坐标
            self.y = ra.randint(-500,500)     #雪花的纵坐标
            self.f = ra.uniform(-3.14,3.14)   #雪花左右移动呈正弦函数
            self.speed = ra.randint(10,15)     #雪花移动速度
            self.color = "white"    #雪花的颜色
            self.outline = 2                #雪花的大小
        def draw(self):                #画每个雪花
            x=self.r                   #雪花的半径
            t.pensize(self.outline)    #雪花的大小
            t.penup()                  #提笔
            t.goto(self.x,self.y)      #随机位置
            t.pendown()                #落笔
            t.color(self.color)        #雪花颜色
            for i in range(6):        #循环画六个雪花瓣
                t.forward(x*5)
                t.backward(x*2)
                t.left(60)
                t.forward(x*2)
                t.backward(x*2)
                t.right(120)
                t.forward(x*2)
                t.backward(x*2)
                t.left(60)
                t.backward(x*3)
                t.right(60)
        def change(self):                    #雪花移动函数
            if self.y >= -500:            #当雪花还在画布中时
                self.y -= self.speed     #设置上下移动速度
                self.x -= self.speed * math.sin(self.f)    #设置左右移动速度
                self.f -= 0.1            #可以理解成标志，改变左右移动的方向
            else:                        #当雪花漂出了画布时，重新生成一个雪花
                self.r = ra.uniform(2,3)
                self.x = ra.randint(-1000,1000)
                self.y = 500
                self.f = ra.uniform(-3.14,3.14)
                self.speed = ra.randint(10,15)
                self.color = "white"
                self.outline = 2

    Christmas=[]              #圣诞礼物列表
    for i in range(99):           #循环增加圣诞礼物
        Christmas.append(Hat())   #圣诞帽
        Christmas.append(Sock())  #圣诞袜
        # Christmas.append(Star())  #星星
        Christmas.append(Snow())  #雪花
        Christmas.append(Snow())
    while True:                   #开始画圣诞礼物
        tu.tracer(0)
        t.clear()
        t.penup()
        t.goto(-366,0)
        t.pendown()
        tree()
        for i in range(66):
            Christmas[i].draw()
            Christmas[i].change()
        tu.update()
    tu.mainloop()
# 主函数
def love():
    root = tk.Tk()
    root.title('🎄')
    root.resizable(0, 0)
    root.wm_attributes("-toolwindow", 1)
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    widths = 300
    heights = 100
    x = (screenwidth - widths) / 2
    y = (screenheight - heights) / 2 - 66
    root.geometry('%dx%d+%d+%d' % (widths, heights, x, y))  # 设置在屏幕中居中显示
    tk.Label(root, text='圣诞快乐!', width=32, font=('宋体', 12, 'bold'), anchor='center').place(x=0, y=10)

    def OK():  # 同意按钮
        root.destroy()
        christmas()   #显示圣诞树


    def NO():  # 拒绝按钮，拒绝不会退出，必须同意才可以退出哦~
        tk.messagebox.showwarning('🎄', '再给你一次机会！')


    def closeWindow():
        tk.messagebox.showwarning('🎄', '嘿嘿，休想')


    tk.Button(root, text='好哦', width=5, height=1, command=OK).place(x=80, y=50)
    tk.Button(root, text='不要', width=5, height=1, command=NO).place(x=160, y=50)
    root.protocol('WM_DELETE_WINDOW', closeWindow)  # 绑定退出事件
    root.mainloop()


love()