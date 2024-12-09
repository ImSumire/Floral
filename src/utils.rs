use std::fs;

pub fn file_size(path: &str) -> u64 {
    match fs::metadata(path) {
        Ok(metadata) => metadata.len(),
        Err(e) => {
            eprintln!("Error reading file size: {}", e);
            return 0;
        }
    }
}

pub fn estimate_size(path: &str) -> usize {
    const AVG_TOKEN_SIZE: f64 = 4.5;
    
    let file_size = file_size(path) as f64;
    (file_size / AVG_TOKEN_SIZE).round() as usize
}
