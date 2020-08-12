<template>
<div>
  <button @click="show_users">我是一个按钮</button>
  <ul>
    <li v-for="item in person">
      {{item}}
    </li>
  </ul>
</div>
</template>

<script>
import axios from 'axios'
export default {
name: "test",
  data()
  {
    person:[]
  },
  methods:{
  show_users(){
  axios({
    url:"http://127.0.0.1:8000/show_users",
    method:"get"
  }).then(res => alert(res.data.list[0].fields.name))
  }
}

}
</script>

<style scoped>

</style>
