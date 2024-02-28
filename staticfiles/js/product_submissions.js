function addMember(values = null) {
    let groupMembers = document.querySelector("#group-members");
    let cardTemplate = document.getElementById("member-template");
    let card = cardTemplate.content.cloneNode(true);
    let cards = groupMembers.querySelector(".cards");
    let randomId = Math.random();

    if (values != null) {
        card.querySelector("#first").value = values[0];
        card.querySelector("#last").value = values[1];
    }

    card.querySelector("label[for=first]").setAttribute("for", `first-${randomId}`);
    card.querySelector("input[id=first]").setAttribute("id", `first-${randomId}`);
    card.querySelector("label[for=last]").setAttribute("for", `last-${randomId}`);
    card.querySelector("input[id=last]").setAttribute("id", `last-${randomId}`);

    cards.insertBefore(card, cards.querySelector(".cards>button"));

    justifyCards();
}

function removeMember(event) {
    let groupMembers = document.querySelector("#group-members");

    if (groupMembers.getElementsByClassName("card").length < 2)
        alert("Must have at least one group member.");
    else
        event.target.closest(".card").remove();

    justifyCards();
}

function justifyCards() {
    let groupMembers = document.querySelector("#group-members");
    let cards = groupMembers.getElementsByClassName("card");
    let input = groupMembers.querySelector("input[name=group_members]");

    let json = "{";
    for (let i = 0; i < cards.length; i++) {
        let card = cards[i];
        json += `"${card.querySelector(".first").value}":"${card.querySelector(".last").value}" `;
        if (i + 1 != cards.length)
            json += ",";
        else
            json += "}";
    }

    input.value = json;
}

function updateCardsToJSON() {
    let groupMembers = document.querySelector("#group-members");
    let jsonInput = groupMembers.querySelector("input[name=group_members]");
    let json = JSON.parse(jsonInput.value);

    for (let key in json) {
        let val = json[key];
        addMember(values = [key, val]);
    }
}

async function handleFormSubmit(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    const imageFiles = document.querySelector('#id_images').files;
    const compressedFiles = [];
    const form = event.target; // Define the form here

    for (const imageFile of imageFiles) {
        const reader = new FileReader(); // Create a new FileReader for each file

        reader.onload = function (event) {
            const img = new Image();
            img.onload = function () {
                const elem = document.createElement('canvas');
                const scaleFactor = 0.1; // Adjust this value to change the compression level
                elem.width = img.width * scaleFactor;
                elem.height = img.height * scaleFactor;
                const ctx = elem.getContext('2d');
                // img, dx, dy, dWidth, dHeight
                ctx.drawImage(img, 0, 0, img.width * scaleFactor, img.height * scaleFactor);

                // Calculate the quality parameter based on the original file size
                const fileSizeInKB = imageFile.size / 1024;
                let quality = 2400 / fileSizeInKB;
                if (quality > 1) {
                    quality = 1
                }

                ctx.canvas.toBlob(function (blob) {
                    const file = new File([blob], imageFile.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    // Add the compressed file to the array
                    compressedFiles.push(file);

                    // If all files have been processed, submit the form
                    if (compressedFiles.length === imageFiles.length) {
                        const formData = new FormData();
                        // Add all the initial form data
                        Array.from(form.elements).forEach(element => {
                            if (element.name) {
                                if (element.type === 'file' && element.id === 'id_images') {
                                    compressedFiles.forEach((file, index) => {
                                        formData.append('images', file); // Removed brackets
                                    });
                                } else if (element.type === 'file') {
                                    Array.from(element.files).forEach(file => {
                                        formData.append(element.name, file);
                                    });
                                } else {
                                    formData.append(element.name, element.value);
                                }
                            }
                        });
                        // Now submit the form with the compressed images
                        const request = new XMLHttpRequest();
                        request.open("POST", form.getAttribute('action')); // Use the form defined outside
                        request.send(formData);
                    }
                }, 'image/jpeg', quality); // Use the calculated quality parameter
            },
                img.src = event.target.result;
        }
        reader.readAsDataURL(imageFile);
    }
}