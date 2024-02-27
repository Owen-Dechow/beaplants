productId = undefined;

function sendProductViewReport() {
    fetch(`/product-view/${encodeURIComponent(getuid())}/${encodeURIComponent(productId)}`);
}

function toggleDonation(event) {
    let dontationSet = event.target.closest(".donation-set");
    let input = dontationSet.querySelector("input[name=donation]");

    input.value = "";
    if (event.target.checked) {
        dontationSet.classList.remove("off");
        dontationSet.classList.add("on");
        input.removeAttribute("disabled");
    } else {
        input.setAttribute("disabled", "true");
        dontationSet.classList.remove("on");
        dontationSet.classList.add("off");
    }
}

function clearParent(event) {
    event.target.parentNode.remove();
}