#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('--base',required=True); p.add_argument('--head','default','HEAD'); p.add_argument('--allow',action='append',default=[]); args=p.parse_args()
    cp=subprocess.run(['git','diff','--name-only',f'{args.base}...{args.head}'],text=True,capture_output=True)
    if cp.returncode: print(cp.stderr,file=sys.stderr); return cp.returncode
    paths=[x for x in cp.stdout.splitlines() if x.strip()]
    bad=[x for x in paths if not any(x==a.rstrip('/') or x.startswith(a.rstrip('/')+'/') for a in args.allow)]
    print(json.dumps({'changed':paths,'violations':bad,'ok':not bad},indent=2)); return 0 if not bad else 8
if __name__=='__main__': raise SystemExit(main())
