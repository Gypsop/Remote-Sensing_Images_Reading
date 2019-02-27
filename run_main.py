# -*- coding: utf-8 -*-
# Author    : Xiaosheng, Zhu (Shandong University of Science and Technology, Hongkong Polytechnic University, Gome Finance)
# Created on: Jan 23rd, 2019
# Topic     : Geo-Image (Remote Sensing) Reading and Processing
#
# ----------Update Log----------
# Update 1  : Jan 24th, 2019
#    Change the preview of current image from BMP files to a matplotlib plot with subplots containing the view of each band.
#    Code tidied up.
#    More comments added.
#    Headfile (*.hdr) existence judgment added and other parts of the code modified to suit the judgement.
#    ***File selection by user is in designing, will work in next version.***
# Update 2  : Jan 25th, 2019
#    Efficiency enhanced.
#    File selection by user is working now in this version. User can choose the file to use in the program.
#    In order to distinguish the top running of the program and the long-time running, notifications of percentage of the drawing work is added.
#    Users can see the 25%, 50%, 75%, 100% notification from this version on during the time the program is drawing the preview image.
# Update 3  : Jan 31st, 2019
#    Training model-aimed adaptability enhanced.
#    More information about the image will be provided for further training in the future.
#    List of the subimages which have the size of 512 * 512 provided, and we can use the list to do the training in the future.
#    There was a bug during the adjustment of the existence of the head file, and now fixed.
# Update 4  : Feb 1st, 2019
#    ***To make a smaller memory use and a shorter running time, the list of the final output data replaced by array.***
#    Efficiency enhanced.
#    Big image (larger than 30000 * 30000) supported.
#    Unnecessary lists and arrays deleted or modified.
#    There was a bug during the output of the 512 * 512 images, and now fixed.

import numpy as np
from osgeo import gdal
from PIL import Image, ImageFont, ImageDraw
import matplotlib.pyplot as plt
import os, sys

#----------判断是否存在头文件----------
currentdir = os.getcwd()                                                 #当前路径

filelist = os.listdir(currentdir)                                        #当前文件夹内文件列表
extension = [0 for i in range(len(filelist))]
filename = [0 for i in range(len(filelist))]
for eachfileindex in range(len(filelist)):
    extension[eachfileindex] = filelist[eachfileindex].split(".")[-1]    #提取文件夹内所有文件的后缀
    filename[eachfileindex] = filelist[eachfileindex].replace("." + extension[eachfileindex], "")   #提取文件夹内所有文件的无后缀文件名

headexist = False

print("----------当前文件夹文件列表----------")
for eachfileindex in range(len(filelist)):
    print(str(eachfileindex + 1) + " " + filelist[eachfileindex])

usefulfileindex = int(input("请输入需要处理的文件的序号。如果影像文件含有头文件，则请输入头文件的序号，程序将自动同时导入同文件夹下同名影像文件："))
usefulfileindex -= 1

if extension[usefulfileindex] == "hdr":
    headfilename = filelist[usefulfileindex]
    imagefilename = filelist[usefulfileindex + 1]
    headexist = True
elif extension[usefulfileindex] not in ["hdr", "img", "png", "tif"]:
    print("----------文件读取失败----------\n本程序当前无法读取png图像、tif图像、img图像及其头文件以外的其他文件格式，程序将立刻退出。\n----------结束----------")
    sys.exit(0)
else:
    imagefilename = filelist[usefulfileindex]
    
