// import { logina, logout, getInfo } from '@/api/system/user'
import api from '@/api/system/user'
import { getToken, setToken, getMenulist, setMenulist, getUsername, setUsername, removeToken } from '@/utils/auth'
// import { resetRouter } from '@/router'



const getDefaultState = () => {
    return {
        token: getToken(),
        name: getUsername(),
        avatar: '',
        menulist: getMenulist()
    }
}

const state = getDefaultState()

const mutations = {
    RESET_STATE: (state) => {
        Object.assign(state, getDefaultState())
    },
    SET_TOKEN: (state, token) => {
        state.token = token
    },
    SET_NAME: (state, name) => {
        state.name = name
    },
    SET_AVATAR: (state, avatar) => {
        state.avatar = avatar
    },
    SET_MENULIST: (state, menulist) => {
        state.menulist = menulist
    }
}

const actions = {
    // user login
    login({ commit }, userInfo) {
        const { username, password, verification } = userInfo
        return new Promise((resolve, reject) => {
            api.login({ username: username.trim(), password: password, verification: verification }).then(response => {
                console.log(response)
                commit('SET_TOKEN', response.token)
                commit('SET_NAME', username)
                commit('SET_MENULIST', response.frontendPrivilegeList)
                setToken(response.token)
                setMenulist(response.frontendPrivilegeList)
                setUsername(username)
                resolve()
            }).catch(error => {
                reject(error)
            })
        })
    },
    codeLogin({ commit }, code) {
        console.log(code)
        return new Promise((resolve, reject) => {
            api.codeLogin({ code: code }).then(response => {
                console.log(response)
                commit('SET_TOKEN', response.token)
                commit('SET_NAME', response.username)
                commit('SET_MENULIST', response.frontendPrivilegeList)
                setToken(response.token)
                setMenulist(response.frontendPrivilegeList)
                setUsername(response.username)
                resolve()
            }).catch(error => {
                reject(error)
            })
        })
    },

    // get user info
    // getInfo({ commit, state }) {
    //     return new Promise((resolve, reject) => {
    //         getInfo(state.token).then(response => {
    //             const { data } = response

    //             if (!data) {
    //                 return reject('Verification failed, please Login again.')
    //             }

    //             const { name, avatar } = data

    //             commit('SET_NAME', name)
    //             commit('SET_AVATAR', avatar)
    //             resolve(data)
    //         }).catch(error => {
    //             reject(error)
    //         })
    //     })
    // },

    // user logout
    logout({ commit, state }) {
        return new Promise((resolve, reject) => {
            // api.logout(state.token).then(() => {
            removeToken() // must remove  token  first
            // resetRouter()
            commit('RESET_STATE')
            resolve()
            // }).catch(error => {
            //     reject(error)
            // })
        })
    },

    // remove token
    resetToken({ commit }) {
        return new Promise(resolve => {
            removeToken() // must remove  token  first
            commit('RESET_STATE')
            resolve()
        })
    }
}

export default {
    namespaced: true,
    state,
    mutations,
    actions
}