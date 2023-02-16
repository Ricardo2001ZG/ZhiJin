"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
require("core-js/modules/es.object.assign.js");
require("core-js/modules/es.promise.js");
require("core-js/modules/es.string.trim.js");
var _user = _interopRequireDefault(require("@/api/system/user"));
var _auth = require("@/utils/auth");
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
// import { logina, logout, getInfo } from '@/api/system/user'

// import { resetRouter } from '@/router'

const getDefaultState = () => {
  return {
    token: (0, _auth.getToken)(),
    name: (0, _auth.getUsername)(),
    avatar: '',
    menulist: (0, _auth.getMenulist)()
  };
};
const state = getDefaultState();
const mutations = {
  RESET_STATE: state => {
    Object.assign(state, getDefaultState());
  },
  SET_TOKEN: (state, token) => {
    state.token = token;
  },
  SET_NAME: (state, name) => {
    state.name = name;
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar;
  },
  SET_MENULIST: (state, menulist) => {
    state.menulist = menulist;
  }
};
const actions = {
  // user login
  login(_ref, userInfo) {
    let {
      commit
    } = _ref;
    const {
      username,
      password,
      verification
    } = userInfo;
    return new Promise((resolve, reject) => {
      _user.default.login({
        username: username.trim(),
        password: password,
        verification: verification
      }).then(response => {
        console.log(response);
        commit('SET_TOKEN', response.token);
        commit('SET_NAME', username);
        commit('SET_MENULIST', response.frontendPrivilegeList);
        (0, _auth.setToken)(response.token);
        (0, _auth.setMenulist)(response.frontendPrivilegeList);
        (0, _auth.setUsername)(username);
        resolve();
      }).catch(error => {
        reject(error);
      });
    });
  },
  codeLogin(_ref2, code) {
    let {
      commit
    } = _ref2;
    console.log(code);
    return new Promise((resolve, reject) => {
      _user.default.codeLogin({
        code: code
      }).then(response => {
        console.log(response);
        commit('SET_TOKEN', response.token);
        commit('SET_NAME', response.username);
        commit('SET_MENULIST', response.frontendPrivilegeList);
        (0, _auth.setToken)(response.token);
        (0, _auth.setMenulist)(response.frontendPrivilegeList);
        (0, _auth.setUsername)(response.username);
        resolve();
      }).catch(error => {
        reject(error);
      });
    });
  },
  // get user info
  // getInfo({ commit, state }) {
  //     return new Promise((resolve, reject) => {
  //         getInfo(state.token).then(response => {
  //             const { data } = response

  //             if (!data) {
  //                 return reject('Verification failed, please Login again.')
  //             }

  //             const { name, avatar } = data

  //             commit('SET_NAME', name)
  //             commit('SET_AVATAR', avatar)
  //             resolve(data)
  //         }).catch(error => {
  //             reject(error)
  //         })
  //     })
  // },

  // user logout
  logout(_ref3) {
    let {
      commit,
      state
    } = _ref3;
    return new Promise((resolve, reject) => {
      // api.logout(state.token).then(() => {
      (0, _auth.removeToken)(); // must remove  token  first
      // resetRouter()
      commit('RESET_STATE');
      resolve();
      // }).catch(error => {
      //     reject(error)
      // })
    });
  },

  // remove token
  resetToken(_ref4) {
    let {
      commit
    } = _ref4;
    return new Promise(resolve => {
      (0, _auth.removeToken)(); // must remove  token  first
      commit('RESET_STATE');
      resolve();
    });
  }
};
var _default = {
  namespaced: true,
  state,
  mutations,
  actions
};
exports.default = _default;