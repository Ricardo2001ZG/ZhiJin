"use strict";

require("core-js/modules/es.promise.js");
var _router = _interopRequireDefault(require("./router"));
var _store = _interopRequireDefault(require("./store"));
var _elementPlus = require("element-plus");
var _nprogress = _interopRequireDefault(require("nprogress"));
require("nprogress/nprogress.css");
var _auth = require("@/utils/auth");
var _getPageTitle = _interopRequireDefault(require("@/utils/get-page-title"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
// progress bar
// progress bar style
// get token from cookie

_nprogress.default.configure({
  showSpinner: false
}); // NProgress Configuration

const whiteList = ['/login']; // no redirect whitelist

_router.default.beforeEach(async (to, from, next) => {
  // start progress bar
  _nprogress.default.start();

  // set page title
  document.title = (0, _getPageTitle.default)(to.meta.title);

  // determine whether the user has logged in
  const hasToken = (0, _auth.getToken)();
  console.log(hasToken);
  if (hasToken) {
    if (to.path === '/login') {
      // if is logged in, redirect to the home page
      next({
        path: '/'
      });
      _nprogress.default.done();
    } else {
      const hasGetUserInfo = _store.default.getters.name;
      if (hasGetUserInfo) {
        next();
      } else {
        next();
        _nprogress.default.done();
      }
    }
  } else {
    /* has no token*/
    console.log(from);
    console.log(to);
    if (whiteList.indexOf(to.path) !== -1) {
      console.log('白名单');
      // in the free login whitelist, go directly
      next();
    } else {
      console.log(to);
      // other pages that do not have permission to access are redirected to the login page.
      next("/login?redirect=".concat(to.path));
      // next()
      _nprogress.default.done();
    }
  }
});
_router.default.afterEach(() => {
  // finish progress bar
  _nprogress.default.done();
});