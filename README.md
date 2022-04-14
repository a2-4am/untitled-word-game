Untitled Word Game is a Wordle clone for 8-bit Apple II computers. It runs on the "rev. 0" Apple II from 1977 (or any later model). It requires only 16KB of RAM. [Download the latest Untitled Word Game disk image](https://github.com/a2-4am/untitled-word-game/releases/tag/v1.0.1) (version **1.0.1**, released **2022-04-14**) or [play it online](https://archive.org/details/UntitledWordGame).

For ease of use on modern emulators, the game is distributed as a 16-sector floppy disk image. This is slightly ahistorical. Apple did not ship a floppy drive until 1978, and did not ship a 16-sector floppy drive until 1980. You'll be okay.

The game is fully playable and feature-complete. It randomly picks from a curated list of 2048 five-letter words and validates your guesses against a list of 9330 words. There is no "daily" play, just random puzzles as long as your Apple II can draw breath. It even plays a little tune when you win.

## Background

Since Wordle exploded in popularity in late 2021 / early 2022, there have been many variations ([Quordle](https://www.quordle.com/), [Octordle](https://octordle.com/)), innovative adjacent spin-offs ([Nerdle](https://nerdlegame.com/), [Worldle](https://worldle.teuteuf.fr/)), and ports to older space- and CPU-constrained devices ([Gameboy Fiver](https://alexanderpruss.blogspot.com/2022/02/game-boy-wordle-how-to-compress-12972.html)).

As you might expect, the primary challenge of a retrocomputing port of a word guessing game is the massive word list. Generalized text compression is a well-studied topic, but CPU-intensive decompression is usually required before access, and there's not enough space to decompress everything (or possibly anything). [Wordle Trie Packing](https://github.com/adamcw/wordle-trie-packing) is the best deep dive into the subject of creating compressed data structures specifically for Wordle-type lookups.

Untitled Word Game uses a [Huffman Coded Bitpacked Smart Trie](https://github.com/adamcw/wordle-trie-packing#lesson-7-continued-the-huffman-coded-bitpacked-smart-trie) to store the two word lists: the first of possible solutions, and the second of all valid words not in the first list. You can use [`unpacker.py`](https://github.com/a2-4am/untitled-word-game/blob/main/bin/unpacker.py) to extract the word lists from the [compressed versions](https://github.com/a2-4am/untitled-word-game/tree/main/res) and [`packer.py`](https://github.com/a2-4am/untitled-word-game/blob/main/bin/packer.py) to repack them.

We split 9330 five-letter words into two lists and encode them into two identical data structures, for a total of 13159 bytes. At runtime, we work directly with these compressed data structures; there's not enough space in memory to decompress them, or even portions of them. To make the game playable at 1 MHz, we have an additional 360 bytes of indexes by first letter. For instance, if your guess is ZEBRA, we can skip directly to the first Z word and only search through 60 words instead of thousands to determine if your guess is a valid word. Lookups are still O(N) within the space of "words that start with this letter," and for some letters that's still several hundred words, but there's a handsome little spinner you can watch while you wait.

[qkumba](https://github.com/peterferrie) wrote the 6502 assembly language routines to access these compressed data structures: [`nth`](https://github.com/a2-4am/untitled-word-game/blob/main/src/lookup.a#L60) to pick a solution word, and [`exists`](https://github.com/a2-4am/untitled-word-game/blob/main/src/lookup.a#L111) to validate your guesses. These routines require another 495 bytes.

If you don't know much about the Apple II, you might be thinking "16K=16384, minus 13159, minus 360, minus 495, still leaves you with 2370 bytes for code!" But the Apple II uses main memory for _everything_. The text screen is 1KB, starting at main memory address 0x400. Even the stack is in main memory (256 bytes, starting at address 0x100).

Then you realize that you forgot to budget for an operating system, or even a disk reading routine, and you have no way to get the game from the disk into memory in the first place.

So that's fun.

To load the game into memory, qkumba wrote a custom bootloader called [0boot](https://github.com/a2-4am/untitled-word-game/blob/main/src/0boot.a). It relocates itself into zero page (hence the name), squeezes its required data structures into the stack page and page 2, then reads the game into memory starting at address 0x300. Since the text page starts at address 0x0400, we end up reading an entire screenful of text directly from disk while loading; we used this for the initial help screen. Once the game starts, we clear the screen (partially, leaving the header and footer) and the help text is gone forever. We also no longer need the disk reading code, so we can reuse zero page, the stack page, and page 2.

The actual game code is in [`untitled.a`](https://github.com/a2-4am/untitled-word-game/blob/main/src/untitled.a), plus a few routines that we squeezed in and around 0boot. [`constants.a`](https://github.com/a2-4am/untitled-word-game/blob/main/src/constants.a) has a good summary of memory usage at various stages. It is all completely ridiculous. Thanks for reading.
