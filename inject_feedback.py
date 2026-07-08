import os

feedback_ui_citizen = """
    {% if complaint.feedback %}
      {% set fb = complaint.feedback[0] if complaint.feedback|is_iterable else complaint.feedback %}
      {% if fb %}
      <h3 class="h6 mt-4 border-top pt-3">Your Feedback</h3>
      <div class="d-flex align-items-center mb-2">
        <span class="badge bg-success me-2">Rating: {{ fb.rating }}/5</span>
        <span class="text-muted small">{{ fb.created_at|datetime if fb.created_at else '' }}</span>
      </div>
      <p class="fst-italic">"{{ fb.comment }}"</p>
      {% endif %}
    {% elif complaint.status in ['Resolved', 'Closed'] %}
      <div class="mt-4 border-top pt-3">
        <a href="{{ url_for('citizen.submit_feedback', complaint_id=complaint.complaint_id) }}" class="btn btn-primary">
          <i class="bi bi-star-fill"></i> Provide Feedback
        </a>
      </div>
    {% endif %}
"""

feedback_ui_admin = """
    {% if complaint.feedback %}
      {% set fb = complaint.feedback[0] if complaint.feedback|is_iterable else complaint.feedback %}
      {% if fb %}
      <h3 class="h6 mt-4 border-top pt-3">Citizen Feedback</h3>
      <div class="d-flex align-items-center mb-2">
        <span class="badge bg-success me-2">Rating: {{ fb.rating }}/5</span>
      </div>
      <p class="fst-italic">"{{ fb.comment }}"</p>
      {% endif %}
    {% endif %}
"""

def inject_feedback(filepath, ui_snippet):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return
        
    if 'Citizen Feedback' in content or 'Your Feedback' in content or 'Provide Feedback' in content:
        return
        
    # Append to the end of the col-lg-8 div
    insert_target = '  </div></div>'
    if insert_target in content:
        content = content.replace(insert_target, ui_snippet + '\n' + insert_target)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Injected feedback UI into {filepath}')

inject_feedback('d:/Local_complaint/backend/templates/citizen/complaint_detail.html', feedback_ui_citizen)
inject_feedback('d:/Local_complaint/backend/templates/admin/complaint_detail.html', feedback_ui_admin)
inject_feedback('d:/Local_complaint/backend/templates/officer/complaint_detail.html', feedback_ui_admin)
