
import os

file_path = r'd:\PROGRAMACION\decidelibre-gravity\web-app\src\views\ProfileView.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar donde termina el </style> original antes de la basura
# La basura empieza en la linea 1278 (indice 1277)
# Linea 1277 es "}"
# Linea 1278 es "</style>/ * C o m p ..."

clean_lines = lines[:1277] # Mantener hasta antes de </style>

# Nuevo CSS mejorado
new_css = """
/* Compatibility Modal Styles */
.compatibility-modal {
  max-width: 600px;
  width: 90%;
  background: #1a1b2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  max-height: 85vh;
  border-radius: 16px;
}

.compatibility-modal .modal-header {
  background: rgba(255, 255, 255, 0.03);
  padding: 20px 25px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.compatibility-badge-large {
  background: linear-gradient(135deg, #10B981, #047857);
  color: white;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.5rem;
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.modal-user-info h3 {
  margin: 0 0 4px 0;
  font-size: 0.85rem;
  color: #9CA3AF;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.match-name {
  font-size: 1.4rem;
  font-weight: 800;
  color: white;
  display: block;
}

.compatibility-modal .modal-body {
  padding: 0;
  overflow-y: auto;
  flex: 1;
  background: #13141f;
}

.details-list {
  list-style: none;
  padding: 25px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  background: #1e2030;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 18px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.detail-item:hover {
  background: #25273c;
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 8px 15px rgba(0,0,0,0.2);
}

.detail-icon {
  width: 44px;
  height: 44px;
  background: rgba(59, 130, 246, 0.15);
  color: #60A5FA;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.detail-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-category {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #60A5FA;
  font-weight: 700;
  letter-spacing: 0.8px;
  margin-bottom: 2px;
}

.detail-question {
  color: #F3F4F6;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.4;
}

.detail-answer {
  margin-top: 8px;
  padding: 10px 12px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  font-size: 0.95rem;
  color: #D1FAE5;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.detail-answer span {
    color: #9CA3AF;
    font-size: 0.85rem;
}

.detail-answer strong {
  color: #34D399;
  font-weight: 700;
  font-size: 1rem;
}

.loading, .no-matches {
  padding: 50px;
  text-align: center;
  color: #9CA3AF;
  font-size: 1.1rem;
}

.loading i {
  margin-right: 12px;
  color: #60A5FA;
}
</style>
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)
    f.write(new_css)

print("Archivo ProfileView.vue limpiado y actualizado con nuevo CSS.")
