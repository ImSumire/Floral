import re
import sly

from src.compiler.lexer import Lexer


class Parser(sly.Parser):
    tokens = Lexer.tokens

    precedence = (
        ("nonassoc", AND, EQEQ, GE, GT, LE, LT, NE, OR, XOR),
        ("left", PLUS, MINUS),
        ("left", MULT, DIV),
        ("left", LSHIFT, RSHIFT),
    )

    def __init__(self):
        self.ast = ("Module", {"body": []})

    ### Base

    @_("statements")
    def body(self, p):
        self.ast[1]["body"] = p.statements

    @_("statement")
    def statements(self, p):
        return [p.statement]

    @_("statements statement")
    def statements(self, p):
        p.statements.append(p.statement)
        return p.statements

    @_("")
    def def_param(self, p):
        return

    ### Variable

    @_("NAME COLON NAME EQ expr")
    def statement(self, p):
        ty = p.NAME1
        return "VarAssign", {"name": p.NAME0, "value": p.expr}

    @_("NAME EQ expr")
    def statement(self, p):
        return "VarAssign", {"name": p.NAME, "value": p.expr}

    @_("NAME COLON NAME")
    def def_param(self, p):
        return {"name": p.NAME0, "type": p.NAME1}

    ### Function

    @_("FN NAME LPAR def_params RPAR COLON NAME LBRA statements RBRA")
    def statement(self, p):
        return "Def", {
            "name": p.NAME0,
            "def_params": p.def_params,
            "return": p.NAME1,
            "body": p.statements,
        }

    @_("def_params COMMA def_param")
    def def_params(self, p):
        p.def_params.append(p.def_param)
        return p.def_params

    @_("def_param")
    def def_params(self, p):
        return [p.def_param]

    @_("RETURN expr")
    def statement(self, p):
        return "Return", {"value": p.expr}

    @_("NAME LPAR params RPAR")
    def statement(self, p):
        return "FuncCall", {"name": p.NAME, "params": p.params}

    @_("NAME LPAR params RPAR")
    def expr(self, p):
        return "FuncCall", {"name": p.NAME, "params": p.params}

    @_("params COMMA param")
    def params(self, p):
        p.params.append(p.param)
        return p.params

    @_("param")
    def params(self, p):
        return [p.param]

    @_("expr")
    def param(self, p):
        return p.expr

    ### Conditional

    @_("IF expr LBRA statements RBRA")
    def statement(self, p):
        return "If", {"test": p.expr, "body": p.statements, "orelse": []}

    @_("IF expr LBRA statements RBRA ELSE LBRA statements RBRA")
    def statement(self, p):
        return "If", {"test": p.statements1, "body": p.statements0, "orelse": p.expr}

    ### Loop

    @_("WHILE expr LBRA statements RBRA")
    def statement(self, p):
        return "While", {"test": p.expr, "body": p.statements}

    @_("UNTIL expr LBRA statements RBRA")
    def statement(self, p):
        return "Until", {"test": p.expr, "body": p.statements}

    ### Operator

    @_(
        "expr PLUS expr",
        "expr MINUS expr",
        "expr MULT expr",
        "expr DIV expr",
        "expr MOD expr",
        "expr LSHIFT expr",
        "expr RSHIFT expr",
        "expr GT expr",
        "expr GE expr",
        "expr LT expr",
        "expr LE expr",
        "expr NE expr",
        "expr EQEQ expr",
        "expr AND expr",
        "expr OR expr",
        "expr XOR expr",
    )
    def expr(self, p):
        return "Expression", {"op": p[1], "lhs": p.expr0, "rhs": p.expr1}

    @_("LPAR expr RPAR")
    def expr(self, p):
        return p.expr

    ### Value

    @_("NAME")
    def expr(self, p):
        return "Name", {"value": p.NAME}

    @_("INT")
    def expr(self, p):
        return "Number", {"value": int(p.INT)}

    @_("MINUS INT")
    def expr(self, p):
        return "Number", {"value": -int(p.INT)}

    @_("FLOAT")
    def expr(self, p):
        return "Float", {"value": float(p.FLOAT)}

    @_("MINUS FLOAT")
    def expr(self, p):
        return "Float", {"value": -float(p.FLOAT)}

    @_("STR")
    def expr(self, p):
        return "String", {"value": p.STR}

    @staticmethod
    def pprint(ast):
        kwd = "If", "Def", "Else", "While", "Until", "Break", "Return", "Continue"
        ope = "=", "/", "-", "%", "*", "+", "&", "==", ">=", "<=", ">", "<", "!=", "|", "^"
        typ = "i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64", "f16", "f32", "f64", "str", "Number", "Float", "String"
        oth = "Expression", "FuncCall", "VarAssign"

        def aux(obj, ind=0, tab="  "):
            ty = type(obj)

            if ty == tuple or ty == list:
                for e in obj:
                    aux(e, ind=ind + 1)

            elif ty == dict:
                for k in obj:
                    # res += tab * ind + f"\033[91m• {k}\033[30m:\033[0m "
                    print(tab * ind + f"\033[91m• {k}\033[30m:\033[0m ", end="")

                    if type(obj[k]) in (dict, tuple, list):
                        # res += "\n"
                        print()
                    aux(obj[k], ind=ind + 1, tab="")

            elif ty == str:
                if obj in kwd:
                    fmted = "\033[96m" + obj
                elif obj in ope:
                    fmted = "\033[1;35m" + obj
                elif obj in typ:
                    fmted = "\033[93m" + obj
                elif obj in oth:
                    fmted = "\033[94m" + obj
                elif re.match(r"(\".*?\")|(\'.*?\')", obj):
                    fmted = f"\033[92m{obj}"
                else:
                    fmted = f"\033[35m{obj}"
                
                # res += tab * ind + f"{fmted}\033[0m\n"
                print(tab * ind + f"{fmted}\033[0m")

            else:
                # res += tab * ind + repr(obj) + "\n"
                print(tab * ind + repr(obj))

            # return res

        aux(ast)
        # print(aux(ast))
