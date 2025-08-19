function toggleHeart(button) {
    const heartIcon = button.querySelector('.heart-icon');
    const productId = button.getAttribute('data-product-id');
    const isLiked = button.getAttribute('data-liked') === 'true';
    const likeCountElement = document.getElementById(`like-count-${productId}`);

    // AJAX 요청
    fetch(`/shop/product/${productId}/toggle_like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}', // CSRF 토큰
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            heartIcon.src = heartIcon.getAttribute('data-filled-src'); // 채워진 하트
            button.setAttribute('data-liked', 'true');
        } else {
            heartIcon.src = heartIcon.getAttribute('data-empty-src'); // 빈 하트
            button.setAttribute('data-liked', 'false');
        }
        // 좋아요 개수 업데이트
        likeCountElement.textContent = data.like_count;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('좋아요 상태를 변경하는 중 문제가 발생했습니다.');
    });
}
