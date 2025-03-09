console.log("Sanity check from room.js.");

const roomName = JSON.parse(document.getElementById('roomName').textContent);

let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");
let change = document.querySelector("#change");

// Brings in template tag information
let url = document.getElementById("url").textContent;
let change_url = document.getElementById("change_url").textContent;
// let change = document.getElementById("change");
let phone_num = document.getElementById("phone_num").textContent;
let send_http_msg = document.querySelector("#chatMessageInput").value;



// adds a new option to 'onlineUsersSelector'
function onlineUsersSelectorAdd(value) {
    if (document.querySelector("option[value='" + value + "']")) return;
    let newOption = document.createElement("option");
    newOption.value = value;
    newOption.innerHTML = value;
    onlineUsersSelector.appendChild(newOption);
}

// removes an option from 'onlineUsersSelector'
function onlineUsersSelectorRemove(value) {
    let oldOption = document.querySelector("option[value='" + value + "']");
    if (oldOption !== null) oldOption.remove();
}

// focus 'chatMessageInput' when user opens the page
chatMessageInput.focus();

// submit if the user presses the enter key
chatMessageInput.onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter key
        chatMessageSend.click();
    }
};


// clear the 'chatMessageInput' and forward the message
chatMessageSend.onclick = function() {
    if (chatMessageInput.value.length === 0) return;
    chatSocket.send(JSON.stringify({
        "message": chatMessageInput.value,
    }));
    send_http(chatMessageInput.value);
    chatMessageInput.value = "";
};

// Old version:
// chatMessageSend.onclick = function() {
//     if (chatMessageInput.value.length === 0) return;
//     // TODO: forward the message to the WebSocket
//     chatMessageInput.value = "";
// };
//##############



// NOTE //
// Additions to allow diverting messages to Whatsapp texting.

// Saves us from CSRF hell.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// Triggers message-sending URL
async function send_http(message) {
    // const user_input = chatMessageInput.value;
    // const url = "{{ send_message_url }}";
    // console.log(send_http_msg);

    
    let data = {
        number: phone_num,
        body: message
    }

    let request = new Request(url, {
        method: 'POST',
        credentials: "same-origin",
        body: JSON.stringify(data),
        headers: new Headers({
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
    });

    fetch(request);
}


let chatSocket = null;

// Added an extra 's' to make 'wss'.
function connect() {
    chatSocket = new WebSocket("wss://" + window.location.host + "/ws/chat/" + roomName + "/");
    

    chatSocket.onopen = function(e) {
        console.log("Successfully connected to the WebSocket.");
        // NOTE //
        console.log("wss://" + window.location.host + "/ws/chat/" + roomName + "/");
    }

    chatSocket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function() {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log(data);
        if (data.sender){
            chatLog.value += data.message + "\n";
        } else {
            switch (data.type) {
                case "chat_message":
                    chatLog.value += data.message + "\n";
                    console.log(phone_num);
                    console.log(url);
                    console.log(data.message);
                    break;
                default:
                    console.error("Unknown message type!");
                    break;
            }
        }


        send_http_msg = "";
        // scroll 'chatLog' to the bottom
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    chatSocket.onerror = function(err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    }
}
connect();


function change_session() {

    let data = {
        number: phone_num,
    }
    console.log(change_url);

    let request = new Request(change_url, {
        method: 'POST',
        credentials: "same-origin",
        body: JSON.stringify(data),
        headers: new Headers({
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })
    });
    fetch(request);
}

change.addEventListener("click", change_session);
