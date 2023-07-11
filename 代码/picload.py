#参考博客：https://blog.csdn.net/qq_57171795/article/details/127838273   ---tkinter选择并展示图片
# https://blog.csdn.net/c343340657c/article/details/119956619   --tkinter图片大小限制
# https://blog.csdn.net/qq_43409114/article/details/104538619   --bmp图数据结构
# https://blog.csdn.net/qq_41205771/article/details/106158344   --LSB算法
# https://blog.csdn.net/m0_52985451/article/details/121706473
# https://lbbai.com/?url=gpt   ---ai工具

import tkinter as tk
from tkinter import PhotoImage, filedialog#用于打开文件  核心：filepath = filedialog.askopenfilename() #获得选择好的文件,单个文件
import tkinter.messagebox #弹窗库
from PIL import Image#PIL需要安装 pip install pillow
from PIL import ImageTk,ImageDraw,ImageFont
import struct
import matplotlib.pyplot as plt
import numpy as np,cv2

# save_img = []
path = ''
max_size = 0

#图片缩放
def resize(w, h, w_box, h_box, pil_image):  
    f1 = 1.0*w_box/w 
    f2 = 1.0*h_box/h  
    factor = min([f1, f2])  
    #print(f1, f2, factor) # test  
    # use best down-sizing filter  
    width = int(w*factor)  
    height = int(h*factor)  
    return pil_image.resize((width, height), Image.Resampling.LANCZOS)

# LSB 信息嵌入函数，区分灰度图和真彩图嵌入
def lsb(img_path, message):
    # 将需要隐藏的信息转换为二进制
    binary_message = ''.join(format(ord(c), '08b') for c in message)
    # print(binary_message)
    print("嵌入信息位数: ",len(binary_message))

    # 读取BMP图像并转换为ndarray
    # 下面2行的操作等同于with open，先read前54字节头部，再read调色板信息，再read剩下像素图像内容，将像素内容reshape
    # with open的实现在mytk class的infoinsert方法里
    img = Image.open(img_path)
    rgb = np.asarray(img, dtype=np.uint8)
    print(rgb.shape)
    flag = 1

    #真彩图
    if img.mode == 'RGB':
        # 将二进制信息序列与RGB值的最低位进行比特替换操作
        binary_message_iter = iter(binary_message)
        for i in range(rgb.shape[0]):
            for j in range(rgb.shape[1]):
                r, g, b = rgb[i][j]
                print(r,g,b)
                if flag<=len(binary_message):
                    r = int(format(r, '08b')[:-1] + next(binary_message_iter), 2)
                    flag+=1
                else:
                    rgb[i][j] = [r, g, b]
                    break

                if flag<=len(binary_message):
                    g = int(format(g, '08b')[:-1] + next(binary_message_iter), 2)
                    flag+=1
                else:
                    rgb[i][j] = [r, g, b]
                    break

                if flag<=len(binary_message):
                    b = int(format(b, '08b')[:-1] + next(binary_message_iter), 2)
                    flag+=1
                else:
                    rgb[i][j] = [r, g, b]
                    break
                rgb[i][j] = [r, g, b]
            if flag>len(binary_message):
                break
    # 灰度图
    else:
        # 遍历每个像素，将其最低位替换为消息中的一个比特
        height, width = rgb.shape
        print(rgb)
        for i in range(height):
            for j in range(width):
                if flag<=len(binary_message):
                    pixel_binary = bin(rgb[i, j])[2:].zfill(8)
                    new_pixel_binary = pixel_binary[:-1] + binary_message[i * width + j]
                    new_pixel_value = int(new_pixel_binary, 2)
                    rgb[i, j] = new_pixel_value
                    flag+=1
                else:
                    break
            if flag>len(binary_message):
                break

    # 将替换后的RGB值数组转换回Pillow的Image对象
    stego_img = Image.fromarray(rgb)
    # 保存隐写后的图像为BMP文件
    stego_img.save('stego.bmp')
    return stego_img

def int_to_bin(n):
    """将整数转换为8位二进制字符串"""
    return '{0:08b}'.format(n)

