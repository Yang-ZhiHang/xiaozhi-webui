export type LogFn = (...args: any[]) => void;

export enum LogLevel {
    LOG = 'log',
    WARN = 'warn',
    ERROR = 'error',
}