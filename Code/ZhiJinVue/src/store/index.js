// import Vue from 'vue'
// import Vuex from 'vuex'
import getters from './getters'
import app from './modules/app'
import settings from './modules/settings'
import user from './modules/user'

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


import { createStore } from "vuex";

export default createStore({
  getters,
  modules:{
    app,
    settings,
    user,
  }
});
