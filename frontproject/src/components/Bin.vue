<template>
  <div class="info" style="width: 70%;margin-top: 30px;float: left">
    <div style="float: left">
      <h1 style="float: left">我的回收站</h1>
    </div>
    <div style="border-bottom:2px solid #CCC;padding-top: 100px"></div>
    <div>
      <el-table :data="BinData" stripe border>
        <el-table-column prop="fields.title" label="文件名"></el-table-column>
        <el-table-column prop="fields.lastedittime" label="上次编辑日期"></el-table-column>
        <el-table-column prop="fields.createtime" label="创建日期"></el-table-column>
        <el-table-column width="217">
          <el-button-group slot-scope="scope" >
            <el-button type="primary" @click="Recover(scope.row)">恢复文件</el-button>
            <el-button type="danger" @click="FinalDelete(scope.row)">彻底删除</el-button>
          </el-button-group>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: "Bin",
  created() {
    axios({
      url:'/getAbandonedArticle',
      params:{
        name: this.$store.state.name,
        token: this.$store.state.token,
      }
    }).then(res=>{
      let array=res.data.articles
      for(let i=0;i<array.length;i++){
        array[i].fields.createtime=this.TimeFormat(array[i].fields.createtime)
        array[i].fields.lastedittime=this.TimeFormat(array[i].fields.lastedittime)
      }
      this.BinData=this.BinData.concat(array)
      console.log(array)
    })
  },
  data(){
    return{
      BinData:[],
      ShowData:'',
      ShowMessage:'嘤嘤嘤',
      DialogVisible:false
    }
  },
  methods:{
    TimeFormat(str){
      return str.substring(0,10)+" "+str.substring(11,19)
    },
    Recover(row) {
      this.$confirm('此操作将恢复该文件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios({
          url:'/articleRecover/'+row.pk,
          params:{
            name: this.$store.state.name,
            token: this.$store.state.token,
          }
        }).then(res=>{
          // console.log(res)
          this.BinData.splice(this.FindRow(row),1)
          this.$message({
            type: 'success',
            message: '恢复成功!'
          });
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消恢复'
        });
      });
    },
    FinalDelete(row){
      this.$confirm('此操作将永久删除该文件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        /*这里写后端代码（彻底删除）








       */
        this.BinData.splice(this.FindRow(row),1)
        this.$message({
          type: 'success',
          message: '删除成功!'
        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    FindRow(row){
      for(let i=0;i<this.BinData.length;i++){
        if(row.fields.content===this.BinData[i].fields.content&&row.fields.createtime===this.BinData[i].fields.createtime){
          return i
        }
      }
      return -1
    },
    MoreMessage(row){
      /*这里写后端代码（查看详情信息）
      将this.ShowMessage的值变为this.BinData[this.Find(row)]的详情信息







       */
      this.ShowData=this.BinData[this.FindRow(row)]
      this.DialogVisible=true
    },
    AllDelete(){

      this.$confirm('此操作将删除所有文档, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        /*这里写后端代码（删除全部文档）








       */
        this.BinData.splice(0,this.BinData.length)
        this.$message({
          type: 'success',
          message: '全部删除!'
        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    AllRecover(){

      this.$confirm('此操作将恢复所有文档, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        /*这里写后端代码（恢复全部文档）








       */
        this.BinData.splice(0,this.BinData.length)
        this.$message({
          type: 'success',
          message: '全部恢复!'
        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消恢复'
        });
      });
    },
  },
}
</script>

<style scoped>
.info{
  margin-left: 8%;
}
.button{
  width: 100px;
}
</style>
