const chatContainer = document.getElementById("chatContainer");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const clearChatButton = document.getElementById("clearChat");


// ============================
// Add user message
// ============================

function addUserMessage(text) {

    const message = document.createElement("div");

    message.className = "message user";

    message.innerHTML = `
        <div class="avatar">👤</div>

        <div class="message-content">
            <div class="message-bubble">
                ${escapeHtml(text)}
            </div>
        </div>
    `;

    chatContainer.appendChild(message);

    scrollToBottom();
}


// ============================
// Add assistant message
// ============================

function addAssistantMessage(data) {

    const message = document.createElement("div");

    message.className = "message assistant";

    const confidence =
        typeof data.confidence_score === "number"
            ? `${(data.confidence_score * 100).toFixed(2)}%`
            : "N/A";


    let sourcesHtml = "";

    if (
        Array.isArray(data.retrieved_chunks) &&
        data.retrieved_chunks.length > 0
    ) {

        sourcesHtml = `
            <div class="sources">

                <div class="sources-title">
                    Retrieved Sources
                </div>

                <div class="source-list">

                    ${data.retrieved_chunks.map(chunk => {

                        const score =
                            typeof chunk.score === "number"
                                ? `${(chunk.score * 100).toFixed(2)}%`
                                : "N/A";

                        return `
                            <div class="source-item">

                                <div class="source-meta">
                                    <strong>
                                        Page ${escapeHtml(String(chunk.page))}
                                    </strong>

                                    <span>
                                        Relevance ${score}
                                    </span>
                                </div>

                                <div class="source-preview">
                                    ${escapeHtml(chunk.text || "")}
                                </div>

                            </div>
                        `;

                    }).join("")}

                </div>

            </div>
        `;
    }


    message.innerHTML = `
        <div class="avatar">🤖</div>

        <div class="message-content">

            <div class="answer-label">
                Assistant
            </div>

            <div class="message-bubble">
                ${formatAnswer(data.answer)}
            </div>

            <div class="confidence">
                Confidence: ${confidence}
            </div>

            ${sourcesHtml}

        </div>
    `;

    chatContainer.appendChild(message);

    scrollToBottom();
}


// ============================
// Loading message
// ============================

function addLoadingMessage() {

    const message = document.createElement("div");

    message.className = "message assistant";
    message.id = "loadingMessage";

    message.innerHTML = `
        <div class="avatar">🤖</div>

        <div class="message-content">

            <div class="message-bubble">

                <div class="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>

            </div>

        </div>
    `;

    chatContainer.appendChild(message);

    scrollToBottom();
}


// ============================
// Remove loading
// ============================

function removeLoadingMessage() {

    const loading =
        document.getElementById("loadingMessage");

    if (loading) {
        loading.remove();
    }
}


// ============================
// Send question
// ============================

async function sendQuestion(question) {

    question = question.trim();

    if (!question) {
        return;
    }

    addUserMessage(question);

    questionInput.value = "";
    questionInput.style.height = "auto";

    sendButton.disabled = true;

    addLoadingMessage();

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                query: question,
                top_k: 5
            })

        });


        const data = await response.json();

        removeLoadingMessage();


        if (!response.ok) {

            throw new Error(
                data.detail || "Something went wrong."
            );

        }


        addAssistantMessage(data);

    }

    catch (error) {

        removeLoadingMessage();

        addAssistantMessage({
            answer:
                "I couldn't process your request. Please try again.",
            retrieved_chunks: [],
            confidence_score: 0
        });

        console.error(error);

    }

    finally {

        sendButton.disabled = false;

        questionInput.focus();

    }
}


// ============================
// Form submit
// ============================

chatForm.addEventListener("submit", event => {

    event.preventDefault();

    sendQuestion(questionInput.value);

});


// ============================
// Enter key
// ============================

questionInput.addEventListener("keydown", event => {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        chatForm.requestSubmit();

    }

});


// ============================
// Auto resize textarea
// ============================

questionInput.addEventListener("input", () => {

    questionInput.style.height = "auto";

    questionInput.style.height =
        Math.min(
            questionInput.scrollHeight,
            130
        ) + "px";

});


// ============================
// Example questions
// ============================

document
    .querySelectorAll("[data-question]")
    .forEach(button => {

        button.addEventListener("click", () => {

            const question =
                button.dataset.question;

            sendQuestion(question);

        });

    });


// ============================
// Clear chat
// ============================

clearChatButton.addEventListener("click", () => {

    chatContainer.innerHTML = `
        <div class="welcome">

            <div class="welcome-icon">🤖</div>

            <h2>Ask about Agentic AI</h2>

            <p>
                Ask questions about the Agentic AI knowledge source.
                Answers are generated using retrieved document context.
            </p>

            <div class="welcome-chips">

                <button
                    class="chip"
                    data-question="What is Agentic AI?">
                    What is Agentic AI?
                </button>

                <button
                    class="chip"
                    data-question="What is the role of memory?">
                    What is the role of memory?
                </button>

                <button
                    class="chip"
                    data-question="What is multi-agent orchestration?">
                    Multi-agent orchestration
                </button>

            </div>

        </div>
    `;


    document
        .querySelectorAll("[data-question]")
        .forEach(button => {

            button.addEventListener("click", () => {

                sendQuestion(
                    button.dataset.question
                );

            });

        });

});


// ============================
// Helpers
// ============================

function scrollToBottom() {

    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth"
    });

}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function formatAnswer(text) {

    return escapeHtml(text || "")
        .replace(/\n/g, "<br>");

}