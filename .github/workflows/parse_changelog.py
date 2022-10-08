import re
import sys


def parse_changelog(contents):
    """
    Parse the CHANGELOG.md and return a mapping from version to the section of the file
    corresponding to that version.

    :param contents: The contents of CHANGELOG.md.
    """
    result = {}

    # Split the changelog into sections based on lines starting with '## '
    for section in re.split(r'\n## ', contents):
        # Clean up each part by removing the compare links at the bottom of the file, and by
        # stripping whitespace
        section = re.split(r'\[Unreleased\]', section)[0].strip()

        # Add back the heading that was removed by re.split()
        section = '## ' + section

        # Parse out the version of this section. Any section which doesn't have a version (such as
        # the '## Unreleased' section or the top introduction) are not kept.
        version_match = re.search(r'## \[([0-9.]+)\].*', section)
        if version_match and len(version_match.groups()) >= 1:
            result[version_match.group(1)] = section

    return result


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Error: too few arguments.')
        sys.exit(1)

    changelog_path = sys.argv[1]
    version = sys.argv[2].removeprefix('v')
    output_path = sys.argv[3]

    with open(changelog_path, 'r') as f:
        changelog_sections = parse_changelog(f.read())

    current_section = changelog_sections.get(version)
    if not current_section:
        print(f'Error: could not find changelog section for version {version}')
        sys.exit(2)

    with open(output_path, 'w') as output:
        output.write(current_section)
