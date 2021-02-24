from datetime import datetime, timedelta
from requests import Session
from xml.etree import ElementTree
from dataclasses import dataclass


@dataclass
class ListParams:
    """
    region_code: 지역 코드. 인천은 28.
    status: 상태. "전체", "공고중", "접수중", "접수마감", "정정공고중" 중 하나.
    period: 검색 기간. 60이면 오늘부터 60일 전까지의 기간.
    """
    region_code: int = 28
    status: str = '공고중'
    period: int = 62


@dataclass
class DetailsParams:
    """
    item_id: 공고 id.
    """
    item_id: int


class LHCrawler:
    """
    apply.lh.or.kr의 분양/임대 공고를 긁어옵니다.
    """
    # 검색 결과 리스트를 가져올 때에 씁니다.
    request_list_url = 'https://apply.lh.or.kr/lhCmcNoSessionAdapter.lh?serviceID=OCMC_LCC_SIL_SILSNOT_L0001'
    request_list_payload_template = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Root xmlns="http://www.nexacroplatform.com/platform/dataset">
            <Dataset id="dsSch">
                <ColumnInfo>
                    <Column id="PAN_NM" type="STRING" size="256"  />
                    <Column id="CNP_CD" type="STRING" size="256"  />
                    <Column id="PG_SZ" type="STRING" size="256"  />
                    <Column id="PAGE" type="STRING" size="256"  />
                    <Column id="CS_CD" type="STRING" size="256"  />
                    <Column id="PAN_ST_DT" type="STRING" size="256"  />
                    <Column id="PAN_ED_DT" type="STRING" size="256"  />
                    <Column id="CLSG_ST_DT" type="STRING" size="256"  />
                    <Column id="CLSG_ED_DT" type="STRING" size="256"  />
                    <Column id="UPP_AIS_TP_CD" type="STRING" size="256"  />
                    <Column id="PAN_SS" type="STRING" size="256"  />
                    <Column id="AIS_TP_CD" type="STRING" size="256"  />
                    <Column id="PREVIEW" type="STRING" size="256"  />
                    <Column id="SCH_TY" type="STRING" size="256"  />
                    <Column id="SCH_ARA" type="STRING" size="256"  />
                    <Column id="SCH_PAN_SS" type="STRING" size="256"  />
                    <Column id="AIS_TP_CD_INT" type="STRING" size="256"  />
                    <Column id="MVIN_QF" type="STRING" size="256"  />
                </ColumnInfo>
                <Rows>
                    <Row>
                        <Col id="CNP_CD">__REGION__</Col>
                        <Col id="PG_SZ">50</Col>
                        <Col id="PAGE">1</Col>
                        <Col id="CS_CD">CNP_CD</Col>
                        <Col id="PAN_ST_DT">__START_DATE__</Col>
                        <Col id="PAN_ED_DT">__END_DATE__</Col>
                        <Col id="CLSG_ST_DT" />
                        <Col id="CLSG_ED_DT" />
                        <Col id="UPP_AIS_TP_CD">06</Col>
                        <Col id="PAN_SS">__STATUS__</Col>
                        <Col id="AIS_TP_CD">07</Col>
                        <Col id="PREVIEW">N</Col>
                        <Col id="SCH_TY">0</Col>
                        <Col id="SCH_ARA">__REGION__</Col>
                        <Col id="SCH_PAN_SS">1</Col>
                        <Col id="AIS_TP_CD_INT" />
                        <Col id="MVIN_QF" />
                    </Row>
                </Rows>
            </Dataset>
        </Root>
    """

    # 공고 상세 정보를 가져올 때에 씁니다.
    request_detail_url = 'https://apply.lh.or.kr/lhCmcNoSessionAdapter.lh?serviceID=OCMC_LCC_SIL_SILSNOT_R0006'
    request_detail_payload_template = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Root xmlns="http://www.nexacroplatform.com/platform/dataset">
            <Dataset id="dsSch">
                <ColumnInfo>
                    <Column id="PAN_ID" type="STRING" size="256"  />
                    <Column id="CCR_CNNT_SYS_DS_CD" type="STRING" size="256"  />
                    <Column id="PREVIEW" type="STRING" size="256"  />
                </ColumnInfo>
                <Rows>
                    <Row>
                        <Col id="PAN_ID">__ITEM_ID__</Col>
                        <Col id="CCR_CNNT_SYS_DS_CD">03</Col>
                    </Row>
                </Rows>
            </Dataset>
        </Root>
    """

    def __init__(self):
        # 앞으로 재활용할 Session입니다.
        self._session = Session()

    ################################
    # 리스트 구하기
    ################################
    def collect_list(self, params: ListParams):
        payload = self.request_list_payload_template\
            .replace('__REGION__', str(params.region_code))\
            .replace('__STATUS__', params.status)\
            .replace('__START_DATE__', self._get_date_string(-params.period))\
            .replace('__END_DATE__', self._get_date_string(0)) \
            .strip()  # 공백으로 시작하면 서버가 싫어합니다.

        result = self._session.post(
            url=self.request_list_url,
            data=payload.encode('utf-8'),
            headers={'Content-Type': 'text/xml; charset=utf-8'}
        ).text

        return self._parse_list_response_xml_to_list_of_dicts(result)

    def _get_date_string(self, delta_date: int = 0):
        f"""
        @{delta_date}일 전의 날짜를 YYYYmmdd 포맷으로 구합니다.
        
        :param delta_date: 오늘로부터의 날짜 차이. 과거는 음수, 미래는 양수입니다.
        :return: YYYYmmdd 포맷의 날짜 스트링
        """
        the_date = datetime.now() + timedelta(days=delta_date)

        return the_date.strftime("%Y%m%d")

    def _parse_list_response_xml_to_list_of_dicts(self, xml_string: str):
        """
        주어진 공고 리스트 XML 응답을 받아 dict의 list로 만들어 반환합니다.

        :param xml_string: 주어진 XML 응답.
        :return: dict의 list.
        """
        tree = ElementTree.fromstring(xml_string)

        ns = {'d': 'http://www.nexacro.com/platform/dataset'}
        rows = tree.findall("./d:Dataset[@id='dsList']/d:Rows/d:Row", ns)

        return [
            {col.attrib['id']: col.text for col in row.findall('d:Col', ns)}
            for row in rows
        ]

    ################################
    # 상세정보 구하기
    ################################
    def collect_details(self, params: DetailsParams):
        payload = self.request_detail_payload_template\
            .replace('__ITEM_ID__', str(params.item_id))\
            .strip()  # 공백은 서버가 토해요 ㅜ

        result = self._session.post(
            url=self.request_detail_url,
            data=payload.encode('utf-8'),
            headers={'Content-Type': 'text/xml; charset=utf-8'}
        ).text

        return self._parse_details_response_xml_to_list_of_dict(result)

    def _parse_details_response_xml_to_list_of_dict(self, xml_string: str):
        """
        주어진 공고 상세 XML 응답을 받아 dict의 list로 만들어 반환합니다.
        모든 Dataset의 Row들이 하나의 list로 flat하게 합쳐집니다.

        :param xml_string: 주어진 XML 응답.
        :return: dict의 list.
        """
        tree = ElementTree.fromstring(xml_string)

        ns = {'d': 'http://www.nexacro.com/platform/dataset'}
        all_rows = tree.findall("./d:Dataset/d:Rows/d:Row", ns)

        return [
            {col.attrib['id']: col.text for col in row.findall('d:Col', ns)}
            for row in all_rows
        ]

    ################################
    # 공고문 PDF 링크 구하기
    ################################
    def collect_pdf_link(self, params: DetailsParams):
        all_detail_rows = self.collect_details(params)
        filtered_rows = filter(
            lambda row: 'SL_PAN_AHFL_DS_CD_NM' in row and row['SL_PAN_AHFL_DS_CD_NM'] == '공고문(PDF)',
            all_detail_rows
        )

        pdf_row = next(iter(filtered_rows), None)
        file_id = pdf_row['CMN_AHFL_SN']

        return f'https://apply.lh.or.kr/fileDownAdapter.lh?fileid={file_id}'

