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

    $: recording = false

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

        return () => {
            socket.disconnect();
        };
    })

    function onSubmit(e : any){
        socket.emit("message", e.target.value, socket.id)
        let m : Message = {
            sender : socket.id,
            message : e.target.value,
        }

        console.log(m.message)
        messages = [...messages, m]
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
        recording = true;
        const options = { mimeType: "video/mp4; codecs=vp9" };
        mediaRecorder = new MediaRecorder(stream, options);

        mediaRecorder.ondataavailable = handleDataAvailable;
        mediaRecorder.start();
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
            download();
            recordedChunks.pop()
        }
    }

    function download() {
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
            socket.emit("message", fileData, socket.id);
            
        }).catch((err) => {
            console.log(err)
        });


    }

</script>

<div>
    <h1>ASL Messenger</h1>
    <h1>hi</h1>
    
    <ul>
       {#each messages as message}
        <li style={message.sender === socket.id ? "background-color: blue" : "background-color: green"}>
            {message.sender} : {message.message}
        </li>
       {/each}
    </ul>

    <input type="text" on:keyup={(e) => {
        if(e.code == "Enter"){
            onSubmit(e)
            e.target.value = ""
        }
        
    }}/>

    <video bind:this={videoSource}  />
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
        <span>Sending</span>
    {/if}
    
</div>

<style>
    li{
        list-style-type: none;
        border : 1px black solid;
        border-radius: 5px;
    }

    video{
        transform: scaleX(-1);
    }
</style>