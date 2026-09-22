<!--<script setup>
import { jwtDecode } from 'jwt-decode';
import UserLayout from '../layout/UserLayout.vue';
import { ref,onMounted } from 'vue';
import { useRouter,useRoute } from 'vue-router';
import {defineComponent} from 'vue';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const token= localStorage.getItem('token')
const router = useRouter();
const route=useRoute();

onMounted(async () => {
  
});



</script>
<template>
<UserLayout>
    
  </UserLayout>
</template>

<style scoped>

</style>-->
<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import UserLayout from '../layout/UserLayout.vue';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const VITE_BACKEND_ENDPOINT = import.meta.env.VITE_BACKEND_ENDPOINT;
const token= localStorage.getItem('token')
const videoRef = ref(null);
const canvasRef = ref(null);
const screenVideoRef = ref(null);
const screenCanvasRef = ref(null);
const screenMessages = ref([]);

let socket = null;
let screenSocket=null;
let stream = null;
let stream1 = null;
let intervalId = null;
let intervalsc = null;

const createTimestampHeader = (capturedAtMs) => {
  const header = new ArrayBuffer(8);
  new DataView(header).setBigUint64(0, BigInt(capturedAtMs), false);
  return header;
};

const sendTimestampedJpeg = (canvas, websocket, quality) => {
  const timestampHeader = createTimestampHeader(Date.now());

  canvas.toBlob((imageBlob) => {
    if (imageBlob && websocket.readyState === WebSocket.OPEN) {
      websocket.send(new Blob([timestampHeader, imageBlob]));
    }
  }, 'image/jpeg', quality);
};

onMounted(async () => {
  setupWebcamSocket();
  setupScreenSocket();
});

const setupWebcamSocket = async () => {
  // 1. Initialize WebSocket
  socket = new WebSocket(`ws://${VITE_BACKEND_ENDPOINT}/ws/webcam?token=${token}`);
  // Define the start logic in a reusable function
  const startStreaming = () => {
    console.log("✅ WebSocket Connected & Streaming Started");    
    intervalId = setInterval(() => {
      // Safety check: Don't capture if video hasn't loaded or socket closed
      if (videoRef.value?.readyState === 4 && socket.readyState === WebSocket.OPEN) {
        const context = canvasRef.value.getContext('2d');
        context.drawImage(videoRef.value, 0, 0, 400, 300);
        sendTimestampedJpeg(canvasRef.value, socket, 0.5);
      }
    }, 5000); // 1 frames per second
  };
  // Handle the 'Race Condition': Check if socket opened instantly
  if (socket.readyState === WebSocket.OPEN) {
    startStreaming();
  } else {
    socket.onopen = startStreaming;
  }
  // Handle errors/closure
  socket.onerror = (err) => console.error("❌ WebSocket Error:", err);
  socket.onclose = () => console.warn(" WebSocket Disconnected");
  // 2. Start Webcam
  try {
    const mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 400, height: 300 } 
    });
    stream = mediaStream;
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream;
    }
  } catch (err) {
    console.error("❌ Webcam access denied:", err);
  }
};
//-------------------------------------------------

const setupScreenSocket = async () => {
  // 1. Start Screen Capture FIRST
  try {
    const mediaStream = await navigator.mediaDevices.getDisplayMedia({  
      video: {width: { ideal: 3840 },height: { ideal: 2160 }}
    });
    
    stream1 = mediaStream;
    if (screenVideoRef.value) {
      screenVideoRef.value.srcObject = mediaStream;
      // MANDATORY: Ensure the video actually starts playing to trigger readyState
      await screenVideoRef.value.play(); 
    }

    mediaStream.getVideoTracks()[0].onended = () => {
      if (intervalsc) clearInterval(intervalsc);
    };
  } catch (err) {
    console.error("❌ Screen capture denied:", err);
    return; // Stop if user cancels screen share
  }

  // 2. Initialize WebSocket
  screenSocket = new WebSocket(`ws://${VITE_BACKEND_ENDPOINT}/ws/screen?token=${token}`);

  const startStreaming = () => {
    console.log("✅ Screen WebSocket Connected");    
    intervalsc = setInterval(() => {
      // DEBUG: Log these states once to see what is failing
      // console.log("Video State:", screenVideoRef.value?.readyState, "Socket State:", screenSocket.readyState);

      if (screenVideoRef.value && screenSocket.readyState === WebSocket.OPEN) {
        const canvas = screenCanvasRef.value;
        const context = canvas.getContext('2d');
        
        // Ensure canvas internal dimensions match your draw call
        canvas.width = 3840; // Match the ideal width you requested
        canvas.height = 2160; // Match the ideal height you requested

        context.drawImage(screenVideoRef.value, 0, 0, 3840, 2160);
        sendTimestampedJpeg(canvas, screenSocket, 1.0);
      }
    }, 9000);
  };

  screenSocket.onopen = startStreaming;
  screenSocket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('Received JSON:', data)
      // Store it / process it
      screenMessages.value.push(data)
    } catch (error) {
      console.error('Invalid JSON received:', event.data)
    }
  };
  screenSocket.onerror = (err) => console.error("❌ Screen WebSocket Error:", err);
  screenSocket.onclose = () => {
     console.warn("Screen WebSocket Disconnected");
     if (intervalsc) clearInterval(intervalsc);
  };
};


//--------------------------------------------------------------------

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
  if (intervalsc) clearInterval(intervalsc); // Added
  if (socket) socket.close();
  if (screenSocket) screenSocket.close(); // Added
  if (stream) stream.getTracks().forEach(track => track.stop());
  if (stream1) stream1.getTracks().forEach(track => track.stop()); // Added
});

</script>

<template>
  <UserLayout>
    <div class="webcam-container">
      <!-- User visible video -->
      <video ref="videoRef" autoplay playsinline width="400" height="300"></video>
      <!-- Hidden canvas for processing -->
      <canvas ref="canvasRef" width="400" height="300" style="display: none;"></canvas>
    </div>
    <div class="p-4">
    <button @click="startCapture" class="btn-primary">Capture Entire Screen</button>
    <!--<canvas ref="canvas" style="display: none;"></canvas>-->
    <video ref="screenVideoRef" autoplay muted playsinline style="display:none;"></video>
    <canvas ref="screenCanvasRef" style="display:none;"></canvas>
  </div>
  <h2>Screen Messages</h2>

    <pre
      v-for="(message, index) in screenMessages"
      :key="index"
    >
      {{ JSON.stringify(message, null, 2) }}
    </pre>
  </UserLayout>
</template>

<style scoped>
.webcam-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
video {
  border-radius: 8px;
  background: #000;
}
</style>
