"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _jsCookie = _interopRequireDefault(require("js-cookie"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
const state = {
  sidebar: {
    opened: _jsCookie.default.get('sidebarStatus') ? !!+_jsCookie.default.get('sidebarStatus') : true,
    withoutAnimation: false
  },
  device: 'desktop'
};
const mutations = {
  TOGGLE_SIDEBAR: state => {
    state.sidebar.opened = !state.sidebar.opened;
    state.sidebar.withoutAnimation = false;
    if (state.sidebar.opened) {
      _jsCookie.default.set('sidebarStatus', 1);
    } else {
      _jsCookie.default.set('sidebarStatus', 0);
    }
  },
  CLOSE_SIDEBAR: (state, withoutAnimation) => {
    _jsCookie.default.set('sidebarStatus', 0);
    state.sidebar.opened = false;
    state.sidebar.withoutAnimation = withoutAnimation;
  },
  TOGGLE_DEVICE: (state, device) => {
    state.device = device;
  }
};
const actions = {
  toggleSideBar(_ref) {
    let {
      commit
    } = _ref;
    commit('TOGGLE_SIDEBAR');
  },
  closeSideBar(_ref2, _ref3) {
    let {
      commit
    } = _ref2;
    let {
      withoutAnimation
    } = _ref3;
    commit('CLOSE_SIDEBAR', withoutAnimation);
  },
  toggleDevice(_ref4, device) {
    let {
      commit
    } = _ref4;
    commit('TOGGLE_DEVICE', device);
  }
};
var _default = {
  namespaced: true,
  state,
  mutations,
  actions
};
exports.default = _default;