# Future:
#
#   $class(<text>, <class>)
#     applies CSS class to text, as defined in either the card template or an external stylesheet called ss.css in the plugins directory
#   $rcsl(orange, apple, pear tree, honey bee)
#     randomises the order of the given comma-separated list
#   $rorl(go big, go home)
#     randomises the order of the given comma-separated list, but uses "or" between the final two items
#   $randl(swings, roundabouts)
#     randomises the order of the given comma-separated list, but uses "and" between the final two items
#   $pick(woven, trabecular, cancellous, spongy)
#     randomly pick any of a list of strings; also sets a variable for use by...
#   $pick2(woven, trabecular, cancellous, spongy)
#     pick the same indexed thing as was picked by $pick(...);
#     this allows a random choice to be made once then used in both question and answer
#   $list(<yaml>)
#     HTML-ify a yaml structure to make a list, seeing as QT can't leave 'em the fuck alone
#   $rlist(<yaml>)
#     same as $list but randomises the 1st-level order

NA = "Na<sup>+</sup>"
K = "K<sup>+</sup>"
CA = "Ca<sup>2+</sup>"
H = "H<sup>+</sup>"
H3O = "H<sub>3</sub>O<sup>+</sup>"
H2O = "H<sub>2</sub>O"
CO2 = "CO<sub>2</sub>"

# vim: softtabstop=8 shiftwidth=8 expandtab
