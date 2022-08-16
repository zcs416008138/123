import os
import shutil
filepath_images = r'G:\标注4.2\images'
filepath_label = r'G:\标注4.2\废钢4.2'
filepath =r'E:\fg_label'
ff = []


def eachFile(filepath):
    global ff
    pathDir =  os.listdir(filepath)
    for allDir in pathDir:
        # print(allDir)
        ff.append(allDir)
        # child = os.path.join('%s%s' % (filepath, allDir))
        # print(child) # .decode('gbk')是解决中文显示乱码问题

def eachfil_label(filepath_label):
    global ff
    pathDir =  os.listdir(filepath_label)
    js = 0
    for allDir in pathDir:
        # print(allDir)
        # print(allDir[:-4] + '.jpg')
        if allDir[:-4] + '.jpg' in ff:
            if js % 10 == 8:
                shutil.copy(filepath_images + r'/' + allDir[:-4] + '.jpg', filepath + r'\valid\images/' + allDir[:-4] + '.jpg')
                shutil.copy(filepath_label + r'/' + allDir, filepath + r'\valid\labels/' + allDir[:-4] + '.txt')
            else:
                # if js % 10 == 9:
                #     shutil.copy(filepath_images+r'/' + allDir[:-4] + '.jpg',filepath + r'\test\images/')
                #     shutil.copy(filepath_label+r'/' + allDir,filepath + r'\test\labels/')
                # else:

                shutil.copy(filepath_images+r'/' + allDir[:-4] + '.jpg',filepath + r'\train\images/'+ allDir[:-4] + '.jpg')
                shutil.copy(filepath_label+r'/' + allDir,filepath + r'\train\labels/' + allDir[:-4] + '.txt')
        js += 1



if __name__ == "__main__":

    eachFile(filepath_images)
    eachfil_label(filepath_label)