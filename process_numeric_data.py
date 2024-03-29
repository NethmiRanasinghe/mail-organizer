import csv
    
def process_sender(mail):
    common_words = ["com", "edu", "lk", "gmail", "yahoo", "org", "co", "noreply", "ai", ".", "-", "@", "ac"]
    for word in common_words:
        mail = mail.replace(word, '')

    return mail

def process_date(date):
    # the date is in DD/MM/YY format
    if "/" in date:
        splitted = date.split("/")
    elif "-" in date:
        splitted = date.split("-")
    else:
        splitted = [-1,-1,-1]

    return splitted

def process_time(time):
    if len(time) > 0:
        hour = time.split(":")[0]
    else:
        hour = -1
    return hour

def process_attachment_type2(attachments_list):
    possible_types = ["image", "pdf", "plain", "calendar"]
    types = set()
    #  ['text/calendar', 'application/ics']
    for type in attachments_list:
        type = type.strip()
        s = type.split("/")
        for item in s:
            if item in possible_types:
                types.add(item)

    if "image" in types:
        image = 1
    elif "pdf" in types:
        pdf = 1
    elif "plain" in types:
        plain = 1
    elif "calendar" in types:
        calendar = 1
    return image, pdf, calendar, plain

def process_attachment_type(attachments_list):
    possible_types = {"image", "pdf", "plain", "calendar"}
    type_counts = {"image": 0, "pdf": 0, "plain": 0, "calendar": 0}

    for attachment_type in attachments_list:
        attachment_type = attachment_type.strip().split("/")
        for item in attachment_type:
            if item in possible_types:
                type_counts[item] = 1

    return tuple(type_counts[type] for type in ("image", "pdf", "calendar", "plain"))

def process_label(labels):
    # defined_labels = {
    # "label_2384422765228743236": 0, # blog
    # "label_7076286195593857530": 1, # personla
    # "label_679974079456540465": 2, # useless
    # "label_1576816929730070722": 3, # likedin
    # "label_4412238560480658524": 4, # engother
    # "label_2911623360968692061": 5, # job
    # "label_8761630829536469935": 6, # engaca
    # "label_2207602746430786030": 7, # ocr
    # "label_7301506489304756691": 8, # fyp
    # "label_8947939715416931986": 9 # invitation
    # }

    defined_labels = {
    "label_6561999058034858804": 0, # blog
    "label_8689670485925259078": 1, # personl
    "label_815898682217517602": 2, # useless
    "label_3909871728411487861": 3, # likedin
    "label_6060744680453086327": 4, # engother
    "label_8007728044897221425": 5, # job
    "label_3262879159084288473": 9 # invitation
    }

    labels = labels.replace('[', '').replace(']', '').replace("'", '').split(",")
    
    for label in labels:
        label = label.strip().lower()
        if label in defined_labels:
            return defined_labels[label]
    return -1

unprocessed_dataset = "../email_data_other.csv"
x = 0
dataset = open(unprocessed_dataset, encoding="utf8")
attachments = set()

# Define column names
fieldnames = ['Image_Attachment', 'PDF_Attachment', 'Calendar_Attachment', 'Text_Attachment',
              'Year', 'Month', 'Date', 'Hour', 'Read', 'Thread', 'Attachment', 'Starred', 'Subscription', 'Forwarded',
              'Attachment_Count', 'Size', 'Sender', 'Label']

# Open the CSV file in write mode
with open('output_other.csv', 'w', newline='') as csvfile:
    # Create a CSV writer object
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write the header row
    writer.writeheader()

    # Iterate over each row in the CSV reader
    with open(unprocessed_dataset, newline='', encoding="utf8") as csvfile:

        # Create a CSV reader object
        csv_reader = csv.reader(csvfile, delimiter=',')

        # Read and process the first line separately
        columns = next(csv_reader)

        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Process attachment types
            attachment_types = process_attachment_type(row[16].replace('[', '').replace(']', '').replace("'", '').split(","))
            
            # Process date and time
            processed_date = process_date(row[4])
            month, date, year = map(int, processed_date)
            hour = int(process_time(row[3]))

            # Convert boolean values to integers
            read = 1 if row[7] else 0
            thread = 1 if row[8] else 0
            attachment = 1 if row[9] else 0
            starred = 1 if row[10] else 0
            subscription = 1 if row[12] else 0
            forwarded = 1 if row[15] else 0

            # Convert attachment count to integer
            attachment_count = int(row[17])
            size = int(row[11])

            # Process sender and label
            sender = process_sender(row[1])
            label = process_label(row[14])

            # Create a dictionary for the current row
            row_data = {
                'Sender': sender,
                'Year': year,
                'Month': month,
                'Date': date,
                'Hour': hour,
                'Read': read,
                'Starred': starred,
                'Subscription': subscription,
                'Forwarded': forwarded,
                'Attachment': attachment,                
                'Attachment_Count': attachment_count,
                'Image_Attachment': attachment_types[0],
                'PDF_Attachment': attachment_types[1],
                'Calendar_Attachment': attachment_types[3],
                'Text_Attachment': attachment_types[2],               
                'Thread': thread,
                'Size': size,
                'Label': label
            }
            
            # Write the row to the CSV file
            writer.writerow(row_data)
