import json
import os
import cv2
import math

# 此处的standard就是用来判断是否是冗余数据的标准
# 由手动设置，并查看效果
standard = 200

def drawChild(son,imgzi):
    if type(son) != dict:
        return imgzi
    else:
        if "children" in son:
            children = son["children"]
            for i in range(len(children)):
                node = children[i]
                imgzi = drawChild(node,imgzi)

        # newBounds = son["rel-bounds"]
        newBounds = son["bounds"]

        newClassNames = son["class"].split(".")
        newClassName = newClassNames[len(newClassNames) - 1]
        imgzi = cv2.putText(imgzi, newClassName, (newBounds[0], newBounds[1] + 50), font, 2, (0, 64, 0), 3)
        imgzi = cv2.rectangle(imgzi, (newBounds[0], newBounds[1]), (newBounds[2], newBounds[3]), (0, 255, 0), 3)
        return imgzi



def getChild(son,mark):
    if type(son) != dict:
        print(son)
    else:
        if "children" in son:
            children = son["children"]
            for i in range(len(children)):
                node = children[i]
                mark = getChild(node, mark)
        newBounds = son["bounds"]
        newClassName = son["class"]
        mark.append([newBounds,newClassName])
    return mark



path = "./ATMobile2020-1"
files = os.listdir(path)
files.sort()
# 去掉readme
files.pop(len(files)-1)
source = []
labels = []
for i in range(0, len(files), 2):
    pair = []
    pair.append(files[i])
    pair.append(files[i+1])
    source.append(pair)

# #   对图片进行了标注
# for i in range(len(source)):
#     filepath = path+"/"+source[i][1]
#     imgpath = path + "/" + source[i][0]
#     savepath = "./markedpics/"+source[i][0][0:len(source[i][0]) - 4] + "-1.jpg"
#     file = open(filepath, "r")
#     content = json.load(file)
#     root = content["activity"]["root"]
#
#     # bounds = root["rel-bounds"]
#     bounds = root["bounds"]
#
#     classNames = root["class"].split('.')
#     className = classNames[len(classNames) - 1]
#     # 以下进行标注
#
#     img = cv2.imread(imgpath)
#     # 对图片进行缩放操作
#     imgzi = cv2.resize(img, (1440, 2560))
#     font = cv2.FONT_HERSHEY_DUPLEX  # 设置字体
#     # # 图片对象，要写的内容，左边距，字的底部到画布上端的距离，字体，大小，颜色，粗细
#     # imgzi = cv2.putText(imgzi,className,(bounds[0],bounds[1]+50),font,1,(26,62,14),3)
#     # # 画矩形，图片对象，左上角坐标，右下角坐标，颜色，宽度
#     # imgzi = cv2.rectangle(imgzi,(bounds[0],bounds[1]),(bounds[2],bounds[3]),(0,255,0),3)
#     imgzi = drawChild(root, imgzi)
#     a = cv2.imwrite(savepath, imgzi)

# 对json中的控件进行读取和合并
# source是图片和json对，其中[0]为jpg,[1]为json
for i in range(len(source)):
    filepath = path+"/"+source[i][1]
    savepath1 = "./jsonlocs/"+source[i][1]
    savepath2 = "./combinedjson/" + source[i][1][0:len(source[i][1])-5]+"-1.json"
    file = open(filepath,"r")
    content = json.load(file)
    root = content["activity"]["root"]
    res = []
    res = getChild(root,res)
    file.close()
    file = open(savepath1,"w")
    file.write(str(res))
    file.close()

    # 对上一步已经读取的json数据进行去除和合并
    res2 = []
    filtered = []
    for j in range(len(res)):
        # 去除其中为负的坐标
        if res[j][0][0] < 0 or res[j][0][1] < 0 or res[j][0][2] < 0 or res[j][0][3] < 0:
            continue
        # 去除其中大于图片size的坐标
        if res[j][0][0] > 1440 or res[j][0][1] > 2560 or res[j][0][2] > 1440 or res[j][0][3] > 2560:
            continue
        if res[j] in filtered:
            continue
        else:
            tem = res[j]
            similar = []
            similar.append(tem)
            for k in range(len(res)):
                # 去除其中为负的坐标
                if res[k][0][0] < 0 or res[k][0][1] < 0 or res[k][0][2] < 0 or res[k][0][3] < 0:
                    continue
                # 去除其中大于图片size的坐标
                if res[k][0][0] > 1440 or res[k][0][1] > 2560 or res[k][0][2] > 1440 or res[k][0][3] > 2560:
                    continue
                if k == j or res[k] in filtered:
                    continue
                else:
                    cmp = res[k]
                    distance = 0
                    for l in range(4):
                        distance += abs(cmp[0][l] - tem[0][l])
                    #     这里的distance就是阈值
                    if distance<=standard:
                        similar.append(cmp)
            index = 0
            for l in range(len(similar)):
                if len(similar[l][1])>=len(tem[1]):
                    tem = similar[l]
                    index = l
            res2.append(tem)
        for k in range(len(similar)):
            filtered.append(similar[k])
    file = open(savepath2,"w")
    file.write(str(res2))
    file.close()
    for j in range(len(res2)):
        if res2[j][1] in labels:
            continue
        else:
            labels.append(res2[j][1])


    # 利用合并之后的坐标对图片进行标记
    # savepath = "./combinedmarkedpics/"+source[i][0][0:len(source[i][0]) - 4] + "-2.jpg"
    # imgpath = path + "/" + source[i][0]
    # img = cv2.imread(imgpath)
    # imgzi = cv2.resize(img, (1440, 2560))
    # for s in range(len(res2)):
    #     font = cv2.FONT_HERSHEY_DUPLEX  # 设置字体
    #     # # 图片对象，要写的内容，左边距，字的底部到画布上端的距离，字体，大小，颜色，粗细
    #     imgzi = cv2.putText(imgzi,res[s][1],(res2[s][0][0],res2[s][0][1]+50),font,1,(26,62,14),3)
    #     # # 画矩形，图片对象，左上角坐标，右下角坐标，颜色，宽度
    #     imgzi = cv2.rectangle(imgzi,(res2[s][0][0],res2[s][0][1]),(res2[s][0][2],res2[s][0][3]),(0,255,0),3)
    # cv2.imwrite(savepath, imgzi)

# 将labels写入文件
labelfile = open("./labels.txt","w")
labelfile.write(str(labels))
labelfile.close()