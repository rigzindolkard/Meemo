document.addEventListener("DOMContentLoaded", () => {
  // App State
  const state = {
    sticker: {
      type: "preset",
      presetKey: "cat",
      title: "Dramatic Cat Collapse",
      desc: "An expressive orange cat lying flat on the floor in dramatic exhaustion and defeat",
      src: "cat.svg",
      filename: "cat.svg"
    },
    chatContext: "",
    language: "English",
    currentAnalysis: null,
    isSpeaking: false
  };

  // DOM Elements
  const presetCards = document.querySelectorAll(".preset-card");
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const dropContent = document.getElementById("dropContent");
  const previewContainer = document.getElementById("previewContainer");
  const previewImage = document.getElementById("previewImage");
  const previewFilename = document.getElementById("previewFilename");
  const btnRemovePreview = document.getElementById("btnRemovePreview");
  const chatContextInput = document.getElementById("chatContextInput");
  const btnFillExampleContext = document.getElementById("btnFillExampleContext");
  const langPills = document.querySelectorAll(".lang-pill");
  const btnAnalyze = document.getElementById("btnAnalyze");
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const sarvamStatusBadge = document.getElementById("sarvamStatusBadge");

  // Pipeline & Output Elements
  const pipelineStatusText = document.getElementById("pipelineStatusText");
  const stepVision = document.getElementById("stepVision");
  const stepEmotion = document.getElementById("stepEmotion");
  const stepContext = document.getElementById("stepContext");
  const stepMeme = document.getElementById("stepMeme");
  const stepGenerator = document.getElementById("stepGenerator");
  const allSteps = [stepVision, stepEmotion, stepContext, stepMeme, stepGenerator];

  const emptyState = document.getElementById("emptyState");
  const resultsContainer = document.getElementById("resultsContainer");
  const resultStickerTitle = document.getElementById("resultStickerTitle");
  const resultConfidenceBadge = document.getElementById("resultConfidenceBadge");
  const resultMeaningText = document.getElementById("resultMeaningText");
  const resultEmotionTags = document.getElementById("resultEmotionTags");
  const resultContextText = document.getElementById("resultContextText");
  const resultVisibleText = document.getElementById("resultVisibleText");
  const resultMemeText = document.getElementById("resultMemeText");
  const resultAlternativesList = document.getElementById("resultAlternativesList");
  const resultRepliesList = document.getElementById("resultRepliesList");

  const btnVoiceRead = document.getElementById("btnVoiceRead");
  const btnCopyExplanation = document.getElementById("btnCopyExplanation");
  const toast = document.getElementById("toast");

  // Follow-up Elements
  const followUpChips = document.querySelectorAll(".chip-btn");
  const followUpInput = document.getElementById("followUpInput");
  const btnSendFollowUp = document.getElementById("btnSendFollowUp");
  const followUpResponseBox = document.getElementById("followUpResponseBox");
  const followUpResponseContent = document.getElementById("followUpResponseContent");

  // Sample Contexts for Presets
  const sampleContexts = {
    cat: "Manager: 'Team, please prepare the complete financial audit report by 8:30 AM tomorrow.'\nMe: *sends this sticker*",
    doge: "Friend: 'Wait, did you accidentally tell Sarah about her surprise birthday party?!'\nMe: *sends this sticker*",
    herapheri: "Client: 'Can we build an entire AI social network with live video streaming for ₹5,000 in 2 days?'\nMe: *sends this sticker*",
    peeking: "Group Chat: 'Everyone is arguing heatedly about politics in the college group...'\nMe: *sends this sticker*"
  };

  // Toast Function
  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.remove("hidden");
    setTimeout(() => {
      toast.classList.add("hidden");
    }, 2800);
  }

  // Theme Toggler
  themeToggleBtn.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nextTheme);
    themeToggleBtn.querySelector(".theme-icon").textContent = nextTheme === "dark" ? "🌙" : "☀️";
    localStorage.setItem("theme", nextTheme);
  });

  // Restore saved theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeToggleBtn.querySelector(".theme-icon").textContent = savedTheme === "dark" ? "🌙" : "☀️";
  }

  // Preset Selection
  presetCards.forEach(card => {
    card.addEventListener("click", () => {
      presetCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");

      const key = card.getAttribute("data-preset");
      const title = card.getAttribute("data-title");
      const desc = card.getAttribute("data-desc");
      const img = card.querySelector("img").src;

      state.sticker = {
        type: "preset",
        presetKey: key,
        title: title,
        desc: desc,
        src: img,
        filename: `${key}.svg`
      };

      // Reset dropzone preview to show active preset
      dropContent.classList.remove("hidden");
      previewContainer.classList.add("hidden");
    });
  });

  // Example Context Button
  btnFillExampleContext.addEventListener("click", () => {
    const key = state.sticker.presetKey || "cat";
    chatContextInput.value = sampleContexts[key] || "Friend: 'Did you finish the assignment?'\nMe: *sends this sticker*";
    chatContextInput.focus();
    showToast("Sample conversation context inserted!");
  });

  // Language Pills Selection
  langPills.forEach(pill => {
    pill.addEventListener("click", () => {
      langPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      state.language = pill.getAttribute("data-lang");
    });
  });

  // File Upload & Drag/Drop
  dropZone.addEventListener("click", () => {
    fileInput.click();
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUploadedFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleUploadedFile(e.target.files[0]);
    }
  });

  // Window Paste listener
  window.addEventListener("paste", (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    for (let index in items) {
      const item = items[index];
      if (item.kind === 'file' && item.type.startsWith('image/')) {
        const blob = item.getAsFile();
        handleUploadedFile(blob, "Pasted_Sticker.png");
        showToast("Sticker pasted from clipboard! 📋");
        break;
      }
    }
  });

  function handleUploadedFile(file, overrideName) {
    const reader = new FileReader();
    reader.onload = (event) => {
      const name = overrideName || file.name;
      const cleanTitle = name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ").replace(/\b\w/g, c => c.toUpperCase());
      state.sticker = {
        type: "upload",
        presetKey: "custom",
        title: cleanTitle || "Uploaded Custom Sticker",
        desc: `Uploaded sticker image '${cleanTitle}'`,
        src: event.target.result,
        filename: name
      };

      // Deselect all preset cards
      presetCards.forEach(c => c.classList.remove("active"));

      // Show in dropzone preview
      dropContent.classList.add("hidden");
      previewContainer.classList.remove("hidden");
      previewImage.src = event.target.result;
      previewFilename.textContent = name;
    };
    reader.readAsDataURL(file);
  }

  btnRemovePreview.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.value = "";
    previewContainer.classList.add("hidden");
    dropContent.classList.remove("hidden");
    state.sticker = {
      type: "empty",
      presetKey: "custom",
      title: "No Sticker Selected",
      desc: "",
      src: "",
      filename: ""
    };
  });

  // Multi-Agent Pipeline Animation Runner
  async function runAgentPipelineVisualizer() {
    pipelineStatusText.textContent = "Multi-agent coordination in progress...";
    pipelineStatusText.style.color = "var(--accent-cyan)";

    // Reset all steps
    allSteps.forEach(s => {
      s.className = "agent-step";
    });

    const stepDelay = (ms) => new Promise(r => setTimeout(r, ms));

    // Agent 1: Vision
    stepVision.classList.add("processing");
    await stepDelay(300);
    stepVision.classList.remove("processing");
    stepVision.classList.add("completed");

    // Agent 2: Emotion
    stepEmotion.classList.add("processing");
    await stepDelay(300);
    stepEmotion.classList.remove("processing");
    stepEmotion.classList.add("completed");

    // Agent 3: Context
    stepContext.classList.add("processing");
    await stepDelay(300);
    stepContext.classList.remove("processing");
    stepContext.classList.add("completed");

    // Agent 4: Meme
    stepMeme.classList.add("processing");
    await stepDelay(300);
    stepMeme.classList.remove("processing");
    stepMeme.classList.add("completed");

    // Agent 5: Explanation Generator
    stepGenerator.classList.add("processing");
    await stepDelay(300);
    stepGenerator.classList.remove("processing");
    stepGenerator.classList.add("completed");

    pipelineStatusText.textContent = "Analysis Complete ✨";
    pipelineStatusText.style.color = "var(--accent-emerald)";
  }

  // Primary Analysis Action
  btnAnalyze.addEventListener("click", async () => {
    state.chatContext = chatContextInput.value.trim();

    btnAnalyze.disabled = true;
    btnAnalyze.querySelector(".btn-text").textContent = "Decoding Sticker...";

    // Start UI Pipeline Animation
    const animPromise = runAgentPipelineVisualizer();

    // Call Backend API
    try {
      const response = await fetch("/api/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sticker_name: state.sticker.presetKey || "custom",
          sticker_description: state.sticker.desc,
          chat_context: state.chatContext,
          language: state.language
        })
      });

      const res = await response.json();
      await animPromise; // Ensure animation finishes cleanly

      if (res.status === "success" && res.data) {
        state.currentAnalysis = res.data;
        renderResults(res.data, res.sarvam_live, res.sarvam_notice);
      } else {
        alert("Unable to analyze sticker. Please check server.");
      }
    } catch (err) {
      console.error(err);
      await animPromise;
      alert("Error contacting the backend server. Is server.py running?");
    } finally {
      btnAnalyze.disabled = false;
      btnAnalyze.querySelector(".btn-text").textContent = "Understand This Sticker";
    }
  });

  // Render Analysis Results
  function renderResults(data, isSarvamLive, sarvamNotice) {
    emptyState.classList.add("hidden");
    resultsContainer.classList.remove("hidden");

    // Update Sarvam Badge
    if (isSarvamLive) {
      sarvamStatusBadge.innerHTML = `<span class="status-dot"></span><span class="badge-label">Sarvam AI (105B Live)</span>`;
      sarvamStatusBadge.style.borderColor = "rgba(16, 185, 129, 0.4)";
    } else if (sarvamNotice) {
      sarvamStatusBadge.innerHTML = `<span class="status-dot" style="background:#f59e0b;box-shadow:0 0 8px #f59e0b;"></span><span class="badge-label" title="${sarvamNotice}">Multi-Agent Engine</span>`;
      sarvamStatusBadge.style.borderColor = "rgba(245, 158, 11, 0.4)";
    }

    resultStickerTitle.textContent = state.sticker.title || "Analyzed Sticker";
    resultConfidenceBadge.textContent = `${data.confidence || "High"} Confidence`;

    // Meaning
    resultMeaningText.textContent = data.primary_meaning || "No meaning provided.";

    // Emotion Tags
    resultEmotionTags.innerHTML = "";
    (data.emotional_tone || ["Playful"]).forEach(tone => {
      const span = document.createElement("span");
      span.className = "tag-badge";
      span.textContent = tone;
      resultEmotionTags.appendChild(span);
    });

    // Context
    resultContextText.textContent = data.contextual_interpretation || "Context independent.";

    // Visible content & Meme
    resultVisibleText.textContent = data.visual_description || state.sticker.desc;
    resultMemeText.textContent = data.meme_reference || "Common reaction trope.";

    // Alternatives
    resultAlternativesList.innerHTML = "";
    (data.alternative_meanings || []).forEach(alt => {
      const li = document.createElement("li");
      li.textContent = alt;
      resultAlternativesList.appendChild(li);
    });

    // Suggested Replies
    resultRepliesList.innerHTML = "";
    (data.suggested_replies || []).forEach(reply => {
      const item = document.createElement("div");
      item.className = "reply-item";
      item.innerHTML = `
        <div class="reply-left">
          <span class="reply-badge">${reply.type || "Reply"}</span>
          <span class="reply-text">"${reply.text}"</span>
        </div>
        <span class="reply-copy-icon" title="Copy reply">📋</span>
      `;
      item.addEventListener("click", () => {
        navigator.clipboard.writeText(reply.text);
        showToast(`Copied: "${reply.text}"! 💬`);
      });
      resultRepliesList.appendChild(item);
    });

    // Clear follow-up response
    followUpResponseBox.classList.add("hidden");
    followUpResponseContent.textContent = "";

    // Scroll results into view smoothly
    resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Voice Readout (Text-To-Speech)
  btnVoiceRead.addEventListener("click", () => {
    if (!('speechSynthesis' in window)) {
      alert("Text-to-speech is not supported by your browser.");
      return;
    }

    if (state.isSpeaking) {
      window.speechSynthesis.cancel();
      state.isSpeaking = false;
      btnVoiceRead.classList.remove("speaking");
      btnVoiceRead.querySelector(".voice-text").textContent = "Listen";
      return;
    }

    if (!state.currentAnalysis) return;

    const speechText = `${resultStickerTitle.textContent}. What it means: ${state.currentAnalysis.primary_meaning}. Context: ${state.currentAnalysis.contextual_interpretation}`;
    const utterance = new SpeechSynthesisUtterance(speechText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // Pick Indian/Hindi accent voice if language is Hindi or Hinglish
    if (state.language === "Hindi" || state.language === "Hinglish") {
      const voices = window.speechSynthesis.getVoices();
      const hiVoice = voices.find(v => v.lang.includes("hi") || v.lang.includes("IN"));
      if (hiVoice) utterance.voice = hiVoice;
    }

    utterance.onend = () => {
      state.isSpeaking = false;
      btnVoiceRead.classList.remove("speaking");
      btnVoiceRead.querySelector(".voice-text").textContent = "Listen";
    };

    utterance.onerror = () => {
      state.isSpeaking = false;
      btnVoiceRead.classList.remove("speaking");
      btnVoiceRead.querySelector(".voice-text").textContent = "Listen";
    };

    window.speechSynthesis.speak(utterance);
    state.isSpeaking = true;
    btnVoiceRead.classList.add("speaking");
    btnVoiceRead.querySelector(".voice-text").textContent = "Stop";
  });

  // Copy Full Explanation
  btnCopyExplanation.addEventListener("click", () => {
    if (!state.currentAnalysis) return;
    const textToCopy = `📌 Sticker: ${resultStickerTitle.textContent}
💡 Meaning: ${state.currentAnalysis.primary_meaning}
🎭 Tone: ${(state.currentAnalysis.emotional_tone || []).join(", ")}
🎯 Context: ${state.currentAnalysis.contextual_interpretation}
🌐 Reference: ${state.currentAnalysis.meme_reference}
💬 Suggested Reply: "${state.currentAnalysis.suggested_replies?.[0]?.text || ''}"
— Decoded with Sticker Understander`;

    navigator.clipboard.writeText(textToCopy);
    showToast("Full explanation copied to clipboard! 📋");
  });

  // Follow-Up Queries
  followUpChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const query = chip.getAttribute("data-query");
      followUpInput.value = query;
      sendFollowUp(query);
    });
  });

  btnSendFollowUp.addEventListener("click", () => {
    const q = followUpInput.value.trim();
    if (q) sendFollowUp(q);
  });

  followUpInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const q = followUpInput.value.trim();
      if (q) sendFollowUp(q);
    }
  });

  async function sendFollowUp(question) {
    if (!state.currentAnalysis) {
      alert("Please analyze a sticker first!");
      return;
    }

    followUpResponseBox.classList.remove("hidden");
    followUpResponseContent.innerHTML = "<em>Thinking...</em>";

    try {
      const res = await fetch("/api/followup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question,
          current_analysis: state.currentAnalysis,
          language: state.language
        })
      });
      const data = await res.json();
      if (data.status === "success") {
        followUpResponseContent.textContent = data.reply;
      } else {
        followUpResponseContent.textContent = "Could not process question.";
      }
    } catch (e) {
      console.error(e);
      followUpResponseContent.textContent = "Error communicating with server.";
    }
  }

  // Pre-load default sticker on startup
  presetCards[0].click();
});
