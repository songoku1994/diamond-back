<template>
    <div class="info" style="width: 70%;margin-top: 30px;float: left">
      <div style="float: left">
        <h1 style="float: left">{{username}}的文档</h1>
      </div>
      <div style="border-bottom:2px solid #CCC;padding-top: 100px"></div>
      <div >
        <h2 style="float: left">最近浏览</h2>
        <el-table :data="RecentFile" stripe border>
          <el-table-column prop="Name" label="文件名" ></el-table-column>
          <el-table-column prop="Author" label="作者" ></el-table-column>
          <el-table-column prop="LastViewDate" label="上次浏览日期"></el-table-column>
          <el-table-column prop="CreateDate" label="创建日期"></el-table-column>
          <el-table-column width="161">
            <el-button-group slot-scope="scope" width="161">
              <el-button type="primary" @click="EditFile(scope.row)">编辑</el-button>
              <el-button type="danger" @click="DeleteFile(scope.row)">删除</el-button>
            </el-button-group>
          </el-table-column>
        </el-table>
      </div>
      <div >
        <h2 style="float: left">全部文档</h2>
        <el-table :data="AllFile" stripe border>
          <el-table-column prop="Name" label="文件名" ></el-table-column>
          <el-table-column prop="Author" label="作者"></el-table-column>
          <el-table-column prop="LastViewDate" label="上次浏览日期" ></el-table-column>
          <el-table-column prop="CreateDate" label="创建日期"></el-table-column>
          <el-table-column width="161">
            <el-button-group slot-scope="scope" width="161">
              <el-button type="primary" @click="EditFile(scope.row)">编辑</el-button>
              <el-button type="danger" @click="DeleteFile(scope.row)">删除</el-button>
            </el-button-group>
          </el-table-column>
        </el-table>
      </div>
    </div>
</template>

<script>
import axios from 'axios'
  export default {
    name: "UserFile",
    created() {
      axios({
        url:"http://127.0.0.1:8000/getAllArticle",
        method:"get",
        params:{
          name:this.$store.state.name,
          token:this.$store.state.token
        }
      }).then(res =>{
        console.log( res.data.articles[0])
        for( let a of res.data.articles)
        {
          console.log(typeof a.fields.title)
          let obj = {}
          obj.Name = a.fields.title
          obj.LastViewDate = '2020/8/11 18:10'
          obj.CreateDate = this.TimeFormat(a.fields.createtime)
          obj.Author = this.$store.state.name
          obj.aid = a.pk
          this.AllFile.push(obj)
        }
      })
    },
    data(){
      return{
        RecentFile:[
          {Name:'北航帝国简史',LastViewDate:'2020/8/11 18:10',CreateDate:'2010/2/30',Author:'徐惠彬'},
        ],
        AllFile:[
          // {Name:'北航帝国简史',LastViewDate:'2020/8/11 18:10',CreateDate:'2010/2/30',Author:'徐惠彬'},
          // {Name:'毛泽东选集',LastViewDate:'2020/8/11 20:21',CreateDate:'1944/1/1',Author:'毛泽东'},
        ],
        username:'我',
      }
    },
    methods:{
      FindFile(row){
        for(let i=0;i<this.AllFile.length;i++)
        {
          if(row.Name===this.AllFile[i].Name&&row.LastViewDate===this.AllFile[i].LastViewDate&&row.CreateDate===this.AllFile[i].CreateDate&&row.Author==this.AllFile[i].Author){
            return i
          }
        }
        return -1
      },
    TimeFormat(str){
        return str.substring(0,10)+" "+str.substring(11,19)
    },
      //EditFile(row){
      //   let i=this.FindFile(row)
      //   axios({
      //     url:"http://127.0.0.1:8000/getAllArticle",
      //     method:"get",
      //     params:{
      //       name:this.$store.state.name,
      //       token:this.$store.state.token
      //     }
      //   }).then(res =>{
      //     console.log( res.data.articles[0])
      //     for( let a of res.data.articles)
      //     {
      //       console.log(typeof a.fields.title)
      //       let obj = {}
      //       obj.Name = a.fields.title
      //       obj.LastViewDate = '2020/8/11 18:10'
      //       obj.CreateDate = this.TimeFormat(a.fields.createtime)
      //       obj.Author = this.$store.state.name
      //       obj.aid = a.pk
      //       this.AllFile.push(obj)
      //     }
      //   })
      //   console.log(this.AllFile[i].aid)
      //
      //   this.$router.push({
      //     path:'/tools/editfile',
      //     query:{
      //       file:this.AllFile[i]
      //     }
      //   })
      // },
      DeleteFile(row){
        let i=this.FindFile(row)
        axios({
          url:"http://127.0.0.1:8000/deleteArticle/"+this.AllFile[i].aid,
          method:"get",
          params:{
            name:this.$store.state.name,
            token:this.$store.state.token,
            aid:this.AllFile[i].aid
          }
        }).then(res =>{
          alert(res.data.msg)
        })
        location.reload()
      },
    }
  }
</script>

<style scoped>
  .info{
    margin-left: 8%;
  }
</style>
