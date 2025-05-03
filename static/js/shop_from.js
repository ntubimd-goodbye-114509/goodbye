const tagInput = document.getElementById("tag-input");
const tagHidden = document.querySelector("input[name='tag_names']");
const tagList = document.getElementById("tag-list");
let tagSet = new Set();


window.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector('.header');
    const content = document.querySelector('.main-content');
    if (header && content) {
      content.style.marginTop = header.offsetHeight + 'px';
    } 
});

tagInput.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        const val = this.value.trim();
        if (val && !tagSet.has(val)) {
            tagSet.add(val);
            const tag = document.createElement("span");
            tag.className = "badge bg-info text-dark me-1";
            tag.textContent = val;
            tagList.appendChild(tag);
            tagHidden.value = [...tagSet].join(",");
        }
        this.value = "";
    }
});

function addProduct() {
    const area = document.getElementById("product-area");
    const index = area.children.length;

    const div = document.createElement("div");
    div.className = "card p-3 mb-3";

    div.innerHTML = `
        <div class="mb-2">
            <label class="form-label">名稱</label>
            <input type="text" name="product_name[]" class="form-control" required>
        </div>
        <div class="mb-2">
            <label class="form-label">價格</label>
            <input type="number" name="product_price[]" class="form-control" required>
        </div>
        <div class="mb-2">
            <label class="form-label">數量</label>
            <input type="number" name="product_qty[]" class="form-control" required>
        </div>
    `;

    area.appendChild(div);
}
