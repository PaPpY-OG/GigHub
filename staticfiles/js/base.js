function toggleMenu() {
    document.querySelector('.sidebar').classList.toggle('active');
  }
function toggleMenu() {
    document.querySelector('.sidebar').classList.toggle('active');
  }

  document.addEventListener('click', function(e) {
    const sidebar = document.querySelector('.sidebar');
    const menuIcon = document.querySelector('.menu-icon');
    if (!sidebar.contains(e.target) && !menuIcon.contains(e.target)) {
      sidebar.classList.remove('active');
    }
  });