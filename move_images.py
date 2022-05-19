import os
import csv
import shutil
path = "/home/lorenzo/outDB"
path_dest = "/home/lorenzo/toDriveTesi"

if __name__ == "__main__":
#        assoc = dict()
#        with open('/home/lorenzo/outDB/attributes.csv', 'r', newline='') as csvfile:
#             reader = csv.reader(csvfile, dialect='excel')
#             for row in reader:
#                 assoc[row[0]] = row[1]
  #      print(assoc)
        save = dict()
        path_pre = os.path.join(path_dest, "pre")
        path_post = os.path.join(path_dest, "post")
        os.makedirs(path_pre,exist_ok=True)
        os.makedirs(path_post,exist_ok=True)
        for folder in os.scandir(path):
            if(folder.is_dir() == False) : continue
            position_last_slash = folder.path.rfind("/")
            combined_pre = os.path.join(path_pre, folder.path[position_last_slash +1:])
            combined_post = os.path.join(path_post, folder.path[position_last_slash +1:])
#            val = assoc[folder.path[position_last_slash +1:]]
  #           if(val.startswith("\"CWE") == False):
     #           print(val)
     #           print("Wrong CWE")
   #             continue
            path_tokpre = os.path.join(folder.path, "tokpre");
            path_tokpost = os.path.join(folder.path, "tokpost");
            doOnce = 0
            for file in os.scandir(path_tokpre):
                print(file.path)
                if(file.path.endswith(".jpg") == False): continue
                if doOnce == 0: os.makedirs(combined_pre,exist_ok=True)
                doOnce = 1
                shutil.copy(file.path, os.path.join(combined_pre, file.name ))
    #            save[folder.path[position_last_slash +1:]] = val

            doOnce = 0
            for file in os.scandir(path_tokpost):
                print(file.path)
                if(file.path.endswith(".jpg") == False): continue
                if doOnce == 0: os.makedirs(combined_post,exist_ok=True)
                doOnce = 1
                shutil.copy(file.path, os.path.join(combined_post, file.name ))
                
        shutil.copy('/home/lorenzo/outDB/classifier.csv', '/home/lorenzo/toDriveTesi/classifier.csv')
 #       with open('/home/lorenzo/toDriveTesi/attributes.csv', 'w', newline='') as csvfile:
 #           writer = csv.writer(csvfile, dialect='excel')
 #           for key, value in save.items():
 #               writer.writerow([key,value])
