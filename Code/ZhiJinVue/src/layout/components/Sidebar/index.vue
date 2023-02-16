<template>
  <div :class="{'has-logo':showLogo}">
    <logo v-if="showLogo"
          :collapse="isCollapse" />
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu :default-active="activeMenu"
               :collapse="isCollapse"
               :background-color="variables.menuBg"
               :text-color="variables.menuText"
               :unique-opened="true"
               :active-text-color="variables.menuActiveText"
               :collapse-transition="false"
               mode="vertical">
        <!-- <sidebar-item v-for="route in routes" :key="route.urlPath" :item="route" :base-path="route.urlPath" /> -->
        <div v-for="menu in routes"
             :key="menu.frontendId">
          <el-sub-menu v-if="(menu.children.length)>0"
                       id="el-main"
                       :index="String(menu.urlPath)">
            <template #title>
              <!-- <i :class="menu.icon"></i> -->
              <!-- <i :class="menu.icon" /> -->
              <svg-icon :icon-class="menu.icon"
                        style="font-size:18px;"
                        class-name='custom-class' />
              <span>{{ menu.menuName }}</span>
            </template>
            <el-menu-item v-for="child in menu.children"
                          :key="child.frontendId"
                          :index="menu.urlPath+child.urlPath"
                          style="padding-left:55px"
                          @click="$router.push(menu.urlPath+child.urlPath)">
              {{ child.menuName }}
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else
                        :index="String(menu.urlPath)"
                        @click="$router.push(menu.urlPath)">
            <svg-icon :icon-class="menu.icon"
                      style="font-size:18px"
                      class-name='custom-class' />
            <span>{{ menu.menuName}}</span>
          </el-menu-item>
        </div>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script>
import { defineComponent, reactive } from 'vue'
import { mapGetters, useStore } from 'vuex'
import Logo from './Logo'
import SidebarItem from './SidebarItem'
import variables from '@/styles/variables1.module.scss'

export default {
  components: { SidebarItem, Logo },
  setup () {
    const routes = reactive(useStore().state.user.menulist)
    console.log(variables)
    return {
      routes
    }
  },
  computed: {
    ...mapGetters(['sidebar']),

    activeMenu () {
      const route = this.$route
      const { meta, path } = route
      // if set path, the sidebar will highlight the path you set
      console.log(path)
      console.log(meta)
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
    },
    showLogo () {
      return this.$store.state.settings.sidebarLogo
    },
    variables () {
      return variables
    },
    isCollapse () {
      return !this.sidebar.opened
    }
  }
}
</script>

<style lang="scss" scoped>
.custom-class,.el-icon-arrow-down{
  vertical-align: middle !important;
}

.el-sub-menu :deep(.el-sub-menu__icon-arrow){
  margin-top:-5px !important
}
.el-sub-menu :deep(.el-sub-menu__title) {
  padding-left: 18px !important;
}

</style>
