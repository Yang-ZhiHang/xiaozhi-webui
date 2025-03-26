# xiaozhi-webui


## 项目简介
xiaozhi-webui 是一个使用 Python + Vue3 实现的小智语音 Web 端，旨在通过代码学习和在没有硬件条件下体验 AI 小智的对话功能。
本仓库是基于 [xiaozhi-web-client](https://github.com/TOM88812/xiaozhi-web-client) 使用 Vue3 重构的

## 环境要求
- Python 3.12.0
- Windows

## 演示
- [Bilibili 演示视频](https://www.bilibili.com/video/BV1HmPjeSED2/#reply255921347937)

![Image](https://github.com/user-attachments/assets/df8bd5d2-a8e6-4203-8084-46789fc8e9ad)
## 功能特点
- **语音交互**：支持语音输入与识别，实现智能人机交互。  
- **图形化界面**：提供直观易用的 GUI，方便用户操作。  
- **音量控制**：支持音量调节，适应不同环境需求。  
- **会话管理**：有效管理多轮对话，保持交互的连续性。  
- **加密音频传输**：保障音频数据的安全性，防止信息泄露。  
- **CLI 模式**：支持命令行运行，适用于嵌入式设备或无 GUI 环境。  
- **自动验证码处理**：首次使用时，程序自动复制验证码并打开浏览器，简化用户操作。  
- **唤醒词**：支持语音唤醒，免去手动操作的烦恼。  
- **键盘按键**：监听可以最小化视口

## 状态流转图

```
                        +---------------+
                        |               |
                        v               |
+------+   文字信息    +------------+    |   +------------+
| IDLE | -----------> | CONNECTING | ---+-> |  WS Server |
+------+              +------------+        +------------+
   ^                                            |
   |                                            | 文本信息+音频信息
   |                                            |
   |          +------------+                    v
   +--------- |  SPEAKING  | <-----------------+
     完成播放 +------------+
```

## 项目结构

```
├── backend                       # 后端代码
│   ├── libs                       
│   │   └── windows/opus.dll      # Windows 系统需要的音频编解码依赖库
│   ├── .env.example              # 环境变量配置示例文件
│   ├── app.py                    # 程序入口
│   ├── system_info.py            # Windows 处理 opus.dll 加载失败的函数
│   ├── websocket_proxy.py        # WebSocket 代理
│   └── requirements.txt          # 依赖库列表
├── frontend/xiaozhi-webui        # 前端代码
│   ├── public                       
│   │   └──  favicon.ico          # 网站图标
│   ├── src                  
│   |   ├── assets                # 静态资源，全局样式文件等
│   |   ├── stores                # Pinia 状态管理
│   |   ├── App.vue               # 根组件
│   |   └── main.ts               # 入口文件
│   ├── package.json              # 项目依赖配置
│   ├── tsconfig.json             # TypeScript 配置文件
│   ├── vite.config.ts            # Vite 配置文件
│   └── index.html                # 入口 HTML 文件
├── .gitignore                    # Git 忽略文件
├── LICENSE                       # 许可证文件
└── README.md                     # 项目说明文件
```

## 已实现功能

- **文字聊天模式**，像微信好友一样聊天  
- **自动获取 MAC 地址**，避免 MAC 地址冲突

## 待实现功能

- **语音对话**，和小智打电话

## 贡献

欢迎提交 Issues 和 Pull Requests！

## 感谢以下开源人员-排名不分前后
[Huang-junsen](https://github.com/Huang-junsen)

[TOM88812](https://github.com/TOM88812)