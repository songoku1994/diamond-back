<template>
  <div class="info" style="width: 70%;margin-top: 30px;float: left">
    <div style="float: left">
      <h1 style="float: left">搜索结果:&nbsp;&nbsp;{{SearchResult.length}}项</h1>
    </div>
    <div style="border-bottom:2px solid #CCC;padding-top: 100px"></div>
    <div >
      <el-table :data="SearchResult" stripe border>
        <el-table-column prop="Name" label="文件名" ></el-table-column>
        <el-table-column prop="Author" label="作者"></el-table-column>
        <el-table-column prop="LastViewDate" label="上次浏览日期" ></el-table-column>
        <el-table-column prop="CreateDate" label="创建日期"></el-table-column>
        <el-table-column >
          <el-button-group slot-scope="scope">
            <el-button type="primary" @click="ViewFile(scope.row)">查看</el-button>
          </el-button-group>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
  export default {
    name: "UserFile",
    created() {
      /*这里写后端代码（初始化）








       */
    },
    data(){
      return{
        SearchResult:[
          {Name:'北航帝国简史',LastViewDate:'2020/8/11 18:10',CreateDate:'2010/2/30',Author:'徐惠彬'},
        ],
        SearchContent:'',
      }
    },
    methods:{
      FindFile(row){
        for(let i=0;i<this.AllFile.length;i++)
        {
          if(row.Name==this.AllFile[i].Name&&row.LastViewDate==this.AllFile[i].LastViewDate&&row.CreateDate==this.AllFile[i].CreateDate&&row.Author==this.AllFile[i].Author){
            return i
          }
        }
        return -1
      },
      ViewFile(row){
        /*后端代码（跳转至编辑界面）







         */
      },
    }
  }
</script>

<style scoped>
  .info{
    margin-left: 8%;
  }
</style>
