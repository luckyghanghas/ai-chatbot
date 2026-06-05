document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearChatBtn = document.getElementById('clear-chat');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    const faqList = document.getElementById('faq-list');
    const categoryChips = document.querySelectorAll('.category-chip');

    // Settings elements
    const openSettingsBtn = document.getElementById('open-settings');
    const closeSettingsBtn = document.getElementById('close-settings');
    const cancelSettingsBtn = document.getElementById('cancel-settings');
    const saveSettingsBtn = document.getElementById('save-settings');
    const settingsModal = document.getElementById('settings-modal');
    const apiKeyInput = document.getElementById('gemini-api-key');

    let allFaqs = [];
    let savedApiKey = localStorage.getItem('gemini_api_key') || '';

    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // Modal events
    openSettingsBtn.addEventListener('click', () => {
        settingsModal.classList.add('open');
    });

    const closeModal = () => {
        settingsModal.classList.remove('open');
        apiKeyInput.value = savedApiKey; // revert any unsaved text
    };

    closeSettingsBtn.addEventListener('click', closeModal);
    cancelSettingsBtn.addEventListener('click', closeModal);
    saveSettingsBtn.addEventListener('click', () => {
        savedApiKey = apiKeyInput.value.trim();
        localStorage.setItem('gemini_api_key', savedApiKey);
        settingsModal.classList.remove('open');
    });

    // Fetch FAQs and initialize sidebar
    async function loadFaqs() {
        try {
            const response = await fetch('/api/faqs');
            if (response.ok) {
                allFaqs = await response.json();
                renderFaqs('all');
            }
        } catch (error) {
            console.error('Error fetching FAQs:', error);
            faqList.innerHTML = `<li class="faq-item" style="color: var(--text-muted);">Failed to load FAQ list.</li>`;
        }
    }

    // Render FAQs in sidebar based on category filter
    function renderFaqs(category) {
        faqList.innerHTML = '';
        const filtered = category === 'all' 
            ? allFaqs 
            : allFaqs.filter(faq => faq.category === category);

        if (filtered.length === 0) {
            faqList.innerHTML = `<li class="faq-item" style="color: var(--text-muted); text-align: center;">No FAQs found in this category.</li>`;
            return;
        }

        filtered.forEach(faq => {
            const li = document.createElement('li');
            li.className = 'faq-item';
            li.innerHTML = `
                <span class="faq-item-category">${faq.category}</span>
                <strong>${faq.question}</strong>
            `;
            li.addEventListener('click', () => {
                // If sidebar is open in mobile mode, close it
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                }
                sendUserQuestion(faq.question);
            });
            faqList.appendChild(li);
        });
    }

    // Category filter chips handler
    categoryChips.forEach(chip => {
        chip.addEventListener('click', () => {
            categoryChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            const category = chip.getAttribute('data-category');
            renderFaqs(category);
        });
    });

    // Helper to get time string
    function getTimeString() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Append Message to Chat Window
    function appendMessage(sender, text, confidence = null, suggestions = null, isGenerated = false) {
        // Remove welcome card if it exists
        const welcomeCard = document.querySelector('.welcome-card');
        if (welcomeCard) {
            welcomeCard.remove();
        }

        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        let contentHtml = `<div class="msg-bubble">${text}`;
        
        // Add confidence rating badge for bot responses when matching
        if (sender === 'bot') {
            if (isGenerated) {
                contentHtml += `
                    <br>
                    <div class="confidence-badge" style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border-color: rgba(99, 102, 241, 0.3);">
                        <i class="fa-solid fa-wand-magic-sparkles"></i> AI Generated Answer
                    </div>
                `;
            } else if (confidence !== null && confidence > 0) {
                const pct = Math.round(confidence * 100);
                contentHtml += `
                    <br>
                    <div class="confidence-badge">
                        <i class="fa-solid fa-gauge-high"></i> Match Confidence: ${pct}%
                    </div>
                `;
            }
        }

        // Add suggestion chips inside the bot bubble
        if (sender === 'bot' && suggestions && suggestions.length > 0) {
            contentHtml += `
                <div class="suggestion-box">
                    <span>Related questions you might want to ask:</span>
            `;
            suggestions.forEach(sug => {
                contentHtml += `<button class="suggestion-item-btn" data-query="${sug}">${sug}</button>`;
            });
            contentHtml += `</div>`;
        }

        contentHtml += `<span class="msg-meta">${getTimeString()}</span></div>`;
        msgDiv.innerHTML = contentHtml;
        
        // If there are suggestion buttons, add click listeners
        const suggestionBtns = msgDiv.querySelectorAll('.suggestion-item-btn');
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                sendUserQuestion(query);
            });
        });

        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    // Show/Hide typing indicator
    function showTyping(show) {
        typingIndicator.style.display = show ? 'flex' : 'none';
        scrollToBottom();
    }

    // Scroll to bottom of chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Execute sending user question
    async function sendUserQuestion(question) {
        if (!question.trim()) return;
        
        // Add user bubble
        appendMessage('user', question);
        
        // Show typing indicator
        showTyping(true);

        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            if (savedApiKey) {
                headers['X-Gemini-Key'] = savedApiKey;
            }

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ message: question })
            });

            if (response.ok) {
                const data = await response.json();
                
                // Simulate typing latency for natural feel
                setTimeout(() => {
                    showTyping(false);
                    appendMessage(
                        'bot', 
                        data.answer, 
                        data.confidence, 
                        data.suggestions,
                        data.is_generated
                    );
                }, 600);
            } else {
                throw new Error('API request failed');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            showTyping(false);
            appendMessage('bot', "I'm sorry, I encountered a connection error. Please make sure the backend server is running.");
        }
    }

    // Form submit listener
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = userInput.value;
        userInput.value = '';
        sendUserQuestion(text);
    });

    // Support quick prompt buttons on welcome card
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('prompt-btn')) {
            const query = e.target.textContent;
            sendUserQuestion(query);
        }
    });

    // Clear chat handler
    clearChatBtn.addEventListener('click', () => {
        chatMessages.innerHTML = `
            <div class="welcome-card">
                <div class="welcome-icon">
                    <i class="fa-solid fa-comments"></i>
                </div>
                <h2>Welcome to AI Support!</h2>
                <p>I can answer questions about shipping, payments, account recovery, returns, and troubleshooting instantly. Try typing a question below or pick a popular query:</p>
                <div class="quick-prompts">
                    <button class="prompt-btn">How do I return an item?</button>
                    <button class="prompt-btn">What payment methods do you accept?</button>
                    <button class="prompt-btn">How secure is my payment?</button>
                </div>
            </div>
        `;
    });

    // Mobile sidebar toggling
    toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && 
            !sidebar.contains(e.target) && 
            !toggleSidebarBtn.contains(e.target) && 
            sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }
    });

    // Initialize application
    loadFaqs();
});
