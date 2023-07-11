from PIL import Image
import random
import numpy as np
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# 将信息进行加密
def encrypt_info(info, key):
    key = key.encode('utf-8')
    h = hashlib.sha256(key).digest()
    key = h[:16]
    iv = h[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    info = info.encode('utf-8')
    info = pad(info)
    ciphertext = cipher.encrypt(info.encode('utf-8'))
    return ciphertext

# 将加密后的信息转化为二进制形式
# def str2bin(s):
#     print(s)
#     return ''.join(format(ord(c), '08b') for c in (s))

# 将信息进行填充
def pad(s):
    return s.decode('utf-8') + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

# 将信息进行解密
def decrypt_info(ciphertext, key):
    # ciphertext.encode('utf-8')
    print(ciphertext)
    key = key.encode('utf-8')
    h = hashlib.sha256(key).digest()
    key = h[:16]
    iv = h[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    plaintext = cipher.decrypt(ciphertext.encode('utf-8'))
    plaintext = plaintext.rstrip(b'\0')
    plaintext = plaintext.decode('utf-8')
    return plaintext

# 嵌入信息
def embed_info(img_path, info, key):
    # 打开图像
    img = Image.open(img_path)
    # 将图像转化为二维数组
    img_arr = np.array(img)
    # 将信息进行加密
    ciphertext = encrypt_info(info, key)
    # 将加密后的信息转化为二进制形式
    bin_info = ciphertext
    # 随机选择像素点
    pixels = []
    for i in range(len(bin_info)):
        x = random.randint(0, img.size[0]-1)
        y = random.randint(0, img.size[1]-1)
        pixels.append((x, y))
    # 将信息嵌入到像素点的LSB中
    for i in range(len(pixels)):
        x, y = pixels[i]
        r, g, b = img_arr[y][x]
        r = r & 0b11111110 | int(bin_info[i])
        img_arr[y][x] = [r, g, b]
    # 保存嵌入信息后的图像
    embedded_img = Image.fromarray(img_arr)
    embedded_img.save('embedded.bmp')

    # 保存加密密钥和嵌入位置的随机数
    with open('key.txt', 'w') as f:
        f.write(key)
    with open('pixels.txt', 'w') as f:
        for p in pixels:
            f.write(str(p[0]) + ' ' + str(p[1]) + '\n')

# 提取信息
def extract_info(embedded_img_path, key_path, pixels_path):
    # 打开图像
    img = Image.open(embedded_img_path)
    # 将图像转化为二维数组
    img_arr = np.array(img)
    # 读取加密密钥和嵌入位置的随机数
    with open(key_path, 'r') as f:
        key = f.read()
    with open(pixels_path, 'r') as f:
        pixels = [(int(line.split()[0]), int(line.split()[1])) for line in f.readlines()]
    # 从图像中提取信息
    bin_info = ''
    for p in pixels:
        x, y = p
        r, g, b = img_arr[y][x]
        bin_info += str(r & 0b1)
    # 将二进制形式的信息转化为字符串
    ciphertext = ''
    for i in range(0, len(bin_info), 8):
        byte = bin_info[i:i+8]
        ciphertext += chr(int(byte, 2))
    # 将信息进行解密
    plaintext = decrypt_info(ciphertext, key)
    return plaintext


path = 'test2.bmp'
info = '00112233445566778899'
key = 'secret'
embed_info(path,info,key)

# 解密中间有一个补全16位数据块的bug，实在不清楚到底padding给字符串还是bytes字符串
# extract_info('embedded.bmp','key.txt','pixels.txt')