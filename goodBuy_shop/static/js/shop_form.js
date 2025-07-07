// 根據 header 高度調整內容區距
window.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector('.header');
  const content = document.querySelector('.main-content');
  if (header && content) {
    content.style.marginTop = header.offsetHeight + 'px';
  }
});

// 標籤輸入與點擊選取邏輯
const tagInput = document.getElementById("tag-input");
const tagHidden = document.querySelector("input[name='tag_names']");
const tagList = document.getElementById("tag-list");
let tagSet = new Set();

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


// 動態新增商品欄位
let productIndex = document.querySelectorAll('#product-area .card').length || 0;

function addProduct() {
  const area = document.getElementById("product-area");
  if (!area) return;

  const div = document.createElement("div");
  div.className = "card p-3 mb-3 position-relative";
  div.innerHTML = `
    <img src="/static/img/x.png" class="position-absolute end-0 top-0 m-2" role="button" onclick="this.parentElement.remove()" style="width:20px;height:20px;">
    <div class="mb-2">
      <label class="form-label">商品名稱</label>
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
      <label class="form-label">商品圖片（可更換）</label>
      <div class="image-preview mb-2"></div>
      <input type="file" name="product_image_${productIndex}" class="form-control product-img-input" accept="image/*">
    </div>
  `;
  area.appendChild(div);

  const fileInput = div.querySelector('.product-img-input');
  const previewDiv = div.querySelector('.image-preview');
  fileInput.addEventListener('change', function () {
    previewDiv.innerHTML = '';
    if (this.files && this.files[0]) {
      const url = URL.createObjectURL(this.files[0]);
      previewDiv.innerHTML = `<img src="${url}" style="width:100px;height:100px;object-fit:cover;">`;
    }
  });

  productIndex += 1;
}



// 切換「開始時間」顯示（僅限現貨）
const shopStateField = document.querySelector('[name="shop_state"]');
const startTimeGroup = document.getElementById("start-time-group");
if (shopStateField && startTimeGroup) {
  const toggleStartTime = () => {
    startTimeGroup.style.display = shopStateField.value.includes("現貨") ? "block" : "none";
  };
  shopStateField.addEventListener("change", toggleStartTime);
  toggleStartTime();
}

// 圖片預覽與封面選取
const uploadBox = document.getElementById('image-upload-box');
const uploadInput = document.getElementById('image-upload-box-input');
const mainImagePreview = document.getElementById('main-image-preview');
const imagePreviewArea = document.getElementById('image-preview-area');
const coverIndexInput = document.querySelector('input[name="cover_index"]');
const imageOrderInput = document.querySelector('input[name="image_order"]');

if (uploadBox && uploadInput) {
  uploadBox.addEventListener('click', function (e) {
    // 避免點擊小圖時也觸發
    if (
      e.target === uploadBox ||
      e.target.classList.contains('main-image-placeholder') ||
      e.target.id === 'main-image-preview' ||
      mainImagePreview.contains(e.target)
    ) {
      uploadInput.click();
    }
  });
}

function updateImagePreviews(selectedCoverIdx = 0) {
  const files = Array.from(uploadInput.files);
  imagePreviewArea.innerHTML = '';
  mainImagePreview.innerHTML = '';

  if (files.length === 0) {
    mainImagePreview.innerHTML = '<span class="main-image-placeholder text-secondary">＋ 新增圖片</span>';
    if (coverIndexInput) coverIndexInput.value = '';
    if (imageOrderInput) imageOrderInput.value = '';
    return;
  }

  // 主圖（封面）
  let coverIdx = Number(selectedCoverIdx);
  if (isNaN(coverIdx) || coverIdx < 0 || coverIdx >= files.length) coverIdx = 0;
  const coverFile = files[coverIdx];
  const coverReader = new FileReader();
  coverReader.onload = function(e) {
    mainImagePreview.innerHTML = `<img src="${e.target.result}" style="max-height:220px;max-width:100%;object-fit:contain;border-radius:10px;">`;
  };
  coverReader.readAsDataURL(coverFile);

  // 小圖預覽
  files.forEach((file, idx) => {
    const reader = new FileReader();
    reader.onload = function(e) {
      const wrapper = document.createElement('div');
      wrapper.className = 'position-relative preview-item me-2 mb-2';
      wrapper.style.cursor = 'pointer';
      wrapper.innerHTML = `
        <img src="${e.target.result}" class="img-thumbnail" style="width:80px;height:80px;object-fit:cover;">
        <div class="position-absolute top-0 end-0">
          <input type="radio" name="cover_choice" value="${idx}" class="btn-check" id="cover_${idx}" ${idx === coverIdx ? 'checked' : ''}>
          <label class="btn btn-sm btn-outline-primary" for="cover_${idx}">封面</label>
        </div>
      `;
      // 點小圖或 radio 都可切換主圖
      wrapper.querySelector('img').addEventListener('click', function() {
        updateImagePreviews(idx);
      });
      wrapper.querySelector('input[type="radio"]').addEventListener('change', function(e) {
        e.stopPropagation();
        updateImagePreviews(idx);
      });
      imagePreviewArea.appendChild(wrapper);
    };
    reader.readAsDataURL(file);
  });

  // 更新隱藏欄位
  if (coverIndexInput) coverIndexInput.value = coverIdx;
  if (imageOrderInput) imageOrderInput.value = files.map((_, i) => i).join(',');
}

if (uploadInput && imagePreviewArea && mainImagePreview) {
  uploadInput.addEventListener('change', () => updateImagePreviews(0));
}

