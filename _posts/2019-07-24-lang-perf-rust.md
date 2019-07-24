---
layout: post
title:  "Language Performance (Part 2): Rust"
---

This is a follow-up to my previous note [Language Performance: C++ vs Python vs Kotlin](/lang-perf.html).
I recently started looking into Rust and wanted to confirm that it comparable to C++ in terms of
expected performance.


Indeed, porting the C++ program to Rust and running both of them 3 times for more statistical results
shows that Rust follows C++ very closely:


<img src="img/lang-perf-rust/rust-vs-cpp.png"/>
<img src="img/lang-perf-rust/rust-vs-cpp-2.png"/>
