import httpx

from adapters.base import BaseAdapter, retry_ahttpx
import collections


class CampaignAdapter(BaseAdapter):

    @retry_ahttpx()
    async def post(
            self,
            url: str,
            headers: dict = None,
            cookies: dict = None,
            body: dict = None,
    ) -> httpx.Response:
        return await self._post(
            url=url,
            headers=headers,
            cookies=cookies,
            body=body,
        )

    @retry_ahttpx()
    async def put(
            self,
            url: str,
            headers: dict = None,
            cookies: dict = None,
            body: dict = None,
    ) -> httpx.Response:
        return await self._put(
            url=url,
            headers=headers,
            cookies=cookies,
            body=body,
        )

    @retry_ahttpx()
    async def get(
            self,
            url: str,
            headers: dict = None,
            cookies: dict = None,
            query: dict = None,
    ) -> httpx.Response:
        return await self._get(
            url=url,
            headers=headers,
            cookies=cookies,
            query=query,
        )

    async def get_subject_id(
            self,
            nms: int
    ) -> int:
        url = f'https://card.wb.ru/cards/detail?nm={nms}'
        result = await self.get(url=url)
        return result.json()['data']['products'][0]['subjectId']

    async def get_keyword(
            self,
            nms: int
    ) -> str:
        subject_id = await self.get_subject_id(nms=nms)

        url = 'https://cmp.wildberries.ru/backend/api/v2/search/supplier-subjects'
        result = await self.get(url=url)
        for item in result.json():
            if item['id'] == subject_id:
                return item['name']
        # todo raise error

    async def create_campaign(
            self,
            name: str,
            nms: list[int],
    ) -> int:
        kw_nms = collections.defaultdict(list)
        for kw, nms in [(await self.get_keyword(nms=item), item)
                        for item in nms]:
            kw_nms[kw].append(nms)

        url = 'https://cmp.wildberries.ru/backend/api/v2/search/save-ad'
        body = {'campaignName': name,
                'groups': [
                    {'nms': v, 'key_word': k}
                    for k, v in kw_nms.items()
                ]
                }
        result = await self.post(url=url, body=body)
        return result.json()['id']

    async def get_campaign_budget(
            self,
            id: int,
    ) -> dict:
        url = f'https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement'
        headers = {'Referer': f'https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}'}
        result = await self.get(url=url, headers=headers)
        return result.json()

    async def add_keywords_to_campaign(
            self,
            id: int,
            keywords: list,
    ):
        url = f'https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus'
        body = {'pluse': keywords}
        await self.post(url=url, body=body)

    async def add_amount_to_campaign_budget(
            self,
            id: int,
            amount: int,
    ):
        url = f'https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget/deposit'
        body = {'sum': amount, 'type': 1}
        await self.post(url=url, body=body)

    async def set_campaign_bet(
            self,
            id: int,
            bet: int,
    ):
        budget = await self.get_campaign_budget(id=id)
        url = f'https://cmp.wildberries.ru/backend/api/v2/search/{id}/save'
        for i in range(len(budget['place'])):
            budget['place'][i]['price'] = bet

        await self.put(url=url, body=budget)
