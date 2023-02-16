import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
// import './permission'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import locale from 'element-plus/lib/locale/lang/zh-cn'

createApp(App).use(ElementPlus, { locale }).use(store).use(router).mount("#app");
