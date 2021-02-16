# author: Adam Yp-Tcha

import argparse
import csv
import datetime as dt
import json
import logging
import math
import os
import sys

from dateutil import tz

import JSON_remove_duplicates


output_path = "./output/" + dt.datetime.now().strftime("%Y-%b-%d_%H%M%S") + '/'

if not os.path.exists(output_path):
    os.makedirs(output_path)

logging.basicConfig(filename=output_path + "logfile.log", filemode='w', level=logging.INFO, format='---- %(asctime)s ---- %('
                                                                                     'levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('start')

# Messenger reactions as stored in the JSON files
LIKE = "ð\u009f\u0091\u008d".encode('iso-8859-1').decode('utf8')
DISLIKE = "ð\u009f\u0091\u008e".encode('iso-8859-1').decode('utf8')
HAHA = "ð\u009f\u0098\u0086".encode('iso-8859-1').decode('utf8')
HEART = "ð\u009f\u0098\u008d".encode('iso-8859-1').decode('utf8')
HEART2 = "â\u009d¤".encode('iso-8859-1').decode('utf8')
HEART3 = "ð\u009f\u0092\u0097".encode('iso-8859-1').decode('utf8')
SAD = "ð\u009f\u0098¢".encode('iso-8859-1').decode('utf8')
OH = "ð\u009f\u0098®".encode('iso-8859-1').decode('utf8')
ANGRY = "ð\u009f\u0091\u008e".encode('iso-8859-1').decode('utf8')
ANGRY2 = "ð\u009f\u0098\u00a0".encode('iso-8859-1')


def get_id(name, participants_list):
    """Return the numeral ID of a participant in the list of people in the conversation.
     Will return -1 if the participant is not found, . """
    i = 0
    while i != len(participants_list) and participants_list[i]['name'] != name:
        i += 1
    if i == len(participants_list):
        return -1
    else:
        return i


def handle_reactions(msg, statistics, participants_list, counter):
    """Identify all reactions in a message and update the statistics table"""
    for i in range(len(msg['reactions'])):
        if msg['reactions'][i]['reaction'].encode('iso-8859-1').decode('utf8') == LIKE:
            statistics[get_id(msg['reactions'][i][
                                  'actor'], participants_list) + 1][2][0] += 1
            statistics[get_id(msg['sender_name'], participants_list) + 1][1][0] += 1

        elif msg['reactions'][i]['reaction'].encode('iso-8859-1').decode('utf8') == DISLIKE:
            statistics[get_id(msg['reactions'][i][
                                  'actor'], participants_list) + 1][2][1] += 1
            statistics[get_id(msg['sender_name'], participants_list) + 1][1][1] += 1

        elif msg['reactions'][i]['reaction'].encode('iso-8859-1').decode('utf8') == HAHA:
            statistics[get_id(msg['reactions'][i][
                                  'actor'], participants_list) + 1][2][2] += 1
            statistics[get_id(msg['sender_name'], participants_list) + 1][1][2] += 1

        elif msg['reactions'][i]['reaction'].encode('iso-8859-1').decode('utf8') in (HEART, HEART2, HEART3):
            statistics[get_id(msg['reactions'][i][
                                  'actor'], participants_list) + 1][2][3] += 1
            statistics[get_id(msg['sender_name'], participants_list) + 1][1][3] += 1

        elif msg['reactions'][i]['reaction'].encode('iso-8859-1').decode('utf8') == SAD:
            statistics[get_id(msg['reactions'][i][
                                  'actor'], participants_list) + 1][2][4] += 1
            statistics[get_id(msg['sender_name'], participants_list) + 1][1][4] += 1

        elif msg['reactions'][i]['reaction'].encode('iso-8859-1').decode('utf8') == OH:
            statistics[get_id(msg['reactions'][i][
                                  'actor'], participants_list) + 1][2][5] += 1
            statistics[get_id(msg['sender_name'], participants_list) + 1][1][5] += 1

        elif msg['reactions'][i]['reaction'].encode('iso-8859-1').decode('utf8') == ANGRY or \
                msg['reactions'][i]['reaction'].encode('iso-8859-1') == ANGRY2:
            statistics[get_id(msg['reactions'][i][
                                  'actor'], participants_list) + 1][2][6] += 1
            statistics[get_id(msg['sender_name'], participants_list) + 1][1][6] += 1

        else:
            if any(x in msg for x in ['content', 'photos', 'sticker', 'gifs', 'videos']):
                statistics[get_id(msg['reactions'][i][
                                      'actor'], participants_list) + 1][2][7] += 1
                statistics[get_id(msg['sender_name'], participants_list) + 1][1][7] += 1
            else:
                logging.warning("can't count react in message " + str(msg))

    return counter + len(msg['reactions'])


def length_without_spaces(msg):
    """Return the length of the message as a string (counting each character). Space characters are ignored."""
    length = len(msg['content'].encode('iso-8859-1').decode(
        'utf-8')) - msg['content'].encode('iso-8859-1').decode(
        'utf-8').count(' ')
    return length


def insert_sort(tab):
    """Sort a table using the insert method. This function is used to sort the people statistics table by number of msgs."""
    tab2 = tab[1:]
    for i in range(1, len(tab2)):
        elt = tab2[i]
        j = i - 1
        while j >= 0 and elt[3][0] < tab2[j][3][0]:
            tab2[j + 1] = tab2[j]
            j -= 1
        tab2[j + 1] = elt
    tab2.reverse()
    tab[1:] = tab2


def round_half_up(n, decimals=0):
    """Round up half float number"""
    multiplier = 10 ** decimals
    ans = math.floor(n * multiplier + 0.5) / multiplier

    return float(format(ans, '.' + str(decimals) + 'f'))


def count_words(msg):
    """Count the number of words in a message."""
    return len(msg['content'].encode('iso-8859-1').decode('utf-8').split())


def strfdelta(tdelta):
    return [int(tdelta.days), int(divmod(tdelta.seconds, 3600)[0])]


def same_time_slot(timeslot, date_timestamp):
    """Check if a date (provided as a timestamp) matches the timeslot"""
    date_str = utc2local(date_timestamp).strftime("%d-%m-%Y %H")
    date_time_slot = date_str + ":00 to " + str(int(date_str[-2:]) + 1).zfill(2) + ":00"
    if timeslot == date_time_slot:
        return True
    else:
        return False


def add_empty_lines(time_table, time_delay, number_of_people):
    """Add empty time slot lines in the daily time table, whenever a message is more than one hour after the previous one."""
    last_date_str = time_delay[1].strftime("%d-%m-%Y %H")
    current_date = time_delay[0] - dt.timedelta(hours=1)
    current_date_str = current_date.strftime("%d-%m-%Y %H")
    while current_date_str != last_date_str:
        time_table += [[current_date_str + ":00 to " + str(int(current_date.hour) + 1).zfill(2) + ":00", 0] + [0, ''] +
                       2 * number_of_people * [0]]
        current_date = current_date - dt.timedelta(hours=1)
        current_date_str = current_date.strftime("%d-%m-%Y %H")


def get_time_slot_index(msg):
    """Return the hour of a message's date"""
    hour = utc2local(msg['timestamp_ms']).strftime("%H")
    time_slot_index = int(hour)
    return time_slot_index


def handle_reacts_table(msg, reacts_table, participants_list):
    """Update the table containing the number of messages with every number of reactions received for every participant"""
    nb_reacts = len(msg['reactions'])
    participant_index = get_id(msg['sender_name'], participants_list)
    if len(reacts_table[participant_index][1]) < nb_reacts:
        reacts_table[participant_index][1] += (nb_reacts - len(reacts_table[participant_index][1])) * [0]
    reacts_table[participant_index][1][nb_reacts - 1] += 1


def equalize_reacts_table(reacts_table):
    """Add zeros at the end of every participant to equalize lengths of reacts table"""
    lengths = len(reacts_table) * [0]
    for k in range(len(reacts_table)):
        lengths += [len(reacts_table[k][1])]
    maximum = max(lengths)
    for k in range(len(reacts_table)):
        reacts_table[k][1] += (maximum - len(reacts_table[k][1])) * [0]


def time_sort(msgs_list, participants_list, time_table, daily_table):
    """Fill the time and the daily table, containing data for every 1-hour timeslot"""
    for msg in msgs_list:
        time_slot_index = get_time_slot_index(msg)

        daily_table[1 + time_slot_index][1] += 1
        daily_table[29 + time_slot_index][1 + 2 * get_id(msg['sender_name'], participants_list)] += 1

        if same_time_slot(time_table[len(time_table) - 1][0], msg['timestamp_ms']):
            time_table[len(time_table) - 1][1] += 1
            time_table[len(time_table) - 1][2 * get_id(msg['sender_name'], participants_list) + 4] += 1

        else:
            str_date1 = time_table[len(time_table) - 1][0][0:13]
            str_date2 = utc2local(msg['timestamp_ms']).strftime("%d-%m-%Y %H")
            delta_t = dt.datetime.strptime(str_date1, "%d-%m-%Y %H") - dt.datetime.strptime(str_date2, "%d-%m-%Y %H")
            time_delay = [dt.datetime.strptime(str_date1, "%d-%m-%Y %H"),
                          utc2local(msg['timestamp_ms']).replace(minute=00, second=00), strfdelta(delta_t)]

            if time_delay[2][0] * 24 + time_delay[2][1] > 1:
                add_empty_lines(time_table, time_delay, nbPeople)

            date = utc2local(msg['timestamp_ms']).strftime("%d-%m-%Y %H")
            time_table += [
                [date + ":00 to " + str(int(date[-2:]) + 1).zfill(2) + ":00", 1] + [0, ''] + 2 * nbPeople * [0]]
            time_table[len(time_table) - 1][2 * get_id(msg['sender_name'], participants_list) + 4] += 1


def init_time_table(participants_list, number_of_people, json_obj):
    """Initialize time table"""
    temp_table = ["date", "messages", "cumulated", ""]
    for k in range(number_of_people):
        temp_table = temp_table + [participants_list[k]['name'].encode('iso-8859-1').decode('utf-8'), '']
    date = utc2local(json_obj['messages'][0]['timestamp_ms']).strftime("%d-%m-%Y %H")
    table = [temp_table] + [
        [date + ":00 to " + str(int(date[-2:]) + 1) + ":00"] + [0, 0, ''] + 2 * number_of_people * [0]]
    return table


def init_daily_time_table(participants_list, number_of_people):
    """Initialize daily time table"""
    table = [['', 'Messages', 'Mean']]
    for k in range(24):
        table += [[str(k).zfill(2) + ":00 to " + str(k + 1).zfill(2) + ":00", 0, 0]]
    table += [[' '], [' '], (2 * number_of_people + 1) * ['']]

    for k in range(number_of_people):
        table[27][2 * k + 1] = participants_list[k]['name'].encode('iso-8859-1').decode('utf-8')
    table += [[''] + number_of_people * ['Messages', 'Mean']]
    for k in range(24):
        table += [[str(k).zfill(2) + ":00 to " + str(k + 1).zfill(2) + ":00"] + 2 * number_of_people * [0]]
    return table


def handle_subscribe(msg, subscribe_table):
    """Add a subscribe message to the susbscribe table"""
    subscribe_table += [dt.datetime.utcfromtimestamp(msg['timestamp_ms'] // 1000).strftime('%d-%m-%y') + ' ' + str(
        msg['content']).encode('iso-8859-1').decode('utf-8')]


def sum_time_table(time_table, number_of_people):
    """Fill the cumulated column of the time table"""
    time_table[len(time_table) - 1][2] = time_table[len(time_table) - 1][1]
    for index in range(number_of_people):
        time_table[len(time_table) - 1][5 + 2 * index] = time_table[len(time_table) - 1][4 + 2 * index]

    for index in range(1, len(time_table) - 1):
        time_table[len(time_table) - index - 1][2] = time_table[len(time_table) - index][2] + time_table[len(time_table)
                                                                                                         - index - 1][1]
        for index2 in range(number_of_people):
            time_table[len(time_table) - index - 1][5 + 2 * index2] = \
                time_table[len(time_table) - index][5 + 2 * index2] + \
                time_table[len(time_table) - index - 1][4 + 2 * index2]


def utc2local(utc):
    """Convert a UTC date to the local timezone."""
    date_time_utc = dt.datetime.utcfromtimestamp(utc // 1000)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    date_time_utc = date_time_utc.replace(tzinfo=from_zone)
    return date_time_utc.astimezone(to_zone)


subscribetable = []
nbMsgs = 0
nbPeople = 0
msgsSum1 = 0
participantsErrors = 0
reactsErrors = 0
reactsCounter = 0
wordsCounter = 0
reactsSeen = []
teststr = []
reactsTable = []
warnings = 0

parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='?', default=os.getcwd(), help="path to JSON files. If not specified, "
                                                                 "current directory is used.")
args = parser.parse_args()

directory = args.path
if JSON_remove_duplicates.get_nb_files(directory) == 0:
    logging.error("No correct JSON file found at " + directory)
    print("No correct JSON file found at " + directory + ".")
    print("Use -h or --help to see how to specify a path.")
    sys.exit()

logging.info("Checking duplicates ...")
duplicates_bool = JSON_remove_duplicates.remove(directory)
input_directory = ''

if duplicates_bool:
    logging.info("duplicates have been found! Correction successful, new files are located in " + directory +
                 '/removed_duplicates')
    input_directory = directory + '/removed_duplicates'

    nb_files = JSON_remove_duplicates.get_nb_files(input_directory)
    print("Duplicates have been found. Correction successful, " + str(nb_files) + " new files have been created.")
    logging.info(str(nb_files) + " files found")
else:
    logging.info("no duplicates found.")
    input_directory = directory
    nb_files = JSON_remove_duplicates.get_nb_files(input_directory)

    print(str(nb_files) + " files have been found!")
    logging.info(str(nb_files) + " files found")

print("Getting conversation participants list...")
logging.info("Opening file 1 for conversation participants...")

with open(input_directory + '/message_1.json', 'r') as myfile:
    data = myfile.read()
    obj = json.loads(data)

nbPeople = len(obj['participants'])
print(str(nbPeople) + ' participants in the conversation.')
logging.info(str(nbPeople) + ' participants in the conversation.')

participants = obj['participants']
logging.info("List of participants created.")
pplStats = [
    ['Name', 'like', 'dislike', 'haha', 'heart', 'sad', 'oh', 'angry', 'others', 'Total', 'Reacted messages',
     'Frequency of reacted messages', 'Reacts/messages sent ratio', 'like', 'dislike', 'haha', 'heart',
     'sad', 'oh', 'angry', 'others', 'Total', 'Reacts given/message in the conversation', 'Messages',
     'Total length (without spaces)', 'Words', 'Words/message']]
timeTable = init_time_table(participants, nbPeople, obj)
dailyTimeTable = init_daily_time_table(participants, nbPeople)

# initialize pplStats (list of each participant's statistics) :
# ['Name',
# [amounts of every 8 reacts (from index 2 to 10, received), total amount of reacts received, amount of reacted messages, amount of messages reacted/amount of messages, reacts received/message sent ratio],
# [amounts of every 8 reacts (from index 2 to 10, given), total amount of reacts given, reacts given/message ratio],
# [total amount of messages, total length of all messages (without spaces), total amount of words, words/messages ratio]]
for k in range(nbPeople):
    pplStats = pplStats + [
        [participants[k]['name'].encode('iso-8859-1').decode('utf-8'), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0]]]

    reactsTable = reactsTable + [[participants[k]['name'].encode('iso-8859-1').decode('utf-8'), []]]
