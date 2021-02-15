# author : Adam Yp-Tcha

# Messenger JSON files sometimes contain duplicate messages: every message had 2 consecutive occurences in its JSON file.
# I don't know what's causing this issue, but it's facebook-side.
# This script detects if any of the input JSON files contains duplicate messages, and re-create proper JSON files if needed.

import json
import os


def get_nb_files(directory):
    """Count the number of JSON files in the input directory"""
    folder = os.listdir(directory)
    counter = 0
    for file in folder:
        if 'message_' in file:
            counter += 1
    return counter


def remove(directory):
    """Detect if any of the input file contains duplicate messages.
    If one does, a new removed_duplicates directory is created and new JSON files are generated without duplicates."""
    nbfiles = get_nb_files(directory)
    duplicates = False
    final_files = []

    for i in range(1, nbfiles + 1):
        final_file = {}
        with open(directory + '/message_' + str(i) + '.json', 'r') as myfile:
            data = myfile.read()
            obj = json.loads(data)
            messages = obj['messages']
            new_messages = []
            nbMsgs = len(obj['messages'])
            for i in range(nbMsgs - 1):
                if messages[i] != messages[i + 1]:
                    new_messages.append(messages[i])
                else:
                    duplicates = True
            new_messages.append(messages[nbMsgs - 1])
        final_file['participants'] = obj['participants']
        final_file['messages'] = new_messages
        final_file['is_still_participant'] = obj['is_still_participant']
        final_file['thread_type'] = obj['thread_type']
        final_file['path'] = obj['thread_path']
        final_files.append(final_file)
    # print('in remove_duplicates : '+ str(duplicates))

    if duplicates:
        if not os.path.exists(directory + '/removed_duplicates/'):
            os.makedirs(directory + '/removed_duplicates/')
        for i in range(len(final_files)):
            with open(directory + '/removed_duplicates/message_' + str(i + 1) + '.json', 'w') as outfile:
                json.dump(final_files[i], outfile)

    return duplicates




