// Lightbox: 点击图片放大，支持 SPA 导航
(function () {
  let overlay = null
  let currentImg = null

  function createOverlay() {
    if (overlay) return
    overlay = document.createElement("div")
    overlay.className = "lightbox-overlay"
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) close()
    })
    document.body.appendChild(overlay)
  }

  function open(img) {
    createOverlay()
    currentImg = img
    const clone = document.createElement("img")
    clone.src = img.src
    clone.alt = img.alt || ""
    clone.addEventListener("click", function (e) {
      e.stopPropagation()
      clone.classList.toggle("zoomed")
    })
    overlay.innerHTML = ""
    overlay.appendChild(clone)
    overlay.classList.add("active")
    document.body.style.overflow = "hidden"
  }

  function close() {
    if (!overlay) return
    overlay.classList.remove("active")
    overlay.innerHTML = ""
    currentImg = null
    document.body.style.overflow = ""
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close()
  })

  function bindImages(root) {
    const selector = "article img:not(.lightbox-bound)"
    const imgs = (root || document).querySelectorAll(selector)
    imgs.forEach(function (img) {
      img.classList.add("lightbox-bound")
      img.style.cursor = "zoom-in"
      img.addEventListener("click", function (e) {
        e.preventDefault()
        open(img)
      })
    })
  }

  // 初始绑定
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { bindImages() })
  } else {
    bindImages()
  }

  // SPA 导航后重新绑定（Quartz SPA 路由会触发 DOM 变化）
  const observer = new MutationObserver(function () { bindImages() })
  observer.observe(document.body, { childList: true, subtree: true })
})()
