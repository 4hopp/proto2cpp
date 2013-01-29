##
# Doxygen filter for Google Protocol Buffers .proto files.
# This script converts .proto files into C++ style ones
# and prints the output to standard output.
#
# version 0.3
#
# How to enable this filter in Doxygen:
#   1. Generate Doxygen configuration file with command 'doxygen -g <filename>'
#        e.g.  doxygen -g doxyfile
#   2. In the Doxygen configuration file, find FILE_PATTERNS and add *.proto
#        FILE_PATTERNS          = *.proto
#   3. In the Doxygen configuration file, find INPUT_FILTER and add this script
#        INPUT_FILTER           = "python proto2cpp.py"
#   4. Run Doxygen with the modified configuration
#        doxygen doxyfile
#
#
# Copyright (C) 2012-2013 Timo Marjoniemi
# All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
##

import os
import sys
import re
import fnmatch


## Parser function.
# 
# The function takes a .proto file as input parameter
# and modifies the contents into C++ style.
# The modified data is printed into standard output.
# 
# @param inputFile Input file object
def parseFile(inputFile):
  # Go through the input file line by line.
  enum = False # This tells if enum is detected.
  for line in inputFile:
    # Search for comment ("//") and add one more "/" to it to enable Doxygen documentation.
    matchComment = re.search("//", line)
    if matchComment is not None:
      line = line[:matchComment.start()] + "///" + line[matchComment.end():]
    # Search for "enum" and if one is found before comment,
    # start changing all semicolons (";") to commas.
    matchEnum = re.search("enum", line)
    if matchEnum is not None and (matchComment is None or matchEnum.start() < matchComment.start()):
      enum = True
    # Search for semicolon (";") and if one is found before comment,
    # add the comment to previous line.
    matchSemicolon = re.search(";", line)
    if matchSemicolon is not None and (matchComment is not None and matchSemicolon.start() < matchComment.start()):
      # Split the line and write the comment first, then newline and code line last.
      lines = line.split(";")
      line = lines[1] + "\n" + lines[0] + ";\n"
    # Search again for semicolon if we have detected an enum, and replace semicolon with comma.
    if enum is True and re.search(";", line) is not None:
      matchSemicolon = re.search(";", line)
      line = line[:matchSemicolon.start()] + "," + line[matchSemicolon.end():]
    # Search for a closing brace.
    matchClosingBrace = re.search("}", line)
    if enum is True and matchClosingBrace is not None:
      # enum ends
      enum = False
    elif enum is False and re.search("}", line) is not None:
      # Message (to be struct) ends => add semicolon so that Doxygen will
      # handle it correctly.
      line = line[:matchClosingBrace.start()] + "};" + line[matchClosingBrace.end():]
    # Search for 'message' and replace it with 'struct' unless 'message' is behind a comment.
    matchMsg = re.search("message", line)
    if matchMsg is not None and (matchComment is None or matchMsg.start() < matchComment.start()):
      print("struct" + line[:matchMsg.start()] + line[matchMsg.end():])
    else:
      print(line)

# Find *.proto from current folder.
for filename in os.listdir('.'):
  if fnmatch.fnmatch(filename, '*.proto'):
    # For command-line debugging:
    #print filename

    # Open the file. Use try to detect whether or not we have an actual file.
    try:
      with open(filename, 'r') as inputFile:
        # Parse the file.
        parseFile(inputFile)
        pass
    except IOError as e:
      print 'the file ' + filename + ' does not exist'

# end of file

