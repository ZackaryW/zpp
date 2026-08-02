---
name: python-django-tdd
description: Apply Django-aware Python utility testing guidance
order: 510
config:
  useThis: true
skill_lookup: []
---
Use pytest with Django's supported test integration for utilities that require
models, settings, transactions, or request objects. Prefer pure focused tests
when framework state is unnecessary, and keep feature policy in BDD scenarios.
