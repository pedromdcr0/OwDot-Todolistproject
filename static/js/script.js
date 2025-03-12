const modal_newtask = document.getElementById("modal_newtask");
const openModal_newtask = document.getElementById("openModal_newtask");
const closeModal = document.getElementById("close");
const openCalendar = document.getElementById('duetime');

openModal_newtask.addEventListener("click", () => {
    modal_newtask.style.display = "flex";
});

closeModal.addEventListener("click", () => {
    modal_newtask.style.display = "none";
});

window.addEventListener("click", (event) => {
    if (event.target === modal) {
        modal_newtask.style.display = "none";
    }
});

openCalendar.addEventListener('focus', function() {
    this.showPicker();
});
