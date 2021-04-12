#
# Copyright (C) 2016 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Common global variables and helper methods for the in-memory python script.
# The script starts with this file and is followed by the code generated form
# the templated snippets. Those define all the helper functions used below.

import sys, re
from io import StringIO

out = StringIO()  # File-like in-memory buffer.
handler_size_bytes = "MTERP_HANDLER_SIZE"
handler_size_bits = "MTERP_HANDLER_SIZE_LOG2"
opcode = ""
opnum = ""

def write_line(line):
  out.write(line + "\n")

def balign():
  write_line("    .balign {}".format(handler_size_bytes))

def write_opcode(num, name, write_method):
  global opnum, opcode
  opnum, opcode = str(num), name
  write_line("/* ------------------------------ */")
  balign()
  write_line(".L_{1}: /* {0:#04x} */".format(num, name))
  opcode_start()
  opcode_pre()
  write_method()
  opcode_end()
  write_line("")
  opnum, opcode = None, None

generated_helpers = {}

# This method generates a helper using the provided writer method.
# The output is temporarily redirected to in-memory buffer.
def add_helper(write_helper, name = None):
  if name == None:
    name = "mterp_" + opcode + "_helper"
  global out
  old_out = out
  out = StringIO()
  helper_start(name)
  write_helper()
  helper_end(name)
  out.seek(0)
  generated_helpers[name] = out.read()
  out = old_out
  return name

def generate(output_filename):
  out.seek(0)
  out.truncate()
  write_line("/* DO NOT EDIT: This file was generated by gen-mterp.py. */")
  header()
  entry()

  instruction_start()
  opcodes()
  balign()
  instruction_end()

  for name, helper in sorted(generated_helpers.items()):
    out.write(helper)
  helpers()

  footer()

  out.seek(0)
  # Squash consequtive empty lines.
  text = re.sub(r"(\n\n)(\n)+", r"\1", out.read())
  with open(output_filename, 'w') as output_file:
    output_file.write(text)

