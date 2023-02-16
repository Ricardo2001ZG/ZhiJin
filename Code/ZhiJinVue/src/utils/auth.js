import Cookies from 'js-cookie'

const TokenKey = 'token'

export function getToken () {
    return Cookies.get(TokenKey)
}

export function setToken (token) {
    return Cookies.set(TokenKey, token)
}

export function getMenulist () {
    return JSON.parse(localStorage.getItem('menulist'))
}

export function setMenulist (menulist) {
    console.log(menulist)
    return localStorage.setItem('menulist', JSON.stringify(menulist))
}

export function getUsername () {
    return JSON.parse(localStorage.getItem('username'))
}

export function setUsername (username) {
    return localStorage.setItem('username', JSON.stringify(username))
}

export function removeToken () {
    console.log('清除')

    return Cookies.remove(TokenKey)
}
