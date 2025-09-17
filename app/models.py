from . import db
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, String, Integer, Float, DateTime, Date
from datetime import datetime, timedelta
import re

class PlantResource(db.Model):
    __tablename__ = 'plant_resources'
    
    # 主键
    id = db.Column(Integer, primary_key=True)
    
    # 分类信息
    classification = db.Column(String(200))
    kingdom = db.Column(String(100))
    chinese_kingdom_name = db.Column(String(100))
    family = db.Column(String(100))
    chinese_family_name = db.Column(String(100))
    genus = db.Column(String(100))
    chinese_genus_name = db.Column(String(100))
    scientific_name = db.Column(String(200))
    vernacular_name = db.Column(String(200))
    identification_id = db.Column(String(100))
    
    # 采集信息
    recorded_by = db.Column(String(100))
    record_number = db.Column(String(50))
    event_date = db.Column(String(50))
    identified_by = db.Column(String(100))
    
    # 地理位置信息
    country = db.Column(String(100))
    state_province = db.Column(String(100))
    city = db.Column(String(100))
    county = db.Column(String(100))
    locality = db.Column(Text)
    decimal_latitude = db.Column(Float)
    decimal_longitude = db.Column(Float)
    
    # 环境信息
    minimum_elevation_in_meters = db.Column(Float)
    habitat = db.Column(Text)
    habit = db.Column(String(100))
    
    # 时间戳
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    
    def to_dict(self):
        """将模型转换为字典"""
        return {
            'id': self.id,
            'classification': self.classification,
            'kingdom': self.kingdom,
            'chineseKingdomName': self.chinese_kingdom_name,  # 注意这里使用驼峰命名
            'family': self.family,
            'chineseFamilyName': self.chinese_family_name,    # 注意这里使用驼峰命名
            'genus': self.genus,
            'chineseGenusName': self.chinese_genus_name,      # 注意这里使用驼峰命名
            'scientificName': self.scientific_name,           # 注意这里使用驼峰命名
            'vernacularName': self.vernacular_name,           # 注意这里使用驼峰命名
            'identificationID': self.identification_id,       # 注意这里使用驼峰命名
            'recordedBy': self.recorded_by,                   # 注意这里使用驼峰命名
            'recordNumber': self.record_number,               # 注意这里使用驼峰命名
            'eventDate': self.event_date,                     # 注意这里使用驼峰命名
            'identifiedBy': self.identified_by,               # 注意这里使用驼峰命名
            'country': self.country,
            'stateProvince': self.state_province,             # 注意这里使用驼峰命名
            'city': self.city,
            'county': self.county,
            'locality': self.locality,
            'decimalLatitude': self.decimal_latitude,         # 注意这里使用驼峰命名
            'decimalLongitude': self.decimal_longitude,       # 注意这里使用驼峰命名
            'minimumElevationInMeters': self.minimum_elevation_in_meters,  # 注意这里使用驼峰命名
            'habitat': self.habitat,
            'habit': self.habit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_json(self):
        """将模型转换为JSON字符串"""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        instance = cls()
        
        # 字段映射：将驼峰命名的键映射到蛇形命名的属性
        field_mapping = {
            'chineseKingdomName': 'chinese_kingdom_name',
            'chineseFamilyName': 'chinese_family_name',
            'chineseGenusName': 'chinese_genus_name',
            'scientificName': 'scientific_name',
            'vernacularName': 'vernacular_name',
            'identificationID': 'identification_id',
            'recordedBy': 'recorded_by',
            'recordNumber': 'record_number',
            'eventDate': 'event_date',
            'identifiedBy': 'identified_by',
            'stateProvince': 'state_province',
            'decimalLatitude': 'decimal_latitude',
            'decimalLongitude': 'decimal_longitude',
            'minimumElevationInMeters': 'minimum_elevation_in_meters'
        }
        
        # 设置属性
        for key, value in data.items():
            # 检查是否需要映射字段名
            field_name = field_mapping.get(key, key)
            
            # 将驼峰命名的键转换为蛇形命名
            if field_name not in field_mapping.values():
                # 如果不是特殊映射的字段，尝试将驼峰转换为蛇形
                field_name = camel_to_snake(key)
            
            if hasattr(instance, field_name):
                # 处理数值字段
                if field_name in ['decimal_latitude', 'decimal_longitude', 'minimum_elevation_in_meters']:
                    try:
                        value = float(value) if value else None
                    except (ValueError, TypeError):
                        value = None
                
                setattr(instance, field_name, value)
        
        return instance 

# 序列号,Leiqun,测序状态,Id,中名,门,门名称,纲,纲名称,目,目名称,中文科名,科名称,属名,种本名,种下名称,
# Cite1,Cite2,资源编码,国家,省,省代码,县,具体地点,经度,纬度,海拔,描述,生境,寄主,图像,记录地址,
# 保存单位,单位代码,采集人,采集时间,采集号,标本号,鉴定人,鉴定时间,标本属性,保藏方式,实物状态,共享方式,获取途径,
# 文献,联系人,单位地址,邮编,电话,Email,项目名称,项目编号,上报时间,取材点,基因编号,基因名称,基因描述,基因别名,测序时间,测序人,课题代码
class InsectResource(db.Model):
    __tablename__ = 'insect_resources'
    
    # 主键
    id = db.Column(Integer, primary_key=True)
    
    # 基本信息
    serial_number = db.Column(String(50), comment='序列号')
    leiqun = db.Column(String(100), comment='Leiqun')
    sequencing_status = db.Column(String(50), comment='测序状态')
    original_id = db.Column(String(50), comment='Id')
    chinese_name = db.Column(String(100), comment='中名')
    
    # 分类信息
    phylum = db.Column(String(50), comment='门')
    phylum_name = db.Column(String(100), comment='门名称')
    class_ = db.Column(String(50), comment='纲')
    class_name = db.Column(String(100), comment='纲名称')
    order = db.Column(String(50), comment='目')
    order_name = db.Column(String(100), comment='目名称')
    chinese_family_name = db.Column(String(100), comment='中文科名')
    family_name = db.Column(String(100), comment='科名称')
    genus_name = db.Column(String(100), comment='属名')
    species_name = db.Column(String(100), comment='种本名')
    infraspecies_name = db.Column(String(100), comment='种下名称')
    
    # 引用信息
    citation1 = db.Column(Text, comment='Cite1')
    citation2 = db.Column(Text, comment='Cite2')
    
    # 资源信息
    resource_code = db.Column(String(50), comment='资源编码')
    country = db.Column(String(50), comment='国家')
    province = db.Column(String(50), comment='省')
    province_code = db.Column(String(50), comment='省代码')
    county = db.Column(String(50), comment='县')
    locality = db.Column(Text, comment='具体地点')
    longitude = db.Column(Float, comment='经度')
    latitude = db.Column(Float, comment='纬度')
    altitude = db.Column(Float, comment='海拔')
    description = db.Column(Text, comment='描述')
    habitat = db.Column(Text, comment='生境')
    host = db.Column(Text, comment='寄主')
    image_url = db.Column(Text, comment='图像')
    record_address = db.Column(Text, comment='记录地址')
    
    # 保存信息
    preservation_institution = db.Column(String(200), comment='保存单位')
    institution_code = db.Column(String(50), comment='单位代码')
    collector = db.Column(String(100), comment='采集人')
    collection_date = db.Column(String(50), comment='采集时间')
    collection_number = db.Column(String(50), comment='采集号')
    specimen_number = db.Column(String(50), comment='标本号')
    identifier = db.Column(String(100), comment='鉴定人')
    identification_date = db.Column(String(50), comment='鉴定时间')
    specimen_attribute = db.Column(String(100), comment='标本属性')
    preservation_method = db.Column(String(100), comment='保藏方式')
    physical_state = db.Column(String(100), comment='实物状态')
    sharing_method = db.Column(String(100), comment='共享方式')
    access_method = db.Column(String(100), comment='获取途径')
    
    # 文献和联系信息
    literature = db.Column(Text, comment='文献')
    contact_person = db.Column(String(100), comment='联系人')
    institution_address = db.Column(Text, comment='单位地址')
    postcode = db.Column(String(20), comment='邮编')
    phone = db.Column(String(50), comment='电话')
    email = db.Column(String(100), comment='Email')
    
    # 项目信息
    project_name = db.Column(String(200), comment='项目名称')
    project_code = db.Column(String(50), comment='项目编号')
    report_date = db.Column(String(50), comment='上报时间')
    sampling_point = db.Column(String(200), comment='取材点')
    
    # 基因信息
    gene_code = db.Column(String(50), comment='基因编号')
    gene_name = db.Column(String(100), comment='基因名称')
    gene_description = db.Column(Text, comment='基因描述')
    gene_alias = db.Column(String(100), comment='基因别名')
    
    # 测序信息
    sequencing_date = db.Column(String(50), comment='测序时间')
    sequencer = db.Column(String(100), comment='测序人')
    project_task_code = db.Column(String(50), comment='课题代码')
    
    # 时间戳
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    
   
    def to_dict(self):
        """将模型转换为字典"""
        return {
            # 基本信息
            'id': self.id,
            'serialNumber': self.serial_number,
            'leiqun': self.leiqun,
            'sequencingStatus': self.sequencing_status,
            'originalId': self.original_id,
            'chineseName': self.chinese_name,
            
            # 分类信息
            'phylum': self.phylum,
            'phylumName': self.phylum_name,
            'class': self.class_,
            'className': self.class_name,
            'order': self.order,
            'orderName': self.order_name,
            'chineseFamilyName': self.chinese_family_name,
            'familyName': self.family_name,
            'genusName': self.genus_name,
            'speciesName': self.species_name,
            'infraspeciesName': self.infraspecies_name,
            
            # 引用信息
            'citation1': self.citation1,
            'citation2': self.citation2,
            
            # 资源信息
            'resourceCode': self.resource_code,
            'country': self.country,
            'province': self.province,
            'provinceCode': self.province_code,
            'county': self.county,
            'locality': self.locality,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'altitude': self.altitude,
            'description': self.description,
            'habitat': self.habitat,
            'host': self.host,
            'imageUrl': self.image_url,
            'recordAddress': self.record_address,
            
            # 保存信息
            'preservationInstitution': self.preservation_institution,
            'institutionCode': self.institution_code,
            'collector': self.collector,
            'collectionDate': self.collection_date.isoformat() if self.collection_date else None,
            'collectionNumber': self.collection_number,
            'specimenNumber': self.specimen_number,
            'identifier': self.identifier,
            'identificationDate': self.identification_date.isoformat() if self.identification_date else None,
            'specimenAttribute': self.specimen_attribute,
            'preservationMethod': self.preservation_method,
            'physicalState': self.physical_state,
            'sharingMethod': self.sharing_method,
            'accessMethod': self.access_method,
            
            # 文献和联系信息
            'literature': self.literature,
            'contactPerson': self.contact_person,
            'institutionAddress': self.institution_address,
            'postcode': self.postcode,
            'phone': self.phone,
            'email': self.email,
            
            # 项目信息
            'projectName': self.project_name,
            'projectCode': self.project_code,
            'reportDate': self.report_date.isoformat() if self.report_date else None,
            'samplingPoint': self.sampling_point,
            
            # 基因信息
            'geneCode': self.gene_code,
            'geneName': self.gene_name,
            'geneDescription': self.gene_description,
            'geneAlias': self.gene_alias,
            
            # 测序信息
            'sequencingDate': self.sequencing_date.isoformat() if self.sequencing_date else None,
            'sequencer': self.sequencer,
            'projectTaskCode': self.project_task_code,
            
            # 时间戳
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_json(self):
        """将模型转换为JSON字符串"""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    @classmethod
    def from_dict(cls, row):
        """从字典创建实例"""
        instance = cls()
        
        # 创建数据字典
        data = {
            # 基本信息
            'serialNumber': row.get('序列号', '').strip(),
            'leiqun': row.get('Leiqun', '').strip(),
            'sequencingStatus': row.get('测序状态', '').strip(),
            'originalId': row.get('Id', '').strip(),
            'chineseName': row.get('中名', '').strip(),
            
            # 分类信息
            'phylum': row.get('门', '').strip(),
            'phylumName': row.get('门名称', '').strip(),
            'class': row.get('纲', '').strip(),
            'className': row.get('纲名称', '').strip(),
            'order': row.get('目', '').strip(),
            'orderName': row.get('目名称', '').strip(),
            'chineseFamilyName': row.get('中文科名', '').strip(),
            'familyName': row.get('科名称', '').strip(),
            'genusName': row.get('属名', '').strip(),
            'speciesName': row.get('种本名', '').strip(),
            'infraspeciesName': row.get('种下名称', '').strip(),
            
            # 引用信息
            'citation1': row.get('Cite1', '').strip(),
            'citation2': row.get('Cite2', '').strip(),
            
            # 资源信息
            'resourceCode': row.get('资源编码', '').strip(),
            'country': row.get('国家', '').strip(),
            'province': row.get('省', '').strip(),
            'provinceCode': row.get('省代码', '').strip(),
            'county': row.get('县', '').strip(),
            'locality': row.get('具体地点', '').strip(),
            'longitude': parse_float(row.get('经度')),
            'latitude': parse_float(row.get('纬度')),
            'altitude': parse_float(row.get('海拔')),
            'description': row.get('描述', '').strip(),
            'habitat': row.get('生境', '').strip(),
            'host': row.get('寄主', '').strip(),
            'imageUrl': row.get('图像', '').strip(),
            'recordAddress': row.get('记录地址', '').strip(),
            
            # 保存信息
            'preservationInstitution': row.get('保存单位', '').strip(),
            'institutionCode': row.get('单位代码', '').strip(),
            'collector': row.get('采集人', '').strip(),
            'collectionDate': row.get('采集时间', '').strip(),
            'collectionNumber': row.get('采集号', '').strip(),
            'specimenNumber': row.get('标本号', '').strip(),
            'identifier': row.get('鉴定人', '').strip(),
            'identificationDate': row.get('鉴定时间', '').strip(),
            'specimenAttribute': row.get('标本属性', '').strip(),
            'preservationMethod': row.get('保藏方式', '').strip(),
            'physicalState': row.get('实物状态', '').strip(),
            'sharingMethod': row.get('共享方式', '').strip(),
            'accessMethod': row.get('获取途径', '').strip(),
            
            # 文献和联系信息
            'literature': row.get('文献', '').strip(),
            'contactPerson': row.get('联系人', '').strip(),
            'institutionAddress': row.get('单位地址', '').strip(),
            'postcode': row.get('邮编', '').strip(),
            'phone': row.get('电话', '').strip(),
            'email': row.get('Email', '').strip(),
            
            # 项目信息
            'projectName': row.get('项目名称', '').strip(),
            'projectCode': row.get('项目编号', '').strip(),
            'reportDate': row.get('上报时间', '').strip(),
            'samplingPoint': row.get('取材点', '').strip(),
            
            # 基因信息
            'geneCode': row.get('基因编号', '').strip(),
            'geneName': row.get('基因名称', '').strip(),
            'geneDescription': row.get('基因描述', '').strip(),
            'geneAlias': row.get('基因别名', '').strip(),
            
            # 测序信息
            'sequencingDate': row.get('测序时间', '').strip(),
            'sequencer': row.get('测序人', '').strip(),
            'projectTaskCode': row.get('课题代码', '').strip()
        }
        
        # 处理日期字段
        for date_field in ['collectionDate', 'identificationDate', 'reportDate', 'sequencingDate']:
            if data[date_field]:
                data[date_field] = parse_date(data[date_field])

        # 处理图像Url
        if data['imageUrl']:
            data['imageUrl'] = '|'.join([os.path.join('images', url) for url in re.split(r'\s*、\s*', data['imageUrl']) if url.strip()])

        # 设置属性
        for key, value in data.items():
            field_name = camel_to_snake(key)
            if hasattr(instance, field_name):
                setattr(instance, field_name, value)

        return instance
    

def camel_to_snake(name):
    """将驼峰命名转换为蛇形命名"""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
def parse_date(date_str):
    """解析多种日期格式"""
    if not date_str or str(date_str).strip() == '':
        return None
    
    date_str = str(date_str).strip()
    date_formats = [
        '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
        '%Y-%m', '%Y/%m', '%Y.%m',
        '%Y年%m月%d日', '%Y年%m月', '%Y年',
        '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # 如果所有格式都失败，尝试只提取年份
    try:
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            year = int(year_match.group(1))
            return datetime(year, 1, 1).date()
    except (ValueError, IndexError):
        pass
    
    return None
    
def parse_float(value):
    """解析浮点数"""
    if not value or str(value).strip() == '':
        return None
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None

def get_beijing_time():
    """将当前UTC时间转换为北京时间"""
    current_utc_time = 'Mon, 15 Sep 2025 10:26:04 GMT'
    
    try:
        utc_time = datetime.strptime(current_utc_time, '%a, %d %b %Y %H:%M:%S GMT')
        # UTC转北京时间（UTC+8）
        beijing_time = utc_time + datetime.timedelta(hours=8)
        return beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return "无效的时间格式"