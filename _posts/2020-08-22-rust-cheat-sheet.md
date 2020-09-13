---
layout: post
title:  "Rust Cheat Sheet"
---

## Links

* [cheats.rs](https://cheats.rs/)
* [github: donbright/rust-lang-cheat-sheet](https://github.com/donbright/rust-lang-cheat-sheet)


## Declaration

 * global constants:

```rust
const SOME_VALUE: i32 = 42;
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

 * join vector of String-s

```rust
a = vec!["Hello", "World!"];
a.join(", ");
```

 * retain: to filter vector

```rust
let mut vec = vec![1, 2, 3, 4];
vec.retain(|&x| x % 2 == 0);
assert_eq!(vec, [2, 4]);
```

 * [Sorting Vectors](https://rust-lang-nursery.github.io/rust-cookbook/algorithms/sorting.html)

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
```

### String

 * repeat string

```
let repeated = "Repeat".repeat(4);
```

### VecDeque

Implmenentation of queue

```rust
use std::collections::VecDeque;

let mut q = VecDeque::new()

q.push_back(1);
q.push_front(2);

q.pop_back(); // -> Some(1)
q.pop_front(); // -> Some(2)
```


## Print

* Print the value of x:

```rust
println!("This is x={}", x);
```

* Print `Debug` output of the variable x:

```rust
println!("This is debug x={:?}", x);
```

* Print float with n decimal digits:

```rust
println!("This is float: {:.n}", x);

* Print without new lines:

```rust
use std::io::{self};

print!(" ");
io::stdout().flush().unwrap(); // flush output
```

* Print to stderr:

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

* Writing tests:

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

* Running specific test: `cargo test <test_name>`
* Show output from passing tests: `cargo test -- --nocapture`
