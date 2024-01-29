# https://docs.python.org/3/library/ctypes.html
# https://llvmlite.readthedocs.io/en/latest/user-guide/ir/types.html

from src.compiler.lexer import Lexer
from src.compiler.parser import Parser

from llvmlite.ir import (
    # Bases
    Module,
    Function,
    IRBuilder,
    Constant,
    # Types
    IntType,
    HalfType,
    FloatType,
    DoubleType,
    VoidType,
    ArrayType,
    FunctionType,
)


class Compiler:
    def __init__(self):
        self.types = {
            "bool": IntType(1),
            "double": DoubleType(),
            "int": IntType(32),
            "i8": IntType(8),
            "i16": IntType(16),
            "i32": IntType(32),
            "i64": IntType(64),
            "u8": IntType(8),
            "u16": IntType(16),
            "u32": IntType(32),
            "u64": IntType(64),
            "float": FloatType(),
            "f16": HalfType(),
            "f32": FloatType(),
            "f64": DoubleType(),
            "void": VoidType(),
            # Note i8 in most languages are characters
            "str": ArrayType(IntType(8), 1),
        }

        self.module = Module("main")

        ### Built-ins
        # Print
        _print = Function(
            self.module,
            FunctionType(self.types["int"], [IntType(8).as_pointer()], var_arg=True),
            "printf",
        )

        ### Variables
        self.variables = {"print": (_print, IntType(32))}

        ### Builder
        self.builder = None
        self.i = 0

    @staticmethod
    def isInt():
        ...

    def inc(self):
        self.i += 1
        return 1

    def compile(self, ast):
        for b in ast:
            match b[0]:
                case "FuncCall":
                    self.visitFunccall(b)
                case "If":
                    self.visitIf(b)
                case "VarAssign":
                    self.visitAssign(b)
                case "While":
                    self.visitWhile(b)
                case "Def":
                    self.visitDef(b)
                case "Return":
                    self.visitReturn(b)
                case "Until":
                    self.visitUntil(b)

    def visitDef(self, branch):
        name = branch[1]["name"]
        body = branch[1]["body"]
        params = branch[1]["def_params"]
        params = params if params[0] else []

        # Keep track of the name/type of each parameter
        paramsName = [p["name"] for p in params]
        paramsType = [self.types[p["type"]] for p in params]

        # Functions return type
        returnType = self.types[branch[1]["return"]]

        # Defining a funtions (return type,  parameters)
        fnty = FunctionType(returnType, paramsType)
        fn = Function(self.module, fnty, name=name)

        # Defining function's block
        block = fn.append_basic_block(f"{name}_entry")

        prevBuilder = self.builder
        self.builder = IRBuilder(block)

        # Storing the pointers of each parameter
        paramsPtr = []
        for i, ty in enumerate(paramsType):
            ptr = self.builder.alloca(ty)
            self.builder.store(fn.args[i], ptr)
            paramsPtr.append(ptr)

        prevVars = self.variables.copy()

        for i, x in enumerate(zip(paramsType, paramsName)):
            ty = paramsType[i]
            ptr = paramsPtr[i]

            # Add function's parameter to stored variables
            self.variables[x[1]] = ptr, ty

        # Adding function to variables
        self.variables[name] = fn, returnType

        # Compile the body of the function
        self.compile(body)

        # Removing the function's variables so it cannot be accessed by other functions
        self.variables = prevVars
        self.variables[name] = fn, returnType

        # Done with the function's builder
        # Return to the previous builder
        self.builder = prevBuilder

    def visitIf(self, branch):
        orelse = branch[1]["orelse"]
        body = branch[1]["body"]
        test, _ = self.visitValue(branch[1]["test"])

        # If there is no else block
        if orelse:
            with self.builder.if_else(test) as (true, otherwise):
                with true:
                    self.compile(body)

                with otherwise:
                    self.compile(orelse)
        else:
            with self.builder.if_then(test):
                self.compile(body)

    def visitValue(self, branch):
        category = branch[0]

        match category:
            case "Number":
                val, ty = branch[1]["value"], self.types["int"]
                return Constant(ty, val), ty

            case "Float":
                val, ty = branch[1]["value"], self.types["float"]
                return Constant(ty, val), ty

            case "Name":
                ptr, ty = self.variables[branch[1]["value"]]
                return self.builder.load(ptr), ty

            case "Expression":
                return self.visitExpr(branch)

            case "FuncCall":
                return self.visitFunccall(branch)

            case "String":
                val = branch[1]["value"]
                string, ty = self.str(val)
                return string, ty

    def visitAssign(self, branch):
        name = branch[1]["name"]
        value = branch[1]["value"]

        value, ty = self.visitValue(value)

        if name in self.variables:
            ptr, _ = self.variables[name]
            self.builder.store(value, ptr)
        else:
            ptr = self.builder.alloca(ty)
            self.builder.store(value, ptr)
            self.variables[name] = ptr, ty

    def str(self, s):
        s = s[1:-1]
        s = s.replace("\\n", "\n\0")
        n = len(s) + 1
        buf = bytearray((" " * n).encode("ascii"))
        buf[-1] = 0
        buf[:-1] = s.encode("utf8")
        return Constant(ArrayType(IntType(8), n), buf), ArrayType(IntType(8), n)

    def printf(self, parms, ty):
        fmt = parms[0]
        parms = parms[1:]
        zero = Constant(IntType(32), 0)
        ptr = self.builder.alloca(ty)
        self.builder.store(fmt, ptr)
        grep = self.builder.gep(ptr, [zero, zero])
        bitcast = self.builder.bitcast(grep, IntType(8).as_pointer())
        fn, _ = self.variables["print"]
        return self.builder.call(fn, [bitcast, *parms])

    def visitFunccall(self, branch):
        name = branch[1]["name"]
        parms = branch[1]["params"]

        args = []
        types = []

        if parms[0]:
            for p in parms:
                val, ty = self.visitValue(p)
                args.append(val)
                types.append(ty)

        if name == "print":
            ret = self.printf(args, types[0])
            retType = self.types["i32"]
        else:
            fn, retType = self.variables[name]
            ret = self.builder.call(fn, args)

        return ret, retType

    def visitWhile(self, branch):
        _test = branch[1]["test"]
        body = branch[1]["body"]
        test, _ = self.visitValue(_test)

        entry = self.builder.append_basic_block(f"while_loop_entry{self.inc()}")
        otherwise = self.builder.append_basic_block(f"while_loop_otherwise{self.i}")

        self.builder.cbranch(test, entry, otherwise)

        # Setting the builder position-at-start
        self.builder.position_at_start(entry)
        self.compile(body)
        test, _ = self.visitValue(_test)
        self.builder.cbranch(test, entry, otherwise)
        self.builder.position_at_start(otherwise)

    def visitUntil(self, branch):
        _test = branch[1]["test"]
        body = branch[1]["body"]
        test, _ = self.visitValue(_test)
        test = self.builder.not_(test)

        entry = self.builder.append_basic_block(f"until_loop_entry{self.inc()}")
        otherwise = self.builder.append_basic_block(f"until_loop_otherwise{self.i}")

        self.builder.cbranch(test, entry, otherwise)

        self.builder.position_at_start(entry)
        self.compile(body)
        test, _ = self.visitValue(_test)
        test = self.builder.not_(test)
        self.builder.cbranch(test, entry, otherwise)
        self.builder.position_at_start(otherwise)

    def visitReturn(self, branch):
        val, _ = self.visitValue(branch[1]["value"])
        self.builder.ret(val)

    def visitExpr(self, branch):
        op = branch[1]["op"]
        lhs, lhsty = self.visitValue(branch[1]["lhs"])
        rhs, rhsty = self.visitValue(branch[1]["rhs"])

        assert lhsty == rhsty

        if lhsty == self.types["float"]:
            ty = self.types["float"]

            match op:
                case "+":
                    val = self.builder.fadd(lhs, rhs)
                case "*":
                    val = self.builder.fmul(lhs, rhs)
                case "/":
                    val = self.builder.fdiv(lhs, rhs)
                case "%":
                    val = self.builder.frem(lhs, rhs)
                case "-":
                    val = self.builder.fsub(lhs, rhs)
                case "<":
                    val = self.builder.fcmp_ordered("<", lhs, rhs)
                    ty = IntType(1)
                case "<=":
                    val = self.builder.fcmp_ordered("<=", lhs, rhs)
                    ty = IntType(1)
                case ">":
                    val = self.builder.fcmp_ordered(">", lhs, rhs)
                    ty = IntType(1)
                case ">=":
                    val = self.builder.fcmp_ordered(">=", lhs, rhs)
                    ty = IntType(1)
                case "!=":
                    val = self.builder.fcmp_ordered("!=", lhs, rhs)
                    ty = IntType(1)
                case "==":
                    val = self.builder.fcmp_ordered("==", lhs, rhs)
                    ty = IntType(1)

        elif lhsty == self.types["int"]:
            ty = self.types["int"]

            match op:
                case "+":
                    val = self.builder.add(lhs, rhs)
                case "*":
                    val = self.builder.mul(lhs, rhs)
                case "/":
                    val = self.builder.sdiv(lhs, rhs)
                case "%":
                    val = self.builder.srem(lhs, rhs)
                case "-":
                    val = self.builder.sub(lhs, rhs)
                case "<":
                    val = self.builder.icmp_signed("<", lhs, rhs)
                    ty = IntType(1)
                case "<=":
                    val = self.builder.icmp_signed("<=", lhs, rhs)
                    ty = IntType(1)
                case ">":
                    val = self.builder.icmp_signed(">", lhs, rhs)
                    ty = IntType(1)
                case ">=":
                    val = self.builder.icmp_signed(">=", lhs, rhs)
                    ty = IntType(1)
                case "!=":
                    val = self.builder.icmp_signed("!=", lhs, rhs)
                    ty = IntType(1)
                case "==":
                    val = self.builder.icmp_signed("==", lhs, rhs)
                    ty = IntType(1)
                case "&":
                    val = self.builder.and_(lhs, rhs)
                    ty = IntType(1)
                case "|":
                    val = self.builder.or_(lhs, rhs)
                    ty = IntType(1)
                case "^":
                    val = self.builder.xor(lhs, rhs)
                    ty = IntType(1)
                case ">>":
                    val = self.builder.ashr(lhs, rhs)
                    ty = IntType(1)
                case "<<":
                    val = self.builder.shl(lhs, rhs)
                    ty = IntType(1)

        return val, ty
