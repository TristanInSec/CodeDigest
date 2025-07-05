# -*- coding: utf-8 -*-
"""
CodeDigest - Repository Aggregator Script

Author: @TristanInSec
License: MIT

Purpose:
    This script recursively scans a source code repository and exports its structure
    and contents into a single AI-friendly file (XML, JSON, or YAML). It distinguishes
    between text files (e.g., .py, .md, .yaml) and other assets (e.g., images, archives),
    embedding readable content as needed.

Version: 0.1

Command Line Usage:
    python codedigest.py --path /repo --output digest.xml
    python codedigest.py --path /repo --output digest.xml --timestamp
    python codedigest.py --path /repo --output digest.yaml --skip-other --only-text
    python codedigest.py --path /repo --output digest.json --include-ext .tex .bib
    python codedigest.py --path /repo --output digest.json --include-ext .cfg .conf --exclude-dir .venv .log
    python codedigest.py --path /repo --output digest.xml --no-summary --no-structure

Features:
    - Recursive folder walk with exclusion support (.git, __pycache__, etc.)
    - Rich file type classification: text, picture, audio, video, archive, other
    - Embeds text file content in output (within CDATA for XML)
    - Includes file type statistics and directory tree summary (optional)
    - Format auto-selected by file extension
    - CLI options to skip mentionning "other" binaries, include only "text" files
    - CLI options to override extensions or folders to include/exclude
    - Optional timestamp insertion in output filename

External dependency:
    - Requires PyYAML (install with: pip install PyYAML)

"""

import os
import argparse
import mimetypes
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import yaml
import datetime
from collections import defaultdict
from pathlib import Path

__version__ = "0.1"

class CDATA(str):
    pass

# Patch ElementTree to support CDATA
ET._original_serialize_xml = ET._serialize_xml
def _serialize_xml(write, elem, qnames, namespaces, short_empty_elements=True, **kwargs):
    if elem.text and isinstance(elem.text, CDATA):
        write(f"<{elem.tag}>")
        write(f"<![CDATA[{elem.text}]]>")
        for e in elem:
            ET._original_serialize_xml(write, e, qnames, namespaces, short_empty_elements=short_empty_elements)
        write(f"</{elem.tag}>")
    else:
        ET._original_serialize_xml(write, elem, qnames, namespaces, short_empty_elements=short_empty_elements)
ET._serialize_xml = _serialize_xml

def detect_file_type(file_path, include_exts):
    """Return (file_type, ext) or (None, ext) if excluded."""
    ext = os.path.splitext(file_path)[1].lower()
    if include_exts and ext not in include_exts:
        return None, ext
    if ext in {'.py', '.md', '.yaml', '.yml', '.sh', '.csv', '.txt', '.log', '.tex', '.bib'}:
        return "text", ext
    mime, _ = mimetypes.guess_type(file_path)
    if mime:
        if mime.startswith("image/"):    
            return "picture", ext
        if mime.startswith("audio/"):    
            return "audio",   ext
        if mime.startswith("video/"):    
            return "video",   ext
        if mime.startswith("application/zip") or ext in {'.zip', '.tar', '.gz'}:
            return "archive", ext
    return "other", ext

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ")

def create_summary_block(stats_dict, ext_stats):
    summary = ET.Element('summary')
    for type_name, count in stats_dict.items():
        ET.SubElement(summary, 'stat', type=type_name).text = str(count)
    ext_block = ET.SubElement(summary, 'extension_stats')
    for ext, count in sorted(ext_stats.items()):
        ET.SubElement(ext_block, 'ext', name=ext).text = str(count)
    return summary

def create_structure_block(paths_list):
    structure = ET.Element('directory_structure')
    for path in sorted(paths_list):
        ET.SubElement(structure, 'entry').text = path
    return structure

def create_code_digest_tree(repo_path, include_exts, exclude_dirs,
                            skip_other, only_text, include_summary=True, include_structure=True):
    stats = defaultdict(int)
    ext_stats = defaultdict(int)
    paths = []
    repo_name = os.path.basename(os.path.abspath(repo_path))
    root = ET.Element('repository', name=repo_name)

    for dirpath, dirnames, filenames in os.walk(repo_path):
        rel_dir = os.path.relpath(dirpath, repo_path)
        if any(part in exclude_dirs for part in Path(rel_dir).parts):
            continue
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        paths.append(rel_dir + '/')
        folder_elem = ET.SubElement(root, 'folder', path=rel_dir)

        for fname in filenames:
            file_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(file_path, repo_path)
            file_type, ext = detect_file_type(file_path, include_exts)
            if file_type is None:                   continue
            if skip_other and file_type == "other": continue
            if only_text and file_type != "text":   continue

            paths.append(rel_path)
            stats[file_type] += 1
            ext_stats[ext] += 1
            file_elem = ET.SubElement(folder_elem, 'file', path=rel_path, type=file_type)
            if file_type == "text":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    code = ET.SubElement(file_elem, 'code')
                    code.text = CDATA(content)
                except Exception as e:
                    file_elem.set('error', f"Cannot read: {e}")

    if include_structure:
        root.insert(0, create_structure_block(paths))
    if include_summary:
        root.insert(0, create_summary_block(stats, ext_stats))
    return root

