<template>
  <div class="hello">

  </div>
</template>

<script>
import axios from 'axios'

/* eslint-disable */

export default {
  data: () => ({
    errors: [],
    model: {},
    schema: {
      groups: [
        {
          legend: "User Details",
	  fields: [
            {
                type: "input",
                inputType: "text",
                label: "ID (disabled text field)",
                model: "id",
                readonly: true,
                disabled: true
              },
              {
                type: "input",
                inputType: "text",
                label: "Name",
                model: "name",
                id: "user_name",
                placeholder: "Your name",
                featured: true,
                required: true
              },
              {
                type: "input",
                inputType: "email",
                label: "E-mail",
                model: "email",
                placeholder: "User's e-mail address"
              },
              {
                type: "input",
                inputType: "password",
                label: "Password",
                model: "password",
                min: 6,
                required: true,
                hint: "Minimum 6 characters"
              }
            ]
          },
          {
            legend: "Skills & Status",
            fields: [
              {
                type: "select",
                label: "skills",
                model: "type",
                values: ["Javascript", "VueJS", "CSS3", "HTML5"]
              },
              {
                type: "checkbox",
                label: "Status",
                model: "status",
                default: true
              }
            ]
          }
          ]
        }
  }),

  created () {
    axios.get(`/api/${router.entity}/_schema`)
    .then(response => {
      this.schema = response.data
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
