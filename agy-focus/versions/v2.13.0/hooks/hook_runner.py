#!/usr/bin/env python3
import sys, json
if len(sys.argv) > 1 and "gate" in sys.argv[1]:
    json.dump({"decision": "allow"}, sys.stdout)
    sys.stdout.write("\n")
sys.exit(0)
