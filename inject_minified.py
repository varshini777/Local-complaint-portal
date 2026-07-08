import os

feedback_ui_admin = """
    {% if complaint.feedbacks %}
      {% set fb = complaint.feedbacks[0] %}
      <h3 class="h6 mt-4 border-top pt-3">Citizen Feedback</h3>
      <div class="d-flex align-items-center mb-2">
        <span class="badge bg-success me-2">Rating: {{ fb.rating }}/5</span>
      </div>
      <p class="fst-italic">"{{ fb.comment }}"</p>
    {% endif %}
"""

def inject_minified(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return
        
    if 'Citizen Feedback' in content:
        return
        
    insert_target = '</div></div><div class="col-lg-4">'
    if insert_target in content:
        content = content.replace(insert_target, feedback_ui_admin + insert_target)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Injected feedback UI into {filepath}')

inject_minified('d:/Local_complaint/backend/templates/admin/complaint_detail.html')
inject_minified('d:/Local_complaint/backend/templates/officer/complaint_detail.html')
