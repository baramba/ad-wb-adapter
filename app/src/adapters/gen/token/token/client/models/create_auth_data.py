from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateAuthData")


@attr.s(auto_attribs=True)
class CreateAuthData:
    """
    Attributes:
        wb_user_id (int):
        wb_supplier_id (str):
        wb_token_ad (str):
        wb_token_refresh (str):
        wb_token_standart (Union[Unset, str]):
        wb_token_stat (Union[Unset, str]):
    """

    wb_user_id: int
    wb_supplier_id: str
    wb_token_ad: str
    wb_token_refresh: str
    wb_token_standart: Union[Unset, str] = UNSET
    wb_token_stat: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        wb_user_id = self.wb_user_id
        wb_supplier_id = self.wb_supplier_id
        wb_token_ad = self.wb_token_ad
        wb_token_refresh = self.wb_token_refresh
        wb_token_standart = self.wb_token_standart
        wb_token_stat = self.wb_token_stat

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "wb_user_id": wb_user_id,
                "wb_supplier_id": wb_supplier_id,
                "wb_token_ad": wb_token_ad,
                "wb_token_refresh": wb_token_refresh,
            }
        )
        if wb_token_standart is not UNSET:
            field_dict["wb_token_standart"] = wb_token_standart
        if wb_token_stat is not UNSET:
            field_dict["wb_token_stat"] = wb_token_stat

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        wb_user_id = d.pop("wb_user_id")

        wb_supplier_id = d.pop("wb_supplier_id")

        wb_token_ad = d.pop("wb_token_ad")

        wb_token_refresh = d.pop("wb_token_refresh")

        wb_token_standart = d.pop("wb_token_standart", UNSET)

        wb_token_stat = d.pop("wb_token_stat", UNSET)

        create_auth_data = cls(
            wb_user_id=wb_user_id,
            wb_supplier_id=wb_supplier_id,
            wb_token_ad=wb_token_ad,
            wb_token_refresh=wb_token_refresh,
            wb_token_standart=wb_token_standart,
            wb_token_stat=wb_token_stat,
        )

        create_auth_data.additional_properties = d
        return create_auth_data

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
