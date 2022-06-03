`use strict`

// getUserMedia() 接口功能
// 1. constraint：对得到的流的一些属性进行限定
const mediaStreamConstraint = {
    video: {
        width: { min: 1024, ideal: 1280, max: 1920 },
        height: { min: 776, ideal: 960,  max: 1080}
    },
    audio: true
};

// 2. 获取媒体的设备流
navigator.mediaDevices.getUserMedia(mediaStreamConstraint)
    .then(stream => {
        let video = document.querySelector("#rtc");
        video.srcObject = stream;
    })
    .catch(err => {
        console.error(err.name + ': ' + err.message);
    });


// RTCPeerConnection() 接口功能
// RTCPeerConnection() 接口代表由本地计算机到远端的WebRTC连接，该接口提供了创建、保持、监控、关闭连接方法的实现
let PeerConnection = window.RTCPeerConnection || 
                     window.RTCPeerConnection ||
                     window.webkitRTCPeerConnection;

const localMedia = window.querySelector('#localVideo');
const remoteMedia = window.querySelector('#remoteVideo');

// call开始的时间
let startTime = null;

let localStream;
let remoteStream;

let localPeerConnection;
let remotePeerConnection;

const callButton = window.querySelector('#callButton');
const hangupButton = window.querySelector('#hangupButton');

// set MediaStream as the video element src
function getLocalMediaStream(mediaStream) {
    localVideo.srcObject = mediaStream;
    localMedia = mediaStream;
    trace('Received local stream.');
    callButton.disabled = false;
}

// 处理控制台登录信息时的错误
function handleLocalMediaStreamError(error) {
    trace(`navigator.getUserMedia error: ${error.toString()}.`);
}

function getRemoteMediaStream(event) {
    const mediaStream = event.stream;
    remoteMedia.srcObject = mediaStream;
    remoteStream = mediaStream;
    trace('Remote peer connection received remote stream');
}

// 显示video元素的id和大小
function logVideoLoaded(event) {
    const video = event.target;
    trace(`${video.id} videoWidth: ${video.videoWidth}px, ` +
          `videoHeight: ${video.videoHeight}px.`);
}

// 显示video元素的id和大小
// 这个事件在视频开始传输时结束
function logResizedVideo(event) {
    logVideoLoaded(event);

    if (startTime) {
        const elapsedTime = window.performance.now() - startTime;
        startTime = null;
        trace(`Setup time: ${elapsedTime.toFixed(3)}ms.`);
    }
}

localVideo.addEventListener('loadedmetadata', logVideoLoaded);
remoteVideo.addEventListener('loadedmetadata', logVideoLoaded);
remoteVideo.addEventListener('onresize', logResizedVideo);

// 定义RTC peer连接行为

// 和一个新的peer候选者相连接
function handleConnection(event) {
    const PeerConnection = event.target;
    const iceCandidate = event.candidate;

    if (iceCandidate) {
        const newIceCandidate = new RTCIceCandidate(iceCandidate);
        const otherPeer = getOtherPeer(PeerConnection);

        otherPeer.addIceCandidate(newIceCandidate)
            .then(() => {
                handleConnectionSuccess(peerConnection);
            }).catch((error) => {
                handleConnectionFailure(peerConnection);
            });
        
        trace(`${getPeerName(peerConnection)} ICE candidate:\n` +
            `${event.candidate.candidate}.`);
    }
}

// 成功连接的处理场景
function handleConnectionSuccess(peerConnection) {
    trace(`${getPeerName(peerConnection)} addIceCandidate success.`);
};
  
  // 连接失败的处理场景
function handleConnectionFailure(peerConnection, error) {
    trace(`${getPeerName(peerConnection)} failed to add ICE Candidate:\n`+
        `${error.toString()}.`);
}

function handleConnectionChange(event) {
    const peerConnection = event.target;
    console.log('ICE state change event: ', event);
    trace(`${getPeerName(peerConnection)} ICE state: ` +
        `${peerConnection.iceConnectionState}.`);
}

// 设置session描述失败时的日志信息
function setSessionDescriptionError(error) {
    trace(`Failed to create session description: ${error.toString()}.`);
}
  
// 设置session描述成功时的日志信息
function setDescriptionSuccess(peerConnection, functionName) {
    const peerName = getPeerName(peerConnection);
    trace(`${peerName} ${functionName} complete.`);
}

// 当本地描述设置后的成功信息
function setLocalDescriptionSuccess(peerConnection) {
    setDescriptionSuccess(peerConnection, 'setLocalDescription');
}
  
