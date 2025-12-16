from kernel.tools.filesystem import FileSystemTool


TOOLS = {
    "filesystem.read": FileSystemTool().read,
    "filesystem.write": FileSystemTool().write,
}
