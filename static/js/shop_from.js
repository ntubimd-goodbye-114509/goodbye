// 頁面載入後調整 header 區塊間距
window.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector('.header');
  const content = document.querySelector('.main-content');
  if (header && content) {
    content.style.marginTop = header.offsetHeight + 'px';
  }
});

// ------------------------------
// 標籤輸入與點擊選取邏輯
// ------------------------------
const tagInput = document.getElementById("tag-input");
const tagHidden = document.querySelector("input[name='tag_names']");
const tagList = document.getElementById("tag-list");
let tagSet = new Set();

if (tagInput && tagHidden && tagList) {
  tagInput.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
      e.preventDefault();
      const val = this.value.trim();
      if (val && !tagSet.has(val)) {
        tagSet.add(val);
        tagList.innerHTML += `<span class='badge bg-info text-dark me-1'>${val}</span>`;
        tagHidden.value = [...tagSet].join(",");
      }
      this.value = "";
    }
  });

  document.querySelectorAll(".tag-option").forEach(btn => {
    btn.addEventListener("click", () => {
      const val = btn.textContent.trim();
      if (!tagSet.has(val)) {
        tagSet.add(val);
        tagList.innerHTML += `<span class='badge bg-info text-dark me-1'>${val}</span>`;
        tagHidden.value = [...tagSet].join(",");
      }
    });
  });
}

// ------------------------------
// 新增商品區塊
// ------------------------------
function addProduct() {
  const area = document.getElementById("product-area");
  if (!area) return;

  const div = document.createElement("div");
  div.className = "card p-3 mb-3 position-relative";
  div.innerHTML = `
    <img src="/static/img/x.png" class="position-absolute end-0 top-0 m-2" role="button" style="width: 20px; height: 20px;" onclick="this.parentElement.remove()">
    <div class="mb-2"><label class="form-label">名稱</label><input type="text" name="product_name[]" class="form-control" required></div>
    <div class="mb-2"><label class="form-label">價格</label><input type="number" name="product_price[]" class="form-control" required></div>
    <div class="mb-2"><label class="form-label">數量</label><input type="number" name="product_qty[]" class="form-control" required></div>
    <div class="mb-2"><label class="form-label">商品圖片</label><input type="file" name="images" multiple"></div>
  `;
  area.appendChild(div);
}

// ------------------------------
// 現貨狀態才顯示開始時間欄位
// ------------------------------
const shopStateField = document.querySelector('[name="shop_state"]');
const startTimeGroup = document.getElementById("start-time-group");
if (shopStateField && startTimeGroup) {
  const toggleStartTime = () => {
    startTimeGroup.style.display = shopStateField.value.includes("現貨") ? "block" : "none";
  };
  shopStateField.addEventListener("change", toggleStartTime);
  toggleStartTime();
}

// ------------------------------
// 封面圖片上傳與預覽邏輯
// ------------------------------
const imageInput = document.querySelector('input[name="images"]');
const coverIndexInput = document.querySelector('input[name="cover_index"]');
const imageOrderInput = document.querySelector('input[name="image_order"]');

if (imageInput && coverIndexInput && imageOrderInput) {
  const imagePreviewArea = document.createElement('div');
  imagePreviewArea.className = 'image-preview-area d-flex flex-wrap gap-2 mt-2';
  imageInput.parentNode.insertBefore(imagePreviewArea, imageInput.nextSibling);

  imageInput.addEventListener('change', updateImagePreviews);

  function updateImagePreviews() {
    imagePreviewArea.innerHTML = '';
    Array.from(imageInput.files).forEach((file, idx) => {
      imagePreviewArea.innerHTML += `
        <div class='position-relative'>
          <img src='${URL.createObjectURL(file)}' class='img-thumbnail' style='width:100px;height:100px;object-fit:cover;'>
          <div class='position-absolute top-0 end-0'>
            <input type='radio' name='cover_choice' value='${idx}' class='btn-check' id='cover_${idx}' ${idx === 0 ? 'checked' : ''}>
            <label class='btn btn-sm btn-outline-primary' for='cover_${idx}'>封面</label>
          </div>
        </div>`;
    });
    updateCoverAndOrder();
  }

  function updateCoverAndOrder() {
    const coverRadio = document.querySelector('input[name="cover_choice"]:checked');
    const coverIndex = coverRadio ? coverRadio.value : '0';
    coverIndexInput.value = coverIndex;

    const fileCount = imageInput.files.length;
    imageOrderInput.value = Array.from({ length: fileCount }, (_, i) => i).join(',');
  }

  imagePreviewArea.addEventListener('change', (e) => {
    if (e.target.name === 'cover_choice') {
      updateCoverAndOrder();
    }
  });
}
