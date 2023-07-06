---
layout: post
title: "Rust Cheat Sheet"
---

## Links

- [cheats.rs](https://cheats.rs/)
- [github: donbright/rust-lang-cheat-sheet](https://github.com/donbright/rust-lang-cheat-sheet)

## Cargo

Create new project:

```bash
cargo new project_name --bin
```

Format code:

```bash
cargo fmt
```

Environment variables:

- `RUSTFLAGS=-Awarnings cargo ...` - disable all warnings when running/building

## Declaration

- global constants:

```rust
const SOME_VALUE: i32 = 42;
```

- Custom operators on structs:

```rust
use std::ops::Add;
impl Add for Vec2 {
   type Output = Vec2;
   fn add(self, rhs: Self) -> Self::Output {
       Vec2 {
           x: self.x + rhs.x,
           y: self.y + rhs.y,
       }
   }
}
```

### enums

```rust
// for C-like enums it is beneficial to derive all the following properties
#[derive(PartialEq, Clone, Copy, Debug)]
enum GlyphType {
   Ineteger = 0,
   Command = 1,
   Variable = 2,
}

// to omit namespace when using constants
use GlyphType::*;
```

## Data Structures

### Vec

```rust
a = vec![0; n]; // create vector of size n with default values to 0
```

- join vector of String-s

```rust
a = vec!["Hello", "World!"];
a.join(", ");
```

- retain: to filter vector

```rust
let mut vec = vec![1, 2, 3, 4];
vec.retain(|&x| x % 2 == 0);
assert_eq!(vec, [2, 4]);
```

- [Sorting floats](https://rust-lang-nursery.github.io/rust-cookbook/algorithms/sorting.html)

```rust
//floats
let mut vec = vec![1.1, 1.15, 5.5, 1.123, 2.0];
vec.sort_by(|a, b| a.partial_cmp(b).unwrap());
```

### HashMap

```rust
use std::collections::HashMap;

let foo = HashMap::new();
foo.insert(key, value);

if (foo.contains_key(&key)) {
   println!("{}", f[&key]);
}

// iteration
for (k, v) in foo.iter() {
   println!("key = {}, value = {}", key, value);
}
```

- Update elements

```rust
*foo.entry(key).or_insert(default_value) += 1;
```

### String

- repeat string

```rust
let repeated = "Repeat".repeat(4);
```

### VecDeque

Implemenation of queue

```rust
use std::collections::VecDeque;

let mut q = VecDeque::new()

q.push_back(1);
q.push_front(2);

q.pop_back(); // -> Some(1)
q.pop_front(); // -> Some(2)
```

## Print

- Print the value of x:

```rust
println!("This is x={}", x);
```

- Print `Debug` output of the variable x:

```rust
println!("This is debug x={:?}", x);
```

- Print float with n decimal digits:

```rust
println!("This is float: {:.n}", x);
```

- Print without new lines:

```rust
use std::io::{self};

print!(" ");
io::stdout().flush().unwrap(); // flush output
```

- Print to stderr:

```rust
eprintln!("Debug message...");
```

## Measuring execution time

```rust
use std::time::Instant;

let now = Instant::now();
let elapsed_ms = now.elapsed().as_millis();
```

## Testing

- Writing tests:

```rust
#[cfg(test)]
mod tests {
   use super::*;
   #[test]
   fn test_foo() {
      let foo = 2 * 2;
      assert_eq!(foo, 4);
   }
}
```

- Run all tests: `cargo test`
- Running specific test: `cargo test <test_name>`
- Show output from passing tests: `cargo test -- --nocapture`
- Show output from passing tests and run specific test: `cargo test <test_name> -- --nocapture`
- Run tests in release mode: `cargo test --release`

## Files

- Read from file by lines:

```rust
pub fn read_input(filename: &str) -> Vec<String> {
    let file = File::open(filename).unwrap();
    let reader = BufReader::new(file);
    let mut res = Vec::new();
    for line in reader.lines() {
        let line = line.unwrap();
        res.push(line.to_string());
    }
    return res;
}
```

- Read the whole file to `String` ([link](https://doc.rust-lang.org/std/fs/fn.read_to_string.html)):

```rust
use std::fs;

fs::read_to_string("foo.txt") // returns Result<String>
```

## Commandline

Reading commandline args:

```rust
let args = std::env::args().collect::<Vec<String>>();
println!("args: {:?}", args);
```
