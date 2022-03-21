import os
import shutil
path = "/home/lorenzo/outDB"
path_dest = "/home/lorenzo/toDriveTesi"
if __name__ == "__main__":

        path_pre = os.path.join(path_dest, "pre")
        path_post = os.path.join(path_dest, "post")
        os.makedirs(path_pre,exist_ok=True)
        os.makedirs(path_post,exist_ok=True)
#TODO create  only folders with associated images
        for folder in os.scandir(path):
            position_last_slash = folder.path.rfind("/")
            combined_pre = os.path.join(path_pre, folder.path[position_last_slash +1:])
            combined_post = os.path.join(path_post, folder.path[position_last_slash +1:])
            os.makedirs(combined_pre,exist_ok=True)
            os.makedirs(combined_post,exist_ok=True)
            path_tokpre = os.path.join(folder.path, "tokpre");
            path_tokpost = os.path.join(folder.path, "tokpost");

            for file in os.scandir(path_tokpre):
                shutil.copy(file.path, combined_pre)
            for file in os.scandir(path_tokpost):
                shutil.copy(file.path, combined_post)
