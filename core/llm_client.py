#
# llm_client.py: Minimalistic LLM Client with defaults suitable for Code Generation
#

import os
import sys
import time
from typing import Dict, List, Tuple
import json
import uuid
import boto3
from botocore.config import Config
import yaml

models = [
    #model = "us.meta.llama3-2-1b-instruct-v1:0"
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-opus-20240229-v1:0"
]
DEFAULT_MODEL = 1

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2', config=Config(
    connect_timeout=300,  # seconds
    read_timeout=600      # seconds
))

DEFAULT_CONFIG = {
    'anthropic_version': 'bedrock-2023-05-31', 
    'max_tokens': 8000, 
    'temperature': 0.5
}

with open(os.path.join(os.path.dirname(__file__), 'base-prompt.json'), 'r') as f:
    base_prompt = json.load(f)

class CodingChat:
    def __init__(self, messages: List[Dict[str,str]] = base_prompt, level: int = DEFAULT_MODEL):

        self.messages = messages
        self.model = models[level]
        self.session = time.strftime("%Y-%m-%d/%H_%M/") + uuid.uuid4().hex[:8]  # useful for log debugging
        self.logfolder = ".llm_logs/" + self.session
        os.makedirs(self.logfolder, exist_ok=True)

    def invoke(self, user_prompt: str, filetype: str, system_prompt: str = None) -> Tuple[str, int, int, str]:
        """Invoke the LLM model with the given prompt and return the generated text and consumed token counts."""

        if not system_prompt:
            system_prompt = f"You are an expert developer of {filetype} files. You deliver complete solutions without placeholders. When fixing code, you repeat the entire file contents, to spare the user's hands from the pain of typing. Write the entire contents for the {filetype} file."

        self.messages.append({ 'role': 'user', 'content': user_prompt })

        config = { **DEFAULT_CONFIG, 'system': system_prompt, 'messages': self.messages }

        print(f"{self.session}: LLM call starting.", file=sys.stderr)
        started = time.time()

        response = bedrock.invoke_model(modelId=self.model, body=json.dumps(config))

        body = json.load(response['body'])
        (ni, no) = (body['usage']['input_tokens'], body['usage']['output_tokens'])

        content = body['content'][0]['text'].strip()
        self.messages.append({ 'role': 'assistant', 'content': content })

        print (f"{self.session}: {ni} in, {no} out, t={time.time()-started:.2f} seconds", file=sys.stderr)

        with open(f"{self.logfolder}/{time.time()}-{filetype}.yaml", "w") as f:
            yaml.dump({ 'session': self.session, 'input': config, 'output': body }, f, default_flow_style=False, sort_keys=False)

        return (content, ni, no, { 'input': config, 'output': body })

def invoke_model(user_prompt: str, system_prompt: str, filetype: str) -> Tuple[str, int, int, str]:

    return CodingChat(system_prompt).invoke(user_prompt, filetype)
