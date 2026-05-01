-- =============================================================================
-- Seed script: chat-practice-service RBAC
-- =============================================================================
-- Stable GUIDs (must match alembic/versions/20260429_0003_seed_chat_practice_service.py)
--
--   Service ID :  c0000003-0000-0000-0000-000000000001
--   User role  :  c0000003-0000-0000-0000-000000000011
--   Admin role :  c0000003-0000-0000-0000-000000000012
--
-- Usage:
--   sqlcmd -S <server> -d <db> -U <user> -P <password> -i seed_chat_practice_service.sql
--   Set @admin_email to the actual admin e-mail before running if different from the default.
-- =============================================================================

DECLARE @admin_email NVARCHAR(256) = 'admin@email.com';
DECLARE @admin_id UNIQUEIDENTIFIER;

-- ---- Service ----
IF NOT EXISTS (SELECT 1 FROM services WHERE id = 'c0000003-0000-0000-0000-000000000001')
BEGIN
    INSERT INTO services (id, name, description, is_active, url, port)
    VALUES (
        'c0000003-0000-0000-0000-000000000001',
        'chat-practice-service',
        'LanguageApp Chat Practice API — conversational English with live feedback',
        1, NULL, NULL
    );
END

-- ---- Roles ----
IF NOT EXISTS (SELECT 1 FROM roles WHERE id = 'c0000003-0000-0000-0000-000000000011')
BEGIN
    INSERT INTO roles (id, service_id, name, description, is_active)
    VALUES (
        'c0000003-0000-0000-0000-000000000011',
        'c0000003-0000-0000-0000-000000000001',
        'chat-practice-user',
        'Can use the Chat Practice API',
        1
    );
END

IF NOT EXISTS (SELECT 1 FROM roles WHERE id = 'c0000003-0000-0000-0000-000000000012')
BEGIN
    INSERT INTO roles (id, service_id, name, description, is_active)
    VALUES (
        'c0000003-0000-0000-0000-000000000012',
        'c0000003-0000-0000-0000-000000000001',
        'admin',
        'Administrator for Chat Practice service',
        1
    );
END

-- ---- Assign to admin user ----
SELECT @admin_id = id FROM users WHERE email = @admin_email AND COALESCE(is_deleted, 0) = 0;

IF @admin_id IS NOT NULL
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM user_roles
        WHERE user_id = @admin_id AND role_id = 'c0000003-0000-0000-0000-000000000011'
    )
        INSERT INTO user_roles (id, user_id, role_id)
        VALUES (NEWID(), @admin_id, 'c0000003-0000-0000-0000-000000000011');

    IF NOT EXISTS (
        SELECT 1 FROM user_roles
        WHERE user_id = @admin_id AND role_id = 'c0000003-0000-0000-0000-000000000012'
    )
        INSERT INTO user_roles (id, user_id, role_id)
        VALUES (NEWID(), @admin_id, 'c0000003-0000-0000-0000-000000000012');

    IF NOT EXISTS (
        SELECT 1 FROM user_services
        WHERE user_id = @admin_id AND service_id = 'c0000003-0000-0000-0000-000000000001'
    )
        INSERT INTO user_services (id, user_id, service_id)
        VALUES (NEWID(), @admin_id, 'c0000003-0000-0000-0000-000000000001');
END
ELSE
    PRINT 'Admin user not found — skipping role/service assignment.';
