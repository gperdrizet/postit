#!/bin/bash

# Authenticate session to HuggingFace so we can download gated models if needed
python3 -c "from huggingface_hub.hf_api import HfFolder; HfFolder.save_token('$HF_TOKEN')"

# Start the API with Gunicorn
gunicorn -w 1 --bind $FLASK_IP:$FLASK_PORT 'model:flask_app'