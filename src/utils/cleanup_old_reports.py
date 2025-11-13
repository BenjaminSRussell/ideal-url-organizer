"""
Utility to clean up old scattered report files after unified report generation
"""
from pathlib import Path
from datetime import datetime
import shutil


def cleanup_old_reports(project_root: Path = None, dry_run: bool = False):
    """
    Clean up old scattered report files (JSON, MD) from analysis directory

    Args:
        project_root: Project root directory
        dry_run: If True, only print what would be deleted without deleting

    Returns:
        Number of files cleaned up
    """
    if project_root is None:
        # Try to find project root
        current = Path(__file__).parent.parent.parent
        project_root = current

    analysis_dir = project_root / 'data' / 'results' / 'analysis'

    if not analysis_dir.exists():
        print("[!] Analysis directory not found")
        return 0

    # Files and directories to clean up
    files_to_remove = []
    dirs_to_remove = []

    # Find old JSON and MD files in main analysis directory
    for pattern in ['*.json', '*.md']:
        files_to_remove.extend(analysis_dir.glob(pattern))

    # Find old subdirectories (advanced, reports, link_graph, semantic)
    old_subdirs = ['advanced', 'reports', 'link_graph', 'semantic']
    for subdir_name in old_subdirs:
        subdir = analysis_dir / subdir_name
        if subdir.exists() and subdir.is_dir():
            dirs_to_remove.append(subdir)

    total_count = len(files_to_remove) + len(dirs_to_remove)

    if total_count == 0:
        print("[+] No old report files to clean up")
        return 0

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Cleaning up old report files...")

    # Remove files
    for file_path in files_to_remove:
        if dry_run:
            print(f"  Would delete: {file_path.relative_to(project_root)}")
        else:
            try:
                file_path.unlink()
                print(f"  [-] Deleted: {file_path.relative_to(project_root)}")
            except Exception as e:
                print(f"  [!] Failed to delete {file_path.name}: {e}")

    # Remove directories
    for dir_path in dirs_to_remove:
        if dry_run:
            print(f"  Would delete directory: {dir_path.relative_to(project_root)}")
        else:
            try:
                shutil.rmtree(dir_path)
                print(f"  [-] Deleted directory: {dir_path.relative_to(project_root)}")
            except Exception as e:
                print(f"  [!] Failed to delete directory {dir_path.name}: {e}")

    if not dry_run:
        print(f"\n[+] Cleaned up {total_count} items")
    else:
        print(f"\n[+] Would clean up {total_count} items (dry run)")

    return total_count


def archive_old_reports(project_root: Path = None):
    """
    Archive old scattered report files instead of deleting them

    Args:
        project_root: Project root directory

    Returns:
        Path to archive directory
    """
    if project_root is None:
        current = Path(__file__).parent.parent.parent
        project_root = current

    analysis_dir = project_root / 'data' / 'results' / 'analysis'
    archive_dir = project_root / 'data' / 'archive'

    # Create timestamp-based archive directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_target = archive_dir / f'old_reports_{timestamp}'
    archive_target.mkdir(parents=True, exist_ok=True)

    if not analysis_dir.exists():
        print("[!] Analysis directory not found")
        return None

    # Files and directories to archive
    items_archived = 0

    # Archive JSON and MD files
    for pattern in ['*.json', '*.md']:
        for file_path in analysis_dir.glob(pattern):
            try:
                dest = archive_target / file_path.name
                shutil.copy2(file_path, dest)
                file_path.unlink()
                items_archived += 1
                print(f"  [+] Archived: {file_path.name}")
            except Exception as e:
                print(f"  [!] Failed to archive {file_path.name}: {e}")

    # Archive subdirectories
    old_subdirs = ['advanced', 'reports', 'link_graph', 'semantic']
    for subdir_name in old_subdirs:
        subdir = analysis_dir / subdir_name
        if subdir.exists() and subdir.is_dir():
            try:
                dest = archive_target / subdir_name
                shutil.copytree(subdir, dest)
                shutil.rmtree(subdir)
                items_archived += 1
                print(f"  [+] Archived directory: {subdir_name}")
            except Exception as e:
                print(f"  [!] Failed to archive directory {subdir_name}: {e}")

    if items_archived > 0:
        print(f"\n[+] Archived {items_archived} items to: {archive_target.relative_to(project_root)}")
        return archive_target
    else:
        # Remove empty archive directory
        archive_target.rmdir()
        print("[+] No items to archive")
        return None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clean up old scattered report files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without deleting')
    parser.add_argument('--archive', action='store_true', help='Archive files instead of deleting')

    args = parser.parse_args()

    if args.archive:
        archive_old_reports()
    else:
        cleanup_old_reports(dry_run=args.dry_run)
