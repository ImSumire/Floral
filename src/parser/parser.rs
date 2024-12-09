use std::str::FromStr;

use crate::lexer::token::{Token, TokenKind};
use super::ast::{Expr, Literal, Param, Statement};

pub struct Parser {
    input: String,
    tokens: Vec<Token>,
    position: usize
}

// Token Stream
impl Parser {
    pub fn new(input: String, tokens: Vec<Token>) -> Self {
        Self { input, tokens, position: 0 }
    }

    fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.position)
    }

    fn peek_kind(&self) -> Option<&TokenKind> {
        self.peek().map(|token| &token.kind)
    }

    fn match_kind(&mut self, kind: TokenKind) -> bool {
        if self.peek_kind() == Some(&kind) {
            // self.advance();
            true
        } else {
            false
        }
    }

    fn peek_value(&self) -> Option<&str> {
        self.peek().map(|token| token.value(&self.input))
    }

    fn advance(&mut self) -> Option<&Token> {
        self.position += 1;
        self.tokens.get(self.position - 1)
    }

    /* fn expect(&mut self, kind: TokenKind) -> Result<&Token, String> {
        match self.peek() {
            Some(token) if token.kind == kind => Ok(self.advance().unwrap()),
            Some(token) => Err(format!("Expected {:?}, found {:?}", kind, token.kind)),
            None => Err("Unexpected end of input".to_string())
        }
    } */
}

// Expression Parsing
impl Parser {
    fn parse_literal(&mut self) -> Option<Expr> {
        let token = self.peek()?;
        let value = token.value(&self.input);

        match token.kind {
            TokenKind::Int => {
                let int_val = value.parse::<i64>().ok()?;
                self.advance();
                Some(Expr::Literal(Literal::Int(int_val)))
            }
            TokenKind::Float => {
                let float_val = value.parse::<f64>().ok()?;
                self.advance();
                Some(Expr::Literal(Literal::Float(float_val)))
            }
            TokenKind::String => {
                let string_val = String::from_str(value).unwrap();
                self.advance();
                Some(Expr::Literal(Literal::String(string_val)))
            }
            TokenKind::Char => {
                let char_val = value.parse::<char>().ok()?;
                self.advance();
                Some(Expr::Literal(Literal::Char(char_val)))
            }
            _ => None,
        }
    }

    fn parse_identifier(&mut self) -> Option<Expr> {
        if let Some(TokenKind::Identifier) = self.peek_kind() {
            let value = self.peek_value()?.to_string();
            self.advance();
            Some(Expr::Identifier(value))
        } else {
            None
        }
    }

    fn parse_expression(&mut self) -> Option<Expr> {
        self.parse_binary_op()
    }

    fn parse_binary_op(&mut self) -> Option<Expr> {
        let mut left = self.parse_primary()?;

        while let Some(TokenKind::Operator) = self.peek_kind() {
            let operator = self.peek_value()?.to_string();
            self.advance();
            let right = self.parse_primary()?;

            left = Expr::BinaryOp {
                left: Box::new(left),
                operator,
                right: Box::new(right)
            };
        }

        Some(left)
    }

    fn parse_primary(&mut self) -> Option<Expr> {
        // Literal
        if let Some(literal) = self.parse_literal() {
            return Some(literal)
        }

        if let Some(identifier) = self.parse_identifier() {
            // Check for function call
            if self.match_kind(TokenKind::Punctuation) && self.peek_value() == Some("(") {
                let mut args = Vec::new();

                while self.peek_kind() != Some(&TokenKind::Punctuation) || self.peek_value() != Some(")") {
                    if !args.is_empty() {
                        // self.match_kind(TokenKind::Punctuation);  // Skip comma
                        self.advance();
                    }
                    args.push(self.parse_expression()?);
                }

                // self.match_kind(TokenKind::Punctuation);  // Consume ')'
                self.advance();

                return Some(Expr::FunctionCall {
                    name: if let Expr::Identifier(name) = identifier {
                        name
                    } else {
                        unreachable!()
                    },
                    args
                });
            }

            return Some(identifier);
        }

        if let Some(scope) = self.parse_scope() {
            return Some(scope);
        }

        None
    }

