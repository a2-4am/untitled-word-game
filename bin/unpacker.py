#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2022 Adam Whiteside

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Forked from https://github.com/adamcw/wordle-trie-packing/blob/main/lesson7/lesson7.py
# and adapted by 4am for use within Untitled Word Game.
# Changes are copyright (c) 2022 4am
# and licensed under the same MIT license as the original, which is reproduced above.
#
# usage:
# $ ./unpacker.py wordlist.bin
#
# will print entire word list, one word per line

from bitstring import BitArray
import collections
import itertools
import sys

class Tree:
  def __init__(self, left=None, right=None):
    self.left = left
    self.right = right

def construct_frequency_tree(freqs):
  nodes = freqs
  while len(nodes) > 1:
    key1, val1 = nodes[-1]
    key2, val2 = nodes[-2]
    node = Tree(key1, key2)
    nodes = nodes[:-2]
    nodes.append((node, val1 + val2))
    nodes = sorted(nodes, key=lambda x: x[1], reverse=True)
  return nodes

def generate_huffman_code(node, binary, is_left_node=True):
  if isinstance(node, str) or isinstance(node, int):
    return {node: binary}
  d = {}
  d.update(generate_huffman_code(node.left, binary + [0], True))
  d.update(generate_huffman_code(node.right, binary + [1], False))
  return d

def count_frequencies(string):
  freq = collections.defaultdict(int)
  for char in string:
    freq[char] += 1
  return sorted(freq.items(), key=lambda x: x[1], reverse=True)

def max_len_table(tables):
  return max([len(huff) for huff in tables])

def bits_needed_to_represent(num):
  mask = 0b1 << 32
  for i in range(32):
    if (((num & mask) >> 31 - i)):
      return 32 - i + 1;
    mask >>= 1
  return 0

def leaves_at_depth(trie, target_level, level=0):
  if level == target_level:
    return trie.keys()
  keys = []
  for v in trie.values():
    keys += leaves_at_depth(v, target_level, level+1)
  return keys

def count_children_trie(trie, children):
  children.append(len(trie.keys()))
  for k, v in trie.items():
    count_children_trie(v, children)

def max_children_trie(trie):
  max_len = 0
  for k, v in trie.items():
    v_len = len(v.keys())
    max_len = max(max_len, v_len)
    max_len = max(max_len, max_children_trie(v))
  return max_len

def convert_trie_to_bits(trie, bit_trie, tables, depth=0, smart=False):
  for k, v in trie.items():
    if not smart or v.keys():
      bit_trie.append(tables[-1][len(v.keys())])
    bit_trie.append(tables[depth][k])
    convert_trie_to_bits(v, bit_trie, tables, depth+1, smart=smart)

class BitStream:
  def __init__(self, bit_array, char_map=None):
    self.bits = bit_array
    self.bin = self.bits.bin
    self.i = 0
    self.char_map = char_map

  def write(self, key, num_bits):
    bits = []
    val = self.char_map[key] if isinstance(key, str) else key
    mask = 0b1 << num_bits - 1
    for i in range(1, num_bits + 1):
      bits.append((val & mask) >> num_bits - i)
      mask >>= 1
    self.bits.append(bits)

  def append(self, data):
    self.bits.append(data)

  def read(self, num_bits):
    bits = self.bin[self.i:self.i+num_bits]
    self.i += num_bits
    return bits

  def read_int(self, num_bits):
    return int(self.read(num_bits), 2)

  def read_varint(self, table):
    buf = ''
    i = 0
    while True:
      buf += str(self.read(1))
      if buf in table.keys():
        return table[buf]
      i += 1

  def __len__(self):
    return len(self.bits)

def read_payload_trie(bits, symbols, tables, depth=0, prefix=''):
  num_children = 0
  if depth < len(tables) - 2:
    num_children = bits.read_varint(tables[-1])
  symbol = bits.read_varint(tables[depth])
  char = symbols[symbol]
  if depth == len(tables) - 2:
    return [prefix + char]
  words = []
  for i in range(num_children):
    words += read_payload_trie(bits, symbols, tables, depth+1, prefix + char)
  return words

def decode(bits, symbols):
  bits = BitStream(bits)
  # Header.
  table_size = bits.read_int(8)
  word_size = bits.read_int(8)
  num_tables = bits.read_int(8)
  num_symbols = bits.read_int(16)

  tables = []
  for i, table_id in enumerate(range(num_tables)):
    num_items = bits.read_int(table_size)
    table = {}
    for j in range(num_items):
      char = bits.read_int(word_size)
      encoding_size = bits.read_int(8)
      encoding = bits.read(encoding_size)
      table[encoding] = char
    tables.append(table)

  words = []
  for alpha in range(num_symbols):
    words += read_payload_trie(bits, symbols, tables)
  return words

if __name__ == "__main__":
  infile = sys.argv[1]

  INT_MAP = dict(zip(
    list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    range(26)
  ))

  with open(infile, 'rb') as fp:
    bits = BitStream(BitArray(fp), char_map=INT_MAP)
  words = decode(bits.bits, list(INT_MAP.keys()))
  print("\n".join(words))
