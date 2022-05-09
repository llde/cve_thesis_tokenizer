"""
Copyright 2017 Rahul Gupta, Soham Pal, Aditya Kanade, Shirish Shevade.
Indian Institute of Science.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import collections
import regex as re
from helpers import get_lines, recompose_program
from token_base import Tokenizer, UnexpectedTokenException, EmptyProgramException

Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])


class C_Tokenizer(Tokenizer):
    _keywords = ['auto', 'break', 'case', 'const', 'continue', 'default',
                 'do', 'else', 'enum', 'extern', 'for', 'goto', 'if',
                 'register', 'return', 'signed', 'sizeof', 'offsetof' , 'static', 'switch',
                 'typedef', 'void', 'volatile', 'while', 'EOF', 'NULL',
                 'null', 'struct', 'union']
    _includes = ['stdio.h', 'stdlib.h', 'string.h', 'math.h', 'malloc.h',
                 'stdbool.h', 'cstdio', 'cstdio.h', 'iostream', 'conio.h']
    _calls = ['printf', 'scanf', 'printk', 'clrscr', 'getch', 'strlen',
              'gets', 'fgets', 'getchar', 'main', 'malloc', 'calloc', 'free']
    _types = ['char', 'double', 'float', 'int', 'long', 'short', 'unsigned']
    def _escape(self, string):
        return repr(string)[1:-1]

    def _tokenize_code(self, code):
        keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
        token_specification = [
            ('comment',
             r'\/\*(?:[^*]|\*(?!\/))*\*\/|\/\*([^*]|\*(?!\/))*\*?|\/\/[^\n]*'),
            ('directive', r'#\w+'),
     #      ('string', r'"(?:[^"\n]|\\")*"?'),
            ('string', r'"(?:(?:(?<!\\)|(?<=\\\\))\\"|[^"])*"?'),
            ('char', r"'(?:\\?[^'\n]|\\')'"),
            ('char_continue', r"'[^']*"),
            ('number',  r'[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'),
            ('op',
             r'\(|\)|\[|\]|{|}|->|<<|>>|\*\*|\|\||&&|--|\+\+|[-+*|&%\/=]=|[-<>~!%^&*\/+=?|.,:;#]'),
            ('include',  r'(?<=\#include) *<([_A-Za-z]\w*(?:\.h))?>'),
            ('name',  r'[_A-Za-z]\w*'),
            ('whitespace',  r'\s+'),
            ('nl', r'\\\n?'),
            ('MISMATCH', r'.'),            # Any other character
        ]
        tok_regex = '|'.join('(?P<%s>%s)' %
                             pair for pair in token_specification)
        line_num = 1
        line_start = 0
        mox = ""
        for mo in re.finditer(tok_regex, code):
            kind = mo.lastgroup
            value = mo.group(kind)
            mox += kind + ":" + value + " "
            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
            elif kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                print(mox)
                yield UnexpectedTokenException('%r unexpected on line %d' % (value, line_num))
            else:
                if kind == 'ID' and value in keywords:
                    kind = value
                column = mo.start() - line_start
                yield Token(kind, value, line_num, column)

    def _sanitize_brackets(self, tokens_string):
        lines = get_lines(tokens_string)

        if len(lines) == 1:
            raise EmptyProgramException(tokens_string)

        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]

            if line.strip() == '_<op>_}' or line.strip() == '_<op>_} _<op>_}' \
               or line.strip() == '_<op>_} _<op>_} _<op>_}' or line.strip() == '_<op>_} _<op>_;' \
               or line.strip() == '_<op>_} _<op>_} _<op>_} _<op>_}' \
               or line.strip() == '_<op>_{' \
               or line.strip() == '_<op>_{ _<op>_{':
                if i > 0:
                    lines[i - 1] += ' ' + line.strip()
                    lines[i] = ''
                else:
                    # can't handle this case!
                    return ''

        # Remove empty lines
        for i in range(len(lines) - 1, -1, -1):
            if lines[i] == '':
                del lines[i]

        for line in lines:
            assert(lines[i].strip() != '')

        return recompose_program(lines)

    def partial_tokenize(self, code):
        name_sequence = []
        func_defs = []
        headers = []
        my_gen = self._tokenize_code(code)
        regex = '%(d|i|f|c|s|u|g|G|e|p|llu|ll|ld|l|o|x|X)'
        isNewLine = True
        prev_id = False
        prev_name = ""
        directive = False
        ok = True
        prevTok = []
        while True:
            try:
                token = next(my_gen)
            except StopIteration:
                break

            if isinstance(token, Exception):
                ok = False
                print(token)
                break

            type_ = str(token[0])
            value = str(token[1])
            definition = False
            if(prev_id == True):
                if(type_ == 'op'  and value == '(' and directive == False):
                    for tok in reversed(prevTok[:-1]):
                        if str(tok[0]) == 'whitespace': continue
                        elif str(tok[0]) == 'name' and not str(tok[1]) == 'return' :
                            definition = True
                            break
                        elif str(tok[0]) == 'op':
                            if tok[1] != '*':
                                definition = False
                                break
                            else: continue
                        elif str(tok[0]) == 'name' and str(tok[1]) == 'return':
                            definition = False
                            break
                        
                    if(definition == True):
                        func_defs.append(prev_name)
                        prevTok.clear()
                    else:
                        name_sequence.append(prev_name)

            prevTok.append(token)

            if type_ == 'whitespace' and (('\n' in value) or ('\r' in value)):
                if isNewLine:
                    continue
    #            line_count += 1
                isNewLine = True
                directive = False
                continue;

            elif type_ == 'whitespace' or type_ == 'comment' or type_ == 'nl':
                continue;

            prev_id = False
            prev_name = ""

            if value in self._keywords:
                isNewLine = False

            elif type_ == 'include':
                headers += value
                isNewLine = False

            elif value in self._types:
                isNewLine = False

            elif 'string' in type_:
                isNewLine = False

            elif type_ == 'name':
                isNewLine = False
                prev_id = True
                prev_name = value

            elif type_ == 'number':
                isNewLine = False

            elif 'char' in type_ or value == '':
                isNewLine = False
            elif type_ == 'directive':
                isNewLine = False
                directive = True

            else:
                isNewLine = False

        return name_sequence, headers, func_defs  , ok

    def tokenize(self, code, keep_format_specifiers=False, keep_names=False,
                 keep_literals=False, custom_names = []):
        line_count = 1
        name_sequence = []
        if(custom_names == []): name_sequence = self._calls
        else : name_sequence = custom_names
        token_seq = []
        regex = '%(d|i|f|c|s|u|g|G|e|p|llu|ll|ld|l|o|x|X)'
        isNewLine = True

        # Get the iterable
        my_gen = self._tokenize_code(code)
        prev_id = True
        prev_name = ""
        directive = False;
        prevTok = []
        while True:
            try:
                token = next(my_gen)
            except StopIteration:
                break

            if isinstance(token, Exception):
                return token

            type_ = str(token[0])
            value = str(token[1])
            definition = False
            if(prev_id == True):
                if(type_ == 'op'  and value == '(' and directive == False):
                    for tok in reversed(prevTok[:-1]):
                        if tok[0] == "whitespace": continue
                        elif tok[0] == "name":
                            definition = True
                            break
                        elif tok[0] == "op":
                            if tok[1] != "*": break
                            else: continue
                        elif tok[0] == "return":
                            break
                    if(definition == True):
                        token_seq.append(("FuncDef", prev_name))
                        prevTok.clear()
                    elif(keep_names == True):
                        #define calls and function style macros call
                        token_seq.append(("id", prev_name))
                    else:
                        #define calls and function style macros call
                        token_seq.append(("id", "func"))
                else:
                    #define vars and macro definitions
                    token_seq.append(("id", "var"))

            prev_id = False
            prev_name = ""
            prevTok.append(token)
            if value in self._keywords:
                token_seq.append(("keyword", self._escape(value)))
                isNewLine = False

            elif type_ == 'include':
                token_seq.append(("include", self._escape(value).lstrip()))
                isNewLine = False

            elif value in name_sequence:
                token_seq.append(("APICall", self._escape(value).lstrip()))
                isNewLine = False

            elif value in self._types:
                token_seq.append(("type", self._escape(value).lstrip()))
                isNewLine = False

            elif type_ == 'whitespace' and (('\n' in value) or ('\r' in value)):
                if isNewLine:
                    continue

                line_count += 1
                isNewLine = True
                directive = False
                token_seq.append(("endline", "-"))


            elif type_ == 'whitespace' or type_ == 'comment' or type_ == 'nl':
                pass

            elif 'string' in type_:
                isNewLine = False
                token_seq.append(("string", "-")) #TODO format string

            elif type_ == 'name':
                isNewLine = False
                prev_id = True
                prev_name = value

            elif type_ == 'number':
                isNewLine = False
                token_seq.append(("number", "-"))

            elif 'char' in type_ or value == '':
                token_seq.append((type_, "-"))
                isNewLine = False
            elif type_ == 'directive':
                token_seq.append(("directive", "-"))
                isNewLine = False
                directive = True

            else:
                converted_value = self._escape(value).replace('~', 'TiLddE')
                token_seq.append((type_, converted_value))
                isNewLine = False
        return token_seq


    def tokenize_function(self, code, function_name ,keep_format_specifiers=False, keep_names=False,
                 keep_literals=False, custom_names = []):
        line_count = 1
        name_sequence = []
        if(custom_names == []): name_sequence = self._calls
        else : name_sequence = custom_names
        regex = '%(d|i|f|c|s|u|g|G|e|p|llu|ll|ld|l|o|x|X)'
        isNewLine = True
        # Get the iterable
        my_gen = self._tokenize_code(code)
        prev_id = True
        prev_name = ""
        directive = False;
        prevTok = []
        real_tok = []
        false_tok = []
        token_seq = false_tok
        line_tok =  []
        curly_brakets = 0; 
        func_found = False
        change = False
        definition = False
        token_lookahead = []
        stop = False
    #    print(function_name)
        while True:
            if token_lookahead != []:
                token = token_lookahead.pop(0)
            else:
                if stop == False:
                    try:
                        token = next(my_gen)
                    except StopIteration:
                        token_seq += line_tok
                        break
                else:
                    token_seq += line_tok
                    break
                    
            if isinstance(token, Exception):
                return token
          #  print(token)
            type_ = str(token[0])
            value = str(token[1])
            if(prev_id == True):
                if(type_ == 'op'  and value == '(' and directive == False):
   #                 print("----")
                 #  print(prevTok)
                    for tok in reversed(prevTok[:-1]):
  #                      print(tok)
                        if str(tok[0]) == 'whitespace' and (('\n' in str(tok[1]))  or ('\r' in str(tok[1]))):
                            definition = False
                            break

                        elif str(tok[0]) == 'whitespace': continue
                        elif str(tok[0]) == 'name' and str(tok[1]) != 'return' and str(tok[1]) != 'else' :
                            definition = True
                            break
                        elif str(tok[0]) == 'op':
                            if tok[1] != '*':
                                definition = False
                                break
                            else: continue
                        elif str(tok[0]) == 'name' and str(tok[1]) == 'return':
                            definition = False
                            break
                    if(definition == True):
                #        print("def found " + prev_name)
                        while True:
                            try:
                                token_fut = next(my_gen)
                            except StopIteration:
                                stop = True
                                break
                            token_lookahead.append(token_fut)
                      #      print(token_fut)
                            if isinstance(token_fut, Exception):
                                break

                            if str(token_fut[0]) == 'op' and str(token_fut[1]) == '{':
                                line_tok.append(("FuncDef", prev_name))
                                prevTok.clear()
                                if prev_name == function_name:
                                   # print(function_name)
                                    token_seq = real_tok;
                                    func_found = True
                                break
                            if str(token_fut[0]) == 'op' and str(token_fut[1]) == ';':
                                line_tok.append(("id", "func"))
                                prevTok.clear()
                                break
                            
                    elif(keep_names == True):
                        #define calls and function style macros call
                        line_tok.append(("id", prev_name))
                   #     prevTok.clear()
                    else:
                        #define calls and function style macros call
                        line_tok.append(("id", "func"))
                 #       prevTok.clear()
                elif type_ != 'whitespace':
                    #define vars and macro definitions
                    line_tok.append(("id", "var"))
              #      prevTok.clear()

            if type_ != 'whitespace' or  (type_ == 'whitespace'  and ('\n' in str(token[1]))  or ('\r' in str(token[1]))) and type_ != 'comment':
                prev_id = False
                prev_name = ""
                prevTok.append(token)
            if type_ == 'op' and func_found:
                if value == '{': 
                    curly_brakets +=1
                if value == '}':
                    curly_brakets -=1
                    if curly_brakets == 0:
                        func_found = False
                        change = True
                        #Wait until newline
            
            if value in self._keywords:
                line_tok.append(("keyword", self._escape(value)))
                isNewLine = False

            elif type_ == 'include':
                line_tok.append(("include", self._escape(value).lstrip()))
                isNewLine = False

            elif value in name_sequence:
                line_tok.append(("APICall", self._escape(value).lstrip()))
                isNewLine = False

            elif value in self._types:
                line_tok.append(("type", self._escape(value).lstrip()))
                isNewLine = False

            elif type_ == 'whitespace' and (('\n' in value) or ('\r' in value)):
                if isNewLine:
                    continue
                line_count += 1
                isNewLine = True
                directive = False
                line_tok.append(("endline", "-"))
                token_seq += line_tok
                line_tok.clear()
        #        prevTok.clear()
    #            del prevTok[0:-2]
                if change == True:
                    token_seq = false_tok
                    change = False

            elif type_ == 'whitespace' or type_ == 'comment' or type_ == 'nl':
                pass

            elif 'string' in type_:
                isNewLine = False
                line_tok.append(("string", "-")) #TODO format string
                
            elif type_ == 'name':
                isNewLine = False
                prev_id = True
                prev_name = value

            elif type_ == 'number':
                isNewLine = False
                line_tok.append(("number", "-"))

            elif 'char' in type_ or value == '':
                line_tok.append((type_, "-"))
                isNewLine = False
            elif type_ == 'directive':
                line_tok.append(("directive", "-"))
                isNewLine = False
                directive = True

            else:
                converted_value = self._escape(value).replace('~', 'TiLddE')
                line_tok.append((type_, converted_value))
                isNewLine = False

        return real_tok
    
        
    def tokenize_tostring(self, code, keep_format_specifiers=False, keep_names=False,
                 keep_literals=False, custom_names = []):
        result = '0 ~ '

        names = ''
        line_count = 1
        name_dict = {}
        name_sequence = []

        regex = '%(d|i|f|c|s|u|g|G|e|p|llu|ll|ld|l|o|x|X)'
        isNewLine = True

        # Get the iterable
        my_gen = self._tokenize_code(code)
        prev_id = True
        prev_name = ""
        directive = False;
        prevTok = []
        while True:
            try:
                token = next(my_gen)
            except StopIteration:
                break

            if isinstance(token, Exception):
                return '', '', ''

            type_ = str(token[0])
            value = str(token[1])
            definition = False
            if(prev_id == True):
                if(type_ == 'op'  and value == '(' and directive == False):
                    for tok in reversed(prevTok[:-1]):
                        if tok[0] == "whitespace": continue
                        elif tok[0] == "name":
                            definition = True
                            break
                        elif tok[0] == "op":
                            if tok[1] != "*": break
                            else: continue
                    if(definition == True):
                        result += '_<FuncDef>_' + '_' + prev_name  + '_@ '  #define functions
                        prevTok.clear()
                    elif(keep_names == True):
                        result += '_<id>_' + '_' + prev_name  + '_@ '  #define calls and function style macros call
                    else:
                        result += '_<id>_' + '_<func>_@ '  #define calls and function style macros call
                else:
                    result += '_<id>_' + '_<var>_@ '  #define vars and macro definitions

            prev_id = False
            prev_name = ""
            prevTok.append(token)
            if value in self._keywords:
                result += '_<keyword>_' + self._escape(value) + ' '
                isNewLine = False

            elif type_ == 'include':
                result += '_<include>_' + self._escape(value).lstrip() + ' '
                isNewLine = False

            elif value in self._calls:
                result += '_<APIcall>_' + self._escape(value) + ' '
                isNewLine = False

            elif value in self._types:
                result += '_<type>_' + self._escape(value) + ' '
                isNewLine = False

            elif type_ == 'whitespace' and (('\n' in value) or ('\r' in value)):
                if isNewLine:
                    continue

                result += ' '.join(list(str(line_count))) + ' ~ '
                line_count += 1
                isNewLine = True
                directive = False

            elif type_ == 'whitespace' or type_ == 'comment' or type_ == 'nl':
                pass

            elif 'string' in type_:
                matchObj = [m.group().strip()
                            for m in re.finditer(regex, value)]
                if matchObj and keep_format_specifiers:
                    for each in matchObj:
                        result += each + ' '
                else:
                    result += '_<string>_' + ' '
                isNewLine = False

            elif type_ == 'name':
#                result += '_<id>_' + '_<var>_@ '  #define vars and macros definition
                isNewLine = False
                prev_id = True
                prev_name = value

            elif type_ == 'number':
                if keep_literals:
                    result += '_<number>_' + self._escape(value) + '# '
                else:
                    result += '_<number>_' + '# '
                isNewLine = False

            elif 'char' in type_ or value == '':
                result += '_<' + type_.lower() + '>_' + ' '
                isNewLine = False
            elif type_ == 'directive':
                result += '_<' + type_ + '>_'
                isNewLine = False
                directive = True

            else:
                converted_value = self._escape(value).replace('~', 'TiLddE')
                result += '_<' + type_ + '>_' + converted_value + ' '

                isNewLine = False

        result = result[:-1]
        names = names[:-1]

        if result.endswith('~'):
            idx = result.rfind('}')
            result = result[:idx + 1]

        return self._sanitize_brackets(result), name_dict, name_sequence

