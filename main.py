import customtkinter as ctk
from customtkinter import CTkEntry, CTkButton, CTkFrame, CTkScrollableFrame
from tkinter import ttk, messagebox
import socketio
from datetime import datetime
import re

class TempMailApp:
    def __init__(self, root):
        self.root = root
        self.current_email_prefix = None  # 添加变量存储当前邮箱前缀
        self.root.title("Cursor重置工具")
        self.root.geometry("900x600")  # 增加窗口尺寸
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主容器
        self.main_container = CTkFrame(root)
        self.main_container.pack(padx=20, pady=20, fill="both", expand=True)
        
        # 标题
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Cursor 重置工具",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # 邮箱地址框架
        self.email_frame = CTkFrame(self.main_container)
        self.email_frame.pack(padx=10, pady=10, fill="x")
        
        self.email_label = ctk.CTkLabel(
            self.email_frame,
            text="临时邮箱地址",
            font=("Arial", 14)
        )
        self.email_label.pack(pady=(5, 0))
        
        self.email_var = ctk.StringVar(value="等待分配临时邮箱...")
        self.email_entry = CTkEntry(
            self.email_frame,
            textvariable=self.email_var,
            width=500,
            height=35,
            font=("Arial", 13)
        )
        self.email_entry.pack(pady=10)
        
        # 按钮框架
        self.button_frame = CTkFrame(self.email_frame)
        self.button_frame.pack(pady=5)
        
        # 统一按钮样式
        button_width = 120
        button_height = 35
        button_font = ("Arial", 13)
        
        self.copy_btn = CTkButton(
            self.button_frame,
            text="复制邮箱",
            width=button_width,
            height=button_height,
            font=button_font,
            command=self.copy_email
        )
        self.copy_btn.pack(side="left", padx=5)
        
        self.refresh_btn = CTkButton(
            self.button_frame,
            text="刷新邮箱",
            width=button_width,
            height=button_height,
            font=button_font,
            command=self.get_new_email
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        self.reset_btn = CTkButton(
            self.button_frame,
            text="重置机器码",
            width=button_width,
            height=button_height,
            font=button_font,
            command=lambda: __import__('ResetMachineCode').reset_machine_code()
        )
        self.reset_btn.pack(side="left", padx=5)
        
        # 验证码列表框架
        self.code_frame = CTkScrollableFrame(
            self.main_container,
            label_text="验证码记录",
            label_font=("Arial", 14, "bold"),
            height=350
        )
        self.code_frame.pack(padx=10, pady=(20, 10), fill="both", expand=True)
        
        # 验证码文本框
        self.code_text = ctk.CTkTextbox(
            self.code_frame,
            height=300,
            font=("Arial", 13)
        )
        self.code_text.pack(fill="both", expand=True)
        self.code_text.configure(state="disabled")
        
        # 初始化 Socket.IO 客户端
        self.sio = socketio.Client()
        self.setup_socket_events()
        
        # 连接到服务器
        self.connect_to_server()

    def setup_socket_events(self):
        @self.sio.on('connect')
        def on_connect():
            print('已连接到服务器')
            if self.current_email_prefix:
                # 如果已有邮箱前缀，则重用它
                self.sio.emit('set shortid', self.current_email_prefix)
                # 直接更新UI显示，不等待服务器响应
                self.email_var.set(f"{self.current_email_prefix}@tempmail.cn")
            else:
                # 首次连接才请求新邮箱
                self.sio.emit('request shortid', True)
            
        @self.sio.on('disconnect')
        def on_disconnect():
            print('与服务器断开连接')
            self.email_var.set("连接已断开，正在重连...")
            # 确保socket实例被正确清理
            try:
                self.sio.disconnect()
            except:
                pass
            
        @self.sio.on('connect_error')
        def on_connect_error(error):
            print(f'连接错误: {error}')
            self.email_var.set("连接错误，正在重试...")
            # 确保socket实例被正确清理
            try:
                self.sio.disconnect()
            except:
                pass
            
        @self.sio.on('shortid')
        def on_shortid(id):
            if not self.current_email_prefix:  # 只在首次获取时保存
                self.current_email_prefix = id
            email = f"{id}@tempmail.cn"
            self.email_var.set(email)
            print(f"获取到临时邮箱地址: {email}")
            
        @self.sio.on('mail')
        def on_mail(mail):
            print("收到新邮件事件")
            self.add_mail_to_list(mail)

    def connect_to_server(self):
        try:
            # 设置连接选项
            self.sio = socketio.Client(
                reconnection=True,
                reconnection_attempts=0,  # 设为0表示无限重试
                reconnection_delay=1,     # 初始重连延迟1秒
                reconnection_delay_max=5, # 最大重连延迟5秒
                logger=True,
                engineio_logger=True
            )
            self.setup_socket_events()
            
            # 添加请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 连接服务器
            self.sio.connect(
                'https://tempmail.cn',
                headers=headers,
                transports=['websocket', 'polling']  # 允许降级到polling
            )
        except Exception as e:
            messagebox.showerror("错误", f"连接服务器失败：{str(e)}")
            print(f"详细错误信息: {str(e)}")
            # 5秒后自动重试连接
            self.root.after(5000, self.connect_to_server)

    def copy_email(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.email_var.get())

    def get_new_email(self):
        """刷新邮箱时清除当前邮箱前缀"""
        self.current_email_prefix = None
        self.sio.emit('request shortid', True)

    def copy_code(self, event):
        """双击复制验证码"""
        selected_item = self.code_tree.selection()
        if selected_item:
            code = self.code_tree.item(selected_item[0])['values'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("复制成功", f"验证码 {code} 已复制到剪贴板")

    def add_mail_to_list(self, mail):
        try:
            # 处理日期
            try:
                if isinstance(mail['headers']['date'], str):
                    date_str = mail['headers']['date']
                    try:
                        # 解析邮件日期字符串并格式化
                        from email.utils import parsedate_to_datetime
                        date_obj = parsedate_to_datetime(date_str)
                        time_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        time_str = date_str
                else:
                    # 处理时间戳
                    time_str = datetime.fromtimestamp(int(mail['headers']['date'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"日期处理错误: {e}")
                time_str = "未知时间"

            # 提取验证码
            verification_code = extract_verification_code(mail['html'])
            if verification_code:
                # 在文本框中添加验证码
                self.code_text.configure(state="normal")
                self.code_text.insert("1.0", f"验证码: {verification_code} | 时间: {time_str}\n")
                self.code_text.configure(state="disabled")
            
        except Exception as e:
            print(f"处理邮件时出错: {e}")
            print(f"邮件数据: {mail}")

    def on_closing(self):
        try:
            self.sio.disconnect()
        except:
            pass
        self.root.destroy()

    def set_custom_email(self):
        """设置自定义邮箱前缀"""
        custom_prefix = self.custom_entry.get().strip()
        if not custom_prefix:
            messagebox.showwarning("警告", "请输入邮箱前缀")
            return
            
        if not re.match(r'^[a-zA-Z0-9_-]+$', custom_prefix):
            messagebox.showwarning("警告", "邮箱前缀只能包含字母、数字、下划线和横线")
            return
            
        try:
            self.current_email_prefix = custom_prefix  # 保存自定义邮箱前缀
            self.sio.emit('set shortid', custom_prefix)
            self.email_var.set(f"{custom_prefix}@tempmail.cn")
            messagebox.showinfo("成功", "自定义邮箱设置成功")
        except Exception as e:
            messagebox.showerror("错误", f"设置自定义邮箱失败：{str(e)}")

def extract_verification_code(html_content):
    # 方法2：查找包含"one-time code"附近的6位数字
    pattern = r'one-time code is[:\s]+(\d{6})'
    match = re.search(pattern, html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None

if __name__ == "__main__":
    root = ctk.CTk()
    app = TempMailApp(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
