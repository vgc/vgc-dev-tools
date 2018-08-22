#!/usr/bin/env python3

import os
import glob
import shutil # for rmtree (= "rm -Rf")
import subprocess # for git (note: in the future, we may want to use GitPython instead)
import sys

if len(sys.argv) < 2:
    print('Usage: ./count_lines.py <vgc-root-dir> [--historical [numCommits]]')
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

class LineCounts:
    def __init__(self):
        # Counters for lines in C++ files
        self.cppBlank = 0
        self.cppLegal = 0
        self.cppComment = 0
        self.cppDoc = 0
        self.cppTest = 0
        self.cppWrap = 0
        self.cppCode = 0

        # Counters for lines in Python files
        self.pyBlank = 0
        self.pyLegal = 0
        self.pyComment = 0
        self.pyDoc = 0
        self.pyTest = 0
        self.pyWrap = 0
        self.pyCode = 0

        # Counters for lines in CMake files
        self.cmakeBlank = 0
        self.cmakeLegal = 0
        self.cmakeComment = 0
        self.cmakeDoc = 0
        self.cmakeTest = 0
        self.cmakeWrap = 0
        self.cmakeCode = 0

        # Counters for lines in GLSL shader files
        self.glslBlank = 0
        self.glslLegal = 0
        self.glslComment = 0
        self.glslDoc = 0
        self.glslTest = 0
        self.glslWrap = 0
        self.glslCode = 0

        # Counters for lines in Qt stylesheet files
        self.qssBlank = 0
        self.qssLegal = 0
        self.qssComment = 0
        self.qssDoc = 0
        self.qssTest = 0
        self.qssWrap = 0
        self.qssCode = 0

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
def cppCount(filepath, count, isTestDir = False, isWrapDir = False):
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
                count.cppLegal += 1
            elif not line:
                count.cppBlank += 1
            elif line.startswith('///') or line.startswith('/**'): # For Doxygen within multiline macros (e.g., see vgc/core/object.h)
                count.cppDoc += 1
            elif line.startswith('//') or not hasCode:
                count.cppComment += 1
            elif isTestDir:
                count.cppTest += 1
            elif isWrapDir:
                count.cppWrap += 1
            else:
                count.cppCode += 1

# Python has # comments
def pyCount(filepath, count, isTestDir = False, isWrapDir = False):
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
                count.pyLegal += 1
            elif not line:
                count.pyBlank += 1
            elif line.startswith('#'):
                count.pyComment += 1
            elif isTestDir:
                count.pyTest += 1
            elif isWrapDir:
                count.pyWrap += 1
            else:
                count.pyCode += 1

# CMake has # comments
def cmakeCount(filepath, count, isTestDir = False, isWrapDir = False):
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
                count.cmakeLegal += 1
            elif not line:
                count.cmakeBlank += 1
            elif line.startswith('#'):
                count.cmakeComment += 1
            elif isTestDir:
                count.cmakeTest += 1
            elif isWrapDir:
                count.cmakeWrap += 1
            else:
                count.cmakeCode += 1

# GLSL has // and /* comments
def glslCount(filepath, count, isTestDir = False, isWrapDir = False):
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
                count.glslLegal += 1
            elif not line:
                count.glslBlank += 1
            elif line.startswith('///'):
                count.glslDoc += 1
            elif line.startswith('//') or not hasCode:
                count.glslComment += 1
            elif isTestDir:
                count.glslTest += 1
            elif isWrapDir:
                count.glslWrap += 1
            else:
                count.glslCode += 1

# Qt stylesheets have /* comments
def qssCount(filepath, count, isTestDir = False, isWrapDir = False):
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
                count.qssBlank += 1
            elif not hasCode:
                count.qssComment += 1
            elif isTestDir:
                count.qssTest += 1
            elif isWrapDir:
                count.qssWrap += 1
            else:
                count.qssCode += 1

def dirCount(dir, count):
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
                cppCount(filepath, count, isTestDir, isWrapDir)
            if filepath.endswith(".py") :
                pyCount(filepath, count, isTestDir, isWrapDir)
            if filepath.endswith("CMakeLists.txt") :
                cmakeCount(filepath, count, isTestDir, isWrapDir)
            if filepath.endswith(".glsl") :
                glslCount(filepath, count, isTestDir, isWrapDir)
            if filepath.endswith(".qss") :
                qssCount(filepath, count, isTestDir, isWrapDir)

