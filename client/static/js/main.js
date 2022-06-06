/* 全局变量 */
// 视频HTML组件名称
var localVideoID;
var remoteVideoID;
// 获取的video组件
var localVideo = document.getElementById(localVideoID);
var remoteVideo = document.getElementById(remoteVideoID);
// 本地和远程连接
var localConnection, remoteConnection;
// 流媒体的参数
var mediaConstraints = {
    video: true,
    audio: false
};
// peer连接的配置
const peerConnectionConfig = {
    iceServers: [
        {url: 'stun:stun.l.google.com:19302'}
    ]
};

/* 辅助函数 */
function hasUserMedia() {
    // 封装各个浏览器的UserMedia -> Boolean
    navigator.getUserData = navigator.getUserMedia || navigator.msGetUseMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
    return !!navigator.getUserData;
}

function hasRTCPeerConnection() {
    // 封装各个浏览器的RTCPeerConnection -> Boolean
    window.RTCPeerConnection = window.RTCPeerConnection || window.msRTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection;
    return !!window.RTCPeerConnection;
}



/* 工作函数 */
// 获取本地媒体流
function getLocalMedia() {
    if (hasUserMedia()) {
        navigator.getUserMedia(mediaConstraints, 
            stream => {
                localVideo.srcObject = stream;
                if (hasRTCPeerConnection()) {
                    // 稍后实现startPeerConnection
                    startPeerConnection(stream);
                } else {
                    alert("没有 RTCPeerConnection的API");
                }
            },
            err => {
                console.log(err);
            }
        )
    } else {
        alert("没有userMedia API");
    }
}

// 连接信令服务器
function connectSignalServer(url) {
    let wsConnection = new WebSocket(url);
    wsConnection.onopen() = function() {
        console.log("信令服务器连接成功");
        resolve(wsConnection);
    }
    wsConnection.onclose() = function(evt) {
        console.log("连接异常，请关闭页面重新进入");
    }
    wsConnection.onerror() = function(evt) {
        console.log("socket error", evt);
    }
    wsConnection.onmessage() = function(evt) {
        // 收到信令服务器的信息执行指定操作
    }
}

// 建立传输视频数据所需要的ICE通信路径
function startPeerConnection(stream) {
    // 使用多个公共stun服务器协议
    var config = {
        'iceServers': [
            { 'url': 'stun:stun.services.mozilla.com' },
            { 'url': 'stun:stunserver.org' },
            { 'url': 'stun:stun.l.google.com:19302' }
        ]
    };
    localConnection = new RTCPeerConnection();
    remoteConnection = new RTCPeerConnection();

    // Internet Connection Engine后段地址触发函数
    localConnection.onicecandidate = function(e) {
        if (e.candidate) {
            remoteConnection.addIceCandidate(new RTCIceCandidate(e.candidate));
        }
    }
    remoteConnection.onicecandidate = function(e) {
        if (e.candidate) {
            localConnection.addIceCandidate(new RTCIceCandidate(e.candidate));
        }
    }

    // 建立 SDP(Session Description Protocol) offer 和 SDP answer
    localConnection.createOffer().then(offer => {
        localConnection.setLocalDescription(offer);
        // 远端接收到这个offer
        remoteConnection.setRemoteDescription(offer);
        // 远端产生一个answer
        remoteConnection.createAnswer().then(answer => {
            remoteConnection.setLocalDescription(answer);
            // 本地接收到这个answer
            localConnection.setRemoteDescription(answer);
        })
    });
}