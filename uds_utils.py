# uds_utils.py
import threading

def handle_request_with_timeout(request, handler_func, timeout, on_timeout, *args, **kwargs):
    """
    以线程方式调用handler_func处理request，并在timeout秒后超时处理。
    
    参数:
    - request: 传入的请求对象
    - handler_func: 处理请求的函数，返回响应
    - timeout: 超时时间，单位秒
    - on_timeout: 超时回调，参数是request
    - *args, **kwargs: 传给handler_func的额外参数
    
    返回:
    - handler_func返回的响应，超时则返回None
    """
    result_container = {}

    def target():
        try:
            result_container['response'] = handler_func(request, *args, **kwargs)
        except Exception as e:
            print(f"[ERROR] Exception in handler_func: {e}")

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        on_timeout(request)
        return None
    return result_container.get('response')

