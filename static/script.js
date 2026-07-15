document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // DOM ELEMENTS
    // ==========================================
    // Navigation Tabs
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const pageTitle = document.getElementById("page-title");
    const pageDesc = document.getElementById("page-desc");

    // Chat Interface
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatContainer = document.getElementById("chat-messages-container");
    const sendButton = document.getElementById("send-button");
    const typingIndicator = document.getElementById("typing-indicator");
    const starterButtons = document.querySelectorAll(".starter-btn");

    // Configuration / Sidebar
    const modelRadios = document.querySelectorAll('input[name="nlp-model"]');
    const activeModelBadge = document.getElementById("header-model-badge");
    const themeToggleBtn = document.getElementById("theme-toggle");

    // Knowledge Base Explorer
    const kbGridContainer = document.getElementById("kb-grid-container");
    const kbSearchInput = document.getElementById("kb-search-input");
    const btnClearSearch = document.getElementById("btn-clear-search");
    const btnSearchKb = document.getElementById("btn-search-kb");
    const kbResultsCount = document.getElementById("kb-results-count");
    const kbCurrentModelLbl = document.getElementById("kb-current-model-lbl");
    const kbPagination = document.getElementById("kb-pagination");
    const prevPageBtn = document.getElementById("prev-page-btn");
    const nextPageBtn = document.getElementById("next-page-btn");
    const pageInfoLbl = document.getElementById("page-info-lbl");
    const btnExploreKb = document.getElementById("btn-explore-kb");

    // ==========================================
    // APP STATE
    // ==========================================
    let currentModel = "indobert";
    let similarityThreshold = 0.70; // Tetap di 0.70 sesuai permintaan user
    let kbCurrentPage = 1;
    const kbPageLimit = 12;
    let kbTotalPages = 1;

    // ==========================================
    // TAB MANAGEMENT
    // ==========================================
    navButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetTab = button.getAttribute("data-tab");

            // Update nav active class
            navButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            // Update tab panes active class
            tabPanes.forEach(pane => {
                pane.classList.remove("active");
                if (pane.id === targetTab) {
                    pane.classList.add("active");
                }
            });

            // Update Header Title & Description
            if (targetTab === "chat-tab") {
                pageTitle.textContent = "Chat Assistant";
                pageDesc.textContent = "Tanyakan keluhan atau informasi seputar menstruasi kepada AI";
            } else if (targetTab === "explorer-tab") {
                pageTitle.textContent = "Knowledge Base Explorer";
                pageDesc.textContent = "Telusuri pangkalan data tanya-jawab seputar menstruasi";
                // Fetch Knowledge base when tab opened
                fetchKnowledgeBase();
            }
        });
    });

    // ==========================================
    // MODEL HANDLERS (Deactivated - Only IndoBERT is used)
    // ==========================================
    /*
    modelRadios.forEach(radio => {
        radio.addEventListener("change", (e) => {
            currentModel = e.target.value;
            
            // Update labels
            const modelText = currentModel === "indobert" ? "IndoBERT" : "SBERT";
            activeModelBadge.textContent = `${modelText} NLP Engine`;
            kbCurrentModelLbl.textContent = modelText;

            // Reset KB explorer page
            kbCurrentPage = 1;
            if (document.getElementById("explorer-tab").classList.contains("active")) {
                fetchKnowledgeBase();
            }
        });
    });
    */

    // ==========================================
    // THEME SWITCHER
    // ==========================================
    themeToggleBtn.addEventListener("click", () => {
        const body = document.body;
        const textLabel = themeToggleBtn.querySelector(".theme-text");

        if (body.classList.contains("dark-theme")) {
            body.classList.remove("dark-theme");
            body.classList.add("light-theme");
            textLabel.textContent = "Mode Gelap";
        } else {
            body.classList.remove("light-theme");
            body.classList.add("dark-theme");
            textLabel.textContent = "Mode Terang";
        }
    });

    // ==========================================
    // CHAT CORE ENGINE
    // ==========================================
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        sendMessage();
    });

    // Handle starter question clicks
    starterButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const question = btn.getAttribute("data-question");
            chatInput.value = question;
            sendMessage();
        });
    });

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Append User Bubble
        appendMessageBubble(text, "user");
        chatInput.value = "";

        // Show typing indicator
        typingIndicator.style.display = "flex";
        scrollToBottom();

        // Lock inputs
        chatInput.disabled = true;
        sendButton.disabled = true;

        // API Call
        fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text,
                model: currentModel,
                threshold: similarityThreshold
            })
        })
        .then(res => res.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.style.display = "none";
            
            if (data.status === "success") {
                appendMessageBubble(data.reply, "bot", data);
            } else {
                appendMessageBubble(`Maaf, terjadi kesalahan: ${data.message}`, "bot", null, true);
            }
            scrollToBottom();
        })
        .catch(err => {
            typingIndicator.style.display = "none";
            appendMessageBubble("Maaf, koneksi ke server terputus. Pastikan server Flask Anda berjalan.", "bot", null, true);
            console.error(err);
            scrollToBottom();
        })
        .finally(() => {
            // Unlock inputs
            chatInput.disabled = false;
            sendButton.disabled = false;
            chatInput.focus();
        });
    }

    function appendMessageBubble(message, sender, apiData = null, isError = false) {
        const messageGroup = document.createElement("div");
        messageGroup.classList.add("message-group", `${sender}-message`);

        const avatar = document.createElement("div");
        avatar.classList.add(sender === "bot" ? "bot-avatar" : "user-avatar");
        avatar.innerHTML = sender === "bot" ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';
        
        const bubbleWrapper = document.createElement("div");
        bubbleWrapper.classList.add("message-bubble-wrapper");

        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        
        if (isError) {
            bubble.style.border = "1px solid var(--warning-color)";
            bubble.style.background = "var(--warning-bg)";
        }

        // Format message paragraphs
        const paragraphs = message.split("\n\n");
        let formattedContent = "";
        paragraphs.forEach(p => {
            if (p.trim()) {
                formattedContent += `<p>${p.replace(/\n/g, "<br>")}</p>`;
            }
        });
        bubble.innerHTML = formattedContent;

        bubbleWrapper.appendChild(bubble);

        // Add matching metadata for bot responses
        if (sender === "bot" && apiData) {
            const similarityPercent = (apiData.similarity * 100).toFixed(1);
            
            const metaContainer = document.createElement("div");
            metaContainer.classList.add("chat-match-details");

            // Row 1: Metrics
            let indicatorColor = "var(--accent-color)";
            if (apiData.is_fallback) indicatorColor = "var(--warning-color)";
            
            const row1 = document.createElement("div");
            row1.classList.add("match-metric-row");
            row1.innerHTML = `
                <span class="match-metric-lbl">
                    ${apiData.is_fallback ? '<span class="fallback-badge">Alternatif</span>' : '<span class="badge">Sesuai</span>'} 
                    Similarity
                </span>
                <span class="match-metric-val" style="color: ${indicatorColor}">
                    ${similarityPercent}% 
                    <div class="similarity-indicator-bar">
                        <div class="similarity-indicator-fill" style="width: ${similarityPercent}%; background: ${indicatorColor};"></div>
                    </div>
                </span>
            `;
            metaContainer.appendChild(row1);

            // Row 2: Matched original question (if not fallback)
            if (!apiData.is_fallback && apiData.matched_question) {
                const row2 = document.createElement("div");
                row2.classList.add("match-db-question");
                row2.innerHTML = `<i class="fa-solid fa-check-double"></i> Cocok: "${apiData.matched_question}"`;
                metaContainer.appendChild(row2);
            }

            bubbleWrapper.appendChild(metaContainer);
        }

        // Add Timestamp
        const meta = document.createElement("div");
        meta.classList.add("message-meta");
        const timeString = new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
        meta.textContent = sender === "bot" ? `SiklusCare AI • ${timeString}` : `Anda • ${timeString}`;
        bubbleWrapper.appendChild(meta);

        messageGroup.appendChild(avatar);
        messageGroup.appendChild(bubbleWrapper);
        
        // Remove starter questions grid if present upon new messages
        const starters = document.querySelector(".starter-questions");
        if (starters && sender === "user") {
            starters.remove();
        }

        chatContainer.appendChild(messageGroup);
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // ==========================================
    // KNOWLEDGE BASE EXPLORER
    // ==========================================
    btnSearchKb.addEventListener("click", () => {
        kbCurrentPage = 1;
        fetchKnowledgeBase();
    });

    kbSearchInput.addEventListener("keyup", (e) => {
        if (e.key === "Enter") {
            kbCurrentPage = 1;
            fetchKnowledgeBase();
        }
        
        // Show/hide clear button
        if (kbSearchInput.value.trim()) {
            btnClearSearch.style.display = "block";
        } else {
            btnClearSearch.style.display = "none";
        }
    });

    btnClearSearch.addEventListener("click", () => {
        kbSearchInput.value = "";
        btnClearSearch.style.display = "none";
        kbCurrentPage = 1;
        fetchKnowledgeBase();
        kbSearchInput.focus();
    });

    prevPageBtn.addEventListener("click", () => {
        if (kbCurrentPage > 1) {
            kbCurrentPage--;
            fetchKnowledgeBase();
        }
    });

    nextPageBtn.addEventListener("click", () => {
        if (kbCurrentPage < kbTotalPages) {
            kbCurrentPage++;
            fetchKnowledgeBase();
        }
    });

    function fetchKnowledgeBase() {
        const query = kbSearchInput.value.trim();
        
        // Show loading state in grid
        kbGridContainer.innerHTML = `
            <div class="loading-state">
                <i class="fa-solid fa-spinner fa-spin loading-icon"></i>
                <p>Mencari database pertanyaan...</p>
            </div>
        `;
        kbPagination.style.display = "none";

        const url = `/api/knowledge?model=${currentModel}&query=${encodeURIComponent(query)}&page=${kbCurrentPage}&limit=${kbPageLimit}`;
        
        fetch(url)
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    renderKnowledgeGrid(data.items);
                    kbResultsCount.textContent = `Menampilkan ${data.total_items} data`;
                    
                    // Manage pagination UI
                    kbTotalPages = data.total_pages;
                    if (kbTotalPages > 1) {
                        kbPagination.style.display = "flex";
                        pageInfoLbl.textContent = `Halaman ${data.page} dari ${data.total_pages}`;
                        
                        // Disable buttons appropriately
                        prevPageBtn.disabled = data.page === 1;
                        nextPageBtn.disabled = data.page === data.total_pages;
                    } else {
                        kbPagination.style.display = "none";
                    }
                } else {
                    renderKbError(data.message);
                }
            })
            .catch(err => {
                renderKbError("Gagal terhubung ke database server.");
                console.error(err);
            });
    }

    function renderKnowledgeGrid(items) {
        if (!items || items.length === 0) {
            kbGridContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-folder-open empty-icon"></i>
                    <p>Tidak ditemukan data pertanyaan yang sesuai dengan kata kunci.</p>
                </div>
            `;
            return;
        }

        let html = "";
        items.forEach(item => {
            html += `
                <div class="kb-card">
                    <div class="kb-question">
                        <i class="fa-solid fa-circle-question"></i>
                        <span>${escapeHtml(item.pertanyaan)}</span>
                    </div>
                    <div class="kb-answer">
                        ${escapeHtml(item.jawaban)}
                    </div>
                </div>
            `;
        });
        kbGridContainer.innerHTML = html;
        kbGridContainer.scrollTop = 0;
    }

    function renderKbError(message) {
        kbGridContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-triangle-exclamation text-danger empty-icon"></i>
                <p>Terjadi kesalahan: ${message}</p>
            </div>
        `;
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

});
