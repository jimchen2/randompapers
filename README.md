- 1811.12359
- 1904.10098
- 1907.04809
- 2102.11107

- https://arxiv.org/abs/2509.21607
- https://arxiv.org/abs/2401.02602
- https://arxiv.org/pdf/2602.11389

- https://youtu.be/9DJWJpn0DmU
- https://youtu.be/btmJtThWmhA

https://github.com/galilai-group/cjepa


for arena agents

```
(function expandTargetButtons() {
  const targets = Array.from(document.querySelectorAll('button[aria-expanded="false"]')).filter(btn => {
    const text = btn.innerText.toLowerCase();
    return text.includes("ran commands") || text.includes("used\nbash") || text.includes("used bash");
  });

  if (targets.length === 0) return;

  targets.forEach(btn => btn.click());
  setTimeout(expandTargetButtons, 200);
})();
```

This library is useful: https://github.com/pdenya/ccbashhistory
