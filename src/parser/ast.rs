#[derive(Debug, PartialEq)]
pub enum Expr {
    Identifier(String),
    Literal(Literal),
    BinaryOp {
        left: Box<Expr>,
        operator: String,
        right: Box<Expr>
    },
    FunctionCall {
        name: String,
        args: Vec<Expr>
    },
    Scope {
        body: Vec<Statement>
    }
}

#[derive(Debug, PartialEq)]
pub enum Literal {
    Int(i64),
    Float(f64),
    String(String),
    Char(char),
}

#[derive(Debug, PartialEq)]
pub struct Param {
    pub name: String,
    pub r#type: String,
}

#[derive(Debug, PartialEq)]
pub enum Statement {
    Let {
        name: String,
        value: Expr
    },
    Function {
        name: String,
        r#type: String,
        parameters: Vec<Param>,
        body: Expr  // Expr::Scope
    },
    Expression(Expr),
    Return(Expr)
}