// 当远程描述设置后的成功信息
function setRemoteDescriptionSuccess(peerConnection) {
    setDescriptionSuccess(peerConnection, 'setRemoteDescription');
}

// 创建连接请求并设置peer连接的session描述
function createdOffer(description) {
    // SDP: Session Description Protocal
    trace(`Offer from localPeerConnection:\n${description.sdp}`);

    trace('localPeerConnection setLocalDescription start.');
    localPeerConnection.setLocalDescription(description)
        .then(() => {
            setLocalDescriptionSuccess(localPeerConnection);
        }).catch(setSessionDescriptionError);
    
    trace('remotePeerConnection setRemoteDescription start.');
    remotePeerConnection.setRemoteDescrip(description)
        .then(() => {
            setRemoteDescriptionSuccess(remotePeerConnection);
        }).catch(setSessionDescriptionError);
    
    trace('remotePeerConnection createAnswer start');
    remotePeerConnection.createdAnswer()
        .then(createdAnswer)
        .catch(setSessionDescriptionError);
}

// 对连接请求进行答复并设置peer连接的session描述
function createdAnswer(description) {
    trace(`Answer from remotePeerConnection:\n${description.sdp}.`);

    trace('remotePeerConnection setLocalDescription start.');
    remotePeerConnection.setLocalDescription(description)
        .then(() => {
            setLocalDescriptionSuccess(remotePeerConnection);
        }).catch(setSessionDescriptionError);
    
    trace('localPeerConnection setRemoteDescription start.');
    localPeerConnection.setRemoteDescrip(description)
        .then(() => {
            setRemoteDescriptionSuccess(localPeerConnection);
        }).catch(setSessionDescriptionError);
}

const startButton = document.getElementById('startButton');

// 初始化：设置按钮不可用（当前RTC请求并未创建或得到响应）
callButton.disabled = true;
hangupButton.disabled = true;

// 处理start按钮的动作
function startAction() {
    startButton.disabled = true;
    navigator.mediaDevices.getUserMedia(mediaStreamConstraint)
        .then(getLocalMediaStream).catch(handleLocalMediaStreamError);
    trace('Requesting local stream.');
}

// 处理call按钮的动作
function callAction() {
    callButton.disabled = true;
    hangupButton.disabled = false;

    trace('Starting call.');
    startTime = window.performance.now()

    // 获取本地媒体流的轨迹
    const videoTracks = localStream.getVideoTracks();
    const audioTracks = localStream.getAudioTracks();
    if (videoTracks.length > 0) {
        trace(`Using video device: ${videoTracks[0].label}.`);
    }
    if (audioTracks.length > 0) {
        trace(`Using audio device: ${audioTracks[0].label}.`);
    }

    const servers = null;    // 允许RTC服务器配置
    
    // 创造peer连接并添加行为
    localPeerConnection = new RTCPeerConnection(servers);
    trace('Created local peer connection object localPeerConnection.');

    localPeerConnection.addEventListener('icecandidate', handleConnection);
    localPeerConnection.addEventListener(
        'iceconnectionstatechange', handleConnectionChange
    );

    remotePeerConnection = new RTCPeerConnection(servers);
    trace('Created remote peer connection object remotePeerConnection.');

    remotePeerConnection.addEventListener('icecandidate', handleConnection);
    remotePeerConnection.addEventListener(
        'iceconnectionstatechange', handleConnectionChange
    );
    remotePeerConnection.addEventListener('addstream', getRemoteMediaStream);

    // 允许本地流创建连接请求
    localPeerConnection.addStream(localStream);
    trace('Added local stream to localPeerConnection.');

    trace('localPeerConnection createOffer start.');
    localPeerConnection.createOffer(offerOptions)
        .then(createdOffer).catch(setSessionDescriptionError);
}

function hangupAction() {
    localPeerConnection.close();
    remotePeerConnection.close();
    localPeerConnection = null;
    remotePeerConnection = null;
    hangupButton.disabled = true;
    callButton.disabled = false;
    trace('Ending call.');
}

// 为每个按钮绑定点击动作
startButton.addEventListener('click', startAction);
callButton.addEventListener('click', callAction);
hangupButton.addEventListener('click', hangupAction);

// 辅助函数

function getOtherPeer(peerConnection) {
    return (peerConnection == localPeerConnection) ?
        remotePeerConnection : localPeerConnection;
}

function getPeerName(peerConnection) {
    return (peerConnection == localPeerConnection) ?
        'localPeerConnection' : 'remotePeerConnection';
} 


function trace(text) {
    text = text.trim();
    const now = (window.performance.now() / 1000).toFixed(3);

    console.log(now, text);
}

