/// <reference types="vite/client" />

declare module '*.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare global {
  interface ImportMetaEnv {
    VITE_APP_SERVER_URL: string
  }
  interface Window {
    AudioContext: typeof AudioContext;
    webkitAudioContext: typeof AudioContext;
  }
  interface Navigator {
    getUserMedia?: any;
    webkitGetUserMedia?: any;
    mozGetUserMedia?: any;
  }
}

export { };