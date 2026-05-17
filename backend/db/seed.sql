BEGIN;

-- Clean slate for deterministic reseeding
TRUNCATE TABLE
    loaned_item,
    loan,
    requested_catalog,
    "request",
    user_session,
    item,
    catalog,
    category,
    matos_user
RESTART IDENTITY CASCADE;

-- Users across all roles
INSERT INTO matos_user (id, username, name, email, access_level, created_at, updated_at) VALUES
    (1, 'admin_alice', 'Alice Martin', 'alice.martin@clap.fr', 'ADMIN', NOW() - INTERVAL '180 days', NOW() - INTERVAL '1 day'),
    (2, 'clap_marie', 'Marie Dupont', 'marie.dupont@clap.fr', 'CLAP', NOW() - INTERVAL '220 days', NOW() - INTERVAL '1 day'),
    (3, 'clap_lucas', 'Lucas Bernard', 'lucas.bernard@clap.fr', 'CLAP', NOW() - INTERVAL '140 days', NOW() - INTERVAL '3 days'),
    (4, 'manager_nora', 'Nora Petit', 'nora.petit@clap.fr', 'MANAGER', NOW() - INTERVAL '260 days', NOW() - INTERVAL '2 days'),
    (5, 'manager_omar', 'Omar Leroy', 'omar.leroy@clap.fr', 'MANAGER', NOW() - INTERVAL '120 days', NOW() - INTERVAL '4 days'),
    (6, 'user_zoe', 'Zoe Richard', 'zoe.richard@etu.univ.fr', 'USER', NOW() - INTERVAL '90 days', NOW() - INTERVAL '1 day'),
    (7, 'user_hugo', 'Hugo Garcia', 'hugo.garcia@etu.univ.fr', 'USER', NOW() - INTERVAL '95 days', NOW() - INTERVAL '6 days'),
    (8, 'user_lina', 'Lina Moreau', 'lina.moreau@etu.univ.fr', 'USER', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
    (9, 'user_noah', 'Noah Simon', 'noah.simon@etu.univ.fr', 'USER', NOW() - INTERVAL '40 days', NOW() - INTERVAL '2 days'),
    (10, 'visitor_test', 'Visitor Test', 'visitor.test@extern.fr', 'UNAUTHENTICATED', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days');

-- Sessions: active + expired; usable for cookie or bearer-token flows
INSERT INTO user_session (id, token, user_id, expires_at, created_at, updated_at) VALUES
    (1, 'sess_admin_alice_active_01', 1, NOW() + INTERVAL '20 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '1 day'),
    (2, 'sess_clap_marie_active_01', 2, NOW() + INTERVAL '15 days', NOW() - INTERVAL '8 days', NOW() - INTERVAL '1 day'),
    (3, 'sess_clap_lucas_bearer_01', 3, NOW() + INTERVAL '7 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '2 days'),
    (4, 'sess_user_zoe_active_01', 6, NOW() + INTERVAL '12 days', NOW() - INTERVAL '3 days', NOW() - INTERVAL '1 day'),
    (5, 'sess_user_hugo_expired_01', 7, NOW() - INTERVAL '2 days', NOW() - INTERVAL '25 days', NOW() - INTERVAL '2 days');

-- Inventory taxonomy
INSERT INTO category (id, name, description, created_at, updated_at) VALUES
    (1, 'Camera', 'Boitiers et optiques cinema', NOW() - INTERVAL '300 days', NOW() - INTERVAL '20 days'),
    (2, 'Sound', 'Prise de son et accessoires', NOW() - INTERVAL '300 days', NOW() - INTERVAL '20 days'),
    (3, 'Lighting', 'Projecteurs et accessoires lumiere', NOW() - INTERVAL '300 days', NOW() - INTERVAL '20 days'),
    (4, 'Grip', 'Supports, stabilisation, machinerie', NOW() - INTERVAL '300 days', NOW() - INTERVAL '20 days'),
    (5, 'Monitoring', 'Enregistrement et monitoring plateau', NOW() - INTERVAL '300 days', NOW() - INTERVAL '20 days');

INSERT INTO catalog (id, name, description, category_id, image_path, created_at, updated_at) VALUES
    (1, 'Sony A7S III', 'Boitier plein format orienté faible lumière', 1, 'https://example.com/img/a7s3.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '12 days'),
    (2, 'Blackmagic Pocket 6K Pro', 'Boitier Super35 avec ND intégrés', 1, 'https://example.com/img/bmpcc6kpro.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '15 days'),
    (3, 'Zoom H6', 'Enregistreur portable 6 pistes', 2, 'https://example.com/img/zoomh6.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '6 days'),
    (4, 'Rode NTG3 Kit', 'Micro canon + perche + bonnette', 2, 'https://example.com/img/ntg3.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '8 days'),
    (5, 'Aputure 300D II', 'Projecteur LED daylight puissant', 3, 'https://example.com/img/300d2.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '9 days'),
    (6, 'Nanlite PavoTube 30C', 'Tube RGB pour ambiances', 3, 'https://example.com/img/pavotube30c.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '5 days'),
    (7, 'Manfrotto 504HD', 'Trépied vidéo avec tête fluide', 4, 'https://example.com/img/504hd.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '10 days'),
    (8, 'DJI RS 3', 'Stabilisateur 3 axes', 4, 'https://example.com/img/rs3.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '7 days'),
    (9, 'Atomos Ninja V', 'Moniteur enregistreur HDMI', 5, 'https://example.com/img/ninjav.jpg', NOW() - INTERVAL '280 days', NOW() - INTERVAL '3 days');

-- Items: available, maintenance, retired, soft-deleted, varied conditions/deposits
INSERT INTO item (id, name, catalog_id, condition, availability, deposit_cents, deleted_at, created_at, updated_at) VALUES
    (1, 'CAM-A7S-01', 1, 'NEW', 'AVAILABLE', 250000, NULL, NOW() - INTERVAL '260 days', NOW() - INTERVAL '2 days'),
    (2, 'CAM-A7S-02', 1, 'GOOD', 'AVAILABLE', 250000, NULL, NOW() - INTERVAL '250 days', NOW() - INTERVAL '3 days'),
    (3, 'CAM-A7S-03', 1, 'DEGRADED', 'MAINTENANCE', 220000, NULL, NOW() - INTERVAL '240 days', NOW() - INTERVAL '1 day'),
    (4, 'CAM-BMP-01', 2, 'GOOD', 'AVAILABLE', 230000, NULL, NOW() - INTERVAL '220 days', NOW() - INTERVAL '3 days'),
    (5, 'CAM-BMP-02', 2, 'DEGRADED', 'RETIRED', 180000, NULL, NOW() - INTERVAL '210 days', NOW() - INTERVAL '10 days'),
    (6, 'SND-H6-01', 3, 'NEW', 'AVAILABLE', 30000, NULL, NOW() - INTERVAL '200 days', NOW() - INTERVAL '5 days'),
    (7, 'SND-H6-02', 3, 'GOOD', 'AVAILABLE', 30000, NULL, NOW() - INTERVAL '195 days', NOW() - INTERVAL '6 days'),
    (8, 'SND-NTG3-01', 4, 'GOOD', 'AVAILABLE', 45000, NULL, NOW() - INTERVAL '190 days', NOW() - INTERVAL '4 days'),
    (9, 'SND-NTG3-02', 4, 'DEGRADED', 'AVAILABLE', 35000, NULL, NOW() - INTERVAL '185 days', NOW() - INTERVAL '8 days'),
    (10, 'LGT-300D-01', 5, 'GOOD', 'AVAILABLE', 90000, NULL, NOW() - INTERVAL '180 days', NOW() - INTERVAL '3 days'),
    (11, 'LGT-300D-02', 5, 'DEGRADED', 'MAINTENANCE', 70000, NULL, NOW() - INTERVAL '175 days', NOW() - INTERVAL '1 day'),
    (12, 'LGT-TUBE-01', 6, 'NEW', 'AVAILABLE', 20000, NULL, NOW() - INTERVAL '170 days', NOW() - INTERVAL '2 days'),
    (13, 'LGT-TUBE-02', 6, 'GOOD', 'AVAILABLE', 20000, NULL, NOW() - INTERVAL '169 days', NOW() - INTERVAL '2 days'),
    (14, 'LGT-TUBE-03', 6, 'GOOD', 'AVAILABLE', 20000, NULL, NOW() - INTERVAL '168 days', NOW() - INTERVAL '2 days'),
    (15, 'GRP-504-01', 7, 'GOOD', 'AVAILABLE', 15000, NULL, NOW() - INTERVAL '165 days', NOW() - INTERVAL '4 days'),
    (16, 'GRP-504-02', 7, 'GOOD', 'AVAILABLE', 15000, NULL, NOW() - INTERVAL '164 days', NOW() - INTERVAL '4 days'),
    (17, 'GRP-RS3-01', 8, 'NEW', 'AVAILABLE', 80000, NULL, NOW() - INTERVAL '160 days', NOW() - INTERVAL '2 days'),
    (18, 'GRP-RS3-02', 8, 'GOOD', 'AVAILABLE', 80000, NULL, NOW() - INTERVAL '158 days', NOW() - INTERVAL '3 days'),
    (19, 'MON-NINJA-01', 9, 'GOOD', 'AVAILABLE', 60000, NULL, NOW() - INTERVAL '150 days', NOW() - INTERVAL '2 days'),
    (20, 'MON-NINJA-02', 9, 'GOOD', 'AVAILABLE', 60000, NULL, NOW() - INTERVAL '149 days', NOW() - INTERVAL '2 days'),
    (21, 'MON-NINJA-03', 9, 'DEGRADED', 'RETIRED', 40000, NULL, NOW() - INTERVAL '148 days', NOW() - INTERVAL '15 days'),
    (22, 'CAM-A7S-OLD-01', 1, 'DEGRADED', 'RETIRED', 100000, NOW() - INTERVAL '20 days', NOW() - INTERVAL '400 days', NOW() - INTERVAL '20 days'),
    (23, 'SND-H6-OLD-01', 3, 'GOOD', 'AVAILABLE', 20000, NOW() - INTERVAL '3 days', NOW() - INTERVAL '390 days', NOW() - INTERVAL '3 days'),
    (24, 'GRP-RS3-03', 8, 'GOOD', 'AVAILABLE', 75000, NULL, NOW() - INTERVAL '147 days', NOW() - INTERVAL '2 days');

-- Borrowing requests: pending, processed+linked, oversized request, in-flight request
INSERT INTO "request" (id, borrower_id, phone_number, start_date, end_date, reason, processed, created_at, updated_at) VALUES
    (1, 6, '+33612345678', NOW() + INTERVAL '3 days', NOW() + INTERVAL '6 days', 'Court metrage de fin d etudes', FALSE, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    (2, 7, '+33623456789', NOW() - INTERVAL '15 days', NOW() - INTERVAL '12 days', 'Captation interview documentaire', TRUE, NOW() - INTERVAL '18 days', NOW() - INTERVAL '12 days'),
    (3, 8, '+33634567890', NOW() + INTERVAL '7 days', NOW() + INTERVAL '9 days', 'Clip musical multi-cameras', FALSE, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    (4, 9, '+33645678901', NOW() - INTERVAL '2 days', NOW() + INTERVAL '4 days', 'Tournage evenement associatif', TRUE, NOW() - INTERVAL '4 days', NOW() - INTERVAL '2 days');

INSERT INTO requested_catalog (id, request_id, catalog_id, quantity) VALUES
    (1, 1, 1, 1),
    (2, 1, 6, 2),
    (3, 2, 3, 1),
    (4, 2, 7, 1),
    (5, 3, 1, 4),
    (6, 3, 9, 2),
    (7, 4, 2, 1),
    (8, 4, 8, 1);

-- Loans: returned, active with partial return, active linked request, future scheduled, early fully-returned, ended
INSERT INTO loan (
    id, borrower_id, assignee_id, start_date, end_date, total_deposit_cents,
    actual_start_date, actual_return_date, retained_deposit_cents, request_id, comments, created_at, updated_at
) VALUES
    (1, 7, 2, NOW() - INTERVAL '15 days', NOW() - INTERVAL '12 days', 45000,
     NOW() - INTERVAL '15 days', NOW() - INTERVAL '12 days', 5000, 2, 'Retour avec légère usure du trépied', NOW() - INTERVAL '16 days', NOW() - INTERVAL '12 days'),
    (2, 6, 3, NOW() - INTERVAL '1 day', NOW() + INTERVAL '2 days', 310000,
     NOW() - INTERVAL '1 day', NULL, NULL, NULL, 'Tournage en cours, retour partiel déjà effectué', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 hours'),
    (3, 9, 2, NOW() - INTERVAL '2 days', NOW() + INTERVAL '4 days', 310000,
     NOW() - INTERVAL '2 days', NULL, NULL, 4, 'Projet événementiel, matériel principal', NOW() - INTERVAL '4 days', NOW() - INTERVAL '1 day'),
    (4, 8, 2, NOW() + INTERVAL '1 day', NOW() + INTERVAL '3 days', 80000,
     NULL, NULL, NULL, NULL, 'Réservation confirmée, prêt pas encore démarré', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    (5, 6, 3, NOW() - INTERVAL '40 days', NOW() - INTERVAL '35 days', 105000,
     NOW() - INTERVAL '40 days', NOW() - INTERVAL '38 days', 0, NULL, 'Retour anticipé sans dommage', NOW() - INTERVAL '41 days', NOW() - INTERVAL '38 days'),
    (6, 7, 3, NOW() - INTERVAL '5 days', NOW() + INTERVAL '1 day', 110000,
     NOW() - INTERVAL '5 days', NOW() - INTERVAL '1 day', 0, NULL, 'Prêt clôturé avant date de fin prévue', NOW() - INTERVAL '6 days', NOW() - INTERVAL '1 day'),
    (7, 8, 2, NOW() + INTERVAL '2 days', NOW() + INTERVAL '5 days', 250000,
     NULL, NULL, NULL, NULL, 'Réservation en conflit intentionnel pour tests API', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day');

-- Loaned items include: normal return, partial return, early return, future booking, conflict scenario
-- Invariant respected: loaned_item.actual_return_date <= loan.actual_return_date when both are set.
INSERT INTO loaned_item (id, loan_id, item_id, actual_return_date, return_condition) VALUES
    (1, 1, 6, NOW() - INTERVAL '12 days', 'GOOD'),
    (2, 1, 15, NOW() - INTERVAL '12 days', 'DEGRADED'),
    (3, 2, 1, NULL, NULL),
    (4, 2, 19, NOW() - INTERVAL '2 hours', 'GOOD'),
    (5, 3, 4, NULL, NULL),
    (6, 3, 17, NULL, NULL),
    (7, 4, 12, NULL, NULL),
    (8, 4, 20, NULL, NULL),
    (9, 5, 10, NOW() - INTERVAL '39 days', 'GOOD'),
    (10, 5, 16, NOW() - INTERVAL '38 days', 'GOOD'),
    (11, 6, 7, NOW() - INTERVAL '2 days', 'GOOD'),
    (12, 6, 18, NOW() - INTERVAL '1 day', 'GOOD'),
    (13, 7, 4, NULL, NULL),
    (14, 7, 13, NULL, NULL);

-- Keep SERIAL/IDENTITY sequences in sync after explicit IDs
SELECT setval(pg_get_serial_sequence('matos_user', 'id'), COALESCE((SELECT MAX(id) FROM matos_user), 1), true);
SELECT setval(pg_get_serial_sequence('user_session', 'id'), COALESCE((SELECT MAX(id) FROM user_session), 1), true);
SELECT setval(pg_get_serial_sequence('category', 'id'), COALESCE((SELECT MAX(id) FROM category), 1), true);
SELECT setval(pg_get_serial_sequence('catalog', 'id'), COALESCE((SELECT MAX(id) FROM catalog), 1), true);
SELECT setval(pg_get_serial_sequence('item', 'id'), COALESCE((SELECT MAX(id) FROM item), 1), true);
SELECT setval(pg_get_serial_sequence('"request"', 'id'), COALESCE((SELECT MAX(id) FROM "request"), 1), true);
SELECT setval(pg_get_serial_sequence('requested_catalog', 'id'), COALESCE((SELECT MAX(id) FROM requested_catalog), 1), true);
SELECT setval(pg_get_serial_sequence('loan', 'id'), COALESCE((SELECT MAX(id) FROM loan), 1), true);
SELECT setval(pg_get_serial_sequence('loaned_item', 'id'), COALESCE((SELECT MAX(id) FROM loaned_item), 1), true);

COMMIT;
