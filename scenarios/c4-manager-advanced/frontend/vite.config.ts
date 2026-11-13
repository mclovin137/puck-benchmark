import {defineConfig} from 'vite';
export default defineConfig({server:{host:'127.0.0.1',port:18204,strictPort:true,watch:{usePolling:true},proxy:{'/api':process.env.API_URL||'http://127.0.0.1:18084'}},preview:{host:'127.0.0.1',port:18204}});