logging.info("Statitistic tables initialized.")

# iterate on every JSON file
for i in range(1, nb_files + 1):
    with open(input_directory + '/message_' + str(i) + '.json', 'r') as myfile:
        data = myfile.read()
        obj = json.loads(data)

    print("Processing file " + str(i) + " out of " + str(nb_files) + " ...")
    logging.info("Processing file " + str(i) + " out of " + str(nb_files) + " ...")

    nbPeople = len(obj['participants'])

    nbMsgs = len(obj['messages'])
    logging.info(str(len(obj['messages'])) + " messages and " + str(nbPeople) + " people in file " + str(i))
    msgsSum1 += nbMsgs

    messages = obj['messages']

    # fill time table
    time_sort(messages, participants, timeTable, dailyTimeTable)

    msgIndex = 0

    # keep last message timestamp to check if the chronolgical order is kept
    previous_timestamp = messages[0]['timestamp_ms']

    for message in messages:
        msgIndex += 1
        if utc2local(message['timestamp_ms']).strftime("%d-%m-%Y %H") == "02-04-2020 14" and False:
            logging.warning(message)
            warnings += 1

        # Check if the chronological order is kept
        if message['timestamp_ms'] > previous_timestamp:
            logging.warning('timestamp issue, at message ' + str(msgIndex) + ' in file ' + str(i) +
                            ': two consecutive messages are not chronologically ordered - script will '
                            'ignore this message.')
            warnings += 1

        # Check if this participant is in the initial participants list
        if get_id(message['sender_name'], participants) == -1:
            participantsErrors += 1
            logging.warning('New participant found after conversation start - script will ignore this message')
            warnings += 1

        else:
            pplStats[get_id(message['sender_name'], participants) + 1][3][0] += 1

            if 'type' in message and message['type'] == 'Subscribe':
                handle_subscribe(message, subscribetable)

            if 'content' in message:
                pplStats[get_id(message['sender_name'], participants) + 1][3][1] += length_without_spaces(message)
                pplStats[get_id(message['sender_name'], participants) + 1][3][2] += count_words(message)

            if 'reactions' in message:
                handle_reacts_table(message, reactsTable, participants)
                pplStats[get_id(message['sender_name'], participants) + 1][1][9] += 1

                reactsCounter = handle_reactions(message, pplStats, participants, reactsCounter)

