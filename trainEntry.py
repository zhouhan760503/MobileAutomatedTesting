import os

file = open('./labels.txt')
labels = file.read()
# labels 是用来标注class的index的
labels = eval(labels)
file.close()

# 读取json文件
path = './combinedjson'
files = os.listdir(path)
files.sort()
# 去除.DS_Store文件
files.pop(0)

for i in range(len(files)):
# for i in range(1):
    picname = files[i][0:len(files[i])-7]+".jpg"
    jsonname = files[i]
    jsonfile = path+"/"+jsonname
    jsonfile = open(jsonfile,"r")
    jsonfile = jsonfile.read()
    content = eval(jsonfile)
    res = ""
    for j in range(len(content)):
        xcenter = ((content[j][0][0]+content[j][0][2])/2)/1440
        ycenter = ((content[j][0][1]+content[j][0][3])/2)/2560
        width = abs((content[j][0][2] - content[j][0][0])/1440)
        height = abs((content[j][0][3] - content[j][0][1])/2560)
        res += str(labels.index(content[j][1])) + " " +str(xcenter)+ " " +str(ycenter)+" "+str(width)+" "+str(height)+"\n"
    labelfile = picname[0:len(picname)-4]+".txt"
    labelfile = open('./pics/labels/train2020/'+labelfile,"w")
    labelfile.write(res)
    labelfile.close()