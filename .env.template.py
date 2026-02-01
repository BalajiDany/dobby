import os
import re


def generate_template(input_file='.env', output_file='.env.template'):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r') as f:
        lines = f.readlines()

    template_lines = []

    for line in lines:
        # Strip whitespace from the end but keep the newline character
        stripped_line = line.strip()

        # Keep comments and empty lines exactly as they are
        if not stripped_line or stripped_line.startswith('#'):
            template_lines.append(line)
        elif '=' in stripped_line:
            # Match the key and replace everything after the first '=' with nothing
            # This regex handles cases with or without spaces around the '='
            new_line = re.sub(r'(=.*)', '=', line)
            template_lines.append(new_line)
        else:
            # Fallback for lines that don't match standard env format
            template_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(template_lines)

    print(f"Successfully created {output_file} from {input_file}")


if __name__ == "__main__":
    generate_template()
