document.addEventListener("DOMContentLoaded", function() {
    const submitBtn = document.getElementById("asklono-submit-btn");
    const userInput = document.getElementById("asklono-user-input");
    const messageContainer = document.getElementById("asklono-message-container");

    let history = [];

    submitBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    userInput.addEventListener("input", adjustInputHeight);

    async function sendMessage() {
        const messageText = userInput.value.trim();
    
        if (messageText !== "") {
            addMessage("user", messageText, true);
            userInput.value = "";
            adjustInputHeight();
            userInput.disabled = true;
            submitBtn.disabled = true;
    
            // Loading animation
            let loadingInterval;
            let loadingDots = 0;
            submitBtn.textContent = 'Loading';
            loadingInterval = setInterval(() => {
                loadingDots = (loadingDots + 1) % 4;
                submitBtn.textContent = 'Loading' + '.'.repeat(loadingDots);
            }, 500);
    
            // Prepare last 5 message pairs (10 messages)
            const lastMessages = history.slice(-10);
    
            try {
                const response = await fetch('https://lono.pythonanywhere.com/chat', { // Update the endpoint as needed
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        query: messageText, 
                        history: lastMessages 
                    }),
                });
    
                if (!response.ok) {
                    throw new Error(`Error: ${response.statusText}`);
                }
    
                const data = await response.json();
                const assistantMessage = data.result; // Adjusted based on backend response
    
                addMessage("assistant", assistantMessage, false);
            } catch (error) {
                console.error("Error sending message:", error);
                addMessage("assistant", "Sorry, something went wrong. Please try again.", false);
            } finally {
                // Reset input and button
                clearInterval(loadingInterval);
                submitBtn.textContent = 'Submit';
                userInput.disabled = false;
                submitBtn.disabled = false;
                userInput.focus();
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        }
    }

    function addMessage(role, content, userTriggered) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("asklono-message");
        messageElement.classList.add(role === "user" ? "asklono-user-message" : "asklono-assistant-message");
        messageElement.textContent = content;

        if(userTriggered){
            const deleteIcon = document.createElement("span");
            deleteIcon.classList.add("asklono-delete-icon");
            deleteIcon.textContent = "❌";
            deleteIcon.onclick = function() {
                deleteMessagePair(messageElement);
            }
            messageElement.appendChild(deleteIcon);
        }

        messageContainer.appendChild(messageElement);
        history.push({ role: role, content: content });

        // Auto-scroll to the bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function deleteMessagePair(messageElement) {
        if (messageElement.classList.contains("asklono-user-message")) {
            const nextElement = messageElement.nextElementSibling;

            // Remove assistant message if it exists
            if (nextElement && nextElement.classList.contains("asklono-assistant-message")) {
                messageContainer.removeChild(nextElement);
                // Remove from history
                history.pop(); // assistant message
            }

            // Remove user message
            messageContainer.removeChild(messageElement);
            // Remove from history
            history.pop(); // user message
        }

        // Reconstruct history from remaining messages
        history = [];
        const remainingMessages = messageContainer.getElementsByClassName("asklono-message");
        Array.from(remainingMessages).forEach(element => {
            const role = element.classList.contains("asklono-user-message") ? "user" : "assistant";
            const content = element.textContent.replace("❌", "").trim();
            history.push({ role: role, content: content });
        });
    }

    function adjustInputHeight() {
        userInput.style.height = "auto";
        userInput.style.height = userInput.scrollHeight + "px";

        // If the input exceeds max height, enable scrollbar
        if (userInput.scrollHeight > 100) { // 100px matches the CSS max-height
            userInput.style.overflowY = "auto";
            userInput.style.height = "100px";
        } else {
            userInput.style.overflowY = "hidden";
        }
    }
});
