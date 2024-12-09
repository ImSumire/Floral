use std::fs;
use std::env;
/* use std::time::Instant; */

mod utils;

mod lexer;
use lexer::lexer::Lexer;

mod parser;
use parser::parser::Parser;

fn main() {
    let args: Vec<String> = env::args().collect();

    // Ensure we have a filename argument
    if args.len() < 2 {
        eprintln!("Usage: {} [path]", args[0]);
        return;
    }

    let path = &args[1];

    /* // Time stats
    let start_time = Instant::now(); */

    // Read the content of the file
    let source = match fs::read_to_string(path) {
        Ok(content) => content,
        Err(e) => {
            eprintln!("Error reading file {path}: {e}");
            return;
        }
    };

    // Create a lexer and tokenize the content
    let mut lexer = Lexer::new(source.clone());
    #[allow(unused_variables)]
    let tokens = lexer.tokensize(path);

    /* // Time stats
    let duration = start_time.elapsed().as_secs_f64();
    let count = tokens.len();
    let avg = if count != 0 {
        duration / count as f64
    } else { 0.0 };  // in seconds
    println!("\x1b[30mToken scanned:\x1b[0m {count}");
    println!("\x1b[30mTotal time taken:\x1b[0m {duration:.4}\x1b[30ms\x1b[0m");
    println!("\x1b[30mAverage time per token:\x1b[0m {:.6}\x1b[30mms\x1b[0m", avg * 1000.0); */

    // Print the tokens
    lexer.pprint(&tokens);

    let mut parser = Parser::new(source.clone(), tokens);
    let ast = parser.parse();
    println!("{ast:#?}");
}
