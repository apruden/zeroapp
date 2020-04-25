<template>
  <div class="hello">
    <h2>Essential Links</h2>
 <div class="panel-body">
    <form>
      <vue-form-generator :schema="schema" :model="model">
      </vue-form-generator>
    </form>
  </div>

  <ul v-if="posts && posts.length">
    <li v-for="post of posts">
      <p><strong>{{post.title}}</strong></p>
      <p>{{post.body}}</p>
    </li>
  </ul>

  <ul v-if="errors && errors.length">
    <li v-for="error of errors">
      {{error.message}}
    </li>
  </ul>
  </div>
</template>

<script>
import axios from 'axios'

/* eslint-disable */

export default {
  data: () => ({
    posts: [],
    errors: [],
    model: {
      id: 1,
      name: "John Doe",
      password: "J0hnD03!x4",
      skills: ["Javascript", "VueJS"],
      email: "john.doe@gmail.com",
      status: true
    },
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
    axios.get(`http://jsonplaceholder.typicode.com/posts`)
    .then(response => {
      this.posts = response.data
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
