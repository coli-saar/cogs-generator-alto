# coding=utf-8
"""Convert Alto variable-free forms back into COGS logical forms."""
import re
import regex
from collections import defaultdict
import json
import pandas as pd
import sys



def parse_varfreeLF(lf):
    """parse variable free LF to extract parenthesized head/arguments pairs
    Args:
     lf: varfree lf
    Returns:
        ('head', 'label1 = argument1, label2 = argument2')
    """
    stack = []
    heads = []
    previous_level_idx = 0
    for i, c in enumerate(lf):
        if c == '(':
            stack.append(i)
            level_i_lf = lf[previous_level_idx: i + 1]
            # match the string before "("
            head = re.findall(r'\w+(?= \()', level_i_lf)
            previous_level_idx = i + 1
            heads.extend(head)
            #breakpoint()

        elif c == ')' and stack:
            start = stack.pop()
            arg = lf[start + 1: i].strip()
            # PCRE pattern regex that splits the string based on commas outside all parenthesis
            arg_substring_list = [x for x in regex.split(r"(\((?:[^()]++|(?1))*\))(*SKIP)(*F)|,", arg) if x]
            # match any characters as few as possible that are followed by an opening parenthesis
            pattern = '.+?(?=\()'
            match = [re.search(pattern,x).group(0).strip() if re.search(pattern,x) else x.strip() for x in arg_substring_list]
            arguments = ",".join(match)
            target_head = heads.pop()
            #breakpoint()
            yield (target_head, arguments)
def varfree_lf_to_cogs(sent,lf):
    """Converts the given variable free logical form into COGS logical form.
    - Nouns (entities and unaries):
        Jack --> Jack
        cat --> cat ( x _ i )
        * cat --> * cat ( x _ i )
    -  proper nouns
       eat ( agent = Jack ) --> eat . agent ( x _ 2 , Jack )
    - The variables representing common nouns:
        eat ( agent = cat ) --> cat ( x _ 1 ) AND eat . agent ( x _ 2 , x _ 1 )
    Args:
      "sent": sentence string
      "lf": variable free logical form string}
    Returns:
      The converted original cogs logical form.
    """

    tokens_list = sent.split()
    # primitives
    if len(tokens_list) == 1:
        cogs_lf = primitives_cogs_lf(tokens_list[0])
        return cogs_lf

    # nodes2var: dict mapping nodes to variables
    nodes2var = dict() #no duplicated verbs/nouns allowed
    v_list = []
    for idx, token in enumerate(tokens_list):
        if token in proper_nouns:
            nodes2var[token]=token
        elif token in ["Who","What"]:
            nodes2var[token] = "?"
        elif token in verbs_lemmas.keys():
            nodes2var[verbs_lemmas[token]] = "x _ " + str(idx)
            v_list.append(token)
        else:
            nodes2var[token] = "x _ " + str(idx)
    #if len(v_list)!=len(set(v_list)):
    #    raise ValueError("sentence '%s' has duplicated verbs (%s)" % (sent, v_list) )

    # `children` maps head nodes to a list of (arg label, target node).
    head_arguments = set(parse_varfreeLF(lf))
    #breakpoint()
    head2args = defaultdict(list)
    isChild = set()
    for head,args_str in head_arguments:
        if "," in args_str:
            args_str = args_str.split(",")
            for child in args_str:
                child = [e.strip() for e in child.split("=") ]
                head2args[head].append(child)
                isChild.add(child[1])
        else:
            child = [e.strip() for e in args_str.split("=")]
            head2args[head].append(child)
            isChild.add(child[1])
    #breakpoint()
    defini_nouns = []
    main_lf = []
    isDefinite = False
    isIndefinite = False
    for i,token in enumerate(sent.split()):
        if token in ("the","The"):
            isDefinite = True
            continue
        if token in ("a", "A"):
            isIndefinite = True
            continue

        if isDefinite:
            defini_nouns.append("* " + token + " ( x _ " + str(i) + " )")
            isDefinite = False
        elif isIndefinite:
            main_lf.append(token + " ( x _ " + str(i) + " )" )
            isIndefinite = False

        if token in verbs_lemmas.keys():
            token = verbs_lemmas[token]
        #breakpoint()
        if token in head2args.keys():
            for child in head2args[token]:
                sub_lf = token + " . " + child[0] + " ( x _ " + str(i) + " , " + nodes2var[child[1].strip("* ")] + " )"
                main_lf.append(sub_lf)

    if defini_nouns:
        return " ; ".join(defini_nouns) + " ; " + " AND ".join(main_lf)
    else:
        return " AND ".join(main_lf)


