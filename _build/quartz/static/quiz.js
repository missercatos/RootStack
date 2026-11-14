// Interactive multiple-choice quizzes.
// Markdown source (a normal `text` fence with a leading QUIZ marker, so the
// syntax highlighter never sees an unknown language):
//
// ```text
// QUIZ
// question: 题干……
// A: 选项 A
// B: 选项 B
// C: 选项 C
// D: 选项 D
// answer: A
// explanation: 解析……
// ```
//
// The script replaces each rendered code block with a clickable card:
// wrong choices turn red, the correct choice turns green, and the
// explanation is revealed below.
(function () {
  "use strict"

  function parseQuiz(text) {
    const data = { options: {} }
    let current = null

    const lines = String(text || "").split(/\r?\n/)
    for (const raw of lines) {
      const line = raw.trim()
      if (!line) continue

      const m = line.match(/^([A-Za-z][A-Za-z0-9_]*)\s*[:：]\s*(.*)$/)
      if (m) {
        const key = m[1].toLowerCase()
        const value = m[2].trim()

        if (key === "question" || key === "answer" || key === "explanation") {
          data[key] = value
          current = key
        } else if (/^[a-z]$/.test(key)) {
          const optionKey = key.toUpperCase()
          data.options[optionKey] = value
          current = "option:" + optionKey
        } else {
          current = null
        }
        continue
      }

      // Continuation line for a multi-line question / option / explanation.
      if (current) {
        if (current.indexOf("option:") === 0) {
          const k = current.slice("option:".length)
          data.options[k] = (data.options[k] + " " + line).trim()
        } else {
          data[current] = ((data[current] || "") + " " + line).trim()
        }
      }
    }

    if (!data.question || !data.answer) return null
    const keys = Object.keys(data.options)
    if (keys.length < 2) return null

    data.answer = String(data.answer).trim().toUpperCase()
    if (!data.options[data.answer]) return null
    return data
  }

  // Render a tiny, safe subset of inline markdown: **bold** and `code`.
  function appendRichText(parent, text) {
    const parts = String(text || "").split(/(\*\*[^*]+\*\*|`[^`]+`)/g)
    for (const part of parts) {
      if (!part) continue
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
        const el = document.createElement("strong")
        el.textContent = part.slice(2, -2)
        parent.appendChild(el)
      } else if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
        const el = document.createElement("code")
        el.textContent = part.slice(1, -1)
        parent.appendChild(el)
      } else {
        parent.appendChild(document.createTextNode(part))
      }
    }
  }

  function buildQuiz(text) {
    const data = parseQuiz(text)
    if (!data) return null

    const card = document.createElement("div")
    card.className = "quiz-card"
    card.setAttribute("role", "group")
    card.setAttribute("aria-label", "选择题")

    const question = document.createElement("div")
    question.className = "quiz-question"
    appendRichText(question, data.question)
    card.appendChild(question)

    const optionList = document.createElement("div")
    optionList.className = "quiz-options"
    const buttons = []

    Object.keys(data.options)
      .sort()
      .forEach(function (key) {
        const btn = document.createElement("button")
        btn.type = "button"
        btn.className = "quiz-option"
        btn.dataset.key = key
        btn.appendChild(document.createTextNode(key + ". "))
        appendRichText(btn, data.options[key])
        btn.addEventListener("click", function () {
          choose(btn)
        })
        optionList.appendChild(btn)
        buttons.push(btn)
      })
    card.appendChild(optionList)

    const status = document.createElement("div")
    status.className = "quiz-status"
    status.setAttribute("aria-live", "polite")
    status.hidden = true
    card.appendChild(status)

    const explanation = document.createElement("div")
    explanation.className = "quiz-explanation"
    explanation.setAttribute("aria-live", "polite")
    explanation.hidden = true
    if (data.explanation) {
      appendRichText(explanation, data.explanation)
    }
    card.appendChild(explanation)

    const reset = document.createElement("button")
    reset.type = "button"
    reset.className = "quiz-reset"
    reset.textContent = "重做"
    reset.hidden = true
    card.appendChild(reset)

    let answered = false

    function choose(btn) {
      if (answered) return
      answered = true

      const correct = data.answer
      const isCorrect = btn.dataset.key === correct

      buttons.forEach(function (b) {
        b.disabled = true
        if (b.dataset.key === correct) b.classList.add("correct")
      })
      if (!isCorrect) btn.classList.add("wrong")

      status.hidden = false
      status.className = "quiz-status " + (isCorrect ? "correct" : "wrong")
      status.textContent = isCorrect ? "回答正确 ✅" : "回答错误 ❌ 正确答案：" + correct

      if (data.explanation) explanation.hidden = false
      reset.hidden = false
    }

    reset.addEventListener("click", function () {
      answered = false
      buttons.forEach(function (b) {
        b.disabled = false
        b.classList.remove("correct", "wrong")
      })
      status.hidden = true
      status.textContent = ""
      status.className = "quiz-status"
      explanation.hidden = true
      reset.hidden = true
    })

    return card
  }

  function enhance() {
    // We use a normal `text` code fence plus a leading QUIZ marker, so the
    // highlighter never sees an unknown language (which can fail the build).
    const codes = document.querySelectorAll(
      'code.language-text, code[data-language="text"]',
    )
    codes.forEach(function (code) {
      if (code.dataset.quizProcessed === "1") return
      const raw = code.textContent || ""
      if (!/^\s*QUIZ\b/.test(raw)) return
      const body = raw.replace(/^\s*QUIZ[^\n]*\n?/, "")
      const card = buildQuiz(body)
      if (!card) return

      code.dataset.quizProcessed = "1"
      // Quartz may wrap code blocks in a <figure> (with a copy button).
      const block = code.closest("figure") || code.closest("pre") || code
      block.replaceWith(card)
    })
  }

  let scheduled = false
  function schedule() {
    if (scheduled) return
    scheduled = true
    if (typeof requestAnimationFrame === "function") {
      requestAnimationFrame(function () {
        scheduled = false
        enhance()
      })
    } else {
      setTimeout(function () {
        scheduled = false
        enhance()
      }, 0)
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", schedule)
  } else {
    schedule()
  }

  // Quartz's SPA router swaps the article without a full page load.
  const observer = new MutationObserver(schedule)
  observer.observe(document.body, { childList: true, subtree: true })
})()
