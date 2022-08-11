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

The values 

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

TODO: Write this




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


