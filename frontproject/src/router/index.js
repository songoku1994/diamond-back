import Vue from 'vue'
import VueRouter from 'vue-router'
import axios from 'axios'
import store from "../store";
Vue.use(VueRouter)
const routes= [
  {
    path:'',
    redirect:'/login',
    meta:{
      title:"登录-金刚石文档",
      requireAuth:false
    }
  },
  {
    path:'/login',
    component:()=>import('../components/Login'),
    meta:{
      title:"登录-金刚石文档",
      requireAuth:false
    }
  },
  {
    path:'/login/:user',
    component:()=>import('../components/Login'),
  },
  {
    path:'/register',
    component:()=>import('../components/Register'),
    meta:{
      title:"注册-金刚石文档",
      requireAuth:false
    }
  },
  {
    path:'/tools',
    component:()=>import('../components/Tools'),
    meta:{
      title:"首页-金刚石文档",
      requireAuth:true
    },
    children:[
      {
        path:'home',
        component:()=>import('../components/Home'),
        meta:{
          title:"首页-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'userinfo',
        component:()=>import('../components/UserInfo'),
        meta:{
          title:"我的信息-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'bin',
        component:()=>import('../components/Bin')
      },
      {
        path:'usermessage',
        component:()=>import('../components/UserMessage'),
        meta:{
          title:"我的消息-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'userteam',
        component:()=>import('../components/UserTeam'),
        meta:{
          title:"我的团队-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'userfile',
        component:()=>import('../components/UserFile')
      },
      {
        path:'editfile',
        component:()=>import('../components/Editfile'),
        meta:{
          title:"我的文档-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'searchfile',
        component:()=>import('../components/SearchFile'),
        meta:{
          title:"我的文档-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'usercollection',
        component:()=>import('../components/UserCollection'),
        meta:{
          title:"我的文档-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'ownfile',
        component:()=>import('../components/ownfile'),
        meta:{
          title:"我的文档-金刚石文档",
          requireAuth:true
        }
      },
      {
        path:'worktrend',
        component:()=>import('../components/Worktrend'),
        meta:{
          title:"我的文档-金刚石文档",
          requireAuth:true
        }
      }

    ]
  },

]
const router = new VueRouter(
  { routes
  }
)

router.beforeEach(
  (to,from,next)=>{
      if(to.meta.requireAuth){
        axios({
          url:"http://127.0.0.1:8000/Authentication",
          methods: "get",
          params:{
            name:store.state.name,
            token:store.state.token
          }
        }).then(res =>{
          console.log(res)
            if(res.data.state === 1)
            {
                document.title=to.meta.title
                next()

            }else{
              alert("认证过期，重新登录!")
            }
        })

      }else{
        document.title=to.meta.title
        next()
      }
  }
)


export default router
