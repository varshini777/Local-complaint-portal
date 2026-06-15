from backend import create_app
app = create_app()
print('Routes:')
for r in app.url_map.iter_rules():
    methods = sorted(m for m in r.methods if m not in {'HEAD', 'OPTIONS'})
    print(f'  {r.rule:<50s} -> {r.endpoint:<35s} {methods}')

