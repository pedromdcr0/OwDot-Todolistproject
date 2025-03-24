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
            console.log(data.message);
        })
        .catch(error => {
            console.error("Erro ao atualizar status:", error);
        });
}


function editStatus(spanElement) {
    let taskId = spanElement.getAttribute("data-task-id");
    let currentStatus = spanElement.innerText.trim();

    let buttonContainer = document.createElement("div");
    buttonContainer.classList.add("status_buttons");

    const statuses = [
        { value: "0", text: "Open", className: "div_clicavel_card" },
        { value: "1", text: "On going", className: "div_clicavel_card" },
        { value: "2", text: "Finished", className: "div_clicavel_card_completed" }
    ];

    statuses.forEach(status => {
        let button = document.createElement("button");
        button.innerText = status.text;
        button.classList.add("status_button");
        if (status.text === currentStatus) {
            button.classList.add("status_button_active");
        }

        button.onclick = function () {
            updateStatus(taskId, status.value, status.text, status.className);
        };

        buttonContainer.appendChild(button);
    });

    spanElement.replaceWith(buttonContainer);

    function handleClickOutside(event) {
        if (!buttonContainer.contains(event.target)) {
            revertToSpan(currentStatus);
        }
    }

    function revertToSpan(text) {
        let newSpan = document.createElement("span");
        newSpan.className = "status_display";
        newSpan.setAttribute("data-task-id", taskId);
        newSpan.innerText = text;
        newSpan.onclick = function () { editStatus(newSpan); };

        buttonContainer.replaceWith(newSpan);
        document.removeEventListener("mousedown", handleClickOutside);
    }

    function updateStatus(taskId, newValue, newText, newClass) {
        fetch("/update_status", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                task_id: taskId,
                status: newValue
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            revertToSpan(newText);

            let taskDiv = document.querySelector(`[data-task-id='${taskId}']`)?.closest(".div_clicavel_card, .div_clicavel_card, .div_clicavel_card_completed");
            if (taskDiv) {
                taskDiv.classList.remove("div_clicavel_card", "div_clicavel_card", "div_clicavel_card_completed");
                void taskDiv.offsetWidth;

                taskDiv.classList.add(newClass);
            }
        })
        .catch(error => {
            console.error("Erro ao atualizar status:", error);
        });
    }

    document.addEventListener("mousedown", handleClickOutside);
}
