#!/usr/bin/python3

import os
import glob
import sys

if len(sys.argv) < 2:
    print('Usage: ./count_lines.py <vgc-root-dir>')
    exit()

# Each line in source files is classified into one of the following categories:
# 1. Blank (only contain whitespaces or tabs)
# 2. Legal (license boilerplate)
# 3. Comment (internal comment for maintainer)
# 4. Doc (documentation of public API, e.g., Doxygen comments)
# 5. Test (line of testing code - not executed in production)
# 6. Wrap (line of wrapping code - counted separately for stats)
# 7. Code (any other line of code)
#
# Note that if there are both code and comment on the same line, then
# the line is only counted as "Code". The sum of the counts for each
# category must be equal to the total number of lines in the file.

# Counters for lines in C++ files
cppBlank = 0
cppLegal = 0
cppComment = 0
cppDoc = 0
cppTest = 0
cppWrap = 0
cppCode = 0

# Counters for lines in Python files
pyBlank = 0
pyLegal = 0
pyComment = 0
pyDoc = 0
pyTest = 0
pyWrap = 0
pyCode = 0

# Counters for lines in CMake files
cmakeBlank = 0
cmakeLegal = 0
cmakeComment = 0
cmakeDoc = 0
cmakeTest = 0
cmakeWrap = 0
cmakeCode = 0

# Counters for lines in GLSL shader files
glslBlank = 0
glslLegal = 0
glslComment = 0
glslDoc = 0
glslTest = 0
glslWrap = 0
glslCode = 0

# Counters for lines in Qt stylesheet files
qssBlank = 0
qssLegal = 0
qssComment = 0
qssDoc = 0
qssTest = 0
qssWrap = 0
qssCode = 0

# The argument \p within tells whether we are starting this line within a C-Style
# comment, i.e., the characters "/*" were found in one of the previous lines
# with no matching "*/" found yet.
#
# Returns a pair (hasCode, within) where 'hasCode' tells you whether this line
# has semantic content outside of C-style comment lines, and where 'within'
# tells you whether this line ended within a C-style comment.
#
# Note: For simplicity, we assume that "/*" and "*/" are never within
#       character constants, string literals, or comments. This
#       means that the following [code] will be counted as comment:
#
#         std::string s1 = "/*";
#         [code]
#         std::string s2 = "*/";
#
#       This should be extremely rare and is unlikely to affect much the line
#       count, which is anyway a very imprecise metric.
#
def handleCStyleComment(line, within):
    line = line.rstrip('\\ ') # Strip trailing backslach to handle comments in macros
    hasCode = False
    i = 0
    while i < len(line):
        if within:
            if line[i:i+2] == '*/':
                within = False
                i += 2
            else:
                i += 1
        else:
            if line[i:i+2] == '/*':
                within = True
                i += 2
            else:
                hasCode = True
                i += 1
    return hasCode, within

# C++ has // and /* comments
def cppCount(filepath, isTestDir = False, isWrapDir = False):
    global cppBlank
    global cppLegal
    global cppComment
    global cppDoc
    global cppTest
    global cppWrap
    global cppCode
    with open(filepath, 'r') as handle:
        isLegal = False
        within = False
        for line in handle:
            line = line.strip()

            # Handle C-style comments
            hasCode, within = handleCStyleComment(line, within)

            # Handle legal comments
            if (line.startswith('// Copyright')
                  or line.startswith('* Copyright')    # For embedded third-party code (e.g., see vgc/core/mat4d.cpp)
                  or line.startswith('/* Copyright')): # For embedded third-party code
                isLegal = True
            elif (isLegal and not (
                    line.startswith('//')
                    or line.startswith('*'))): # For embedded third-party code
                isLegal = False

            # Dispatch
            if isLegal:
                cppLegal += 1
            elif not line:
                cppBlank += 1
            elif line.startswith('///') or line.startswith('/**'): # For Doxygen within multiline macros (e.g., see vgc/core/object.h)
                cppDoc += 1
            elif line.startswith('//') or not hasCode:
                cppComment += 1
            elif isTestDir:
                cppTest += 1
            elif isWrapDir:
                cppWrap += 1
            else:
                cppCode += 1

