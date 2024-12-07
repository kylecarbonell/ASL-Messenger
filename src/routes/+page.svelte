<script lang="ts">
	import { onMount } from "svelte";
    import io, { Socket } from 'socket.io-client';
    import "../app.css";
    // import ffmpeg from 'fluent-ffmpeg';

    interface Message {
        sender: String;
        message : String
    }


    let port = "ws://0.0.0.0:8080/"
    let socket : Socket; 

    let videoSource: HTMLVideoElement | null = null;
    let loading = false;

    let messages : Message[] = []

    const recordedChunks : any[] = [];
    let mediaRecorder : MediaRecorder;
    let sending = false

    let speed = 24
    let brightness = 75

    $: recording = false
    $: console.log(speed)

    onMount(() => {

        getCam()
        socket = io(port)
        
        socket.on('connect', (newMessage:string) => {
            console.log(newMessage)
        });

        // Listen for incoming messages
        socket.on('message', (newMessage:string, sender: string) => {
            
            let m : Message = {
				sender: sender,
				message: newMessage
			}
            messages = [...messages, m]
            console.log("IN MESSAGE")
            console.log(messages)
            sending = false
        });


        socket.on('textMessage', (newMessage:string, sender: string) => {
            let m : Message = {
				sender: sender,
				message: newMessage
			}
            messages = [...messages, m]
            console.log("IN MESSAGE")
            console.log(messages)
            sending = false
        });

        return () => {
            socket.disconnect();
        };
    })

    function onSubmit(e : any){
        socket.emit("textMessage", e.target.value, socket.id)
        let m : Message = {
            sender : socket.id,
            message : e.target.value,
        }

        // console.log(m.message)
        // messages = [...messages, m]
    }
    
    async function getCam(){
        try {
        loading = true;
        const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
        });
        videoSource.srcObject = stream
        videoSource?.play();
        loading = false;
        } catch (error) {
        console.log(error);
        }
    };
   
    
    function recordVideo(){
        const canvas = document.querySelector("video");

        // Optional frames per second argument.
        const stream = canvas?.captureStream(25);
       

        console.log(stream);
        
        const options = { mimeType: "video/mp4; codecs=vp9" };
        mediaRecorder = new MediaRecorder(stream, options);

        mediaRecorder.ondataavailable = handleDataAvailable;
        mediaRecorder.start();

        
        mediaRecorder.onstart = handleStart;
        mediaRecorder.onstop = handleEnd;
    }

    function handleStart(){
        recording = true
    }

    function handleEnd(){
        recording = false
    }
    
    async function stopRecord(){
        mediaRecorder.stop()
        recording = false
    }

    function handleDataAvailable(event : any) {
        console.log("data-available");
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
            console.log(recordedChunks);
            sendData();
            recordedChunks.pop()
        }
    }

    function sendData() {
        const blob = new Blob(recordedChunks, {
            type: "video/mp4",
        });

        const url = URL.createObjectURL(blob);

        // extractKeyframes(url, "../../backend/ASL Videos")
        console.log(blob.size)

        blob.arrayBuffer().then((buffer) => {
            const fileData = {
                fileName: "test.mp4",
                buffer: buffer,
            };
            
            console.log("File sent to server");
            
            sending = true
            socket.emit("message", fileData, socket.id, speed);
            
        }).catch((err) => {
            console.log(err)
        });
    }
