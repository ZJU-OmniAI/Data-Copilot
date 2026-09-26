import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from io import BytesIO
from main import run, add_to_queue,gradio_interface
import io
import sys
import time
import os
import pandas as pd
OPENAI_KEY = None
css = """#col-container {max-width: 90%; margin-left: auto; margin-right: auto; display: flex; flex-direction: column;}
#header {text-align: center;}
#col-chatbox {flex: 1; max-height: min(750px, 100%);}
#label {font-size: 4em; padding: 0.5em; margin: 0;}
.scroll-hide {overflow-y: scroll; max-height: 100px;}
.wrap {max-height: 680px;}
.message {font-size: 3em;}
.message-wrap {max-height: min(700px, 100vh);}
body {
        background-color: #ADD8E6;
    }
"""

# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
# plt.rcParams['axes.unicode_minus'] = False

plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK']
plt.rcParams['axes.unicode_minus'] = False


example_stock =['给我画一下可孚医疗2022年年中到今天的股价','北向资金今年的每日流入和累计流入','看一下近三年宁德时代和贵州茅台的pb变化','画一下五粮液和泸州老窖从2019年年初到2022年年中的收益率走势','成都银行近一年的k线图和kdj指标','比较下沪深300,创业板指,中证1000指数今年的收益率','今年上证50所有成分股的收益率是多少']
example_economic =['中国过去十年的cpi走势是什么','过去五年中国的货币供应量走势,并且打印保存','我想看看现在的新闻或者最新的消息','我想看看中国近十年gdp的走势','预测中国未来12个季度的GDP增速']
example_fund =['易方达的张坤管理了几个基金','基金经理周海栋名下的所有基金今年的收益率情况','我想看看周海栋管理的华商优势行业的近三年来的的净值曲线','比较下华商优势行业和易方达蓝筹精选这两只基金的近三年的收益率']
example_company =['介绍下贵州茅台,这公司是干什么的,主营业务是什么','我想比较下工商银行和贵州茅台近十年的净资产回报率','今年一季度上证50的成分股的归母净利润同比增速分别是']

class Client:
    def __init__(self) -> None:
        self.OPENAI_KEY = OPENAI_KEY
        self.OPENAI_API_BASED_AZURE = None
        self.OPENAI_ENGINE_AZURE = None
        self.OPENAI_API_KEY_AZURE = None
        self.stop = False  # 添加停止标志

    def set_key(self, openai_key, openai_key_azure, api_base_azure, engine_azure):
        self.OPENAI_KEY = openai_key
        self.OPENAI_API_BASED_AZURE = api_base_azure
        self.OPENAI_API_KEY_AZURE = openai_key_azure
        self.OPENAI_ENGINE_AZURE = engine_azure
        return self.OPENAI_KEY, self.OPENAI_API_KEY_AZURE, self.OPENAI_API_BASED_AZURE, self.OPENAI_ENGINE_AZURE


    def run(self, messages):
        # The keys are None until the OK button is clicked
        openai_key = self.OPENAI_KEY or ''
        openai_key_azure = self.OPENAI_API_KEY_AZURE or ''
        if openai_key == '' and openai_key_azure == '':
            yield '', np.zeros((100, 100, 3), dtype=np.uint8), "Please set your OpenAI API key first!!!", pd.DataFrame()
        elif not openai_key.startswith('sk') and openai_key_azure == '':
            yield '', np.zeros((100, 100, 3), dtype=np.uint8), "Your openai key is incorrect!!!", pd.DataFrame()
        else:
            # self.stop = False
            gen = gradio_interface(messages, openai_key, openai_key_azure, self.OPENAI_API_BASED_AZURE or '', self.OPENAI_ENGINE_AZURE or '')
            while not self.stop:  #
                try:
                    yield next(gen)
                except StopIteration:
                    print("StopIteration")
                    break

            # yield from gradio_interface(messages, self.OPENAI_KEY)
        #return finally_text, img, output, df





