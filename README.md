## AI无限对话程序说明
### 如果你有什么好的优化建议，请指出
### 运行原理
#### 整体架构
本程序是一个基于 PyQt5 框架的仿Mac聊天窗口应用，主要由两个核心类 ApiWorker 和 ChatWindow 组成。ApiWorker 类继承自 QThread，用于在单独的线程中处理与 API 的交互；ChatWindow 类继承自 QWidget，负责构建聊天窗口的界面和处理用户的输入与消息显示。
####  ApiWorker 类
##### 信号定义：
`chunk_received`信号用于在接收到 API 返回的文本块时发送数据到主线程，以便在聊天窗口中显示。
`finished` 信号在 API 请求完成时发送，通知主线程请求已结束。
`error` 信号在发生异常时发送，将错误信息传递给主线程。
初始化方法：
`__init__` 方法接收 messages 参数，调用父类的初始化方法并保存 messages，用于后续的 API 请求。
##### 运行方法：
`run` 方法是线程的执行逻辑。它设置了 API 的 URL、请求头和请求数据，然后使用 requests.post 方法发送 POST 请求。
对于响应，使用 iter_lines 逐行处理响应数据，将每一行解码后通过 `chunk_received` 信号发送。
如果发生异常，通过 error 信号发送异常信息，并在最后发送 finished 信号。
#### ChatWindow 类
##### 初始化方法：
`__init__` 方法调用父类的初始化方法，初始化 `messages` 列表，并调用 `initUI` 方法来构建用户界面。
##### 界面初始化方法：
initUI 方法设置窗口的样式和标志（无边框），创建顶部控制栏（包括关闭、最小化和最大化按钮），主布局，聊天显示区域（QTextEdit），输入区域（QTextEdit 和发送按钮）。
为每个组件设置相应的样式和连接相应的信号槽，如关闭按钮连接到 close 方法，最小化按钮连接到 showMinimized 方法等。
发送消息方法：
`send_message` 方法获取用户输入，记录用户消息并显示在聊天窗口中。
禁用发送按钮以防止重复点击，初始化当前响应和缓冲区。
创建 ApiWorker 实例，连接 chunk_received、finished 和 error 信号到相应的处理方法，并启动线程。
鼠标事件处理方法：
`mousePressEvent` 方法在鼠标左键按下时记录鼠标位置。
`mouseMoveEvent` 方法在鼠标移动且左键按下时移动窗口位置。
##### 信号处理方法：
`on_chunk_received` 方法使用 rich 模块处理接收到的 Markdown 格式的文本块，并将其插入到聊天显示区域，同时滚动到聊天显示区域的底部。
on_api_finished 方法在 API 请求完成时启用发送按钮。
on_api_error 方法在 API 请求发生错误时启用发送按钮，并在聊天显示区域显示错误信息。
### 运行方法
（一）安装依赖
确保已经安装了 PyQt5、requests 和 rich 库。可以使用 pip 进行安装：
```bash
pip install PyQt5 requests rich
```


### 运行代码
将代码下载，main.py。
在命令行中进入保存文件的目录。
运行以下命令：
```bash
python main.py
```

## 作者
cc-Infiltration
