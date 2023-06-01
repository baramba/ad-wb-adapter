from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.about_about_get_response_about_about_get_additional_property import (
        AboutAboutGetResponseAboutAboutGetAdditionalProperty,
    )


T = TypeVar("T", bound="AboutAboutGetResponseAboutAboutGet")


@attr.s(auto_attribs=True)
class AboutAboutGetResponseAboutAboutGet:
    """ """

    additional_properties: Dict[str, "AboutAboutGetResponseAboutAboutGetAdditionalProperty"] = attr.ib(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        pass

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.about_about_get_response_about_about_get_additional_property import (
            AboutAboutGetResponseAboutAboutGetAdditionalProperty,
        )

        d = src_dict.copy()
        about_about_get_response_about_about_get = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = AboutAboutGetResponseAboutAboutGetAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        about_about_get_response_about_about_get.additional_properties = additional_properties
        return about_about_get_response_about_about_get

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "AboutAboutGetResponseAboutAboutGetAdditionalProperty":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "AboutAboutGetResponseAboutAboutGetAdditionalProperty") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
