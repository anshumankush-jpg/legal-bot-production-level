/**
 * Artillity Frontend - Enhanced with Welcome Flow and Suggested Questions
 * Multi-modal embedding engine frontend
 */

// API Configuration
const API_BASE = "http://localhost:8000/api/artillity";

// State
let hasDocuments = false;
let documentCount = 0;

// DOM Elements
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const uploadStatus = document.getElementById('upload-status');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatWindow = document.getElementById('chat-window');
const sendBtn = document.getElementById('send-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showWelcomeMessage();
});

/**
 * Show initial welcome message asking what document type to embed
 */
function showWelcomeMessage() {
    chatWindow.innerHTML = '';
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-container';
    welcomeDiv.innerHTML = `
        <div class="welcome-message">
            <p class="welcome-title">👋 Hi! I'm Artillity</p>
            <p class="welcome-text">I'm your AI assistant that can help you search and understand your documents, images, and text files.</p>
            <p class="welcome-question">What kind of document would you like to embed today?</p>
            <div class="document-options">
                <button class="doc-option-btn" onclick="showUploadHint('text')">📝 Text Document</button>
                <button class="doc-option-btn" onclick="showUploadHint('image')">🖼️ Image</button>
                <button class="doc-option-btn" onclick="showUploadHint('document')">📄 PDF/DOCX</button>
            </div>
            <p class="welcome-hint">You can upload files using the panel on the left →</p>
        </div>
    `;
    chatWindow.appendChild(welcomeDiv);
}

/**
 * Show hint for selected document type
 */
function showUploadHint(type) {
    const hints = {
        text: "Great! Upload .txt files to get started. I'll help you search through them.",
        image: "Perfect! Upload images (.png, .jpg, etc.) and I can search for similar ones or describe them.",
        document: "Excellent! Upload PDF or DOCX files and I'll extract and index all the content for you."
    };
    
    addMessage('bot', hints[type] || "Upload your files using the panel on the left!", null, false);
}

/**
 * Add a message to the chat window
 */
function addMessage(role, text, meta = null, isResults = false) {
    // Remove welcome message on first interaction
    const welcomeContainer = chatWindow.querySelector('.welcome-container');
    if (welcomeContainer && role === 'user') {
        welcomeContainer.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    
    if (isResults && role === 'bot') {
        bubble.classList.add('results');
        bubble.innerHTML = text;
    } else {
        bubble.innerHTML = text;
    }

    messageDiv.appendChild(bubble);

    if (meta) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'meta';
        metaDiv.textContent = meta;
        messageDiv.appendChild(metaDiv);
    }

    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

/**
 * Show suggested questions after document upload
 */
function showSuggestedQuestions(questions, fileName) {
    if (!questions || questions.length === 0) return;
    
    let questionsHTML = `
        <div class="suggested-questions">
            <p class="suggested-intro">
                <strong>Hi, my name is Artillity!</strong> I've read through <strong>${fileName}</strong>. 
                Here are some questions you might want to ask:
            </p>
            <div class="questions-list">
    `;
    
    const timestamp = Date.now();
    questions.forEach((question, index) => {
        const questionId = `question-${timestamp}-${index}`;
        questionsHTML += `
            <button class="question-btn" data-question="${escapeHtml(question)}" id="${questionId}">
                ${escapeHtml(question)}
            </button>
        `;
    });
    
    questionsHTML += `</div></div>`;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    const bubble = document.createElement('div');
    bubble.className = 'bubble results';
    bubble.innerHTML = questionsHTML;
    messageDiv.appendChild(bubble);
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    
    // Add event listeners to question buttons
    questions.forEach((question, index) => {
        const questionId = `question-${timestamp}-${index}`;
        setTimeout(() => {
            const btn = document.getElementById(questionId);
            if (btn) {
                btn.addEventListener('click', () => askQuestion(question));
            }
        }, 100);
    });
}

/**
 * Ask a suggested question
 */
function askQuestion(question) {
    chatInput.value = question;
    chatForm.dispatchEvent(new Event('submit'));
}

// Make askQuestion available globally
window.askQuestion = askQuestion;

/**
 * Add status message to upload panel
 */
function addStatusMessage(message, type = 'success') {
    const statusItem = document.createElement('div');
    statusItem.className = `status-item ${type}`;
    statusItem.textContent = `• ${message}`;
    uploadStatus.appendChild(statusItem);
    uploadStatus.scrollTop = uploadStatus.scrollHeight;
    return statusItem;
}

/**
 * Handle file upload
 */
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const files = fileInput.files;
    if (!files || files.length === 0) {
        addStatusMessage('Please select at least one file', 'error');
        return;
    }

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    // Process each file
    for (const file of files) {
        let statusElement = null;
        try {
            statusElement = addStatusMessage(`${file.name} - Uploading...`, 'processing');

            const formData = new FormData();
            formData.append('file', file);

            statusElement.textContent = `• ${file.name} - Processing...`;

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 180000);

            try {
                const response = await fetch(`${API_BASE}/upload`, {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
                    throw new Error(errorData.detail || `HTTP ${response.status}`);
                }

                const data = await response.json();

                const contentType = data.content_type || 'unknown';
                const numChunks = data.num_chunks || 0;
                statusElement.className = 'status-item success';
                statusElement.textContent = `• ${file.name} (${contentType}) – ${numChunks} chunk(s) indexed ✓`;

                // Update state
                hasDocuments = true;
                documentCount++;

                // Show success message in chat
                addMessage('bot', `✅ I've successfully indexed <strong>${file.name}</strong>! (${numChunks} chunks)`, null, false);

                // Show suggested questions if available
                if (data.suggested_questions && data.suggested_questions.length > 0) {
                    setTimeout(() => {
                        showSuggestedQuestions(data.suggested_questions, file.name);
                    }, 500);
                }

            } catch (fetchError) {
                clearTimeout(timeoutId);
                if (fetchError.name === 'AbortError') {
                    throw new Error('Upload timeout - file is too large.');
                }
                throw fetchError;
            }

        } catch (error) {
            console.error('Upload error:', error);
            if (statusElement) {
                statusElement.className = 'status-item error';
                statusElement.textContent = `• ${file.name} – Error: ${error.message}`;
            } else {
                addStatusMessage(`${file.name} – Error: ${error.message}`, 'error');
            }
        }
    }

    fileInput.value = '';
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Upload & Index';
});

