import sys, os, random, string, shutil

raw_code_path = open(sys.argv[1], 'r', encoding="utf-8")
raw_code = raw_code_path.read().split("\n")

code_name = raw_code_path.name.split("\\")[-1].replace(".mcpp", "")
dummy = "#" + code_name

compiled = "#System->\nscoreboard objectives add MCPP.num dummy\n#<-System\n".format(dummy)

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
    global pointer
    result = ""

    if not (_raw_code.replace("    ", "") == "" or _raw_code.startswith("#")):
        _raw = _raw_code.split(" ")

        def define_variable(variable_name:str): # 変数を宣言する関数
            global variables
            variables.append(variable_name)
        
        def set_value(variable_name:str, value:int): #変数に代入する関数
            global variables

            if variable_name in variables:
                add_code("scoreboard players set {} {} {}".format(dummy, variable_name, value))
            else:
                raise Exception("Undefined variable")
        
        def constant(constant_value:int):
            global constant_dummies

            constant_name = "#{}.CONSTANT.{}".format(code_name, constant_value)
            
            if not constant_name in constant_dummies:
                add_code("scoreboard players set {} MCPP.num {}".format(constant_name, constant_value))
            
            return constant_name

        def convert_to_operation(target:str, source:str, operation:str):
            if operation == "+" or operation == "-" or operation == "*" or operation == "/":
                if source.isdigit():
                    return "scoreboard players operation {} MCPP.num {}= {} MCPP.num".format("#" + target, operation, constant(source))
                if source in variables:
                    return "scoreboard players operation {} MCPP.num {}= {} MCPP.num".format("#" + target, operation, "#" + source)

        def add_code(__code__:str):
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



        # 関数を変換
        if _raw[0].endswith("()"):
            if _raw[0][0:-2] in functions.keys():
                add_code(functions[_raw[0][0:-2]])



        # 変数宣言の処理
        if _raw[0] == "var":
            define_variable(_raw[1])



        # 代入の処理
        if _raw[0] in variables and _raw[1] == "=":
            set_value(_raw[0], _raw[2])



        #四則演算の処理
        if _raw[0] in variables and (_raw[1] == "+=" or _raw[1] == "-=" or _raw[1] == "*=" or _raw[1] == "/="):
            operation = _raw[1][0]
            add_comment("{} {} {}".format(_raw[0], operation, _raw[2]))

            if (operation == "+" or operation == "-") and _raw[2].isdigit(): # 整数の足し算、引き算だともっと短く書けるのでその処理
                if operation == "+":
                    add_code("scoreboard players add {} MCPP.num {}".format("#" + _raw[0], _raw[2]))
                if operation == "-":
                    add_code("scoreboard players remove {} MCPP.num {}".format("#" + _raw[0], _raw[2]))
            else:
                add_code(convert_to_operation(_raw[0], _raw[2], operation))



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
            make_mcfunction("\n".join(__compiled_in_indents__), __functin_name__, current_dir + r"\__a_indent_under__")

            __result_in_indent__ = "function " + r"__a_indent_under__/{}".format(__functin_name__)

            if _raw[0] == "if":
                add_code("execute {} {}".format(" ".join(_raw).rsplit(":")[0], __result_in_indent__))
            
            if _raw[0] == "func":
                functions[_raw[1].rsplit(":")[0]] = __result_in_indent__
    return result


if raw_code_path.name.split("\\")[-1].split(".")[-1] == "mcpp":
    while pointer in range(len(raw_code)):
        code = raw_code[pointer]
        __compiled__ = compile(code, compiled_folder)
        if not len(__compiled__) == 0:
            compiled += "\n" + __compiled__
        pointer += 1
else:
    raise Exception('Given file is not a .mcpp.')

compiled += "\n\n#System->\nscoreboard objectives remove MCPP.num\n#<-System"
make_mcfunction("".join(compiled), code_name, compiled_folder)