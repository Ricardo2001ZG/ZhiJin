<template>
  <div class="sidebar-logo-container" :class="{'collapse':collapse}">
    <transition name="sidebarLogoFade">
      <router-link v-if="collapse" key="collapse" class="sidebar-logo-link" to="/">
        <img v-if="logo" :src="logo" class="sidebar-logo"  >
        <h1 v-else class="">{{ title }} </h1>
      </router-link>
      <router-link v-else key="expand" class="sidebar-logo-link"  to="/" style="margin-left: -9px">
        <img v-if="logo" :src="logo" class="sidebar-logo"  style="margin-right: 18px;">
        <h1 class="sidebar-title">{{ title }} </h1>
      </router-link>
    </transition>
  </div>
</template>

<script>
import defaultSettings from '@/settings'

import logoImg from "@/assets/images/logo.png"
export default {
  name: 'SidebarLogo',
  props: {
    collapse: {
      type: Boolean,
      required: true
    }
  },
  setup(){
    return {
      title: defaultSettings.title,
      logo: logoImg
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebarLogoFade-enter-active {
  transition: opacity 1.5s;
}

.sidebarLogoFade-enter,
.sidebarLogoFade-leave-to {
  opacity: 0;
}

.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 50px;
  line-height: 50px;
  background: #5681ce;
  text-align: center;
  overflow: hidden;

  & .sidebar-logo-link {
    height: 100%;
    width: 100%;

    & .sidebar-logo {
      width: 18px;
      height: 18px;
      vertical-align: middle;
    }

    & .sidebar-title {
      font-family: 'siyuan-medium';
      display: inline-block;
      margin: 0;
      color: #fff;
      font-weight: 400;
      line-height: 50px;
      font-size: 18px;
      vertical-align: middle;
    }
  }
}
</style>
