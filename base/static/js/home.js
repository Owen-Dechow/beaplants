function overlap(keywords, data) {
    let found = false;

    keywords.forEach(item => {
        if (data.indexOf(item) > -1) {
            found = true;
        }
    });

    return found;
}

function applySorting(event, sendData = true) {
    let sortOrder = document.getElementById("sort").value;
    let sizeFilter = document.getElementById("filter-size").value;
    let search = document.getElementById("search").value.toLowerCase().split(" ");
    let products = document.getElementsByClassName("grid-item");
    let productGrid = document.getElementsByClassName("product-grid")[0];
    let csrf = document.querySelector("input[name=csrfmiddlewaretoken]");

    // Filtering & Search
    for (let idx = 0; idx < products.length; idx++) {
        let item = products[idx];

        item.style.removeProperty("display");

        if (sizeFilter !== "none") {
            if (item.getAttribute("size") != sizeFilter)
                item.style.display = "none";
        }

        if (search.length > 0) {
            if (!overlap(search, item.getAttribute("searchdata").toLowerCase()))
                item.style.display = "none";
        }
    }

    // Sorting
    {
        let func;
        if (sortOrder === "random") {
            func = (a, b) => 0.5 - Math.random();
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

    // Send data
    if (sendData)
        fetch(`/filter/${encodeURIComponent(getuid())}/${encodeURIComponent(sizeFilter)}/${encodeURIComponent(sortOrder)}/s${encodeURIComponent(search)}`);
}


function clearSorting(event) {
    document.getElementById("sort").value = "random";
    document.getElementById("filter-size").value = "none";
    document.getElementById("search").value = "";

    applySorting(event, false);
}
