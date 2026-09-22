import { createRouter, createWebHistory } from 'vue-router';
import {jwtDecode} from 'jwt-decode';
import Welcome from './components/pages/Welcome.vue'
import Signup from './components/pages/Signup.vue'

import userDashboard from './components/pages/user_pages/userDashboard.vue'


//note: /:id -> .params . ?id -> query . 
//note2 use name if you do route.push({name:'userDashboard,params:{'id':2}})  else router.push(`/user/Dashboard?id=${id}`); does not require name .h
const routes = [
  { path: '/', name: 'Welcome', component: Welcome ,beforeEnter: (to, from, next) => {
      const token = localStorage.getItem('token');
      if (!token) return next();

      try {
        const payload = jwtDecode(token);
        if (payload.role === 'admin') {
          return next('/admin/Dashboard');
        } else {
          return next(`/user/Dashboard/${payload.id}`);
        }
      } catch {
        return next(); 
      }
    }},
  { path: '/Signup', name: 'Signup', component: Signup },
  /*{ path: '/admin/Dashboard', name: 'AdminDashboard', component: AdminDashboard,beforeEnter: (to, from, next) => {
      const token = localStorage.getItem('token');
      if (!token) return next('/');

      try {
        const payload = jwtDecode(token);
        const isExpired = payload.exp *1000 < Date.now();
        if (payload.role!= 'admin' || isExpired) {
          localStorage.removeItem('token');
          return next('/');
        } else {
          return next();
        }
      } catch {
        return next('/');
      }
    } }, //, meta: { requiresAdmin: true }*/
  /*{ path: '/admin/users', name: 'Admin_side_user_data', component: Admin_side_user_data }, 
  { path: '/Admin/summary', name: 'Admin_summary', component: Admin_summary }, 
  { path: '/admin/ParkingLotdetails', name: 'ParkingLotdetails', component: ParkingLotdetails },*/
  { path: '/user/Dashboard/:id', name: 'userDashboard', component: userDashboard},
  /*beforeEnter: (to, from, next) => {
      const token = localStorage.getItem('token');
      if (!token) return next('/');
      try {
        const payload = jwtDecode(token);
        const isExpired = payload.exp *1000 < Date.now();
        if (payload.role!= 'user' || isExpired) {
          localStorage.removeItem('token');
          return next('/');
        } else {
          return next();
        }
      } catch {
        return next('/'); // invalid token → stay on login
      }
    } },*/
  //, meta: { requiresuser: true }
  /*{ path: '/user/summary', name: 'user_summary', component: user_summary },*/
]

const router = createRouter({
  history: createWebHistory(),routes
})


export default router

