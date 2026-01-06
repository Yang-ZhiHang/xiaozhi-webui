import { LogLevel, type LogFn } from '@/types/log';
import { errorStackMatcher } from './regex';

const buildLog = (level: LogLevel): LogFn => {
    return (...args) => {
        const stack = new Error().stack!.split('\n');

        // 第 2 行表示真实的调用者信息
        // 形如： at Proxy.loadFromLocal (http://localhost:5173/src/stores/setting.ts?t=12345:85:7)
        const line = stack[2];

        // 正则匹配获取函数名、文件名和行号
        const match_result = errorStackMatcher.exec(line);
        if (!match_result) {
            console[level](...args);
            return;
        }
        const [, rawFn, url, row] = match_result;
        const cleanUrl = url.split(/[?#]/)[0];
        const file = cleanUrl.replace(/^.*[\\\/]/, '');
        const fn = rawFn.trim() || '<anon>';

        const prefix = `[${file}][${fn}:${row}]`;
        console[level](prefix, ...args);
    };
};

export const log = buildLog(LogLevel.LOG);
export const warn = buildLog(LogLevel.WARN);
export const error = buildLog(LogLevel.ERROR);