<template>
  <div class="info" style="width: 70%;margin-top: 30px;float: left">
    <div style="float: left">
      <h1 style="float: left">我的回收站</h1>
    </div>
    <div style="border-bottom:2px solid #CCC;padding-top: 100px"></div>
    <div>
      <h2 style="float: left">未读消息</h2>
      <el-table :data="BinData" stripe border>
        <el-table-column prop="Name" label="文件名"></el-table-column>
        <el-table-column prop="DeleteDate" label="删除日期"></el-table-column>
        <el-table-column prop="CreateDate" label="创建日期"></el-table-column>
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
  export default {
    name: "Bin",
    created() {
      /*这里写后端代码（初始化）








       */
    },
    data(){
      return{
        BinData:[
          {Name:'我是垃圾甲',DeleteDate:'2020/8/10',CreateDate:'2020/1/1'},
          {Name:'我是垃圾乙',DeleteDate:'2012/12/21',CreateDate:'2020/2/2'},
          {Name:'我是垃圾丙',DeleteDate:'2020/2/30',CreateDate:'2020/3/3'},
        ],
        ShowData:'',
        ShowMessage:'嘤嘤嘤',
        DialogVisible:false
      }
    },
    methods:{
      Recover(row) {
        this.$confirm('此操作将恢复该文件, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          /*这里写后端代码（恢复文档）








         */
          this.BinData.splice(this.FindRow(row),1)
          this.$message({
            type: 'success',
            message: '恢复成功!'
          });
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
          if(row.Name==this.BinData[i].Name&&row.DeleteDate==this.BinData[i].DeleteDate){
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
