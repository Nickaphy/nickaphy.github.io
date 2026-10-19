---
title: PassCrypt
date: 2026-10-19
tags: projects, security
---

# PassCrypt

PassCrypt is a password manager I built with C# and Blazor. I wanted a project that brought together my interests in programming, cybersecurity, open source, and privacy.
I designed it to keep its vault on the user’s machine, without a PassCrypt account or built-in cloud sync. That keeps the project simple, but it also means there’s no password recovery if you forget your master password.
The vault is encrypted with AES-256-GCM. PassCrypt derives the encryption key from the master password using Argon2id. I store the Argon2id settings with the vault so they can be adjusted later without changing the code and potentially locking out existing vaults.

## Clean Architecture

I also tried using Clean Architecture. It helped me separate the interface, application logic, and storage, but it added overhead to a personal project. I spent time organizing code that could have gone toward improving the app. It was a useful lesson: an architecture can be well structured and still be more than a project needs.

## Takeaway

The main takeaway for me was that an architecture can be useful to learn, even when it’s more than a project needs. I understand the benefits of Clean Architecture, but on a project this size, following it too strictly meant spending more time maintaining structure than building useful features. In future personal projects, I’d use those ideas selectively and keep the design proportional to the problem.