// const sessionId = "sess-" + Math.random().toString(36).substring(2, 9);
// document.getElementById("sessionDisplay").textContent = `ID: ${sessionId}`;

// const chatHistory = document.getElementById("chatHistory");
// const queryForm = document.getElementById("queryForm");
// const queryInput = document.getElementById("queryInput");
// const voiceInputBtn = document.getElementById("voiceInputBtn");
// const ttsToggle = document.getElementById("ttsToggle");
// const intentTag = document.getElementById("intentTag");
// const confidenceBar = document.getElementById("confidenceBar");
// const confidenceText = document.getElementById("confidenceText");
// const chunksList = document.getElementById("chunksList");

// const uploadForm = document.getElementById("uploadForm");
// const fileInput = document.getElementById("fileInput");
// const uploadStatus = document.getElementById("uploadStatus");
// const uploadBtn = document.getElementById("uploadBtn");
// const docAnalysisCard = document.getElementById("docAnalysisCard");
// const docAnalysisDetails = document.getElementById("docAnalysisDetails");

// // File Upload & Diagnostic Analysis Handling
// uploadForm.addEventListener("submit", async (e) => {
//   e.preventDefault();
//   if (!fileInput.files.length) return;

//   const file = fileInput.files[0];
//   const formData = new FormData();
//   formData.append("file", file);

//   uploadBtn.disabled = true;
//   uploadStatus.textContent = `Uploading and analyzing ${file.name}...`;

//   try {
//     const res = await fetch("/api/upload", { method: "POST", body: formData });
//     const data = await res.json();

//     if (data.status === "success") {
//       const a = data.analysis;
//       uploadStatus.textContent = `Ready: ${a.file_name} (${a.generated_chunks} chunks generated)`;
      
//       docAnalysisCard.classList.remove("hidden");
//       docAnalysisDetails.innerHTML = `
//         <p><strong>File:</strong> ${a.file_name}</p>
//         <p><strong>Words:</strong> ${a.total_words} | <strong>Chunks:</strong> ${a.generated_chunks}</p>
//         <p><strong>Detected Entities:</strong> ${a.key_topics_detected.join(", ")}</p>
//         <p class="text-[11px] text-slate-500 italic mt-1">First chunk preview: "${a.first_chunk_preview.substring(0, 110)}..."</p>
//       `;

//       appendMessage("assistant", `Successfully ingested and analyzed **${a.file_name}**. Extracted ${a.generated_chunks} chunks. You can now run factual, procedural, or comparative questions against it.`);
//     } else {
//       uploadStatus.textContent = "Upload failed: " + data.message;
//     }
//   } catch (err) {
//     uploadStatus.textContent = "Error processing upload.";
//   } finally {
//     uploadBtn.disabled = false;
//   }
// });

// // Milestone 3.3: Web Speech API (STT)
// const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// if (SpeechRecognition) {
//   const recognition = new SpeechRecognition();
//   recognition.continuous = false;
//   recognition.interimResults = false;

//   voiceInputBtn.addEventListener("click", () => {
//     recognition.start();
//     voiceInputBtn.classList.add("bg-red-500/20", "text-red-400");
//   });

//   recognition.onresult = (event) => {
//     queryInput.value = event.results[0][0].transcript;
//     voiceInputBtn.classList.remove("bg-red-500/20", "text-red-400");
//     queryForm.dispatchEvent(new Event("submit"));
//   };

//   recognition.onerror = () => {
//     voiceInputBtn.classList.remove("bg-red-500/20", "text-red-400");
//   };
// } else {
//   voiceInputBtn.disabled = true;
//   voiceInputBtn.title = "Web Speech Recognition not supported in this browser";
// }

// // Milestone 3.3: Text-to-Speech (TTS)
// function speakResponse(text) {
//   if (!ttsToggle.checked || !window.speechSynthesis) return;
//   window.speechSynthesis.cancel();
//   const clean = text.replace(/\[.*?\]/g, "");
//   const utterance = new SpeechSynthesisUtterance(clean);
//   utterance.rate = 1.0;
//   window.speechSynthesis.speak(utterance);
// }

// function appendMessage(role, text) {
//   const msgDiv = document.createElement("div");
//   msgDiv.className = role === "user" 
//     ? "ml-auto max-w-[80%] bg-indigo-600/90 text-white p-3 rounded-xl text-sm leading-relaxed"
//     : "mr-auto max-w-[80%] bg-slate-800/80 text-slate-100 p-3 rounded-xl text-sm border border-slate-700/50 leading-relaxed";
//   msgDiv.innerHTML = text.replace(/\n/g, "<br>");
//   chatHistory.appendChild(msgDiv);
//   chatHistory.scrollTop = chatHistory.scrollHeight;
// }

