# Reimplementation of the COGS grammar for Alto

This repository is intended to be an [Alto](https://github.com/coli-saar/alto)-based reimplementation of the original COGS grammar.

It contains a bunch of [Jinja](https://palletsprojects.com/p/jinja/) templates from which [IRTG](https://github.com/coli-saar/alto/wiki/GettingStarted) grammars can be produced. You will need to run `cogs-preprocess.py` to expand the templates to produce actual IRTGs:

```
$ python cogs-preprocess.py main.irtg > preprocessed-main.irtg
```

Note: cogs-preprocess.py is a variant of [preprocess.py](https://github.com/coli-saar/alto/blob/master/scripts/grammar-preprocessor/preprocess.py) from the Alto repository which adds COGS-specific functionality, such as computing vocabulary probabilities.

You can then load `preprocessed-main.irtg` into Alto.



### The OrderedFeatureTree algebra

The grammar in this repository is a synchronous grammar which constructs pairs of strings and [ordered feature trees](https://javadoc.jitpack.io/com/github/coli-saar/alto/master-SNAPSHOT/javadoc/de/saar/coli/algebra/OrderedFeatureTreeAlgebra.html). This is defined by the two "interpretation" lines at the start of the grammar:

```
interpretation english: de.up.ling.irtg.algebra.StringAlgebra
interpretation semantics: de.saar.coli.algebra.OrderedFeatureTreeAlgebra
```

Each grammar rule consists of three rows: one tree automaton rule which says how the nonterminals can be combined; one `english` row which says how the strings for the nonterminals are combined; and one `semantics` row which says how the meaning representations for the nonterminals are combined. On the `english` row, we use the `*` operator to concatenate strings; so in the rule

```
VP_passive -> r{{ cnt.next() }}(AUX, V_trans_omissible_pp)   
[english] *(?1, ?2)
[semantics] auxpass(?2, ?1)
```

the `*(?1, ?2)` says that we obtain a string for the `VP_passive` node by concatenating the string for the first child (`?1`, i.e. the `AUX` child) with the string for the second child (`?2`, i.e. the `V_trans_omissible_pp` child).

On the `semantics` row, we can use arbitrary symbols to combine the meaning representations of the children. In the example, the `auxpass` operation returns the meaning representation of the second child (`?2`), with the meaning representation for the first child (`?1`) attached under its root with an edge with label `auxpass`. This will be returned as the meaning representation for the `VP_passive` node.

There are two variants of each meaning-combining operation. When you write `auxpass` or `post_auxpass`, `?1` will be attached as the *last* child of `?2`'s root node. If you want `?1` to be attached under an `auxpass` edge as the *first* child of `?2`, you can use the `pre_auxpass` operation instead. This will make the difference between something like (with `auxpass`)

```
like(theme = Fred, auxpass = is)
```

and (with `pre_auxpass`)

```
like(auxpass = is, theme = Fred
```

In the grammar, we try to follow the convention that the order of edges in the meaning representation should reflect the order of the words in the sentence if possible. Thus in the grammar rule above one should probably use `pre_auxpass`.

### Control and raising

You can model control and raising in the grammar through parameter sharing. For instance, write

```
[semantics] "hope[agent = xcomp!agent]"
```

to indicate that "hope" is a subject control verb, which shares its own agent (on the left of the equals sign) with the agent of its xcomp argument (on the right of the equals sign). 

With the equals sign, "hope" retains its own "agent" argument, it simply shares it with its xcomp. If you replace the equals with an arrow, you can model raising:

```
[semantics] "seem[agent -> xcomp!agent]"
```

Note that you need to enclose `hope[agent = xcomp!agent]` in single or double quotes. This indicates to Alto that the whole thing is one symbol, and allows it to interpret it correctly. 

You cannot annotate variables with control/raising information; so `?1[agent = xcomp!agent]` is illegal. This means you will have to model control and raising in the lexicon.



### Rule counter

`cogs-preprocess.py` defines a counter object that can be used e.g. to generate consecutive rule numbers. This is useful because Alto expects that each rule uses a different terminal symbol after the arrow.

So for instance, you can write in the template:

```
VP_passive -> r{{ cnt.next() }}(AUX, V_trans_omissible_pp)   
[english] *(?1, ?2)  
[semantics] auxpass(?2, ?1)
```

Each occurrence of `{{ cnt.next() }}` will be expanded into a different number, e.g.

```
VP_passive -> r423(AUX, V_trans_omissible_pp)   
[english] *(?1, ?2)  
[semantics] auxpass(?2, ?1)
```


### Parsing

You can use Alto to parse a whole corpus of English sentences and produce meaning representations. This may be useful for building a test suite of sentences with their desired meanings.

To this end, write an [unannotated Alto corpus](https://github.com/coli-saar/alto/wiki/Corpora) that contains your input sentences. An example corpus is [available in this repository](https://github.com/coli-saar/cogs-generator-alto/blob/main/test-inputs.txt).

You can then batch parse this corpus as follows:

```
java -cp <alto-all.jar> de.up.ling.irtg.script.ParsingEvaluator -g <grammar.irtg> -I english -O semantics=cogs --no-derivations <corpus.txt>
```

The command line says that:

- the grammar (-g) is in the file `<grammar.irtg>` (replace with your actual grammar filename)
- the input corpus is `test-inputs.txt`
- we are reading input from the interpretation "english" (look at test-inputs.txt to see that it only contains lines for "english")
- we are printing output on the "semantics" interpretation using the "cogs" output codec, which does the COGS-specific postprocessing
- we only care about the "semantics" interpretation, not the derivation trees
- we are printing into the default file "out.txt"; you can specify a different output file with the "-o" parameter.

You can then compare the contents of out.txt against the gold output. For instance,

```
grep -cFwf out.txt gold-outputs.txt
```

will determine the number of lines in `out.txt` that are identical to their corresponding lines in `gold-outputs.txt` ([source](https://stackoverflow.com/questions/25283335/counting-equal-lines-in-two-files
)). You can use this to easily compute exact match.


### Corpus generation

See [here](https://github.com/coli-saar/alto/wiki/Generating-a-COGS-corpus) for an explanation of how to generate a new random corpus from a grammar.