def create_code_digest_dict(repo_path, include_exts, exclude_dirs,
                            skip_other, only_text, include_summary=True, include_structure=True):
    stats = defaultdict(int)
    ext_stats = defaultdict(int)
    paths = []
    repo_name = os.path.basename(os.path.abspath(repo_path))
    result = {'repository': {'name': repo_name, 'folders': {}}}

    for dirpath, dirnames, filenames in os.walk(repo_path):
        rel_dir = os.path.relpath(dirpath, repo_path)
        if any(part in exclude_dirs for part in Path(rel_dir).parts):
            continue
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        paths.append(rel_dir + '/')
        folder = result['repository']['folders'].setdefault(rel_dir, {'files': []})

        for fname in filenames:
            file_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(file_path, repo_path)
            file_type, ext = detect_file_type(file_path, include_exts)
            if file_type is None:                   continue
            if skip_other and file_type == "other": continue
            if only_text and file_type != "text":   continue

            paths.append(rel_path)
            stats[file_type] += 1
            ext_stats[ext] += 1
            rec = {'path': rel_path, 'type': file_type}
            if file_type == "text":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        rec['code'] = f.read()
                except Exception as e:
                    rec['error'] = f"Cannot read: {e}"
            folder['files'].append(rec)

    if include_summary:
        result['repository']['summary'] = dict(stats)
        result['repository']['extension_stats'] = dict(ext_stats)
    if include_structure:
        result['repository']['directory_structure'] = sorted(paths)

    return result

def main():
    parser = argparse.ArgumentParser(description='CodeDigest: Aggregate repository into XML, JSON, or YAML.')
    parser.add_argument('--path',        required=True, help='Repository root path')
    parser.add_argument('--output',      required=True, help='Output file (.xml, .json, .yaml)')
    parser.add_argument('--timestamp',   action='store_true', help='Append timestamp to filename')
    parser.add_argument('--skip-other',  action='store_true', help='Skip files of type "other"')
    parser.add_argument('--only-text',   action='store_true', help='Include only text files')
    parser.add_argument('--include-ext', nargs='*', default=None, help='Extensions to include')
    parser.add_argument('--exclude-dir', nargs='*', default=None, help='Directories to exclude')
    parser.add_argument('--no-summary',  action='store_true', help='Disable summary block')
    parser.add_argument('--no-structure',action='store_true', help='Disable structure block')
    parser.add_argument('--version',     action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    # prepare output filename
    if args.timestamp:
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M")
        base, ext = os.path.splitext(args.output)
        output_file = f"{base}_{ts}{ext}"
    else:
        output_file = args.output
    fmt = os.path.splitext(output_file)[1].lower()

    include_exts     = set(args.include_ext) if args.include_ext else {'.py','.md','.yaml','.yml','.sh','.csv','.txt','.log'}
    exclude_dirs     = set(args.exclude_dir) if args.exclude_dir else {'.git','__pycache__','.venv','node_modules','.idea','docs','outputs'}
    include_summary  = not args.no_summary
    include_structure= not args.no_structure

    # Configuration summary
    print("[+] Configuration Summary")
    print(f"    ├── Input path           : {args.path}")
    print(f"    ├── Output file          : {output_file}")
    print(f"    ├── Output format        : {fmt.upper()[1:]}")
    print(f"    ├── Timestamp appended   : {'Yes' if args.timestamp else 'No'}")
    print(f"    ├── Include only text    : {'Yes' if args.only_text else 'No'}")
    print(f"    ├── Skip 'other' files   : {'Yes' if args.skip_other else 'No'}")
    print(f"    ├── Include summary block: {'Yes' if include_summary else 'No'}")
    print(f"    ├── Include structure    : {'Yes' if include_structure else 'No'}")
    print(f"    ├── Included extensions  : {sorted(include_exts)}")
    print(f"    └── Excluded directories : {sorted(exclude_dirs)}")

    try:
        # build data structure
        data = create_code_digest_dict(
            args.path, include_exts, exclude_dirs,
            args.skip_other, args.only_text,
            include_summary, include_structure
        )

        # write output
        if fmt == '.xml':
            tree = create_code_digest_tree(
                args.path, include_exts, exclude_dirs,
                args.skip_other, args.only_text,
                include_summary, include_structure
            )
            content = prettify(tree)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

        elif fmt in ('.json', '.yaml', '.yml'):
            with open(output_file, 'w', encoding='utf-8') as f:
                if fmt == '.json':
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(data, f, allow_unicode=True)
        else:
            print("[-] Unsupported format. Use .xml, .json, or .yaml/.yml")
            return

        size_mb = os.path.getsize(output_file) / (1024*1024)

        # terminal stats in nested tree form
        if include_summary:
            summary   = data['repository'].get('summary', {})
            ext_stats = data['repository'].get('extension_stats', {})
            print("[+] File Statistics")
            # types
            types = sorted(summary.items())
            print("    ├── By Type:")
            for i, (t, cnt) in enumerate(types):
                branch = "├──" if i < len(types)-1 else "└──"
                print(f"    │    {branch} {t:<10}: {cnt}")
            # extensions
            if ext_stats:
                exts = sorted(ext_stats.items())
                print("    └── By Extension:")
                for i, (e, cnt) in enumerate(exts):
                    branch = "├──" if i < len(exts)-1 else "└──"
                    print(f"         {branch} {e:<7}: {cnt}")

        print(f"[+] File created successfully: {output_file} ({size_mb:.2f} MB)")

    except Exception as e:
        print(f"[-] Error during export: {e}")

if __name__ == '__main__':
    main()