with open('lexicon/verbs2lemmas.json') as lemma_file:
    verbs_lemmas = json.load(lemma_file)
with open('lexicon/proper_nouns.json') as propN_file:
    proper_nouns = json.load(propN_file)
with open('lexicon/nouns.json') as file:
    nouns = json.load(file)
with open('lexicon/V_trans.json') as file:
    V_trans = json.load(file)
with open('lexicon/V_unacc.json') as file:
    V_unacc = json.load(file)
with open('lexicon/V_unerg.json') as file:
    V_unerg = json.load(file)

def primitives_cogs_lf(source):
    template_noun = "{}".format("LAMBDA a . {w} ( a )")
    template_proper_noun = "{}".format("{w}")
    template_transitive_verb = "{}".format("LAMBDA a . LAMBDA b . LAMBDA e . {w} . agent ( e , b ) AND {w} . theme ( e , a )")
    template_unaccusative_verb = "{}".format("LAMBDA a . LAMBDA e . {w} . theme ( e , a )")
    template_unergative_verb = "{}".format("LAMBDA a . LAMBDA e . {w} . agent ( e , a )")
    if source in nouns:
        template = template_noun
    elif source in proper_nouns:
        template = template_proper_noun
    elif source in V_unerg:
        template = template_unergative_verb
    elif source in V_unacc:
        template = template_unaccusative_verb
    elif source in V_trans:
        template = template_transitive_verb
    else:
        raise ValueError("invalid source type: '%s' " % source)
    cogs_lf = template.format(w = source)
    return cogs_lf

#sent = "Emma bought the cake that the student that the woman that William liked saw baked "
#cogs_wrong = "* girl ( x _ 4 ) ; * rose ( x _ 7 ) ; hope . agent ( x _ 1 , Emma ) AND hope . ccomp ( x _ 1 , x _ 10 ) AND give . theme ( x _ 5 , x _ 7 ) AND give . recipient ( x _ 5 , x _ 13 ) AND give . agent ( x _ 5 , x _ 16 ) AND give . agent ( x _ 5 , x _ 4 ) AND give . theme ( x _ 5 , x _ 7 ) AND give . recipient ( x _ 5 , Olivia ) AND rose . nmod ( x _ 7 , x _ 10 ) AND give . theme ( x _ 10 , x _ 7 ) AND give . recipient ( x _ 10 , x _ 13 ) AND give . agent ( x _ 10 , x _ 16 ) AND give . agent ( x _ 10 , x _ 4 ) AND give . theme ( x _ 10 , x _ 7 ) AND give . recipient ( x _ 10 , Olivia ) AND father ( x _ 13 ) AND chicken ( x _ 16 )"
#lf = "buy ( agent = Emma , theme = * cake ( nmod = bake ( agent = * student ( nmod = see ( agent = * woman ( nmod =like ( agent = William , theme = * woman ) ) , theme = * student ) ) , theme = * cake ) ) )"
#sent = "The cat that froze smiled ."
#lf = " smile ( agent = * cat ( nmod = freeze ( theme = * cat ) ) )"
sent3 = "A child valued that the butterfly liked that a mirror was liked by Liam ."
cogsLF3 = "* butterfly ( x _ 5 ) ; child ( x _ 1 ) AND value . agent ( x _ 2 , x _ 1 ) AND value . ccomp ( x _ 2 , x _ 6 ) AND like . agent ( x _ 6 , x _ 5 ) AND like . ccomp ( x _ 6 , x _ 11 ) AND mirror ( x _ 9 ) AND like . theme ( x _ 11 , x _ 9 ) AND like . agent ( x _ 11 , Liam )"
varfreeLF3 = "value ( agent = child , ccomp = like ( agent = * butterfly , ccomp = like ( theme = mirror , agent = Liam ) ) )"




"""if __name__ == "__main__":

  varfree_lf_file = sys.argv[1]
  cogs_file = sys.argv[2]

  df_varfree = pd.read_csv(varfree_lf_file, sep="\t", names=["sent", "varfree_lf","type"])
  df_cogs = pd.read_csv(cogs_file, sep="\t", names=["sent", "cogs_lf","type"])
  df_varfree["converted_lf"] = df_varfree.apply(lambda x: varfree_lf_to_cogs(x.sent, x.varfree_lf), axis=1)
  df_varfree["cogs_lf"] = df_cogs["cogs_lf"]
  exact_match = (df_varfree["converted_lf"] == df_varfree["cogs_lf"]).sum()
  total_items = df_varfree.shape[0]
  print(f"Exact match rate between converted LFs and original cogs LFs: {exact_match}/{total_items} ({exact_match / total_items:.2f})")
"""
