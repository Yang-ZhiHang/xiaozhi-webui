import asyncio
import websockets
import os
import json
import uuid
import wave
import io
import numpy as np
import sys

# 加载环境变量
from dotenv import load_dotenv

load_dotenv()

# 在导入 opuslib 之前 windows 需要手动加载 opus.dll 动态链接库
from system_info import setup_opus

setup_opus()
try:
    import opuslib
except Exception as e:
    print(f"导入 opuslib 失败: {e}")
    print("请确保 opus 动态库已正确安装或位于正确的位置")
    sys.exit(1)


def get_mac_address():
    mac = uuid.getnode()
    return ":".join(
        ["{:02x}".format((mac >> elements) & 0xFF) for elements in range(0, 8 * 6, 8)][
            ::-1
        ]
    )


def pcm_to_opus(pcm_data):
    """将PCM音频数据转换为Opus格式"""
    try:
        # 创建编码器：16kHz, 单声道, VOIP模式
        encoder = opuslib.Encoder(16000, 1, "voip")

        try:
            # 确保PCM数据是Int16格式
            pcm_array = np.frombuffer(pcm_data, dtype=np.int16)

            # 编码PCM数据，每帧960个采样点
            opus_data = encoder.encode(pcm_array.tobytes(), 960)  # 60ms at 16kHz
            return opus_data

        except opuslib.OpusError as e:
            print(f"Opus编码错误: {e}, 数据长度: {len(pcm_data)}")
            return None

    except Exception as e:
        print(f"Opus初始化错误: {e}")
        return None


def opus_to_wav(opus_data):
    """将Opus音频数据转换为WAV格式"""
    try:
        # 创建解码器：16kHz, 单声道
        decoder = opuslib.Decoder(16000, 1)

        try:
            # 解码Opus数据
            pcm_data = decoder.decode(opus_data, 960)  # 使用960采样点
            if pcm_data:
                # 将PCM数据转换为numpy数组
                audio_array = np.frombuffer(pcm_data, dtype=np.int16)

                # 创建WAV文件
                wav_io = io.BytesIO()
                with wave.open(wav_io, "wb") as wav:
                    wav.setnchannels(1)  # 单声道
                    wav.setsampwidth(2)  # 16位
                    wav.setframerate(16000)  # 16kHz
                    wav.writeframes(audio_array.tobytes())
                return wav_io.getvalue()
            return None

        except opuslib.OpusError as e:
            print(f"Opus 解码错误: {e}, 数据长度: {len(opus_data)}")
            return None

    except Exception as e:
        print(f"音频处理错误: {e}")
        return None


class AudioProcessor:
    def __init__(self, buffer_size=960):
        self.buffer_size = buffer_size
        self.buffer = np.array([], dtype=np.float32)
        self.sample_rate = 16000

    def reset_buffer(self):
        self.buffer = np.array([], dtype=np.float32)

    def process_audio(self, input_data):
        # 将输入数据转换为float32数组
        input_array = np.frombuffer(input_data, dtype=np.float32)

        # 将新数据添加到缓冲区
        self.buffer = np.append(self.buffer, input_array)

        chunks = []
        # 当缓冲区达到指定大小时处理数据
        while len(self.buffer) >= self.buffer_size:
            # 提取数据
            chunk = self.buffer[: self.buffer_size]
            self.buffer = self.buffer[self.buffer_size :]

            # 转换为16位整数
            pcm_data = (chunk * 32767).astype(np.int16)
            chunks.append(pcm_data.tobytes())

        return chunks

    def process_remaining(self):
        if len(self.buffer) > 0:
            # 转换为16位整数
            pcm_data = (self.buffer * 32767).astype(np.int16)
            self.buffer = np.array([], dtype=np.float32)
            return [pcm_data.tobytes()]
        return []


