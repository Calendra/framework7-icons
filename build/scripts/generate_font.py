# Font generation script from Ionicons + FontCustom
# https://github.com/FontCustom/fontcustom/
# https://github.com/driftyco/ionicons/
# http://fontcustom.com/
# http://ionicons.com/

import fontforge
import os
import subprocess
import tempfile
import json
import copy

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
BLANK_PATH = os.path.join(SCRIPT_PATH, '..', 'blank.svg')
INPUT_SVG_DIR = os.path.join(SCRIPT_PATH, '..', '..', 'src')
OUTPUT_FONT_DIR = os.path.join(SCRIPT_PATH, '..', '..', 'package/fonts')
MANIFEST_PATH = os.path.join(SCRIPT_PATH, '..', 'manifest.json')
PACKAGE_PATH = os.path.join(SCRIPT_PATH, '..', '..', 'package.json')
BUILD_DATA_PATH = os.path.join(SCRIPT_PATH, '..', 'build_data.json')
AUTO_WIDTH = False
KERNING = 15

f = fontforge.font()
f.encoding = 'UnicodeFull'
f.design_size = 28
f.em = 512
f.ascent = 448
f.descent = 64

# Add lookup table
f.addLookup("ligatable","gsub_ligature",(),(("liga",(("latn",("dflt")),)),))
f.addLookupSubtable("ligatable","ligatable1")

# Import base characters
for char in "0123456789abcdefghijklmnopqrstuvwzxyz_- ":
  glyph = f.createChar(ord(char))
  glyph.importOutlines(BLANK_PATH)
  glyph.width = 0

manifest_file = open(MANIFEST_PATH, 'r')
manifest_data = json.loads(manifest_file.read())
manifest_file.close()

package_file = open(PACKAGE_PATH, 'r')
package = json.loads(package_file.read())
package_file.close()

build_data = copy.deepcopy(manifest_data)
build_data['icons'] = []

font_name = manifest_data['name']

for dirname, dirnames, filenames in os.walk(INPUT_SVG_DIR):
  for filename in filenames:
    name, ext = os.path.splitext(filename)
    filePath = os.path.join(dirname, filename)
    size = os.path.getsize(filePath)
    if ext in ['.svg', '.eps']:

      build_data['icons'].append({
        'name': name
      })

      if ext in ['.svg']:
        # hack removal of <switch> </switch> tags
        svgfile = open(filePath, 'r+')
        tmpsvgfile = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        svgtext = svgfile.read()
        svgfile.seek(0)

        # replace the <switch> </switch> tags with 'nothing'
        svgtext = svgtext.replace('<switch>', '')
        svgtext = svgtext.replace('</switch>', '')
        
        bytes = svgtext.encode(encoding='UTF-8')
        tmpsvgfile.file.write(bytes)

        svgfile.close()
        tmpsvgfile.file.close()

        filePath = tmpsvgfile.name
        # end hack

      glyph = f.createChar(-1, name)
      glyph.importOutlines(filePath)

      # Add ligatures
      ligature = [];
      for c in name:
        if (c == '_'):
          c = "underscore"
        if (c == '-'):
          c = "hyphen"
        if (c == ' '):
          c = "space"
        if (c == '1'):
          c = "one"
        if (c == '2'):
          c = "two"
        if (c == '3'):
          c = "three"
        if (c == '4'):
          c = "four"
        if (c == '5'):
          c = "five"
        if (c == '6'):
          c = "six"
        if (c == '7'):
          c = "seven"
        if (c == '8'):
          c = "eight"
        if (c == '9'):
          c = "nine"
        if (c == '0'):
          c = "zero"
        ligature.append(c)
      glyph.addPosSub('ligatable1', ligature)

      # if we created a temporary file, let's clean it up
      if tmpsvgfile:
        os.unlink(tmpsvgfile.name)

      # set glyph size explicitly or automatically depending on autowidth
      if AUTO_WIDTH:
        glyph.left_side_bearing = glyph.right_side_bearing = 0
        glyph.round()
      else:
        glyph.width = 512

    # resize glyphs if autowidth is enabled
    if AUTO_WIDTH:
      f.autoWidth(0, 0, 512)

  fontfile = '%s/Framework7Icons-Regular' % (OUTPUT_FONT_DIR)

f.fontname = font_name
f.familyname = font_name
f.fullname = font_name
f.generate(fontfile + '.ttf')

scriptPath = os.path.dirname(os.path.realpath(__file__))

# eotlitetool.py script to generate IE7-compatible .eot fonts
subprocess.call('python ' + scriptPath + '/eotlitetool.py ' + fontfile + '.ttf -o ' + fontfile + '.eot', shell=True)
subprocess.call('mv ' + fontfile + '.eotlite ' + fontfile + '.eot', shell=True)

# Hint the TTF file
subprocess.call('ttfautohint -s -f -n ' + fontfile + '.ttf ' + fontfile + '-hinted.ttf > /dev/null 2>&1 && mv ' + fontfile + '-hinted.ttf ' + fontfile + '.ttf', shell=True)

# WOFF2 Font
subprocess.call('./woff2/woff2_compress ' + fontfile + '.ttf', shell=True)

manifest_data['icons'] = sorted(build_data['icons'], key=lambda k: k['name'])
build_data['icons'] = sorted(build_data['icons'], key=lambda k: k['name'])

print ("Save Manifest, Icons: %s" % ( len(manifest_data['icons']) ))
f = open(MANIFEST_PATH, 'w')
f.write( json.dumps(manifest_data, indent=2, separators=(',', ': ')) )
f.close()

print ("Save Build, Icons: %s" % ( len(build_data['icons']) ))
f = open(BUILD_DATA_PATH, 'w')
f.write( json.dumps(build_data, indent=2, separators=(',', ': ')) )
f.close()
