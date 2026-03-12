"""Fix syntax errors in two modules."""
# Fix 1: internet_job_scraper.py - ] instead of } at line 50
with open('modules/internet_job_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The dict literal for _COMPANY_STACK ends with ] instead of }
# Find the last entry and fix closing
old = '    "stripe":     ["python", "ruby", "java", "postgresql", "kafka", "aws"],\n]\n'
new = '    "stripe":     ["python", "ruby", "java", "postgresql", "kafka", "aws"],\n}\n'
if old in content:
    content = content.replace(old, new)
    print("Fixed internet_job_scraper.py: ] -> }")
else:
    print("Pattern not found - showing lines 47-53:")
    for i, l in enumerate(content.split('\n')[46:54], 47):
        print(f"  {i}: {repr(l)}")

with open('modules/internet_job_scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix 2: skill_extractor.py - invalid escape \. in raw string label
with open('modules/skill_extractor.py', 'r', encoding='utf-8') as f:
    ec = f.read()

# Fix the .NET pattern - the canonical string "\\.net" is invalid, should be ".net"
# Line 36: (re.compile(r'\.NET\b', re.IGNORECASE),"\.net"),
old2 = r'    (re.compile(r\'\.NET\b\', re.IGNORECASE),"\.net"),' + '\n'
new2 = r'    (re.compile(r\'[.]NET\b\', re.IGNORECASE),".net"),' + '\n'
if old2 in ec:
    ec = ec.replace(old2, new2)
    print("Fixed skill_extractor.py: escape sequence")
else:
    # Try alternate form
    print("Trying alternate fix for skill_extractor.py escape...")
    # Just rewrite the ORIGINAL_TEXT_PATTERNS section
    import re
    ec2 = re.sub(
        r"\(re\.compile\(r'\\\.NET\\b', re\.IGNORECASE\),\"\\\.net\"\)",
        '(re.compile(r\'[.]NET\\\\b\', re.IGNORECASE),".net")',
        ec
    )
    if ec2 != ec:
        ec = ec2
        print("Fixed with regex replacement")
    else:
        print("Could not fix automatically, showing line 34-38:")
        for i, l in enumerate(ec.split('\n')[33:38], 34):
            print(f"  {i}: {repr(l)}")

with open('modules/skill_extractor.py', 'w', encoding='utf-8') as f:
    f.write(ec)

print("\nDone. Checking syntax...")
import subprocess
r1 = subprocess.run(['python', '-m', 'py_compile', 'modules/internet_job_scraper.py'], capture_output=True, text=True)
r2 = subprocess.run(['python', '-m', 'py_compile', 'modules/skill_extractor.py'], capture_output=True, text=True)
print("internet_job_scraper:", "OK" if r1.returncode == 0 else r1.stderr)
print("skill_extractor:", "OK" if r2.returncode == 0 else r2.stderr)