// // Query Submission & Transparency Handling (Milestones 2.1 - 2.4, 3.4)
// queryForm.addEventListener("submit", async (e) => {
//   e.preventDefault();
//   const query = queryInput.value.trim();
//   if (!query) return;

//   appendMessage("user", query);
//   queryInput.value = "";

//   try {
//     const res = await fetch("/api/resolve", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ session_id: sessionId, query: query })
//     });
//     const data = await res.json();

//     appendMessage("assistant", data.response);
//     speakResponse(data.response);

//     intentTag.textContent = data.intent || "Unknown";
//     const pct = Math.round((data.confidence || 0) * 100);
//     confidenceBar.style.width = pct + "%";
//     confidenceText.textContent = `${pct}% (${data.confidence_label || 'N/A'})`;

//     chunksList.innerHTML = "";
//     if (data.chunks && data.chunks.length > 0) {
//       data.chunks.forEach(c => {
//         const item = document.createElement("div");
//         item.className = "p-2.5 rounded bg-slate-900 border border-slate-800 text-xs space-y-1";
//         item.innerHTML = `
//           <div class="flex justify-between font-mono text-slate-400">
//             <span>[${c.id}] ${c.source}</span>
//             <span class="text-emerald-400 font-semibold">Score: ${c.score}</span>
//           </div>
//           <p class="text-slate-300 leading-normal">${c.content}</p>
//         `;
//         chunksList.appendChild(item);
//       });
//     } else {
//       chunksList.innerHTML = '<div class="text-xs text-slate-500 italic">No chunks retrieved or query handled via clarification.</div>';
//     }
//   } catch (err) {
//     appendMessage("assistant", "Orchestrator error encountered while resolving query.");
//   }

//   function appendComparativeBotMessage(data) {
//   const container = document.getElementById("chatHistory");
//   if (!container) return;

//   const div = document.createElement("div");
//   div.style.cssText = "display: flex; justify-content: flex-start; margin: 10px 0;";

//   div.innerHTML = `
//     <div style="background: #0f1c3f; color: #e2e8f0; padding: 16px; border-radius: 12px; border: 1px solid #1e2c53; width: 100%; max-width: 900px; font-size: 0.88rem;">
      
//       <!-- Top Badges -->
//       <div style="display: flex; gap: 8px; margin-bottom: 12px;">
//         <span style="background: #0284c7; color: #fff; font-size: 0.72rem; padding: 3px 8px; border-radius: 4px; font-weight: bold;">
//           HISTORIC PDF + GEMINI HYBRID
//         </span>
//       </div>

//       <!-- Side-by-Side Comparative Grid -->
//       <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;">
        
//         <!-- Left Box: PDF Grounded Answer -->
//         <div style="background: #081024; padding: 12px; border-radius: 8px; border: 1px solid #23345d;">
//           <h4 style="color: #38bdf8; margin-bottom: 8px; font-size: 0.85rem;">📄 From Uploaded PDFs (With Citations)</h4>
//           <div style="line-height: 1.5; color: #cbd5e1;">
//             ${(data.pdf_grounded_answer || "").replace(/\n/g, "<br>")}
//           </div>
//         </div>

//         <!-- Right Box: Gemini API Answer -->
//         <div style="background: #081024; padding: 12px; border-radius: 8px; border: 1px solid #23345d;">
//           <h4 style="color: #a855f7; margin-bottom: 8px; font-size: 0.85rem;">✨ General Gemini API Answer</h4>
//           <div style="line-height: 1.5; color: #cbd5e1;">
//             ${(data.gemini_api_answer || "").replace(/\n/g, "<br>")}
//           </div>
//         </div>

//       </div>

//       <!-- Bottom Comparative Summary -->
//       <div style="background: #16264f; padding: 12px; border-radius: 8px; border: 1px solid #2d437e;">
//         <h4 style="color: #f59e0b; margin-bottom: 6px; font-size: 0.82rem;">📊 Comparative Analysis</h4>
//         <div style="line-height: 1.4; color: #f1f5f9;">
//           ${(data.comparison_summary || "").replace(/\n/g, "<br>")}
//         </div>
//       </div>

//     </div>
//   `;

//   container.appendChild(div);
//   container.scrollTop = container.scrollHeight;
// }
// });

const API_BASE = window.location.origin;
let activeFile = null;

