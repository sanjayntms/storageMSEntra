let index = 0;

function openLightbox(i) {
    index = i;
    document.getElementById("lightboxOverlay").style.display = "flex";
    display();
}

function closeLightbox() {
    document.getElementById("lightboxOverlay").style.display = "none";
    document.getElementById("lightboxVideo").pause();
    document.getElementById("lightboxAudio").pause();
}

function changeItem(step) {
    index = (index + step + mediaFiles.length) % mediaFiles.length;
    display();
}

function display() {
    const item = mediaFiles[index];

    const img = document.getElementById("lightboxImage");
    const vid = document.getElementById("lightboxVideo");
    const aud = document.getElementById("lightboxAudio");
    const pdf = document.getElementById("lightboxPDF");

    img.style.display = "none";
    vid.style.display = "none";
    aud.style.display = "none";
    pdf.style.display = "none";

    if (item.type === "image") {
        img.src = item.url;
        img.style.display = "block";
    } else if (item.type === "video") {
        vid.src = item.url;
        vid.style.display = "block";
        vid.play();
    } else if (item.type === "audio") {
        aud.src = item.url;
        aud.style.display = "block";
        aud.play();
    } else if (item.type === "pdf") {
        pdf.src = item.url;
        pdf.style.display = "block";
    }
}

/* Delete file */
function deleteFile(blobName) {
    if (!confirm("Delete this file permanently?")) return;

    fetch(`/delete/${blobName}`, { method: "POST" })
        .then(res => {
            if (res.status === 204) {
                location.reload();
            } else {
                alert("Delete failed");
            }
        })
        .catch(() => alert("Delete failed"));
}

/* Share file (copy SAS link) */
function shareFile(blobName) {
    fetch(`/share/${blobName}`)
        .then(r => r.text())
        .then(url => {
            if (!url.startsWith("http")) {
                alert("Share failed");
                return;
            }
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url)
                    .then(() => alert("Shareable link copied to clipboard!"))
                    .catch(() => alert(url));
            } else {
                // fallback
                window.prompt("Copy this link:", url);
            }
        })
        .catch(() => alert("Share failed"));
}
