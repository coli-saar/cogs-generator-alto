# Reimplementation of the COGS grammar for Alto

This repository is intended to be an [Alto](https://github.com/coli-saar/alto)-based reimplementation of the original COGS grammar.

It contains a bunch of [Jinja](https://palletsprojects.com/p/jinja/) templates from which [IRTG](https://github.com/coli-saar/alto/wiki/GettingStarted) grammars can be produced. You will need to run `cogs-preprocess.py` to expand the templates to produce actual IRTGs:

```
$ python cogs-preprocess.py main.irtg > preprocessed-main.irtg
```

Note: cogs-preprocess.py is a variant of [preprocess.py](https://github.com/coli-saar/alto/blob/master/scripts/grammar-preprocessor/preprocess.py) from the Alto repository which adds COGS-specific functionality, such as computing vocabulary probabilities.

You can then load `preprocessed-main.irtg` into Alto.


### Rule counter

`preprocess.py` defines a counter object that can be used e.g. to generate consecutive rule numbers. This is useful because Alto expects that each rule uses a different terminal symbol after the arrow.

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


