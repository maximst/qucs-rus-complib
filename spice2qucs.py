#!/usr/bin/env python
import os
import re
import shutil
from optparse import OptionParser
from tempfile import NamedTemporaryFile


r_ltspice = re.compile(r'(mfg|type)\=[^ ]*\s?', re.IGNORECASE)
r_model = re.compile(r'(\.MODEL.*|\+.*)', re.IGNORECASE)


parser = OptionParser()

parser.add_option('-i', '--input-file', dest='input_file', help='Path to input file (default stdin).', metavar='<path>')
parser.add_option('-o', '--output-file', dest='output_file', help='Path to output file (default stdout).', metavar='<path>')
parser.add_option('-a', '--append', dest='append_', help='Add model to end of output file (ignoring withouth -o attribute).', action='store_true', default=False)

options, args = parser.parse_args()

input_file = options.input_file
output_file = options.output_file
append = options.append_

if input_file:
    with open(input_file, 'r') as f:
        input_model = f.read()
else:
    print('Please enter spice model(withouth empty lines) and press <ENTER>...\n:')
    new_line = True
    input_model = ''
    while new_line:
        new_line = raw_input()
        input_model += new_line + '\n'

# Filter only model
input_model = r_model.findall(input_model)

# Remove LTSpice specific parameters
input_model = '\n'.join(r_ltspice.sub('', s) for s in input_model)

input_tmp_file = NamedTemporaryFile(delete=False)
input_tmp_file.write(input_model + '\n')
input_tmp_file.close()

output_tmp_file = NamedTemporaryFile(mode='r')

os.system('qucsconv -i "{}" -o "{}" -if spice -of qucslib 2>&1'.format(input_tmp_file.name, output_tmp_file.name))
input_tmp_file.close()
os.remove(input_tmp_file.name)

if not output_file:
    print(output_tmp_file.read())
    output_tmp_file.close()
    exit()

if append:
    with open(output_file, 'a+') as out_file:
        for line in output_tmp_file.readlines()[1:]:
            out_file.write(line)
else:
    with open(output_file, 'w+') as out_file:
        out_file.write(output_tmp_file.read())
