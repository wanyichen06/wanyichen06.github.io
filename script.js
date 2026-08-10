let currentNewsPage = 1;
const newsPerPage = 5;

function displayNewsPage(page) {
    const newsItems = document.querySelectorAll('.news-item');
    const totalPages = Math.max(1, Math.ceil(newsItems.length / newsPerPage));
    currentNewsPage = Math.min(Math.max(page, 1), totalPages);

    newsItems.forEach((item, index) => {
        const start = (currentNewsPage - 1) * newsPerPage;
        const end = start + newsPerPage;
        item.classList.toggle('active', index >= start && index < end);
    });

    document.getElementById('current-page').textContent = currentNewsPage;
    document.getElementById('total-pages').textContent = totalPages;
    document.getElementById('prev-btn').disabled = currentNewsPage === 1;
    document.getElementById('next-btn').disabled = currentNewsPage === totalPages;
    document.querySelector('.pagination').style.display = totalPages > 1 ? 'flex' : 'none';
}

function changePage(delta) {
    displayNewsPage(currentNewsPage + delta);
}

function showWechat(event) {
    event.preventDefault();
    document.getElementById('wechat-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeWechat(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('wechat-modal').style.display = 'none';
    document.body.style.overflow = '';
}

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeWechat();
});

const backToTop = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    backToTop.classList.toggle('show', window.scrollY > 360);
});

backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

displayNewsPage(1);
