from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="AuthDataGetResponse")


@attr.s(auto_attribs=True)
class AuthDataGetResponse:
    """
    Attributes:
        wb_user_id (int):
        wb_supplier_id (str):
        wb_token_access (str):
    """

    wb_user_id: int
    wb_supplier_id: str
    wb_token_access: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        wb_user_id = self.wb_user_id
        wb_supplier_id = self.wb_supplier_id
        wb_token_access = self.wb_token_access

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "wb_user_id": wb_user_id,
                "wb_supplier_id": wb_supplier_id,
                "wb_token_access": wb_token_access,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        wb_user_id = d.pop("wb_user_id")

        wb_supplier_id = d.pop("wb_supplier_id")

        wb_token_access = d.pop("wb_token_access")

        auth_data_get_response = cls(
            wb_user_id=wb_user_id,
            wb_supplier_id=wb_supplier_id,
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
