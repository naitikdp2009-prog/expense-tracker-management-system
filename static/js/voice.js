/* ==========================================================================
   Voice Expense Input Module - Browser Web Speech API Integration
   ========================================================================== */

function initVoiceRecognition() {
    const micBtn = document.getElementById('startVoiceBtn');
    const voiceStatus = document.getElementById('voiceStatus');
    const speechResultBox = document.getElementById('speechResultBox');

    if (!micBtn) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        voiceStatus.innerHTML = "<span class='text-danger'>Web Speech API is not supported in this browser. Please enter manually.</span>";
        micBtn.disabled = true;
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    micBtn.addEventListener('click', () => {
        try {
            recognition.start();
            voiceStatus.innerHTML = "<span class='text-warning'><i class='fas fa-spinner fa-spin'></i> Listening... Speak now (e.g., 'Spent 250 rupees on food')</span>";
            micBtn.classList.add('btn-danger');
        } catch (e) {
            console.error(e);
        }
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        voiceStatus.innerHTML = `<span class='text-success'><i class='fas fa-check-circle'></i> Heard: "${transcript}"</span>`;
        micBtn.classList.remove('btn-danger');
        parseVoiceTranscript(transcript);
    };

    recognition.onerror = (event) => {
        voiceStatus.innerHTML = `<span class='text-danger'><i class='fas fa-exclamation-circle'></i> Speech recognition error: ${event.error}</span>`;
        micBtn.classList.remove('btn-danger');
    };
}

function parseVoiceTranscript(text) {
    const textLower = text.toLowerCase();
    
    // 1. Extract Amount (look for digits or rupees/rs/dollars)
    let amount = null;
    const numberMatch = textLower.match(/(\d+[\.,]?\d*)/);
    if (numberMatch) {
        amount = parseFloat(numberMatch[1]);
    }

    // 2. Extract Category
    let categoryId = null;
    const catSelect = document.getElementById('category_id');
    if (catSelect) {
        Array.from(catSelect.options).forEach(opt => {
            if (opt.value && textLower.includes(opt.text.toLowerCase())) {
                categoryId = opt.value;
            }
        });
        if (!categoryId) {
            // Keyword fallbacks
            if (textLower.includes('lunch') || textLower.includes('dinner') || textLower.includes('pizza') || textLower.includes('coffee') || textLower.includes('food')) categoryId = "1"; // Food
            else if (textLower.includes('bus') || textLower.includes('auto') || textLower.includes('cab') || textLower.includes('uber') || textLower.includes('petrol')) categoryId = "2"; // Transport
            else if (textLower.includes('book') || textLower.includes('fee') || textLower.includes('pen') || textLower.includes('college')) categoryId = "4"; // Education
            else if (textLower.includes('recharge') || textLower.includes('bill') || textLower.includes('wifi')) categoryId = "6"; // Bills
        }
    }

    // Populate Form Inputs
    if (amount) {
        document.getElementById('amount').value = amount;
    }
    if (categoryId) {
        document.getElementById('category_id').value = categoryId;
    }
    document.getElementById('description').value = text;
    document.getElementById('notes').value = `Voice auto-parsed: "${text}"`;
}

document.addEventListener('DOMContentLoaded', initVoiceRecognition);
