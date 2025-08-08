# xiaozhi-webui

> 本项目供学习交流使用，如果有问题欢迎联系 zamyang@qq.com

## 项目简介

声明：「小智」项目起源于 [虾哥](https://github.com/78/xiaozhi-esp32) 之手。

本项目 xiaozhi-webui 是一个使用 Python + Vue3 实现的小智语音 Web 端，旨在通过代码学习和在没有硬件条件下体验 AI 小智的对话功能。

本仓库使用 Vue3 基于 [xiaozhi-web-client](https://github.com/TOM88812/xiaozhi-web-client) 进行重构，并进行了一定的优化和拓展。

小智美美滴头像取自 [小红书 @涂丫丫](http://xhslink.com/a/ZWjAcoOzvzq9)

## 演示

<div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
    <img src="./images/聊天.jpg" alt="聊天" style="width: 45%;">
    <img src="./images/聊天3.jpg" alt="聊天3" style="width: 45%;">
</div>

<div style="display: flex; justify-content: space-around;">
    <img src="./images/设置面板.jpg" alt="设置面板" style="width: 45%;">
    <img src="./images/语音通话.jpg" alt="语音通话" style="width: 45%;">
</div>

## 功能特点

- [x] 文字聊天：像微信好友一样聊天
- [x] 语音聊天：和小智进行语音对话，支持打断
- [x] 自动配置：自动获取 MAC 地址、更新 OTA 版本，避免繁杂的配置流程
- [x] 反馈动效：（语音对话时）用户的说话波形 + 小智回答时的头像缩放动画
- [x] 移动适配：支持移动端配置服务器地址

## 系统要求
- Python 3.9+
- NodeJS 18+
- pnpm (推荐) 或 npm
- uv (Python 包管理器)
- 支持的操作系统：Windows 10+、macOS 10.15+、Linux

## 快速开始

### 方式一：一键启动（推荐）

1. 克隆项目并进入目录

```bash
git clone https://github.com/kalicyh/xiaozhi-webui.git
cd xiaozhi-webui
```

2. 安装前端依赖

```bash
pnpm install
```

3. 安装后端依赖

```bash
cd backend
uv sync
cd ..
```

> **注意**：如果遇到 WebSocket 连接问题，请确保使用兼容的 `websockets` 库版本。项目使用 `websockets>=15.0.1`。

4. 同时启动前后端

```bash
pnpm dev
```

此命令将使用 `concurrently` 同时启动前后端服务，在终端可以看到带颜色区分的前后端日志输出。

> **Windows 用户注意**：如果在控制台看到中文乱码，项目已自动配置 UTF-8 编码。如果仍有问题，请确保：
> 1. 终端使用 PowerShell 或 Windows Terminal（推荐）
> 2. 在 CMD 中手动执行 `chcp 65001` 命令切换到 UTF-8 编码
> 3. 或使用 VS Code 内置终端

> **停止服务**：使用 `Ctrl+C` 可以优雅地停止前后端服务，系统会自动清理所有进程和连接。

### 方式二：分别启动

如果你需要单独启动前端或后端，可以使用以下命令：


**单独启动前端**
```bash
pnpm dev:frontend
```

**单独启动后端**
```bash
pnpm dev:backend
```

**手动分别启动**

前端：
```bash
pnpm install
pnpm dev:frontend
```

后端：
```bash
cd backend
uv run main.py
```

### 浏览页面

在浏览器中访问 `http://localhost:5173` 即可使用

<img src="./images/页面展示.jpg" alt="页面展示" style="width: 100%;">

## 常见问题

**1. WebSocket 连接错误**

如果看到类似下面的报错：
```
BaseEventLoop.create_connection() got an unexpected keyword argument 'extra_headers'
```

- 确保使用正确版本的 `websockets` 库（建议 >=15.0.1）
- 运行 `cd backend && uv sync` 重新安装依赖

**2. 中文字符显示乱码**

- 使用 PowerShell 或 Windows Terminal（推荐）
- 在 CMD 中执行 `chcp 65001` 切换编码
- 使用 VS Code 内置终端

**3. 端口占用问题**

- 前端默认端口：5173
- 后端默认端口：5000
- 如有冲突，请在配置文件中修改端口设置

## 项目实现框图

```
                      reconnect
                    +-----------+
                    |           |
                    v           |
Text message  +------------+    |     +-------------------+            +-------------------+
+-----------> | CONNECTING | ---+---> |                   | ---------> |                   |
|             +------------+          |     Websocket     |            |      Xiaozhi      |
|             +------------+          |       Proxy       |            |       Server      |
+------------ |  AI_SPEAK  | <------- |                   | <--------- |                   |
Speak complet +------------+          +-------------------+            +-------------------+
```

## 主要逻辑框图

本项目的小智语音通话部分主要使用 "状态驱动" 的设计模式，以下是主要逻辑框图：
```
state change process
+------------------+        +--------------------------+        +------------------+
|  oldState.onExit | -----> | current_state = newState | -----> | newState.onEnter |
+------------------+        +--------------------------+        +------------------+
```
```
user speak process                      +--------------------------------+             
                                        |          circulation           |             
                                        v                                |             
+--------------------+        +--------------------+        +------------------------+ 
| getUserMediaStream | -----> | detect audio level | -----> | handleUserAudioLevel() | 
+--------------------+        +--------------------+        +------------------------+ 
```
```
ai speak process
+----------------------------------------------------------+
|                    audioQueue.empty() ?                  |
+----------------------------------------------------------+
           | no                           | yes         ^   
           v                              v             |   
+---------------------------+     +--------------+      |   
| audio = audioQueue.pop()  |     | state = idle |      |   
+---------------------------+     +--------------+      |   
       |                                                |   
       v                                                |   
+------------+                                      +------+
| play audio | -----------------------------------> | done |
+------------+                                      +------+
```

## 项目结构

```
├── backend/                            # 后端目录
│   ├── app/
│   |   ├── constant/                   # 常量
│   |   ├── proxy/                      # websocket 代理
│   |   ├── router/                     # 路由
│   |   ├── utils/                      # 工具函数
│   │   └── config.py                   # 配置
│   ├── libs/                           # 第三方库文件
│   ├── main.py                         # 后端入口
│   ├── pyproject.toml                  # Python 项目配置
│   └── uv.lock                         # Python 依赖锁定文件
├── src/                                # 前端源码目录
│   ├── assets/                         # 静态资源
│   ├── components/                     # Vue 组件
│   ├── services/                       # 模块化服务
│   ├── stores/                         # 全局状态管理
│   ├── types/                          # TypeScript 类型定义
│   ├── App.vue                         # 前端入口组件
│   └── main.ts                         # 前端入口文件
├── public/                             # 公共静态资源
├── images/                             # 项目展示图片
├── package.json                        # 前端项目配置
├── pnpm-lock.yaml                      # 前端依赖锁定文件
├── vite.config.ts                      # Vite 配置
├── tsconfig.json                       # TypeScript 配置
├── .gitignore
├── LICENSE
└── README.md
```

## 技术栈

**前端**

- 框架： Vue3 + TypeScript + Pinia
- 构建工具：Vite
- 包管理器：pnpm
- UI 组件：Element Plus
- Web API：WebSocket、Web Audio API、AudioWorklet

**后端**

- Python>=3.12 + FastAPI
- 包管理器：uv

**开发工具**

- concurrently：同时运行前后端服务
- TypeScript：类型安全
- Less：CSS 预处理器

## 贡献

欢迎提交问题报告和代码贡献。请确保遵循以下规范：

1. Python 代码风格符合 PEP8 规范
2. Vue 代码按单一指责进行模块化管理
3. 更新相关文档

## 感谢以下开源/分享人员（排名不分前后）

[虾哥](https://github.com/78)
[Huang-junsen](https://github.com/huangjunsen0406)
[TOM88812](https://github.com/TOM88812)
[小红书 @涂丫丫](http://xhslink.com/a/ZWjAcoOzvzq9)

## Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=yang-zhihang/xiaozhi-webui&type=Date)](https://www.star-history.com/#yang-zhihang/xiaozhi-webui&Date)