/**
 * Handle chat/search with AI
 */
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const query = chatInput.value.trim();
    if (!query) {
        return;
    }

    // Check if this is an image search
    const isImageSearch = query.toLowerCase().includes('image') || 
                         query.toLowerCase().includes('picture') ||
                         query.toLowerCase().includes('photo') ||
                         query.toLowerCase().includes('show me') && query.toLowerCase().includes('image');

    // Add user message
    addMessage('user', query);
    chatInput.value = '';

    // Add thinking message
    const thinkingId = Date.now();
    const thinkingDiv = document.createElement('div');
    thinkingDiv.id = `thinking-${thinkingId}`;
    thinkingDiv.className = 'message bot';
    const thinkingBubble = document.createElement('div');
    thinkingBubble.className = 'bubble thinking';
    thinkingBubble.textContent = isImageSearch ? 'Searching for images...' : 'Thinking with Artillity AI…';
    thinkingDiv.appendChild(thinkingBubble);
    chatWindow.appendChild(thinkingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    sendBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                k: 5,
                use_rag: true,
                is_image_search: isImageSearch
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Chat failed' }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();

        // Remove thinking message
        const thinkingElement = document.getElementById(`thinking-${thinkingId}`);
        if (thinkingElement) {
            thinkingElement.remove();
        }

        // Display AI answer
        const answer = data.answer || 'No answer generated.';
        const sources = data.sources || [];
        const numSources = data.num_sources || 0;

        let answerHTML = `<div class="ai-answer">${formatAnswer(answer)}</div>`;
        
        if (sources.length > 0) {
            answerHTML += `<div class="sources-section"><strong>Sources (${numSources}):</strong><ul class="sources-list">`;
            sources.forEach((source) => {
                const file = source.file || 'Unknown';
                const preview = source.preview || '';
                answerHTML += `
                    <li class="source-item">
                        <span class="source-file">${escapeHtml(file)}</span>
                        ${preview ? `<div class="source-preview">${escapeHtml(preview)}</div>` : ''}
                    </li>
                `;
            });
            answerHTML += `</ul></div>`;
        }

        addMessage('bot', answerHTML, `Artillity AI • ${numSources} source(s)`, true);

    } catch (error) {
        console.error('Chat error:', error);

        const thinkingElement = document.getElementById(`thinking-${thinkingId}`);
        if (thinkingElement) {
            thinkingElement.remove();
        }

        addMessage('bot', `Error: ${error.message}`, null, false);
    } finally {
        sendBtn.disabled = false;
    }
});

/**
 * Format answer text (preserve line breaks, etc.)
 */
function formatAnswer(text) {
    const escaped = escapeHtml(text);
    return escaped.replace(/\n/g, '<br>');
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle Enter key in chat input
 */
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});
