import router from './router'
import store from './store'
import { Message } from 'element-plus'
import { getToken } from '@/utils/auth' // get token from cookie
import getPageTitle from '@/utils/get-page-title'


const whiteList = ['/login'] // no redirect whitelist

router.beforeEach(async (to, from, next) => {
    // start progress bar

    // set page title
    document.title = getPageTitle(to.meta.title)

    // determine whether the user has logged in
    const hasToken = getToken()
    console.log(hasToken)
    if (hasToken) {
        if (to.path === '/login') {
            // if is logged in, redirect to the home page
            next({ path: '/' })
        } else {
            const hasGetUserInfo = store.getters.name
            if (hasGetUserInfo) {
                next()
            } else {
                next()
            }
        }
    } else {
        /* has no token*/
        console.log(from)
        console.log(to)
        if (whiteList.indexOf(to.path) !== -1) {
            console.log('白名单')
            // in the free login whitelist, go directly
            next()
        } else {
            console.log(to)
            // other pages that do not have permission to access are redirected to the login page.
            next(`/login?redirect=${to.path}`)
            // next()
        }
    }
})

router.afterEach(() => {
    // finish progress bar
})