</script>
<!-- style="height:100%;background-color:green" -->
<div class="Container">
    <title>ASL Messenger</title>
    <h1>ASL Messenger</h1>

    <div class="header">
        <nav>
            <img src="src/lib/assets/sign-language-asl.png" class="logo"/>
            <ul>
                <li><img src="src/lib/assets/home.png" ></li>
                <li><img src="src/lib/assets/video-chat.png" class="active"></li>
                <!-- <li><img src="src/lib/assets/chat.png"></li> -->
                <li><img src="src/lib/assets/user-guide.png"></li>
                <!-- <li><img src="src/lib/assets/settings.png"></li> -->
            </ul>
        </nav>
        <div class="container">
            <div class="top-icons">
                <img src="src/lib/assets/settings.png">
            </div>
            <div class="rows">
                
            </div>
            <div class="row-1">
                <div class="col-1">
                    <div class="video-player">
                        <video style="filter: brightness({brightness}%);" bind:this={videoSource} class="video" />
                        <div class="controls">
                            <img src="src/lib/assets/rec.png" class="record-button" on:click={async () => {
                                recordVideo()
                            }}>
                            <img src="src/lib/assets/right-arrow.png" on:click={async () => {
                                stopRecord()
                            }}>
                            <!-- <img src="src/lib/assets/stop.png" on:click={async () => {
                                stopRecord()
                            }}> -->
                        </div>
                    </div>
                </div>
                <div class="col-2">
                    <div class="Messages">
                        <h2>Chat</h2>
                        <ul class="message">
                        {#each messages as message}
                            <li style={message.sender === socket.id ? "background-color: white" : "background-color: yellow"}>
                                {message.sender} : {message.message}
                            </li>
                        {/each}
                        </ul>
                    </div>
                </div>
            </div>
            <div class="row-2">
                {#if recording}
                    <div class="blinking-text">RECORDING</div>  
                {/if}

                {#if sending}
                    <div class="sending">SENDING</div>
                {/if}
            </div>
        </div>
    </div>

    

    <div>
        <label>Signing speed: </label>
        <select name="speeds" id="speeds"  on:change={(e) => {
            speed = e.target.value
            
        }}>
            <option value={36}>Slow</option>
            <option value={24} selected={true}>Medium</option>
            <option value={12}>Fast</option>
        </select>
        <label>Brightness: </label>
        <select name="brightness" id="brightness" on:change={(e) => {
            brightness = e.target.value
            
        }}>
            <option value={25}>Dark</option>
            <option value={50}>Dim</option>
            <option value={75} selected={true}>Bright</option>
            <option value={100}>Brightest</option>
        </select>

    </div>

    <input type="text" on:keyup={(e) => {
        if(e.code == "Enter"){
            onSubmit(e)
            e.target.value = ""
        }
        
    }}/>
    
</div>

<style>
    html, body {
        height: 100%;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Poppins', sans-serif;
    }

    li{
        list-style-type: none;
        border-radius: 5px;
    }

    .video{
        width: 100%;
        border-radius: 15px;
        transform: scaleX(-1);
        /* box-shadow: 1px 1px 25px grey; */
    }

    .controls{
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .controls img{
        width: 40px;
        margin: 5px 10px;
        filter: invert(100%);
        cursor: pointer;
        transition: transform 0.5s;
    }

    .controls .record-button{
        width: 80px;
    }

    .controls img:hover{
        transform: translateY(-10px)
    }

    .Messages{
        width: 80%;
        height: 85%;
        background: #182842;
        border-radius: 15px;
        padding: 40px;
    }

    .Messages .message{
        padding: 0;
        left: 0;
    }

    .Messages h2{
        color: white; 
    }

    .Container{
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;

        padding: 0;
    }

    .header{
        width: 100%;
        height: 100vh;
        background: #00122e;
        position: relative;
    }

    nav{
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        background: #182842;
        width: 100px;
        padding: 10px 10px;
    }

    nav .logo{
        width: 66px;
        display: block;
        margin: auto;
        cursor: pointer;
        filter: invert(100%);
        border-radius: 10px;
    }

    nav ul{
        left: 0;
        margin-top: 160px;
        padding: 0;
    }

    nav ul li{
        list-style: none;
        margin: 10px;
    }

    nav ul li img{
        width: 30px;
        height: 30px;
        object-fit: cover;
        display: block;
        margin: 5px auto;
        padding: 10px;
        cursor: pointer;
        filter: invert(100%);
        border-radius: 10px;
        opacity: 0.5;
        transition: opacity 0.5s, background 0.5s;
    }

    nav ul li img:hover{
        opacity: 1;
        background: #b19e7d; 

    }

    .active{
        opacity: 1;
        background: #b19e7d; 
    }

    .container{
        margin-left: 100px;
        padding: 0 2.5%;
    }

    .top-icons{
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding: 25px 0;
    }

    .top-icons img{
        width: 30px;
        cursor: pointer;
        filter: invert(100%);
    }

    .row-1{
        margin-top: 15px;
        display: flex;
    }

    .row-2{
        margin-left: 20%;
        display: flex;
    }

    .col-1{
        flex-basis: 50%;
        margin-left: auto;

        /* padding: 20px; */
        /* display: flex; */
        align-items: center;
        justify-content: center;
        margin-right: 20px;
    }

    .col-2{
        flex-basis: 48%; 
    }

    @keyframes blink {
        0% {
            opacity: 1;
        }

        50% {
            opacity: 0;
        }

        100% {
            opacity: 1;
        }
    }

    .blinking-text {
        text-align: center;
        /* margin-top: 5%; */
        font-size: 24px;
        color: #4D6080;
        animation: blink 1s infinite;
    }

    .sending{
        text-align: center;
        /* margin-top: 5%; */
        font-size: 24px;
        color: #4D6080;
    }

    .recordButton{
        color:red;
    }
</style>