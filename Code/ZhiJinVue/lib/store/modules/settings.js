"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _settings = _interopRequireDefault(require("@/settings"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
const {
  showSettings,
  fixedHeader,
  sidebarLogo
} = _settings.default;
const state = {
  showSettings: showSettings,
  fixedHeader: fixedHeader,
  sidebarLogo: sidebarLogo
};
const mutations = {
  CHANGE_SETTING: (state, _ref) => {
    let {
      key,
      value
    } = _ref;
    // eslint-disable-next-line no-prototype-builtins
    if (state.hasOwnProperty(key)) {
      state[key] = value;
    }
  }
};
const actions = {
  changeSetting(_ref2, data) {
    let {
      commit
    } = _ref2;
    commit('CHANGE_SETTING', data);
  }
};
var _default = {
  namespaced: true,
  state,
  mutations,
  actions
};
exports.default = _default;