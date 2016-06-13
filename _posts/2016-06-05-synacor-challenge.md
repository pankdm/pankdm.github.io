---
layout: post
title:  "Synacor Challenge"
---

I recently came across this awesome programming challenge at
[https://challenge.synacor.com/](https://challenge.synacor.com/)
and enjoyed solving it a lot. Highly recommending this to everyone who likes puzzles,
virtual machines, reverse engineering and textual quests.

This note shares details of my approach as well as some interesting
tricks I learned while solving it.

**WARNING!**
There will be a lot of spoilers along the way so if you want
to enjoy solving it on you own, stop here!


## Task description

When you download `synacor-challenge.tgz` -- input for the challenge,
you'll find only two files inside.
One file is a [`arch-spec`](https://github.com/pankdm/synacor-challenge/blob/master/data/arch-spec)
that contains short description and specification for some virtual machine.

```
== Synacor Challenge ==
In this challenge, your job is to use this architecture spec to create a
virtual machine capable of running the included binary.  Along the way,
you will find codes; submit these to the challenge website to track
your progress.  Good luck!

...
```

The other one is `challenge.bin` that is the actual bytecode for that virtual machine.


## VM implementation

Virtual machine was pretty straight forward to implement (see [`vm2.py`](https://github.com/pankdm/synacor-challenge/blob/master/vm2.py)):

* Use array of size 8 for registers
* Use array of size 32768 for memory
* Variable `index` for current position program execution
* Fill memory with given program
* Have giant `if` block to update internal state

VM bytecode performs self-check which helps to identify common issues.
Once this self-check finished successfully, you get the next code.

```
Executing self-test...

self-test complete, all tests pass
The self-test completion code is: GNIbaFAvOpUX
```

I implemented vm specification and got into quest prompt.

```
== Foothills ==
You find yourself standing at the base of an enormous mountain.  
At its base to the north, there is a massive doorway.  
A sign nearby reads "Keep out!  Definitely no treasure within!"

Things of interest here:
- tablet

There are 2 exits:
- doorway
- south

What do you do?
>:
```

Whatever I was entering to stdin didn't work: the program just was stuck.

After some debugging I realized that `raw_input()` was stripping trailing `'\n'`,
so I had to add it manually:

```python
input = raw_input('>:')
self.buffer += input + '\n'
```

Okay, now as this bug was fixed, I was able to explore locations.
If you type any unknown command, you'll get advice to use `help`
and the `help` command gives you the full list of available options.

```
>:help

look
  You may merely 'look' to examine the room, or you may 'look <subject>'
  (such as 'look chair') to examine something specific.
go
  You may 'go <exit>' to travel in that direction (such as 'go west'),
  or you may merely '<exit>' (such as 'west').
inv
  To see the contents of your inventory, merely 'inv'.
take
  You may 'take <item>' (such as 'take large rock').
drop
  To drop something in your inventory, you may 'drop <item>'.
use
  You may activate or otherwise apply an item with 'use <item>'.
```


Taking tablet and using it produces the code [4/8].

```
You find yourself writing "zHQkEJVhuWiv" on the tablet.  
Perhaps it's some kind of code?
```


I walked around and found couple of other things:

- `empty lantern` in another location
- maze with all rooms exactly the same
 - (spoiler: actually they are not the same, but I didn't noticed that)
- darkness where monsters eat you when trying to pass it


## Reverse engineering

Having exhausted all ideas what to do next, I started reverse engineering
the vm bytecode. And to do this you need some good tools: you cannot just read raw bytes.
Let's start with printing source code in human-readable format. My VM used hardcoded way of executing bytecode,
so I wrote more generic helpers to interpret the byte sequences.


Created ops specification list and `OpSpec` class that will be later used
to parse the input.

```python
SPEC = [
    ('halt', '0'),
    ('set', '1 a b'),
    ('push', '2 a'),
    ('pop', '3 a'),
    # ...
]

class OpSpec:
    def __init__(self, name=None, spec=None):
        if name is not None:
            self.name = name
            ss = spec.split(' ')
            self.opcode = int(ss[0])
            self.arity = len(ss) - 1
            self.args = ", ".join(ss[1:])

```

Looking inside disassembled code shows:

```python
    0| noop
    1| noop
    2| out "W"
    4| out "e"
    6| out "l"
    8| out "c"
   10| out "o"
   12| out "m"
   14| out "e"
```

This is obviously not very readable.
We can do better here and write some code to collapse multiple `out`-s into one statement:

```python
  530| set r0 0
  533| jt r0 1118
  536| add r0 1 1
  540| jt r0 564
  543| out "no add op\n"
```

Now we need some way to trace through the code to actually understand what it does.

## GDB implementation

I created new class `GDB` and started adding more methods that will help
with interactive debugging (see also
[`gdb.py`](https://github.com/pankdm/synacor-challenge/blob/master/gdb.py))

* `def execute_one_op(self)` -- execute one next command
* `def step(self, limit)` -- execute `limit` next commands
* `def disasm(self, offset, limit=14)` -- show the code starting from `offset`
* `def set_input(self, buffer)` -- write `buffer` to stdin of vm
* `def show_state(self)` -- prints current state of stack and registers


Nice thing about python is that it has REPL: interactive shell where you can
explore things. Also you can combine scripting and shell by running the script
with `-i` option:

```
ipython -i run.py
```

This will execute the script `run.py` but will stay in python shell with all
variables and functions from the global scope being available.

We can put in `run.py` init script and shortcuts for the common debugging commands.

```python
ops = load_bytecode()
vm = VM2(ops)
vm.index = 0

def p():
    vm.show_state()

def n():
    vm.execute_one_op()

def r():
    vm.run()
```



Another trick is to have method `x()`:

```python
def x():
    return reload(gdb).GDB(vm)
```

That will return instance of class `GDB` with the **latest** version of the code.
This allows adding more methods to this class and using them immediately without
re-running the whole script! To make this work all you need to do is to make
`GDB` stateless and keep all data fields in class `VM`.


Another thing that ended up being useful is to have a way to switch between
entering commands in the vm itself vs calling python functions in the shell.
I could be setting stdin of virtual machine, but sometimes it's more convenient to type
commands `take`, `go`, `inv`, etc in the vm directly.
The way it works is we create special exception type to control the flow of the program

```python
class Break(Exception):
    def __init__(self, value):
        self.value = value
```

Then there are 2 options

1. If flag `return_on_input` is set to `True` then we will return to python shell
whenever we try to read from stdin while inside vm.

2. If we entered `?` while inside vm we return back to python shell.

```python
def get_char(self):
    if self.return_on_input:
        # restore 2 read symbols
        self.index -= 2
        raise Break('>: returned while reading from stdin')

    input = raw_input('>:')
    if input == '?':
        # restore 2 read symbols
        self.index -= 2
        raise Break('>: returned back to shell')
    # ...
```

Now `GDB` feels like real gdb and allow pretty convenient inspecting and tracing
program logic. Let's use it to make some further progress.


## call 1458

The goal is to find the codes, so I started with investigation how the current codes are getting returned.
I found that the data is getting printed after `call 1458`.
First observation is that registers are used both as arguments to the functions
and scope variables.

Here is the complete code of `call 1458` with my notes.

```python
 1458| push r0   # save  registers to use them as locals
 1460| push r3
 1462| push r4
 1464| push r5
 1466| push r6
 1468| set r6 r0   # r6 = r0
 1471| set r5 r1   # r5 = r1
 1474| rmem r4 r0  # number of iterations is specified in first element of offset
 1477| set r1 0    # r1 = 0 # start loop with 0
 1480| add r3 1 r1  # start for loop
 1484| gt r0 r3 r4  #  condition to ext (r3 > r4)
 1488| jt r0 1507
 1491| add r3 r3 r6  # r6 used as starting offset (r0)
 1495| rmem r0 r3   # r3 used as i # r0 = s[i]
 1498| call r5      #
 1500| add r1 r1 1  # r1 - loop counter
 1504| jt r1 1480   # end for loop
 1507| pop r6       # restore registers
 1509| pop r5
 1511| pop r4
 1513| pop r3
 1515| pop r0
 1517| ret
```

Basically `call 1458` is a general for-loop over sequences and has 3 input parameters:

1. `r0` - memory offset to the sequence
  1. `mem[r0] = n` is length of the sequence
  2. `mem[r0 + 1], ..., mem[r0 + n]` - actual data
3. `r1` - address of the function to call on each element of sequence
4. `r2` - optional parameter that will be passed to that function

There are a few other functions that has a code `call 1458` in them:

1) `r1 = 1528`

```python
 1528| out (r0)
 1530| ret
```
This is equivalent to printing the string defined at `r0` offset.


2) `r1 = 1531`

```python
 1531| push r1
 1533| set r1 r2
 1536| call 2125
 1538| out (r0)
 1540| pop r1
 1542| ret
```

```python
 2125| push r1
 2127| push r2
 2129| and r2 r0 r1
 2133| not r2 r2
 2136| or r0 r0 r1
 2140| and r0 r0 r2
 2144| pop r2
 2146| pop r1
 2148| ret
```

This one is less obvious. It doesn't really matter what `call 2125` exactly does,
important part is that is modifies the value in `r0` using value from `r2`.
Let's call it `unhash(r0, r2)`. Thus in this case `call_1458(r0, 1531, r2)` will
decode and print string from offset `r0` using `r2` as seed.


Now if re-implement `unhash` in python we can perform pattern matching and
programmatically annotate the code:

```python
 4393| set r0 26299
 4396| call 1518  // print "  The orb shatters!\n\n"
```

```python
 3012| set r0 27432
 3015| set r1 1531
 3018| add r2 10916 8261
 3022| call 1458  // print "You see no such item.\n"
```

A snippet of the code which adds more annotations:

```python
  if op.name == 'call':
      addr = m[offset + 1]
      if addr == 2125:
          data += '  //  unhash(r0, r1)'
      if addr == 1518:
          find_result = self.try_match_1518(offset)
          if find_result is not None:
              data += find_result.info
          else:
              data += '  // print_string( m[r0] )'
      if addr == 5814:
          data += '  // print_stirng("- m[r0] \\n") '
```


It revealed a number of interesting things in the byte code, but not the actual codes for the challenge.
The codes seemed to be encrypted using seed from some memory location. Without knowing the actual value
it's impossible to decode it. Very naive reverse engineering didn't work out.
Need to go back to the quest itself and see what options are there.

## Hacking items and locations

It seemed that you need some source of light to pass the darkness.
Empty lantern in one location implies that you can also find non-empty lantern somewhere.
Let's see if there is a way to hack vm to get all available items.
My first approach was to find the code that checks if the item is in your inventory
and hack it to always return true.
This is happening around line 5906:

```python
 5895| add r3 r0 2
 5899| rmem r3 r3
 5902| eq r3 r2 r3
 5906| jf r3 5918
 5909| add r0 r0 0
 5913| rmem r0 r0
 5916| call 5814  // print_stirng("- m[r0] \n")
```

I replaced this line with `noop` operation:

```python
vm.memory[5906] = 21
vm.memory[5907] = 21
vm.memory[5908] = 21
```

and it worked! Now by running `inv` command I was able to see all items in my inventory.

```
>:inv

Your inventory:
- tablet
- empty lantern
- lantern
- lit lantern
- can
- red coin
- corroded coin
- shiny coin
- concave coin
- blue coin
- teleporter
- business card
- strange book
- journal
- orb
- mirror

What do you do?
```

Unfortunately, this was all phantom items. They only appeared in inventory but cannot
be used.

Another idea was to debug where the check for `lit lantern` is happening while
passing the darkness and patch it instead. It ended up being difficult so I gave up
this idea and started looking how actually having an item in inventory is stored
in memory.

Soon I found that information about items is placed starting from memory offset
2668 and occupies 4 memory cells. If cell 2 (0-based) contains 0 it means the item
is in inventory and can actually be used. Okay, we can now write simple method to
`GDB` that will give all items.

```python
def get_all_items(self):
    pos = 2668
    while pos <= 2728:
        self.vm.memory[pos + 2] = 0
        pos += 4
```

This granted access to darkness and soon the next location was closed door
where you can be inserting coins. We have only 5 coins so total number of combinations
is `5! = 120` which makes it pretty easy to write a brute force algorithm that
will try inserting coins in all possible permutations (python even has a handy
method `itertools.permutations` for that).

```python
def try_coins(self):
    coins = [
        'red coin',
        'corroded coin',
        'shiny coin',
        'concave coin',
        'blue coin',
    ]
    for cc in permutations(coins):
        self.get_all_items()
        seq = ''
        for c in cc:
            seq += 'use ' + c + '\n'
        self.vm.set_input(seq)
        self.vm.run()
```

Later I realized that the door had a sign:

```
There is a strange monument in the center of the hall with circular slots
and unusual symbols.  It reads:

_ + _ * _^2 + _^3 - _ = 399
```

and the coins have actual numbers on them. So you were supposed to brute force
the equation. Ah, whatever, my approach also worked :)

When the door was opened it produced the code. But it didn't work on the website.
I suspected this was because I bypassed some checks and hacked the game to grant
all items.

Let's actually try to pass the darkness in a more fair way.

After more reverse engineering I figured out more details what the memory
at different offset of the item means:

* Stored in memory offsets `[2668 : 2731]`
* `item + 0` - name of the item
* `item + 1` - description of item (`look X`)
* `item + 2` - current location of item
* `item + 3` - address of function to call used (`use X`)

Memory layout for locations could be decoded using similar techniques:

* Stored in memory offsets `[2317 : 2461] + [2463 : 2667]`
* `loc + 0` - name of location
* `loc + 1` - description of location
* `loc + 2` - list of names of the exits
* `loc + 3` - list of memory offsets of the exits
* `loc + 4` - address of function to call when entering

There are multiple locations with the same name: `Twisty passages` which makes
it hard to distinguish them. I did a trick to modify the memory where the location
name is stored by overwriting it with incremental counters.


```python
def mark_locations(self):
    counter = 0
    ranges = \
        range(2317, 2460, 5) + \
        range(2463, 2658, 5)

    for i in ranges:
        self.mark_location(i, counter)
        counter += 1

def mark_location(self, offset, counter):
    addr = self.vm.memory[offset]
    s = str(counter)
    if len(s) < 2:
        s = '0' + s
    self.vm.memory[addr + 1] = ord(s[0])
    self.vm.memory[addr + 2] = ord(s[1])
    self.vm.memory[addr + 3] = ord('_')
```

As usual I added this annotations to `disasm` method.
Now we can see where is the `can`.

```python
 2684| unknown (18568) //  desc: "can"
 2685| unknown (18572) //  desc: "This can is full of high-quality lantern oil."
 2686| unknown (2417) // loc: "20_sty passages"
 2687| unknown (4799)
```

```python
 2382| unknown (8332)  //  __________ "13_sty passages"
 2383| unknown (8348)  // "You are in a twisty maze of little passages, all alike."
 2384| unknown (26983)  // num exits 3: "north", "south", "west"
 2385| unknown (26987)  // loc 3: "14_sty passages", "12_sty passages", "13_sty passages"
 2386| unknown (3746)
```


## Finding the rest of the codes

Walking in a maze where you have unique integers assigned to each room became so
much easier. Then it was pretty straight froward process to get 2 more codes.

* find the `can` in the maze (another code obtained! [5/8])
* `use can` + `empty lantern` gives `lantern`
* `use lantern` gives `lit lantern`
* carry `lit lantern` and go through darkness
* gather coins in nearby rooms
* apply the right sequence of coins found by brute force before
* find and use `teleporter` (more codes! [6/8])

There you find a book that explains how teleporter works
(see [`teleport_book.txt`](https://github.com/pankdm/synacor-challenge/blob/master/txt/teleport_book.txt)
):

```
Then, set the eighth register to this value, activate the teleporter, and
bypass the confirmation mechanism.  If the eighth register is set correctly, no
anomalies should be experienced, but beware - if it is set incorrectly, the
now-bypassed confirmation mechanism will not protect you!
```

Basically, you need to understand what the confirmation algorithm does and find
the value it expects. Here is the byte code for it with my notes:

```python
 6027| jt r0 6035  # if A == 0
 6030| add r0 r1 1 # r0 = r1 + 1
 6034| ret
 6035| jt r1 6048 # if B == 0
 6038| add r0 r0 32767 # r0 = r0 - 1
 6042| set r1 r7 # r1 = r7
 6045| call 6027
 6047| ret
 6048| push r0
 6050| add r1 r1 32767 # r1 = r1 - 1
 6054| call 6027
 6056| set r1 r0 # r1 = r0
 6059| pop r0
 6061| add r0 r0 32767 # r0 = r0 - 1
 6065| call 6027
 6067| ret
```

After reading this code carefully it could be seen that function `call 6027`
takes 3 parameters: `r0`, `r1`, `r7` and changes the values of registers `r0` and `r1`.
In the output `r0` and `r1` are always satisfy the equation: `r0 = r1 + 1`.
Let's put `r7 = C` and assume that `call 6027` is a function `f(A, B)` that returns the value
of `r0` (using `r0 = r1 + 1` we can always compute `r1`). Then the algorithm looks as following:

1. If `A == 0` then `f(0, B) = B + 1`
2. If `A > 0` then
  1. If `B == 0` then `f(A, 0) = f(A - 1, C)`
  2. If `B > 0` then `f(A, B) = f(A - 1, f(A, B - 1))`

Now let's see what are the values of `r0` and `r1` when we `call 6027`.

```python
 5483| set r0 4
 5486| set r1 1
 5489| call 6027
 5491| eq r1 r0 6
 5495| jf r1 5579
 5498| push r0
 5500| push r1
 5502| push r2
 5504| set r0 29014
 5507| set r1 1531
 5510| add r2 19357 709
 5514| call 1458  // print "You wake up on a sandy beach ..."
```

In order not to jump to 5579 the value of `r7` needs to satisfy condition
`f(4, 1, r7) == 6`. Trying to compute this directly appeared to be really slow.
We need to go with smarter approach. Denoting `r7 = C`, by induction we can prove the following
equations:

* `f(0, B) = B + 1`
* `f(1, B) = B + C + 1`
* `f(2, B) = B (C + 1) + 2C + 1`
* `f(3, B) = f(3, B - 1) (C + 1) + 2C + 1`

Then we get `f(4, 1) = f(3, f(4, 0)) = f(3, f(3, C))`. For each value of `C`
from 1 to 32768 we can calculate `f(3, B)` for each `B` using dynamic programming,
then check if `f(3, f(3, C))` equal to 6. When
[written in C++](https://github.com/pankdm/synacor-challenge/blob/master/teleport.cpp)
works vey fast.

Apparently, this function `f` is also known as
[Ackerman Function](https://en.wikipedia.org/wiki/Ackermann_function):

>Its value grows rapidly, even for small inputs.
For example, `f(4,2)` is an integer of 19,729 decimal digits.

Setting the right value to `r7` and using teleport gives the next code [7/8].
It also teleports to some new location. Here I found a set of connected rooms, each
having either number or operation symbol: `"+"`, `"-"`, `"*"`.

```
== 52_lt Door ==
You stand before the door to the vault; it has a large '30' carved into it.  
Affixed to the wall near the door, there is a running hourglass which
never seems to run out of sand.

The floor of this room is a large mosaic depicting the number '1'.
```

The goal is to find the shortest path from start to finish that produces
the desired value 30. This is pretty problem that could be solved by checking all
possible routes in the order of increasing length (BFS works fine).
See [`vault_solver.py`](https://github.com/pankdm/synacor-challenge/blob/master/vault_solver.py)
for complete solution.
The only trick here was to programmatically construct the graph of rooms.
But we already know the memory layout of the vm and know how information about rooms
is stored. For extracting the actual symbols, regular expressions are the best fit here:

```python
def symbol_impl(self):
    re1 = "the number '(.*?)'"
    re2 = "depicting a '(.*)' symbol"
    m1 = re.search(re1, self.desc)
    m2 = re.search(re2, self.desc)
    if m1 is not None:
        return m1.group(1)
    elif m2 is not None:
        return m2.group(1)
    else:
        return None
```

This gives the last code [8/8] and the challenge is finished:

```
Congratulations; you have reached the end of the challenge!
```
