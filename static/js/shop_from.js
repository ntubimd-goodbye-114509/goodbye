// 封面 header 占位
window.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector('.header');
    const content = document.querySelector('.main-content');
    if (header && content) {
      content.style.marginTop = header.offsetHeight + 'px';
    }
  });
  
  // 標籤輸入與選取邏輯
  const tagInput = document.getElementById("tag-input");
  const tagHidden = document.querySelector("input[name='tag_names']");
  const tagList = document.getElementById("tag-list");
  let tagSet = new Set();
  
  if (tagInput) {
    tagInput.addEventListener("keydown", function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const val = this.value.trim();
        if (val && !tagSet.has(val)) {
          tagSet.add(val);
          addTagBadge(val);
          tagHidden.value = [...tagSet].join(",");
        }
        this.value = "";
      }
    });
  }
  
  // 點擊預設標籤按鈕時加入
  const predefinedTags = document.querySelectorAll(".tag-option");
  predefinedTags.forEach(btn => {
    btn.addEventListener("click", () => {
      const val = btn.textContent.trim();
      if (!tagSet.has(val)) {
        tagSet.add(val);
        addTagBadge(val);
        tagHidden.value = [...tagSet].join(",");
      }
    });
  });
  
  function addTagBadge(val) {
    const tag = document.createElement("span");
    tag.className = "badge bg-info text-dark me-1";
    tag.textContent = val;
    tagList.appendChild(tag);
  }
  
  // 新增商品
  function addProduct() {
    const area = document.getElementById("product-area");
    const index = area.children.length;
  
    const div = document.createElement("div");
    div.className = "card p-3 mb-3 position-relative";
  
    div.innerHTML = `
      <img src="/static/img/x.png" class="position-absolute end-0 top-0 m-2" role="button" style="width: 20px; height: 20px;" onclick="this.parentElement.remove()">
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
      <div class="mb-2">
          <label class="form-label">商品圖片</label>
          <input type="file" name="product_img[]" class="form-control">
      </div>
    `;
  
    area.appendChild(div);
  }
  
  // 狀態邏輯：現貨才顯示開始時間
  const shopStateField = document.querySelector('[name="shop_state"]');
  const startTimeGroup = document.getElementById("start-time-group");
  if (shopStateField && startTimeGroup) {
    const toggleStartTime = () => {
      const val = shopStateField.value;
      if (val.includes("現貨")) {
        startTimeGroup.style.display = "block";
      } else {
        startTimeGroup.style.display = "none";
      }
    };
    shopStateField.addEventListener("change", toggleStartTime);
    toggleStartTime(); // 預設執行一次
  }
  