# Python has # comments
def pyCount(filepath, isTestDir = False, isWrapDir = False):
    global pyBlank
    global pyLegal
    global pyComment
    global pyDoc
    global pyTest
    global pyWrap
    global pyCode
    with open(filepath, 'r') as handle:
        isLegal = False
        for line in handle:
            line = line.lstrip()

            # Handle legal comments
            if line.startswith('# Copyright'):
                isLegal = True
            elif isLegal and not line.startswith('#'):
                isLegal = False

            # Dispatch
            if isLegal:
                pyLegal += 1
            elif not line:
                pyBlank += 1
            elif line.startswith('#'):
                pyComment += 1
            elif isTestDir:
                pyTest += 1
            elif isWrapDir:
                pyWrap += 1
            else:
                pyCode += 1

# CMake has # comments
def cmakeCount(filepath, isTestDir = False, isWrapDir = False):
    global cmakeBlank
    global cmakeLegal
    global cmakeComment
    global cmakeDoc
    global cmakeTest
    global cmakeWrap
    global cmakeCode
    with open(filepath, 'r') as handle:
        isLegal = False
        for line in handle:
            line = line.lstrip()

            # Handle legal comments
            if line.startswith('# Copyright'):
                isLegal = True
            elif isLegal and not line.startswith('#'):
                isLegal = False

            # Dispatch
            if isLegal:
                cmakeLegal += 1
            elif not line:
                cmakeBlank += 1
            elif line.startswith('#'):
                cmakeComment += 1
            elif isTestDir:
                cmakeTest += 1
            elif isWrapDir:
                cmakeWrap += 1
            else:
                cmakeCode += 1

# GLSL has // and /* comments
def glslCount(filepath, isTestDir = False, isWrapDir = False):
    global glslBlank
    global glslLegal
    global glslComment
    global glslDoc
    global glslTest
    global glslWrap
    global glslCode
    with open(filepath, 'r') as handle:
        isLegal = False
        within = False
        for line in handle:
            line = line.lstrip()

            # Handle C-style comments
            hasCode, within = handleCStyleComment(line, within)

            # Handle legal comments
            if line.startswith('// Copyright'):
                isLegal = True
            elif isLegal and not line.startswith('//'):
                isLegal = False

            # Dispatch
            if isLegal:
                glslLegal += 1
            elif not line:
                glslBlank += 1
            elif line.startswith('///'):
                glslDoc += 1
            elif line.startswith('//') or not hasCode:
                glslComment += 1
            elif isTestDir:
                glslTest += 1
            elif isWrapDir:
                glslWrap += 1
            else:
                glslCode += 1

# Qt stylesheets have /* comments
def qssCount(filepath, isTestDir = False, isWrapDir = False):
    global qssBlank
    global qssLegal
    global qssComment
    global qssDoc
    global qssTest
    global qssWrap
    global qssCode
    with open(filepath, 'r') as handle:
        isLegal = False
        within = False
        for line in handle:
            line = line.lstrip()

            # Handle C-style comments
            hasCode, within = handleCStyleComment(line, within)

            # Handle legal comments
            if line.startswith('/* Copyright'):
                isLegal = True
            elif isLegal and not line.startswith('*'):
                isLegal = False

            # Dispatch
            if not line:
                qssBlank += 1
            elif not hasCode:
                qssComment += 1
            elif isTestDir:
                qssTest += 1
            elif isWrapDir:
                qssWrap += 1
            else:
                qssCode += 1

def dirCount(dir):
    isTestDir = False
    isWrapDir = False
    currentTestDir = 'NONE'
    currentWrapDir = 'NONE'

    for subdir, dirs, filenames in os.walk(dir):

        # Check whether we are in a test dir
        if subdir.endswith('/tests'):
            currentTestDir = subdir
        if subdir.startswith(currentTestDir):
            isTestDir = True
        else:
            isTestDir = False
            currentTestDir = 'NONE'

        # Check whether we are in a wrap dir
        if subdir.endswith('/wraps'):
            currentWrapDir = subdir
        if subdir.startswith(currentWrapDir):
            isWrapDir = True
        else:
            isWrapDir = False
            currentWrapDir = 'NONE'

        # Dispatch based on file name
        for filename in filenames:
            filepath = os.path.join(subdir, filename)
            if filepath.endswith(".h") or filepath.endswith(".cpp"):
                cppCount(filepath, isTestDir, isWrapDir)
            if filepath.endswith(".py") :
                pyCount(filepath, isTestDir, isWrapDir)
            if filepath.endswith("CMakeLists.txt") :
                cmakeCount(filepath, isTestDir, isWrapDir)
            if filepath.endswith(".glsl") :
                glslCount(filepath, isTestDir, isWrapDir)
            if filepath.endswith(".qss") :
                qssCount(filepath, isTestDir, isWrapDir)

