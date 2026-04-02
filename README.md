# n8n + MySQL Docker Compose

Docker Compose를 이용한 n8n 워크플로우 자동화 + MySQL 데이터베이스 연동 프로젝트

## 아키텍처

```
┌─────────────────────────────────────────┐
│           Docker Network (n8n_network)  │
│                                         │
│  ┌──────────────┐    ┌───────────────┐  │
│  │   n8n:5678   │───▶│  MySQL:3306   │  │
│  │  (워크플로우) │    │  (데이터베이스)│  │
│  └──────┬───────┘    └───────┬───────┘  │
│         │                   │           │
│    n8n_data              mysql_data     │
│    (볼륨)                  (볼륨)        │
└─────────────────────────────────────────┘
```

## 구성 요소

| 서비스 | 이미지 | 포트 | 역할 |
|--------|--------|------|------|
| n8n | n8nio/n8n:latest | 5678 | 워크플로우 자동화 엔진 |
| mysql | mysql:8.0 | 3306 | 백엔드 데이터베이스 |

## 볼륨

- `mysql_data`: MySQL 데이터 영구 저장
- `n8n_data`: n8n 설정 및 자격증명 영구 저장

## 빠른 시작

### 1. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 비밀번호 설정
```

### 2. 컨테이너 실행
```bash
docker-compose up -d
```

### 3. 상태 확인
```bash
docker-compose ps
docker-compose logs -f
```

### 4. n8n 접속
브라우저에서 http://localhost:5678 접속
- ID: admin
- PW: admin1234 (`.env`에서 변경 가능)

### 5. 중지 및 정리
```bash
# 컨테이너 중지
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v
```

## n8n에서 MySQL 트리거 워크플로우 설정 방법

### MySQL 크레덴셜 등록
1. n8n 접속 → **Settings > Credentials**
2. **Add Credential** → `MySQL` 선택
3. 입력값:
   - Host: `mysql` (컨테이너 이름)
   - Port: `3306`
   - Database: `n8n_db`
   - User: `n8n_user`
   - Password: `n8n_password`

### 샘플 워크플로우: 주기적으로 MySQL에 데이터 삽입

1. **Schedule Trigger** 노드 추가 (예: 매 1분마다)
2. **MySQL** 노드 추가
   - Operation: `Execute Query`
   - Query:
     ```sql
     INSERT INTO workflow_log (workflow_name, status, message)
     VALUES ('auto_trigger', 'success', 'Triggered at {{$now}}');
     ```
3. 노드 연결 후 **Activate** 토글 ON

### MySQL 데이터 확인
```bash
docker exec -it n8n_mysql mysql -u n8n_user -pn8n_password n8n_db

# 데이터 조회
SELECT * FROM workflow_log;
SELECT * FROM sensor_data;
```

## 데이터베이스 스키마

### sensor_data
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INT AUTO_INCREMENT | 기본키 |
| sensor_name | VARCHAR(100) | 센서 이름 |
| value | FLOAT | 측정값 |
| unit | VARCHAR(20) | 단위 |
| recorded_at | TIMESTAMP | 기록 시간 |

### workflow_log
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INT AUTO_INCREMENT | 기본키 |
| workflow_name | VARCHAR(200) | 워크플로우 이름 |
| status | VARCHAR(50) | 실행 상태 |
| message | TEXT | 로그 메시지 |
| executed_at | TIMESTAMP | 실행 시간 |

## 트러블슈팅

**n8n이 MySQL에 연결 안 될 때:**
```bash
# MySQL 헬스체크 확인
docker-compose ps
# mysql 컨테이너가 healthy 상태인지 확인 후 n8n 재시작
docker-compose restart n8n
```

**포트 충돌 시:**
- `docker-compose.yml`에서 `ports` 섹션의 호스트 포트 변경
