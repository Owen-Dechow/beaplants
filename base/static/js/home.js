// @ts-check

/**
 * @param {string[]} keywords
 * @param {string} data
 */
function overlap(keywords, data) {
    let found = false;

    keywords.forEach(item => {
        if (data.indexOf(item) > -1) {
            found = true;
        }
    });

    return found;
}

/**
 * @param {string} q
 */
function $ipt(q) {
    let elem = /** @type {HTMLInputElement} */(document.querySelector(q));

    if (elem)
        return elem;
    else
        throw Error(`"${q}" is not a valid query.`);
}

/**
 * @param {string} q
 */
function $(q) {
    let elem = /** @type {NodeListOf<HTMLElement>} */(document.querySelectorAll(q));

    if (elem)
        return elem;
    else
        throw Error(`"${q}" is not a valid query.`);
}

function applySorting() {
    let sortOrder = $ipt("#sort").value;
    let sizeFilter = $ipt("#filter-size").value;
    let search = $ipt("#search").value.toLowerCase().split(" ");
    let products = $(".grid-item");
    let productGrid = $(".product-grid")[0];

    // Filtering & Search
    for (let idx = 0; idx < products.length; idx++) {
        let item = products[idx];

        item.style.removeProperty("display");

        if (sizeFilter !== "none") {
            if (item.getAttribute("size") != sizeFilter)
                item.style.display = "none";
        }

        if (search.length > 0) {
            if (!overlap(search, (item.getAttribute("searchdata") || "").toLowerCase()))
                item.style.display = "none";
        }
    }

    // Sorting
    {
        let func;
        if (sortOrder === "random") {
            func = (_a, _b) => 0.5 - Math.random();
        } else if (sortOrder === "price-low-to-high") {
            func = (a, b) => parseFloat(a.getAttribute("price")) - parseFloat(b.getAttribute("price"));
        } else if (sortOrder === "price-high-to-low") {
            func = (a, b) => parseFloat(b.getAttribute("price")) - parseFloat(a.getAttribute("price"));
        } else {
            throw Error("NO VALID SORT METHOD");
        }
        let productList = Array.from(products);
        productList.sort(func);
        productGrid.innerHTML = "";
        productList.forEach(item => productGrid.append(item));
    }
}


function clearSorting() {
    $ipt("#sort").value = "random";
    $ipt("#filter-size").value = "none";
    $ipt("#search").value = "";

    applySorting();
}