sum_time_table(timeTable, nbPeople)
equalize_reacts_table(reactsTable)

for k in range(len(pplStats) - 1):
    pplStats[k + 1] += [reactsTable[k][1]]

# sort the statistics table by participant's number of messages
insert_sort(pplStats)

# some verification on total amount of messages
msgsSum2 = participantsErrors
for pplStat in pplStats[1:]:
    msgsSum2 += pplStat[3][0]
if msgsSum1 != msgsSum2:
    logging.warning("sum of all participants' messages (" + str(msgsSum2) + ") is different from the total number of messages (" + str(msgsSum1) + ").")
    warnings += 1


# some verification on total amount of given reactions
reactsGivenSum = 0
for pplStat in pplStats[1:]:
    for k in range(8):
        reactsGivenSum += pplStat[2][k]

if reactsCounter != reactsGivenSum:
    logging.warning("sum of all participants' given reactions (" + str(reactsGivenSum) + ") is different from the total number of given reactions (" + str(reactsCounter) + "): "
                    "this can be due to a participant added to the conversation after the first message.")
    warnings += 1


# some verification on total amount of received reactions
reactsReceivedSum = 0
for pplStat in pplStats[1:]:
    for k in range(8):
        reactsReceivedSum += pplStat[1][k]

if reactsCounter != reactsReceivedSum:
    logging.warning("sum of all participants' received reactions (" + str(reactsReceivedSum) + ") different from total number of received reactions (" + str(reactsCounter) + "): "
                    "this can be due to a participant added to the conversation after the first message.")
    warnings += 1

