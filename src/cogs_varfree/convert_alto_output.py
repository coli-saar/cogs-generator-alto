# coding=utf-8
"""Convert the alto output to original cogs format"""


import varfreeLF_converter
import pandas as pd
import sys

varfree_lf_file = sys.argv[1]
out_file = sys.argv[2]

def main():
    df_varfree = pd.read_csv(varfree_lf_file, sep="\t", names=["sent", "varfree_lf", "types"])
    df_varfree["cogs_lf"] = df_varfree.apply(lambda x: varfreeLF_converter.varfree_lf_to_cogs(x.sent, x.varfree_lf), axis=1)
    df_varfree.drop('varfree_lf', axis=1, inplace=True)
    df_varfree.to_csv(out_file, sep='\t', columns=["sent", "cogs_lf", "types"], index=False, header=False)


if __name__ == "__main__":
    main()