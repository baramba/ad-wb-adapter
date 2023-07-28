from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthDataGetResponse")


@attr.s(auto_attribs=True)
class AuthDataGetResponse:
    """
    Attributes:
        wb_user_id (Union[Unset, int]):
        wb_supplier_id (Union[Unset, str]):
        wb_token_standart (Union[Unset, str]):
        wb_token_stat (Union[Unset, str]):
        wb_token_ad (Union[Unset, str]):
        wb_token_access (Union[Unset, str]):
    """

    wb_user_id: Union[Unset, int] = UNSET
    wb_supplier_id: Union[Unset, str] = UNSET
    wb_token_standart: Union[Unset, str] = UNSET
    wb_token_stat: Union[Unset, str] = UNSET
    wb_token_ad: Union[Unset, str] = UNSET
    wb_token_access: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        wb_user_id = self.wb_user_id
        wb_supplier_id = self.wb_supplier_id
        wb_token_standart = self.wb_token_standart
        wb_token_stat = self.wb_token_stat
        wb_token_ad = self.wb_token_ad
        wb_token_access = self.wb_token_access

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if wb_user_id is not UNSET:
            field_dict["wb_user_id"] = wb_user_id
        if wb_supplier_id is not UNSET:
            field_dict["wb_supplier_id"] = wb_supplier_id
        if wb_token_standart is not UNSET:
            field_dict["wb_token_standart"] = wb_token_standart
        if wb_token_stat is not UNSET:
            field_dict["wb_token_stat"] = wb_token_stat
        if wb_token_ad is not UNSET:
            field_dict["wb_token_ad"] = wb_token_ad
        if wb_token_access is not UNSET:
            field_dict["wb_token_access"] = wb_token_access

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        wb_user_id = d.pop("wb_user_id", UNSET)

        wb_supplier_id = d.pop("wb_supplier_id", UNSET)

        wb_token_standart = d.pop("wb_token_standart", UNSET)

        wb_token_stat = d.pop("wb_token_stat", UNSET)

        wb_token_ad = d.pop("wb_token_ad", UNSET)

        wb_token_access = d.pop("wb_token_access", UNSET)

        auth_data_get_response = cls(
            wb_user_id=wb_user_id,
            wb_supplier_id=wb_supplier_id,
            wb_token_standart=wb_token_standart,
            wb_token_stat=wb_token_stat,
            wb_token_ad=wb_token_ad,
            wb_token_access=wb_token_access,
        )

        auth_data_get_response.additional_properties = d
        return auth_data_get_response

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
