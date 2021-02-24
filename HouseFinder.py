from datetime import datetime, timedelta
from requests import Session
from xml.etree import ElementTree


class HouseFinder:
    request_url = 'https://apply.lh.or.kr/lhCmcNoSessionAdapter.lh?serviceID=OCMC_LCC_SIL_SILSNOT_L0001'
    request_payload_template = """
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

    def __init__(self, region_code: int = 28, status: str = '공고중', period: int = 60):
        """
        :param region_code: 지역 코드. 인천은 28.
        :param status: 상태. "전체", "공고중", "접수중", "접수마감", "정정공고중" 중 하나.
        :param period: 검색 기간. 60이면 오늘부터 60일 전까지의 기간.
        """
        self._region_code = region_code
        self._status = status
        self._period = period

        # 앞으로 재활용할 Session입니다.
        self._session = Session()

    def search(self):
        result = self._request()

        return self._parse_xml(result)

    def _row_to_dict(self, row):
        columns = row.findall('')
        pass

    def _request(self):
        response = self._session.post(
            url=self.request_url,
            data=self._get_request_payload().encode('utf-8'),
            headers={'Content-Type': 'text/xml; charset=utf-8'}
        )

        return response.text

    def _get_request_payload(self):
        return self.request_payload_template\
            .replace('__REGION__', str(self._region_code))\
            .replace('__STATUS__', self._status)\
            .replace('__START_DATE__', self._get_date_string(-self._period))\
            .replace('__END_DATE__', self._get_date_string(0)) \
            .strip()  # 공백으로 시작하면 서버가 싫어합니다.

    def _get_date_string(self, delta_date: int = 0):
        f"""
        @{delta_date}일 전의 날짜를 YYYYmmdd 포맷으로 구합니다.
        :param delta_date: 오늘로부터의 날짜 차이. 과거는 음수, 미래는 양수입니다.
        :return: YYYYmmdd 포맷의 날짜 스트링
        """
        the_date = datetime.now() + timedelta(days=delta_date)

        return the_date.strftime("%Y%m%d")

    def _parse_xml(self, xml_string):
        """
        주어진 XML 응답을 받아 dict의 list로 만들어 반환합니다.
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
