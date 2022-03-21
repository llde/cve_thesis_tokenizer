import os
import tokenizer
import json
import regex
import math
from PIL import Image

path = "/home/lorenzo/outDB"

def sort(i):
    return i[1]

idx = 4
exclude = [0,1,2,3,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35, 36, 37,38,40,50,232,233,234,235,236,237,238,239,240,241,42,243,244,245,246,247,248,249,250,251,252,253,254,255]
cache = {}
def pick_progressive(name):
    if name in cache: return cache[name]
    old_idx = idx
    idx+=1
    if(old_idx > 233): return -1 #No enough token
    while (idx in exclude): idx+=1
    cache[name] = old_idx
    return old_idx

def token_to_pixel(token):
    if(tok[0] == "keyword" or tok[0] == "op"): #Just for ?
        if(tok[1] == "if" or tok[1] == "?"): return 255
        if(tok[1] == "else"): return 254
        if(tok[1] == "for"): return 253
        if(tok[1] == "while"): return 252
        if(tok[1] == "break"): return 251
        if(tok[1] == "return"): return 250
        if(tok[1] == "switch"): return 249
        if(tok[1] == "case"): return 248
        if(tok[1] == "continue"): return 247
        if(tok[1] == "default"): return 246
        if(tok[1] == "signed" or tok[1] == "unsigned"): return 245  #Auto is C++
        if(tok[1] == "const"): return 244
        if(tok[1] == "enum"): return 243
        if(tok[1] == "struct"): return 242
        if(tok[1] == "union"): return 241
        if(tok[1] == "typedef"): return 240
        if(tok[1] == "volatile"): return 239
        if(tok[1] == "void"): return 238
        if(tok[1] == "static"): return 237
        if(tok[1] == "extern"): return 236
        if(tok[1] == "do"): return 235
        if(tok[1] == "&","goto"): return 234
        if(tok[1] == "null" or tok[1] == "NULL" ): return 3
        if(tok[1] == "offsetof"): return 233
        if(tok[1] == "sizeof"): return 232
        if(tok[1] == "register"): return -2 # (-2 ignore and skip token)  register doesn't modify behaviour in modern compilers
        if(tok[1] == "EOF"): return 0
    if(tok[0] == "directive"): return 20
    if(tok[0] == "type"): return 50
    if(tok[0] == "include"): return 21
    if(tok[0] == "string"): return 22
    if(tok[0] == "char" or tok[0] == "char_continue"): return 23
    if(tok[0] == "number"): return 24
    if(tok[0] == "whitespace"): return 1
    if(tok[0] == "nl" or tok[0] == "endline"): return 2
    if(tok[0] == "op"):
        if(tok[1] in ["+", "-", "/" , "%" , "^" ,"|" , "!", ">>", "<<", "TiLddE"]): return 29 #* isn't just an operation but can also identify a pointer, & is also get pointer
        if(tok[1] in ["&&" , "||"]) : return 28
        if(tok[1] in ["&=" , "|=", "=", "+=", "-=", "*=", "/=", "%="]) : return 27
        if(tok[1] in [".", "->"]) : return 26 #split?
        if(tok[1] in ["**"]) : return 25
        if(tok[1] in [";", ",", ":", "#"]) : return 31
        if(tok[1] in ["(", ")"]) : return 32
        if(tok[1] in ["[", "]"]) : return 33
        if(tok[1] in ["{", "}"]) : return 34
        if(tok[1] in ["++" , "--"]) : return 36
        if(tok[1] in ["&" , "*"]) : return 38 #  Context dependant
        if(tok[1] in ["<", ">", "==", ">=", "<="]) : return 37
        print(tok[1])
        return 0
    if(tok[0] == "id"):
        if(tok[1] == "var"): return 30
        if(tok[1] == "func"): return 40
    if(tok[0] == "FuncDef"): return 35
    if(tok[0] == "APICall"):
        return pick_progressive(tok[1])
    print(tok[0] + tok[1])
    return 0


if __name__ == "__main__":
    tokenizer = tokenizer.C_Tokenizer()
    name_and_count = dict()
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
            func_names, headers,func_defs , ok = tokenizer.partial_tokenize(content)
            if(ok == False):
                print(file.path)
            for named in func_names:
                if named in name_and_count:
                    name_and_count[named] += 1
                else:
                    name_and_count[named] = 1

    normalized = []
    for key,value in name_and_count.items():
        if(value >= 300):
            normalized.append((key,value))

    normalized.sort(reverse = True, key = sort)
    print(len(normalized))

    number = 200
    for folder in os.scandir(path):
        if number == 0: break
        path_pre = os.path.join(folder.path, "pre");
        path_post = os.path.join(folder.path, "post");
        path_tokpre = os.path.join(folder.path, "tokpre");
        path_tokpost = os.path.join(folder.path, "tokpost");
        os.makedirs(path_tokpre,exist_ok=True)
        os.makedirs(path_tokpost,exist_ok=True)
        idx = 4
        cache.clear()
        for file in os.scandir(path_pre):
            with open(file.path,'r') as f:
                content = f.read()
            tok_code = tokenizer.tokenize(content, custom_names=normalized)
            path_new = file.path.replace("/pre/", "/tokpre/")
            lenght = len(tok_code)
            size = math.ceil(math.sqrt(lenght))
            print(lenght)
            if(lenght == 0):  continue
            img  = Image.new( mode = "L", size = (size,size) )
            imp = img.load()
            currIndex = 0
            for i in range(0,size):
                for j in range(0,size):
                    if(currIndex >= lenght -1): break
                    try:
                        tok = tok_code[currIndex]
                    except:
                        print("Error index " + str(currIndex) + ", lenght" + str(lenght))
                        break
                    ret = token_to_pixel(tok)
                    if(ret == -1): print("No enough value available")
                    currIndex+=1;
                    if(ret == -2):
                        continue
                    imp[j,i] = ret

            img.save(path_new + ".jpg")
            print(path_new)
            break
        for file in os.scandir(path_post):
            with open(file.path,'r') as f:
                content = f.read()
            tok_code = tokenizer.tokenize(content, custom_names=normalized)
            path_new = file.path.replace("/post/", "/tokpost/")
            lenght = len(tok_code)
            size = math.ceil(math.sqrt(lenght))
            print(lenght)
            img  = Image.new( mode = "L", size = (size,size) )
            imp = img.load()
            currIndex = 0
            for i in range(0,size):
                for j in range(0,size):
                    if(currIndex >= lenght -1): break
                    try:
                        tok = tok_code[currIndex]
                    except:
                        print("Error index " + str(currIndex) + ", lenght" + str(lenght))
                        break
                    ret = token_to_pixel(tok)
                    if(ret == -1): print("No enough value available")
                    currIndex+=1;
                    if(ret == -2):
                        continue
                    imp[j,i] = ret

            img.save(path_new + ".jpg")
            print(path_new)
            break

        number -=1
