
import json
import os

# Path to questions.json
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions.json')

def determine_type(options, title="", current_type=None):
    # Preserve existing explicit types if valid
    if current_type in ['slider']:
        return current_type

    if not options:
        return 'open'

    # Convert options to strings for comparison
    opts_str = [str(o).lower() for o in options if isinstance(o, (str, int))]
    
    # Binary
    if set(opts_str) == {'si', 'no'}:
        return 'binary'
    
    # Scale (1-5)
    scale_opts = ['1', '2', '3', '4', '5']
    if opts_str == scale_opts:
        return 'scale'
        
    # Default
    return 'dropdown'

def process_file():
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    
    for category, questions in data.items():
        for q in questions:
            # Get current type if exists
            current_type = q.get('question_type')
            
            # Determine correct type
            new_type = determine_type(q['options'], q['title'], current_type)
            
            # Update/Set type
            q['question_type'] = new_type
            updated_count += 1
            
            print(f"Updated '{q['title'][:30]}...' -> {new_type}")

    # Write back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"\n✅ Updated {updated_count} questions in {json_path}")

if __name__ == "__main__":
    process_file()
