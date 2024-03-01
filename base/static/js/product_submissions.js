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
    event.preventDefault();

    const imageField = document.querySelector('#id_images')
    const imageFiles = imageField.files;
    const compressedFiles = new DataTransfer();
    const form = event.target; // Define the form here

    for (const imageFile of imageFiles) {
        const reader = new FileReader(); // Create a new FileReader for each file

        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                const elem = document.createElement('canvas');
                elem.width = img.width;
                elem.height = img.height;
                const ctx = elem.getContext('2d');
                // img, dx, dy, dWidth, dHeight
                ctx.drawImage(img, 0, 0, img.width, img.height);

                // Calculate the quality parameter based on the original file size
                const fileSizeInKB = imageFile.size / 1024;
                let quality = 256 / fileSizeInKB;
                if (quality > 1) {
                    quality = 1
                }

                ctx.canvas.toBlob((blob) => {
                    const file = new File([blob], imageFile.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    // Add the compressed file to the array
                    compressedFiles.items.add(file);

                    // If all files have been processed, submit the form
                    if (compressedFiles.files.length === imageFiles.length) {
                        const newImageField = document.createElement("input");
                        newImageField.setAttribute("type", "file");
                        newImageField.setAttribute("name", "images");
                        newImageField.files = compressedFiles.files;

                        const newFormField = document.createElement("form");
                        Array.from(form.elements).forEach(e => {
                            if (e.id != "id_images") {
                                if (e.name)
                                    newFormField.append(e);
                            } else {
                                newFormField.append(newImageField);
                            }
                        });

                        newFormField.action = form.action;
                        newFormField.method = form.method;
                        newFormField.enctype = form.enctype;
                        document.body.append(newFormField);
                        newFormField.submit();
                    }

                }, 'image/jpeg', quality); // Use the calculated quality parameter
            },
                img.src = event.target.result;
        }
        reader.readAsDataURL(imageFile);
    }
}