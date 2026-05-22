document.addEventListener('DOMContentLoaded', () => {
  const fab        = document.getElementById('donate-fab');
  const modal      = document.getElementById('donate-modal');
  const overlay    = document.getElementById('donate-overlay');
  const closeBtn   = document.getElementById('donate-close');
  const copyBtn    = document.getElementById('donate-copy-btn');
  const accountSpan = document.getElementById('donate-account');
  const qrImg      = document.getElementById('donate-qr-img');
  const zoomOverlay = document.getElementById('donate-zoom-overlay');

  if (!fab || !overlay || !modal) return;

  // ── Open / Close ──
  const openModal = () => {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // prevent page scroll
  };

  const closeModal = () => {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  };

  fab.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);

  // Close when clicking the dark backdrop (not the modal card itself)
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal();
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal();
      if (zoomOverlay) zoomOverlay.classList.remove('active');
    }
  });

  // ── Copy account number ──
  if (copyBtn && accountSpan) {
    copyBtn.addEventListener('click', () => {
      const accountNo = accountSpan.innerText.replace(/\s+/g, '');
      navigator.clipboard.writeText(accountNo).then(() => {
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Đã copy
        `;
        copyBtn.style.background = '#10B981';
        copyBtn.style.borderColor = '#10B981';
        copyBtn.style.color = '#fff';

        setTimeout(() => {
          copyBtn.innerHTML = originalHTML;
          copyBtn.style.background = '';
          copyBtn.style.borderColor = '';
          copyBtn.style.color = '';
        }, 2000);
      }).catch(err => {
        console.error('Copy failed:', err);
      });
    });
  }

  // ── Zoom QR Code ──
  if (qrImg && zoomOverlay) {
    qrImg.addEventListener('click', () => {
      zoomOverlay.classList.add('active');
    });

    zoomOverlay.addEventListener('click', () => {
      zoomOverlay.classList.remove('active');
    });
  }
});
