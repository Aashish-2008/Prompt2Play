document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form');
  forms.forEach((form) => {
    form.addEventListener('submit', () => {
      const submitButton = form.querySelector('input[type="submit"]');
      if (!submitButton) return;
      submitButton.disabled = true;
      submitButton.value = 'Processing...';
    });
  });
});
