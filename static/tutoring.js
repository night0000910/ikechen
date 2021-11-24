var mapPeers = {};

var usernameElement = document.getElementById("username");
var username = usernameElement.value;
console.log("ユーザー名 : ", username);

var userIdElement = document.getElementById("user-id");
var userId = userIdElement.value;

var webSocket;

var loc = window.location;
var wsStart = "ws://";

if(loc.protocol == "https:"){
    wsStart = "wss://";
}

var endPoint = wsStart + loc.host + loc.pathname + userId + "/";

console.log("遷移先のURL : ", endPoint);

webSocket = new WebSocket(endPoint);

webSocket.addEventListener("open", (e) => {
    console.log("WebSocketでの接続に成功しました");

    sendSignal("new-peer", {});
});

webSocket.addEventListener("message", webSocketOnMessage);

webSocket.addEventListener("close", (e) => {
    console.log("WebSocketでの接続が切断されました");
});

webSocket.addEventListener("error", (e) => {
    console.log("エラーが発生しました");
});

var localStream = new MediaStream();

const constraints = {
    "video" : true,
    "audio" : true
};

const localVideo = document.querySelector("#local-video");

// ビデオや音声のオンとオフを切り替えるためのボタン
const btnToggleVideo = document.querySelector("#btn-toggle-video");
const btnToggleAudio = document.querySelector("#btn-toggle-audio");

var userMedia = navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        localVideo.srcObject = localStream;
        localVideo.muted = true;

        var videoTracks = stream.getVideoTracks();
        var audioTracks = stream.getAudioTracks();

        videoTracks[0].enabled = true;
        audioTracks[0].enabled = true;

        btnToggleVideo.addEventListener("click", () => {
            videoTracks[0].enabled = !videoTracks[0].enabled;

            if(videoTracks[0].enabled){
                btnToggleVideo.innerHTML = "カメラをオフ";

                return;
            }

            btnToggleVideo.innerHTML = "カメラをオン";
        });

        btnToggleAudio.addEventListener("click", () => {
            audioTracks[0].enabled = !audioTracks[0].enabled;

            if(audioTracks[0].enabled){
                btnToggleAudio.innerHTML = "ミュート";

                return;
            }

            btnToggleAudio.innerHTML = "ミュート解除";
        });
    })
    .catch(error => {
        console.log("メディアデバイスへのアクセスに失敗しました", error);
    });

// btnSendMsg : メッセージの送信ボタン
// messageList : メッセージのリスト
// messageInput : メッセージの入力フォーム
var btnSendMsg = document.querySelector("#btn-send-msg");
var messageList = document.querySelector("#message-list");
var messageInput = document.querySelector("#msg");

btnSendMsg.addEventListener("click", sendMsgOnClick);


// ---------------------------------関数----------------------------------


function webSocketOnMessage(event){
    var parsedData = JSON.parse(event.data);

    var peerUsername = parsedData["peer"];
    var action = parsedData["action"];

    if(username == peerUsername){
        return;
    }

    var receiver_channel_name = parsedData["message"]["receiver_channel_name"];

    console.log(action);

    if(action == "new-peer"){
        createOfferer(peerUsername, receiver_channel_name);

        return;
    }

    if(action == "new-offer"){
        var offer = parsedData["message"]["sdp"];

        createAnswerer(offer, peerUsername, receiver_channel_name);

        return;
    }

    if(action == "new-answer"){
        var answer = parsedData["message"]["sdp"];

        var peer = mapPeers[peerUsername][0];

        peer.setRemoteDescription(answer);

        return;
    }
}

function sendMsgOnClick(){
    var message = messageInput.value;

    var li = document.createElement("li");
    li.style.listStyleType = "none";
    li.appendChild(document.createTextNode(username + ": " + message));
    messageList.appendChild(li);

    var dataChannels = getDataChannels();

    message = username + ": " + message;

    for(index in dataChannels){
        dataChannels[index].send(message);
    }

    messageInput.value = "";
}

function sendSignal(action, message){
    var jsonStr = JSON.stringify({
        "peer" : username,
        "action" : action,
        "message" : message
    });

    webSocket.send(jsonStr);
}

function createOfferer(peerUsername, receiver_channel_name){
    var peer = new RTCPeerConnection(null);
    addLocalTracks(peer);

    var dc = peer.createDataChannel("channel");
    dc.addEventListener("open", () => {
        console.log("WebRTCでの接続に成功しました");
    });

    dc.addEventListener("message", dcOnMessage);

    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, dc];

    peer.addEventListener("iceconnectionstatechange", () => {
        var iceConnectionState = peer.iceConnectionState;

        if(iceConnectionState === "failed" || iceConnectionState === "disconnected" || iceConnectionState === "closed"){
            delete mapPeers[peerUsername];

            if(iceConnectionState != "closed"){
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener("icecandidate", (event) => {
        if(event.candidate){
            console.log("New IceCandidate : ", JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal("new-offer", {
            "sdp" : peer.localDescription,
            "receiver_channel_name" : receiver_channel_name
        });
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log("Local descriptionのセットが完了しました")
        });
}

function createAnswerer(offer, peerUsername, receiver_channel_name){
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    peer.addEventListener("datachannel", e => {
        peer.dc = e.channel;
        peer.dc.addEventListener("open", () => {

        });

        peer.dc.addEventListener("message", dcOnMessage);

        mapPeers[peerUsername] = [peer, peer.dc];
    });

    peer.addEventListener("iceconnectionstatechange", () => {
        var iceConnectionState = peer.iceConnectionState;

        if(iceConnectionState === "failed" || iceConnectionState === "disconneted" || iceConnectionState === "closed"){
            delete mapPeers[peerUsername];

            if(iceConnectionState != "closed"){
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener("icecandidate", (event) => {
        if(event.candidate){
            console.log("New IceCandidate : ", JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal("new-answer", {
            "sdp" : peer.localDescription,
            "receiver_channel_name" : receiver_channel_name
        });
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log("Local descriptionのセットが完了しました");
        });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log("Remote descriptionのセットが完了しました。 ユーザー : %s", peerUsername);

            peer.createAnswer();
        })
        .then(a => {
            console.log("アンサーが作成されました")

            peer.setLocalDescription(a);
        })

}

function addLocalTracks(peer){
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream)
    });

    return;
}

function dcOnMessage(event){
    var message = event.data;

    var li = document.createElement("li");
    li.style.listStyleType = "none";
    li.appendChild(document.createTextNode(message));
    messageList.appendChild(li);
}

function createVideo(peerUsername){
    var videoContainer = document.querySelector("#video-container");

    var remoteVideo = document.createElement("video");

    remoteVideo.id = peerUsername + "-video";
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;
    remoteVideo.width = 800;
    remoteVideo.height = 600;
    remoteVideo.style.gridTemplateColumns = 2;
    remoteVideo.style.gridTemplateRows = 1;

    var videoWrapper = document.createElement("div");

    videoContainer.appendChild(videoWrapper);
    videoWrapper.appendChild(remoteVideo);

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo){
    var remoteStream = new MediaStream()

    remoteVideo.srcObject = remoteStream;

    peer.addEventListener("track", async (event) => {
        remoteStream.addTrack(event.track, remoteStream)
    });
}

function removeVideo(video){
    var videoWrapper = video.parentNode;

    videoWrapper.parentNode.removeChild(videoWrapper);
}

function getDataChannels(){
    var dataChannels = [];

    for(peerUsername in mapPeers){
        var dataChannel = mapPeers[peerUsername][1];

        dataChannels.push(dataChannel);
    }

    return dataChannels;
}