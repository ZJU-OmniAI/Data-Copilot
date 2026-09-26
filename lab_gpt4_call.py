import openai
import tiktoken
import os
import time
from functools import wraps

import threading


def retry(exception_to_check, tries=3, delay=5, backoff=1):
    """
    Decorator used to automatically retry a failed function. Parameters:

    exception_to_check: The type of exception to catch.
    tries: Maximum number of retry attempts.
    delay: Waiting time between each retry.
    backoff: Multiplicative factor to increase the waiting time after each retry.
    """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    print(f"{str(e)}, Retrying in {mdelay} seconds...")
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

def timeout_decorator(timeout):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]  # Nonlocal mutable variable
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout)
            if thread.is_alive():
                # Raise instead of calling wrapper() again: the recursion retried forever when the API kept timing out.
                # The retry decorator decides whether to try again.
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")
            if isinstance(result[0], Exception):
                raise result[0]
            return result[0]
        return wrapper
    return decorator


# Errors worth retrying. A wrong key or an invalid request fails at once instead of being retried for hours.
TRANSIENT_ERRORS = (openai.error.RateLimitError, openai.error.APIError, openai.error.APIConnectionError,
                    openai.error.ServiceUnavailableError, openai.error.Timeout, TimeoutError)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    print('num_tokens:',num_tokens)
    return num_tokens

@retry(TRANSIENT_ERRORS, tries=10, delay=20, backoff=2)
@timeout_decorator(45)
def send_chat_request_Azure(query, openai_key, api_base, engine):
    max_token_num = 8000 - num_tokens_from_string(query,'cl100k_base')

    # The credentials are passed per request instead of being written to openai.api_type / api_base / api_key:
    # those module-level settings are shared by all users of the web demo and leaked into later official-API calls.
    response = openai.ChatCompletion.create(
        engine = engine,
        messages=[{"role": "system", "content": "You are an useful AI assistant that helps people solve the problem step by step."},
                  {"role": "user", "content": "" + query}],
        temperature=0.0,
        max_tokens=max_token_num,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        api_type="azure",
        api_version="2023-03-15-preview",
        api_base=api_base,
        api_key=openai_key)



    data_res = response['choices'][0]['message']['content']
    return data_res
#Note: The openai-python library support for Azure OpenAI is in preview.



@retry(TRANSIENT_ERRORS, tries=10, delay=20, backoff=2)
@timeout_decorator(45)
def send_official_call(query, openai_key='', api_base='', engine=''):
    start = time.time()
    # 转换成可阅读的时间
    start = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))
    print(start)

    response = openai.ChatCompletion.create(
        # engine="gpt35",
        model="gpt-3.5-turbo",
        messages = [{"role": "system", "content": "You are an useful AI assistant that helps people solve the problem step by step."},
                  {"role": "user", "content": "" + query}],
        #max_tokens=max_token_num,
        temperature=0.1,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        api_key=openai_key)  # per request, so that concurrent users of the web demo do not overwrite each other's key

    data_res = response['choices'][0]['message']['content']
    return data_res








