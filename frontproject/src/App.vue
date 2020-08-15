<template>
<!--  <div>-->
<!--    <TopTools/>-->
<!--    <Aside/>-->
<!--    <TeamManage/>-->
<!--  </div>-->
    <router-view/>
</template>
<script>
  import test from './components/test'
  import TopTools from "./components/TopTools";
  import Aside from "./components/Aside";
  import TeamManage from "./components/TeamManage";
  export default {
  name: 'App',
    components:{TeamManage, Aside, TopTools, test}
}

</script>

<style>
</style>
