import io
import sys
import wave
import numpy as np
from logging import getLogger

logger = getLogger(__name__)

try:
    import opuslib
except Exception as e:
    logger.error(f"导入 opuslib 失败: {e}")
    logger.error("请确保 opus 动态库已正确安装或位于正确的位置")
    sys.exit(1)

decoder = opuslib.Decoder(16000, 1)  # 16KHz, 单声道


def opus_to_wav(opus_data: bytes) -> bytes | None:
    try:
        try:
            pcm_data = decoder.decode(opus_data, 960)
            if pcm_data:
                audio_array = np.frombuffer(pcm_data, dtype=np.int16)

                # 创建 Wave 文件
                wav_io = io.BytesIO()
                with wave.open(wav_io, "wb") as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(16000)
                    wav.writeframes(audio_array.tobytes())
                return wav_io.getvalue()
            return None

        except opuslib.OpusError as e:
            logger.error(f"Opus 解码错误: {e}, 数据长度: {len(opus_data)}")
            return None

    except Exception as e:
        logger.error(f"音频处理错误: {e}")
        return None


def pcm_to_opus(pcm_data: bytes) -> bytes | None:
    try:
        encoder = opuslib.Encoder(16000, 1, "voip")
        pcm_array = np.frombuffer(pcm_data, dtype=np.int16)
        opus_data = encoder.encode(pcm_array.tobytes(), 960)
        return opus_data
    except opuslib.OpusError as e:
        logger.error(f"Opus 编码错误: {e}, 数据长度: {len(pcm_data)}")
        return None


class AudioProcessor:
    def __init__(self, buffer_size):
        self.buffer_size: int = buffer_size
        self.buffer = np.array([], dtype=np.float32)
        self.sample_rate = 16000

    def reset_buffer(self):
        self.buffer = np.array([], dtype=np.float32)

    def process_audio(self, input_data: bytes) -> list[bytes]:
        # 将输入数据转换为 float32 数组
        input_array = np.frombuffer(input_data, dtype=np.float32)

        # 将新数据添加到缓冲区
        self.buffer = np.append(self.buffer, input_array)

        # 当缓冲区达到指定大小时处理数据
        chunks = []
        while len(self.buffer) >= self.buffer_size:
            # 提取数据
            chunk = self.buffer[: self.buffer_size]
            self.buffer = self.buffer[self.buffer_size :]
            # 转换为 16 位整数
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
