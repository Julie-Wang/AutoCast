"""AutoCast CLI 主入口"""
import argparse
import sys
import io
from pathlib import Path

# 修复 Windows 终端编码问题
_old_stdout = sys.stdout
_old_stderr = sys.stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from autocast.pipelines.doc_to_video import DocToVideoPipeline

def main():
    parser = argparse.ArgumentParser(
        description="AutoCast - AI-powered content pipeline for open source projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m autocast pipeline doc_to_video README.md --template release_note
  python -m autocast pipeline doc_to_video CHANGELOG.md --template bug_fix --output bugfix_demo
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # pipeline 命令
    pipeline_parser = subparsers.add_parser("pipeline", help="运行流水线")
    pipeline_subparsers = pipeline_parser.add_subparsers(dest="pipeline_type")

    # doc_to_video 子命令
    doc2video = pipeline_subparsers.add_parser("doc_to_video", help="文档转视频")
    doc2video.add_argument("source", help="源文档路径 (如 README.md)")
    doc2video.add_argument("--template", default="release_note", 
                          choices=["release_note", "bug_fix", "feature_demo", "contributor_thanks"],
                          help="视频模板")
    doc2video.add_argument("--output", default=None, help="输出文件名")
    doc2video.add_argument("--config", default="config.yaml", help="配置文件路径")

    # issue_to_visual 子命令（占位）
    issue2visual = pipeline_subparsers.add_parser("issue_to_visual", help="Issue 转信息图")
    issue2visual.add_argument("--issue", type=int, required=True, help="Issue 编号")
    issue2visual.add_argument("--config", default="config.yaml", help="配置文件路径")

    # 其他命令
    list_parser = subparsers.add_parser("list", help="列出可用模板")

    version_parser = subparsers.add_parser("version", help="显示版本")

    args = parser.parse_args()

    if args.command == "pipeline":
        if args.pipeline_type == "doc_to_video":
            pipeline = DocToVideoPipeline(args.config)
            pipeline.run(args.source, args.template, args.output)
        elif args.pipeline_type == "issue_to_visual":
            print("🚧 Issue to Visual 功能开发中...")
        else:
            pipeline_parser.print_help()

    elif args.command == "list":
        print("📋 可用模板:")
        print("  release_note      - 版本发布视频")
        print("  bug_fix          - Bug 修复说明")
        print("  feature_demo     - 新功能演示")
        print("  contributor_thanks - 贡献者致谢")

    elif args.command == "version":
        from autocast import __version__
        print(f"AutoCast v{__version__}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