rootDir = os.path.abspath(sys.argv[1])
dirCount(os.path.join(rootDir, 'apps'))
dirCount(os.path.join(rootDir, 'cmake'))
dirCount(os.path.join(rootDir, 'libs'))
cmakeCount(os.path.join(rootDir, 'CMakeLists.txt'))

print("C++ Line Counts: " + str(
    cppBlank + cppLegal + cppComment + cppDoc + cppTest + cppWrap + cppCode))
print("  Blank:   " + str(cppBlank))
print("  Legal:   " + str(cppLegal))
print("  Comment: " + str(cppComment))
print("  Doc:     " + str(cppDoc))
print("  Test:    " + str(cppTest))
print("  Wrap:    " + str(cppWrap))
print("  Code:    " + str(cppCode))

print("\nPython Line Counts: " + str(
    pyBlank + pyLegal + pyComment + pyDoc + pyTest + pyWrap + pyCode))
print("  Blank:   " + str(pyBlank))
print("  Legal:   " + str(pyLegal))
print("  Comment: " + str(pyComment))
print("  Doc:     " + str(pyDoc))
print("  Test:    " + str(pyTest))
print("  Wrap:    " + str(pyWrap))
print("  Code:    " + str(pyCode))

print("\nCMake Line Counts: " + str(
    cmakeBlank + cmakeLegal + cmakeComment + cmakeDoc + cmakeTest + cmakeWrap + cmakeCode))
print("  Blank:   " + str(cmakeBlank))
print("  Legal:   " + str(cmakeLegal))
print("  Comment: " + str(cmakeComment))
print("  Doc:     " + str(cmakeDoc))
print("  Test:    " + str(cmakeTest))
print("  Wrap:    " + str(cmakeWrap))
print("  Code:    " + str(cmakeCode))

print("\nGLSL Line Counts: " + str(
    glslBlank + glslLegal + glslComment + glslDoc + glslTest + glslWrap + glslCode))
print("  Blank:   " + str(glslBlank))
print("  Legal:   " + str(glslLegal))
print("  Comment: " + str(glslComment))
print("  Doc:     " + str(glslDoc))
print("  Test:    " + str(glslTest))
print("  Wrap:    " + str(glslWrap))
print("  Code:    " + str(glslCode))

print("\nQt Stylesheet Line Counts: " + str(
    qssBlank + qssLegal + qssComment + qssDoc + qssTest + qssWrap + qssCode))
print("  Blank:   " + str(qssBlank))
print("  Legal:   " + str(qssLegal))
print("  Comment: " + str(qssComment))
print("  Doc:     " + str(qssDoc))
print("  Test:    " + str(qssTest))
print("  Wrap:    " + str(qssWrap))
print("  Code:    " + str(qssCode))

totalBlank = cppBlank + pyBlank + cmakeBlank + glslBlank + qssBlank
totalLegal = cppLegal + pyLegal + cmakeLegal + glslLegal + qssLegal
totalComment = cppComment + pyComment + cmakeComment + glslComment + qssComment
totalDoc = cppDoc + pyDoc + cmakeDoc + glslDoc + qssDoc
totalTest = cppTest + pyTest + cmakeTest + glslTest + qssTest
totalWrap = cppWrap + pyWrap + cmakeWrap + glslWrap + qssWrap
totalCode = cppCode + pyCode + cmakeCode + glslCode + qssCode

print("\nTOTAL Line Counts: " + str(
    totalBlank + totalLegal + totalComment + totalDoc + totalTest + totalWrap + totalCode))
print("  Blank:   " + str(totalBlank))
print("  Legal:   " + str(totalLegal))
print("  Comment: " + str(totalComment))
print("  Doc:     " + str(totalDoc))
print("  Test:    " + str(totalTest))
print("  Wrap:    " + str(totalWrap))
print("  Code:    " + str(totalCode))
