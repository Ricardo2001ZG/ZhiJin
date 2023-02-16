"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _store = _interopRequireDefault(require("@/store"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
const {
  body
} = document;
const WIDTH = 992; // refer to Bootstrap's responsive design
var _default = {
  watch: {
    $route(route) {
      if (this.device === 'mobile' && this.sidebar.opened) {
        _store.default.dispatch('app/closeSideBar', {
          withoutAnimation: false
        });
      }
    }
  },
  beforeMount() {
    window.addEventListener('resize', this.$_resizeHandler);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.$_resizeHandler);
  },
  mounted() {
    const isMobile = this.$_isMobile();
    if (isMobile) {
      _store.default.dispatch('app/toggleDevice', 'mobile');
      _store.default.dispatch('app/closeSideBar', {
        withoutAnimation: true
      });
    }
  },
  methods: {
    // use $_ for mixins properties
    // https://vuejs.org/v2/style-guide/index.html#Private-property-names-essential
    $_isMobile() {
      const rect = body.getBoundingClientRect();
      return rect.width - 1 < WIDTH;
    },
    $_resizeHandler() {
      if (!document.hidden) {
        const isMobile = this.$_isMobile();
        _store.default.dispatch('app/toggleDevice', isMobile ? 'mobile' : 'desktop');
        if (isMobile) {
          _store.default.dispatch('app/closeSideBar', {
            withoutAnimation: true
          });
        }
      }
    }
  }
};
exports.default = _default;