if reactsErrors != 0:
    logging.warning(str(reactsErrors) + " errors related to reactions. Some reactions haven't been identified.")
    warnings += 1

# Computation of some reacts-related quantities
for pplStat in pplStats[1:]:
    pplStat[1][8] = sum(k for k in pplStat[1][0:8])  # number of received reacts
    pplStat[1][10] = round_half_up(pplStat[1][9] / pplStat[3][0], 2)  # reacted messages/message ratio
    pplStat[1][11] = round_half_up(pplStat[1][8] / pplStat[3][0], 2)  # reacts received/messages sent

    pplStat[2][8] = sum(k for k in pplStat[2][0:8])  # number of given reacts
    pplStat[2][9] = round_half_up(pplStat[2][8] / msgsSum1, 3)  # reacts given/message ratio
    pplStat[3][3] = round_half_up(pplStat[3][2] / pplStat[3][0], 2)  # words/message


# initialize final results csv matrix
csvMatrix = [[list(i) for i in zip(*pplStats)][0], [''] * (nbPeople + 1)]

# copy [total amount of messages, total length of all messages (without spaces), total amount of words, words/messages ratio]
# to csvMatrix
for statIndex in range(1, 5):
    csvMatrix.append([pplStats[0][statIndex + 22]] + [0] * nbPeople)

    for pplIndex in range(1, nbPeople + 1):
        csvMatrix[statIndex + 1][pplIndex] = pplStats[pplIndex][3][statIndex - 1]

