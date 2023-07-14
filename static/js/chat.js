var results_dict = {}

function adjustFixedInput() {
    if (window.innerWidth >= 992) {
      $('.chat-button').css('margin-top', 15);
      $('.container').css('margin-left', $('#slide-out').width());
      $('.container').css('width', "100%");
      $('.chat_container').css('margin-left', $('#slide-out').width());
      $('.nav-wrapper').css('margin-left', $('#slide-out').width());
      $('.brand-logo').css('margin-left', '25px');
    } else {
      $('.chat-button').css('margin-top', 14);
      $('.chat_container').css('margin-left', 0);
      $('.container').css('margin-left', 0);
      $('.container').css('width', "90%");
      $('.nav-wrapper').css('margin-left', 0);
      $('.brand-logo').css('margin-left', '0px');
    }
  }          


  $(document).ready(function(){

    const url = new URL(window.location.href);
    question_param = url.searchParams.get("question")
    
    $('.sidenav').sidenav({ edge: 'left' });
    adjustFixedInput();
    $(window).resize(adjustFixedInput);

    const chatInput = document.getElementById("chat-input");
    const sendMessage = document.getElementById("send-message");
    chatMessages = document.querySelector(".chat-window");

    var chat_div = document.getElementById("messages-div");
    chat_div.innerHTML = `<div id="initial_message" class="message response-message"><p>Hi! I'm <b>Sucession Chat</b> - your personal guide to all things Succession. What would you like to know?</p></div>`


    sendMessage.addEventListener("click", function (event) {
      event.preventDefault();
      if (chatInput.value.trim() !== "") {
        addMessage(chatInput.value, "user-message");
        sendChatRequest(chatInput.value);
        chatInput.value = "";
        setTimeout(add_loading_chat, 1000);
      }
    });

    chatInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        addMessage(chatInput.value, "user-message");
        sendChatRequest(chatInput.value);
        chatInput.value = "";
        setTimeout(add_loading_chat, 1000);
      }
    })

    if (question_param != null) {
      addMessage(question_param, "user-message");
      sendChatRequest(question_param);
      setTimeout(add_loading_chat, 1000);
    }
})

function fetchWithTimeout(url, data, timeout, options = {}) {
    
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  options.signal = controller.signal;

  if (data) {
    options.method = 'POST';
    options.headers = {
      ...options.headers,
      'Content-Type': 'application/json; charset=utf-8',
    };
    options.body = JSON.stringify(data);
  }

  return fetch(url, options)
    .finally(() => clearTimeout(timeoutId));
}

async function fetchData(url, data, timeout=TIMEOUT,retries = 10) {
  try {
    const response = await fetchWithTimeout(url, data, timeout);
    const responseData = await response.json();
    return responseData;
  } catch (error) {
    if (retries > 0) {
      console.log(`Retrying, ${retries} retries left...`);
      return fetchData(url, data, timeout, retries - 1);
    } else {
      throw error;
    }
  }
}

function addMessage(text, className) {
  return new Promise((resolve, reject) => {
    
    console.log(className)
    const message = document.createElement("div");
    message.classList.add("message", className);
    if (className == 'loading'){
      const messageText = document.createElement("p");
      const id = generateRandomID();
      messageText.id = id;
      message.appendChild(messageText);
      chatMessages.appendChild(message);
      typeLetter(id,text).then(resolve);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } else if (className == 'response-message'){
      const messageText = document.createElement("p");
      const id = generateRandomID();
      messageText.id = id;
      messageText.style = "white-space: pre-line"
      message.appendChild(messageText);
      chatMessages.appendChild(message);
      typeLetter(id,text).then(resolve);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } else {
      const messageText = document.createElement("p");
      const id = generateRandomID();
      messageText.id = id;
      messageText.style = "white-space: pre-line"
      messageText.innerText = text;
      message.appendChild(messageText);
      chatMessages.appendChild(message);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      resolve();
    }
  })
}

function sendChatRequest(userMessage) {

  const textbox = document.getElementById("chat-input");

  const chatLoader = document.getElementById("chat_loader_div");

  const parentDiv = document.getElementById('messages-div');
  const childP = parentDiv.querySelectorAll('div > p');
  const childDivs = parentDiv.querySelectorAll('div');

  const textArray = Array.from(childP).map(p => p.textContent);
  const classArray = Array.from(childDivs).map(div => div.className);

  url = '/getChatResponse'
  data = {'messages':textArray,'roles':classArray}

  fetchData(url, data, 90000)
  .then(async responseData => {

    response = responseData["response"]
    console.log(response)
    removeDivByClass("loading")
    await addMessage(response, "response-message");
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }).catch(error => console.error('Failed to fetch data:', error));

}

function typeLetter(elementId, textToType, currentTextIndex = 0) {
    return new Promise((resolve, reject) => {
        const textElement = document.getElementById(elementId);

        function typeNextLetter() {
            if (currentTextIndex < textToType.length) {
                textElement.textContent += textToType[currentTextIndex];
                currentTextIndex++;
                chatMessages.scrollTop = chatMessages.scrollHeight;
                setTimeout(typeNextLetter, 20); // Adjust the number (20) to control typing speed (in milliseconds)
            } else {
                resolve();
            }
        }

        typeNextLetter();
    });
}


function generateRandomID() {
  // Get the current timestamp as a string
  const timestamp = Date.now().toString();

  // Generate a random number between 1 and 1000000
  const randomNumber = Math.floor(Math.random() * 1000000);

  // Combine the timestamp and random number to create the ID
  const randomID = `${timestamp}-${randomNumber}`;

  return randomID;
}

function chipClicked(chip) {
  const chipText = chip.textContent || chip.innerText;
  
  addMessage(chip.innerText, "user-message");
  sendChatRequest(chip.innerText);
  
  let elem = document.querySelector('#slide-out');
  let instance = M.Sidenav.getInstance(elem);
  if (window.innerWidth< 992) {
    instance.close();
  }
  setTimeout(add_loading_chat, 1000);
  
}

function add_loading_chat(){
  addMessage("One moment, I'm thinking about it ... ", "loading");
}

function removeDivByClass(className) {
  // Select all elements with the given class name
  const elements = document.getElementsByClassName(className);

  // Loop through the elements in reverse order and remove them
  for (let i = elements.length - 1; i >= 0; i--) {
    const element = elements[i];
    element.parentNode.removeChild(element);
  }
}