import Vue from 'vue'
import Router from 'vue-router'
import test from '../components/test'
import register from '../components/register'
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '',
      name: 'test',
      component: test
    },
    {
      path:'/register',
      name:'register',
      component: register
    }
  ]
})
