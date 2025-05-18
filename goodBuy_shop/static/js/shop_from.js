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

function addProduct() {
  const area = document.getElementById("product-area");
  if (!area) return;

  const div = document.createElement("div");
  div.className = "card p-3 mb-3 position-relative";
  div.innerHTML = `
    <img src="/static/img/x.png" class="position-absolute end-0 top-0 m-2" role="button" style="width: 20px; height: 20px;" onclick="this.parentElement.remove()">
    <div class="row">
      <!-- 左側圖片方塊 -->
      <div class="col-4 d-flex flex-column align-items-center justify-content-center">
        <div class="image-preview mb-2"></div>
        <input type="file" name="product_image" class="form-control product-img-input mt-2" accept="image/*" style="display:none;">
      </div>
      <!-- 右側表單 -->
      <div class="col-8">
        <div class="mb-2">
          <label class="form-label">商品名稱</label>
          <input type="text" name="product_name[]" class="form-control" required>
        </div>
        <div class="row">
          <div class="col-6">
            <label class="form-label">價格</label>
            <input type="number" name="product_price[]" class="form-control" required>
          </div>
          <div class="col-6">
            <label class="form-label">數量</label>
            <input type="number" name="product_qty[]" class="form-control" required>
          </div>
        </div>
      </div>
    </div>
  `;
  area.appendChild(div);

  // 點擊圖片方塊可開啟檔案選擇
  const fileInput = div.querySelector('.product-img-input');
  const previewDiv = div.querySelector('.image-preview');
  previewDiv.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', function () {
    previewDiv.innerHTML = '';
    if (this.files && this.files[0]) {
      const url = URL.createObjectURL(this.files[0]);
      previewDiv.innerHTML = `<img src="${url}" style="width:100%;height:100%;object-fit:cover;">`;
    }
  });
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

// 點擊方塊觸發 input
const imageUploadBox = document.getElementById('image-upload-box');
const imageUploadInput = document.getElementById('image-upload-box-input');
const imageUploadPlaceholder = document.getElementById('image-upload-placeholder');

if (imageUploadBox && imageUploadInput && imageUploadPlaceholder) {
  imageUploadBox.addEventListener('click', () => {
    imageUploadInput.click();
  });

  imageUploadInput.addEventListener('change', function () {
    imageUploadBox.innerHTML = '';
    if (!this.files || this.files.length === 0) {
      imageUploadBox.appendChild(imageUploadPlaceholder);
      imageUploadPlaceholder.style.display = "block";
      return;
    }
    // 只顯示第一張
    const file = this.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = e => {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.style.width = "100%";
        img.style.height = "100%";
        img.style.objectFit = "cover";
        img.style.borderRadius = "12px";
        imageUploadBox.appendChild(img);
      };
      reader.readAsDataURL(file);
    }
  });
}

