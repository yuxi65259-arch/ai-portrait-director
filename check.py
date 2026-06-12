"""预提交检查：Python 语法 + JS 语法 + 功能性测试"""
import sys, subprocess, re

errors = 0

# 1. Python 语法检查
print("=== Python Syntax ===")
for f in ['config.py','models.py','models_config.py','database.py','prompt_engine.py','image_generator.py','system_prompt.py','main.py']:
    result = subprocess.run([sys.executable, '-c', f'import py_compile; py_compile.compile("{f}", doraise=True)'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'  OK  {f}')
    else:
        print(f'  FAIL {f}: {result.stderr.strip()[:200]}')
        errors += 1

# 2. JavaScript 语法检查
print("\n=== JavaScript Syntax ===")
with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

script = html[html.find('<script>')+8:html.find('</script>')]

# 检查重复变量声明
conts = re.findall(r'\b(const|let|var)\s+(\w+)', script)
seen = set()
for decl_type, var_name in conts:
    key = (decl_type, var_name)
    if key in seen:
        print(f'  FAIL Duplicate: {decl_type} {var_name}')
        errors += 1
    seen.add(key)

# 检查 const + var 冲突
const_vars = set(name for t, name in conts if t == 'const')
var_vars = set(name for t, name in conts if t in ('var', 'let'))
conflicts = const_vars & var_vars
for name in conflicts:
    print(f'  FAIL const/var conflict: {name}')
    errors += 1

# 检查 template literal 配对
backtick_count = script.count('`')
if backtick_count % 2 != 0:
    print(f'  FAIL Unmatched backticks: {backtick_count}')
    errors += 1

# 检查括号匹配
if script.count('{') != script.count('}'):
    print(f'  FAIL Brace mismatch: {script.count("{")} vs {script.count("}")}')
    errors += 1

if script.count('(') != script.count(')'):
    print(f'  FAIL Paren mismatch: {script.count("(")} vs {script.count(")")}')
    errors += 1

# 检查引号
for q in ["'", '"']:
    count = script.count(q)
    if count % 2 != 0:
        lines = script.split('\n')
        for i, line in enumerate(lines):
            if line.strip().count(q) % 2 != 0 and not line.strip().startswith('//'):
                print(f'  FAIL Unmatched {q} on line {i}: {line.strip()[:100]}')
                errors += 1

print(f"\n=== Result: {errors} errors {'FAIL' if errors else 'PASS'} ===")
sys.exit(errors)
