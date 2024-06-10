# pip install sly

import os
import subprocess
from time import perf_counter
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int

from src.compiler import Lexer, Parser, Compiler


target = "target/"
project = "main"
output = target + project


def c():
    with open("main.💐", "r") as f:
        code = f.read()

    lexer = Lexer()
    tokens = lexer.tokenize(code)
    # lexer.pprint(lexer.tokenize(code))

    parser = Parser()
    parser.parse(tokens)
    ast = parser.ast[1]["body"]
    # parser.pprint(ast)

    compiler = Compiler()
    compiler.compile(ast)
    module = compiler.module
    module.triple = "x86_64-pc-linux-gnu"  # llvm.get_default_triple()

    with open(f"{output}.ll", "w") as f:
        f.write(str(module))

    # Optimize
    subprocess.run(
        ["clang", "-O3", "-S", "-emit-llvm", f"{output}.ll", "-o", f"{output}.ll"]
    )

    # To output
    subprocess.run(["llc", "-filetype=obj", f"{output}.ll", "-o", f"{output}.o"])

    # Compile with gcc
    start = perf_counter()
    subprocess.run(["gcc", f"{output}.o", "-o", output])
    elapsed = perf_counter() - start
    print(f"\033[0;90mCompiled in \033[0;37m{elapsed:.9f}s (gcc)")


def run(path):
    start = perf_counter()
    subprocess.run([path])
    elapsed = perf_counter() - start

    print(f"\033[0;90mExecuted {path} in \033[0;37m{elapsed:.9f}s (bin)")


def llvm_run():
    with open(f"{output}.ll", "r") as f:
        module = f.read()

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    llvm_ir_parsed = llvm.parse_assembly(module)
    llvm_ir_parsed.verify()

    # Generate assembly code
    target_machine = llvm.Target.from_default_triple().create_target_machine()
    engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
    engine.finalize_object()

    # Run the function with name func_name. This is why it makes sense to have a 'main' function that calls other functions.
    entry = engine.get_function_address("main")
    cfunc = CFUNCTYPE(c_int)(entry)

    start = perf_counter()
    result = cfunc()
    elapsed = perf_counter() - start

    # print(f"\033[0;90mOutput : \033[0;37m{result}")
    print(f"\033[0;90mExecuted in \033[0;37m{elapsed:.9f}s (llvm)")


c()
run(target + "main")
# llvm_run()
