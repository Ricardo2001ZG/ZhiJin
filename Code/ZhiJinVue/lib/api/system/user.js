"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
require("core-js/modules/es.promise.js");
var _request = _interopRequireDefault(require("@/utils/request"));
var _menulist = require("@/store/modules/menulist");
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
const api = {};

//获取登陆验证码
api.getLoginCode = data => {
  return (0, _request.default)({
    url: '/getLoginCode',
    method: 'Post',
    params: data
  });
};
//检验登录验证码
api.checkLoginCode = data => {
  return (0, _request.default)({
    url: '/checkLoginCode',
    method: 'post',
    data
  });
};
let result = {
  token: 123456,
  frontendPrivilegeList: _menulist.menulist
};
api.login = data => {
  data.loginType = 1;
  return new Promise(resolve => {
    resolve(result);
  });
  // request({
  //     url: '/login',
  //     method: 'post',
  //     data
  // })
};

// 修改密码
api.changePassword = data => {
  return (0, _request.default)({
    url: '/user/changePassword',
    method: 'post',
    data
  });
};
api.logout = () => {
  return (0, _request.default)({
    url: '/system/user/logout',
    method: 'post'
  });
};

// 获取用户列表
api.findUser = data => {
  return (0, _request.default)({
    url: '/user/findUser',
    method: 'post',
    data
  });
};
// 获取单个用户
api.getUser = data => {
  return (0, _request.default)({
    url: '/user/getUser',
    method: 'get',
    params: data
  });
};
// 添加/编辑用户
api.saveUser = data => {
  return (0, _request.default)({
    url: '/user/saveUser',
    method: 'post',
    data
  });
};

// 获取角色字典
api.findRoleDict = data => {
  return (0, _request.default)({
    url: '/role/findRoleDict',
    method: 'get',
    params: data
  });
};
// 获取部门字典
api.findDeptDict = data => {
  return (0, _request.default)({
    url: '/dept/findDeptDict',
    method: 'get',
    params: data
  });
};

// 获取前端权限字典
api.findFrontendPrivilegeDict = data => {
  return (0, _request.default)({
    url: '/privilege/findFrontendPrivilegeDict',
    method: 'get',
    params: data
  });
};

// 获取后端权限字典
api.findAuthorityDict = data => {
  return (0, _request.default)({
    url: '/backendAuthority/findAuthorityDict',
    method: 'get',
    params: data
  });
};
api.delUser = data => {
  return (0, _request.default)({
    url: '/user/delUser',
    method: 'get',
    params: data
  });
};
var _default = api;
exports.default = _default;