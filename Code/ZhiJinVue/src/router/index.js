import { createRouter, createWebHashHistory } from "vue-router";
import Layout from '@/layout'
const routes = [
  {
    path: "/login",
    component: () => import("@/views/login"),
    hidden: true,
  },

  {
    path: "/404",
    // component: () => import("@/views/404"),
    hidden: true,
  },

  {
    path: "/",
    component: Layout,
    redirect: "/login",
  },
  {
    path: "/home",
    component: Layout,
    redirect:'/home/index',
    meta: { title: "主页", meta: "/home" },
    children:[
      {
        path: "index",
        name: "home",
        component: () => import("@/views/Home"),
      }
    ]
  },
  {
    path: "/task",
    component: Layout,
    redirect:'/task/index',
    meta: { title: "任务", meta: "/task" },
    children:[
      {
        path: "index",
        name: "task",
        component: () => import("@/views/task"),
      }
    ]
  },

  // 404 page must be placed at the end !!!
  { path: "/:pathMatch(.*)*", redirect: "/404", hidden: true },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;