class WebSocketProxy:
    def __init__(
        self,
        device_id: str,
        websocket_url: str,
        proxy_host: str,
        proxy_port: str,
        token_enable: bool,
        token: str,
    ):
        self.device_id = device_id
        self.websocket_url = websocket_url
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.token_enable = token_enable
        self.token = token

        self.audio_processor = AudioProcessor(buffer_size=960)
        self.decoder = opuslib.Decoder(16000, 1)  # 保持单个解码器实例即可
        self.audio_buffer = bytearray()  # 用于存储解码后的音频数据
        self.is_first_audio = True  # 用于判断是否创建 Wave 头信息
        self.total_samples = 0  # 跟踪总采样数
        self.audio_lock = asyncio.Lock()  # 保证音频按顺序发送

        self.headers = {
            "Device-Id": self.device_id,
            "Client-Id": "15f426f7-b0dd-42a1-8445-64c6f720c1c4",
            "Protocol-Version": "1",
        }
        if self.token_enable:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def create_wav_header(self, total_samples):
        """
        创建 Wave 文件头
        https://blog.csdn.net/shulianghan/article/details/117351966

        参数:
        total_samples (int): 音频数据的总采样数

        返回:
        bytearray: Wave 文件头的字节数组

        """
        header = bytearray(44)

        # ========== The "RIFF" chunk descriptor ==========
        header[0:4] = b"RIFF"
        header[4:8] = (total_samples * 2 + 36).to_bytes(4, "little")
        header[8:12] = b"WAVE"

        # ========== The "fmt" sub-chunk ==========
        header[12:16] = b"fmt "
        header[16:20] = (16).to_bytes(4, "little")
        header[20:22] = (1).to_bytes(2, "little")
        header[22:24] = (1).to_bytes(2, "little")
        header[24:28] = (16000).to_bytes(4, "little")
        header[28:32] = (32000).to_bytes(4, "little")
        header[32:34] = (2).to_bytes(2, "little")
        header[34:36] = (16).to_bytes(2, "little")

        # ========== The "data" sub-chunk ==========
        header[36:40] = b"data"
        header[40:44] = (total_samples * 2).to_bytes(4, "little")

        return header

    async def proxy_handler(self, websocket):
        """来自浏览器的 WebSocket 连接"""
        try:
            print(
                f"[WebSocketProxy][proxy_handler] New client connection from {websocket.remote_address}"
            )
            async with websockets.connect(
                self.websocket_url, extra_headers=self.headers
            ) as server_ws:
                print(
                    f"[WebSocketProxy][proxy_handler] Connected to server with headers: {self.headers}"
                )

                # 创建任务
                client_to_server = asyncio.create_task(
                    self.handle_client_messages(websocket, server_ws)
                )
                server_to_client = asyncio.create_task(
                    self.handle_server_messages(server_ws, websocket)
                )

                # 等待任意一个任务完成
                done, pending = await asyncio.wait(
                    [client_to_server, server_to_client],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # 取消其他任务
                for task in pending:
                    task.cancel()

        except Exception as e:
            print(f"[WebSocketProxy][proxy_handler] Proxy error: {e}")
        finally:
            print("[WebSocketProxy][proxy_handler] Client connection closed")

    async def handle_server_messages(self, server_ws, client_ws):
        """处理来自 WebSocket 服务器的消息"""
        try:
            async for message in server_ws:
                if isinstance(message, str):
                    try:
                        msg_data = json.loads(message)
                        if (
                            msg_data.get("type") == "tts"
                            and msg_data.get("state") == "start"
                        ):
                            # 新的音频流开始，播放未发送完的语音并重置状态
                            if len(self.audio_buffer) > 44:
                                async with self.audio_lock:
                                    chunk_size = (self.total_samples * 2 + 36).to_bytes(
                                        4, "little"
                                    )
                                    subchunk2_size = (self.total_samples * 2).to_bytes(
                                        4, "little"
                                    )
                                    self.audio_buffer[4:8] = chunk_size
                                    self.audio_buffer[40:44] = subchunk2_size
                                    await client_ws.send(bytes(self.audio_buffer))
                            self.audio_buffer = bytearray()
                            self.is_first_audio = True
                            self.total_samples = 0
                        elif (
                            msg_data.get("type") == "tts"
                            and msg_data.get("state") == "stop"
                        ):
                            # 音频流结束，发送剩余数据并重置状态
                            if len(self.audio_buffer) > 44:
                                async with self.audio_lock:
                                    chunk_size = (self.total_samples * 2 + 36).to_bytes(
                                        4, "little"
                                    )
                                    subchunk2_size = (self.total_samples * 2).to_bytes(
                                        4, "little"
                                    )
                                    self.audio_buffer[4:8] = chunk_size
                                    self.audio_buffer[40:44] = subchunk2_size
                                    await client_ws.send(bytes(self.audio_buffer))
                                    self.audio_buffer = bytearray()
                                    self.is_first_audio = True
                                    self.total_samples = 0

                        await client_ws.send(message)
                    except json.JSONDecodeError:
                        await client_ws.send(message)
                else:
                    async with self.audio_lock:
                        try:
                            # 解码 Opus 音频数据
                            pcm_data = self.decoder.decode(message, 960)

                            if pcm_data:
                                # 计算采样数
                                samples = (
                                    len(pcm_data) // 2
                                )  # 16 位音频，每个采样 2 字节
                                self.total_samples += samples

                                # 如果是第一个音频片段，创建 Wave 头
                                if self.is_first_audio:
                                    self.audio_buffer.extend(
                                        self.create_wav_header(self.total_samples)
                                    )
                                    self.is_first_audio = False

                                # 追加音频数据
                                self.audio_buffer.extend(pcm_data)

                                # 当缓冲区达到一定大小时发送数据
                                # Wave 头 + 32000 个音频采样数据 = 64044 字节
                                # 一句简短的话一般为 64KB 的 Wave 音频文件
                                if len(self.audio_buffer) >= 64044:

                                    # 更新 Wave 头中的元数据
                                    chunk_size = (self.total_samples * 2 + 36).to_bytes(
                                        4, "little"
                                    )
                                    subchunk2_size = (self.total_samples * 2).to_bytes(
                                        4, "little"
                                    )
                                    self.audio_buffer[4:8] = chunk_size
                                    self.audio_buffer[40:44] = subchunk2_size

                                    # 发送数据
                                    await client_ws.send(bytes(self.audio_buffer))

                                    # 完全重置缓冲区
                                    self.audio_buffer = bytearray()
                                    self.is_first_audio = True
                                    self.total_samples = 0

                        except Exception as e:
                            print(
                                f"[WebSocketProxy][handle_server_messages] Audio handle error: {e}"
                            )
        except Exception as e:
            print(
                f"[WebSocketProxy][handle_server_messages] Server message handling error: {e}"
            )

    async def handle_client_messages(self, client_ws, server_ws):
        """处理来自客户端的消息"""
        try:
            async for message in client_ws:
                if isinstance(message, str):
                    await server_ws.send(message)
                else:
                    print(
                        "[WebsocketProxy][handle_client_messages] Message is not a string."
                    )
        except Exception as e:
            print(
                f"[WebsocketProxy][handle_client_messages] Client message handling error: {e}"
            )

    async def main(self):
        """启动代理服务器"""
        async with websockets.serve(
            self.proxy_handler, self.proxy_host, self.proxy_port
        ):
            await asyncio.Future()


if __name__ == "__main__":
    proxy = WebSocketProxy()
    asyncio.run(proxy.main())
