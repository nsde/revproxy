# Reverse Proxy
A very simple reverse proxy for websites and APIs.
Quite easy to set up.

![Explanation of how it works](explanation.png)


## Why?
- **Censorship circumvention:** create a mirror of almost any website in seconds!
- **Privacy:** hide your IP address from the website you're mirroring!
    > - specify **`expose-client-ip: true`** if you want the target website to know the IP address of the client
- **Security:** hide your server's IP address from the public!

## Supported platforms
- Microsoft **Windows** 10 and higher
- Most newer Debian-based **Linux** distributions

## How?	
- **Install:** `python -m pip install --upgrade -r requirements.txt`
- **Configure:** edit `config.yml`
- **Run:** `python revproxy run-debug`
