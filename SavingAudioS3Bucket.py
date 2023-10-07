#!/usr/bin/env python
# coding: utf-8

# In[11]:


# AWS credentials and region
aws_access_key = 'AKIA3PSSEHU4WHI2K5L2'
aws_secret_key = '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'
aws_region = 'ap-south-1'


# In[10]:


import sounddevice as sd
import numpy as np
import boto3
from botocore.exceptions import NoCredentialsError

# Constants for recording and AWS S3
duration = 60
sampling_frequency = 44100
bucket_name = "sagemaker-studio-16ett2dlnfl"
s3_file_key = "audio_test_2.wav"

# Input AWS credentials
aws_access_key_id = aws_access_key
aws_secret_access_key = aws_secret_key

# Record audio from the user
print("Recording...")
is_recording = True
audio_data = []
while is_recording:
    # Record audio in a chunk
    chunk = sd.rec(int(duration * sampling_frequency), samplerate=sampling_frequency, channels=2)
    audio_data.append(chunk)

    # Check for user input to stop recording
    user_input = input("Press Enter to stop recording: ")
    if user_input == "":
        is_recording = False

# Convert the audio data to a NumPy array
audio_data = np.concatenate(audio_data)

# Upload the audio data to S3 directly
try:
    # Create an S3 client with provided credentials
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Upload the audio data as bytes directly to S3 bucket
    s3.put_object(Body=audio_data.tobytes(), Bucket=bucket_name, Key=s3_file_key)
    print(f"Audio data uploaded to S3 bucket: {bucket_name}/{s3_file_key}")

except NoCredentialsError:
    print("Invalid AWS credentials.")
except Exception as e:
    print(f"Error: {e}")


# In[19]:


import requests
import time
# Initialize the Amazon Transcribe client
transcribe_client = boto3.client('transcribe', 
    aws_access_key_id= aws_access_key,
    aws_secret_access_key = aws_secret_key,
    region_name = aws_region
)
# Specify the S3 URI of the audio file you want to transcribe
s3_uri = 's3://sagemaker-studio-16ett2dlnfl/sample_voice.wav'
# Define a job name for the transcription job
job_name = 'sample-job_3'
# Start the transcription job
transcribe_client.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': s3_uri},
    MediaFormat='wav',
    LanguageCode='en-US'  # Adjust the language code as needed
)
# Automatic wait loop
while True:
    # Retrieve the transcription results
    response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)

    job_status = response['TranscriptionJob']['TranscriptionJobStatus']
    # Check if the job has completed successfully
    if job_status == 'COMPLETED':    
        # Download the transcript file from S3
        transcript_s3_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_response = requests.get(transcript_s3_uri)
        break
#    else:
#        time.sleep(1)
import json

# Assuming transcript_response.content contains the JSON response
response_json = json.loads(transcript_response.content)

# Extract the transcript text
transcript = response_json["results"]["transcripts"][0]["transcript"]

# Print the transcript
print(transcript)
# List all transcription jobs
response = transcribe_client.list_transcription_jobs()
# Delete each transcription job
for job in response['TranscriptionJobSummaries']:
    job_name = job['TranscriptionJobName']
    transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
    print(f"Deleted job: {job_name}")

