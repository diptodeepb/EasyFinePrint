(function() {
  try {
    var saved = localStorage.getItem('theme');
    var isDark = true;
    if (saved === 'light') {
      isDark = false;
    } else if (saved === 'dark') {
      isDark = true;
    } else {
      isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    if (isDark) {
      document.documentElement.classList.add('dark');
      var metaDark = document.querySelector('meta[name="theme-color"]');
      if (metaDark) metaDark.setAttribute('content', '#050507');
    } else {
      document.documentElement.classList.remove('dark');
      var metaLight = document.querySelector('meta[name="theme-color"]');
      if (metaLight) metaLight.setAttribute('content', '#f4ecde');
    }
  } catch {
    // Ignore storage access errors in restrictive environments
  }
})();
