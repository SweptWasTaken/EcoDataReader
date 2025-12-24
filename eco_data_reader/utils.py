import re
import codecs


class JsonTypeScriptProcessor:
    @staticmethod
    def process_json_to_typescript(json_str: str) -> str:
        result = json_str.replace('"', "'")
        result = re.sub(r"'item':'(\w+)'", r"'item':getItemByNameID('\1')", result)
        result = re.sub(r"'skill':'(\w+)'", r"'skill':getSkillByNameID('\1')", result)
        result = re.sub(r"'craftingTable':'(\w+)'", r"'craftingTable':getCraftingTableByNameID('\1')", result)
        # Decode unicode escape sequences
        result = codecs.decode(result, 'unicode_escape')
        return result

    @staticmethod
    def process_typescript_to_json(typescript: str) -> str:
        result = re.sub(r"'item': getItemByNameID\('(\w+)'\)", r"'item':'\1'", typescript)
        result = re.sub(r"'skill': getSkillByNameID\('(\w+)'\)", r"'skill':'\1'", result)
        result = re.sub(r"'craftingTable': getCraftingTableByNameID\('(\w+)'\)", r"'craftingTable':'\1'", result)
        result = result.replace("'", '"')
        return result
