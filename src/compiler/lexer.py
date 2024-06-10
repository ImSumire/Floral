import re
import sly


# Useful tools :
# - https://regex-generator.olafneumann.org/
# - https://regexr.com/

# Int
rBin = r"0[bB](?:_*?[01])+"
rOct = r"0[oO](?:_*?[0-7])+"
rDec = r"\d(?:_*?\d)*"
rHex = r"0[xX](?:_*?[0-9a-fA-F])+"
intSuffix = r"(?:([ui]\d{1,2})*)"

rInt = f"({rBin}|{rOct}|{rDec}|{rHex}){intSuffix}"

# Float
floatSuffix = r"(?:(f\d{1,2})*)"
rFlt = r"\d(?:_*?\d)*\.\d(?:_*?\d)*" + floatSuffix


class Lexer(sly.Lexer):
    # fmt: off
    tokens = {
        NAME,

        # Types
        FLOAT,
        INT,
        STR,

        # Operators
        EQ,
        DIV, MINUS, MOD, MULT, PLUS, LSHIFT, RSHIFT,
        AND, EQEQ, GE, GT, LE, LT, NE, OR, XOR,

        # Brackets
        LPAR, RPAR, LBRA, RBRA,

        # Statements
        BREAK, CONTINUE, ELSE, FN, IF, RETURN, UNTIL, WHILE, 

        # Separators
        COLON, COMMA
    }
    # fmt: on

    ignore = " \t\r"

    # literals = {",", ";"}

    @_(r"\n")
    def newline(self, t):
        self.lineno += 1

    NAME = r"[a-zA-Z_][a-zA-Z0-9_]*"
    NAME["if"] = IF
    NAME["fn"] = FN
    NAME["else"] = ELSE
    NAME["while"] = WHILE
    NAME["until"] = UNTIL
    NAME["break"] = BREAK
    NAME["return"] = RETURN
    NAME["continue"] = CONTINUE

    FLOAT = rFlt
    INT = rInt
    STR = r"(\".*?\")|(\'.*?\')"

    DIV = r"(?<!\/)\/(?!\/)"
    MINUS = r"-"
    MOD = r"%"
    MULT = r"\*"
    PLUS = r"\+"

    AND = r"\&"
    EQEQ = r"=="
    GE = r">="
    GT = r">"
    LE = r"<="
    LT = r"<"
    NE = r"!="
    OR = r"\|"
    XOR = r"\^"

    EQ = r"="

    LPAR = r"\("
    RPAR = r"\)"
    LBRA = r"\{"
    RBRA = r"\}"

    COLON = r":"
    COMMA = r","

    @_(r"\/\/.*")
    def COMMENT(self, t):
        ...
    
    def error(self, t):
        print(
            f"Illegal character {t.value[0]}, in line {self.lineno}, index {self.index}"
        )
        exit()
    
    def tokenize(self, code):
        # Removing multi-line comments
        return super().tokenize(re.sub(r"\/\*[\s\S]*?\*\/", "", code))

    @staticmethod
    def pprint(tokens):
        result = ""
        lineno = 0
        index = -2

        for tok in tokens:
            line = tok.lineno
            if line > lineno:
                # Blank lines
                while not(line == lineno + 1):
                    result += "\n" + f"\033[30m{lineno} |".rjust(12)
                    index += 1
                    lineno += 1

                indent = " " * (tok.index - index)
                result += "\n" + f"\033[30m{line} |".rjust(12) + indent
                lineno = line

            index = tok.index
            result += f"\033[34m{tok.type}\033[30m:\033[33m{tok.value} "
        
        print(result + "\n\033[37m")
