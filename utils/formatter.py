def format_output(issues):

    if not issues:
        return "✅ No major issues found"

    result = "⚠️ Issues Found:\n"

    for i, issue in enumerate(issues, 1):
        result += f"{i}. {issue}\n"

    return result