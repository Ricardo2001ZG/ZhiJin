import request from '@/utils/request'
import {menulist} from '@/store/modules/menulist'

const api = {}

//获取登陆验证码
api.getLoginCode = (data) => {
    return  request({
        url: '/getLoginCode',
        method: 'Post',
        params:data
    })
}
//检验登录验证码
api.checkLoginCode = (data) => {
    return  request({
        url: '/checkLoginCode',
        method: 'post',
        data
    })
}

let result={
    token:123456,
    frontendPrivilegeList:menulist
}

api.login = (data) => {
    data.loginType = 1
    return  new Promise((resolve)=>{
        resolve(result)
    })
    // request({
    //     url: '/login',
    //     method: 'post',
    //     data
    // })
}



// 修改密码
api.changePassword = (data) => {
    return request({
        url: '/user/changePassword',
        method: 'post',
        data
    })
}

api.logout = () => {
    return request({
        url: '/system/user/logout',
        method: 'post'
    })
}

// 获取用户列表
api.findUser = (data) => {
    return request({
        url: '/user/findUser',
        method: 'post',
        data
    })
}
// 获取单个用户
api.getUser = (data) => {
    return request({
        url: '/user/getUser',
        method: 'get',
        params: data
    })
}
// 添加/编辑用户
api.saveUser = (data) => {
    return request({
        url: '/user/saveUser',
        method: 'post',
        data
    })
}

// 获取角色字典
api.findRoleDict = (data) => {
    return request({
        url: '/role/findRoleDict',
        method: 'get',
        params: data
    })
}
// 获取部门字典
api.findDeptDict = (data) => {
    return request({
        url: '/dept/findDeptDict',
        method: 'get',
        params: data
    })
}

// 获取前端权限字典
api.findFrontendPrivilegeDict = (data) => {
    return request({
        url: '/privilege/findFrontendPrivilegeDict',
        method: 'get',
        params: data
    })
}

// 获取后端权限字典
api.findAuthorityDict = (data) => {
    return request({
        url: '/backendAuthority/findAuthorityDict',
        method: 'get',
        params: data
    })
}

api.delUser = (data) => {
    return request({
        url: '/user/delUser',
        method: 'get',
        params: data
    })
}

export default api
