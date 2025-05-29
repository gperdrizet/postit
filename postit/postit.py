'''Main script to launch PostIt app.'''

import os
import time
import json
import urllib.request
import gradio as gr


def submit_text(string: str) -> str:

    '''Sends user's suspect text to scoring api, get's back a result id
    so we can poll and wait for the scoring backend to do it's thing.'''

    # Assemble the payload
    payload = {'text': string}
    json_payload = json.dumps(payload) # Explicitly converts to json
    json_bytes_payload = json_payload.encode('utf-8') # Encodes to bytes

    # Setup the request
    req = urllib.request.Request(
        f"http://{os.environ['FLASK_IP']}:{os.environ['FLASK_PORT']}/submit_text"
    )
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Content-Length', len(json_bytes_payload))

    # Submit the request
    body = urllib.request.urlopen(req, json_bytes_payload).read()

    # Read and parse the results
    contents = json.loads(body)

    # Collect the result id
    result_id = contents['result_id']

    return result_id


def retrieve_result(result_id: str = None) -> str:
    '''Polls for result id, returns result content'''

    while True:

        # Ask for the results from this id
        body = urllib.request.urlopen(
            f"http://{os.environ['FLASK_IP']}:{os.environ['FLASK_PORT']}/result/{result_id}"
        ).read()

        # Read and parse the results
        contents = json.loads(body)

        if contents['ready'] is True:

            print(contents)

            reply = contents['value']
            return reply

        # Wait before checking again
        time.sleep(0.1)


def summarize(string):
    '''Submits text for summarization, gets result ID and waits for job to finish,
    then returns result.'''

    result_id = submit_text(string)
    summary = retrieve_result(result_id)

    return summary



if __name__ == '__main__':

    with gr.Blocks() as postit:
        string_input = gr.Textbox(label='Input text')
        summary_output = gr.Textbox(label='Summary')
        submit_btn = gr.Button('Submit')
        submit_btn.click(fn=summarize, inputs=string_input, outputs=summary_output, api_name='summarize')

    postit.launch(share=True)
