
import json
import zipfile
import os
import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = 'FILL_THIS_IN'
PREFIX = 'FILL_THIS_IN'

# Function below unzips the archive to the local directory. 

def unzip_data(input_data_path):
    with zipfile.ZipFile(input_data_path, 'r') as input_data_zip:
        input_data_zip.extractall('/tmp/')
        return '/tmp/' + input_data_zip.namelist()[0]

# Input data is a file with a single JSON object per line with the following format: 
# {
#  "reviewerID": <string>,
#  "asin": <string>,
#  "reviewerName" <string>,
#  "helpful": [
#    <int>, (indicating number of "helpful votes")
#    <int>  (indicating total number of votes)
#  ],
#  "reviewText": "<string>",
#  "overall": <int>,
#  "summary": "<string>",
#  "unixReviewTime": <int>,
#  "reviewTime": "<string>"
# }
# 
# We are specifically interested in the fields "helpful" and "reviewText"
#

def label_data(input_data):
    labeled_data = []
    HELPFUL_LABEL = "__label__1"
    UNHELPFUL_LABEL = "__label__2"
     
    for l in open(input_data, 'r'):
        l_object = json.loads(l)
        helpful_votes = float(l_object['helpful'][0])
        total_votes = l_object['helpful'][1]
        reviewText = l_object['reviewText']
        if total_votes != 0:
            if helpful_votes / total_votes > .5:
                labeled_data.append(" ".join([HELPFUL_LABEL, reviewText]))
            elif helpful_votes / total_votes < .5:
                labeled_data.append(" ".join([UNHELPFUL_LABEL, reviewText]))
          
    return labeled_data


# Labeled data is a list of sentences, starting with the label defined in label_data. 

def split_sentences(labeled_data):
    new_split_sentences = []
    for d in labeled_data:
        label = d.split()[0]        
        sentences = " ".join(d.split()[1:]).split(".") # Initially split to separate label, then separate sentences
        for s in sentences:
            if s: # Make sure sentences isn't empty. Common w/ "..."
                new_split_sentences.append(" ".join([label, s]))
    return new_split_sentences

def upload_data(file_name):
    object_name = os.path.join(PREFIX, os.path.basename(file_name))
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, BUCKET_NAME, object_name)
    except ClientError as e:
        logging.error(e)
        return False

def write_data(data, b_name, proportion):
    train_path = '/tmp/' + b_name + '_train'
    test_path = '/tmp/' +  b_name + '_test'
    border_index = int(proportion * len(data))
    train_f = open(train_path, 'w')
    test_f = open(test_path, 'w')
    index = 0
    for d in data:
        if index < border_index:
            train_f.write(d + '\n')
        else:
            test_f.write(d + '\n')
        index += 1
    train_f.close()
    test_f.close()
    upload_data(train_path)
    upload_data(test_path)

def download_data(s3_input_uri):
    s3 = boto3.client('s3')
    input_bucket = s3_input_uri.split('/')[0]
    input_object = '/'.join(s3_input_uri.split('/')[1:])
    file_name = '/tmp/' + os.path.basename(input_object)
    s3.download_file(input_bucket, input_object, file_name)
    return file_name
        
def preprocess(s3_input_uri):
    f_name = download_data(s3_input_uri)
    unzipped_path = unzip_data(f_name)
    labeled_data = label_data(unzipped_path)
    new_split_sentence_data = split_sentences(labeled_data)
    write_data(new_split_sentence_data, os.path.basename(s3_input_uri), .9)

