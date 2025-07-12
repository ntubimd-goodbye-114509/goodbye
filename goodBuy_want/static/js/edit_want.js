window.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector('.header');
  const content = document.querySelector('.main-content');
  if (header && content) {
    content.style.marginTop = header.offsetHeight + 'px';
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById('id_images');
  const mainPreview = document.getElementById('main-image-preview');
  const previewArea = document.getElementById('image-preview');
  const uploadBox = document.querySelector('.image-upload-box');
  const coverIndexInput = document.querySelector('input[name="cover_index"]');
  const imageOrderInput = document.querySelector('input[name="image_order"]');

  // 點擊大框或小預覽都可開啟檔案選擇
  if (uploadBox && imageInput) {
    uploadBox.addEventListener('click', () => imageInput.click());
  }


  // 更新主圖與小圖預覽
  function updateImagePreviews(selectedCoverIdx = 0) {
    const files = Array.from(imageInput.files);
    previewArea.innerHTML = '';
    mainPreview.innerHTML = '';

    if (files.length === 0) {
      mainPreview.innerHTML = '<span style="color:#ff69b4;font-size:1.2rem;">＋ 新增圖片</span>';
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
      mainPreview.innerHTML = `<img src="${e.target.result}" style="max-height:140px;max-width:100%;object-fit:contain;border-radius:10px;">`;
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
        // 點小圖可切換主圖
        wrapper.querySelector('input[type="radio"]').addEventListener('change', function(e) {
          e.stopPropagation();
          updateImagePreviews(idx);
        });
        previewArea.appendChild(wrapper);
      };
      reader.readAsDataURL(file);
    });

    // 更新隱藏欄位
    if (coverIndexInput) coverIndexInput.value = coverIdx;
    if (imageOrderInput) imageOrderInput.value = files.map((_, i) => i).join(',');
  }

  if (imageInput && previewArea && mainPreview) {
    imageInput.addEventListener('change', () => updateImagePreviews(0));
  }

  //選擇封面
  document.querySelectorAll('.click-cover').forEach(img => {
    img.addEventListener('click', function () {
      // 移除所有圖片的選擇框
      document.querySelectorAll('.click-cover').forEach(i => i.classList.remove('selected-cover'));
      // 加上選中圖的選擇框
      this.classList.add('selected-cover');
      // 更新 cover_index
      const position = this.dataset.position;
      if (coverIndexInput && position !== undefined) {
        coverIndexInput.value = position;
      }
    });
  });
});


