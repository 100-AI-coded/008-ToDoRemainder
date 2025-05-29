import os
import win32gui
import win32con
import msvcrt
import tempfile
import win32process
import win32api
import time

def get_app_data_dir():
    """获取应用程序数据目录"""
    # 获取用户的文档目录
    documents_dir = os.path.expanduser("~/Documents")
    # 在文档目录下创建应用程序数据目录
    app_data_dir = os.path.join(documents_dir, "ToDoRemainder")
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    return app_data_dir

def find_running_window():
    """查找已经运行的程序窗口"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "待办事项提醒" in title:
                windows.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

def is_already_running():
    """检查程序是否已经运行"""
    # 在临时目录创建锁文件
    lock_file = os.path.join(tempfile.gettempdir(), "ToDoRemainder.lock")
    
    try:
        # 尝试以独占方式打开文件
        file_handle = os.open(lock_file, os.O_CREAT | os.O_RDWR)
        # 尝试获取文件锁
        msvcrt.locking(file_handle, msvcrt.LK_NBLCK, 1)
        
        # 如果成功获取锁，说明没有其他实例在运行
        return False
        
    except IOError:
        # 如果无法获取锁，说明程序已经在运行
        try:
            # 查找并激活已存在的窗口
            windows = find_running_window()
            if windows:
                hwnd = windows[0]
                try:
                    # 如果窗口最小化，先恢复
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    
                    # 获取窗口线程ID和进程ID
                    thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
                    
                    # 获取当前线程ID
                    current_thread = win32api.GetCurrentThreadId()
                    
                    # 如果线程ID不同，才需要附加线程输入
                    if thread_id != current_thread:
                        # 临时附加线程输入
                        win32process.AttachThreadInput(current_thread, thread_id, True)
                        try:
                            # 激活窗口
                            win32gui.SetForegroundWindow(hwnd)
                            # 将窗口提升到最前
                            win32gui.BringWindowToTop(hwnd)
                            # 给窗口一些时间来响应
                            time.sleep(0.1)
                        finally:
                            # 确保分离线程输入
                            win32process.AttachThreadInput(current_thread, thread_id, False)
                    else:
                        # 如果线程ID相同，直接激活窗口
                        win32gui.SetForegroundWindow(hwnd)
                        win32gui.BringWindowToTop(hwnd)
                except Exception as e:
                    print(f"激活窗口时出错: {str(e)}")
        except Exception as e:
            print(f"查找窗口时出错: {str(e)}")
        return True
        
    except Exception as e:
        print(f"检查程序运行状态时出错: {str(e)}")
        return False 