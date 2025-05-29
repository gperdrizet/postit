'''Main script to launch PostIt app.'''


import gradio as gr

def greet(name):
    return "Hello " + name + "!"


if __name__ == '__main__':

    demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")
    demo.launch(share=True)
