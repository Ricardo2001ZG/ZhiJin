<template>
  <div class="navbar">
    <hamburger
      :is-active="sidebar.opened"
      class="hamburger-container"
      @toggleClick="toggleSideBar"
    />

    <breadcrumb class="breadcrumb-container" />

    <div class="right-menu">
      <el-dropdown trigger="click">
        <span
          class="el-dropdown-link"
          style="margin-right:10px;cursor: pointer"
        >
          {{ name }}<i class="el-icon-caret-bottom" />
        </span>
        <!-- <div class="avatar-wrapper">
          <img :src="avatar+'?imageView2/1/w/80/h/80'" class="user-avatar">
          <i class="el-icon-arrow-down" />
        </div> -->
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>
              <div @click="openDialog">
                修改密码
              </div>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <span style="margin-right:20px;">
        <el-button
          type="text"
          @click="logout"
        >退出</el-button></span>
    </div>
  </div>
  <div v-dialogdrag>
      <el-dialog
        v-model="editPasswordVisible"
        title="修改密码"
        width="500px"
        :close-on-click-modal="false"
        @close="dialogClose"
        class="dialogStyle"
      >
        <el-form
          ref="userForm"
          label-position="right"
          label-width="107px"
          :model="userForm"
          :rules="rules"
        >
          <el-form-item
            prop="oldPassword"
            label="请输入旧密码"
          >
            <el-input
              v-model="userForm.oldPassword"
              autocomplete="off"
              type="password"
              placeholder="请输入旧密码"
            />
          </el-form-item>
          <el-form-item
            prop="newPassword"
            label="请输入新密码"
          >
            <el-input
              v-model="userForm.newPassword"
              autocomplete="off"
              type="password"
              placeholder="请输入新密码"
            />
          </el-form-item>
          <el-form-item
            prop="confirmPassword"
            label="请确认新密码"
          >
            <el-input
              v-model="userForm.confirmPassword"
              autocomplete="off"
              type="password"
              placeholder="请确认新密码"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editPasswordVisible = false">
            取消
          </el-button>
          <el-button
            type="primary"
            @click="editPassword()"
          >
            确定
          </el-button>
        </template>
      </el-dialog>
    </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Breadcrumb from '@/components/Breadcrumb'
import Hamburger from '@/components/Hamburger'
import api from '@/api/system/user'
export default {
  components: {
    Breadcrumb,
    Hamburger
  },
  data () {
    const passwordRule = (rule, value, callback) => {
      if(value == '' || value == undefined || value == null){
        callback(new Error('密码不能为空!'))
      }if (!/^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,20}$/.test(value)) {
          callback(new Error('格式有误！请输入以字母+数字组成的6-20位密码'))
        }  else {
          callback()
        }
    }
    const commitPasswordRule = (rule, value, callback) => {
      if(value == '' || value == undefined || value == null) value=''
      if(value!==this.userForm.newPassword){
        callback(new Error('两次输入密码不一致！'))
      }else{
        callback()
      }
    }
    return {
      editPasswordVisible: false,
      userForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      rules: {
        oldPassword: [ { required: true, message: '密码不能为空', trigger: 'blur' },
          { required: true, pattern: /^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,20}$/, message: '格式有误！请输入以字母+数字组成的6位密码', trigger: 'blur'} ],
        newPassword:[ { required: true, validator: passwordRule, trigger: 'blur'} ],
        confirmPassword: [ { required: true, validator: commitPasswordRule, trigger: 'blur'} ],
      }
    }
  },
  computed: {
    ...mapGetters([
      'sidebar',
      'name'
    ])
  },
  methods: {
    toggleSideBar () {
      this.$store.dispatch('app/toggleSideBar')
    },
    dialogClose () {
      this.userForm = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    },
    openDialog () {
      this.editPasswordVisible = true
    },
    editPassword () {
      this.editPasswordVisible = true
      this.$refs['userForm'].validate(async (valid) => {
        if (valid) {
          await api.changePassword(this.userForm)
        this.$message({
              message: '修改密码成功,请重新登录',
              type: 'success'
            })
            this.logout()
        }
      })
    },
    async logout () {
      await this.$confirm(
        '确定要退出吗?',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
        }
      ).then(() => {
        console.log(this.$route)
        this.$store.dispatch('user/logout')
        this.$router.push(`/login?redirect=${this.$route.fullPath}`)
        this.$message({
              type: 'success',
              message: '退出成功!',
            })
      }).catch(() => {
            this.$message({
              type: 'info',
              message: '已取消退出',
            })
          })

    }
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  height: 50px;
  line-height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0px 5px 5px rgba(37,104,219,0.1);

  .hamburger-container {
    line-height: 48px;
    height: 100%;
    float: left;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color:transparent;

    &:hover {
      background: rgba(0, 0, 0, .025)
    }
  }

  .breadcrumb-container {
    float: left;
    margin-left:0px
  }

  .right-menu {
    float: right;
    height: 100%;
    line-height: 50px;

    &:focus {
      outline: none;
    }

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      height: 100%;
      font-size: 18px;
      color: #5a5e66;
      vertical-align: text-bottom;

      &.hover-effect {
        cursor: pointer;
        transition: background .3s;

        &:hover {
          background: rgba(0, 0, 0, .025)
        }
      }
    }
  }
}
</style>
