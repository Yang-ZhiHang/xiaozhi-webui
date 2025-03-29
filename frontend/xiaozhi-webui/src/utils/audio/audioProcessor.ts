interface AudioWorkletProcessor {
    readonly port: MessagePort;
    process(inputs: Float32Array[][], outputs: Float32Array[][]): boolean;
}

declare const AudioWorkletProcessor: {
    prototype: AudioWorkletProcessor;
    new(options?: AudioWorkletNodeOptions): AudioWorkletProcessor;
};

declare function registerProcessor(
    name: string,
    processor: new (options?: AudioWorkletNodeOptions) => AudioWorkletProcessor
): void;

class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    // 处理节点的内部逻辑
    process(inputs: Float32Array[][]): boolean {
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