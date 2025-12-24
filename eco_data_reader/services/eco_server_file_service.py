import os
import re
import logging
from pathlib import Path
from decimal import Decimal
from typing import List, Optional
from ..models import Item, Recipe, Ingredient, Output, CraftingTable, Skill

logger = logging.getLogger(__name__)


class EcoServerFileService:
    ITEMS_LOCATION = "AutoGen\\"
    TAGS_LOCATION = "Systems\\TagDefinitions.cs"

    ITEM_FOLDERS = ["Block", "Clothing", "Fertilizer", "Food", "Item",
                    "PluginModule", "Seed", "Tool", "Vehicle", "WorldObject"]

    RECIPE_FOLDERS = ["Block", "Clothing", "Fertilizer", "Food", "Item",
                      "PluginModule", "Recipe", "Seed", "Tool", "Vehicle", "WorldObject"]

    CRAFTING_TABLE_FOLDERS = ["WorldObject"]
    SKILL_FOLDERS = ["Tech"]

    def __init__(self, eco_server_mods_core_path: str):
        self.eco_server_path = eco_server_mods_core_path

    def get_all_items(self) -> List[Item]:
        items = []

        for folder in self.ITEM_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    name = self._get_name_from_cs_file_contents(file_contents)
                    if name:
                        item_name_id = self._get_item_name_id_from_cs_file_contents(file_contents)
                        items.append(Item(
                            name=name,
                            item_name_id=item_name_id,
                            image_file="UI_Icons_06.png",
                            x_pos=0,
                            y_pos=0
                        ))
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        items.sort(key=lambda x: x.item_name_id)
        return items

    def get_all_tags(self) -> List[Item]:
        tags = []

        try:
            tags_file = Path(self.eco_server_path) / self.TAGS_LOCATION
            with open(tags_file, 'r', encoding='utf-8') as f:
                file_contents = f.read()

            # Ignore hidden tags in tag definitions file
            hidden_index = file_contents.find("Hidden")
            if hidden_index != -1:
                file_contents = file_contents[:hidden_index]

            tag_regex = r'new TagDefinition\("([\w\s]+)"'
            matches = re.finditer(tag_regex, file_contents)

            for match in matches:
                tag_name = match.group(1)
                tag_name = tag_name.replace(" ", "")
                # Split by camel case
                tag_name_spaced = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', tag_name)).strip()
                tags.append(Item(
                    name=tag_name_spaced,
                    item_name_id=tag_name.replace(" ", ""),
                    tag=True
                ))
        except Exception as e:
            logger.error(f"Error reading tags: {e}")

        tags.sort(key=lambda x: x.item_name_id)
        return tags

    def get_all_recipes(self) -> List[Recipe]:
        recipes = []

        for folder in self.RECIPE_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    recipe = self._get_recipe_from_cs_file_contents(file_contents, file_path.name)
                    if recipe:
                        recipes.append(recipe)
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        recipes.sort(key=lambda x: x.name_id)
        return recipes

    def get_all_crafting_tables(self) -> List[CraftingTable]:
        crafting_tables = []

        for folder in self.CRAFTING_TABLE_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    crafting_table = self._get_crafting_table_from_cs_file_contents(
                        file_contents, file_path.name)
                    if crafting_table:
                        crafting_tables.append(crafting_table)
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        crafting_tables.sort(key=lambda x: x.crafting_table_name_id)
        return crafting_tables

    def get_all_skills(self) -> List[Skill]:
        skills = []

        for folder in self.SKILL_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    skill = self._get_skill_from_cs_file_contents(file_contents, file_path.name)
                    if skill:
                        skills.append(skill)
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        skills.sort(key=lambda x: x.name_id)
        return skills

    @staticmethod
    def _get_recipe_from_cs_file_contents(contents: str, file_name: str) -> Optional[Recipe]:
        # Recipe display name (e.g. Butcher Bison)
        recipe_name_regex = r'displayName:\s*Localizer\.DoStr\("([\w\s]+)"\)'
        match = re.search(recipe_name_regex, contents)
        if not match:
            logger.warning(f"Could not find recipe name for file {file_name}")
            return None
        recipe_name = match.group(1)

        # Recipe name ID (e.g. ButcherBison)
        recipe_name_id_regex = r'recipe.Init\(\n*\s*name:\s*"(\w+)"'
        match = re.search(recipe_name_id_regex, contents)
        if not match:
            logger.warning(f"Could not find recipe name ID for recipe {recipe_name}")
            return None
        recipe_name_id = match.group(1)

        ingredients = []

        # Recipe ingredients - Specific items (non-tag)
        recipe_ingredient_regex = r'new IngredientElement\(typeof\( *(\w+)\), (\d+(?:\.\d+)?)f?, *(\w+)'
        matches = re.finditer(recipe_ingredient_regex, contents)
        for match in matches:
            ingredient_name_id = match.group(1)
            quantity = Decimal(match.group(2))
            reducible = match.group(3).lower() == "typeof"
            ingredients.append(Ingredient(
                item_name_id=ingredient_name_id,
                quantity=quantity,
                reducible=reducible,
                tag=False
            ))

        # Recipe ingredients - tags
        tag_recipe_ingredients_regex = r'new IngredientElement\("([\w\s]+)", *(\d+), *(\w+)'
        matches = re.finditer(tag_recipe_ingredients_regex, contents)
        for match in matches:
            tag_ingredient_name_id = match.group(1).replace(" ", "")
            quantity = Decimal(match.group(2))
            reducible = match.group(3).lower() == "typeof"
            ingredients.append(Ingredient(
                item_name_id=tag_ingredient_name_id,
                quantity=quantity,
                reducible=reducible,
                tag=True
            ))

        if not ingredients:
            logger.warning(f"Could not find ingredients for recipe {recipe_name}")

        outputs = []

        # Recipe outputs
        recipe_outputs_regex = r'new CraftingElement<(\w+)>\((\d*\.?\d*)f?\)'
        matches = re.finditer(recipe_outputs_regex, contents)
        output_count = 0
        for match in matches:
            output_item_name_id = match.group(1)
            quantity_string = match.group(2)
            quantity = Decimal(1) if not quantity_string else Decimal(quantity_string)
            output = Output(
                item_name_id=output_item_name_id,
                quantity=quantity,
                reducible=False,
                primary=(output_count == 0)
            )
            outputs.append(output)
            output_count += 1

        if not outputs:
            logger.warning(f"Could not find outputs for recipe {recipe_name}")

        # Recipe outputs - secondary (e.g. Tailings, Slag, Barrel)
        recipe_outputs_waste_regex = r'new CraftingElement<(\w+)>\(typeof\(\w+\), (\d+)(,?)'
        matches = re.finditer(recipe_outputs_waste_regex, contents)
        for match in matches:
            output_item_name_id = match.group(1)
            quantity = Decimal(match.group(2))
            reducible = bool(match.group(3)) or "Tailings" in output_item_name_id or "Slag" in output_item_name_id
            outputs.append(Output(
                item_name_id=output_item_name_id,
                quantity=quantity,
                reducible=reducible
            ))

        # Skill and level
        skill_level_regex = r'\[RequiresSkill\(typeof\((\w+)\), (\d)'
        match = re.search(skill_level_regex, contents)
        if match:
            skill_name_id = match.group(1)
            level = int(match.group(2))
        else:
            logger.warning(f"Could not find skill and level for recipe {recipe_name}, assuming SelfImprovement")
            skill_name_id = "SelfImprovementSkill"
            level = 0

        # Labor cost
        labor_regex = r'CreateLaborInCaloriesValue\((\d+)'
        match = re.search(labor_regex, contents)
        if match:
            labor = int(match.group(1))
        else:
            logger.warning(f"Could not find labor cost for recipe {recipe_name}")
            labor = 0

        # Crafting table
        crafting_table_regex = r'CraftingComponent\.AddRecipe\(tableType:\s*typeof\((\w+)\)'
        match = re.search(crafting_table_regex, contents)
        if match:
            crafting_table_name_id = match.group(1)
        else:
            logger.warning(f"Could not find crafting table for recipe {recipe_name}")
            crafting_table_name_id = ""

        return Recipe(
            name=recipe_name,
            name_id=recipe_name_id,
            skill_name_id=skill_name_id,
            level=level,
            labor=labor,
            crafting_table_name_id=crafting_table_name_id,
            ingredients=ingredients,
            outputs=outputs
        )

    @staticmethod
    def _get_name_from_cs_file_contents(contents: str) -> Optional[str]:
        name_search_regex = r'LocDisplayName\("([\w\s]+)"'
        match = re.search(name_search_regex, contents)
        return match.group(1) if match else None

    @staticmethod
    def _get_item_name_id_from_cs_file_contents(contents: str) -> Optional[str]:
        name_search_regex = r'public partial class (\w+Item)'
        match = re.search(name_search_regex, contents)
        return match.group(1) if match else None

    @staticmethod
    def _get_skill_from_cs_file_contents(file_contents: str, file_name: str) -> Optional[Skill]:
        skill_search_regex = r'Tag\("Specialty"\)'
        if not re.search(skill_search_regex, file_contents):
            return None

        name_id_search_regex = r'public partial class (\w+Skill) : Skill'
        match = re.search(name_id_search_regex, file_contents)
        if not match:
            logger.warning(f"Could not find skill name ID for file {file_name}")
            return None
        name_id = match.group(1)

        name = file_name.replace(".cs", "")
        # Split by camel case
        name = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).strip()

        return Skill(name=name, name_id=name_id)

    @staticmethod
    def _get_crafting_table_from_cs_file_contents(file_contents: str, file_name: str) -> Optional[CraftingTable]:
        crafting_search_regex = r'RequireComponent\(typeof\(CraftingComponent'
        if not re.search(crafting_search_regex, file_contents):
            return None

        name_search_regex = r'DisplayName\s+=>\s+Localizer\.DoStr\("([\w\s]+)"\)'
        match = re.search(name_search_regex, file_contents)
        if not match:
            logger.warning(f"Could not find crafting table name for file {file_name}")
            return None
        name = match.group(1)

        name_id_search_regex = r'public partial class (\w+Object)'
        match = re.search(name_id_search_regex, file_contents)
        if not match:
            logger.warning(f"Could not find nameID for crafting table {name}")
            return None
        name_id = match.group(1)

        upgrade_module_search_regex = r'AllowPluginModules\(Tags = new\[] \{ "(\w+)'
        match = re.search(upgrade_module_search_regex, file_contents)
        upgrade_module = match.group(1) if match else None

        return CraftingTable(
            crafting_table_name=name,
            crafting_table_name_id=name_id,
            upgrade_module_tag=upgrade_module
        )
