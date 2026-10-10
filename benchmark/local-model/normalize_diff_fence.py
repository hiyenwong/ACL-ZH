#!/usr/bin/env python3
import argparse
from pathlib import Path

def strip_outer_diff_fence(text):
    s=text.strip()
    if s.startswith('```diff') and s.endswith('```'):
        s=s[len('```diff'):].lstrip('\r\n')
        s=s[:-3].rstrip()
        return s+'\n'
    return text

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    src=Path(args.input).read_text(encoding='utf-8')
    out=strip_outer_diff_fence(src)
    Path(args.output).write_text(out,encoding='utf-8')

if __name__=='__main__':
    main()
