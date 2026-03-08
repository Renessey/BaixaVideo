<script>

let videoUrl=""
let timer=null

function buscar(){

let url=document.getElementById("url").value
videoUrl=url

fetch("/info",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({url:url})
})

.then(res=>res.json())
.then(data=>{

let html=`

<h2>${data.title}</h2>

<img src="${data.thumbnail}">

<br>

<select id="res">

${data.formats.map(f=>`<option value="${f.height}">${f.res}</option>`).join("")}

</select>

<br><br>

<button onclick="baixarVideo()">Baixar Vídeo</button>
<button onclick="baixarMP3()">Baixar MP3</button>

`

document.getElementById("resultado").innerHTML=html

})

}


function acompanhar(){

document.getElementById("progressBox").style.display="block"

document.getElementById("status").innerText="Aguarde..."

timer=setInterval(()=>{

fetch("/progress")
.then(r=>r.json())
.then(data=>{

document.getElementById("progressBar").style.width=data.percent+"%"
document.getElementById("percent").innerText=data.percent+"%"

if(data.percent>=100){

clearInterval(timer)

document.getElementById("status").innerText="Seu vídeo foi baixado com sucesso!"

}

})

},1000)

}


function baixarVideo(){

let res=document.getElementById("res").value

acompanhar()

window.location=`/download?url=${videoUrl}&res=${res}&tipo=video`

}


function baixarMP3(){

acompanhar()

window.location=`/download?url=${videoUrl}&tipo=mp3`

}

</script>