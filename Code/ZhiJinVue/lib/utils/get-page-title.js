"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = getPageTitle;
var _settings = _interopRequireDefault(require("@/settings"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
const title = _settings.default.title || 'Vue Admin Template';
function getPageTitle(pageTitle) {
  if (pageTitle) {
    return "".concat(pageTitle, " - ").concat(title);
  }
  return "".concat(title);
}