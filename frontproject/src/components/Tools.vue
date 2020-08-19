<template>
  <div id="Background_H">
    <TopTools></TopTools>
    <Aside id="Tools_aside"></Aside>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
    import TopTools from "./TopTools";
    import Aside from "./Aside";
    import NewFile from "./NewFile";
    export default {
        name: "Tools",
      components: {NewFile, Aside, TopTools},
    }
</script>
<style>
  #Background_H {
    background-image: linear-gradient(120deg,#ffffff,#AFEEEE);
    width: 100%;
    height: 100%;
  }

  /*#Tools_aside {*/
  /*  min-height: 100%;*/
  /*}*/
</style>
