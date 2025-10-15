# uds_utils.py
import threading

def handle_request_with_timeout(request, handler_func, timeout, on_timeout, on_finish,*args, **kwargs):
    """
    以线程方式调用handler_func处理request，并在timeout秒后超时处理，处理结束后调用on_finish。
    
    参数:
    - request: 传入的请求对象
    - handler_func: 处理请求的函数，返回响应
    - timeout: 超时时间，单位秒
    - on_timeout: 超时回调，参数是request
    - on_finish: 处理完成回调，参数是response
    - *args, **kwargs: 传给handler_func的额外参数
    
    不返回结果，响应由回调处理
    """
    #result_container = {}
    finished_event = threading.Event()
    def target():
        try:
            response = handler_func(request, *args, **kwargs)
            finished_event.set()
            on_finish(response)
        except Exception as e:
            print(f"[ERROR] Exception in handler_func: {e}")
            finished_event.set()

    thread = threading.Thread(target=target)
    thread.start()
    #thread.join(timeout=timeout)
    def timeout_checker():
        if not finished_event.wait(timeout):
            on_timeout(request)
    threading.Thread(target=timeout_checker).start()

