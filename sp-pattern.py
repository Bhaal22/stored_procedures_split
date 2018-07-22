import sys
import os
import re

current_line_index = 1

def PatternExtraction(inputFile, output_folder):
    input_file_object = open(inputFile, "r")

    match_count = 0
    global current_line_index

    current_line = input_file_object.readline()
    while current_line:

        pattern = "^create[ \t]+procedure.*(proc_[a-zA-Z0-9_]+)[ ]*{?.*"
        match = re.match(pattern, current_line.strip(), re.IGNORECASE)
        if match:
            match_count += 1

            stored_procedure = match.groups()[0]
            #print(str(current_line_index) + ' ' + stored_procedure)
            print(stored_procedure)

            #extended_properties = extract_extended_properties(input_file_object)
            #append_extended_properties_to_file(stored_procedure, output_folder, extended_properties)

        current_line = input_file_object.readline()
        current_line_index += 1

    print(str(match_count) + ' strored procedures')


def extract_extended_properties(input_file_object):
    extended_sp_properties = []

    global current_line_index

    last_position = input_file_object.tell()
    current_line = input_file_object.readline()
    current_line_index += 1
    while current_line:
        pattern = "^SP_ADDEXTENDEDPROPERTY[ ]+(.*)"
        match = re.match(pattern, current_line.strip(), re.IGNORECASE)

        if match:
            extended_sp_properties.append('GO\n' + current_line)

        create_proc_pattern = "^create[ \t]+procedure.*(proc_[a-zA-Z0-9_]+)[ ]*{?.*"
        match_proc_pattern = re.match(create_proc_pattern, current_line.strip(), re.IGNORECASE)
        if match_proc_pattern or not current_line:
            current_line_index -= 1
            input_file_object.seek(last_position)
            return extended_sp_properties
        
        last_position = input_file_object.tell()
        current_line = input_file_object.readline()
        current_line_index += 1

def append_extended_properties_to_file(stored_procedure, output_folder, extended_properties):
    stored_procedure_file = open(os.path.join(output_folder, 'dbo.' + stored_procedure + '.sql'), 'a')
    content = '\n'.join(extended_properties)

    stored_procedure_file.write(content)
    stored_procedure_file.write('\nGO')

if __name__ == "__main__":
    inputFile = sys.argv[1]
    output_folder = sys.argv[2]
    
    print(inputFile)
    PatternExtraction(inputFile, output_folder)