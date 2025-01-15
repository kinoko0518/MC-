import mcpt
import mcpp_parser

def title(input:str, longness:int = 55):
    hyphen = int((longness - len(input)) / 2)
    print("\n" + "-"*hyphen+input+"-"*hyphen)

def valid_check():
    task = mcpp_parser.ParseTaskInfo()
    title("Preparser Validness Checkment")
    print(task.formula_to_tokens("a + 12/2"), end="\n"*2)

    title("Assignment Validness Checking")
    print(task.parse_assignment("b = 6"))
    print(task.parse_assignment("a = 1 + 1 + 1"))
    print(task.parse_assignment("a += b"))
    print(task.parse_assignment("a -= 1"))
    print(task.parse_assignment("a *= 1"))
    print(task.parse_assignment("a /= 1 + 1"))

    title("Logical Formula Validness Checking")
    print(task.parse_logical_formula("a | b & ! c"))

    title("Parser Validness Checking")
    print(mcpp_parser.parser("a = 1 + 1 + 1"))

valid_check()