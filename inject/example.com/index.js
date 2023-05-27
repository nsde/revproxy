text = document.querySelector('p');
text.textContent = "You're currently viewing example.com, with injected CSS and JS by the reverse proxy.";

link = document.querySelector('a');
link.href = '/';
link.textContent = 'Back home';
