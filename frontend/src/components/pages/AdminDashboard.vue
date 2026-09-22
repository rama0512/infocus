<script setup>
//import bg from '../../assets/ss.png'
import AdminLayout from './layout/AdminLayout.vue';
import { ref } from 'vue';
import { useRouter} from 'vue-router';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const token= localStorage.getItem('token')
const router = useRouter();
const showForm= ref(false);
const showparkinglots= ref(false);
const parkingLotsData = ref([])

const prime_location_name=ref('')

const price=ref('')

const address=ref('')

const pin_code=ref('')
const number_of_spots=ref('')
const latitude=ref('')
const longitude=ref('')
const wait_bruhh=ref(false);
async function populate_parking_spots(name1,num1) {
  console.log('populating Parking:', name1)
    const response = await fetch(`${API_BASE_URL}/api/get_parking_lot_data_one?location_name=${encodeURIComponent(name1)}`,{method:'GET',headers:{'Authorization':`Bearer ${token}`,'Content-Type': 'application/json'}});   
    const data = await response.json();
    if (response.ok) {
      const id=data.id;
      const response = await fetch (`${API_BASE_URL}/api/admin/add_parking_spot?lot_id=${id}&create_spots=${num1}`,{
        method:'POST',
        headers:{
          'Authorization':`Bearer ${token}`,
          'Content-Type': 'application/json'
        }});
      if (response.ok) {
        console.log("done");
      }
      /*for (let i = 0;i<num1;i++) {
        const d=data.prime_location_name+i;
        const response = await fetch (`${API_BASE_URL}/api/admin/add_parking_spot?lot_id=${id}`,{
        method:'POST',
        headers:{
          'Authorization':`Bearer ${token}`,
          'Content-Type': 'application/json'
        }});
      const response1 =await response.json()
      if (response.ok) {
        console.log("done");
      }
      }*/
  }
}
async function viewparkinglots() {
  showparkinglots.value=true;
  try {
    const response = await fetch (`${API_BASE_URL}/api/get_parking_lot_data_one?all_rows=true`,{
      method:'GET',
      headers:{
        'Authorization':`Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data =await response.json()
    if (response.ok) {
      parkingLotsData.value = data
      console.log(data)
    } else {
      alert("error"+data.message)
    }
  }
  catch(error){
    alert('Failed to get data'+error.message);
  }
}
function addparking() {
  showForm.value=true;
}
async function submitForm() {

  console.log('Parking name:', prime_location_name.value)
  try {
    const response = await fetch (`${API_BASE_URL}/api/admin/add_parking_lot`,{
      method:'POST',
      headers:{
        'Content-Type': 'application/json',
        'Authorization':'Bearer ' +localStorage.getItem('token')
      },
      body:JSON.stringify ({
        prime_location_name:prime_location_name.value,
        price:price.value,
        address:address.value,
        pin_code:pin_code.value,
        number_of_spots:number_of_spots.value,
        latitude:latitude.value,
        longitude:longitude.value
      })
    })
    const data =await response.json()
    if (response.ok) {
      alert("spot added");
      populate_parking_spots(prime_location_name.value,number_of_spots.value)
    }
    else if (response.status==403){
      alert("admin only")
    } 
    else {
      alert("error"+data.message)
    }
  }
  catch(error){
    alert('Failed to create account'+error.message);
  }
  showForm.value = false  // close the form
}
function cancelForm() {
  showForm.value=false;
}
function closeparkingdetails(){
  showparkinglots.value=false;
}
function showdetails(id){
  router.push(`/admin/ParkingLotdetails?id=${id}`); 
}
</script>

<template>
  <AdminLayout>
    <div class="container1" >
      <button v-on:click="addparking" >+ add parking</button>
      <div v-if="showForm" class="parkingForm">
        <div class="parkingBox">
          <h1>new parking spot </h1>
          <div class="fild"><label>enter location name:</label>
          <input type="text" v-model="prime_location_name" placeholder="location name"></div>
          <div class="fild"><label>enter price</label>
          <input type="text" v-model="price" placeholder="location name"></div>
          <div class="fild"><label>address</label>
          <input type="text" v-model="address" placeholder="enter address"></div>
          <div class="fild"><label>pin_code</label>
          <input type="text" v-model="pin_code" placeholder="enter pin_code"></div>
          <div class="fild"><label>enter number_of_spots</label>
          <input type="text" v-model="number_of_spots" placeholder="number_of_spots"></div>
          <div class="fild"><label>latitude</label>
          <input type="text" v-model="latitude" placeholder="latitude"></div>
          <div class="fild"><label>longitude</label>
          <input type="text" v-model="longitude" placeholder="longitude"></div>
          <div class="form-actions">
            <button v-on:click="submitForm">Submit</button>
            <div v-if="wait_bruhh" class="parkingForm">
              <h1>plz wait loading spots </h1>
            </div>
            <button v-on:click="cancelForm">Cancel</button>
          </div>
        </div>
      </div>
      <br/>
      <button v-on:click="viewparkinglots" :style="{color:'red',background:'blue'}">see parking lots</button>
      <div v-if="showparkinglots" class="parkinggrid">
        <div v-for="lot in parkingLotsData" :key="lot.prime_location_name" >
          <button v-on:click="showdetails(lot.id)">{{ lot.prime_location_name }}</button>
        </div>
        <button v-on:click="closeparkingdetails" class="closeButton" :style="{color:'red',background:'blue'}">close</button>
      </div>
    </div>
  </AdminLayout>
</template>

<style scoped>
.container1 {
  background-color: #f5f1f0; /* dark brown */
  background-image: url('../../assets/ss.png');
  background-size: cover;   /* make it cover entire container */
  /*background-position: center;*/ /* center the image */
  min-height: 100vh;
  padding: 2rem;
  color: #fdf6e3; /* creamy white text */
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Parking form styling */
.parkingForm {
  background-color: #2b1a13;
  border: 2px solid #a97c50; /* light brown border */
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 500px;
  margin: 1rem auto;
}

.parkingForm h1 {
  color: #fdf6e3; /* creamy white heading */
  text-align: center;
}

.fild {
  margin-bottom: 1rem;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.4rem;
  color: #fdf6e3;
}

input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #a97c50;
  border-radius: 6px;
  background-color: #3d2b1f; /* slightly lighter dark brown for input */
  color: #fdf6e3;
}

input::placeholder {
  color: #d8cbb0; /* softer cream for placeholders */
}

/* Light brown buttons with creamy white text */
button {
  background-color: #a97c50;
  color: #fdf6e3;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
  display: block;
  margin: 0.5rem auto; /* center horizontally */
}

button:hover {
  background-color: darkblue;
}

/* Parking lots grid */
.parkinggrid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  padding: 1rem;
}

/* Close button appears below all parking lots */
.closeButton {
  flex-basis: 100%; /* forces it onto its own row */
  text-align: center;
  margin-top: 1rem;
}
</style>

