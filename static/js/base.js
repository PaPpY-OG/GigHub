  function toggleMenu() {
      const sidebar = document.querySelector('.sidebar');
      const menuIcon = document.querySelector('.menu-icon');

      sidebar.classList.toggle('active');
      menuIcon.classList.toggle('hidden');
  }

  document.addEventListener('click', function(e) {
      const sidebar = document.querySelector('.sidebar');
      const menuIcon = document.querySelector('.menu-icon');

      if (!sidebar.contains(e.target) && !menuIcon.contains(e.target)) {
          sidebar.classList.remove('active');
          menuIcon.classList.remove('hidden');
      }
  });