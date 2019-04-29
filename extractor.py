from config import input_dir, file_name_column, tags, output_csv_file
import logging
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import glob
import locale

log = logging.getLogger('extractor')


results_columns = [file_name_column] + ([tags[key] for key in tags.keys()])
results_data_frame = pd.DataFrame(columns=results_columns)


def extract_info_from_file(input_file_path):
    """
        Extracts the required information out of a file.

        Params:
            input_file_path - path to the file used to extract the information

        Returns:
            Dataframe - containing the previous and current extracted information
    """
    results_dict = {}

    file_name = os.path.basename(input_file_path)
    log.debug('Processing file: {}'.format(file_name))
    results_dict[file_name_column] = file_name

    f = open(input_file_path, mode='r', encoding='utf-8')
    fileContent = f.read()

    soup = BeautifulSoup(fileContent, 'lxml')

    # XBRL Terms description:
    #
    # instance - an XBRL document whose root element is <xbrli:xbrl>
    # fact - An individual detail in a report, such as $20M
    # concept - The meaning associated with a fact, such as the cost of goods sold
    # entity - The company or individual described by a concept
    # context - A data structure that associates an entity with a concept



    for xml_tag in tags:

        resultKey = tags[xml_tag]

        name, index = get_node_name_and_index(xml_tag)

        if input_file_path.endswith('.xml'): #XBRL format

            tag_list = soup.find_all(re.compile('\w+:' + name, re.IGNORECASE))

        else: #iXBRL format

            tag_list = soup.find_all(re.compile('.+', re.IGNORECASE), {'name': re.compile('\w+:' + name, re.IGNORECASE)})

        count = 0
        results_dict[resultKey] = ''

        for tag in tag_list:
            if count == index:

                value = tag.text.strip()

                log.debug('Found {} with value: {}'.format(xml_tag, value))

                try:
                    results_dict[resultKey] = locale.atof(value)
                except ValueError:
                    log.debug('{} is not a number'.format(value))
                    results_dict[resultKey] = value

                break

            count += 1

    log.info('For file {} extracted the following features: {}'.format(file_name, results_dict))
    return results_data_frame.append(results_dict, ignore_index=True)

def get_node_name_and_index(name):
    """
        For a specific node in format node[index] extracts the node name and the index.

        Params:
            name - string containing the name to be parsed in format name[index]

        Returns:
            node_name - the substring up to the '[' character
            index - the index contained betweek the '[]' characters
    """

    if '[' not in name and ']' not in name:
        return name, 0

    bracket_start_index = name.find('[')
    bracket_end_index = name.find(']')

    node_name = name[:bracket_start_index]
    index = int(name[bracket_start_index + 1:
                 bracket_end_index])

    return node_name, index



# For each file in the current directory and all of the subdirs extract the necessary information
for file_name in glob.iglob(input_dir + '/**/*.*', recursive=True):
    results_data_frame = extract_info_from_file(input_file_path=file_name)

results_data_frame.to_csv(output_csv_file)
