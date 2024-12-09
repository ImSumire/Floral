// Branch-less fanatic
#[allow(dead_code)]
pub static KEYWORDS: phf::Set<&'static str> = phf::phf_set! {
    "use", "import",
    "fn", "iter", "yield", "return",
    "let", "const",
    "in", "for", "while", "break", "continue",
    "impl", "enum", "trait", "struct",
    "if", "else", "elif",
};

#[derive(Debug, PartialEq)]
pub struct Token {
    pub kind: TokenKind,
    pub start: usize,  // Starting index
    pub end: usize,  // Ending index
}

impl Token {
    pub fn value<'a>(&self, input: &'a str) -> &'a str {
        &input[self.start..self.end]
    }
}

#[derive(Debug, PartialEq)]
pub enum TokenKind {
    Keyword,
    Identifier,

    // Symbols
    Operator,
    Punctuation,

    // Literals
    String,
    Char,
    Int,
    Float,
    
    Unknown,
}
