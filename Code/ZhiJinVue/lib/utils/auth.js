"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getMenulist = getMenulist;
exports.getToken = getToken;
exports.getUsername = getUsername;
exports.removeToken = removeToken;
exports.setMenulist = setMenulist;
exports.setToken = setToken;
exports.setUsername = setUsername;
require("core-js/modules/es.json.stringify.js");
var _jsCookie = _interopRequireDefault(require("js-cookie"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
const TokenKey = 'token';
function getToken() {
  return _jsCookie.default.get(TokenKey);
}
function setToken(token) {
  return _jsCookie.default.set(TokenKey, token);
}
function getMenulist() {
  return JSON.parse(localStorage.getItem('menulist'));
}
function setMenulist(menulist) {
  console.log(menulist);
  return localStorage.setItem('menulist', JSON.stringify(menulist));
}
function getUsername() {
  return JSON.parse(localStorage.getItem('username'));
}
function setUsername(username) {
  return localStorage.setItem('username', JSON.stringify(username));
}
function removeToken() {
  console.log('清除');
  return _jsCookie.default.remove(TokenKey);
}