import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QScrollBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import requests
from rich.markdown import Markdown
from rich.console import Console
from io import StringIO

class ApiWorker(QThread):
    chunk_received = pyqtSignal(str)  # 定义信号，用于发送接收到的文本块
    finished = pyqtSignal()  # 定义信号，用于发送完成信号
    error = pyqtSignal(str)  # 定义信号，用于发送错误信息
    
    # 接收messages作为参数
    def __init__(self, messages): 
        super().__init__()  # 调用父类的初始化方法
        self.messages = messages
    
    def run(self): # 重写run方法，定义线程的执行逻辑
        try:
            url = "https://api.binjie.fun/api/generateStream"
            headers = {
                "Content-Type": "application/json",
                "Origin": "chat18.aichatos.xyz",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
            }
            data = {
                "prompt": self.messages[-1]['content'],
                "userId": "#/chat/master",
                "network": True
            }
            response = requests.post(url, json=data, headers=headers, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines(decode_unicode=False):
                if line:
                    decoded_line = line.decode('utf-8')  # 解码 bytes 为字符串
                    self.chunk_received.emit(decoded_line)
            
            self.finished.emit()  # 发送完成信号
        except Exception as e:  # 捕获异常
            self.error.emit(str(e))  # 发送错误信息
            self.finished.emit()  # 发送完成信号

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.initUI()
        self.url = "https://api.binjie.fun/api/generateStream"
        self.headers = {
            "Content-Type": "application/json",
            "Origin": "chat18.aichatos.xyz",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框窗口
        self.setStyleSheet("background-color: #1C1C1E; color: #F2F2F7;")  # 设置窗口背景颜色和字体颜色

        # 顶部控制栏
        top_layout = QHBoxLayout()  # 水平布局
        top_layout.setContentsMargins(0, 0, 0, 0)  # 设置边距

        # 窗口控制按钮
        close_button = QPushButton("×")  # 关闭按钮
        close_button.setFixedSize(20, 20)  # 设置按钮大小
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF453A;
                border-radius: 10px;
                font-size: 14px;
                color: transparent;
            }
            QPushButton:hover {
                background-color: #E83B30;
                color: white;
            }
        """)
        close_button.clicked.connect(self.close)  # 连接按钮点击事件到关闭窗口方法
        top_layout.addWidget(close_button)  # 添加按钮到布局

        minimize_button = QPushButton("─")  # 最小化按钮
        minimize_button.setFixedSize(20, 20)  # 设置按钮大小
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #FFBC00;
                border-radius: 10px;
                font-size: 14px;
                color: transparent;
            }
            QPushButton:hover {
                background-color: #E6A800;
                color: white;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)  # 连接按钮点击事件到最小化窗口方法
        top_layout.addWidget(minimize_button)  # 添加按钮到布局

        maximize_button = QPushButton("+")  # 最大化按钮
        maximize_button.setFixedSize(20, 20)  # 设置按钮大小
        maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                border-radius: 10px;
                font-size: 14px;
                color: transparent;
            }
            QPushButton:hover {
                background-color: #2DA54E;
                color: white;
            }
        """)
        maximize_button.clicked.connect(self.showMaximized)  # 连接按钮点击事件到最大化窗口方法 
        top_layout.addWidget(maximize_button)  # 添加按钮到布局

        top_layout.addStretch()  # 添加伸缩项，用于将按钮推到右侧

        # 主布局
        main_layout = QVBoxLayout()  # 垂直布局
        main_layout.addLayout(top_layout)  # 添加顶部布局到主布局

        # 聊天显示区域
        self.chat_display = QTextEdit()  # 文本编辑框
        self.chat_display.setReadOnly(True)  # 设置为只读，禁止用户编辑
        self.chat_display.setWordWrapMode(True)  # 自动换行

        # 优化的滚动条样式
        scroll_bar = QScrollBar()  # 创建滚动条对象
        scroll_bar.setStyleSheet("""
            QScrollBar:vertical {
                background: #2C2C2E;
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #545458;
                min-height: 20px;
                border-radius: 5px;
            }
        """)
        self.chat_display.setVerticalScrollBar(scroll_bar)  # 设置垂直滚动条

        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2C2C2E;
                border: 1px solid #3A3A3C;
                border-radius: 10px;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 30px;
            }
            .user-message {
                background-color: #007AFF;
                color: white;
                border-radius: 10px;
                padding: 8px 12px;
                margin: 5px;
                float: right;
                clear: both;
                max-width: 70%;
                word-wrap: break-word;
            }
            .assistant-message {
                background-color: #3A3A3C;
                color: white;
                border-radius: 10px;
                padding: 8px 12px;
                margin: 5px;
                float: left;
                clear: both;
                max-width: 70%;
                word-wrap: break-word;
            }
            .typing-cursor {
                animation: blink 1s infinite;
            }
            pre {
                background-color: #2D2D2D;
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
                overflow-x: auto;
            }
            code {
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                color: #A9B7C6;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0; }
            }
        """)
        main_layout.addWidget(self.chat_display)  # 添加文本编辑框到主布局

        # 输入区域
        input_layout = QHBoxLayout()  # 水平布局
        self.input_field = QTextEdit()  # 文本编辑框
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #2C2C2E;
                border: 1px solid #3A3A3C;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 20px;
            }
        """)
        self.input_field.setFixedHeight(60)  # 设置固定高度
        input_layout.addWidget(self.input_field)  # 添加文本编辑框到输入布局
        self.input_field.setPlaceholderText("今天聊点什么...")  # 设置占位文本
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏垂直滚动条
        self.input_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏水平滚动条
        self.send_button = QPushButton("发送")  # 发送按钮
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 10px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
            QPushButton:pressed {
                background-color: #0052A3;
            }
            QPushButton:disabled {
                background-color: #545458;
            }
        """)
        self.send_button.clicked.connect(self.send_message)  # 连接按钮点击事件到发送消息方法
        input_layout.addWidget(self.send_button)  # 添加按钮到输入布局

        main_layout.addLayout(input_layout)  # 添加输入布局到主布局
        self.setLayout(main_layout)  # 设置窗口布局
        self.setWindowTitle('Chat with GPT')
        self.setGeometry(300, 300, 800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

    def send_message(self):
        user_input = self.input_field.toPlainText().strip()  # 获取用户输入并去除空格
        if not user_input:
            self.chat_display.append('<div class="assistant-message"></div>')   
        
        # 记录用户消息并显示
        self.messages.append({"role": "user", "content": user_input})  # 将用户消息添加到消息列表
        user_html = f'<div class="user-message">你: {user_input}</div>'  # 格式化用户消息为HTML
        self.chat_display.append(user_html)  # 在聊天显示区域添加用户消息
        self.input_field.clear()  # 清空输入框

        # 禁用发送按钮防止重复点击
        self.send_button.setEnabled(False)  # 设置按钮为禁用状态

        # 初始化当前响应
        self.current_response = "AI: "  # 设置当前响应的前缀
        self.buffer = []  # 清空缓冲区

        # 在聊天窗口中添加空的助手消息容器
        self.chat_display.append('<div class="assistant-message"></div>')   
        self.current_message_id = self.chat_display.document().lastBlock().blockNumber()  # 获取最后一个消息的ID

        # 在单独的线程中执行API调用
        self.api_worker = ApiWorker(self.messages)  # 创建API工作线程
        self.api_worker.chunk_received.connect(self.on_chunk_received)  # 连接接收到文本块的信号到处理方法 
        self.api_worker.finished.connect(self.on_api_finished)  # 连接完成信号到完成处理方法
        self.api_worker.error.connect(self.on_api_error)  # 连接错误信号到错误处理方法
        self.api_worker.start()
        
        if user_input == 'exit':
            sys.exit()
        elif user_input == 'clear':
            self.chat_display.clear()
            self.input_field.clear()
            return

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def on_chunk_received(self, chunk):
        # 使用rich模块处理Markdown并启用代码高亮
        console = Console(file=StringIO(), force_terminal=True, width=60)
        md = Markdown(chunk, code_theme="monokai")
        console.print(md)
        html_chunk = console.file.getvalue()
        html_chunk = html_chunk.replace('<pre>', '<pre class="code-block">')
        # 使用 QTextCursor 追加新的文本块到当前消息
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(html_chunk)
        self.chat_display.setTextCursor(cursor)
        # 滚动到聊天显示区域的底部
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def on_api_finished(self):
        # 启用发送按钮
        self.send_button.setEnabled(True)
        def mousePressEvent(self, event):
            # 此处可添加方法的具体实现代码
            pass

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def on_api_error(self, error):
        # 启用发送按钮
        self.send_button.setEnabled(True)
        # 在聊天显示区域显示错误信息
        error_html = f'<div class="assistant-message">AI错误: {error}</div>'
        self.chat_display.append(error_html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatWindow()
    sys.exit(app.exec_())
