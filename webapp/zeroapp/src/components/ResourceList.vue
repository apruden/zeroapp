<template>
  <div class="hello">
    <v-client-table :data="tableData" :columns="columns" :options="options"></v-client-table>
  </div>
</template>

<script>
import axios from 'axios'

/* eslint-disable */

export default {
  data: () => ({
    columns: [],
    tableData: [],
    options: {},
  }),

  created () {
    axios.all([
	    axios.get(`/api/${router.entity}`),
	    axios.get(`/api/${router.entity}/_table`)
	    ])
    .then((entities, table) => {
      this.tableData = entities.data
      this.columns = table.data
    })
    .catch(e => {
      this.errors.push(e)
    })
  }
}

/* eslint-enable */
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
