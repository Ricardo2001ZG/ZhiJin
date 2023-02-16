"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
require("core-js/modules/es.promise.js");
require("core-js/modules/es.weak-map.js");
require("core-js/modules/web.dom-collections.iterator.js");
var _vueRouter = require("vue-router");
var _layout = _interopRequireDefault(require("@/layout"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }
function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }
const routes = [{
  path: "/login",
  component: () => Promise.resolve().then(() => _interopRequireWildcard(require("@/views/login"))),
  hidden: true
}, {
  path: "/404",
  // component: () => import("@/views/404"),
  hidden: true
}, {
  path: "/",
  component: _layout.default,
  redirect: "/login"
}, {
  path: "/home",
  component: _layout.default,
  redirect: '/home/index',
  meta: {
    title: "主页",
    meta: "/home"
  },
  children: [{
    path: "index",
    name: "home",
    component: () => Promise.resolve().then(() => _interopRequireWildcard(require("@/views/Home")))
  }]
}, {
  path: "/task",
  component: _layout.default,
  redirect: '/task/index',
  meta: {
    title: "任务",
    meta: "/task"
  },
  children: [{
    path: "index",
    name: "task",
    component: () => Promise.resolve().then(() => _interopRequireWildcard(require("@/views/task")))
  }]
},
// 404 page must be placed at the end !!!
{
  path: "/:pathMatch(.*)*",
  redirect: "/404",
  hidden: true
}];
const router = (0, _vueRouter.createRouter)({
  history: (0, _vueRouter.createWebHashHistory)(),
  routes
});
var _default = router;
exports.default = _default;