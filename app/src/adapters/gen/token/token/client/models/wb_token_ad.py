from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="WbTokenAd")


@attr.s(auto_attribs=True)
class WbTokenAd:
    """
    Attributes:
        wb_token_ad (str):
    """

    wb_token_ad: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        wb_token_ad = self.wb_token_ad

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "wb_token_ad": wb_token_ad,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        wb_token_ad = d.pop("wb_token_ad")

        wb_token_ad = cls(
            wb_token_ad=wb_token_ad,
        )

        wb_token_ad.additional_properties = d
        return wb_token_ad  # type: ignore [no-any-return]

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
