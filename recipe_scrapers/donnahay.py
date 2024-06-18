# mypy: allow-untyped-defs

import warnings

from recipe_scrapers._grouping_utils import IngredientGroup

from ._abstract import AbstractScraper

BUG_REPORT_LINK = "https://github.com/hhursev/recipe-scrapers/issues"


def _field_not_provided_by_website_warning(host, field):
    class FieldNotProvidedByWebsiteWarning(Warning):
        pass

    message = (
        "{} doesn't seem to support the {} field. "
        "If you know this to be untrue for some recipe, please submit a bug report at {}"
    )

    warnings.warn(
        message.format(host, field, BUG_REPORT_LINK),
        category=FieldNotProvidedByWebsiteWarning,
    )


class DonnaHay(AbstractScraper):
    @classmethod
    def host(cls):
        return "donnahay.com.au"

    def author(self):
        return "Donna Hay"

    def site_name(self):
        return "Donna Hay"

    def title(self):
        return (
            self.soup.find("h1", class_="text-center recipe-title__mobile")
            .getText()
            .upper()
        )

    def yields(self):
        div = self.soup.find("div", class_="col-sm-6 method")
        instructions = div.findAll("li")
        last_instruction = instructions[:-1]
        if last_instruction.find("b") is not None:
            return last_instruction.find("b").getText()
        else:
            array = last_instruction.getText().split(".")
            for entry in array:
                if "Serves" in entry:
                    if entry[0] == " ":
                        yield_ = entry.replace(" ", "", 1)
                    return yield_

    def image(self):
        div = self.soup.find("div", class_="image-frame recipes")
        if not div:
            return
        image = div.find("img")
        return image["src"]

    def ingredients(self):
        ingredient_element = self.soup.find("div", {"class": "ingredients"})

        ingredients = []
        for ingredient in ingredient_element.find_all("li"):
            ingredients.append(ingredient.text.replace("\xa0", " ").strip())

        return ingredients

    def ingredient_groups(self):
        ingredient_element = self.soup.find("div", {"class": "ingredients"})

        ingredient_group_elements = ingredient_element.find_all("ul")
        ingredient_group_names = ingredient_element.find_all("p")

        ingredient_groups = []
        for index, group in enumerate(ingredient_group_elements):

            ingredient_groups.append(
                IngredientGroup(
                    ingredients=[
                        ingredient.text.replace("\xa0", " ").strip()
                        for ingredient in group
                    ],
                    purpose=(
                        ingredient_group_names[index - 1]
                        .text.replace("\xa0", " ")
                        .strip()
                        if len(ingredient_groups) != 0
                        else None
                    ),
                ),
            )

        return ingredient_groups

    def instructions(self):
        div = self.soup.find("div", class_="col-sm-6 method")
        if not div:
            return
        instructions = div.find_all("li")
        for instruction in instructions:
            text = instruction.get_text(separator=" ", strip=True)
            if "Serves" in text:
                text = text.split("Serves", 1)[
                    0
                ].strip()  # Remove the sentence starting with Serves
            instruction.string = text
        return instructions

    def keywords(self):
        div = self.soup.find("div", class_="section text-left")
        tags = div.find_all("a")
        keywords = []
        for tag in tags:
            keywords.append(tag.getText())
        return keywords

    def total_time(self):
        _field_not_provided_by_website_warning(self.host(), "total_time")
        return None
