NA = "Na<span style='vertical-align:super; font-size:small; '>+</span>"
CA = "Ca<span style='vertical-align:super; font-size:small; '>2+</span>"
NCX = NA .. "/" .. CA
K = "K<span style='vertical-align:super; font-size:small; '>+</span>"
KD = "K<span style='vertical-align:sub; font-size:small; '>D</span>"
EC50 = "EC<span style='vertical-align:sub; font-size:small; '>50</span>"
LD50 = "LD<span style='vertical-align:sub; font-size:small; '>50</span>"
H = "H<span style='vertical-align:super; font-size:small; '>+</span>"
H3O = "H<span style='vertical-align:sub; font-size:small; '>3</span>O<span style='vertical-align:super; font-size:small; '>+</span>"
H2O = "H<span style='vertical-align:sub; font-size:small; '>2</span>O"
CO2 = "CO<span style='vertical-align:sub; font-size:small; '>2</span>"
O2 = "O<span style='vertical-align:sub; font-size:small; '>2</span>"
LP = "L<span style='vertical-align:sub; font-size:small; '>p</span>"

CD8 = "CD8<span style='vertical-align:super; font-size:small; '>+</span>"
CD4 = "CD4<span style='vertical-align:super; font-size:small; '>+</span>"

PGG2 = "PGG<span style='vertical-align:sub; font-size:small; '>2</span>"
PGH2 = "PGH<span style='vertical-align:sub; font-size:small; '>2</span>"
PGI2 = "PGI<span style='vertical-align:sub; font-size:small; '>2</span>"
PGI3 = "PGI<span style='vertical-align:sub; font-size:small; '>3</span>"
TXA2 = "TXA<span style='vertical-align:sub; font-size:small; '>2</span>"
TXA3 = "TXA<span style='vertical-align:sub; font-size:small; '>3</span>"

A1 = "&alpha;<span style='vertical-align:sub; font-size:small; '>1</span>"
A2 = "&alpha;<span style='vertical-align:sub; font-size:small; '>2</span>"
B1 = "&beta;<span style='vertical-align:sub; font-size:small; '>1</span>"
B2 = "&beta;<span style='vertical-align:sub; font-size:small; '>2</span>"
M1 = "M<span style='vertical-align:sub; font-size:small; '>1</span>"
M2 = "M<span style='vertical-align:sub; font-size:small; '>2</span>"
M3 = "M<span style='vertical-align:sub; font-size:small; '>3</span>"

ST = "<span style='vertical-align:super; font-size:small; '>st</span>"
ND = "<span style='vertical-align:super; font-size:small; '>nd</span>"
RD = "<span style='vertical-align:super; font-size:small; '>rd</span>"
TH = "<span style='vertical-align:super; font-size:small; '>th</span>"

G0 = "G<span style='vertical-align:sub; font-size:small; '>0</span>"
G1 = "G<span style='vertical-align:sub; font-size:small; '>1</span>"
G2 = "G<span style='vertical-align:sub; font-size:small; '>2</span>"
GAI = "G<span style='vertical-align:sub; font-size:small; '>&alpha;i</span>"
GAQ = "G<span style='vertical-align:sub; font-size:small; '>&alpha;q</span>"
IP3R = "IP<span style='vertical-align:sub; font-size:small; '>3</span>R"
GAS = "G<span style='vertical-align:sub; font-size:small; '>&alpha;s</span>"
INA = "I<span style='vertical-align:sub; font-size:small; '>Na</span>"
IK = "I<span style='vertical-align:sub; font-size:small; '>K</span>"
ICA = "I<span style='vertical-align:sub; font-size:small; '>Ca</span>"
IFUNNY = "I<span style='vertical-align:sub; font-size:small; '>f</span>"
NADP = "NADP<span style='vertical-align:super; font-size:small; '>+</span>"

CAI = "[" .. CA .. "]<span style='vertical-align:sub; font-size:small; '>i</span>"
CAMPI = "[cAMP]<span style='vertical-align:sub; font-size:small; '>i</span>"

-- Tried many other Unicode arrow symbols but they're ugly in some fonts
DA = "<span style='font-weight:bold; color:blue; '>&darr;</span>"
UA = "<span style='font-weight:bold; color:blue; '>&uarr;</span>"
DDA = "<span style='font-weight:bold; color:blue; '>&#x21ca;</span>"
UUA = "<span style='font-weight:bold; color:blue; '>&#x21c8;</span>"

-- A "P" in a circle, denoting phosphorylation
PPN = "&#x024c5;" 

T4 = "&there4;"
-- because (upside down therefore)
BC = "&#x2235;"

POS = "<span style='color:green; font-weight:bold; '>&oplus;</span>"
NEG = "<span style='color:red; font-weight:bold; '>&#x02296;</span>"

-- There's no X-bar in Unicode; combine x and the bar instead.
-- FIXME: this doesn't work in some fonts -- why not?
MEAN = "x&#772;"

-- Interrobang
IBANG = "&#x203D;"

-- Smiley
SMILEY = "&#x263a;"
SMILE = SMILEY

-- Replacement way of saying '<br/>', because that gets replaced with '\n' before execution of escapes.
BR = "<br />"

-- Meaning, not presentation :)
raised, raises, increased, high, higher, greater, elevated, raising, maximises, maximising =
UA,     UA,     UA,        UA,   UA,     UA,      UA,       UA,      UA,        UA

lowered, lowers, lower, lowering, minimises, minimising, reduces, reducing, reduced, low, decreased, decreasing, depressed =
DA,      DA,     DA,    DA,       DA,        DA,         DA,      DA,       DA,      DA,  DA,        DA,         DA

inhibits, inhibited, inhibiting =
NEG,      NEG,       NEG

activates, promotes, activating, promoting =
POS,       POS,      POS,        POS
