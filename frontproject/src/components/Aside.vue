<template>
  <div id="Aside_bg">
    <div class="fixedBlock" v-if="isFixed">
      <el-col :span="3">
        <span v-for="i in 5">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
      </el-col>
    </div>
    <div id="fixedAside" :class="{fixedAside : isFixed}">
      <el-col :span="3">
      <el-menu
        :default-active="activeIndex"
        class="el-menu-vertical-demo"
        background-color="#f2fcfc"
        @open="handleOpen"
        @close="handleClose"
        :default-openeds="openeds">
        <div class="block"></div>
        <div id="test">
          <el-menu-item v-for="(item,i) in name" :key="i" :index="item.id" @click="handle(item.url)">
            <i :class="item.icon"></i>
            <span slot="title">{{item.title}}</span>
          </el-menu-item>
          <el-submenu index="3">
            <template slot="title">
              <i class="el-icon-location"></i>
              <span>我的空间</span>
            </template>
            <el-menu-item-group>
              <el-menu-item v-for="(item,i) in zone" :key="i" :index="item.id" @click="handle(item.url)">
                <div> <!-- :class="{MessageClass : item.id=='4-2'&&MessageNum!=0}" -->
                  <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                  <span v-if="item.id==='4-2' && MessageNum!=0">&nbsp;&nbsp;</span>
                  <span slot="title">{{item.title}}</span>
                  <el-badge :value="MessageNum" :max="99" v-if="item.id==='4-2' && MessageNum!=0"></el-badge>
                  <el-button type="text" icon="el-icon-circle-plus" v-if="item.id==='4-3'" @click="NewFile"></el-button>
                  <span v-if="item.id!='4-3'">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                </div>
              </el-menu-item>
            </el-menu-item-group>
          </el-submenu>
        </div>
      </el-menu>
    </el-col>
<!--    <div v-if="NewFileVisible">-->
      <NewFile :visible="NewFileVisible" @cancel="NewFileVisible=false"></NewFile>
<!--    </div>-->
    </div>

  </div>
</template>

<script>
  import NewFile from "./NewFile";
  import axios from "axios";
  export default {
    name: "Aside",
    components: {NewFile},
    data() {
      return{
        openeds: ['3'],
        MessageNum: 0,
        isFixed: false,
        offsetTop: 0,
        name: [
          {icon: "el-icon-edit", title: "工作台", url:'/tools/home',id:"1"},
          {icon: "el-icon-share", title: "团队管理", url:'/tools/userteam',id:"2"},
        ],
        zone: [
          {icon: "el-icon-edit", title: "个人信息", url:'/tools/userinfo', id:"4-1"},
          {icon: "el-icon-s-comment", title: "我的消息", url:'/tools/usermessage', id:"4-2"},
          {title: "我的文档", url:'/tools/userfile', id:"4-3"},
          {icon: "el-icon-delete", title: "我的回收站", url:'/tools/bin', id:"4-4"},
        ],
        activeIndex: "1",
        openson: this.isson === "true",
        NewFileVisible:false
      }
    },
    mounted() {
      this.offsetTop = document.querySelector("#fixedAside").offsetTop;
      window.addEventListener('scroll', this.handleScroll);
    },
    methods: {
      handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop;
        if (scrollTop >= this.offsetTop) {
          this.isFixed = true;
        } else {
          this.isFixed = false;
        }
      },
      NewFile(){
        console.log(123321)
        this.NewFileVisible=true
      },
      handleOpen(key, keyPath) {
        console.log(key, keyPath);
      },
      handleClose(key, keyPath) {
        console.log(key, keyPath);
      },
      handle(url) {
        if(this.$route.path != url)
          this.$router.push(url)
      },
      newfile() {
        this.$notify({
          title: '提示',
          message: '这是一条不会自动关闭的消息',
        });
      }
    },
    created() {
      console.log("正在搞消息")
      axios({
        url: "http://112.124.17.52/getMessagenum",
        method:"get",
        params: {
          name:this.$store.state.name,
          token:this.$store.state.token
        }
      }).then(res => {
        console.log(res)
        this.MessageNum = res.data.messagenum
      })
    },
    destroyed () {
      window.removeEventListener('scroll', this.handleScroll); // 离开页面 关闭监听 不然会报错
    }
  }
</script>

<style scope>
  .MessageClass {
    margin-left: 10px;
  }

  #fixedAside {
    z-index: 99;
    background-color: #D3D3D3;
  }

    .fixedAside {
        position: fixed;
        z-index: 90;
        top: 0;
        height: 60px;
        width: 100%;
    }

  .newbutton {
    width: 30px;
    height: 30px;
    background-color: rgb(211, 211, 211);
    color:darkblue;
  }

  #test {
    text-align: center;
    background-color: #ffffffbd;
  }

  #wid {
    width: 50px;
  }

  #third {
    margin-top: 10px;
  }

  #aside {
    font-size: 20px;
    font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif;;
  }

  .block {
    height: 200px;
  }

</style>
