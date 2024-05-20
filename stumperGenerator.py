#!/usr/bin/env python3

import csv
import sys
import random


def parse_subjects(json_file):
    parsed_subjects = []
    print("Parsing subjects...")
    for subject in json_file:
        # Remove all the Sujet Stumper N objects from the subject
        for key in list(subject.keys()):
            if key.startswith('Sujet Stumper'):
                del subject[key]
        # Remove the empty keys
        subject = {key: value for key, value in subject.items() if value}
        parsed_subjects.append(subject)
    print(parsed_subjects)
    make_groups(parsed_subjects)


def save_groups(groups):
    # Order the groups by master login
    groups.sort(key=lambda group: group[0]['Login'])
    print("Groups: ", groups)
    print("Saving groups...")
    with open(sys.argv[2], mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['master', 'member0', 'common_subjects'])
        for group in groups:
            # Find all the subjects in common between the two members except the key Login
            common_subjects = set(group[0].keys()).intersection(set(group[1].keys()))
            common_subjects.discard("Login")
            if len(group) > 2:
                common_subjects = common_subjects.intersection(set(group[2].keys()))
                writer.writerow([group[0]['Login'], group[1]['Login'], group[2]['Login'],  common_subjects])
            else:
                writer.writerow([group[0]['Login'], group[1]['Login'], common_subjects])
    print(f"Output written to {sys.argv[2]}")


def make_groups(parsed_subjects):
    print("Making groups...")
    groups = []
    # Keep track of used logins
    used_logins = []
    # Shuffle to introduce randomness
    random.shuffle(parsed_subjects)
    print("Shuffled subjects: ")
    print(parsed_subjects)
    for i in range(len(parsed_subjects)):
        for j in range(i+1, len(parsed_subjects)):
            subjects_i = set(parsed_subjects[i].keys())
            subjects_j = set(parsed_subjects[j].keys())
            common_subjects = subjects_i.intersection(subjects_j)
            # Ensure common subjects criteria
            if len(common_subjects) > 6 and parsed_subjects[i]['Login'] not in used_logins and parsed_subjects[j]['Login'] not in used_logins:
                group = [parsed_subjects[i], parsed_subjects[j]]
                groups.append(group)
                used_logins.append(parsed_subjects[i]['Login'])
                used_logins.append(parsed_subjects[j]['Login'])
    # If there's one member left, add them to an existing pair to make it a trio
    if len(parsed_subjects) % 2 != 0:
        # Find an existing pair with at least 6 common subjects
        for group in groups:
            if len(set(group[0].keys()).intersection(set(parsed_subjects[-1].keys()))) > 6:
                group.append(parsed_subjects[-1])
                break
        else:
            # If no existing pair is found, create a new single-member group
            groups.append([parsed_subjects[-1]])
    save_groups(groups)


def main(input_csv, output_csv):
    subject_list = []
    # Load the list of valid logins from the input CSV
    with open(input_csv, mode='r', newline='') as file:
        reader = csv.DictReader(file, delimiter=';')
        valid_logins = set(row['Login'] for row in reader)
    print(valid_logins)
    with open(input_csv, mode='r', newline='') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            # Extract members from the row, filtering out empty values
            login = row.get('Login')
            # If all members are in the valid logins, add the group
            if login in valid_logins:
                subject_list.append(row)
                valid_logins.remove(login)
    print(subject_list)
    parse_subjects(subject_list)



if len(sys.argv) == 3:
    print("Processing...")
    main(sys.argv[1], sys.argv[2])
else:
    print("Usage: stumperGenerator.py <liste_sujet_csv_path> <output_csv_path>")
    sys.exit(1)
