import sys
import os
import re
from jinja2 import Template

current_line_index = 1

def PatternExtraction(inputFile, output_folder):
    input_file_object = open(inputFile, "r")

    match_count = 0
    global current_line_index

    current_line = input_file_object.readline()
    stored_procedures = []
    while current_line:

        pattern = "^create[ \t]+procedure.*(proc_[a-zA-Z0-9_]+)[ ]*{?.*"
        match = re.match(pattern, current_line.strip(), re.IGNORECASE)
        if match:
            match_count += 1

            stored_procedure = match.groups()[0]
            print(stored_procedure)
            stored_procedures.append(stored_procedure)

            procedure_code_block = []
            procedure_code_block = extract_procedure_code_block(input_file_object)

            procedure_code_block.insert(0, current_line)

            generate_stored_procedure_into_file(stored_procedure, procedure_code_block, output_folder)

        current_line = input_file_object.readline()
        current_line_index += 1

    generate_sp_list(os.path.basename(inputFile), stored_procedures, output_folder)
    print(str(match_count) + ' strored procedures')


def process_extended_properties(line):
    pattern = "^SP_ADDEXTENDEDPROPERTY[ ]+(.*)"
    match = re.match(pattern, line.strip(), re.IGNORECASE)

    if match:
        return True
    else:
        return False

def extract_procedure_code_block(input_file_object):
    code_block = []

    global current_line_index

    last_position = input_file_object.tell()
    current_line = input_file_object.readline()
    current_line_index += 1
    at_extended_properties = False
    while current_line:
        at_extended_properties = at_extended_properties or process_extended_properties(current_line)

        create_proc_pattern = "^create[ \t]+procedure.*(proc_[a-zA-Z0-9_]+)[ ]*{?.*"
        match_proc_pattern = re.match(create_proc_pattern, current_line.strip(), re.IGNORECASE)
        if match_proc_pattern or not current_line:
            current_line_index -= 1
            input_file_object.seek(last_position)
            return code_block
        else:
            if at_extended_properties:
                pattern = "^GO$"
                go_match = re.match(pattern, current_line.strip(), re.IGNORECASE)
                if process_extended_properties(current_line) or go_match:
                    code_block.append(current_line)
                else:
                    current_line_index -= 1
                    input_file_object.seek(last_position)
                    return code_block
            else:
                code_block.append(current_line)
        
        last_position = input_file_object.tell()
        current_line = input_file_object.readline()
        current_line_index += 1
    
    if not current_line:
        return code_block

def extract_extended_properties(input_file_object):
    code_block = []

    global current_line_index

    last_position = input_file_object.tell()
    current_line = input_file_object.readline()
    current_line_index += 1
    while current_line:
        pattern = "^SP_ADDEXTENDEDPROPERTY[ ]+(.*)"
        match = re.match(pattern, current_line.strip(), re.IGNORECASE)

        if match:
            code_block.append('GO\n' + current_line)

        create_proc_pattern = "^create[ \t]+procedure.*(proc_[a-zA-Z0-9_]+)[ ]*{?.*"
        match_proc_pattern = re.match(create_proc_pattern, current_line.strip(), re.IGNORECASE)
        if match_proc_pattern or not current_line:
            current_line_index -= 1
            input_file_object.seek(last_position)
            return code_block
        
        last_position = input_file_object.tell()
        current_line = input_file_object.readline()
        current_line_index += 1


def generate_stored_procedure_into_file(stored_procedure_name, procedure_code_block, output_folder):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    content = ''.join(procedure_code_block)
    with open('sp_template') as template_file:
        template = Template(template_file.read())

        sp_full_content = template.render(procedure_name=stored_procedure_name, procedure_code_block=content)
        stored_procedure_file = open(os.path.join(output_folder, 'dbo.' + stored_procedure_name + '.sql'), 'w')
        stored_procedure_file.write(sp_full_content)

def generate_sp_list(input_file, stored_procedures, output_folder):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    with open('sp_list_template') as template_file:
        template = Template(template_file.read())

        sp_list_full_content = template.render(input_file=input_file, store_procedure_names=stored_procedures)
        sp_list_file = open(os.path.join(output_folder, 'sp_list.sql'), 'w')
        sp_list_file.write(sp_list_full_content)

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