def getCurrentCount(rootDir):
    count = LineCounts()
    dirCount(os.path.join(rootDir, 'apps'), count)
    dirCount(os.path.join(rootDir, 'cmake'), count)
    dirCount(os.path.join(rootDir, 'libs'), count)
    cmakeCount(os.path.join(rootDir, 'CMakeLists.txt'), count)
    return count

def printCount(count):
    totalBlank = count.cppBlank + count.pyBlank + count.cmakeBlank + count.glslBlank + count.qssBlank
    totalLegal = count.cppLegal + count.pyLegal + count.cmakeLegal + count.glslLegal + count.qssLegal
    totalComment = count.cppComment + count.pyComment + count.cmakeComment + count.glslComment + count.qssComment
    totalDoc = count.cppDoc + count.pyDoc + count.cmakeDoc + count.glslDoc + count.qssDoc
    totalTest = count.cppTest + count.pyTest + count.cmakeTest + count.glslTest + count.qssTest
    totalWrap = count.cppWrap + count.pyWrap + count.cmakeWrap + count.glslWrap + count.qssWrap
    totalCode = count.cppCode + count.pyCode + count.cmakeCode + count.glslCode + count.qssCode

    print("Total Line Counts: " + str(
        totalBlank + totalLegal + totalComment + totalDoc + totalTest + totalWrap + totalCode))
    print("  Blank:   " + str(totalBlank))
    print("  Legal:   " + str(totalLegal))
    print("  Comment: " + str(totalComment))
    print("  Doc:     " + str(totalDoc))
    print("  Test:    " + str(totalTest))
    print("  Wrap:    " + str(totalWrap))
    print("  Code:    " + str(totalCode))

    print("\nC++ Line Counts: " + str(
        count.cppBlank + count.cppLegal + count.cppComment + count.cppDoc + count.cppTest + count.cppWrap + count.cppCode))
    print("  Blank:   " + str(count.cppBlank))
    print("  Legal:   " + str(count.cppLegal))
    print("  Comment: " + str(count.cppComment))
    print("  Doc:     " + str(count.cppDoc))
    print("  Test:    " + str(count.cppTest))
    print("  Wrap:    " + str(count.cppWrap))
    print("  Code:    " + str(count.cppCode))

    print("\nPython Line Counts: " + str(
        count.pyBlank + count.pyLegal + count.pyComment + count.pyDoc + count.pyTest + count.pyWrap + count.pyCode))
    print("  Blank:   " + str(count.pyBlank))
    print("  Legal:   " + str(count.pyLegal))
    print("  Comment: " + str(count.pyComment))
    print("  Doc:     " + str(count.pyDoc))
    print("  Test:    " + str(count.pyTest))
    print("  Wrap:    " + str(count.pyWrap))
    print("  Code:    " + str(count.pyCode))

    print("\nCMake Line Counts: " + str(
        count.cmakeBlank + count.cmakeLegal + count.cmakeComment + count.cmakeDoc + count.cmakeTest + count.cmakeWrap + count.cmakeCode))
    print("  Blank:   " + str(count.cmakeBlank))
    print("  Legal:   " + str(count.cmakeLegal))
    print("  Comment: " + str(count.cmakeComment))
    print("  Doc:     " + str(count.cmakeDoc))
    print("  Test:    " + str(count.cmakeTest))
    print("  Wrap:    " + str(count.cmakeWrap))
    print("  Code:    " + str(count.cmakeCode))

    print("\nGLSL Line Counts: " + str(
        count.glslBlank + count.glslLegal + count.glslComment + count.glslDoc + count.glslTest + count.glslWrap + count.glslCode))
    print("  Blank:   " + str(count.glslBlank))
    print("  Legal:   " + str(count.glslLegal))
    print("  Comment: " + str(count.glslComment))
    print("  Doc:     " + str(count.glslDoc))
    print("  Test:    " + str(count.glslTest))
    print("  Wrap:    " + str(count.glslWrap))
    print("  Code:    " + str(count.glslCode))

    print("\nQt Stylesheet Line Counts: " + str(
        count.qssBlank + count.qssLegal + count.qssComment + count.qssDoc + count.qssTest + count.qssWrap + count.qssCode))
    print("  Blank:   " + str(count.qssBlank))
    print("  Legal:   " + str(count.qssLegal))
    print("  Comment: " + str(count.qssComment))
    print("  Doc:     " + str(count.qssDoc))
    print("  Test:    " + str(count.qssTest))
    print("  Wrap:    " + str(count.qssWrap))
    print("  Code:    " + str(count.qssCode))

