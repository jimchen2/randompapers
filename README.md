1. Use agents to prepare the environment, it is much easier
(but Claude code agent locally cost me 8 dollars on one run, around 100 sessions with Opus 5, arena is free but they have a very small cloud platform)




https://arxiv.org/abs/2602.11389

---



- 1811.12359
- 1904.10098
- 1907.04809
- 2102.11107

- https://arxiv.org/abs/2509.21607
- https://arxiv.org/abs/2401.02602
- https://arxiv.org/pdf/2602.11389



23:37-1:20:00

https://www.youtube.com/watch?v=9DJWJpn0DmU&list=PLa1nV9NMvC6cejJg3LNw47ETopwM-CPgT&index=3


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
