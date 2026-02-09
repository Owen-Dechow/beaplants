productId = undefined;

function toggleDonation(event) {
    let donationSet = event.target.closest(".donation-set");
    let input = donationSet.querySelector("input[name=donation]");

    input.value = "";
    if (event.target.checked) {
        donationSet.classList.remove("off");
        donationSet.classList.add("on");
        input.removeAttribute("disabled");
    } else {
        input.setAttribute("disabled", "true");
        donationSet.classList.remove("on");
        donationSet.classList.add("off");
    }
}

function clearParent(event) {
    event.target.parentNode.remove();
}

function selectVariation(event) {
    let vId = event.target.getAttribute("variation");
    let inStock = event.target.getAttribute("in-stock");

    let selectedBtn = document.querySelector(".variation-tab-btn.selected");
    if (selectedBtn) selectedBtn.classList.remove("selected");

    let selectedTab = document.querySelector(".variation.selected");
    if (selectedTab) selectedTab.classList.remove("selected");

    document.querySelector(`.variation[variation="${vId}"]`).classList.add("selected");
    document.querySelector(`.variation-tab-btn[variation="${vId}"]`).classList.add("selected");

    let form = document.querySelector("#order-form");
    if (form) {
        if (parseInt(inStock) > 0) {
            form.style.display = "";
            form.querySelector("[name=product]").value = vId;
        } else {
            form.style.display = "none";
        }
    }
}
