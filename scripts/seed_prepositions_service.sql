-- Seed prepositions-service for LanguageApp-PrepositionsSvc (stable GUIDs = Alembic 20260428_0002).
-- Run against IdentityDB. Set @AdminEmail to match your seed admin.

DECLARE @PrepositionsServiceId UNIQUEIDENTIFIER = 'c0000002-0000-0000-0000-000000000001';
DECLARE @RoleUserId UNIQUEIDENTIFIER = 'c0000002-0000-0000-0000-000000000011';
DECLARE @RoleAdminId UNIQUEIDENTIFIER = 'c0000002-0000-0000-0000-000000000012';
DECLARE @AdminEmail NVARCHAR(250) = N'admin@email.com';

IF NOT EXISTS (SELECT 1 FROM services WHERE id = @PrepositionsServiceId)
  INSERT INTO services (id, name, description, is_active, url, port)
  VALUES (@PrepositionsServiceId, N'prepositions-service', N'LanguageApp Prepositions practice API', 1, NULL, NULL);

IF NOT EXISTS (SELECT 1 FROM roles WHERE id = @RoleUserId)
  INSERT INTO roles (id, service_id, name, description, is_active)
  VALUES (@RoleUserId, @PrepositionsServiceId, N'prepositions-user', N'Can use the Prepositions practice API', 1);

IF NOT EXISTS (SELECT 1 FROM roles WHERE id = @RoleAdminId)
  INSERT INTO roles (id, service_id, name, description, is_active)
  VALUES (@RoleAdminId, @PrepositionsServiceId, N'admin', N'Catalog administrator for Prepositions service', 1);

DECLARE @AdminUserId UNIQUEIDENTIFIER = (
  SELECT TOP 1 id FROM users WHERE email = @AdminEmail AND COALESCE(is_deleted, 0) = 0
);

IF @AdminUserId IS NOT NULL
BEGIN
  IF NOT EXISTS (SELECT 1 FROM user_roles WHERE user_id = @AdminUserId AND role_id = @RoleUserId)
    INSERT INTO user_roles (id, user_id, role_id) VALUES (NEWID(), @AdminUserId, @RoleUserId);
  IF NOT EXISTS (SELECT 1 FROM user_roles WHERE user_id = @AdminUserId AND role_id = @RoleAdminId)
    INSERT INTO user_roles (id, user_id, role_id) VALUES (NEWID(), @AdminUserId, @RoleAdminId);
  IF NOT EXISTS (SELECT 1 FROM user_services WHERE user_id = @AdminUserId AND service_id = @PrepositionsServiceId)
    INSERT INTO user_services (id, user_id, service_id) VALUES (NEWID(), @AdminUserId, @PrepositionsServiceId);
END