    fn parse_scope(&mut self) -> Option<Expr> {
        if self.match_kind(TokenKind::Punctuation) && self.peek_value() == Some("{") {
            self.advance();  // Consume '{'

            let mut body = Vec::new();
            while self.peek_kind() != Some(&TokenKind::Punctuation) || self.peek_value() != Some("}") {
                if let Some(statement) = self.parse_statement() {
                    body.push(statement);
                } else {
                    return None;
                }
            }

            self.advance();  // Consume '}'
            return Some(Expr::Scope { body });
        }

        None
    }

    fn parse_statement(&mut self) -> Option<Statement> {
        // DEV
        /* if let Some(token) = self.peek() {
            println!("\x1b[30m{:?}:\x1b[37;1m{}", token.kind, token.value(&self.input));
            println!("{:?}", token);
            println!();
        } */

        // Let
        if self.match_kind(TokenKind::Keyword) && self.peek_value() == Some("let") {
            self.advance();

            let name = self.parse_identifier()?;
            let name = if let Expr::Identifier(name) = name {
                name
            } else {
                return None;
            };

            // self.match_kind(TokenKind::Operator);  // Expect '='
            self.advance();
            let value = self.parse_expression()?;
            return Some(Statement::Let { name, value });
        }

        // Fn
        if self.match_kind(TokenKind::Keyword) && self.peek_value() == Some("fn") {
            self.advance();  // Comsume 'fn'

            let name = self.parse_identifier()?;
            let name = if let Expr::Identifier(name) = name {
                name
            } else {
                return None;
            };

            // self.match_kind(TokenKind::Punctuation);  // Expect '('
            self.advance();  // Consume '('

            let mut parameters = Vec::new();
            while self.peek_kind() != Some(&TokenKind::Punctuation) || self.peek_value() != Some(")") {
                if !parameters.is_empty() {
                    // self.match_kind(TokenKind::Punctuation);  // Skip comma
                    self.advance();  // Consume ','
                }
                
                let name = self.parse_identifier()?;
                let name = if let Expr::Identifier(name) = name {
                    name
                } else {
                    return None;
                };

                // self.match_kind(TokenKind::Punctuation);  // Consume ':'
                self.advance();  // Consume ':'
                
                let r#type = self.parse_identifier()?;
                let r#type = if let Expr::Identifier(r#type) = r#type {
                    r#type
                } else {
                    return None;
                };
                
                parameters.push(Param { name, r#type });
            }

            // self.match_kind(TokenKind::Punctuation);  // Consume ')'
            self.advance();

            // self.match_kind(TokenKind::Punctuation);  // Consume ':'
            self.advance();

            let r#type = self.parse_identifier()?;
            let r#type = if let Expr::Identifier(r#type) = r#type {
                r#type
            } else {
                return None;
            };

            // Parse the function body as a scope
            if let Some(body) = self.parse_scope() {
                return Some(Statement::Function {
                    name,
                    r#type,
                    parameters,
                    body,
                });
            } else {
                return None; // Failed to parse the function body
            }
        }

        if self.match_kind(TokenKind::Keyword) && self.peek_value() == Some("return") {
            self.advance();
            let expr = self.parse_expression()?;
            return Some(Statement::Return(expr));
        }

        let expr = self.parse_expression()?;
        Some(Statement::Expression(expr))
    }

    pub fn parse(&mut self) -> Vec<Statement> {
        let mut statements = Vec::new();

        while self.position < self.tokens.len() {
            if let Some(statement) = self.parse_statement() {
                statements.push(statement);
            }
        }

        statements
    }
}
