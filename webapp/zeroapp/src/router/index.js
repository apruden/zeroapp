import Vue from 'vue'
import Router from 'vue-router'
import Hello from '@/components/Hello'
import Resource from '@/components/Resource'
import ResourceList from '@/components/ResourceList'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Hello',
      component: Hello
    },
    {
      path: '/:resource',
      name: 'ResouceList',
      component: ResourceList
    },
    {
      path: '/:resource/:id',
      name: 'Resouce',
      component: Resource
    }
  ]
})
