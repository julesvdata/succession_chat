$(document).ready(function(){

    document.querySelectorAll('.chip').forEach(function(div) {
        div.addEventListener('click', function() {
            const text = this.textContent;
            chip_clicked(text);
        });
    });

    const chatInput = document.getElementById("index-chat-input");

    chatInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          submit_question()
        }
    })

})

function goToPageWithArguments(url, arguments) {
  // Create an array to hold the URL parameters
  let queryParams = [];

  // Iterate through the arguments object
  for (let key in arguments) {
    if (arguments.hasOwnProperty(key)) {
      // Encode the key and value to ensure they are URL-safe
      let encodedKey = encodeURIComponent(key);
      let encodedValue = encodeURIComponent(arguments[key]);

      // Add the key-value pair to the queryParams array
      queryParams.push(encodedKey + '=' + encodedValue);
    }
  }

  // Join the queryParams array with '&' to create the query string
  let queryString = queryParams.join('&');

  // Append the query string to the URL and navigate to the new page
  window.location.href = url + '?' + queryString;
}

function submit_question(){

  const inputElement = document.querySelector('.input-text');

  const inputValue = inputElement.value;

  goToPageWithArguments('/chat', {
    question: inputValue,
  });
  
}

function chip_clicked(question){

  goToPageWithArguments('/chat', {
    question: question,
  });
  
}