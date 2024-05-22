

SET SERVEROUTPUT ON SIZE 1000000;

DECLARE
    -- 테이블 이름을 저장할 변수 선언
    v_table_name VARCHAR2(50);

    -- 커서 선언: 접두사가 'RBS_'이고, 예외 테이블이 아닌 테이블 목록
    CURSOR c_tables IS
        SELECT table_name FROM all_tables
        WHERE table_name LIKE 'RBS\_%' ESCAPE '\'
        AND table_name NOT IN ('RBS_OPTION_INFO', 'RBS_OPTION_INFO_LANG')
        AND owner = 'TARGET_SCHEMA_NAME'; -- 운영 DB의 스키마 이름으로 변경

BEGIN
    -- 외래 키 제약 조건 해제
    FOR r_constraint IN (SELECT constraint_name, table_name FROM all_constraints WHERE constraint_type = 'R' AND table_name LIKE 'RBS\_%' ESCAPE '\' AND owner = 'TARGET_SCHEMA_NAME')
    LOOP
        EXECUTE IMMEDIATE 'ALTER TABLE ' || r_constraint.table_name || ' DROP CONSTRAINT ' || r_constraint.constraint_name;
        DBMS_OUTPUT.PUT_LINE('Dropped constraint from ' || r_constraint.table_name);
    END LOOP;

    -- 테이블 데이터 삭제
    FOR r_table IN c_tables LOOP
        EXECUTE IMMEDIATE 'TRUNCATE TABLE ' || r_table.table_name;
        DBMS_OUTPUT.PUT_LINE('Truncated table ' || r_table.table_name);
    END LOOP;

    -- 개발 DB에서 운영 DB로 데이터를 이관
    FOR r_table IN c_tables LOOP
        EXECUTE IMMEDIATE 'INSERT INTO ' || r_table.table_name || ' SELECT * FROM ' || r_table.table_name || '@DBLINK_PKNUDEV01_UNI';
        DBMS_OUTPUT.PUT_LINE('Inserted data into ' || r_table.table_name);
    END LOOP;

    -- 외래 키 제약 조건 재적용
    FOR r_constraint IN (SELECT constraint_name, table_name FROM all_constraints WHERE constraint_type = 'R' AND table_name LIKE 'RBS\_%' ESCAPE '\' AND owner = 'TARGET_SCHEMA_NAME')
    LOOP
        EXECUTE IMMEDIATE 'ALTER TABLE ' || r_constraint.table_name || ' ADD CONSTRAINT ' || r_constraint.constraint_name || ' FOREIGN KEY (...) REFERENCES ...'; -- 외래키 상세 조건 추가
        DBMS_OUTPUT.PUT_LINE('Reapplied constraint to ' || r_constraint.table_name);
    END LOOP;
END;
/
