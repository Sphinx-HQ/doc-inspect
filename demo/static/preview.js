(function () {
  var download = document.getElementById("download-json");
  var factsEl = document.getElementById("facts-json");
  if (download && factsEl) {
    download.addEventListener("click", function () {
      var blob = new Blob([factsEl.textContent || ""], { type: "application/json" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = download.getAttribute("data-filename") || "facts.json";
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  var root = document.getElementById("document-preview");
  if (!root) return;

  var kind = root.getAttribute("data-kind");
  var mediaType = root.getAttribute("data-media-type") || "";
  var bytesEl = document.getElementById("preview-bytes");
  var canvas = document.getElementById("preview-canvas");
  var image = document.getElementById("preview-image");
  var fallback = document.getElementById("preview-fallback");
  var b64 = bytesEl ? bytesEl.value : "";

  function showFallback() {
    if (fallback) fallback.hidden = false;
  }

  function b64ToUint8Array(value) {
    var binary = atob(value);
    var bytes = new Uint8Array(binary.length);
    for (var i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }

  if (!b64) {
    showFallback();
    return;
  }

  if (kind === "image") {
    if (image) {
      image.hidden = false;
      image.src = "data:" + mediaType + ";base64," + b64;
    }
    return;
  }

  if (kind !== "pdf") {
    showFallback();
    return;
  }

  var script = document.createElement("script");
  script.src = "https://unpkg.com/pdfjs-dist@4.8.69/build/pdf.min.js";
  script.onload = function () {
    if (!window.pdfjsLib) {
      showFallback();
      return;
    }
    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      "https://unpkg.com/pdfjs-dist@4.8.69/build/pdf.worker.min.js";
    var bytes = b64ToUint8Array(b64);
    window.pdfjsLib
      .getDocument({ data: bytes })
      .promise.then(function (pdf) {
        return pdf.getPage(1);
      })
      .then(function (page) {
        var viewport = page.getViewport({ scale: 1.1 });
        if (!canvas) return;
        canvas.hidden = false;
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        return page.render({ canvasContext: canvas.getContext("2d"), viewport: viewport }).promise;
      })
      .catch(function () {
        showFallback();
      });
  };
  script.onerror = showFallback;
  document.head.appendChild(script);
})();