def printInline(s):
    print(s, end='')

class Csv:
    def __init__(self):
        self.first_ = True

    def printValue(self, s):
        if self.first_:
            self.first_ = False
        else:
            printInline(',')
        printInline(s)


    def printNewline(self):
        printInline('\n')

def beginCsv(s):
    global csvIsBegin_
    csvIsBegin_ = True

def endCsv(s):
    global csvIsBegin_
    csvIsBegin_ = Fal

    printInline(s)

def printCsv(s):
    printInline(s)

def printCountOneLine(date, count):
    csv = Csv()

    csv.printValue(date)

    totalBlank = count.cppBlank + count.pyBlank + count.cmakeBlank + count.glslBlank + count.qssBlank
    totalLegal = count.cppLegal + count.pyLegal + count.cmakeLegal + count.glslLegal + count.qssLegal
    totalComment = count.cppComment + count.pyComment + count.cmakeComment + count.glslComment + count.qssComment
    totalDoc = count.cppDoc + count.pyDoc + count.cmakeDoc + count.glslDoc + count.qssDoc
    totalTest = count.cppTest + count.pyTest + count.cmakeTest + count.glslTest + count.qssTest
    totalWrap = count.cppWrap + count.pyWrap + count.cmakeWrap + count.glslWrap + count.qssWrap
    totalCode = count.cppCode + count.pyCode + count.cmakeCode + count.glslCode + count.qssCode

    csv.printValue(totalBlank + totalLegal + totalComment + totalDoc + totalTest + totalWrap + totalCode)
    csv.printValue(totalBlank)
    csv.printValue(totalLegal)
    csv.printValue(totalComment)
    csv.printValue(totalDoc)
    csv.printValue(totalTest)
    csv.printValue(totalWrap)
    csv.printValue(totalCode)

    csv.printValue(count.cppBlank + count.cppLegal + count.cppComment + count.cppDoc + count.cppTest + count.cppWrap + count.cppCode)
    csv.printValue(count.cppBlank)
    csv.printValue(count.cppLegal)
    csv.printValue(count.cppComment)
    csv.printValue(count.cppDoc)
    csv.printValue(count.cppTest)
    csv.printValue(count.cppWrap)
    csv.printValue(count.cppCode)

    csv.printValue(count.pyBlank + count.pyLegal + count.pyComment + count.pyDoc + count.pyTest + count.pyWrap + count.pyCode)
    csv.printValue(count.pyBlank)
    csv.printValue(count.pyLegal)
    csv.printValue(count.pyComment)
    csv.printValue(count.pyDoc)
    csv.printValue(count.pyTest)
    csv.printValue(count.pyWrap)
    csv.printValue(count.pyCode)

    csv.printValue(count.cmakeBlank + count.cmakeLegal + count.cmakeComment + count.cmakeDoc + count.cmakeTest + count.cmakeWrap + count.cmakeCode)
    csv.printValue(count.cmakeBlank)
    csv.printValue(count.cmakeLegal)
    csv.printValue(count.cmakeComment)
    csv.printValue(count.cmakeDoc)
    csv.printValue(count.cmakeTest)
    csv.printValue(count.cmakeWrap)
    csv.printValue(count.cmakeCode)

    csv.printValue(count.glslBlank + count.glslLegal + count.glslComment + count.glslDoc + count.glslTest + count.glslWrap + count.glslCode)
    csv.printValue(count.glslBlank)
    csv.printValue(count.glslLegal)
    csv.printValue(count.glslComment)
    csv.printValue(count.glslDoc)
    csv.printValue(count.glslTest)
    csv.printValue(count.glslWrap)
    csv.printValue(count.glslCode)

    csv.printValue(count.qssBlank + count.qssLegal + count.qssComment + count.qssDoc + count.qssTest + count.qssWrap + count.qssCode)
    csv.printValue(count.qssBlank)
    csv.printValue(count.qssLegal)
    csv.printValue(count.qssComment)
    csv.printValue(count.qssDoc)
    csv.printValue(count.qssTest)
    csv.printValue(count.qssWrap)
    csv.printValue(count.qssCode)

    csv.printNewline()

