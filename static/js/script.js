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

openCalendar.addEventListener('focus', function () {
    this.showPicker();
});

function updateTaskStatus(selectElement) {
    let taskId = selectElement.getAttribute("data-task-id");
    let newStatus = selectElement.value;

    fetch("/update_status", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            task_id: taskId,
            status: newStatus
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.message); // Mensagem de sucesso
        })
        .catch(error => {
            console.error("Erro ao atualizar status:", error);
        });
}


function editStatus(spanElement) {
    let taskId = spanElement.getAttribute("data-task-id");
    let currentStatus = spanElement.innerText.trim();

    let select = document.createElement("select");
    select.classList.add("select_dropdown")
    select.innerHTML = `
        <option class="option_dropdown" value="0" ${currentStatus === "Open" ? "selected" : ""}>Open</option>
        <option class="option_dropdown" value="1" ${currentStatus === "Progress" ? "selected" : ""}>Progress</option>
        <option class="option_dropdown" value="2" ${currentStatus === "Finished" ? "selected" : ""}>Finished</option>
    `;

    spanElement.replaceWith(select);

    setTimeout(() => {
        select.focus();
        select.size = 3;
    }, 0);

    select.addEventListener("change", function () {
        let newStatus = select.value;

        fetch("/update_status", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                task_id: taskId,
                status: newStatus
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);

                let newSpan = document.createElement("span");
                newSpan.className = "status_display";
                newSpan.setAttribute("data-task-id", taskId);
                newSpan.innerText = select.options[select.selectedIndex].text;
                newSpan.onclick = function () { editStatus(newSpan); };

                select.replaceWith(newSpan);
            })
            .catch(error => {
                console.error("Erro ao atualizar status:", error);
            });
    });
}