-- n8n 워크플로우에서 사용할 샘플 테이블 생성
CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(20),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 테스트용 초기 데이터 삽입
INSERT INTO sensor_data (sensor_name, value, unit) VALUES
('temperature', 25.3, 'celsius'),
('humidity', 60.5, 'percent'),
('pressure', 1013.25, 'hPa');

-- n8n 워크플로우 로그 테이블
CREATE TABLE IF NOT EXISTS workflow_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workflow_name VARCHAR(200),
    status VARCHAR(50),
    message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
