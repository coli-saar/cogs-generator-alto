# coding=utf-8
"""Convert Alto variable-free forms back into COGS logical forms."""
import re
import regex
from collections import defaultdict
import json
import pandas as pd
import sys

"""
varfree_lf_file = sys.argv[1]
cogs_file = sys.argv[2]

df_lf = pd.read_csv(varfree_lf_file,sep="\t",names=["sent","varfree_lf"])
df_cogs = pd.read_csv(cogs_file,sep="\t",names=["sent","cogs_lf"])
"""

with open('verbs2lemmas.json') as lemma_file:
    verbs_lemmas = json.load(lemma_file)
with open('proper_nouns.json') as propN_file:
    proper_nouns = json.load(propN_file)

def parse_varfreeLF(lf):
    """parse variable free LF to extract parenthesized head/arguments pairs
    @param lf: varfree lf
    @return: ('head', 'label1,argument1, label2, argument2')
    """
    stack = []
    heads = []
    previous_level_idx = 0
    for i, c in enumerate(lf):
        if c == '(':
            stack.append(i)
            level_i_lf = lf[previous_level_idx: i + 1]
            # match all words before "("
            head = re.findall(r'\w+(?= \()', level_i_lf)
            previous_level_idx = i + 1
            heads.extend(head)

        elif c == ')' and stack:
            start = stack.pop()
            arg = lf[start + 1: i].strip()
            # PCRE pattern regex that splits the string based on commas outside all parenthesis
            arg_substring_list = [x for x in regex.split(r"(\((?:[^()]++|(?1))*\))(*SKIP)(*F)|,", arg) if x]
            # match any chara ters as few as possible until a '(' is found, without '('
            pattern = '.+?(?=\()'
            match = [re.search(pattern,x).group(0).strip() if re.search(pattern,x) else x.strip() for x in arg_substring_list]
            arguments = ",".join(match)
            target_head = heads.pop()
            yield (target_head, arguments)


def varfree_lf_to_cogs(row):
    """Converts the given variable free logical form into COGS logical form.
    don't consider the primitives
    - Nouns (entities and unaries):
        Jack --> Jack
        cat --> cat ( x _ i )
        * cat --> * cat ( x _ i )
    - Verb functions with argument names become verb and argument roles
       eat ( agent = Jack ) --> eat . agent ( x _ 2 , Jack )
    - The variables representing nouns:
        eat ( agent = cat ) --> cat ( x _ 1 ) AND eat . agent ( x _ 2 , x _ 1 )
    This converter constructs a graph where variables are nodes and binaries
    are edges. After identifying the root, it then performs depth-first traversal
    to construct the output.
    Args:
      {"sent": sentence string
      "varfree_lf": variable free logical form string}
    Returns:
      The converted original cogs logical form.
    """
    sent = row["sent"]
    lf = row["varfree_lf"]
    tokens_list = sent.split()
    nodes2var = dict() # # no duplicated verbs/nouns allowed
    for idx, token in enumerate(tokens_list):
        if token in proper_nouns:
            nodes2var[token]=token
        elif token in verbs_lemmas.keys():
            nodes2var[verbs_lemmas[token]] = "x _ " + str(idx)
        else:
            nodes2var[token] = "x _ " + str(idx)

    # `children` maps variables to a list of (edge name, target node).
    head_arguments = set(parse_varfreeLF(lf))
    children_dict = defaultdict(list)
    ischild = set()
    for head,args in head_arguments:
        if "," in args:
            args = args.split(",")
            for child in args:
                child = [e.strip() for e in child.split("=") ]
                children_dict[head].append(child)
                ischild.add(child[1])
        else:
            child = [e.strip() for e in args.split("=")]
            children_dict[head].append(child)
            ischild.add(child[1])

    defini_nouns = []
    main_lf = []
    isdefinitive = False
    isnondefini = False
    for i,token in enumerate(sent.split()):
        if token in ("the","The"):
            isdefinitive = True
            continue
        elif token in ("a", "A"):
            isnondefini = True
            continue

        if isdefinitive:
            defini_nouns.append("* " + token + " ( x _ " + str(i) + " )")
            isdefinitive = False
        elif isnondefini:
            main_lf.append(token + " ( x _ " + str(i) + " )" )
            isnondefini = False

        if token in verbs_lemmas.keys():
            token = verbs_lemmas[token]

        if token in children_dict.keys():
            for child in children_dict[token]:
                sub_lf = token + " . " + child[0] + " ( x _ " + str(i) + " , " + nodes2var[child[1].strip("* ")] + " )"
                main_lf.append(sub_lf)

    if defini_nouns:
        return " ; ".join(defini_nouns) + " ; " + " AND ".join(main_lf)
    else:
        return " AND ".join(main_lf)

#row = {"sent":"A mouse in a cage liked that the cat on the table wanted to sneeze",
#       "varfree_lf":"like ( agent = mouse ( nmod . in = cage ) , ccomp = want ( agent = * cat ( nmod . on = * table ) , xcomp = sneeze ( agent = * cat ( nmod . on = * table ) ) ) )"}
#s = varfree_lf_to_cogs(row)
#print(s)

"""
df_lf["converted_lf"] = df_lf.apply(varfree_lf_to_cogs,axis=1)
df_lf["cogs_lf"] = df_cogs["cogs_lf"]

df_lf["correct"] = df_lf["converted_lf"] == df_cogs["cogs_lf"]
print(df_lf["correct"].value_counts())
#df_lf[df_lf["correct"]==False].to_csv("convert_error.tsv",sep="\t", header=False)
"""