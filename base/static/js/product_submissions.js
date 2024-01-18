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