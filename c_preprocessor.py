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

PATH = './code_file.txt'


class processor():
    
    def __init__(self, path: str) -> None:
        self.file = open(path)
        self.datatype_list = deque()
        self.symbol = {'\n': ' $linespace ',
                       ',': ' $comma ',
                       '(': ' $bracket ',
                       ')': ' $cbracket ',
                       ';': ' $semicol '}
        
    def decoding(self, line: str) -> list:
        for key, val in self.symbol.items():
            line = line.replace(key, val)
        line = line.split(' ')
        for index, word in enumerate(line):
            if word in DATA_TYPE:
                self.datatype_list.append(word)
                line[index] = '$datatype'
        return (list(filter(None, line)))
    
    def encoding(self, stack: list) -> str:
        res_str = ""
        for index, word in enumerate(stack):
            if word == '$datatype': word = self.datatype_list.popleft()
            res_str += " " + word + " "
        for key, val in self.symbol.items():
            res_str = res_str.replace(val, key)
        res_str = re.sub('[\s]+', ' ', res_str)
        return res_str
    
    def processVar(self, stack: list, symbol: str) -> list:
        if stack[-1] == '!$datatype': 
                        stack.append(symbol)
        else:
            tmp = stack.pop()
            stack.append(symbol)
            stack.append(tmp)
        
    def execute(self) -> None:
        varFunc, varData = set(), set()
        for line in self.file:
            line = self.decoding(line)
            stack = list()
            var, varfunc = False, False
            for index, word in enumerate(line):
                if word == 'var': ## var 변수가 존재하면 varmod && varData에 변수명 저장
                    var = True
                    if ('$' not in line[index + 2]): varData.add(line[index + 2])
                    # if not data_name == []: varFunc.add(data_name.pop())
                    continue
                elif word == '}': varData = set() ## 함수 끝나면 varData 비우기
                elif (word in varFunc) and (stack == [] or stack[-1] != '$datatype'): varfunc = True ## 선언된 함수이면 varfunc모드
                elif word == '$datatype' and (line[index + 2] == '$bracket'): varFunc.add(line[index + 1]) ## type + 이름 + () 형태로 선언된 함수면 varFunc에 함수명 저장

                if (word in varData) or (var and (word == '$comma' or word == '$cbracket')): ## 함수 파라메터 *처리
                    stack.append(word)
                    self.processVar(stack, '*')
                    var = False
                    continue
                if varfunc and (word == '$comma' or word == '$cbracket'): ## 함수 호출 시 파라메터 &처리
                    self.processVar(stack, '&')
                    if word == '$cbracket': varfunc = False
                
                stack.append(word)
            print(line)
            print(self.encoding(stack))
            
        
    def debug(self):
        print('$' not in '$comma')
    
p = processor(PATH)
p.execute()
