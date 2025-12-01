#!/usr/bin/env python3

import sys
import os
import random
import string
import traceback
from io import StringIO
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'FAME-ML'))

try:
    import lint_engine
    import py_parser
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def generate_random_string(min_length=1, max_length=1000):
    length = random.randint(min_length, max_length)
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation + ' \n\t') for _ in range(length))


def generate_random_filename():
    extensions = ['.py', '.txt', '.csv', '.json', '.xml', '']
    name = generate_random_string(1, 50)
    ext = random.choice(extensions)
    return name + ext


def fuzz_getPythonParseObject():
    print("Fuzzing py_parser.getPythonParseObject...")
    
    test_cases = [
        "print('hello world')",
        "x = 1 + 2",
        "import os\nprint(os.getcwd())",
        "# This is a comment\nx = 42",
        "def func(): pass",
        "print('unclosed string",
        "x = ) invalid syntax (",
        "if True print 'missing colon'",
        "",  
        "\n" * 1000,  
        "x = " + "a" * 10000,  
    ]
    
    extreme_cases = [
        "x = " + "a" * 100000, 
        "\n" * 100000,  
        "# " * 100000, 
        "x = " + "(" * 5000 + ")" * 5000, 
        "x = " + "['item']" * 10000,
        "def x():\n  " + "pass\n  " * 10000, 
        "a" * 50000 + " = 1",  
        "x = '''" + "multi\nline\nstring\n" * 10000 + "'''",  
        "for i in range(100000):\n  pass",  
        "\xff" * 1000,  
        "x = 'valid' # " + "comment" * 10000,  
        "x = 1\n" * 50000,  
        "import sys\n" * 10000,  
        "class X:\n    " + "def m(self): pass\n    " * 10000,  
        "try:\n    pass\n" * 10000 + "except:\n    pass",  
    ]
    
    test_cases.extend(extreme_cases)
    
    for _ in range(10):
        test_cases.append(generate_random_string(1, 10000))
    
    bugs_found = 0
    for i, test_input in enumerate(test_cases):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_input)
                temp_file = f.name
            
            result = py_parser.getPythonParseObject(temp_file)
            
            os.unlink(temp_file)
            
            if hasattr(result, 'body'):
                print(f"  Test {i+1}: OK - Parsed successfully")
            else:
                print(f"  Test {i+1}: WARNING - Unexpected result type: {type(result)}")
                
        except Exception as e:
            print(f"  Test {i+1}: EXCEPTION - {type(e).__name__}: {e}")
            bugs_found += 1
    
    print(f"  getPythonParseObject fuzzing completed. Bugs found: {bugs_found}")
    return bugs_found


def fuzz_getPythonAtrributeFuncs():
    print("Fuzzing py_parser.getPythonAtrributeFuncs...")
    
    test_cases = [
        "import os\nos.path.join('a', 'b')",
        "x = list()\nx.append(1)",
        "str.upper('hello')",
        "",  
        "# just a comment",
        "x = 5",  
        "print('hello')",  
    ]
    
    # Add more extreme test cases
    extreme_cases = [
        "x = " + "a" * 50000,  
        "obj." + "method()" * 10000,  
        "a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z()" * 1000,  
        "getattr(obj, 'method')()" * 10000,  
        "import sys\n" * 10000,  
        "obj.method().method().method()" * 10000,  
        "for x in range(10000):\n    obj.method()",
        "obj[" + "'key']" * 10000 + ".method()",
        "obj.attr.attr.attr.attr" * 10000,  
        "\xff" * 1000,
    ]
    
    test_cases.extend(extreme_cases)
    
    bugs_found = 0
    for i, test_input in enumerate(test_cases):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_input)
                temp_file = f.name
            
            tree = py_parser.getPythonParseObject(temp_file)
            
            result = py_parser.getPythonAtrributeFuncs(tree)
            
            os.unlink(temp_file)
            
            print(f"  Test {i+1}: OK - Found {len(result)} attribute functions")
                
        except Exception as e:
            print(f"  Test {i+1}: EXCEPTION - {type(e).__name__}: {e}")
            print(f"    Input: {repr(test_input[:50])}")
            traceback.print_exc()
            bugs_found += 1
    
    print(f"  getPythonAtrributeFuncs fuzzing completed. Bugs found: {bugs_found}")
    return bugs_found


def fuzz_getDataLoadCount():
    print("Fuzzing lint_engine.getDataLoadCount...")
    
    test_cases = [
        "import pandas as pd\ndf = pd.read_csv('file.csv')",
        "import pickle\ndata = pickle.load(open('file.pkl', 'rb'))",
        "import json\ndata = json.load(open('file.json'))",
        "",
        "# comment only",
        "x = 1",  
    ]
    
    extreme_cases = [
        "import pandas as pd\n" * 10000 + "df = pd.read_csv('test.csv')",
        "import pickle\nimport json\nimport numpy as np\n" * 5000,
        "df = pd.read_csv('a.csv')\n" * 10000,  
        "import h5py\nimport tensorflow as tf\nimport torch\n" * 5000,  
        "for i in range(10000):\n    df = pd.read_csv(f'file{i}.csv')", 
        "import very_long_module_name_" * 10000 + "\ndata = very_long_module_name.read_csv('f.csv')",
        "x = " + "pd.read_csv('f.csv')" * 10000,  
        "import json\njson.loads(" + "'data'" * 10000 + ")",  
        "df = pd.read_csv('file.csv')\n" * 50000,  
        "\xff" * 1000,  # Invalid bytes
    ]
    
    test_cases.extend(extreme_cases)
    
    bugs_found = 0
    for i, test_input in enumerate(test_cases):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_input)
                temp_file = f.name
            
            result = lint_engine.getDataLoadCount(temp_file)
            
            os.unlink(temp_file)
            
            print(f"  Test {i+1}: OK - Count: {result}")
                
        except Exception as e:
            print(f"  Test {i+1}: EXCEPTION - {type(e).__name__}: {e}")
            print(f"    Input: {repr(test_input[:50])}")
            traceback.print_exc()
            bugs_found += 1
    
    print(f"  getDataLoadCount fuzzing completed. Bugs found: {bugs_found}")
    return bugs_found


