import json

def extract_code_cells_from_notebook(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        code_blocks = []
        for cell in notebook_data['cells']:
            if cell['cell_type'] == 'code':
                code_blocks.append(''.join(cell['source']))
        
        return '\n\n'.join(code_blocks)
    
    except Exception as e:
        print(f"Error processing Jupyter notebook {file_path}: {e}")
        return None
    
'''
if __name__ == "__main__":
    file_path = r"D:\venv-test\GANs\DCGAN\anime_dcgan.ipynb"
    code = extract_code_cells_from_notebook(file_path)
    print(code)

'''