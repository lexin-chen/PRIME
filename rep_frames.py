import argparse
import modules as mod

"""Call the `gen_method_max` with the parsed trim and index argument
Example usage:
----------------
No trim, RR index
>>> python scripts/rep_frames.py
10% trim, RR index
>>> python scripts/rep_frames.py -t 0.1
20% trim, SM index
>>> python scripts/rep_frames.py -t 0.2 -i SM
"""
parser = argparse.ArgumentParser(description='Generate method max with optional trim and n_ary')
parser.add_argument('-t', '--trim_frac', type=float, default=None,
                    help='Trim parameter for gen_method_max method')
parser.add_argument('-i', '--index', type=str, default='RR',
                    help='n_ary parameter for gen_method_max method')
args = parser.parse_args()

mod.gen_method_max(trim_frac=args.trim_frac, n_ary=args.index)