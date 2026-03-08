/* progress.js
   Hides the progress box by default and only shows it when a download starts.
   Wraps the existing `acompanhar` function (if present) so the UI behavior changes
   without modifying the original inline code. Also auto-hides the progress box
   when the percent element reaches 100%.
*/
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    const progressBox = document.getElementById('progressBox');
    const percentEl = document.getElementById('percent');

    if (progressBox) {
      // hide initially
      progressBox.style.display = 'none';
    }

    // If the page defined acompanhar already, wrap it so we show progressBox
    // before starting the original behavior. This script should be included
    // after the page's inline script so the original function exists.
    if (typeof window.acompanhar === 'function') {
      const originalAcompanhar = window.acompanhar;
      window.acompanhar = function(){
        if (progressBox) progressBox.style.display = 'block';
        try { originalAcompanhar(); } catch (e) { console.error(e); }
      };
    } else {
      // Provide a fallback implementation used if the original isn't present
      window.acompanhar = function(){ if (progressBox) progressBox.style.display = 'block'; };
    }

    // Auto-hide when percent reaches 100%
    if (percentEl && progressBox) {
      const observer = new MutationObserver(() => {
        const text = percentEl.innerText || '';
        const value = parseInt(text.replace('%','').trim()) || 0;
        if (value >= 100) {
          progressBox.style.display = 'none';
        }
      });
      observer.observe(percentEl, { childList: true, characterData: true, subtree: true });
    }
  });
})();
