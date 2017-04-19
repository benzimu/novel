CREATE TABLE novel (
  id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  res_id VARCHAR (20) COMMENT '原始ID',
  name VARCHAR (20) COMMENT '小说名',
  author VARCHAR (20) COMMENT '作者',
  author_href VARCHAR (255) COMMENT '作者详情链接',
  picture VARCHAR (255) COMMENT '图片',
  update_time VARCHAR (30) COMMENT '小说更新时间',
  status VARCHAR (20) COMMENT '状态：连载中、已完结、、、',
  type VARCHAR (20) COMMENT '类型：玄幻、都市、、、',
  type_href VARCHAR (255) COMMENT '类型详情链接',
  source VARCHAR (20) COMMENT '来源',
  description VARCHAR (255) COMMENT '描述',
  latest_chapters VARCHAR (255) COMMENT '最新章节',
  latest_chapters_href VARCHAR (255) COMMENT '最新章节详情链接'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='小说首页表';