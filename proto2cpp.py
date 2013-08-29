##
# Doxygen filter for Google Protocol Buffers .proto files.
# This script converts .proto files into C++ style ones
# and prints the output to standard output.
#
# version 0.4-beta
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
import inspect

## Class for converting Google Protocol Buffers .proto files into C++ style output to enable Doxygen usage.
## 
## The C++ style output is printed into standard output.<br />
## There are three different logging levels for the class:
## <ul><li>#logNone: do not log anything</li>
## <li>#logErrors: log errors only</li>
## <li>#logAll: log everything</li></ul>
## Logging level is determined by \c #logLevel.<br />
## Error logs are written to file determined by \c #errorLogFile.<br />
## Debug logs are written to file determined by \c #logFile.
#
class proto2cpp:

  ## Logging level: do not log anything.
  logNone   = 0
  ## Logging level: log errors only.
  logErrors = 1
  ## Logging level: log everything.
  logAll    = 2

  ## Constructor
  #
  def __init__(self):
    ## Debug log file name.
    self.logFile = "proto2cpp.log"
    ## Error log file name.
    self.errorLogFile = "proto2cpp.error.log"
    ## Logging level.
    self.logLevel = self.logNone

  ## Handles a file.
  ##
  ## If @p fileName has .proto suffix, it is processed through parseFile().
  ## Otherwise it is printed to stdout as is except for file \c proto2cpp.py without
  ## path since it's the script given to python for processing.
  ##
  ## @param fileName Name of the file to be handled.
  #
  def handleFile(self, fileName):
    if fnmatch.fnmatch(filename, '*.proto'):
      self.log('\nXXXXXXXXXX\nXX ' + filename + '\nXXXXXXXXXX\n\n')
      # Open the file. Use try to detect whether or not we have an actual file.
      try:
        with open(filename, 'r') as inputFile:
          self.parseFile(inputFile)
        pass
      except IOError as e:
        self.logError('the file ' + filename + ' could not be opened for reading')

    elif not fnmatch.fnmatch(filename, os.path.basename(inspect.getfile(inspect.currentframe()))):
      self.log('\nXXXXXXXXXX\nXX ' + filename + '\nXXXXXXXXXX\n\n')
      try:
        with open(filename, 'r') as theFile:
          for theLine in theFile:
            print(theLine)
            self.log(theLine)
        pass
      except IOError as e:
        self.logError('the file ' + filename + ' could not be opened for reading')
    else:
      self.log('\nXXXXXXXXXX\nXX ' + filename + ' --skipped--\nXXXXXXXXXX\n\n')

  ## Parser function.
  ## 
  ## The function takes a .proto file object as input
  ## parameter and modifies the contents into C++ style.
  ## The modified data is printed into standard output.
  ## 
  ## @param inputFile Input file object
  #
  def parseFile(self, inputFile):
    # Go through the input file line by line.
    isEnum = False
    for line in inputFile:
      # Search for comment ("//") and add one more "/" to it to enable Doxygen documentation.
      matchComment = re.search("//", line)
      if matchComment is not None:
        line = line[:matchComment.start()] + "///" + line[matchComment.end():]
      # Search for "enum" and if one is found before comment,
      # start changing all semicolons (";") to commas.
      matchEnum = re.search("enum", line)
      if matchEnum is not None and (matchComment is None or matchEnum.start() < matchComment.start()):
        isEnum = True
      # Search for semicolon (";") and if one is found before comment,
      # move the comment to previous line.
      matchSemicolon = re.search(";", line)
      if matchSemicolon is not None and (matchComment is not None and matchSemicolon.start() < matchComment.start()):
        # Split the line and write the comment first, then newline and code line last.
        lines = line.split(";")
        line = lines[1] + "\n" + lines[0] + ";\n"
      # Search again for semicolon if we have detected an enum, and replace semicolon with comma.
      if isEnum is True and re.search(";", line) is not None:
        matchSemicolon = re.search(";", line)
        line = line[:matchSemicolon.start()] + "," + line[matchSemicolon.end():]
      # Search for a closing brace.
      matchClosingBrace = re.search("}", line)
      if isEnum is True and matchClosingBrace is not None:
        isEnum = False
      elif isEnum is False and re.search("}", line) is not None:
        # Message (to be struct) ends => add semicolon so that it'll
        # be a proper C(++) struct and Doxygen will handle it correctly.
        line = line[:matchClosingBrace.start()] + "};" + line[matchClosingBrace.end():]
      # Search for 'message' and replace it with 'struct' unless 'message' is behind a comment.
      matchMsg = re.search("message", line)
      if matchMsg is not None and (matchComment is None or matchMsg.start() < matchComment.start()):
        output = "struct" + line[:matchMsg.start()] + line[matchMsg.end():]
        print(output)
        self.log(output)
      else:
        print(line)
        self.log(line)

  ## Writes @p string to log file.
  ##
  ## #logLevel must be #logAll or otherwise the logging is skipped.
  ##
  ## @param string String to be written to log file.
  #
  def log(self, string):
    if self.logLevel >= self.logAll:
      with open(self.logFile, 'a') as theFile:
        theFile.write(string)

  ## Writes @p string to error log file.
  ##
  ## #logLevel must be #logError or #logAll or otherwise the logging is skipped.
  ##
  ## @param string String to be written to error log file.
  #
  def logError(self, string):
    if self.logLevel >= self.logError:
      with open(self.errorLogFile, 'a') as theFile:
        theFile.write(string)


converter = proto2cpp()
# Doxygen will give us the file names
for filename in sys.argv:
  converter.handleFile(filename)

# end of file
