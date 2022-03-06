import os
import tokenizer
import json
import regex

path = "/home/lorenzo/outDB"
if __name__ == "__main__":
    tokenizer = tokenizer.C_Tokenizer()
    for folder in os.scandir(path):
        path_pre = os.path.join(folder.path, "pre");
        path_post = os.path.join(folder.path, "post");
        path_tokpre = os.path.join(folder.path, "tokpre");
        path_tokpost = os.path.join(folder.path, "tokpost");
        os.makedirs(path_tokpre,exist_ok=True)
        os.makedirs(path_tokpost,exist_ok=True)
        for file in os.scandir(path_pre):
            with open(file.path,'r') as f:
                content = f.read()
            func_names, headers, ok = tokenizer.partial_tokenize(content)
            if(ok == False):
                print(file.path)
            name_and_count = dict()
            for named in func_names:
                if named in name_and_count:
                    name_and_count[named] += 1
                else:
                    name_and_count[named] = 1
   #         print(name_and_count)
            tok_code, name_dict, name_seq  = tokenizer.tokenize(content)
            path_new = file.path.replace("/pre/", "/tokpre/")
            with open(path_new.replace(file.name, file.name + ".tok"),'w') as f:
                f.write(json.dumps(tok_code))
       #     with open(path_new.replace(file.name, file.name + ".namedict"),'w') as f:
       #         f.write(json.dumps(name_dict))
       #     with open(path_new.replace(file.name, file.name + ".nameseq"),'w') as f:
       #         f.write(json.dumps(name_seq))

#        for file in os.scandir(path_post):
#            with open(file.path,'r') as f:
#                content = f.read()
#            tok_code, name_dict, name_seq  = tokenizer.tokenize(content)
#            path_new = file.path.replace("/post/", "/tokpost/")
#            with open(path_new.replace(file.name, file.name + ".tok"),'w') as f:
#                f.write(json.dumps(tok_code))
        #    with open(path_new.replace(file.name, file.name + ".namedict"),'w') as f:
        #        f.write(json.dumps(name_dict))
        #    with open(path_new.replace(file.name, file.name + ".nameseq"),'w') as f:
        #        f.write(json.dumps(name_seq))

   # print(name_dict)
