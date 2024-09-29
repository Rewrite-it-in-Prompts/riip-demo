#
# Minimalistic LLM CLI. 
#
import boto3
import json
import sys

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
output_file = sys.argv[1]
prompt = '\n\n'.join([open(arg).read() for arg in sys.argv[2:]])

response = bedrock.invoke_model(modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                                body=json.dumps({
                                    'anthropic_version': 'bedrock-2023-05-31', 
                                    'max_tokens': 8000, 
                                    'temperature': 0.5, 
                                    'system': 'You are a genius Software Developer who can solve even the most complex problems with extremely efficient and well-documented code. Wrap your output in HTML <pre> tags.',
                                    'messages': [ {
                                        'role': 'user', 'content': prompt
                                    } ]
                                }))

body = json.load(response['body'])

with open(output_file, "w", encoding="utf-8") as f:
    f.write(body['content'][0]['text'])