def fuzz_getFunctionAssignments():
    print("Fuzzing py_parser.getFunctionAssignments...")
    
    test_cases = [
        "x = len([1, 2, 3])",
        "result = some_func(arg1, arg2)",
        "a, b = func(), func2()",
        "",
        "# comment",
        "x = 5",  
    ]
    
    extreme_cases = [
        "x = func()" * 10000,  
        "a, b, c, d, e, f, g, h, i, j = " + "func()," * 10,  
        "x = func(arg1, arg2, arg3)" * 10000,  
        "result = func() + func() + func()" * 5000,  
        "for i in range(10000):\n    x = func()",  
        "x = " + "func() + " * 10000 + "0", 
        "[x for x in range(10000) if func()]", 
        "x = func(arg1=1, arg2=2, arg3=3)" * 10000, 
        "x = func(*args, **kwargs)" * 10000, 
        "\xff" * 1000, 
    ]
    
    test_cases.extend(extreme_cases)
    
    bugs_found = 0
    for i, test_input in enumerate(test_cases):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_input)
                temp_file = f.name
            
            tree = py_parser.getPythonParseObject(temp_file)
            
            result = py_parser.getFunctionAssignments(tree)
            
            os.unlink(temp_file)
            
            print(f"  Test {i+1}: OK - Found {len(result)} function assignments")
                
        except Exception as e:
            print(f"  Test {i+1}: EXCEPTION - {type(e).__name__}: {e}")
            print(f"    Input: {repr(test_input[:50])}")
            traceback.print_exc()
            bugs_found += 1
    
    print(f"  getFunctionAssignments fuzzing completed. Bugs found: {bugs_found}")
    return bugs_found


def fuzz_checkIfParsablePython():
    print("Fuzzing py_parser.checkIfParsablePython...")
    
    test_cases = [
        "print('hello')",
        "x = 1",
        "def func(): pass",
        "print('unclosed",
        "x = ) invalid (",
        "",  
        generate_random_string(),
        generate_random_string(),
        generate_random_string(),
    ]
    
    extreme_cases = [
        "x = " + "a" * 100000,  
        "\n" * 100000, 
        "x = " + "(" * 50000 + ")" * 50000, 
        "def x():\n  " + "pass\n  " * 50000, 
        "class X:\n    " + "def m(self): pass\n    " * 50000,  
        "try:\n    pass\n" * 50000 + "except:\n    pass",  
        "x = '''" + "multi\nline\nstring\n" * 50000 + "'''", 
        "for i in range(100000):\n  pass\n" * 10,  
        "if True:\n  " + "x = 1\n  " * 10000,  
        "\xff" * 10000,  
        "x = 'valid'\n" + "# comment\n" * 100000,  
        "import sys\n" * 100000,  
        "x = " + "[i for i in range(100)]" * 10000,  
        "x = " + "1 + " * 50000 + "1",  
        "def f():\n  " + "if True: return\n  " * 50000,
    ]
    
    test_cases.extend(extreme_cases)
    
    for _ in range(10):
        test_cases.append(generate_random_string(1, 10000))
    
    bugs_found = 0
    for i, test_input in enumerate(test_cases):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_input)
                temp_file = f.name
            
            result = py_parser.checkIfParsablePython(temp_file)
            
            os.unlink(temp_file)
            
            print(f"  Test {i+1}: OK - Result: {result}")
                
        except Exception as e:
            print(f"  Test {i+1}: EXCEPTION - {type(e).__name__}: {e}")
            print(f"    Input: {repr(test_input[:50])}")
            traceback.print_exc()
            bugs_found += 1
    
    print(f"  checkIfParsablePython fuzzing completed. Bugs found: {bugs_found}")
    return bugs_found


def main():
    print("=" * 60)
    print("Fuzzing Python Methods for SQA Project")
    print("=" * 60)
    
    total_bugs = 0
    
    total_bugs += fuzz_getPythonParseObject()
    print()
    total_bugs += fuzz_getPythonAtrributeFuncs()
    print()
    total_bugs += fuzz_getDataLoadCount()
    print()
    total_bugs += fuzz_getFunctionAssignments()
    print()
    total_bugs += fuzz_checkIfParsablePython()
    print()
    
    print("=" * 60)
    print(f"Total bugs found during fuzzing: {total_bugs}")
    print("=" * 60)
    
    if total_bugs > 0:
        print("Bugs discovered! Check the output above for details.")
        return 1
    else:
        print("No bugs discovered during fuzzing.")
        return 0


if __name__ == "__main__":
    sys.exit(main())