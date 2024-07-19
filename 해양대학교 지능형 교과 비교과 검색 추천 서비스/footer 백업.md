

```
	<c:if test="${!empty loginVO.memberId }">
	<jsp:include page = "./satisfaction.jsp" flush = "false"/>
	</c:if>
	<!-- footer -->
	<footer>
        <button class="goTop_btn d-flex justify-content-center align-items-center d-lg-none"><img src="../images/arr_top_footer.png" alt="위로가기버튼" class="d-block"/></button>
		<ul class="footer_1 d-flex flex-row justify-content-center align-items-center gap-4 mb-1">
			<li><a href="#" title="개인정보처리방침">개인정보처리방침</a></li>
			<li><a href="#" title="이용약관">이용약관</a></li>
			<li><a href="#" title="이메일주소무단수집거부">이메일주소무단수집거부</a></li>
			<li><a href="#" title="오류신고">오류신고</a></li>
		</ul>
		<div class="footer_2">
			<address class="d-block lh-sm">${siteInfo.site_addr }<span>TEL : ${siteInfo.site_phone } / FAX : ${siteInfo.site_fax }</span><br>
			${siteInfo.site_copyright }</address>
		</div>
    </footer>
	<!-- //footer -->
	<%@ include file="../../../include/login_check.jsp"%>

```