class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    // 处理节点的内部逻辑
    process(inputs) {
        // inputs[0] 代表第一个输入通道
        // inputs[0][0] 代表第一个输入通道的第一个声道（单声道音频）
        const input = inputs[0][0];
        if (!input) return true;

        // 创建新的 Float32Array 并复制数据
        const audioData = new Float32Array(input);

        // 发送音频数据至主线程的 port.onmessage
        this.port.postMessage(audioData, [audioData.buffer]);

        return true;
    }
}

registerProcessor('audioProcessor', AudioProcessor);