with gr.Blocks() as demo:
    state = gr.State(value={"client": Client()})
    def change_textbox(query):
        # 根据不同输入对输出控件进行更新
        return gr.update(lines=2, visible=True, value=query)
    # 图片框显示

    with gr.Row():
        gr.Markdown(
        """
        # Hello Data-Copilot ! 😀 
        A powerful AI system connects humans and data.
        The current version only supports Chinese financial data, in the future we will support for other country data
        """)


    if not OPENAI_KEY:
        with gr.Row().style():
            with gr.Column(scale=0.9):
                gr.Markdown(
                    """
                    You can use gpt35 from openai or from openai-azure.
                    """)
                openai_api_key = gr.Textbox(
                    show_label=False,
                    placeholder="Set your OpenAI API key here and press Submit  (e.g. sk-xxx)",
                    lines=1,
                    type="password"
                ).style(container=False)

                with gr.Row():
                    openai_api_key_azure = gr.Textbox(
                        show_label=False,
                        placeholder="Set your Azure-OpenAI key",
                        lines=1,
                        type="password"
                    ).style(container=False)
                    openai_api_base_azure = gr.Textbox(
                        show_label=False,
                        placeholder="Azure-OpenAI api_base (e.g. https://zwq0525.openai.azure.com)",
                        lines=1,
                        type="password"
                    ).style(container=False)
                    openai_api_engine_azure = gr.Textbox(
                        show_label=False,
                        placeholder="Azure-OpenAI engine here (e.g. gpt35)",
                        lines=1,
                        type="password"
                    ).style(container=False)


                gr.Markdown(
                    """
                    It is recommended to use the Openai paid API or Azure-OpenAI service, because the free Openai API will be limited by the access speed and 3 Requests per minute (very slow).
                    """)


            with gr.Column(scale=0.1, min_width=0):
                btn1 = gr.Button("OK").style(height= '100px')

    with gr.Row():
        with gr.Column(scale=0.9):
            input_text = gr.inputs.Textbox(lines=1, placeholder='Please input your problem...', label='what do you want to find？')

        with gr.Column(scale=0.1, min_width=0):
            start_btn = gr.Button("Start").style(full_height=True)
            # end_btn = gr.Button("Stop").style(full_height=True)


    gr.Markdown(
        """
        # Try these examples  ➡️➡️
        """)
    with gr.Row():

        example_selector1 = gr.Dropdown(choices=example_stock, interactive=True,
                                        label="查股票 Query stock:", show_label=True)
        example_selector2 = gr.Dropdown(choices=example_economic, interactive=True,
                                       label="查经济 Query Economy:", show_label=True)
        example_selector3 = gr.Dropdown(choices=example_company, interactive=True,
                                       label="查公司 Query Company:", show_label=True)
        example_selector4 = gr.Dropdown(choices=example_fund, interactive=True,
                                        label="查基金 Query Fund:", show_label=True)



    def set_key(state, openai_api_key,openai_api_key_azure, openai_api_base_azure, openai_api_engine_azure):
        return state["client"].set_key(openai_api_key, openai_api_key_azure,openai_api_base_azure, openai_api_engine_azure)


    def run(state, chatbot):
        generator =  state["client"].run(chatbot)
        for solving_step, img, res, df in generator:
            # if state["client"].stop:
            #     print('Stopping generation')
            #     break
            yield solving_step, img, res, df


    # def stop(state):
    #     print('Stop signal received!')
    #     state["client"].stop = True




    with gr.Row():
        with gr.Column(scale=0.3, min_width="500px", max_width="500px", min_height="500px", max_height="500px"):
                Res = gr.Textbox(label="Summary and Result: ")
        with gr.Column(scale=0.7, min_width="500px", max_width="500px", min_height="500px", max_height="500px"):
            solving_step = gr.Textbox(label="Solving Step: ", lines=5)


    img = gr.outputs.Image(type='numpy')
    df = gr.outputs.Dataframe(type='pandas')
    with gr.Row():
        gr.Markdown(
            """
            [Tushare](https://tushare.pro/) provides financial data support for our Data-Copilot. 
            
            [OpenAI](https://openai.com/) provides the powerful Chatgpt model for our Data-Copilot.
            """)


    outputs = [solving_step ,img, Res, df]
    #设置change事件
    example_selector1.change(fn = change_textbox, inputs = example_selector1, outputs = input_text)
    example_selector2.change(fn = change_textbox, inputs = example_selector2, outputs = input_text)
    example_selector3.change(fn = change_textbox, inputs = example_selector3, outputs = input_text)
    example_selector4.change(fn = change_textbox, inputs = example_selector4, outputs = input_text)


    if not OPENAI_KEY:
        openai_api_key.submit(set_key, [state, openai_api_key, openai_api_key_azure,openai_api_base_azure, openai_api_engine_azure], [openai_api_key, openai_api_key_azure,openai_api_base_azure, openai_api_engine_azure])
        btn1.click(set_key, [state, openai_api_key, openai_api_key_azure,openai_api_base_azure, openai_api_engine_azure], [openai_api_key,openai_api_key_azure, openai_api_base_azure, openai_api_engine_azure])

    start_btn.click(fn = run, inputs = [state, input_text], outputs=outputs)
    # end_btn.click(stop, state)



demo.queue()
demo.launch()


