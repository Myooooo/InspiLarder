-- ============================================
-- 灵感食仓 (InspiLarder) 数据库初始化脚本 v2.0
-- 用途：创建表结构 + 铺底数据
-- 更新：重构表结构，支持完整业务逻辑
-- ============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS inspilarder 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE inspilarder;

-- ============================================
-- 1. 用户表 (users)
-- ============================================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NULL COMMENT '邮箱',
    hashed_password VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin', 'user') DEFAULT 'user' NOT NULL COMMENT '用户角色',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    avatar VARCHAR(255) NULL COMMENT '头像URL',
    nickname VARCHAR(50) NULL COMMENT '昵称',
    last_login DATETIME NULL COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. 储存空间表 (locations) - 支持二级目录
-- ============================================
CREATE TABLE locations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '空间名称',
    icon VARCHAR(10) DEFAULT '📦' COMMENT '图标emoji',
    description VARCHAR(255) NULL COMMENT '描述',
    parent_id INT NULL COMMENT '父级ID（支持二级目录）',
    level INT DEFAULT 1 COMMENT '层级（1=一级，2=二级）',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    user_id INT NOT NULL COMMENT '所属用户',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES locations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_level (user_id, level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='储存空间表';

-- ============================================
-- 3. 食物记录表 (food_items) - 增强版
-- ============================================
CREATE TABLE food_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL COMMENT '食物名称',
    category VARCHAR(50) NOT NULL COMMENT '类别',
    icon VARCHAR(10) NULL COMMENT '图标emoji',
    quantity DECIMAL(10, 2) DEFAULT 1 COMMENT '数量',
    unit VARCHAR(20) DEFAULT '个' COMMENT '单位',
    
    -- 保质期逻辑（支持两种模式）
    expiry_date DATE NULL COMMENT '保质期截止日期',
    shelf_life_days INT NULL COMMENT '保质天数（从添加日期计算）',
    
    -- 位置关联
    location_id INT NULL COMMENT '存放位置ID',
    
    -- AI识别相关
    storage_advice VARCHAR(255) NULL COMMENT '存放建议（AI生成）',
    image_path VARCHAR(500) NULL COMMENT '图片文件路径',
    thumbnail_path VARCHAR(500) NULL COMMENT '缩略图路径',
    ai_metadata JSON NULL COMMENT 'AI识别的原始JSON数据',
    ai_confidence FLOAT NULL COMMENT 'AI识别置信度',
    
    -- 状态管理
    is_opened BOOLEAN DEFAULT FALSE COMMENT '是否已开封',
    opened_at DATETIME NULL COMMENT '开封时间',
    original_shelf_life_days INT NULL COMMENT '开封前原始保质天数（用于计算缩短后的保质期）',
    
    -- 消耗管理
    is_finished BOOLEAN DEFAULT FALSE COMMENT '是否已用完',
    finished_at DATETIME NULL COMMENT '用完时间',
    
    -- 扩展信息
    tags VARCHAR(500) NULL COMMENT '标签（逗号分隔）',
    notes TEXT NULL COMMENT '备注',
    
    -- 语音录入支持
    voice_text VARCHAR(1000) NULL COMMENT '原始语音转文字内容',
    
    -- 所属用户
    user_id INT NOT NULL COMMENT '所属用户',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_expiry_date (expiry_date),
    INDEX idx_location_id (location_id),
    INDEX idx_status (user_id, is_finished, expiry_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食物记录表';

-- ============================================
-- 4. 铺底数据 - 管理员账号
-- ============================================
-- 密码是 'admin123' 的 bcrypt 哈希值
INSERT INTO users (username, email, hashed_password, role, is_active, nickname, created_at)
VALUES ('admin', 'admin@inspilarder.com', '$2b$12$YR7UXfurc9xhb7VnvRvxPe7p3KovpdK37y8v046KmJTndDa6DJLeK', 'admin', TRUE, '管理员', NOW());

-- ============================================
-- 5. 铺底数据 - 默认储存空间（给管理员）
-- ============================================
-- 一级空间：冰箱
INSERT INTO locations (name, icon, description, parent_id, level, sort_order, user_id)
VALUES ('冰箱', '🧊', '家用冰箱', NULL, 1, 1, 1);

SET @fridge_id = LAST_INSERT_ID();

-- 二级空间：冰箱内部区域
INSERT INTO locations (name, icon, description, parent_id, level, sort_order, user_id) VALUES
('冷藏室', '🥬', '冰箱冷藏室', @fridge_id, 2, 1, 1),
('冷冻室', '🧊', '冰箱冷冻室', @fridge_id, 2, 2, 1),
('果蔬盒', '🍎', '冰箱果蔬保鲜盒', @fridge_id, 2, 3, 1);

-- 一级空间：储藏室
INSERT INTO locations (name, icon, description, parent_id, level, sort_order, user_id)
VALUES ('储藏室', '📦', '干货储藏室', NULL, 1, 2, 1);

SET @pantry_id = LAST_INSERT_ID();

-- 二级空间：储藏室内部
INSERT INTO locations (name, icon, description, parent_id, level, sort_order, user_id) VALUES
('干货区', '🌾', '米面粮油存放区', @pantry_id, 2, 1, 1),
('调料区', '🧂', '调味品存放区', @pantry_id, 2, 2, 1);

-- 一级空间：厨房台面
INSERT INTO locations (name, icon, description, parent_id, level, sort_order, user_id)
VALUES ('厨房台面', '🍳', '厨房操作台面', NULL, 1, 3, 1);

SET @counter_id = LAST_INSERT_ID();

-- 二级空间：台面区域
INSERT INTO locations (name, icon, description, parent_id, level, sort_order, user_id) VALUES
('常用调料架', '🧂', '每日使用的调味品', @counter_id, 2, 1, 1),
('水果篮', '🍊', '常温水果存放', @counter_id, 2, 2, 1);

-- ============================================
-- 6. 食谱表 (recipes)
-- ============================================
CREATE TABLE recipes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL COMMENT '食谱名称',
    description TEXT NULL COMMENT '食谱描述',
    ingredients JSON NULL COMMENT '食材列表',
    steps JSON NULL COMMENT '烹饪步骤',
    cooking_time INT NULL COMMENT '烹饪时间（分钟）',
    difficulty VARCHAR(20) NULL COMMENT '难度：简单/中等/困难',
    servings INT DEFAULT 2 COMMENT '份数',
    tags JSON NULL COMMENT '标签列表',
    category VARCHAR(20) NOT NULL COMMENT '分类：quick-快手晚餐, expiring-消耗临期, creative-创意混搭',
    user_id INT NOT NULL COMMENT '所属用户',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食谱表';

-- ============================================
-- 7. 示例食物数据（给管理员）
-- ============================================
-- 获取各个位置的ID
SET @fridge_cold_id = (SELECT id FROM locations WHERE name = '冷藏室' AND user_id = 1);
SET @fridge_frozen_id = (SELECT id FROM locations WHERE name = '冷冻室' AND user_id = 1);
SET @fridge_veggie_id = (SELECT id FROM locations WHERE name = '果蔬盒' AND user_id = 1);
SET @pantry_dry_id = (SELECT id FROM locations WHERE name = '干货区' AND user_id = 1);
SET @counter_condiment_id = (SELECT id FROM locations WHERE name = '常用调料架' AND user_id = 1);

-- 插入示例食物
INSERT INTO food_items (name, category, icon, quantity, unit, expiry_date, shelf_life_days, location_id, storage_advice, is_opened, user_id, created_at) VALUES
('澳洲和牛牛排', 'meat', '🥩', 2, '块', DATE_ADD(CURDATE(), INTERVAL 3 DAY), 3, @fridge_cold_id, '建议冷藏保存，尽快食用', FALSE, 1, NOW()),
('红富士苹果', 'fruit', '🍎', 5, '个', DATE_ADD(CURDATE(), INTERVAL 7 DAY), 7, @fridge_veggie_id, '冷藏可延长保鲜期', FALSE, 1, NOW()),
('鲜牛奶', 'dairy', '🥛', 1, '升', DATE_ADD(CURDATE(), INTERVAL 5 DAY), 5, @fridge_cold_id, '开封后建议3天内喝完', FALSE, 1, NOW()),
('土鸡蛋', 'dairy', '🥚', 12, '个', DATE_ADD(CURDATE(), INTERVAL 14 DAY), 14, @fridge_cold_id, '尖端朝下存放更保鲜', FALSE, 1, NOW()),
('三文鱼刺身', 'seafood', '🐟', 200, '克', DATE_ADD(CURDATE(), INTERVAL 1 DAY), 1, @fridge_cold_id, '建议24小时内食用完毕', FALSE, 1, NOW()),
('有机菠菜', 'vegetable', '🥬', 300, '克', DATE_ADD(CURDATE(), INTERVAL 2 DAY), 2, @fridge_veggie_id, '洗净后沥干水分保存', FALSE, 1, NOW()),
('冷冻虾仁', 'seafood', '🦐', 1, '包', DATE_ADD(CURDATE(), INTERVAL 90 DAY), 90, @fridge_frozen_id, '冷冻保存，解冻后尽快食用', FALSE, 1, NOW()),
('生抽酱油', 'condiment', '🧂', 1, '瓶', DATE_ADD(CURDATE(), INTERVAL 365 DAY), 365, @counter_condiment_id, '避光阴凉处保存，开封后6个月内用完', TRUE, 1, NOW()),
('五常大米', 'grain', '🍚', 5, '千克', DATE_ADD(CURDATE(), INTERVAL 180 DAY), 180, @pantry_dry_id, '密封防潮保存', FALSE, 1, NOW()),
('意大利面', 'grain', '🍝', 2, '包', DATE_ADD(CURDATE(), INTERVAL 365 DAY), 365, @pantry_dry_id, '干燥避光保存', FALSE, 1, NOW());

-- ============================================
-- 8. 示例食谱数据（给管理员）
-- ============================================
INSERT INTO recipes (name, description, ingredients, steps, cooking_time, difficulty, servings, tags, category, user_id) VALUES
('蒜蓉西兰花', '清淡可口的家常蔬菜，蒜香浓郁', 
'["西兰花 500g", "大蒜 4瓣", "盐 适量", "食用油 1勺", "清水 适量"]',
'["步骤1：西兰花切成小朵，用清水浸泡5分钟后洗净，沥干水分", "步骤2：大蒜切末备用", "步骤3：锅中烧开水，加入少许盐和食用油，放入西兰花焯水1分钟至变色", "步骤4：捞出沥干水分备用", "步骤5：热锅下油，小火炒香蒜末", "步骤6：放入西兰花，大火翻炒30秒", "步骤7：加入适量盐调味，翻炒均匀即可出锅"]',
10, '简单', 2, '["快手", "素食", "家常"]', 'quick', 1),

('番茄鸡蛋汤', '酸甜开胃的经典汤品，10分钟搞定',
'["番茄 2个", "鸡蛋 2个", "盐 适量", "香葱 1根", "食用油 1勺", "清水 500ml"]',
'["步骤1：番茄洗净切块，鸡蛋打散 清水 500备用", "步骤2：香葱切末备用", "步骤3：热锅下油，放入番茄块中火翻炒2分钟至出汁", "步骤4：加入500ml清水，大火烧开", "步骤5：水开后转中火，慢慢淋入蛋液，边淋边用筷子搅动", "步骤6：蛋花成形后加入适量盐调味", "步骤7：撒上葱花即可出锅"]',
10, '简单', 2, '["快手", "汤", "家常"]', 'quick', 1),

('土豆烧牛肉', '软糯入味的家常硬菜，消耗临期食材',
'["土豆 2个", "牛肉 300g", "生抽 2勺", "老抽 1勺", "料酒 1勺", "冰糖 3颗", "八角 1个", "桂皮 1小块", "姜片 3片", "蒜 2瓣"]',
'["步骤1：牛肉切块，冷水下锅加料酒和姜片焯水，捞出洗净备用", "步骤2：土豆去皮切块，蒜切片备用", "步骤3：热锅下油，放入冰糖小火炒至融化成焦糖色", "步骤4：放入牛肉块快速翻炒上色", "步骤5：加入生抽、老抽、蒜片、八角、桂皮翻炒均匀", "步骤6：加入没过牛肉的热水，大火烧开后转小火炖40分钟", "步骤7：放入土豆块，继续小火炖15分钟至土豆软烂", "步骤8：大火收汁，加盐调味即可出锅"]',
60, '中等', 4, '["消耗食材", "下饭菜", "硬菜"]', 'expiring', 1);

-- ============================================
-- 完成
-- ============================================
SELECT '数据库初始化完成！已创建管理员账号(admin/admin123)和示例数据' AS message;