def bin_to_int(b):
    """将8位二进制字符串转换为整数"""
    return int(b, 2)

# 椒盐噪声
# 遍历图片的每个像素，如果随机数小于噪声比例，就将该像素设为黑色，如果随机数大于 1 - 噪声比例，就将该像素设为白色
def add_salt_and_pepper_RGB(image, noise_ratio):
    """
    给图像添加椒盐噪声
    """
    height, width, _ = image.shape
    mask = np.random.choice((0, 1, 2), size=(height, width), p=[noise_ratio / 2, noise_ratio / 2, 1 - noise_ratio])
    salt = (mask == 0)
    pepper = (mask == 1)
    image[salt] = 255
    image[pepper] = 0
    return image

def salt_pepper_noise(image, prob):
    output = np.zeros(image.shape, np.uint8)
    thres = 1 - prob
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            rdn = np.random.rand()
            if rdn < prob:
                output[i][j] = 0
            elif rdn > thres:
                output[i][j] = 255
            else:
                output[i][j] = image[i][j]
    return output


#myTK 初始化窗口 通过openfile函数来选择文件并显示
class myTK():
    def __init__(self) -> None:
        global max_size
        self.window=tk.Tk()#创建对象
        self.window.title("LSB信息隐藏")#标题
        # window.geometry("720x480")#设置窗口大小
        self.window.geometry("1200x960")#设置窗口大小
        self.window.resizable(height=False,width=False)#设置窗口不可改变大小
 
        # Label 组件用于显示图片
        self.label_img1 = tk.Label(self.window)
        self.label_img1.place(x=0, y=200)

        self.label_img2 = tk.Label(self.window)
        self.label_img2.place(x=700, y=200)

        self.label_img3 = tk.Label(self.window)
        self.label_img3.place(x=100, y=600)

        self.label_type = tk.Label(self.window,bg='pink')
        self.label_type.place(x=350, y=250)

        self.label_limit = tk.Label(self.window,bg='pink')
        self.label_limit.place(x=350, y=300)
        # 提示文本
        self.text1 = tk.Label(self.window,text='文本框里输入嵌入密码字节大小,点击提取信息可提取;输入嵌入信息点嵌入按钮可嵌入',bg='pink')
        self.text1.place(x=400, y=0)

        self.text2 = tk.Label(self.window,text='嵌入的图片大小在此展示',bg='pink')
        self.text2.place(x=400, y=200)


        # 文本框
        self.textarea = tk.Entry(self.window,width=100)
        self.textarea.place(x=200,y=50)

 
        #打开文件按钮
        self.bt_open = tk.Button(self.window,command=self.infoinsert, text='选择导入图片',height=2,width=10,activebackground='red')
        self.bt_open.place(x=0, y=0)
        #LSB生成并保存图片按钮
        self.bt_open = tk.Button(self.window,command=self.savepic, text='生成并保存',height=2,width=10,activebackground='red')
        self.bt_open.place(x=100, y=0)
        # 提取嵌入信息按钮
        self.bt_open = tk.Button(self.window,command=self.outletinfo, text='提取信息',height=2,width=10,activebackground='red')
        self.bt_open.place(x=200, y=0)
        # 添加噪声
        self.bt_open = tk.Button(self.window,command=self.addnoise, text='添加噪声',height=2,width=10,activebackground='red')
        self.bt_open.place(x=300, y=0)

 
        self.window.mainloop()#显示

    # def openfile(self):#打开文件并显示
    #     global path
    #     filepath = filedialog.askopenfilename() #获得选择好的文件,单个文件
    #     path=filepath 
    #     imgtype=[".jpg",".png",".bmp",".BMP"]#规定读取的文件类型
    #     if str(filepath)[-4:] in imgtype:
    #         print("打开文件",filepath)
    #         image = Image.open(filepath)  
    #         imgwidth,imgheight=image.size
    #         image_resized = resize(imgwidth, imgheight, 300, 300, image)
    #         print("图1 resize大小: ",image_resized.size)
    #         im = ImageTk.PhotoImage(image_resized)
    #         self.label_img1.config(bg='red',image=im,text='传入图像',compound='center',justify='left',anchor='center',font=('微软雅黑',18),fg='blue')
    #         self.label_img1.image = im
    #     else:
    #         tkinter.messagebox.showinfo('提示','请选择.jpg .png 图片')

    # def openfile2(self):#打开文件并显示
    #     filepath = filedialog.askopenfilename() #获得选择好的文件,单个文件
    #     imgtype=[".jpg",".png",".bmp",".BMP"]#规定读取的文件类型
    #     if str(filepath)[-4:] in imgtype:
    #         print("打开文件",filepath)
    #         image2 = Image.open(filepath)  
    #         imgwidth,imgheight=image2.size
    #         im2 = ImageTk.PhotoImage(resize(imgwidth, imgheight, 300, 300, image2))
    #         # 在图片上添加文字
    #         draw = ImageDraw.Draw(image2)
    #         font = ImageFont.truetype("arial.ttf", 36)
    #         draw.text((10, 10), "Hello World", font=font, fill=(255, 0, 0))
    #         # 将 PhotoImage 对象设置为 Label 的图片属性
    #         self.label_img2.config(bg='red',image=im2,text='嵌入图像',compound='center',justify='left',anchor='center',font=('微软雅黑',18),fg='blue')
    #         self.label_img2.image = im2  
    #     else:
    #         tkinter.messagebox.showinfo('提示','请选择.jpg .png 图片')


    # 选择图片，解析图片类型，计算可嵌入最大字节长度
    def infoinsert(self):
        global path,max_size
        # '先将位图打开'
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.bmp")])
        path = file_path
        # 读取bmp文件头和信息头，这便是bmp图片存储的数据结构
        with open(file_path, 'rb') as f:
            # 读取文件头
            bfType = f.read(2)
            bfSize = struct.unpack('<i', f.read(4))[0]
            bfReserved1 = struct.unpack('<h', f.read(2))[0]
            bfReserved2 = struct.unpack('<h', f.read(2))[0]
            bfOffBits = struct.unpack('<i', f.read(4))[0]
            # 读取信息头
            biSize = struct.unpack('<i', f.read(4))[0]
            biWidth = struct.unpack('<i', f.read(4))[0]
            biHeight = struct.unpack('<i', f.read(4))[0]
            biPlanes = struct.unpack('<h', f.read(2))[0]
            biBitCount = struct.unpack('<h', f.read(2))[0]
            biCompression = struct.unpack('<i', f.read(4))[0]
            biSizeImage = struct.unpack('<i', f.read(4))[0]
            biXPelsPerMeter = struct.unpack('<i', f.read(4))[0]
            biYPelsPerMeter = struct.unpack('<i', f.read(4))[0]
            biClrUsed = struct.unpack('<i', f.read(4))[0]
            biClrImportant = struct.unpack('<i', f.read(4))[0]
            f.close()
        # 读取图片除开头外的像素数据信息，并保存为ndarray数组 
        with open(file_path, 'rb') as f:
            # 读取 BMP 文件头
            header = f.read(54)
            # 解析 BMP 文件头
            width, height, depth = struct.unpack('<iii', header[18:30])
            print(width,height,depth)
            # 判断是灰度图还是真彩色图
            typetext = '' #标识灰度图/真彩图
            if biBitCount == 8: #============================================== 灰度图
                typetext='灰度图'
                # 判断 BMP 文件是否包含调色板
                if bfOffBits != 54:
                    # 计算调色板的字节数
                    palette_size = bfOffBits - 54
                    # 跳过调色板的字节数
                    f.seek(palette_size, 1) 
                # 读取像素数据
                data = np.frombuffer(f.read(), dtype=np.uint8)
                data = data.reshape((height, width))
                # 翻转数组，使其与 BMP 灰度图的显示方向一致
                data = np.flipud(data)
                print(data.shape)
                print(type(data))
                img = data
            else: #============================================================ 真彩图
                typetext='真彩图'
                # 读取像素数据
                data = np.frombuffer(f.read(), dtype=np.uint8)
                data = data.reshape((height, width, 3))[::-1,:,:]
                print(data.shape)
                print(type(data))
                # 将 BGR 数据转换为 RGB 数据
                img = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

            max_size = biWidth*biHeight
            # 将替换后的RGB值数组转换回Pillow的Image对象
            pil_img = Image.fromarray(img)
            f.close()
 
        print("类型:",str(bfType),"大小:",bfSize,"位图数据偏移量:",bfOffBits,"宽度:",biWidth,"高度:",biHeight,"位图:",biBitCount)
        # tkinter 组件数据加载
        imgwidth,imgheight=pil_img.size
        image_resized = resize(imgwidth, imgheight, 300, 300, pil_img)
        print("图1 resize大小: ",image_resized.size)
        im = ImageTk.PhotoImage(image_resized) # Pillow的Image对象转换成TK的image
        self.label_img1.config(bg='red',image=im,text='传入图像',compound='center',justify='left',anchor='center',font=('微软雅黑',18),fg='blue')
        self.label_img1.image = im
        self.label_type.config(text=typetext)
        self.label_limit.config(text='最大嵌入大小为'+str(max_size)+'位')
        

    # 图片保存，该部分调用LSB函数，输出stego.bmp文件
    def savepic(self):
        global path,max_size
        message = self.textarea.get()
        print(path)
        l = len(''.join(format(ord(c), '08b') for c in message))
        if l>max_size:
            tkinter.messagebox.showinfo('提示','嵌入信息过长')
        else:
            pilimage=lsb(path ,message) #LSB
            # tkinter展示隐写图片
            imgwidth,imgheight=pilimage.size
            im3 = ImageTk.PhotoImage(resize(imgwidth, imgheight, 300, 300, pilimage))
            self.label_img3.config(bg='red',image=im3,text='生成结果',compound='center',justify='left',anchor='center',font=('微软雅黑',18),fg='blue')
            self.label_img3.image = im3
            self.text2.config(text=str(l))
 

    # LSB 最低位信息提取
    def outletinfo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.bmp")])
        image = Image.open(file_path)
        # 获取像素值
        pixels = list(image.getdata())
        print(len(pixels))
        length = int(self.textarea.get())
        if image.mode == 'RGB':
            # 提取真彩图 LSB 信息
            message = ''
            for pixel in pixels:
                for i in range(3):
                    binary = int_to_bin(pixel[i])
                    message += binary[-1]

            # 将二进制字符串转换为 ASCII 码
            message = [message[i:i+8] for i in range(0, length, 8)]
            message = ''.join([chr(bin_to_int(m)) for m in message])
            print(message)

            new_text = "密码位数为"+str(length)+'时,嵌入的信息是'+message
            self.textarea.delete(0,tk.END)
            self.textarea.insert(0, new_text)  # 在0号位置处插入新文本
        else:
            # 提取灰度图 LSB 信息
            message = ''
            for pixel in pixels:
                binary = int_to_bin(pixel)
                message += binary[-1]

            # 将二进制字符串转换为 ASCII 码
            message = [message[i:i+8] for i in range(0, length, 8)]
            message = ''.join([chr(bin_to_int(m)) for m in message])
            print(message)

            new_text = "密码位数为"+str(length)+'时,嵌入的信息是'+message
            self.textarea.delete(0,tk.END)
            self.textarea.insert(0, new_text)  # 在0号位置处插入新文本
 
    # 添加噪声
    def addnoise(self):
        # 读取真彩图
        im = Image.open("stego.bmp")
        im_arr = np.array(im)
        if im.mode == 'RGB':
            # 添加椒盐噪声
            noisy_im_arr = add_salt_and_pepper_RGB(im_arr, 0.1)
            # 将噪声图像转换为 PIL 图像并显示
            noisy_im = Image.fromarray(np.uint8(noisy_im_arr))
            noisy_im.show()
            noisy_im.save('noisy.bmp')
        else:
            noisy_im_arr = salt_pepper_noise(im_arr, 0.05) #添加 5% 的椒盐噪声
            noisy_im = Image.fromarray(np.uint8(noisy_im_arr))
            noisy_im.show()
            noisy_im.save('noisy.bmp')

if __name__=="__main__":
    mywindow=myTK()
 
 
 
 
 
 
 
 
 
 