document.addEventListener("DOMContentLoaded", () => {
  loadUploadedDocuments();

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");
  const sendBtn = document.getElementById("sendBtn");
  const queryInput = document.getElementById("queryInput");

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        activeFile = e.target.files[0];
        document.getElementById("dropLabel").innerHTML = `Selected: <strong>${activeFile.name}</strong>`;
      }
    });
  }

  if (uploadBtn) uploadBtn.addEventListener("click", uploadSelectedFile);
  if (sendBtn) sendBtn.addEventListener("click", executeQuery);
  if (queryInput) {
    queryInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); executeQuery(); }
    });
  }
});

async function loadUploadedDocuments() {
  const container = document.getElementById("documentsList");
  if (!container) return;
  try {
    const res = await fetch(`${API_BASE}/api/documents`);
    const data = await res.json();
    if (!data.documents || data.documents.length === 0) {
      container.innerHTML = `<p style="color: #64748b; font-size: 0.8rem;">No past documents stored.</p>`;
      return;
    }
    container.innerHTML = data.documents.map(doc => `
      <div class="doc-item-row">
        <span class="doc-name">📄 ${doc.filename}</span>
        <span class="doc-chunks">${doc.chunks} chunks</span>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<p style="color: #ef4444; font-size: 0.78rem;">Failed to load index.</p>`;
  }
}

async function uploadSelectedFile() {
  const fileInput = document.getElementById("fileInput");
  const fileToUpload = activeFile || (fileInput && fileInput.files[0]);
  if (!fileToUpload) { alert("Select a document first."); return; }

  const formData = new FormData();
  formData.append("file", fileToUpload);

  try {
    const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    alert(`Successfully stored and indexed ${data.filename} (${data.chunks_count} chunks)!`);
    loadUploadedDocuments();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

async function executeQuery() {
  const queryInput = document.getElementById("queryInput");
  const query = queryInput.value.trim();
  if (!query) return;

  appendUserMessage(query);
  queryInput.value = "";

  try {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Query failed");
    appendComparativeBotMessage(data);
  } catch (err) {
    appendBotError(err.message);
  }
}

function appendUserMessage(text) {
  const container = document.getElementById("chatHistory");
  const div = document.createElement("div");
  div.style.cssText = "display: flex; justify-content: flex-end; margin: 6px 0;";
  div.innerHTML = `<div style="background: #2563eb; color: #fff; padding: 10px 14px; border-radius: 10px; max-width: 75%; font-size: 0.9rem;">${text}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendComparativeBotMessage(data) {
  const container = document.getElementById("chatHistory");
  const div = document.createElement("div");
  div.style.cssText = "display: flex; justify-content: flex-start; margin: 10px 0;";

  div.innerHTML = `
    <div style="background: #0f1c3f; color: #e2e8f0; padding: 16px; border-radius: 12px; border: 1px solid #1e2c53; width: 100%;">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;">
        <div style="background: #081024; padding: 12px; border-radius: 8px; border: 1px solid #23345d;">
          <h4 style="color: #38bdf8; margin-bottom: 8px; font-size: 0.85rem;">📄 Past/Present PDF Answer (With Citations)</h4>
          <div style="line-height: 1.5; color: #cbd5e1; font-size: 0.85rem;">${(data.pdf_grounded_answer || "").replace(/\n/g, "<br>")}</div>
        </div>
        <div style="background: #081024; padding: 12px; border-radius: 8px; border: 1px solid #23345d;">
          <h4 style="color: #a855f7; margin-bottom: 8px; font-size: 0.85rem;">✨ Gemini API General Knowledge</h4>
          <div style="line-height: 1.5; color: #cbd5e1; font-size: 0.85rem;">${(data.gemini_api_answer || "").replace(/\n/g, "<br>")}</div>
        </div>
      </div>
      <div style="background: #16264f; padding: 10px; border-radius: 8px; border: 1px solid #2d437e;">
        <h4 style="color: #f59e0b; margin-bottom: 4px; font-size: 0.8rem;">📊 Comparative Summary</h4>
        <div style="font-size: 0.82rem; color: #f1f5f9;">${(data.comparison_summary || "").replace(/\n/g, "<br>")}</div>
      </div>
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendBotError(errMsg) {
  const container = document.getElementById("chatHistory");
  const div = document.createElement("div");
  div.style.cssText = "background: #ef4444; color: #fff; padding: 10px; border-radius: 8px; font-size: 0.85rem; margin: 6px 0;";
  div.innerText = `Error: ${errMsg}`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}