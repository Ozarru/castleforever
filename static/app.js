/* Shared progressive-enhancement helpers. Loaded with `defer` from both the
   public and dashboard layouts so it is cached once across the whole site. */
(function () {
  "use strict";

  function reveal(wrapper) {
    wrapper.classList.add("is-loaded");
  }

  function observe(wrapper) {
    var image = wrapper.tagName === "IMG" ? wrapper : wrapper.querySelector("img");
    if (!image) {
      reveal(wrapper);
      return;
    }
    if (image.complete) {
      reveal(wrapper);
      return;
    }
    image.addEventListener("load", function () { reveal(wrapper); }, { once: true });
    image.addEventListener("error", function () { reveal(wrapper); }, { once: true });
  }

  function initImageSkeletons(root) {
    var scope = root || document;
    var wrappers = scope.classList && scope.classList.contains("image-skeleton")
      ? [scope]
      : scope.querySelectorAll(".image-skeleton");
    Array.prototype.forEach.call(wrappers, function (wrapper) {
      if (wrapper.dataset.imageSkeletonReady) return;
      wrapper.dataset.imageSkeletonReady = "1";
      observe(wrapper);
    });
  }

  // Public API so AJAX-swapped fragments (dashboard list results) can wire up
  // newly inserted images without a MutationObserver on the whole document.
  window.cfInitImageSkeletons = initImageSkeletons;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { initImageSkeletons(document); });
  } else {
    initImageSkeletons(document);
  }
})();
