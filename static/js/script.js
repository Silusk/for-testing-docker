function openLogin() {
    document.getElementById("loginPopup").style.display = "block";
}
function closeLogin() {
    document.getElementById("loginPopup").style.display = "none";
}
// Close popup when clicking outside it
window.onclick = function(event) {
    let popup = document.getElementById("loginPopup");
    if (event.target == popup) {
        popup.style.display = "none";
    }
}