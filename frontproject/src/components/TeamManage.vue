<template>
  <div class="info" style="width: 70%;margin-top: 30px;float: left">
    <div>
      <h1>{{Team.tname}}</h1>
      <el-radio-group v-model="SelectMode">
        <el-radio-button :label="true" border>
          文档
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="SelectMode" @click="NewTeamFileVisible=true"></el-button>
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="!SelectMode"></el-button>
        </el-radio-button>
        <el-radio-button :label="false" border>
          成员
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="!SelectMode" @click="SearchNewMemberVisible=true"></el-button>
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="SelectMode"></el-button>
        </el-radio-button>
      </el-radio-group>
    </div>
    <div style="border-bottom:2px solid #CCC;padding-top: 30px"></div>
    <div>
      <el-table v-show="SelectMode" :data="TeamFile" stripe border>
        <el-table-column prop="fields.title" label="标题"></el-table-column>
        <el-table-column prop="fields.lastedittime" label="最近修改日期"></el-table-column>
        <el-table-column prop="fields.createtime" label="创建日期"></el-table-column>
        <el-table-column prop="fields.uid" label="作者"></el-table-column>
        <el-table-column width="175">
          <template slot-scope="scope">
            <el-button-group>
              <el-button type="primary" @click="Config(scope.$index)" icon="el-icon-edit"></el-button>
              <el-button type="success" @click="CollectFile(scope.$index)" :icon="Star(scope.row)" circle></el-button>
              <el-button type="danger" @click="" icon="el-icon-delete" :disabled="!scope.row.AbleToConfig"></el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      <el-table v-show="!SelectMode" :data="TeamMember" stripe border>
        <el-table-column prop="name" label="用户名"></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
        <el-table-column prop="createtime" label="创建日期"></el-table-column>
        <el-table-column width="190">
          <template slot-scope="scope">
            <el-button-group>
              <el-button type="info" @click="" icon="el-icon-info"></el-button>
              <el-button type="primary" @click="" icon="el-icon-chat-line-round"></el-button>
              <el-button type="danger" @click="" icon="el-icon-delete" :disabled="!isCaptain"></el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <NewTeamFile v-if="NewTeamFileVisible"
                 :visible="NewTeamFileVisible"
                 :team-id="Team.tid"
                 :team-name="Team.tname"
                 :team="Team"
                 @cancel="NewTeamFileVisible=false"></NewTeamFile>
    <ConfigOldTeamFile v-if="ConfigOldTeamFileVisible"
                       :visible="ConfigOldTeamFileVisible"
                       :title="SelectArticle.fields.title"
                       :team-id="Team.tid"
                       :team="Team"
                       :team-name="Team.tname"
                       :article-authority="SelectArticle.fields.visibility"
                       :simple-message="SelectArticle.fields.message"
                       :revise="SelectArticle.fields.commentGranted"
                       :aid="SelectArticle.pk"
                       @cancel="ConfigOldTeamFileVisible=false"></ConfigOldTeamFile>
    <SearchNewMember :visible="SearchNewMemberVisible"
                     :team="Team"
                     @cancel="SearchNewMemberVisible=false"></SearchNewMember>
  </div>
</template>
<script>
  import NewTeamFile from "./NewTeamFile";
  import ConfigOldTeamFile from "./ConfigOldTeamFile";
  import axios from 'axios'
  import SearchNewMember from "./SearchNewMember";
  export default {
    name: "TeamManage",
    created() {
      // this.TeamId=this.$route.query.Team.TeamId
      // this.TeamName=this.$route.query.Team.TeamName
      this.Team=JSON.parse(this.$route.query.Team)
      axios.all([
        axios({
        url:'http://127.0.0.1:8000/getTeamMembers',
        params:{
          name:this.$store.state.name,
          token:this.$store.state.token,
          tid:this.Team.tid
        }
      }),axios({
        url:'http://127.0.0.1:8000/getTeamArticles',
        params:{
          name:this.$store.state.name,
          token:this.$store.state.token,
          tid:this.Team.tid
        }
      })]).then((res)=>{
        console.log(res)
        this.TeamMember=this.TeamMember.concat(res[0].data.userList)
        for(let i of res[1].data.ArticleList){
          i.fields.lastedittime=this.TimeFormat(i.fields.lastedittime)
          i.fields.createtime=this.TimeFormat(i.fields.createtime)
        }
        this.TeamFile=this.TeamFile.concat(res[1].data.ArticleList)
      })
    },
    data(){
      return{
        Team:null,
        // TeamId:24601,
        NewTeamFileVisible:false,
        ConfigOldTeamFileVisible:false,
        SearchNewMemberVisible:false,
        // TeamName:'大北航帝国',
        SelectMode:true,
        SelectArticle:null,
        TeamMember:[],
        TeamFile:[],
        isCaptain:false
      }
    },
    methods:{
      TimeFormat(str){
        return str.substring(0,10)+" "+str.substring(11,19)
      },
      Star(row){
        if(row.Collected===true)
          return 'el-icon-star-on'
        else
          return 'el-icon-star-off'
      },
      CollectFile(index){

      },
      Config(index){
        this.SelectArticle=this.TeamFile[index]
        console.log(this.SelectArticle)
        this.ConfigOldTeamFileVisible=true
      },
    },
    components:{SearchNewMember, ConfigOldTeamFile, NewTeamFile},
  }
</script>
<style scoped>
  .info{
    margin-left: 8%;
  }
</style>