if extension[usefulfileindex] == "hdr":
    #----------影像头文件读取，各种短代码对应----------
    dataheadfile = open(headfilename).read().replace("\n ", "")
    dataheadfile = dataheadfile.split("\n")
    for eachlineindedx in range(len(dataheadfile)):
        dataheadfile[eachlineindedx] = dataheadfile[eachlineindedx].replace(" ", "").replace("{", "").replace("}", "").replace("\n", "").split("=")
    for eachlineindedx in range(len(dataheadfile)):
        if dataheadfile[eachlineindedx][0] == "description":          #影像描述
            head_description = str(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "samples":            #列数
            head_width = int(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "lines":              #行数
            head_height = int(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "bands":              #波段数
            head_bands = int(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "headeroffset":       #影像文件读取时开头跳过字节数
            head_headeroffset = int(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "filetype":           #影像文件类型
            head_filetype = str(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "datatype":           #影像数据类型
            if dataheadfile[eachlineindedx][1] == "1":                    #8位字节
                head_datatype = "8-bit byte"
            elif dataheadfile[eachlineindedx][1] == "2":                  #16位有符号整数
                head_datatype = "16-bit signed integer"
            elif dataheadfile[eachlineindedx][1] == "3":                  #32位有符号长整数
                head_datatype = "32-bit signed long integer"
            elif dataheadfile[eachlineindedx][1] == "4":                  #32位浮点数
                head_datatype = "32-bit floating point"
            elif dataheadfile[eachlineindedx][1] == "5":                  #64位双精度浮点数
                head_datatype = "64-bit double-precision floating point"
            elif dataheadfile[eachlineindedx][1] == "6":                  #2 * 32位复数，实虚双精度对
                head_datatype = "2*32-bit complex, real-imaginary pair of double precision"
            elif dataheadfile[eachlineindedx][1] == "9":                  #2 * 64位双精度复数，实虚双精度对
                head_datatype = "2*64-bit double-precision complex, real-imaginary pair of double precision"
            elif dataheadfile[eachlineindedx][1] == "12":                 #16位无符号整数
                head_datatype = "16-bit unsigned integer"
            elif dataheadfile[eachlineindedx][1] == "13":                 #32位无符号长整数
                head_datatype = "32-bit unsigned long integer"
            elif dataheadfile[eachlineindedx][1] == "14":                 #64位有符号长整数
                head_datatype = "64-bit signed long integer"
            elif dataheadfile[eachlineindedx][1] == "15":                 #64位无符号长整数
                head_datatype = "64-bit unsigned long integer"
        elif dataheadfile[eachlineindedx][0] == "interleave":         #影像存储方式
            head_interleave = str(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "sensortype":         #传感器类型
            head_sensortype = str(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "wavelengthunits":    #波长单位
            head_wavelengthunits = str(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "zplotrange":         #影像坐标范围
            dataheadfile[eachlineindedx][1] = dataheadfile[eachlineindedx][1].split(",")
            head_zplotrange_min = float(dataheadfile[eachlineindedx][1][0])
            head_zplotrange_max = float(dataheadfile[eachlineindedx][1][1])
        elif dataheadfile[eachlineindedx][0] == "zplottitles":        #影像横纵坐标标题
            dataheadfile[eachlineindedx][1] = dataheadfile[eachlineindedx][1].split(",")
            head_zplottitles_X = str(dataheadfile[eachlineindedx][1][0])
            head_zplottitles_Y = str(dataheadfile[eachlineindedx][1][1])
        elif dataheadfile[eachlineindedx][0] == "defaultstretch":     #默认显示拉伸方式
            head_defaultstretch = str(dataheadfile[eachlineindedx][1])
        elif dataheadfile[eachlineindedx][0] == "bandnames":          #各波段名称
            head_bandnames = str(dataheadfile[eachlineindedx][1])
            head_bandnames = head_bandnames.split(",")
        elif dataheadfile[eachlineindedx][0] == "wavelength":         #各波段波长
            dataheadfile[eachlineindedx][1] = dataheadfile[eachlineindedx][1].split(",")
            head_wavelength = dataheadfile[eachlineindedx][1]
            #下面的倍数变量transmultiple用于统一将头文件中提供的波长转换为纳米单位以供处理
            if head_wavelengthunits == "Micrometers":
                transmultiple = 1000
            for eachwavelengthindex in range(len(head_wavelength)):     #波长频谱对应信息，波长范围可能不准确
                nanometerwavelength = float(head_wavelength[eachwavelengthindex]) * transmultiple
                if nanometerwavelength > 400 and nanometerwavelength <= 500:
                    head_wavelength[eachwavelengthindex] = head_wavelength[eachwavelengthindex] + "（" + head_bandnames[eachwavelengthindex] + "：蓝光B）"
                elif nanometerwavelength > 500 and nanometerwavelength <= 580:
                    head_wavelength[eachwavelengthindex] = head_wavelength[eachwavelengthindex] + "（" + head_bandnames[eachwavelengthindex] + "：绿光G）"
                elif nanometerwavelength > 580 and nanometerwavelength <= 780:
                    head_wavelength[eachwavelengthindex] = head_wavelength[eachwavelengthindex] + "（" + head_bandnames[eachwavelengthindex] + "：红光R）"
                elif nanometerwavelength > 780 and nanometerwavelength <= 2526:
                    head_wavelength[eachwavelengthindex] = head_wavelength[eachwavelengthindex] + "（" + head_bandnames[eachwavelengthindex] + "：近红外NIR）"
                elif nanometerwavelength > 2526 and nanometerwavelength <= 25000:
                    head_wavelength[eachwavelengthindex] = head_wavelength[eachwavelengthindex] + "（" + head_bandnames[eachwavelengthindex] + "：中红外IIR）"
                elif nanometerwavelength > 25000 and nanometerwavelength <= 300000:
                    head_wavelength[eachwavelengthindex] = head_wavelength[eachwavelengthindex] + "（" + head_bandnames[eachwavelengthindex] + "：远红外FIR）"
    print(
          "----------当前打开的文件信息----------\n" + 
          "━┳来自头文件报告的信息：\n" + 
          " ┣━影像描述 = " + head_description + "\n" + 
          " ┣━列数 = " + str(head_width) + "\n" +
          " ┣━行数 = " + str(head_height) + "\n" +
          " ┣━波段数 = " + str(head_bands) + "\n" + 
          " ┣━列数 = " + str(head_width) + "\n" + 
          " ┣━影像文件类型 = " + head_filetype + "\n" + 
          " ┣━影像数据类型 = " + head_datatype + "\n" + 
          " ┣━影像存储方式 = " + head_interleave + "\n" + 
          " ┣━传感器类型 = " + head_sensortype + "\n" + 
          " ┗┳各波段名称、波长及所属波段"
          )
    for eachwavelengthindex in range(len(head_wavelength)-1):
        print("  ┣━" + head_wavelength[eachwavelengthindex])
    print("  ┗━" + head_wavelength[len(head_wavelength)-1])
else:
    print(
      "----------当前打开的影像文件信息----------\n" + 
      "━┳来自头文件报告的信息：\n" + 
      " ┗━选择的文件非头文件，将只处理选中的影像文件。"
      )
#----------影像文件读取----------
data = gdal.Open(imagefilename)          #打开影像
image_width = data.RasterXSize
image_height = data.RasterYSize
image_geotrans = data.GetGeoTransform()  #仿射矩阵
image_proj = data.GetProjection()        #地图投影信息
image_data = data.ReadAsArray(0, 0, image_width, image_height).astype(np.float) #将数据写成数组，对应原图像栅格矩阵
#在image_data数组中，第一层索引值0, 1, 2…分别代表影像的第1, 2, 3…波段，第二层索引值代表行数height，第三层索引值代表列数width

print(
      "━┳来自影像文件报告的信息：\n" +  
      " ┣━列数 = " + str(image_width) + "\n" +
      " ┣━行数 = " + str(image_height) + "\n" +
      " ┣━波段数 = " + str(len(image_data)) + "\n" + 
      " ┣━仿射矩阵 = " + str(image_geotrans) + "\n" +
      " ┗━投影信息 = " + str(image_proj) + "\n"
      )

print("----------头文件与影像文件相符性检查----------")
if extension[usefulfileindex] != "hdr":
    print("选择的文件非头文件，无法进行头文件与影像文件相符性检查。")
elif head_width == image_width and head_height != image_height:
    print("头文件与同名影像文件报告的列数相符但行数不相符，验证不通过。请检查头文件与影像文件是否配套。")
elif head_width != image_width and head_height == image_height:
    print("头文件与同名影像文件报告的行数相符但列数不相符，验证不通过。请检查头文件与影像文件是否配套。")
elif head_width != image_width and head_height != image_height:
    print("头文件与同名影像文件报告的行列数均不相符，验证不通过。请检查头文件与影像文件是否配套。")
elif head_width == image_width and head_height == image_height:
    print("头文件与同名影像文件报告的行列数相符，验证通过。")
else:
    print("头文件与同名影像文件相符性检查出现未知错误，验证不通过。请检查文件。")
    
print("----------预览图绘制----------\n对于较大的影像，该过程可能会花费较长时间，请等待。\n预览图将在所有波段全部绘制完成后显示。")
#----------分波段绘图，对读入的影像进行线性拉伸处理以产生良好的输出效果----------
plt.figure("Current Image Preview of Each Band (" + "Width = " + str(image_width) + ", Height = " + str(image_height) + ")")
linearstretchmultiplenotification = ["" for i in range(len(image_data))]
for eachbandindex in range(len(image_data)):
#for eachbandindex in range(1):
    print("━┳波段" + str(eachbandindex + 1) + "读取")
    imageshow = Image.new("L", (image_width, image_height))
    maxvalueinband = 0
    for eachcolumnindex in range (0, image_width):
        for eachlineindex in range (0, image_height):
            if image_data[eachbandindex][eachlineindex][eachcolumnindex] > maxvalueinband:
                maxvalueinband = image_data[eachbandindex][eachlineindex][eachcolumnindex]
                
        if abs(eachcolumnindex - image_width / 4) < 0.5:
            print(" ┣━波段" + str(eachbandindex + 1) + "读取 - 25%已完成")
        elif abs(eachcolumnindex - image_width / 2) <= 1 and eachcolumnindex < image_width / 2:
            print(" ┣━波段" + str(eachbandindex + 1) + "读取 - 50%已完成")
        elif abs(eachcolumnindex - image_width * 3 / 4) < 0.5:
            print(" ┣━波段" + str(eachbandindex + 1) + "读取 - 75%已完成")
        elif abs(eachcolumnindex - image_width) == 1:
            print(" ┣━波段" + str(eachbandindex + 1) + "读取 - 100%已完成")
    print(" ┗━根据读取到的数据绘制波段" + str(eachbandindex + 1) + "的预览图…")
    linearstretchmultiple = 255 / maxvalueinband
    for eachcolumnindex in range (0, image_width):
        for eachlineindex in range (0, image_height):
            imageshow.putpixel((eachcolumnindex, eachlineindex), int(image_data[eachbandindex][eachlineindex][eachcolumnindex] * linearstretchmultiple))
    draw = ImageDraw.Draw(imageshow)                                    #绘图句柄
    x, y=(0, 0)                                                         #初始左上角的坐标
    #draw.ink = (R) + (G) * 256 + (B) * 256 * 256
    draw.ink = 255 + 255 * 256 + 255 * 256 * 256                        #颜色
    font = ImageFont.truetype("courbd.ttf", int(image_height / 15))
    if headexist == True:
        draw.text((x, y), head_bandnames[eachbandindex], font = font) #在图中加入文字标注
    else:
        draw.text((x, y), str(eachbandindex + 1), font = font)
    if len(image_data) % 2 == 0:
        subplot = plt.subplot(2, len(image_data) / 2, eachbandindex + 1)
    else:
        subplot = plt.subplot(2, (len(image_data) + 1) / 2, eachbandindex + 1)
    if headexist == True:
        subplot.set_title(head_bandnames[eachbandindex])
    else:
        subplot.set_title(str(eachbandindex + 1))
    plt.imshow(imageshow)
    #imageshow.show()
    if extension[usefulfileindex] == "hdr":
        linearstretchmultiplenotification[eachbandindex] = str("波段" + head_bandnames[eachbandindex] + "的线性拉伸比例 = " + str(linearstretchmultiple))
    else:
        linearstretchmultiplenotification[eachbandindex] = str("波段" + str(eachbandindex + 1) + "的线性拉伸比例 = " + str(linearstretchmultiple))
    #PIL颜色模式
    #1             1位像素，黑和白，按8位像素存储
    #L             8位像素，黑白
    #P             8位像素，使用调色板映射到任何其他模式
    #RGB           3×8位像素，真彩
    #RGBA          4×8位像素，真彩+透明通道
    #CMYK          4×8位像素，颜色隔离
    #YCbCr         3×8位像素，彩色视频格式
    #I             32位整型像素
    #F             32位浮点型像素
plt.show()
for eachbandindex in range(len(image_data)):
    print(linearstretchmultiplenotification[eachbandindex])
print("预览图绘制完成。")


#----------影像高级处理，以NDVI计算为例----------
#ndvi = (image_data[3] - image_data[2]) / (image_data[3] + image_data[2])

print("----------结束----------")