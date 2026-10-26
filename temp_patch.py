from pathlib import Path

p = Path('comptes/models.py')
text = p.read_text(encoding='utf-8')
old = '''    role = models.CharField(max_length=30, choices=Role.choices)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
'''
new = '''    role = models.CharField(max_length=30, choices=Role.choices)

    def is_anp(self):
        return self.role == self.Role.TECHNICIEN_ANP

    def is_haddoun(self):
        return self.role in {
            self.Role.DIRECTEUR,
            self.Role.CHEF_EQUIPE,
            self.Role.TECHNICIEN,
            self.Role.TECHNICIEN_HADDOUN,
        }

    def is_technicien_haddoun(self):
        return self.role in {self.Role.TECHNICIEN, self.Role.TECHNICIEN_HADDOUN}

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
'''

if old not in text:
    raise SystemExit('OLD block not found in comptes/models.py')

text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')
print('patched')
