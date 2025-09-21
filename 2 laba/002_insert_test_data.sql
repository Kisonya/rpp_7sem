INSERT INTO users (username, email) VALUES
('ivan', 'ivan@example.com'),
('maria', 'maria@example.com'),
('petr', 'petr@example.com')
ON CONFLICT (username) DO NOTHING;

INSERT INTO orders (user_id, amount, status) VALUES
(1, 100.50, 'completed'),
(2, 250.75, 'pending'),
(3, 50.00, 'completed')
ON CONFLICT DO NOTHING;

SELECT 'Test data inserted successfully' as result;