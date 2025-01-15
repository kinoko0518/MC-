import random
import build_option as bil

def random_name(longness:int):
    res = ""
    pattern = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0".split(" ")
    for i in range(longness):
        res += pattern[random.randint(0, len(pattern)-1)]
    return res

class Scoreboard:
    def __init__(self, var_name:str, scope:"list[str]", mcpp_type:type = None) -> None:
        self.name = var_name
        self.scope = ["MCPP"] + scope
        self.type = mcpp_type
    
    @property
    def mc_name(self):
        if bil.is_raw_variable_name:
            return self.name
        else:
            return "#" + (".".join(self.scope) + "." if self.scope else "") + self.name
        

    def operation(self, operater:str, source):
        if type(source) == int:
            if operater == "+=":
                return self + source
            elif operater == "-=":
                return self - source
            temp = Scoreboard("TEMP", ["SYS"])
            return "\n".join([(temp << source), operate(self, operater, temp)])
        if type(source) == Scoreboard:
            return operate(self, operater, source)

    # 代入
    def __lshift__(self, source) -> str:
        if self.type == None:
            if is_bool(source):
                self.type = bool
            elif is_int(source):
                self.type = int
        
        # ToDo
        # ・LogicalFormulaを計算できるようにする
        if self.type is bool:
            if type(source) == bool:
                return "scoreboard players set {} {} {}".format(self.mc_name, bil.namespace, 1 if source else 0)
        elif self.type is int:
            if type(source) == int:
                return "scoreboard players set {} {} {}".format(self.mc_name, bil.namespace, str(source))
            if type(source) == Scoreboard:
                return operate(self, "=", source)
        else:
            print("Undefined assignment : {} and {}".format(self.type, type(source)))
    
    # 足し算
    def __add__(self, source) -> str:
        if self.type is int:
            if type(source) == int:
                return "scoreboard players add {} {} {}".format(self.mc_name, bil.namespace, str(source))
            if type(source) == Scoreboard:
                return self.operation("+=", source)
    
    # 引き算
    def __sub__(self, source) -> str:
        if type(source) == int:
            if type(source) == int: return "scoreboard players remove {} {} {}".format(self.mc_name, bil.namespace, str(source))
        if type(source) == Scoreboard:
            return self.operation("-=", source)
    
    # 掛け算
    def __mul__(self, source) -> str:
        if is_int(source):
            return self.operation("*=", source)
    
    # 割り算
    def __truediv__(self, source) -> str:
        if is_int(source):
            return self.operation("/=", source)
    
    # 比較演算
    def __eq__(self, other):
        if type(other) is int:
            return "if score {} {} matches {}".format(self.mc_name, bil.namespace, str(other))
        if type(other) is Scoreboard:
            return "if score {} {} = {} {}".format(self.mc_name, bil.namespace, other.mc_name, bil.namespace)
    
    # 比較演算(否定)
    def __ne__(self, other):
        if type(other) is int:
            return "unless score {} {} matches {}".format(self.mc_name, bil.namespace, str(other))
        if type(other) is Scoreboard:
            return "unless score {} {} = {} {}".format(self.mc_name, bil.namespace, other.mc_name, bil.namespace)
    
    # 比較演算(以上)
    def __le__(self, other):
        if type(other) is int:
            return "if score {} {} matches {}..".format(self.mc_name, bil.namespace, str(other))
        if type(other) is Scoreboard:
            return "if score {} {} >= {} {}".format(self.mc_name, bil.namespace, other.mc_name, bil.namespace)
    
    # 比較演算(以下)
    def __ge__(self, other):
        if type(other) is int:
            return "if score {} {} matches ..{}".format(self.mc_name, bil.namespace, str(other))
        if type(other) is Scoreboard:
            return "if score {} {} <= {} {}".format(self.mc_name, bil.namespace, other.mc_name, bil.namespace)
    
    @property
    def freement(self) -> str:
        return "scoreboard players reset {} {}".format(self.mc_name, bil.namespace)

class Version:
    def __init__(self, raw:str):
        version:list[int] = []
        if True:
            version_raw = raw.split(".")
            for i in range(len(version_raw)):
                version += [int(version_raw[i])]
    
    def __eq__(self, value):
        return self.version == value.version

    def __lt__(self, value):
        for i in range(max(len(self.version), len(value.version))):
            if self.version[i] < value.version[i]: return True
        return False
    
    def __gt__(self, value):
        for i in range(max(len(self.version), len(value.version))):
            if self.version[i] > value.version[i]: return True
        return False
    
    def get_packformat(self) -> int:
        if Version("1.13") <= self <= Version("1.14.4"):
            return 4
        elif Version("1.15") <= self <= Version("1.16.1"):
            return 5
        elif Version("1.16.2") <= self <= Version("1.16.5"):
            return 6
        elif Version("1.17") <= self <= Version("1.17.1"):
            return 7
        elif Version("1.18") <= self <= Version("1.18.1"):
            return 8
        elif self == Version("1.18"):
            return 9
        elif Version("1.19") <= self <= Version("1.19.3"):
            return 10
        elif self == Version("1.19.4"):
            return 12
        elif Version("1.20") <= self <= Version("1.20.1"):
            return 15
        elif self == Version("1.20.2"):
            return 18
        elif Version("1.20.3") <= self <= Version("1.20.4"):
            return 26

class DataPack:
    def __init__(self, path:str, name:str, version:str):
        name:str = name
        path:str = path
        version:Version = Version(version)

class MCFunction:
    @property
    def callment(self) -> str:
        return "function"

    def __init__(self, root:DataPack, name:str):
        name:str = name
        header:list[str] = []
        main:list[str] = []
        footer:list[str] = []

    def save(self):
        with open("{}\{}.mcfunction".format(self.root.path, self.name), "w") as f:
            header_joined = "\n".join(self.header)
            main_joined = "\n".join(self.main)
            footer_joined = "\n".join(self.footer)
            f.write("\n\n".join([header_joined, main_joined, footer_joined]))



def solve_formula(target:Scoreboard, raw:"list[str|int|Scoreboard]"):
    res:list[str] = []
    for i in range(len(raw)-1):
        if i % 2 == 0:
            if raw[i] == "+":
                res.append(target + raw[i+1])
            elif raw[i] == "-":
                res.append(target - raw[i+1])
            elif raw[i] == "*":
                res.append(target * raw[i+1])
            elif raw[i] == "/":
                res.append(target / raw[i+1])
            elif raw[i] == "%":
                res.append(target % raw[i+1])
    return "\n".join(res)

def is_int(source):
    return type(source) is int or (type(source) is Scoreboard and source.type is int)

def is_bool(source):
    return type(source) is bool or (type(source) is Scoreboard and source.type is bool)

def operate(target:Scoreboard, operation:str, source:Scoreboard):
    return "scoreboard players operation {} {} {} {} {}".format(target.mc_name, bil.namespace, operation, source.mc_name, bil.namespace)