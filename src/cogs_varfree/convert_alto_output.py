# coding=utf-8
"""Convert the variable free format to original cogs format"""


import varfreeLF_converter
import pandas as pd
import sys
from sklearn.model_selection import train_test_split

varfree_lf_file = sys.argv[1]
out_file = sys.argv[2]

def main():
    df_varfree = pd.read_csv(varfree_lf_file, sep="\t", names=["sent", "varfree_lf","types"])#,"c_label"])
    df_varfree["cogs_lf"] = df_varfree.apply(lambda x: varfreeLF_converter.varfree_lf_to_cogs(x.sent, x.varfree_lf), axis=1)
    df_varfree.drop('varfree_lf', axis=1, inplace=True)

    #df_varfree["sent"] = df_varfree["sent"] + " ?" # for wh-Q
    df_varfree = df_varfree[["sent", "cogs_lf","types"]]#,"c_label"]]

    df_varfree.to_csv(out_file, sep='\t', index=False, header=False)
    #for train split
    """train, temp, _, _ = train_test_split(df_varfree, df_varfree, test_size=0.2, random_state=42)
    dev, test, _, _ = train_test_split(temp, temp, test_size=0.5, random_state=42)
    # breakpoint()
    train.to_csv(out_file + "_train.tsv", sep='\t', index=False, header=False)
    dev.to_csv(out_file + "_dev.tsv", sep='\t', index=False, header=False)
    test.to_csv(out_file + "_test.tsv", sep='\t', index=False, header=False)"""


if __name__ == "__main__":
    main()