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
    <h1>ASL Messenger</h1>

    <div class="Messages">
        <ul>
        {#each messages as message}
            <li style={message.sender === socket.id ? "background-color: white" : "background-color: yellow"}>
                {message.sender} : {message.message}
            </li>
        {/each}
        </ul>
    </div>

    

    <div>
        <video  style="filter: brightness({brightness}%);"   bind:this={videoSource}  />
        <button on:click={async () => {
            recordVideo()
        }}>RECORD</button>
        <button on:click={async () => {
            stopRecord()
        }}>STOP</button>

        {#if recording}
            <span>RECORDING</span>
        {/if}

        {#if sending}
            <span>SENDING</span>
        {/if}
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
        padding:0;
    }

    li{
        list-style-type: none;
        border : 1px black solid;
        border-radius: 5px;
    }

    video{
        width: 50%;
        height: 50%;
        transform: scaleX(-1);
        

    }

    .Messages{
        width: 100%;
        height: 50%;
        background-color: black;
    }

    .Container{
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;

        padding: 0;
    }
</style>