def printCountOneLineHeader():

    csv = Csv()

    csv.printValue("Commit date/time")

    csv.printValue("Total")
    csv.printValue("Blank")
    csv.printValue("Legal")
    csv.printValue("Comment")
    csv.printValue("Doc")
    csv.printValue("Test")
    csv.printValue("Wrap")
    csv.printValue("Code")

    csv.printValue("C++ (Total)")
    csv.printValue("C++ (Blank)")
    csv.printValue("C++ (Legal)")
    csv.printValue("C++ (Comment)")
    csv.printValue("C++ (Doc)")
    csv.printValue("C++ (Test)")
    csv.printValue("C++ (Wrap)")
    csv.printValue("C++ (Code)")

    csv.printValue("Python (Total)")
    csv.printValue("Python (Blank)")
    csv.printValue("Python (Legal)")
    csv.printValue("Python (Comment)")
    csv.printValue("Python (Doc)")
    csv.printValue("Python (Test)")
    csv.printValue("Python (Wrap)")
    csv.printValue("Python (Code)")

    csv.printValue("CMake (Total)")
    csv.printValue("CMake (Blank)")
    csv.printValue("CMake (Legal)")
    csv.printValue("CMake (Comment)")
    csv.printValue("CMake (Doc)")
    csv.printValue("CMake (Test)")
    csv.printValue("CMake (Wrap)")
    csv.printValue("CMake (Code)")

    csv.printValue("GLSL (Total)")
    csv.printValue("GLSL (Blank)")
    csv.printValue("GLSL (Legal)")
    csv.printValue("GLSL (Comment)")
    csv.printValue("GLSL (Doc)")
    csv.printValue("GLSL (Test)")
    csv.printValue("GLSL (Wrap)")
    csv.printValue("GLSL (Code)")

    csv.printValue("Qt Stylesheet (Total)")
    csv.printValue("Qt Stylesheet (Blank)")
    csv.printValue("Qt Stylesheet (Legal)")
    csv.printValue("Qt Stylesheet (Comment)")
    csv.printValue("Qt Stylesheet (Doc)")
    csv.printValue("Qt Stylesheet (Test)")
    csv.printValue("Qt Stylesheet (Wrap)")
    csv.printValue("Qt Stylesheet (Code)")

    csv.printNewline()

def printCurrentCount(rootDir):
    count = getCurrentCount(rootDir)
    printCount(count)

def printHistoricalCount(rootDir):
    curDir = os.path.abspath(os.curdir)
    tmpDir = os.path.abspath("count_lines_tmp")

    if os.path.isdir(tmpDir):
        shutil.rmtree(tmpDir)

    subprocess.run(["git",  "clone", "-q", rootDir, tmpDir])

    os.chdir(tmpDir)

    maxCommits = -1
    if len(sys.argv) > 3:
        maxCommits = int(sys.argv[3])

    printCountOneLineHeader()

    numCommits = 0
    while maxCommits == -1 or numCommits < maxCommits:
        if numCommits > 0:
            subprocess.run(["git",  "checkout", "-q", "HEAD^"])
        numCommits += 1

        # Get commit date and time as per git "iso" format: "2018-08-08 15:40:31 +0200"
        commitDatetime = subprocess.check_output(["git",  "show", "-s", "--date=iso", "--format=format:%ad"]).decode('utf8')

        # Get commit date and time as ISO 8601: "2018-08-08T15:40:31+0200"
        commitDatetime = commitDatetime.replace(" ", "T", 1)
        commitDatetime = commitDatetime.replace(" ", "", 1)

        try:
            count = getCurrentCount(tmpDir)
            printCountOneLine(commitDatetime, count)
        except FileNotFoundError:
            # This is raised when 'CMakeLists.txt' is not found, which happens for the first
            # few commits of the VGC git repository. This is a good moment to break out of
            # the loop
            maxCommits = 0

    if os.path.isdir(tmpDir):
        shutil.rmtree(tmpDir)

rootDir = os.path.abspath(sys.argv[1])
if len(sys.argv) > 2:
    if sys.argv[2] == "--historical":
        printHistoricalCount(rootDir)
    else:
        print("Unknown option " + sys.argv[2])
else:
    printCurrentCount(rootDir)
