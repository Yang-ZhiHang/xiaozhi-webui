export type Message = {
    type: 'user' | 'ai';
    content: string;
    time: string;
}

export type WebSocketMessage =
    | HelloResponse
    | UserEcho
    | AI_TTS_Start
    | AIResponse_Emotion
    | AIResponse_Text

export type HelloResponse = {
    type: 'hello'
    version: number
    transport: string
    session_id: string
    audio_params: {
        format: 'opus'
        sample_rate: number
        channels: number
        frame_duration: number
    }
}

export type UserEcho = {
    type: 'stt'
    text: string
    session_id: string
}

export type UserMessage = {
    type: "listen",
    state: "detect",
    text: string,
    source: "text",
}

export type AbortMessage = {
    type: "abort"
    session_id: string
}

export type AI_TTS_Start = {
    type: 'tts'
    state: 'start'
    sample_rate: number
    session_id: string
}

export type AIResponse_Emotion = {
    type: 'llm'
    text: string
    emotion: string
    session_id: string
}

export type AIResponse_Text = {
    type: 'tts'
    state: 'sentence_start' | 'sentence_end'
    text: string
    session_id: string
}

export type AIListening_Start = {
    type: "listen"
    state: "start"
    mode: "auto"
}

export type AIListening_Stop = {
    type: "listen"
    state: "stop"
    mode: "auto"
}