function addMarkupCard(markupEditorId, values = null) {
    let cardTemplate = document.getElementById("markup-card-template");
    let card = cardTemplate.content.cloneNode(true);
    let markupEditor = document.getElementById(markupEditorId);
    let randomId = Math.random();

    if (values) {
        card.querySelector("#markup-days").value = values[0];
        card.querySelector("#markup-percent").value = values[1];
    }

    card.querySelector("label[for=markup-days]").setAttribute("for", `markup-days-${randomId}`);
    card.querySelector("input[id=markup-days]").setAttribute("id", `markup-days-${randomId}`);
    card.querySelector("label[for=markup-percent]").setAttribute("for", `markup-percent-${randomId}`);
    card.querySelector("input[id=markup-percent]").setAttribute("id", `markup-percent-${randomId}`);


    markupEditor.querySelector(".cards").insertBefore(card, markupEditor.querySelector(".cards>button"));

    justifyMarkupCards(markupEditor = markupEditor.id);
}

function removeMarkupCard(event) {
    let markupEditor = event.target.closest(".markup-editor");
    let cards = markupEditor.getElementsByClassName("card");

    if (cards.length >= 2) {
        event.target.closest(".card").remove();
        markupEditor.querySelector(".card").querySelector("input");
    } else {
        alert("Cannot remove base markup card!");
    }

    justifyMarkupCards(markupEditor = markupEditor.id);
}

function justifyMarkupCards(markupEditorId) {
    let markupEditor = document.getElementById(markupEditorId);

    let cards = markupEditor.getElementsByClassName("card");
    let firstDay = cards[0].querySelector("input");

    firstDay.setAttribute("min", "0");
    firstDay.setAttribute("max", "0");
    firstDay.value = 0;

    let lastDay = 0;
    for (let i = 1; i < cards.length; i++) {
        let card = cards[i];
        let input = card.querySelector("input");
        input.setAttribute("min", lastDay + 1);

        if (input.value)
            lastDay = parseFloat(input.value);
        else
            lastDay += 1;
    }

    let json = "{";
    for (let i = 0; i < cards.length; i++) {
        let card = cards[i];
        json += `"${card.querySelector(".markup-days").value}":${parseFloat(card.querySelector(".markup-percent").value) / 100}`;
        if (i + 1 != cards.length)
            json += ",";
        else
            json += "}";
    }

    markupEditor.querySelector("input[name=markup]").value = json;
}

function updateCardsToJSON(markupEditorId) {
    let markupEditor = document.getElementById(markupEditorId);
    let jsonInput = markupEditor.querySelector("input[name=markup]");
    let json = JSON.parse(jsonInput.value);

    for (let key in json) {
        let val = json[key];
        addMarkupCard(markupEditorId, values = [key, val * 100]);
    }
}

function deleteSeason(seasonId) {
    if (confirm("Are you absolutely certain you want to delete this season? This action CANNOT be undone!")) {
        window.location = `/delete-season/${seasonId}`;
    }
}

function markupCardValueChange(event) {
    justifyMarkupCards(event.target.closest(".markup-editor").id);
}

function confirmCloseOrder(event) {
    if (!confirm("Are you sure you want to close this order? Once it is closed it cannot be reopened!"))
        event.preventDefault()
}