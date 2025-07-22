from __future__ import annotations
import copy
from typing import Any, Dict, List, get_type_hints, get_origin, get_args, Literal
import dataclasses
from gradio.components.base import Component

def prop_meta(**kwargs) -> dataclasses.Field:
    """
    A helper function to create a dataclass field with Gradio-specific metadata.
    
    Returns:
        A dataclasses.Field instance with the provided metadata.
    """
    return dataclasses.field(metadata=kwargs)

class PropertySheet(Component):
    """
    A Gradio component that renders a dynamic UI from a Python dataclass instance.
    It allows for nested settings and automatically infers input types.
    """
    EVENTS = ["change", "input", "expand", "collapse"]

    def __init__(
        self, 
        value: Any | None = None, 
        *,  
        label: str | None = None,
        visible: bool = True,
        open: bool = True,
        elem_id: str | None = None,
        scale: int | None = None,
        width: int | str | None = None,
        height: int | str | None = None,
        min_width: int | None = None,
        container: bool = True,
        elem_classes: list[str] | str | None = None,
        **kwargs
    ):
        """
        Initializes the PropertySheet component.

        Args:
            value: The initial dataclass instance to render.
            label: The main label for the component, displayed in the accordion header.
            visible: If False, the component will be hidden.
            open: If False, the accordion will be collapsed by default.
            elem_id: An optional string that is assigned as the id of this component in the DOM.
            scale: The relative size of the component in its container.
            width: The width of the component in pixels.
            height: The maximum height of the component's content area in pixels before scrolling.
            min_width: The minimum width of the component in pixels.
            container: If True, wraps the component in a container with a background.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the DOM.
        """
        if value is not None and not dataclasses.is_dataclass(value):
            raise ValueError("Initial value must be a dataclass instance")
        
        # Store the current dataclass instance and its type.
        # These might be None if the component is initialized without a value.
        self._dataclass_value = copy.deepcopy(value) if value is not None else None
        self._dataclass_type = type(value) if dataclasses.is_dataclass(value) else None
        
        self.width = width
        self.height = height
        self.open = open
        
        super().__init__(
            label=label, visible=visible, elem_id=elem_id, scale=scale,
            min_width=min_width, container=container, elem_classes=elem_classes,
            value=self._dataclass_value, **kwargs
        )

    def _extract_prop_metadata(self, obj: Any, field: dataclasses.Field) -> Dict[str, Any]:
        """
        Inspects a dataclass field and extracts metadata for UI rendering.

        This function infers the appropriate frontend component (e.g., slider, checkbox)
        based on the field's type hint if not explicitly specified in the metadata.
        
        Args:
            obj: The dataclass instance containing the field.
            field: The dataclasses.Field object to inspect.
        Returns:
            A dictionary of metadata for the frontend to render a property control.
        """
        metadata = field.metadata.copy()
        metadata["name"] = field.name
        current_value = getattr(obj, field.name)
        metadata["value"] = current_value if current_value is not None else (field.default if field.default is not dataclasses.MISSING else None)
        metadata["label"] = metadata.get("label", field.name.replace("_", " ").capitalize())
        
        prop_type = get_type_hints(type(obj)).get(field.name)
        if "component" not in metadata:
            if metadata.get("component") == "colorpicker": pass
            elif get_origin(prop_type) is Literal: metadata["component"] = "dropdown"
            elif prop_type is bool: metadata["component"] = "checkbox"
            elif prop_type is int: metadata["component"] = "number_integer"
            elif prop_type is float: metadata["component"] = "number_float"
            else: metadata["component"] = "string"
        
        if metadata.get("component") == "dropdown":
            if get_origin(prop_type) is Literal:
                choices = list(get_args(prop_type))
                metadata["choices"] = choices
                if metadata["value"] not in choices:
                    metadata["value"] = choices[0] if choices else None
        return metadata

    def postprocess(self, value: Any) -> List[Dict[str, Any]]:
        """
        Converts the Python dataclass instance into a JSON schema for the frontend.

        Crucially, this method also acts as a "state guardian". When Gradio calls it
        with a valid dataclass (e.g., during a `gr.update` that makes the component visible),
        it synchronizes the component's internal state (`_dataclass_value` and `_dataclass_type`),
        ensuring the object is "rehydrated" and ready for `preprocess`.
        
        Args:
            value: The dataclass instance to process.
        Returns:
            A list representing the JSON schema for the frontend UI.
        """
        if dataclasses.is_dataclass(value):
            self._dataclass_value = copy.deepcopy(value)
            # Restore the dataclass type if it was lost (e.g., on re-initialization).
            if self._dataclass_type is None:
                self._dataclass_type = type(value)
        
        if value is None or not dataclasses.is_dataclass(value): 
            return []
            
        json_schema, root_properties = [], []
        for field in dataclasses.fields(value):
            field_type = get_type_hints(type(value)).get(field.name)
            field_is_dataclass = False
            try:
                if dataclasses.is_dataclass(field_type): field_is_dataclass = True
            except TypeError:
                field_is_dataclass = False

            if field_is_dataclass:
                group_obj, group_props = getattr(value, field.name), []
                for group_field in dataclasses.fields(group_obj):
                    group_props.append(self._extract_prop_metadata(group_obj, group_field))
                json_schema.append({"group_name": field.name.capitalize(), "properties": group_props})
            else:
                root_properties.append(self._extract_prop_metadata(value, field))
        
        if root_properties:
            json_schema.insert(0, {"group_name": "General", "properties": root_properties})

        return json_schema

    def preprocess(self, payload: Any) -> Any:
        """
        Processes the payload from the frontend to create an updated dataclass instance.

        This method is stateless regarding the instance value. It reconstructs the object
        from scratch using the `_dataclass_type` (which is reliably set by `postprocess`)
        and then applies the changes from the payload.
        
        Args:
            payload: The data received from the frontend, typically a list of property groups.
        Returns:
            A new, updated instance of the dataclass.
        """
        if payload is None:
            return None

        if self._dataclass_type is None:
            # This can happen if the component is used in a way that prevents postprocess
            # from ever being called with a valid value. Returning None is a safe fallback.
            return None
            
        # Create a new, default instance of the stored dataclass type.
        reconstructed_obj = self._dataclass_type()

        # Apply the values from the payload to the new instance.
        if isinstance(payload, list):
            for group in payload:
                for prop in group.get("properties", []):
                    prop_name = prop["name"]
                    new_value = prop["value"]
                    if hasattr(reconstructed_obj, prop_name):
                        setattr(reconstructed_obj, prop_name, new_value)
                    else:
                        # Handle nested dataclasses.
                        for f in dataclasses.fields(reconstructed_obj):
                            if dataclasses.is_dataclass(f.type):
                                group_obj = getattr(reconstructed_obj, f.name)
                                if hasattr(group_obj, prop_name):
                                    setattr(group_obj, prop_name, new_value)
                                    break
        elif isinstance(payload, dict):
            for key, new_value in payload.items():
                if hasattr(reconstructed_obj, key):
                    setattr(reconstructed_obj, key, new_value)
                else:
                    # Handle nested dataclasses for dict payloads.
                    for f in dataclasses.fields(reconstructed_obj):
                        if dataclasses.is_dataclass(f.type):
                            group_obj = getattr(reconstructed_obj, f.name)
                            if hasattr(group_obj, key):
                                setattr(group_obj, key, new_value)
                                break
        
        return reconstructed_obj
    
    def api_info(self) -> Dict[str, Any]:
        """
        Provides API information for the component for use in API docs.
        """
        return {"type": "object", "description": "A key-value dictionary of property settings."}

    def example_payload(self) -> Any:
        """
        Returns an example payload for the component's API.
        """
        return {"seed": 12345}