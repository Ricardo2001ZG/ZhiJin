"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _getters = _interopRequireDefault(require("./getters"));
var _app = _interopRequireDefault(require("./modules/app"));
var _settings = _interopRequireDefault(require("./modules/settings"));
var _user = _interopRequireDefault(require("./modules/user"));
var _vuex = require("vuex");
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
// import Vue from 'vue'
// import Vuex from 'vuex'
// Vue.use(Vuex)
// const store = new Vuex.Store({
//   modules: {
//     app,
//     settings,
//     user,
//   },
//   getters
// })
// export default store
var _default = (0, _vuex.createStore)({
  getters: _getters.default,
  modules: {
    app: _app.default,
    settings: _settings.default,
    user: _user.default
  }
});
exports.default = _default;