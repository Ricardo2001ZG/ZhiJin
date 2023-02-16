<template>
  <!-- <section class="app-main">
    <transition
      name="fade-transform"
      mode="out-in"
    >
      <router-view :key="key" />
    </transition>
  </section> -->
  <div class="bgbox" ref="dom">
    <router-view :key="key" v-slot="{ Component }">
      <transition name="fade-transform" mode="out-in">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </transition>
    </router-view>
  </div>
</template>

<script>
import { computed } from '@vue/runtime-core'
import { useRoute } from 'vue-router'
export default {
  name: 'AppMain',
  setup(){
    const route = useRoute()
    const key = computed(()=> route.path)
    return {
      key
    }
  }
}
</script>

<style scoped>
.bgbox {
  background-color: #edf4ff;
  min-height: calc(100% - 50px);
  width: 100%;
  position: absolute;
  box-shadow: inset 0px 0px 6px 4px rgba(37,104,219,0.1);
}
.app-main {
  /*50 = navbar  */
  min-height: calc(100vh - 50px);
  width: 100%;
  position: relative;
  overflow: hidden;
}
.fixed-header + .app-main {
  padding-top: 50px;
}
</style>
