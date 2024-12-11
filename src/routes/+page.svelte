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

    function openSettings() {
        document.getElementById("settingsSidenav").style.width = "250px";
    }

    function closeSettings() {
        document.getElementById("settingsSidenav").style.width = "0";
    }

    function openKey() {
        document.getElementById("keySidenav").style.width = "500px";
    }

    function closeKey() {
        document.getElementById("keySidenav").style.width = "0";
    }


</script>
<!-- style="height:100%;background-color:green" -->
<div class="Container">
    <title>ASL Messenger</title>
    <h1>ASL Messenger</h1>

    <div class="header">
        <nav class="nav-buttons">
            <img src="src/lib/assets/sign-language-asl.png" class="highlight logo"/>
            <ul>
                <li><img src="src/lib/assets/home.png" class="highlight home"></li>
                <li><img src="src/lib/assets/video-chat.png" class="highlight active"></li>
                <li>
                    <div id="keySidenav" class="key sidenav">

                        <a href="javascript:void(0)" class="closebtn" on:click={closeKey}>&times;</a>
                        <h3>ASL Alphabet</h3>
                            <img src="src/lib/assets/asl-key.png" class="asl-key">
                    </div>
                    <img src="src/lib/assets/user-guide.png" class="highlight alphabet" on:click={openKey}>
                </li>
                
            </ul>
        </nav>

        <div class="container">
            <div id="settingsSidenav" class="sidenav">
                <a href="javascript:void(0)" class="closebtn" on:click={closeSettings}>&times;</a>
                <h3>Settings</h3>
                <div class="options">
                    <div class="speed">
                        <label>Signing speed: </label>
                        <select name="speeds" id="speeds"  on:change={(e) => {
                            speed = e.target.value
                            
                        }}>
                            <option value={36}>Slow</option>
                            <option value={24} selected={true}>Medium</option>
                            <option value={12}>Fast</option>
                        </select>
                    </div>
                    <div class="brightness">
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
                </div>
            </div>
            <span class="settings-button" on:click={openSettings}>&#9776;</span>

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

    <!-- <input type="text" on:keyup={(e) => {
        if(e.code == "Enter"){
            onSubmit(e)
            e.target.value = ""
        }
        
    }}/> -->
    
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
        box-shadow: rgba(0, 0, 0, 0.2) 0px 20px 30px;    
    }

    .controls {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .controls img {
        width: 40px;
        margin: 5px 10px;
        filter: invert(100%);
        cursor: pointer;
        transition: transform 0.5s;
    }

    .controls img:hover {
        transform: translateY(-10px)
    }

    .controls .record-button {
        width: 80px;
    }

    .Messages {
        width: 80%;
        height: 85%;
        background: #182842;
        border-radius: 15px;
        padding: 40px;
        box-shadow: rgba(0, 0, 0, 0.2) 0px 20px 30px;    
    }

    .Messages .message {
        padding: 0;
        left: 0;
    }

    .Messages h2 {
        color: white; 
    }

    .Container {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        background-color: #4D6080;
        padding: 0;
    }

    .Container h1 {
        text-align: center;
    }

    .header {
        width: 100%;
        height: 100vh;
        background: #00122e;
        position: relative;
    }

    nav {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        background: #182842;
        width: 100px;
        padding: 10px 10px;
    }

    nav .logo {
        width: 66px;
        display: block;
        margin: auto;
        cursor: pointer;
        filter: invert(100%);
        border-radius: 10px;
    }

    nav ul {
        left: 0;
        margin-top: 160px;
        padding: 0;
    }

    nav ul li {
        list-style: none;
        margin: 10px;
    }

    nav ul li .highlight {
        width: 30px;
        height: 30px;
        object-fit: cover;
        display: block;
        margin: 5px auto;
        padding: 10px;
        cursor: pointer;
        filter: invert(100%);
        border-radius: 10px;
        opacity: 0.7;
        transition: opacity 0.5s, background 0.5s;
    }

    nav ul li img:hover {
        opacity: 1;
        background: #b19e7d; 
    }

    .active {
        opacity: 1;
        background: #b19e7d; 
    }

    .container {
        margin-left: 100px;
        padding: 0 2.5%;
    }

    .sidenav {
        height: 100%;
        width: 0;
        position: fixed;
        z-index: 1;
        top: 0;
        right: 0;
        background-color: white;
        overflow-x: hidden;
        transition: 0.5s;
        padding-top: 60px;

        font-size: 25px;
        color: #818181;
        display: block;
    }

    .sidenav .options {
        padding: 8px 8px 8px 32px;
    }

    .sidenav a {
        padding: 8px 8px 8px 32px;
        text-decoration: none;
        font-size: 25px;
        color: #818181;
        display: block; 
        transition: 0.3s;
    }

    .sidenav h3 {
        color: #00132E;
        text-align: center;

    }

    .sidenav .closebtn {
        position: absolute;
        top: 0;
        right: 25px;
        font-size: 36px;
        margin-left: 50px;
    }

    .settings-button {
        position: absolute;
        font-size: 30px;
        cursor: pointer;
        color:white;
        right: 20px;
    }

    .asl-key{
        width: 500px;
        height: 500px;
    }

    .nav-buttons img:active {
        background-color: red;

    }

    .row-1 {
        margin-top: 15px;
        display: flex;
    }

    .row-2 {
        margin-left: 20%;
        display: flex;
    }

    .col-1 {
        flex-basis: 50%;
        margin-left: auto;

        align-items: center;
        justify-content: center;
        margin-right: 20px;
    }

    .col-2 {
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
        font-size: 24px;
        color: #4D6080;
        animation: blink 1s infinite;
    }

    .sending {
        text-align: center;
        font-size: 24px;
        color: #4D6080;
    }

    @media screen and (max-height: 450px) {
        .sidenav {padding-top: 15px;}
        .sidenav a {font-size: 18px;}
    }
</style>