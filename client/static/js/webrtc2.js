var websocket;
var yourVideo = document.getElementById("yours");
var theirVideo = document.getElementById("their");
var Connection;

// 生成随机数
function randomNum(minN, maxN) {
    switch (arguments.length) {
        case 1:
            return parseInt(Math.random() * minN + 1, 10);
        case 2:
            return parseInt(Math.random() * (maxN - minN + 1) + minN, 10);
        default:
            return 0;
    }
}

let minN = 0, maxN = 100000;
const userID = 'user' + randomNum(minN, maxN);

// 检测是否有媒体流
function hasUserMedia() {
    navigator.getUserMedia = navigator.getUserMedia ||
                             navigator.msGetUserMedia ||
                             navigator.webktiGetUserMedia ||
                             navigator.mozGetUserMedia;
    return !!navigator.getUserMedia;
}

// 检测是否有点对点连接
function hasRTCPeerConnection() {
    window.RTCPeerConnection = window.RTCPeerConnection ||
                               window.msRTCPeerConnection ||
                               window.webkirRTCPeerConnection ||
                               window.mozRTCPeerConnection;
    return !!window.RTCPeerConnection;
}

constraints = {
    video: true,
    audio: true,
};

// 初始化本地流，并将流添加到RTCPeerConnection
function f() {
    navigator.getUserMedia(
    constraints,
    stream => {
        yourVideo.srcObject = stream;
        window.stream = stream;
        Connection.addStream(stream);
    },
    err => {
        console.log(err);
    })
}

function startPeerConnection() {
    var config = {
        'iceServers': [
            { 'url': 'stun:stun.l.google.com:19302' }
        ]
    };
    config = {
        'iceServers': [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:global.stun.twilio.com:34782?transport=udp' }
        ],
    };
    Connection = new RTCPeerConnection(config);
    Connection.onicecandidate = (e) => {
        console.log('onicecandidate');
        if (e.candidate) {
            websocket.send(JSON.stringify({
                "userID": userID,
                "event": "_ice_candidate",
                "data": {
                    "candidate": e.candidate
                }
            }))
        }
    }
    Connection.onaddstream = (e) => {
        console.log('onaddstream');
        theirVideo.srcObject = e.stream;
    }
}

// 将websocket和相关事件绑定
function eventBind() {
    websocket.onopen = (e) => {
        console.log("连接成功");
    }
    websocket.onclose = (e) => {
        console.log("关闭连接");
    }
    websocket.onerror = (e) => {
        console.log("error");
    }
    websocket.onmessage = (e) => {
        if (e.data === "new user") {
            location.reload();
        } else {
            var json = JSON.parse(e.data);
            console.log(json);
            if (json.userID !== userID) {
                if (json.event === "_ice_candidate" && json.data.candidate) {
                    Connection.addIceCandidate(new RTCIceCandidate(json.data.candidate));
                } else if (json.event == "offer") {
                    Connection.setRemoteDescription(json.data.sdp);
                    Connection.createAnswer().then(answer => {
                        Connection.setLocalDescription(answer);
                        console.log(stream);
                        websocket.send(JSON.stringify({
                            "userID": userID,
                            "event": "answer",
                            "data": {
                                "sdp": answer
                            }
                        }));
                    })
                } else if (json.event == "answer") {
                    Connection.setRemoteDescription(json.data.sdp);
                    console.log(window.stream);
                }
            }
        }
    }
}

function createSocket() {
    var user = Math.round(Math.random() * 1000) + "";
    websocket = mediaWS;
    eventBind();
}

createSocket()
startPeerConnection();