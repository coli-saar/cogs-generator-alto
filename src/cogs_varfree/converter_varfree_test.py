# coding=utf-8
"""Tests for varfreeLF_converter."""
import varfreeLF_converter
import tensorflow as tf


class CogsConverterTest(tf.test.TestCase):

  def test_single_entity(self):
    # James investigated .
    expected = "investigate . agent ( x _ 1 , James )"
    row = {"varfree_lf" : "investigate ( agent = James )",
    "sent" : "James investigated"}
    self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)

    # A cat floated .
    expected = "cat ( x _ 1 ) AND float . theme ( x _ 2 , x _ 1 )"
    row = {"varfree_lf" : "float ( theme = cat )",
    "sent" : "A cat floated"}
    self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)

    # The captain ate .
    expected = "* captain ( x _ 1 ) ; eat . agent ( x _ 2 , x _ 1 )"
    row = {"varfree_lf" : "eat ( agent = * captain )",
    "sent" : "The captain ate"}
    self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)

  def test_flat_lfs(self):
    # The sailor dusted a boy .
    expected = ("* sailor ( x _ 1 ) ; dust . agent ( x _ 2 , x _ 1 ) "
          "AND dust . theme ( x _ 2 , x _ 4 ) AND boy ( x _ 4 )")
    row = {"varfree_lf" : "dust ( agent = * sailor , theme = boy )",
    "sent" : "The sailor dusted a boy"}
    self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)

    # Eleanor sold Evelyn the cake .
    expected = ("* cake ( x _ 4 ) ; sell . agent ( x _ 1 , Eleanor ) "
          "AND sell . recipient ( x _ 1 , Evelyn ) "
          "AND sell . theme ( x _ 1 , x _ 4 )")
    row = {"varfree_lf":"sell ( agent = Eleanor , recipient = Evelyn , theme = * cake )",
    "sent":"Eleanor sold Evelyn the cake"}
    self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)

  def test_nested_lfs(self):
      # The girl needed to cook .
      expected = ("* girl ( x _ 1 ) ; need . agent ( x _ 2 , x _ 1 ) "
                  "AND need . xcomp ( x _ 2 , x _ 4 ) "
                  "AND cook . agent ( x _ 4 , x _ 1 )")
      row = {"varfree_lf": "need ( agent = * girl , xcomp = cook ( agent = * girl ) )",
             "sent": "The girl needed to cook"}
      self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)
      # The penguin dreamed that Emma wanted to paint .
      expected = ("* penguin ( x _ 1 ) ; dream . agent ( x _ 2 , x _ 1 ) "
                  "AND dream . ccomp ( x _ 2 , x _ 5 ) "
                  "AND want . agent ( x _ 5 , Emma ) "
                  "AND want . xcomp ( x _ 5 , x _ 7 ) "
                  "AND paint . agent ( x _ 7 , Emma )")
      row = {
          "varfree_lf": "dream ( agent = * penguin , ccomp = want ( agent = Emma , xcomp = paint ( agent = Emma ) ) )",
          "sent": "The penguin dreamed that Emma wanted to paint"}
      self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)

      # The dog in a bakery in the bag sneezed .
      expected = ("* dog ( x _ 1 ) ; * bag ( x _ 7 ) ; "
                  "dog . nmod . in ( x _ 1 , x _ 4 ) "
                  "AND bakery ( x _ 4 ) AND bakery . nmod . in ( x _ 4 , x _ 7 ) "
                  "AND sneeze . agent ( x _ 8 , x _ 1 )")
      row = {"varfree_lf": "sneeze ( agent = * dog ( nmod . in = bakery ( nmod . in = * bag ) ) )",
             "sent": "The dog in a bakery in the bag sneezed"}
      self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)

      expected = ("* cat ( x _ 8 ) ; * table ( x _ 11 ) ; "
                  "mouse ( x _ 1 ) AND mouse . nmod . in ( x _ 1 , x _ 4 ) "
                  "AND cage ( x _ 4 ) AND like . agent ( x _ 5 , x _ 1 ) "
                  "AND like . ccomp ( x _ 5 , x _ 12 ) "
                  "AND cat . nmod . on ( x _ 8 , x _ 11 ) "
                  "AND want . agent ( x _ 12 , x _ 8 ) "
                  "AND want . xcomp ( x _ 12 , x _ 14 ) "
                  "AND sneeze . agent ( x _ 14 , x _ 8 )")
      row = {"sent": "A mouse in a cage liked that the cat on the table wanted to sneeze",
             "varfree_lf": "like ( agent = mouse ( nmod . in = cage ) , ccomp = want ( agent = * cat ( nmod . on = * table ) , xcomp = sneeze ( agent = * cat ( nmod . on = * table ) ) ) )"}
      self.assertEqual(varfreeLF_converter.varfree_lf_to_cogs(row), expected)


if __name__ == "__main__":
  tf.test.main()