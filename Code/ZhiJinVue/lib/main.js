"use strict";

var _vue = require("vue");
var _App = _interopRequireDefault(require("./App.vue"));
var _router = _interopRequireDefault(require("./router"));
var _store = _interopRequireDefault(require("./store"));
var _elementPlus = _interopRequireDefault(require("element-plus"));
require("element-plus/dist/index.css");
var _zhCn = _interopRequireDefault(require("element-plus/lib/locale/lang/zh-cn"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
// import './permission'

(0, _vue.createApp)(_App.default).use(_elementPlus.default, {
  locale: _zhCn.default
}).use(_store.default).use(_router.default).mount("#app");