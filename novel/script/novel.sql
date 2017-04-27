CREATE TABLE novel_detail (
  id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  res_id VARCHAR (255) COMMENT '原始ID',
  name VARCHAR (20) COMMENT '小说名',
  author VARCHAR (20) COMMENT '作者',
  author_href VARCHAR (255) COMMENT '作者详情链接',
  picture VARCHAR (255) COMMENT '图片',
  update_time VARCHAR (30) COMMENT '小说更新时间',
  status VARCHAR (20) COMMENT '状态：连载中、已完结、、、',
  type VARCHAR (20) COMMENT '类型：玄幻、都市、、、',
  type_href VARCHAR (255) COMMENT '类型详情链接',
  source VARCHAR (255) COMMENT '来源',
  description VARCHAR (255) COMMENT '描述',
  latest_chapters VARCHAR (50) COMMENT '最新章节,用于判断是否与数据库数据同步',
  chapters_categore_href VARCHAR (255) COMMENT '章节目录详情链接'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='小说详情表';


CREATE TABLE novel_chapters (
  id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  res_id int (11) COMMENT '原始ID',
  novel_detail_id INT(11) COMMENT '小说ID',
  source VARCHAR (255) COMMENT '来源',
  counts VARCHAR (255) COMMENT '第几章',
  name VARCHAR (255) COMMENT '章节名',
  content TEXT (255) COMMENT '章节内容',
  CONSTRAINT fk_chapters_detail FOREIGN KEY (novel_detail_id) REFERENCES novel_detail (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='小说章节';