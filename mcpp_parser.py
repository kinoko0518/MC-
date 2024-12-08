import re
import mcpt

# インデントの深さ+コードの内容を返す
def preparser(raw:str) -> "list[tuple[int, str]]":
    res = []
    # 後にバックスラッシュが続かない改行またはセミコロンで分割
    splitted = re.split("\n(?!\\))|;", raw)
    i = 0
    while i <= len(splitted)-1:
        # インデントの深さを数える
        indent = 0
        for o in range(len(splitted[i])):
            if splitted[i][o] != " ":
                if o % 4 != 0:
                    print("Invalid indent. The amount of space must be multiple of 4.")
                    break
                indent = int(o / 4)
                break
        splitted[i] = str.strip(splitted[i])

        # コメントを処理
        if splitted[i][0] == "#":
            splitted.pop(i)
        elif splitted[i].find("#") != -1:
            splitted[i] = splitted[i].split("#")[0]
        else:
            res.append((indent, splitted[i]))
            i += 1
    
    return (res)

# 演算子(OPeRaTor)の正規表現
oprt = "[\+\-\*\/\%]"
# 式(FoRMuLa)の正規表現
frml = "(\s*\w+\s*[\+\-\*\/\%]?)+"

class ParseTaskInfo():
    TEMP = mcpt.Scoreboard("TEMP", ["SYS"])

    def __init__(self) -> None:
        self.__current_scope:list[str] = []
        self.variables:dict[str, mcpt.Scoreboard] = {}
        
    @property
    def current_scope(self):
        return self.__current_scope
    
    def set_scope(self, new_scope:"list[str]"):
        res:str = self.destruct_local(new_scope)
        print(type(self.__current_scope), type(new_scope))
        self.__current_scope = new_scope
        return res

    def destruct_local(self, new_scope:"list[str]"):
        res:list[str] = []
        for i in range(len(self.variables.keys)):
            current_key = self.variables.keys[i]
            if len(self.variables[current_key].scope) >= len(new_scope):
                res.append(self.variables[current_key].freement)
        return "\n".join(res)
    
    def guess_type(self, raw:str) -> "mcpt.Scoreboard|int":
        if re.match("[0-9]+", raw):
            return int(raw)
        elif raw.isidentifier():
            if not raw in self.variables.keys():
                self.variables[raw] = mcpt.Scoreboard(raw, self.current_scope)
            return self.variables[raw]

    def formula_to_tokens(self, raw:str) -> "list[str|int|mcpt.Scoreboard]":
        begin:int = 0
        res:"list[str|int|mcpt.Scoreboard]" = []
        if not re.match(frml, raw):
            print("Can't parse invalid formula.")
        for i in range(len(raw)):
            if raw[i] in ["+", "-", "*", "/", "%", "(", ")"]:
                value = self.guess_type(str.strip(raw[begin:i]))
                operator = raw[i]
                res += [value, operator]
                begin = i+1
        res += [self.guess_type(str.strip(raw[begin:]))]
        return res
    
    def split_logical_formula(self, raw:str) -> "list[str]":
        begin:int = 0
        res:"list[str]" = []
        if not re.match(frml, raw):
            print("Can't parse invalid formula.")
        for i in range(len(raw)):
            if raw[i] in ["!", "&", "|"]:
                value = raw[begin:i]
                operator = raw[i]
                res += [value, operator]
                begin = i+1
        res += [str.strip(raw[begin:])]
        return res

    # a = 1 + b - 3 * c / 5 のようなstr型の式をマイクラコマンドにパルスする
    # 例 : 
    #   a = 1 + 2(ソースコード) ->
    #   a << 1, a + 2(抽象構造木) ->
    #   scoreboard players set #MCPP.a MCPP.var 1
    #   scoreboard players add #MCPP.a MCPP.var 1(コマンド)
    def parse_assignment(self, raw:str) -> str:
        lhs = "\w+\s*"
        oper_eq = "[\+\-\*\/\%]?="

        var_name = ""
        formula = self.formula_to_tokens(str.strip(raw.split("=")[1]))

        # 下ごしらえ
        target:mcpt.Scoreboard

        # - 変数の名前を推測する
        if not re.match(oprt, raw[raw.find("=") - 1]):
            var_name = str.strip(raw.split("=")[0])
        else:
            var_name = str.strip(raw.split("=")[0][0:-2])
        # - 変数がすでに存在していればそれを取得、なければ新規作成
        if var_name in self.variables.keys():
            target = self.variables[var_name]
        else:
            target = mcpt.Scoreboard(var_name, self.current_scope, int)
            self.variables[var_name] = target
        
        # 代入だったら
        if re.match(lhs+"="+frml, raw):
            res = ["# " + raw, target << formula[0]]
            form_solved = mcpt.solve_formula(target, formula[1:])
            if form_solved: res += [form_solved]
            return "\n".join(res)
        # 代入演算子だったら
        elif re.match(lhs+oper_eq+frml, raw):
            operation = raw[raw.find("=")-1] + "="

            # ±= 一個ならもっと短く書ける
            if len(formula) == 1:
                if operation == "+=":
                    return "\n".join(["# " + raw, target + formula[0]])
                elif operation == "-=":
                    return "\n".join(["# " + raw, target - formula[0]])
            
            # 短く書けるケースにあてはまらなかったときの処理
            temp_opr = mcpt.solve_formula(self.TEMP, formula[1:])
            result = ["# " + raw, self.TEMP << formula[0]]
            if temp_opr: result += [temp_opr]
            result += [target.operation(operation, self.TEMP)]
            return "\n".join(result)
        else:
            print("Invalid assignment. As it may be compiler's bug, please make issue on GitHub with how it happened.")
    
    def parse_logical_formula(self, raw:str):
        tokens:list[str] = self.split_logical_formula(raw)
        return tokens

    def parse_a_line(self, raw:str) -> str:
        # 代入系だったら
        if re.match("\w\s+[+-/*%]?="+frml, raw):
            return self.parse_assignment(raw)

def parser(raw:str) -> str:
    res:list[str] = []
    task = ParseTaskInfo()
    preparsed = preparser(raw)
    for i in range(len(preparsed)-1):
        res += [task.parse_a_line(preparsed[i][1], task)]
    return "\n".join(res)