csvMatrix.append([''] * (nbPeople + 1))
csvMatrix.append(['RECEIVED REACTIONS :'] + [''] * nbPeople)

# copy received reacts statistics to csvMatrix
for statIndex in range(1, 13):
    csvMatrix.append([pplStats[0][statIndex]] + [0] * nbPeople)

    for pplIndex in range(1, nbPeople + 1):
        csvMatrix[statIndex + 7][pplIndex] = pplStats[pplIndex][1][statIndex - 1]

csvMatrix.append([''] * (nbPeople + 1))
csvMatrix.append(['GIVEN REACTIONS :'] + [''] * nbPeople)

# copy given reacts statistics to csvMatrix
for statIndex in range(1, 11):
    csvMatrix.append([pplStats[0][statIndex + 12]] + [0] * nbPeople)
    for pplIndex in range(1, nbPeople + 1):
        b = pplStats[pplIndex][2][statIndex - 1]
        csvMatrix[statIndex + 21][pplIndex] = pplStats[pplIndex][2][statIndex - 1]

csvMatrix.append([''] * (nbPeople + 1))
csvMatrix.append([''] * (nbPeople + 1))

# creates rows lines for amounts of reacted messages for every amount of received reacts
for i in range(len(reactsTable[0][1])):  # 0 to 8
    l1 = ['msgs with ' + str(i + 1) + ' reaction(s)']
    l2 = [pplStats[j + 1][4][i] for j in range(nbPeople)]
    csvMatrix.append(l1 + l2)


# saving output files

with open(output_path + "subscribe.txt", "w") as txt_file:
    for line in subscribetable:
        txt_file.write("%s\n" % line)

with open(output_path + "results.csv", 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerows(csvMatrix)

with open(output_path + "timeTable.csv", 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(timeTable[0])
    for index in range(1, len(timeTable)):
        filewriter.writerow(timeTable[len(timeTable) - index])

with open(output_path + "dailyTimeTable.csv", 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerows(dailyTimeTable)


print("Script is over. " + str(warnings) + " warning(s), see logfile for further details.")
logging.info("end of script. Total warnings: " + str(warnings) + ".")