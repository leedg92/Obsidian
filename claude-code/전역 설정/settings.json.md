# ~/.claude/settings.json

Claude Code 하네스 설정 파일. `permissions`(허용 커맨드), `hooks`(SessionStart/PreToolUse), `language`, `enabledPlugins` 등을 정의.

## 원본 위치
`~/.claude/settings.json`

## 주요 구성
- **permissions.allow**: Bash 허용 명령 화이트리스트 (누적 승인 이력)
- **hooks.SessionStart(compact)**: `/compact` 후 핵심 규칙 재주입
- **hooks.PreToolUse(Bash)**: 위험 명령(rm -rf, --force, --hard, --no-verify, drop database/table) 감지 경고
- **enabledPlugins**: `claude-mem@thedotmack`
- **language**: Korean

## 전체 내용

```json
{
  "permissions": {
    "allow": [
      "Bash(mkdir:*)",
      "Bash(grep:*)",
      "Bash(xargs cat:*)",
      "Bash(xargs ls:*)",
      "Bash(find /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/java -name \"*.java\" -exec grep -l \"websocket\\\\|stomp\\\\|sse\\\\|deferred\\\\|callable\" {} \\\\; 2>/dev/null | head -20)",
      "Bash(ls -la /mnt/d/workspace/bctrans_prod/api-bctrans/target/*.war 2>/dev/null)",
      "Bash(echo \"=== ALLCONE JAVA FILES IMPORTING BCTRANS ===\"\ngrep -r \"import.*bctrans\\\\|import.*bctrans\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/java/kr/co/chainportal/allconebctrans/allcone --include=\"*.java\" | grep -o \"^[^:]*\" | sort | uniq | head -30)",
      "Bash(echo \"=== ALLCONE JAVA FILES IMPORTING BCTRANS ===\"\ngrep -r \"import kr.co.chainportal.allconebctrans.bctrans\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/java/kr/co/chainportal/allconebctrans/allcone --include=\"*.java\" | cut -d: -f1 | sort | uniq)",
      "Bash(grep -r \"bctrans\\\\.\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/java/kr/co/chainportal/allconebctrans/allcone --include=\"*.java\" | cut -d: -f1 | sort | uniq | head -20)",
      "Bash(echo \"Checking for tb_b_truck_trans_odr access:\"\necho \"\"\necho \"ALLCONE mappers accessing tb_b_truck_trans_odr:\"\ngrep -l \"tb_b_truck_trans_odr\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/allcone/*/*Mapper.xml\n\necho \"\"\necho \"BCTRANS mappers accessing tb_b_truck_trans_odr:\"\ngrep -l \"tb_b_truck_trans_odr\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/bctrans/*/*Mapper.xml\n\necho \"\"\necho \"Checking container_transport_vbs tables:\"\necho \"ALLCONE accessing container_transport_vbs:\"\ngrep -l \"container_transport_vbs\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/allcone/*/*Mapper.xml\n\necho \"BCTRANS accessing container_transport_vbs:\"\ngrep -l \"container_transport_vbs\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/bctrans/*/*Mapper.xml)",
      "Bash(__NEW_LINE_a2ff4d00a0df189a__ echo:*)",
      "Bash(echo \"=== tb_b_truck_trans_odr ACCESS ANALYSIS ===\"\necho \"\"\necho \"ALLCONE mappers accessing tb_b_truck_trans_odr:\"\ngrep -l \"tb_b_truck_trans_odr\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/allcone/*/*.xml\n\necho \"\"\necho \"BCTRANS mappers accessing tb_b_truck_trans_odr:\"\ngrep -l \"tb_b_truck_trans_odr\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/bctrans/*/*.xml\n\necho \"\"\necho \"=== tb_b_tss_group_order_c ACCESS ANALYSIS ===\"\necho \"\"\necho \"ALLCONE mappers accessing tb_b_tss_group_order_c:\"\ngrep -l \"tb_b_tss_group_order_c\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/allcone/*/*.xml\n\necho \"\"\necho \"BCTRANS mappers accessing tb_b_tss_group_order_c:\"\ngrep -l \"tb_b_tss_group_order_c\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/bctrans/*/*.xml)",
      "Bash(echo \"=== CROSS-PACKAGE DEPENDENCIES IN ALLCONE ORDER SERVICES ===\"\ngrep -n \"import.*bctrans\" /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/java/kr/co/chainportal/allconebctrans/allcone/order/service/*.java)",
      "Bash(find /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources/mappers/mainDataSource/bctrans -name \"*.xml\" 2>/dev/null | sort)",
      "Bash(git fetch:*)",
      "Bash(git merge:*)",
      "Bash(git stash:*)",
      "Bash(git diff:*)",
      "Bash(git add:*)",
      "Bash(git reset:*)",
      "Bash(git log:*)",
      "Bash(git commit:*)",
      "Bash(git config:*)",
      "Bash(git push:*)",
      "Bash(git diff-tree:*)",
      "Bash(git checkout:*)",
      "Bash(codex --version 2>&1)",
      "Bash(codex --model gpt-5.4 --help 2>&1 | head -20)",
      "Bash(codex --model gpt-5.4 --quiet exec \"echo hello\" 2>&1 | head -20)",
      "Bash(codex --model gpt-5.4 exec \"say hello\" 2>&1 | head -20)",
      "Bash(codex exec:*)",
      "Bash(kill 193081 186542 186549 2>/dev/null; sleep 1; echo \"killed\")",
      "Bash(codex --model gpt-5.4 exec --full-auto \"이 프로젝트의 src/main/java/kr/co/chainportal/allconebctrans/invoke/ 패키지 안의 Java 파일들을 읽고, 각 파일의 JavaDoc 주석이 실제 코드 동작과 일치하는지 검증해줘. CRITICAL\\(주석이 코드와 다름\\) 이슈만 보고해. 결과를 .review-context/codex-review-invoke.json 에 JSON으로 저장해.\" 2>&1)",
      "Bash(codex --model gpt-5.4 exec --full-auto \"이 프로젝트의 src/main/java/kr/co/chainportal/allconebctrans/allcone/ 패키지 안의 Java 파일들을 읽고, 각 파일의 JavaDoc 주석이 실제 코드 동작과 일치하는지 검증해줘. CRITICAL\\(주석이 코드와 다름\\) 이슈만 보고해. 결과를 .review-context/codex-review-allcone.json 에 JSON으로 저장해.\" 2>&1)",
      "Bash(codex --model gpt-5.4 exec --full-auto \"이 프로젝트의 src/main/java/kr/co/chainportal/allconebctrans/common/ 패키지 안의 Java 파일들을 읽고, 각 파일의 JavaDoc 주석이 실제 코드 동작과 일치하는지 검증해줘. CRITICAL\\(주석이 코드와 다름\\) 이슈만 보고해. 결과를 .review-context/codex-review-common.json 에 JSON으로 저장해.\" 2>&1)",
      "Bash(codex --model gpt-5.4 exec --full-auto \"이 프로젝트의 src/main/java/kr/co/chainportal/allconebctrans/bctrans/auth/ 와 src/main/java/kr/co/chainportal/allconebctrans/bctrans/admin/ 와 src/main/java/kr/co/chainportal/allconebctrans/bctrans/external/ 패키지 안의 Java 파일들을 읽고, 각 파일의 JavaDoc 주석이 실제 코드 동작과 일치하는지 검증해줘. CRITICAL\\(주석이 코드와 다름\\) 이슈만 보고해. 결과를 .review-context/codex-review-bctrans-1.json 에 JSON으로 저장해.\" 2>&1)",
      "Bash(codex --model gpt-5.4 exec --full-auto \"이 프로젝트의 src/main/java/kr/co/chainportal/allconebctrans/bctrans/group/ 패키지 안의 Java 파일들을 읽고, 각 파일의 JavaDoc 주석이 실제 코드 동작과 일치하는지 검증해줘. CRITICAL\\(주석이 코드와 다름\\) 이슈만 보고해. 결과를 .review-context/codex-review-bctrans-2.json 에 JSON으로 저장해.\" 2>&1)",
      "Bash(codex --model gpt-5.4 exec --full-auto \"이 프로젝트의 src/main/java/kr/co/chainportal/allconebctrans/bctrans/generalContainer/ 와 src/main/java/kr/co/chainportal/allconebctrans/bctrans/generalTrucker/ 와 src/main/java/kr/co/chainportal/allconebctrans/bctrans/common/ 와 src/main/java/kr/co/chainportal/allconebctrans/bctrans/vbs/ 패키지 안의 Java 파일들을 읽고, 각 파일의 JavaDoc 주석이 실제 코드 동작과 일치하는지 검증해줘. CRITICAL\\(주석이 코드와 다름\\) 이슈만 보고해. 결과를 .review-context/codex-review-bctrans-3.json 에 JSON으로 저장해.\" 2>&1)",
      "Bash(mvn javadoc:javadoc -Dshow=private -Dencoding=UTF-8 -DdocEncoding=UTF-8 -Dcharset=UTF-8 2>&1 | tail -50)",
      "Bash(mvn spring-boot:run -Dspring-boot.run.profiles=allconedev 2>&1 | head -150)",
      "Bash(sudo mkdir:*)",
      "Bash(mvn spring-boot:run -Dspring-boot.run.profiles=allconedev 2>&1 | tail -80)",
      "Bash(pkill -f \"spring-boot:run\" 2>/dev/null; echo \"stopped\")",
      "Bash(nc -zv 133.186.222.171 23306 -w 5 2>&1)",
      "Bash(pkill -f \"spring-boot:run\" 2>/dev/null; sleep 2; mvn spring-boot:run -Dspring-boot.run.profiles=allconedev 2>&1 | head -200)",
      "Bash(pkill -f \"spring-boot:run\" 2>/dev/null; pkill -f \"allconebctrans\" 2>/dev/null; sleep 2; ps aux | grep -E \"spring-boot|allconebctrans\" | grep -v grep || echo \"clean\")",
      "Bash(which python3:*)",
      "Bash(pip3 install:*)",
      "Bash(python3:*)",
      "Bash(curl:*)",
      "Read(//logs/**)",
      "Read(//logs/bctrans/**)",
      "WebSearch",
      "Bash(git branch:*)",
      "Bash(find src/main/resources -name *.xml -path *mapper*)",
      "Bash(mvn compile:*)",
      "mcp__plugin_claude-mem_mcp-search__search",
      "mcp__plugin_claude-mem_mcp-search__get_observations",
      "Bash(find /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/java -type f -name \"*.java\" -exec grep -l \"userId\\\\|UserId\" {})",
      "Bash(find /mnt/d/workspace/bctrans_prod/api-bctrans/src/main/resources -name \"*.xml\" -type f -exec grep -l \"userId\\\\|LGN_ID\\\\|MBR_NM\\\\|MBR_TELNO\" {})",
      "Bash(./mvnw compile:*)",
      "Bash(perl:*)",
      "Bash(xxd docs/vbs-flow/02_reservation-result.md)",
      "Bash(mv 00_invoke-alarm-entry.md invoke-alarm-entry.md)",
      "Bash(mv 01_copino-verification-result.md CopinoVerificationResult.md)",
      "Bash(mv 02_reservation-result.md ReservationResult.md)",
      "Bash(mv 03_remove-copino.md RemoveCopino.md)",
      "Bash(mv 04_reefer-plug-inout.md ReeferPlugInOutResult.md)",
      "Bash(mv 01_copino.md CreateCopino.md)",
      "Bash(mv 02_terminal-event.md TerminalEvent.md)",
      "Bash(mv 03_cancel.md CancelOut.md)",
      "Bash(mv 04_group-order.md GroupOrder.md)",
      "Bash(for f:*)",
      "Bash(do sed:*)",
      "Bash(done)",
      "Bash(git status:*)",
      "Bash(ls /mnt/d/workspace/bctrans_prod/api-bctrans/*.md)"
    ],
    "defaultMode": "default"
  },
  "enabledPlugins": {
    "claude-mem@thedotmack": true
  },
  "language": "Korean",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[하네스] 컨텍스트 압축 후 핵심 규칙 재확인: (1) 람다/Stream/Optional 금지 → for문/if-else 사용. (2) 무조건 존댓말. (3) 선실행 금지 — 명시 요청만 실행. (4) 페르소나는 ~/.claude/personas/ 참조. (5) 도메인 지식: ~/.claude/projects/-mnt-d-workspace-bctrans-prod-api-bctrans/CLAUDE.md.'"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command // \"\"' | grep -qE 'rm -rf|--force([[:space:]]|$)|--hard|--no-verify|drop database|drop table' && echo '[하네스 경고] 위험 가능 명령 감지. 의도 재확인 필요.' >&2; exit 0"
          }
        ]
      }
    ]
  }
}
```
