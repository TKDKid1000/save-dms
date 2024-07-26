import sys


if not sys.argv[1]:
    print("error: no summary supplied.")
    sys.exit(1)

with open(sys.argv[1], encoding="utf8") as f:
    summary = f.read()

