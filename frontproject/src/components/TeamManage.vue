<template>
  <div class="info" style="width: 70%;margin-top: 30px;float: left">
    <div>
      <h1>{{TeamName}}</h1>
      <el-radio-group v-model="SelectMode">
        <el-radio-button :label="true" border>
          文档
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="SelectMode" @click="NewTeamFilevisible=true"></el-button>
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="!SelectMode"></el-button>
        </el-radio-button>
        <el-radio-button :label="false" border>
          成员
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="!SelectMode"></el-button>
          <el-button style="color: white" type="text" icon="el-icon-circle-plus" v-if="SelectMode"></el-button>
        </el-radio-button>
      </el-radio-group>
    </div>
    <div style="border-bottom:2px solid #CCC;padding-top: 30px"></div>
    <div>
      <el-table v-show="SelectMode" :data="TeamFile" stripe border>
        <el-table-column prop="Name" label="标题"></el-table-column>
        <el-table-column prop="LastEditDate" label="最近修改日期"></el-table-column>
        <el-table-column prop="CreateDate" label="创建日期"></el-table-column>
        <el-table-column prop="Author" label="作者"></el-table-column>
        <el-table-column width="210">
          <template slot-scope="scope">
            <el-button-group>
              <el-button type="primary" @click="" icon="el-icon-edit"></el-button>
              <el-button type="info" @click="" icon="el-icon-setting" :disabled="scope.row.AbleToConfig"></el-button>
              <el-button type="danger" @click="" icon="el-icon-delete" :disabled="scope.row.AbleToConfig"></el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      <el-table v-show="!SelectMode" :data="TeamMember" stripe border>
        <el-table-column prop="Name" label="用户名"></el-table-column>
        <el-table-column prop="LastLoginDate" label="最近登录日期"></el-table-column>
        <el-table-column prop="JoinDate" label="加入日期"></el-table-column>
        <el-table-column width="210">
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
    <NewTeamFile v-if="NewTeamFilevisible" :visible="NewTeamFilevisible" :team-id="TeamId" :team-name="TeamName" @cancel="NewTeamFilevisible=false"></NewTeamFile>
  </div>
</template>
<script>
  import NewTeamFile from "./NewTeamFile";
  export default {
    name: "TeamManage",
    created() {
      let Team=this.$route.query.Team
      this.TeamId=Team.TeamId
      this.TeamName=Team.TeamName
    },
    data(){
      return{
        TeamId:24601,
        NewTeamFilevisible:false,
        TeamName:'大北航帝国',
        SelectMode:true,
        TeamMember:[
          {Name:'马冬什么',LastLoginDate:'2020/8/12',JoinDate:'2018/9/1'},
          {Name:'马什么梅',LastLoginDate:'2020/8/11',JoinDate:'2018/9/2'},
          {Name:'什么冬梅',LastLoginDate:'2020/8/1',JoinDate:'2018/9/3'},
        ],
        TeamFile:[
          {Name:'北航帝国简史',LastEditDate:'2020/8/14',CreateDate:'2010/2/30',Author:'徐惠彬',AbleToConfig:true},
          {Name:'毛泽东选集',LastEditDate:'1990/7/1',CreateDate:'1944/1/1',Author:'毛泽东',AbleToConfig:false},
        ],
        isCaptain:false
      }
    },
    components:{NewTeamFile},
  }
</script>
<style scoped>
  .info{
    margin-left: 8%;
  }
</style>
