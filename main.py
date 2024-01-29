# pip install sly

import os
import subprocess
from time import perf_counter
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int

from src.compiler.lexer import Lexer
from src.compiler.parser import Parser
from src.compiler.compiler import Compiler


def c():
    # llc -filetype=obj main.ll -o main.o
    # clang main.o -o main
    
    with open("main.💐", "r") as f:
        code = f.read()
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    # lexer.pprint(tokens)

    parser = Parser()
    parser.parse(tokens)
    ast = parser.ast[1]["body"]
    # parser.pprint(ast)

    compiler = Compiler()
    compiler.compile(ast)
    module = compiler.module
    module.triple = llvm.get_default_triple()

    with open("main.ll", "w") as f:
        f.write(str(module))
        
    subprocess.run(["llc", "-filetype=obj", "main.ll", "-o", "main.o"])
    
    start = perf_counter()
    subprocess.run(["clang", "main.o", "-o", "main"])
    print(perf_counter() - start)

    start = perf_counter()
    subprocess.run(["gcc", "main.o", "-o", "main"], check=True)
    print(perf_counter() - start)

def run():
    if not os.path.exists("main"):
        c()
    
    start = perf_counter()
    subprocess.run(["./main"])
    elapsed = round(perf_counter() - start, 5)

    print(f"\033[0;90mExecuted in \033[0;37m{elapsed}s")

def llvm_run():
    with open("main.ll", "r") as f:
        module = f.read()

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    llvm_ir_parsed = llvm.parse_assembly(module)
    llvm_ir_parsed.verify()

    # Generate assembly code
    target_machine = llvm.Target.from_default_triple().create_target_machine()
    # engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
    # engine.finalize_object()

    with llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine) as engine:
        engine.finalize_object()

        with open("main.o", "wb") as output:
            output.write(engine.get_object_file().get_binary())

    return
    # Run the function with name func_name. This is why it makes sense to have a 'main' function that calls other functions.
    entry = engine.get_function_address('main')
    cfunc = CFUNCTYPE(c_int)(entry)

    start = perf_counter()
    result = cfunc()
    elapsed = round((perf_counter() - start) * 1000.0, 5)

    print(f"\033[0;90mOutput : \033[0;37m{result}")
    print(f"\033[0;90mExecuted in \033[0;37m{elapsed}ms")

c()
run()
# llvm_run()
