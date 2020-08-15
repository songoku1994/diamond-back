<template>
  <div class="info" style="width: 70%;margin-top: 30px;float: left">
    <div style="float: left">
      <h1 style="float: left">{{username}}的文档</h1>
    </div>
    <div style="border-bottom:2px solid #CCC;padding-top: 100px"></div>
    <div >
      <el-table :data="AllFile" stripe border>
        <el-table-column prop="Name" label="文件名" ></el-table-column>
        <el-table-column prop="Author" label="作者"></el-table-column>
        <el-table-column prop="LastViewDate" label="上次浏览日期" ></el-table-column>
        <el-table-column prop="CreateDate" label="创建日期"></el-table-column>
        <el-table-column width="225">
          <template slot-scope="scope">
            <el-button type="primary" @click="EditFile(scope.row)" icon="el-icon-edit" circle></el-button>
            <el-button type="info" @click="ConfigFile(scope.row)" icon="el-icon-setting" circle></el-button>
            <el-button type="success" @click="CollectFile(scope.row)" icon="el-icon-star-on" circle></el-button>
            <el-button type="danger" @click="DeleteFile(scope.row)" icon="el-icon-delete" circle></el-button>
          </template>
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
          obj.TeamId=a.fields.tid
          obj.Title = a.fields.title
          obj.SimpleMessage = a.fields.message
          obj.Authority = a.fields.visibility
          obj.Revise = a.fields.commentGranted? 1:0
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
          if(row.Name===this.AllFile[i].Name&&row.LastViewDate===this.AllFile[i].LastViewDate&&row.CreateDate===this.AllFile[i].CreateDate&&row.Author===this.AllFile[i].Author){
            return i
          }
        }
        return -1
      },
    TimeFormat(str){
        return str.substring(0,10)+" "+str.substring(11,19)
    },
      EditFile(row){
        let i=this.FindFile(row)
        console.log(this.AllFile[i].aid)

        this.$router.push({
          path:'/tools/editfile',
          query:{
            NewFile:this.AllFile[i]
          }
        })
      },
      DeleteFile(row){
        this.$confirm('此操作将删除该文档, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          axios({
            url:'/deleteArticle/'+this.AllFile[this.FindFile(row)].aid,
            params:{
              name:this.$store.state.name,
              token:this.$store.state.token
            }
          }).then(res=>{
            this.AllFile.splice(this.FindFile(row),1)
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
          })
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消删除'
          });
        });
      },
      ConfigFile(row){
        console.log(row)
      },
      CollectFile(row){

      }


    }
  }
</script>

<style scoped>
  .info{
    margin-left: 8%;
  }
</style>
