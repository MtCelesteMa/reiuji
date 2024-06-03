"""Component Catalogs for Reiuji."""

import pydantic


class Catalog[E](pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    catalog: dict[str, dict[str, E]]

    def __getitem__(self, index: tuple[str, str]) -> E:
        """Get the item from the catalog using the specified index.

        Args:
            index (tuple[str, str]): The index of the item in the catalog. The first element of the tuple represents the key of the outer dictionary, and the second element represents the key of the inner dictionary.

        Returns:
            E: The item from the catalog at the specified index.
        """
        return self.catalog[index[0]][index[1]]
    
    def __setitem__(self, index: tuple[str, str], value: E) -> None:
        """Set the value at the specified index in the catalog.

        Args:
            index (tuple[str, str]): The index of the item in the catalog. The first element of the tuple represents the key of the outer dictionary, and the second element represents the key of the inner dictionary.
            value (E): The value to set at the specified index.

        Returns:
            None: This function does not return anything.
        """
        if index[0] not in self.catalog:
            self.catalog[index[0]] = dict()
        self.catalog[index[0]][index[1]] = value
    
    def as_list(self) -> list[list[E]]:
        """Returns a nested list representation of the catalog.

        This method iterates over the keys in the catalog dictionary and for each key, it retrieves the corresponding value, which is another dictionary. It then iterates over the keys in this inner dictionary and retrieves the corresponding values. These values are then collected into a nested list.

        Returns:
            list[list[E]]: A nested list representation of the catalog.
        """
        return [[self.catalog[key][subkey] for subkey in self.catalog[key]] for key in self.catalog]
    
    
