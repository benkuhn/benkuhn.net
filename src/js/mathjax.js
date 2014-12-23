var macros = {
    f: ["\\frac{#1}{#2}", 2],
    ang: ["\\left\\langle#1\\right\\rangle", 1],
    abs: ["\\left\\lvert#1\\right\\rvert", 1],
    norm: ["\\left\\lVert#1\\right\\rVert", 1],
    sqb: ["\\left[#1\\right]", 1],
    cub: ["\\left\\{#1\\right\\}", 1],
    floor: ["\\left\\lfloor #1 \\right\\rfloor", 1],
    ceil: ["\\left\\lceil #1 \\right\\rceil", 1],
    bm: ["\\left(\\begin{array}{cc} #1 & #2 \\\\ #3 & #4 \\end{array}\\right)", 4],
};

// shorter names for longer commands
var SHORTNAMES = [
    ['v', 'vec'],
    ['h', 'hat'],
    ['c', 'mathcal'],
    ['del', 'partial'],
    ['Del', 'nabla'],
    ['b', 'mathbf'],
    ['bb', 'mathbb'],
    ['cc', 'overline'], // complex conjugate
    ['ol', 'overline'],
]

SHORTNAMES.map(function (lst) {
    var alias = lst[0];
    var name = lst[1];
    macros[alias] = ["\\" + name + "{#1}", 1];
});

// blackboard letters
var BB_LETTERS = 'NZQRCF';
BB_LETTERS.split('').map(function (letter) {
    macros[letter] = "\\mathbb{" + letter + "}";
});

var CAL_LETTERS = 'FLNM';
CAL_LETTERS.split('').map(function (letter) {
    macros['c' + letter] = "\\mathcal{" + letter + "}";
});

// math operators and distributions
var OPERATORS = [
    'Bin',
    'Pois',
    'Binom',
    'NBinom',
    'HGeom',
    'Geom',
    'Bern',
    'Pareto',
    'Unif',
    'Norm',
    'Expo',
    'Beta',
    ['Gam', 'Gamma'],
    'Var',
    'Cov',
    'Corr',
];

OPERATORS.map(function (obj) {
    var opname, optext;
    if (Array.isArray(opname)) {
        opname = obj[0];
        optext = obj[1];
    }
    else {
        opname = optext = obj;
    }
    macros[opname] = "\\operatorname{" + optext + "}";
});

// greek letters: each one gets an alias of its first two letters
var GREEK_LETTERS = [
    'omega',
    'Omega',
    'alpha',
    'beta',
    'gamma',
    'Gamma',
    'delta',
    'Delta',
    'epsilon',
    'zeta',
    'theta',
    'Theta',
    'iota',
    'kappa',
    'Lambda',
    'lambda',
    'upsilon',
    'Sigma',
    'sigma',
    // also some other random things
    'prime',
]
GREEK_LETTERS.map(function (name) {
    var alias = name.slice(0, 2);
    macros[alias] = '\\' + name;
});


window.MathJax = {
    extensions: ["tex2jax.js"],
    tex2jax: {inlineMath: [['$[',']'], ['\\(','\\)']]},
    TeX: {
        Macros: macros
    }
};
