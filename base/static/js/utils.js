function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getuid() {
    let uid = getCookie("uid");

    if (uid)
        return uid;

    uid = `id${Math.floor(Math.random() * 10000)}u${Date.now()}`;
    setCookie("uid", uid, 50);
}

function moveCarousel(dist, carouselId) {
    let carousel = document.getElementById(carouselId);
    let items = carousel.getElementsByClassName("carousel-item");
    let currentIndex = clamp(0, parseInt(carousel.getAttribute("index")) + dist, items.length);

    carousel.setAttribute("index", currentIndex);

    for (let idx = 0; idx < items.length; idx++) {
        let rel = idx - currentIndex;
        let item = items[idx];

        item.classList.remove("center");
        item.classList.remove("left");
        item.classList.remove("left2");
        item.classList.remove("right");
        item.classList.remove("right2");
        item.classList.remove("hidden");

        item.onclick = (event) => {
            if (rel === 0)
                return;

            event.preventDefault();
            moveCarousel(rel);
        };

        if (rel === 0) item.classList.add("center");
        else if (rel === 1) item.classList.add("right");
        else if (rel === 2) item.classList.add("right2");
        else if (rel === -1) item.classList.add("left");
        else if (rel === -2) item.classList.add("left2");
        else item.classList.add("hidden");

    }
}

function clamp(min, num, max) {
    return Math.max(Math.min(num, max - 1), min);
}
