#!/usr/bin/env python3
#
# How to use this file converter?
#
# 1. Install Python 3 (minimum 3.6) on your computer.
#
# 2. Download this file to your computer, for example in
#    your "Downloads" folder.
#
# 3. In a command line, execute this python script with the name
#    of the VGC file you want to convert, for example:
#
#    cd Downloads
#    python vgc-2022-to-2023-file-converter.py 'C:\path\to\my-file.vgci'
#
# This will create a new file called 'my-file-converted.vgci' in the new format.
#

from pathlib import Path
import argparse
import xml.etree.ElementTree as ET

def createVertex(parent, id, position):
    global vertexId
    vertex = ET.SubElement(parent, 'vertex')
    vertex.set('id', f"v{id}")
    vertex.set('position', position)

def getStartAndEndPosition(path):
    positionsString = path.get('positions')
    positions = []
    parenthesisOpened = False
    position = ""
    for c in positionsString:
        if not parenthesisOpened:
            if c == '(':
                parenthesisOpened = True
                position = '('
        else:
            position += c
            if c == ')':
                parenthesisOpened = False
                positions.append(position)
    if not positions:
        print("Warning: path with empty positions: using (0, 0) as start/end vertex position.")
        return ('(0, 0)', '(0, 0)')
    else:
        return (positions[0], positions[-1])

# Convert an XML tree from 2022 to 2023 representation
#
def convert2022to2023(root):
    vertexId = 0
    for path in root.findall('path'):
        startVertexId = vertexId
        endVertexId = vertexId + 1
        vertexId += 2
        (startPosition, endPosition) = getStartAndEndPosition(path)
        createVertex(root, startVertexId, startPosition)
        createVertex(root, endVertexId, endPosition)
        path.set('startvertex', f"#v{startVertexId}")
        path.set('endvertex', f"#v{endVertexId}")
        path.tag = 'edge'

# Script entry point.
#
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='vgc-2022-to-2023-file-converter',
        description="Converts VGC Illustration *.vgci files from the 2022 format to the 2023 format.")
    parser.add_argument('file', nargs='+', help="path to a *.vgci file to convert")
    parser.add_argument('-f', '--force', action='store_true', help="force overwrite of existing files")
    args = parser.parse_args()

    # Iterate over files
    for f in args.file:
        inPath = Path(f)
        if inPath.suffix != '.vgci':
            print(f"Ignoring {inPath}: not a .vgci file.")
            continue
        outPath = inPath.with_name(f"{inPath.stem}-converted{inPath.suffix}")
        if outPath.exists() and not args.force:
            print(f"Ignoring {inPath}: the file {outPath} already exists (use -f option to overwrite).")
            continue
        print(f"Converting {inPath}...")
        tree = ET.parse(str(inPath))
        root = tree.getroot()
        convert2022to2023(root)
        tree.write(str(outPath), encoding='UTF-8', xml_declaration=True)
        print("Done.")
