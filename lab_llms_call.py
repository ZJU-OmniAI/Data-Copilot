import os
from http import HTTPStatus
import dashscope

# API keys are read from environment variables:
#   DASHSCOPE_API_KEY  Qwen / ChatGLM on DashScope, https://bailian.console.aliyun.com/
#   ZHIPUAI_API_KEY    GLM, https://open.bigmodel.cn/
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
def send_chat_request_qwen(query):
    '''
    You can generate API keys in https://bailian.console.aliyun.com/
    '''
    messages = [
        {'role': 'system', 'content': 'You are an useful AI assistant that helps people solve the problem step by step.'},
        {'role': 'user', 'content': query}]
    response = dashscope.Generation.call(
        'qwen-72b-chat',
        messages=messages,
        result_format='message',  
    )
    if response.status_code == HTTPStatus.OK:
        data_res = response['output']['choices'][0]['message']['content']
        #print(data_res)
        return data_res
    else:
        # raise instead of returning None, which main.py cannot parse
        raise RuntimeError('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        

def send_chat_request_chatglm3_6b(query):
    '''
    You can generate API keys in https://bailian.console.aliyun.com/
    '''
    messages = [
        {'role': 'system', 'content': 'You are an useful AI assistant that helps people solve the problem step by step.'},
        {'role': 'user', 'content': query}]
    response = dashscope.Generation.call(
        'chatglm3-6b',
        messages=messages,
        result_format='message',  
    )
    if response.status_code == HTTPStatus.OK:
        data_res = response['output']['choices'][0]['message']['content']
        print(data_res)
        return data_res
    else:
        # raise instead of returning None, which main.py cannot parse
        raise RuntimeError('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        

def send_chat_request_chatglm_6b(query):
    '''
    You can generate API keys in https://bailian.console.aliyun.com/
    '''
    messages = [
        {'role': 'system', 'content': 'You are an useful AI assistant that helps people solve the problem step by step.'},
        {'role': 'user', 'content': query}]
    response = dashscope.Generation.call(
        'chatglm-6b-v2',
        messages=messages,
        result_format='message',  
    )
    if response.status_code == HTTPStatus.OK:
        data_res = response['output']['choices'][0]['message']['content']
        # print(data_res)
        return data_res
    else:
        # raise instead of returning None, which main.py cannot parse
        raise RuntimeError('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
   
	
def send_chat_request_glm(query):
    '''
    You can generate API keys in https://open.bigmodel.cn/
    '''
    # Optional dependency (pip install zhipuai==2.0.1), imported here so that main.py works without it.
    # zhipuai 2.x needs pydantic 2, which the Gradio 3.34 web demo does not support: use a separate environment.
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY'))
    response = client.chat.completions.create(
        model="glm-3-turbo",  
        messages=[
        {'role': 'system', 'content': '你是一个有用的人工智能助手，帮助人们逐步解决问题.'},
        {'role': 'user', 'content': query}],
    )
    response=response.choices[0].message.content
    return response


      
if __name__ == '__main__':
    # response=send_chat_request_qwen("hello")
    response=send_chat_request_glm("你好")
    print(response)