import sys, os, random, string, shutil

raw_code_path = open(sys.argv[1], 'r', encoding="utf-8")
raw_code = raw_code_path.read().split("\n")

code_name = raw_code_path.name.split("\\")[-1].replace(".mcpp", "")

compiled = "#System->\nscoreboard objectives add MCPP.num dummy\n#<-System\n"

variables = []
constant_dummies = []
functions = {}

pointer = 0



# 開始前処理
__path__ = "\\".join(sys.argv[1].split("\\")[0:-1])

raw_code[0] = raw_code[0].replace("\ufeff", "") #UFT-8に設定したときの邪魔な\ufeffを消す

shutil.rmtree(__path__ + r"\{}_compiled".format(code_name), True)
os.makedirs(__path__ + r"\{}_compiled".format(code_name))
compiled_folder = __path__ + r"\{}_compiled".format(code_name)


def make_mcfunction(code:str, name:str, path:str):
    __file__ = open(path + r"\{}.mcfunction".format(name), 'w', encoding = "utf-8_sig")
    __file__.write(code)
    __file__.close()

def compile(_raw_code:str, current_dir:str):
    valid_opeartions = ["+", "-", "*", "/", "%"]

    global pointer
    result = ""

    if not (_raw_code.replace("    ", "") == "" or _raw_code.startswith("#")):
        _raw = _raw_code.split(" ")

        def get_defined_variable(variable_name:str):
            for _i in range(len(variables)):
                if variables[_i][0] == variable_name:
                    return _i
            return -1

        def get_type(variable_name:str):
            return variables[get_defined_variable(variable_name)][1]


        # 変数宣言関数群　プロトコル -> [変数名, 変数型, 変数データ1, 変数データ2...]
        def define_int_variable(variable_name:str, value:int): #int型変数を宣言する関数 プロトコル -> [変数名, int, 数値]
            variables.append([variable_name, "int", value])
            add_code("scoreboard players set #{}.{} num {}".format(code_name, variable_name, value))
        
        def define_float_variable(variable_name:str, value:float): #float型変数を宣言する関数 プロトコル -> [変数名, float, 生の値, 倍率]
            magnification = 10 ** len(str(value).rsplit(".")[1].rsplit("0")[0]) # 倍率を計算する
            variables.append([variable_name, "float", float(value), magnification]) # 変数にデータを保存する
            add_code("scoreboard players set #{}.MAGNIFICATIONS.{} num {}".format(code_name, variable_name, magnification)) # 倍率をスコアボードに保存しておく
            add_code("scoreboard players set #{}.{} num {}".format(code_name, variable_name, int(float(value) * magnification))) # 整数化した数値をスコアボードに代入する
        
        def set_value(variable_name:str, value:str): #変数に代入する関数
            global variables

            __type__ = "none"
            
            # 型を判別
            if value.isascii():
                if float(value).is_integer(): # 整数だったら
                    if value.endswith(".0"): #明示的にfloat型で定義されていたら
                        __type__ = "float"
                    else:
                        __type__ = "int"
                else: # float型だったら
                    __type__ = "float"
            else:
                raise ValueError("Invalid type. The value is {}".format(value))
            
            if get_defined_variable(variable_name) == -1: # 変数が宣言されていなければ
                if __type__ == "int":
                    define_int_variable(variable_name, value)
                if __type__ == "float":
                    define_float_variable(variable_name, value)
            else: # 変数が宣言されていれば
                if get_type(variable_name) == __type__: # 変数と値の型が一致していることを確認して
                    if __type__ == "int":
                        variables[get_defined_variable(variable_name)][2] = int(value)
                        add_code("scoreboard players set #{}.{} num {}".format(code_name, variable_name, value))
                    if __type__ == "float":
                        magnification = len(str(value).rsplit(".")[1])
                        variables[get_defined_variable(variable_name)][2] = float(value)
                        add_code("scoreboard players set #{}.{} num {}".format(code_name, variable_name, int(float(value) * (10 ** magnification))))
                        add_code("scoreboard players set #{}.MAGNIFICATION.{} num {}".format(code_name, variable_name, magnification))
                else:
                    return_syntax_error("The given value has different type from the given variable")
        
        def int_to_float(variable_name:string):
            add_code("scoreboard players set #{}.MAGNIFICATION.{} num 1".format(code_name, variable_name))
            variables[get_defined_variable(variable_name)][1] = "float"
            variables[get_defined_variable(variable_name)][2] = float(variables[get_defined_variable(variable_name)][2])
            variables[get_defined_variable(variable_name)].append(1)



        def constant(constant_value:int): #定数が存在していればその定数を、存在していなければ新規作成して返す
            global constant_dummies

            constant_name = "#{}.CONSTANT.{}".format(code_name, constant_value)
            
            if not constant_name in constant_dummies:
                add_code("scoreboard players set {} MCPP.num {}".format(constant_name, constant_value))
                constant_dummies.append(constant_name)
            
            return constant_name

        def add_code(__code__:str):
            if not __code__ == None:
                nonlocal result
                if result == "":
                    result = __code__
                else:
                    result += "\n" + __code__
        
        def add_comment(__comment__:str):
            nonlocal result
            if result == "":
                result = "#" + __comment__
            else:
                result += "\n#" + __comment__
        
        def convert_to_operation(target:str, source:str, operation:str):
            float_actuality = 8
            
            if (not get_defined_variable(target) == -1 and get_type(target) in ["int", "float"]): # targetがintかfloatの変数ならば
                if (source.isascii() or (not get_defined_variable(source) == -1 and get_type(source) in ["int", "float"])): #sourceが数字かintかfloatの変数であるならば
                    __source__ = source
                    __source_magnification__ = 1
                    __is_source_float__ = "." in str(source)

                    if __is_source_float__: # sourceが小数を含む場合の処理
                        if get_type(target) == "int": # targetがint型だったらfloat型に変換する
                            int_to_float(target)
                        
                        __source__ = float(source) * variables[get_defined_variable(target)][3]
                        if "." in str(__source__):
                            __source_magnification__ = 10 ** len(str(__source__).rsplit(".")[1])
                            __source__ = int(__source__ * __source_magnification__) # sourceを整数にする
                            # 倍率を揃える
                            variables[get_defined_variable(target)][3] *= __source_magnification__
                            add_code("scoreboard players operation #{}.MAGNIFICATION.{} MCPP.num *= {} MCPP.num".format(code_name, target, constant(__source_magnification__)))
                            add_code("scoreboard players operation #{} MCPP.num *= {} MCPP.num".format(target, constant(__source_magnification__)))
                    
                    if (operation == "+" or operation == "-") and source.isascii(): # 整数の足し算、引き算だともっと短く書けるのでその処理
                        __add_or_remove__:str
                        if operation == "+":
                            __add_or_remove__ = "add"
                        else:
                            __add_or_remove__ = "remove"

                        # 足す/引く
                        add_code("scoreboard players {} #{} MCPP.num {}".format(__add_or_remove__, target, __source__))
                        
                        if operation == "+":
                            variables[get_defined_variable(target)][2] += float(source)
                        elif operation == "-":
                            variables[get_defined_variable(target)][2] -= float(source)
                    
                    elif operation == "/" and "." in str(variables[get_defined_variable(target)][2] / float(source)): # 計算が割り算かつ結果が小数を含むなら
                        if get_type(target) == "int": # targetがint型だったらfloat型に変換する
                            int_to_float(target)
                        __result_magnification__ = 10 ** min(len(str(variables[get_defined_variable(target)][2] / float(source)).rsplit(".")[1]), float_actuality)
                        add_code("scoreboard players operation #{}.MAGNIFICATION.{} MCPP.num *= {} MCPP.num".format(code_name, target, constant(__result_magnification__)))
                        add_code("scoreboard players operation #{} MCPP.num *= {} MCPP.num".format(target, constant(__result_magnification__)))
                    
                    else:
                        if operation in valid_opeartions:
                            if source.isascii():
                                add_code("scoreboard players operation #{} MCPP.num {}= #{} MCPP.num".format(target, operation, constant(__source__)))
                            else: # sourceが変数だった場合
                                add_code("scoreboard players operation #{} MCPP.num {}= #{} MCPP.num".format(target, operation, source))
                        else:
                            raise ValueError("Given operation is invalid. Invallid operation -> " + operation)
                else:
                    return_syntax_error("The source must be number or defined float/int type variable")
            else:
                return_syntax_error("The target must be float/int type variable")
        
        def return_syntax_error(__error__):
            print("\033[31m!SYNTAX ERROR! {} [Line {}]\033[0m".format(__error__, pointer))
        
        def return_warning(__warning__):
            print("\033[33mWarning: {} [Line {}]\033[0m".format(__warning__, pointer))



        # 関数を変換
        if _raw[0].endswith("()"):
            if _raw[0][0:-2] in functions.keys():
                add_code(functions[_raw[0][0:-2]])



        # 代入の処理
        if _raw[1] == "=":
            add_comment(" ".join(_raw))
            if not _raw[0] == _raw[2]:
                set_value(_raw[0], _raw[2])
            if len(_raw) >= 3: # 代入に計算が含まれていた場合の処理
                for _i in range(3, len(_raw) - 1):
                    if not _i % 2 == 0:
                        if _raw[_i] in valid_opeartions:
                            convert_to_operation(_raw[0], _raw[_i + 1], _raw[_i])
                        else:
                            return_syntax_error("Invalid operation")



        #四則演算の処理
        if _raw[0] in variables and _raw[1].rsplit("=")[0] in valid_opeartions:
            add_comment("{} {} {}".format(_raw[0], _raw[1][0], _raw[2]))
            convert_to_operation(_raw[0], _raw[2], _raw[1][0])



        # インデントされていた場合の処理
        if ":" in _raw[-1]:
            # インデント内をコンパイルする
            def count_indent(__input__:str): # インデントの数を数える関数
                _i = 0
                while _i in range(len(__input__)):
                    if not __input__[-_i].isspace():
                        break
                    else:
                        _i += 1
                return _i

            global pointer
            global raw_code

            __indent__ = count_indent(raw_code[pointer + 1])
            __compiled_in_indents__ = []

            while __indent__ == count_indent(raw_code[pointer + 1]):
                pointer += 1
                __compiled_in_indents__.append(compile(raw_code[pointer].replace("    ", ""), current_dir))
                if pointer + 1 >= len(raw_code): # コードの終わりまで来たらbreak
                    break

            os.makedirs(current_dir + r"\__a_indent_under__", exist_ok = True)
            __functin_name__ = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

            __result_in_indent__ = "function " + r"__a_indent_under__/{}".format(__functin_name__)

            if _raw[0] == "if":
                if _raw[1] == "not":
                    add_code("execute {} {}".format("unless " + " ".join(_raw[2:]).rsplit(":")[0], __result_in_indent__))
                else:
                    add_code("execute {} {}".format("if " + " ".join(_raw[1:]).rsplit(":")[0], __result_in_indent__))
            
            if _raw[0] == "func":
                functions[_raw[1].rsplit(":")[0]] = __result_in_indent__
            
            if _raw[0] == "while":
                __compiled_in_indents__.append("execute {} {}".format("unless " + " ".join(_raw)[1:-1].rsplit(":")[0], __result_in_indent__))
            
            make_mcfunction("\n".join(__compiled_in_indents__), __functin_name__, current_dir + r"\__a_indent_under__")

    return result


# ここから先がメイン処理
if raw_code_path.name.split("\\")[-1].split(".")[-1] == "mcpp": # 拡張子が.mcppか確認する
    while pointer in range(len(raw_code)):
        code = raw_code[pointer]
        __compiled__ = compile(code, compiled_folder)
        if __compiled__.startswith("!SYNTAX ERROR!"):
            print(__compiled__)
        if not len(__compiled__) == 0:
            compiled += "\n" + __compiled__
        pointer += 1
else:
    raise Exception('Given file is not a .mcpp.')

compiled += "\n\n#System->\nscoreboard objectives remove MCPP.num\n#<-System"
make_mcfunction("".join(compiled), code_name, compiled_folder)