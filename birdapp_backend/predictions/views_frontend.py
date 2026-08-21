# [AI-GENERATED - Claude AI 21-08-2026]
import os
from django.conf import settings
from django.views.static import serve

FRONTEND_DIST = os.path.join(settings.BASE_DIR.parent, 'birdapp-frontend', 'dist')

def frontend_view(request, path=''):
    """Serves the built React app. Serves the exact file if it exists
    (JS bundles, manifest, icons, etc), otherwise falls back to
    index.html so client-side routes still resolve."""
    file_path = os.path.join(FRONTEND_DIST, path)
    if path and os.path.isfile(file_path):
        return serve(request, path, document_root=FRONTEND_DIST)
    return serve(request, 'index.html', document_root=FRONTEND_DIST)