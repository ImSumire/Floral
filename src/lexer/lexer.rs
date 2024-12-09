#[allow(unused_imports)]
use super::token::{Token, TokenKind, KEYWORDS};
use crate::utils::estimate_size;

pub struct Lexer {
    input: String,
    position: usize,  // Current character index
}

impl Lexer {
    pub fn new(input: String) -> Self {
        Self { input, position: 0 }
    }

    fn next_char(&mut self) -> Option<char> {
        self.position += 1;
        self.input.chars().nth(self.position - 1)
    }

    fn peek_char(&self) -> Option<char> {
        self.input.chars().nth(self.position)
    }

    fn skip_whitespace_and_comments(&mut self) {
        while let Some(ch) = self.peek_char() {
            if ch == '/' {
                self.next_char();  // Skip '/'

                if let Some(ch) = self.peek_char() {
                    // Line comment
                    if ch == '/' {
                        self.next_char();
                        // Skip to end of line (jump over multiple characters at once)
                        while self.next_char().map(|c| c != '\n').unwrap_or(false) {}
                    }

                    // Block comment
                    else if ch == '*' {
                        self.next_char();  // Skip '*'

                        while let Some(ch) = self.peek_char() {
                            if ch == '*' {
                                self.next_char();  // Skip '*'
                                if let Some(ch) = self.peek_char() {
                                    if ch == '/' {
                                        self.next_char();  // Skip '/'
                                        break;  // End of block comment
                                    }
                                }
                            } else {
                                self.next_char();  // Continue skiping characters
                            }
                        }
                    }
                }
            }
            // Whitespace
            else if ch.is_whitespace() {
                self.next_char();
            } else {
                break;  // Exit when encountering non-whitespace and non-comment characters
            }
        }
    }

    fn slice(&self, start: usize) -> &str {
        &self.input[start..self.position]
    }

    fn consume_while<F>(&mut self, mut condition: F) where F: FnMut(char) -> bool {
        while let Some(ch) = self.peek_char() {
            if condition(ch) {
                self.next_char();
            } else {
                break;
            }
        }
    }

    fn next(&mut self) -> Option<Token> {
        self.skip_whitespace_and_comments();

        let start = self.position;
        
        let kind = match self.peek_char()? {
            // String literal
            '"' => {
                self.next_char();  // Skip '"'

                while let Some(ch) = self.peek_char() {
                    if ch == '"' {
                        self.next_char();  // Skip '"'
                        break;
                    }

                    if ch == '\\' {
                        self.next_char();
                        self.next_char();
                    }
                    else {
                        self.next_char();
                    }
                }

                TokenKind::String
            }

            // Char literal
            '\'' => {
                self.next_char();  // Skip '''

                if let Some(ch) = self.peek_char() {
                    if ch == '\\' {
                        self.next_char();
                    }
                }

                self.next_char();  // Skip the character
                self.next_char();  // Skip '''
                TokenKind::Char
            }

            // Identifier or Keyword
            ch if ch.is_alphabetic() || ch == '_' => {
                self.consume_while(|c| c.is_alphanumeric() || c == '_');

                if KEYWORDS.contains(self.slice(start)) {
                    TokenKind::Keyword
                } else {
                    TokenKind::Identifier
                }
            }

            // Literal number
            ch if ch.is_digit(10) => {
                // Binary and hex literal ints
                if ch == '0' {
                    self.next_char();
                    if let Some(ch) = self.peek_char() {
                        match ch {
                            'b' => {
                                self.next_char(); // Skip 'b'
                                self.consume_while(|c| c == '0' || c == '1');
                                TokenKind::Int
                            }
    
                            'x' => {
                                self.next_char(); // Skip 'x'
                                self.consume_while(|c| c.is_digit(16)); // Hex digits
                                TokenKind::Int
                            }
    
                            'o' => {
                                self.next_char(); // Skip 'o'
                                self.consume_while(|c| c.is_digit(8)); // Octal digits
                                TokenKind::Int
                            }
    
                            _ => {
                                self.consume_while(|c| c.is_digit(10));
                                TokenKind::Int
                            }
                        }
                    }
                    
                    else {
                        // If there is no valid digit after '0', treat as decimal
                        self.consume_while(|c| c.is_digit(10)); // Decimal digits
                        TokenKind::Int
                    }
                }

                else {
                    self.consume_while(|c| c.is_digit(10));

                    // Check if there's a decimal point, indicating a float
                    if let Some('.') = self.peek_char() {
                        self.next_char(); // Skip the '.'
                        self.consume_while(|c| c.is_digit(10));
                        TokenKind::Float
                    } else {
                        TokenKind::Int
                    }
                }
            }
            
            // == or =
            '=' => {
                self.next_char();  // Skip '='
                if let Some('=') = self.peek_char() {
                    self.next_char();  // Skip '='
                }
                TokenKind::Operator
            }

            // != or !
            '!' => {
                self.next_char();  // Skip '!'
                if let Some('=') = self.peek_char() {
                    self.next_char();  // Skip '='
                }
                TokenKind::Operator
            }
            
            // Operator
            '+' | '-' | '*' | '/' | '.' => {
                self.next_char();
                TokenKind::Operator
            }

            // Handle the `::` operator
            ':' => {
                self.next_char(); // Skip ':'
                if let Some(':') = self.peek_char() {
                    self.next_char(); // Skip ':'
                    TokenKind::Operator  // Treat `::` as an operator
                } else {
                    TokenKind::Punctuation  // If only one ':', treat it as punctuation
                }
            }

            // Punctuation
            '(' | ')' | '{' | '}' | ';' | ',' => {
                self.next_char();
                TokenKind::Punctuation
            }

            // Unknow
            _ch => {
                self.next_char();
                TokenKind::Unknown
            }
        };

        let end = self.position;
        Some(Token { kind, start, end })
    }

    pub fn tokensize(&mut self, path: &str) -> Vec<Token> {
        let mut tokens = Vec::with_capacity(estimate_size(path));  // Pre-allocate space for tokens

        while self.position < self.input.len() {
            if let Some(token) = self.next() {
                tokens.push(token);
            }
        }

        tokens
    }

    #[allow(dead_code)]
    fn get_line(&self, index: usize) -> usize {
        self.input[0..index].matches('\n').count() + 1
    }

    #[allow(dead_code)]
    pub fn pprint(&self, tokens: &Vec<Token>) {
        let mut line = 0;

        for token in tokens {
            let color = match token.kind {
                TokenKind::Char => "32", // Green
                TokenKind::Float => "33", // Yellow
                TokenKind::Identifier => "37", // White
                TokenKind::Int => "33", // Yellow
                TokenKind::Keyword => "35", // Magenta
                TokenKind::Operator => "36", // Cyan
                TokenKind::Punctuation => "34", // Blue
                TokenKind::String => "32", // Green
                TokenKind::Unknown => "31", // Red
            };

            let current_line = self.get_line(token.start);
            while line < current_line {
                line += 1;
                print!("\n\x1b[37;2m{line:<4}|\x1b[0m ");
            }

            print!("\x1b[37m{:?}:\x1b[{};1m{}\x1b[0m ", token.kind, color, token.value(&self.input));

        }
        println!();
    }
}