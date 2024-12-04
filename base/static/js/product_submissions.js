var Q = document.querySelector.bind(document);

function addMember(values = null) {
    let groupMembers = Q("#group-members");
    let cardTemplate = Q("#member-template");
    let card = cardTemplate.content.cloneNode(true);
    let cards = groupMembers.querySelector(".cards");
    let randomId = Math.random();

    if (values != null) {
        card.querySelectorAll("*").forEach(e => {
            if (e.id.includes("first")) {
                e.value = values[0]
            } else if (e.id.includes("last")) {
                e.value = values[1]
            }
        })
    }

    card.querySelectorAll("*").forEach(e => {
        ["id", "for", "name"].forEach(a => {
            let original = e.getAttribute(a);
            if (original)
                e.setAttribute(a, e.getAttribute(a).replace("%", randomId))
        })
    })

    cards.insertBefore(card, cards.querySelector(".cards>button"));

    justifyCards();
}

function addVariation() {
    let cardTemplate = Q("#variation-template");
    let card = cardTemplate.content.cloneNode(true);
    let variations = Q("#variations");
    let cards = variations.querySelector(".cards");
    let randomId = Math.random();

    card.querySelectorAll("*").forEach(e => {
        ["id", "for", "name"].forEach(a => {
            let original = e.getAttribute(a);
            if (original)
                e.setAttribute(a, e.getAttribute(a).replace("%", randomId))
        })
    })

    cards.insertBefore(card, cards.querySelector(".cards>button"));
}

function removeMember(event) {
    let groupMembers = Q("#group-members");

    if (groupMembers.getElementsByClassName("card").length < 2)
        alert("Must have at least one group member.");
    else
        event.target.closest(".card").remove();

    justifyCards();
}

function removeVariant(event) {
    let variants = Q("#variations")
    if (variants.getElementsByClassName("card").length < 2)
        alert("Must have at least one product variant.");
    else
        event.target.closest(".card").remove()
}

function justifyCards() {
    let groupMembers = Q("#group-members");
    let cards = groupMembers.getElementsByClassName("card");
    let input = groupMembers.querySelector("input[name=group_members]");

    let json = "{";
    for (let i = 0; i < cards.length; i++) {
        let card = cards[i];
        json += `"${card.querySelector(".first").value}":"${card.querySelector(".last").value
            }" `;
        if (i + 1 != cards.length) json += ",";
        else json += "}";
    }

    input.value = json;
}

function updateCardsToJSON() {
    let groupMembers = Q("#group-members");
    let jsonInput = groupMembers.querySelector("input[name=group_members]");
    let json = JSON.parse(jsonInput.value);

    for (let key in json) {
        let val = json[key];
        addMember((values = [key, val]));
    }
}
