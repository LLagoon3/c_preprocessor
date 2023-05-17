import re
from collections import deque

DATA_TYPE = ['void', 
             'short', 
             'int', 
             'long', 
             'unsinged short', 
             'unsinged int', 
             'unsinged long', 
             'char', 
             'unsinged char', 
             'float', 
             'double']

PATH = 'code_file.c'


class processor():
    
    def __init__(self) -> None:
        self.datatype_list = deque()
        self.symbol = {'\n': ' $linespace ',
                       #',': ' , ',
                       #'var': ' $var',
                       ',': ' $comma ',
                       '(': ' $bracket ',
                       ')': ' $cbracket ',
                       ';': ' $semicol '}
        self.re_dict = {
            'macro': re.compile('\#include+\s+\"\w+\.h\"'),
            'varfunc': re.compile("\$datatype\s+\w+\s+\$bracket[\s*var\s+\$datatype\s+\w+\s*\$comma]*\s*var\s+\$datatype\s+\w+\s*\$cbracket"),
            'defunc': re.compile("\$datatype\s+\w+\s+\$bracket[\s*var\s+\$datatype\s*\$comma]*\s*var\s+\$datatype\s*\$cbracket"),
            'callfunc': re.compile("\s*\w+\s*\$bracket[\s*\w+\s*\$comma]*\s*\w+\s*\$cbracket"),
            'define': re.compile("\s*\#define\s+\w+\s+\w+"),
            'find_name': re.compile("\w+"),
        }
        
    def read_file(self, path: str) -> list:
        file = open(path)
        res_list = list()
        for line in file:
            res_list.append(line)
        file.close()
        return res_list
        
    def encoding(self, line: str) -> list:
        for key, val in self.symbol.items():
            line = line.replace(key, val)
        line = line.split(' ')
        for index, word in enumerate(line):
            if word in DATA_TYPE:
                self.datatype_list.append(word)
                line[index] = '$datatype'
        return (deque(filter(None, line)))
    
    def decoding(self, stack: list) -> str:
        res_str = ""
        for index, word in enumerate(stack):
            if word == '$datatype': word = self.datatype_list.popleft()
            res_str += " " + word + " "
        for key, val in self.symbol.items():
            res_str = res_str.replace(val, key)
        res_str = re.sub('[\s]+', ' ', res_str)
        return res_str
    
    def processMacro(self, word_list: list) -> list:
        if word_list[0] == "#include":
            file = self.read_file("./" + word_list[1].replace('"', ''))
            res = self.execute_(file)
            return [res]
        
    def processDefine(self, word_list: deque, defineData: dict) -> deque:
        res_stack = deque()
        while word_list:
            res_stack.append(word_list.popleft())
            if res_stack[-1] in defineData.keys():
                tmp = res_stack.pop()
                res_stack.append(defineData[tmp])
        return res_stack
    
    def processVar(self, word_list: deque, varFunc: set, varData: set) -> list:
        res_stack = deque([word_list.popleft()])
        if res_stack[0] in varFunc:
            bracket = False
            while word_list:
                tmp = word_list.popleft()
                if tmp == '$cbracket': bracket = False
                if bracket and tmp != '$comma':
                    res_stack.append('&')
                elif tmp == '$bracket': bracket = True
                res_stack.append(tmp)
        elif res_stack[0] == '$datatype':
            while word_list:
                res_stack.append(word_list.popleft())
                if res_stack[-1] == 'var':
                    res_stack.pop()
                elif res_stack[-1] == '$datatype':
                    res_stack.append('*')
        else:
            while word_list:
                if res_stack[-1] in varData:
                    tmp = res_stack.pop()
                    res_stack.append('*')
                    res_stack.append(tmp)
                res_stack.append(word_list.popleft())
                
        return res_stack, varFunc, varData
        
    def execute_(self, file):
        
        varFunc, varData, defineData = set(), set(), dict()
        result = ""
        
        for line in file:
            word_list = self.encoding(line)
            line = ' '.join(word_list)
            if '}' in line: 
                varData = set()

            if self.re_dict['macro'].findall(line):
                result += self.processMacro(word_list)[0] + "\n"
                continue
            elif self.re_dict['define'].findall(line):
                defineData[word_list[1]] = word_list[2]
                continue
            elif self.re_dict['defunc'].findall(line):
                varFunc.add(word_list[1])
                word_list, varFunc, varData = self.processVar(word_list, varFunc, varData)
            elif self.re_dict['varfunc'].findall(line):
                varFunc.add(word_list[1])
                for index, word in enumerate(word_list):
                    if word == '$datatype' and index != 0: varData.add(word_list[index + 1])
                word_list, varFunc, varData = self.processVar(word_list, varFunc, varData)
            elif self.re_dict['callfunc'].findall(line):
                word_list, varFunc, varData = self.processVar(word_list, varFunc, varData)
            elif varData & set(word_list):
                word_list, varFunc, varData = self.processVar(word_list, varFunc, varData)
            if set(defineData.keys()) & set(word_list):
                word_list = self.processDefine(word_list, defineData)
            result += self.decoding((word_list)) + '\n'

        return result
        
    def debug(self):
        text = '$datatype swap $bracket var $datatype x , var $datatype y $cbracket { $linespace'
        text2 = '$datatype main $bracket $cbracket { $linespace'
        varfunc = re.compile("\$datatype\s+\w+\s+\$bracket[\s*var\s+\$datatype\s+\w+\s*\,]*\s*var\s+\$datatype\s+\w+\s*\$cbracket")
        varfunc_name = re.compile("\w+")
        print(varfunc.findall(text))
        print(varfunc_name.findall(text2)[1])
        callfunc = re.compile("\s*\w+\s*\$bracket[\s*\w+\s*\$comma]*\s*\w+\s*\$cbracket")
        text = "swap $bracket a $comma b $cbracket $semicol $linespace"
        text = '#include "myHeader.h" $linespace'
        text2 = '$linespace'
        defunc = re.compile('\#include\s+\"\w+\.h\"')
        print(defunc.findall(text))
        print(defunc.findall(text2))
        varData = {'a', 'b'}
        word = ['c', 'a', 'k', 'e']
        print(varData & set(word))
            
    # def processVar(self, stack: list, symbol: str) -> list:
    #     if stack[-1] == '!$datatype': 
    #                     stack.append(symbol)
    #     else:
    #         tmp = stack.pop()
    #         stack.append(symbol)
    #         stack.append(tmp)
        
    # def execute(self, file: list) -> dict:
    #     varFunc, varData, globalData = set(), set(), set()
    #     for line in file:
    #         line = self.encoding(line)
    #         stack = list()
    #         var, varfunc = False, False
    #         for index, word in enumerate(line):
    #             if '#' in word: self.processMacro(line)
    #             elif word == 'var': ## var 변수가 존재하면 varmod && varData에 변수명 저장
    #                 var = True
    #                 if ('$' not in line[index + 2]): varData.add(line[index + 2])
    #                 # if not data_name == []: varFunc.add(data_name.pop())
    #                 continue
    #             elif word == '}': varData = set() ## 함수 끝나면 varData 비우기
    #             elif (word in varFunc) and (stack == [] or stack[-1] != '$datatype'): varfunc = True ## 선언된 함수이면 varfunc모드
    #             elif word == '$datatype' and (len(line) == 2) and not varfunc: ## type + 이름, 함수 모드가 아니면 전역변수
    #                 globalData.add(line[1])
    #                 break
    #             elif word == '$datatype' and (line[index + 2] == '$bracket'): varFunc.add(line[index + 1]) ## type + 이름 + () 형태로 선언된 함수면 varFunc에 함수명 저장

    #             if (word in varData) or (var and (word == '$comma' or word == '$cbracket')): ## 함수 파라메터 *처리
    #                 stack.append(word)
    #                 self.processVar(stack, '*')
    #                 var = False
    #                 continue
    #             if varfunc and (word == '$comma' or word == '$cbracket'): ## 함수 호출 시 파라메터 &처리
    #                 self.processVar(stack, '&')
    #                 if word == '$cbracket': varfunc = False
                
    #             stack.append(word)
    #         #print(line)
    #         print((stack))
    #     return {
    #         'data': varData, #변수명
    #         'global': globalData, #
    #         'func': varFunc, #함수명
    #         'stack': stack   #전처리 결과
    #     }

        
        
p = processor()
print(p.execute_(p.read_file(PATH)))
# p.debug()