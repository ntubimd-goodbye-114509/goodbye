document.addEventListener("DOMContentLoaded", function () {
    const products = [

    ];

    const productList = document.getElementById("product-list");
    const searchInput = document.getElementById("search");
    const typeFilter = document.getElementById("type-filter");
    const statusFilter = document.getElementById("status-filter");

    function renderProducts(filteredProducts) {
        productList.innerHTML = ""; // 清空現有商品
        filteredProducts.forEach(product => {
            const productDiv = document.createElement("div");
            productDiv.classList.add("product");

            if (product.type === "receive") {
                productDiv.classList.add("receive");
            } else if (product.type === "sell") {
                productDiv.classList.add("sell");
            }

            const tagsHtml = product.tags.map(tag => 
                `<span class="tag" data-tag="${tag}">${tag}</span>`
            ).join(" ");

            productDiv.innerHTML = `
                <img src="${product.image}" alt="${product.name}" width="150" onerror="this.onerror=null; this.src='image/default.jpg';">
                <h3>${product.name}</h3>
                <p class="price">${product.price}</p>
                <div class="tags">${tagsHtml}</div>
                ${product.sale ? '<div class="sale-tag">促銷</div>' : ""}
                ${product.soldOut ? '<div class="sold-out">已售完</div>' : ""}
            `;
            productList.appendChild(productDiv);
        });

        // 點擊標籤篩選
        document.querySelectorAll(".tag").forEach(tagElement => {
            tagElement.addEventListener("click", function () {
                const selectedTag = this.dataset.tag;
                searchByTag(selectedTag);
            });
        });
    }

    // 側邊欄開關按鈕
    document.getElementById("menu-toggle").addEventListener("click", function() {
        const sidebar = document.getElementById("sidebar");
        if (sidebar.style.width === "250px") {
            sidebar.style.width = "0";
        } else {
            sidebar.style.width = "250px";
        }
    });

    // 側邊欄 ✕ 關閉按鈕
    document.getElementById("close-sidebar").addEventListener("click", function (e) {
        e.preventDefault();
        document.getElementById("sidebar").style.width = "0";
    });

    function filterProducts(keyword = "") {
        const type = typeFilter.value;
        const status = statusFilter.value;

        const filteredProducts = products.filter(product => {
            const matchesSearch = product.name.toLowerCase().includes(keyword) || 
                                  product.tags.some(tag => tag.toLowerCase().includes(keyword));
            const matchesType = type === "all" || product.type === type;
            const matchesStatus = status === "all" || 
                                  (status === "on-sale" && !product.soldOut) || 
                                  (status === "sold-out" && product.soldOut);
            
            return matchesSearch && matchesType && matchesStatus;
        });

        renderProducts(filteredProducts);
    }

    function searchByTag(tag) {
        searchInput.value = tag;
        filterProducts(tag.toLowerCase());
    }

    searchInput.addEventListener("input", () => filterProducts(searchInput.value.toLowerCase()));
    typeFilter.addEventListener("change", () => filterProducts(searchInput.value.toLowerCase()));
    statusFilter.addEventListener("change", () => filterProducts(searchInput.value.toLowerCase()));

    renderProducts(products);
});
