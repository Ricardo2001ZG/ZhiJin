import axios from 'axios'
import { ElMessageBox, ElMessage } from 'element-plus'
import store from '@/store'
import route from '@/router/index'
import { getToken } from '@/utils/auth'
// import { checkUrl } from '@/checkApi'
console.log(process.env)
    // create an axios instance
const service = axios.create({
    baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
    // withCredentials: true, // send cookies when cross-domain requests
    timeout: 120000 // request timeout
})

// request interceptor
service.interceptors.request.use(
    config => {
        console.log('config.url', config.url)
        // console.log(config.url.indexOf('/network/getData'))
        // if (checkUrl(config.url)) {
        //     config.baseURL = 'http://192.168.10.231:9999'
        // }
        // if (config.url.indexOf('topology/getTopologyCore') || config.url.indexOf('topology/getNodeData')) {
        //     config.baseURL = 'http://192.168.10.191:8081'
        // }
        // do something before request is sent

        if (store.getters.token) {
            // let each request carry token
            // ['X-Token'] is a custom headers key
            // please modify it according to the actual situation
            // config.headers['X-Token'] = getToken()
            config.headers['Authorization'] = getToken()
        }
        return config
    },
    error => {
        // do something with request error
        console.log(error) // for debug
        return Promise.reject(error)
    }
)

// response interceptor
service.interceptors.response.use(
    /**
     * If you want to get http information such as headers or status
     * Please return  response => response
     */

    /**
     * Determine the request status by custom code
     * Here is just an example
     * You can also judge the status by HTTP Status Code
     */
    response => {
        console.log(response)
        if (response.headers['content-type'] === 'application/vnd.ms-excel;charset=utf-8') {
            return response.data
        }
        const res = response.data
        // 如果有code但code不为000000，或者没有code且err不为0的时候，请求有问题
        if ((res.code && res.code !== '000000')||(!res.code&&res.err!==0)) {
            console.log(res)
            ElMessage({
                message: res.msg || 'Error',
                type: 'error',
                duration: 5 * 1000
            })


            if (res.code === 'A99003'||res.err===401||res.err===403||res.err===1001) {
                // to re-login
                ElMessageBox.confirm('登录凭证过期，是否重新登陆？', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    store.dispatch('user/resetToken').then(() => {
                        route.push('/login')
                        console.log(route)
                    })
                })
            }
            return Promise.reject(res)
        } else {
            return res.data
        }
        // return res.data;
    },
    error => {
        console.log('err' + error) // for debug
        ElMessage({
            ElMessage: error.ElMessage,
            type: 'error',
            duration: 5 * 1000
        })
        return Promise.reject(error)
    }
)

export default service
