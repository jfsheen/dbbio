from app import db, create_app
import csv
import os
import re
import datetime
from app.models import PlantResource, InsectResource

def init_db():
    """初始化数据库"""
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有数据
        if PlantResource.query.first():
            print("数据库已有数据，跳过导入")
            return
        
        # 从 CSV 文件导入数据
        plants_csv_file_path = os.path.join(os.path.dirname(__file__), 'plants.csv')
        
        if not os.path.exists(plants_csv_file_path):
            print(f"CSV文件不存在: {plants_csv_file_path}")
            # 添加示例数据作为备选
            add_sample_plant_data()
            return
        
        try:
            import_plants_data_from_csv(plants_csv_file_path)
            print("植物数据导入成功")
        except Exception as e:
            print(f"植物导入数据时出错: {str(e)}")
            # 出错时添加示例数据
            add_sample_plant_data()
        
        # 从 CSV 文件导入数据
        insects_csv_file_path = os.path.join(os.path.dirname(__file__), 'insects.csv')
        
        if not os.path.exists(insects_csv_file_path):
            print(f"CSV文件不存在: {insects_csv_file_path}")
            # 添加示例数据作为备选
            add_sample_insect_data()
            return
        
        try:
            import_insects_data_from_csv(insects_csv_file_path)
            print("动物数据导入成功")
        except Exception as e:
            print(f"动物导入数据时出错: {str(e)}")
            # 出错时添加示例数据
            add_sample_insect_data()

def import_plants_data_from_csv(csv_file_path):
    """从CSV文件导入数据到数据库"""
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        # 使用DictReader以便通过列名访问数据
        reader = csv.DictReader(csvfile)
        
        # 计数器
        success_count = 0
        error_count = 0
        
        for row in reader:
            try:
                # 使用from_dict方法创建实例
                plant = PlantResource.from_dict(row)
                # 添加到会话
                db.session.add(plant)
                success_count += 1
                
                # 每100条记录提交一次，避免内存占用过大
                if success_count % 100 == 0:
                    db.session.commit()
                    print(f"已导入 {success_count} 条记录")
                    
            except Exception as e:
                error_count += 1
                print(f"导入第 {success_count + error_count} 行时出错: {str(e)}")
                # 发生错误时回滚当前事务
                db.session.rollback()
        
        # 提交剩余记录
        db.session.commit()
        print(f"数据导入完成: 成功 {success_count} 条, 失败 {error_count} 条")

def add_sample_plant_data():
    """添加示例数据（当CSV文件不存在或导入失败时使用）"""
    sample_data = [
        PlantResource(
            classification="植物界-被子植物门-双子叶植物纲-蔷薇目-蔷薇科-蔷薇属",
            kingdom="Plantae",
            chinese_kingdom_name="植物界",
            family="Rosaceae",
            chinese_family_name="蔷薇科",
            genus="Rosa",
            chinese_genus_name="蔷薇属",
            scientific_name="Rosa chinensis",
            vernacular_name="月季",
            identification_id="ICN001",
            recorded_by="张三",
            record_number="RC2023001",
            event_date="2023-05-10",
            identified_by="李四",
            country="中国",
            state_province="云南省",
            city="昆明市",
            county="呈贡区",
            locality="昆明植物园蔷薇园",
            decimal_latitude=25.1367,
            decimal_longitude=102.7433,
            minimum_elevation_in_meters=1890,
            habitat="栽培于植物园",
            habit="灌木"
        ),
        PlantResource(
            classification="植物界-被子植物门-单子叶植物纲-禾本目-禾本科-竹属",
            kingdom="Plantae",
            chinese_kingdom_name="植物界",
            family="Poaceae",
            chinese_family_name="禾本科",
            genus="Bambusa",
            chinese_genus_name="簕竹属",
            scientific_name="Bambusa multiplex",
            vernacular_name="孝顺竹",
            identification_id="ICN002",
            recorded_by="王五",
            record_number="BM2023001",
            event_date="2023-06-15",
            identified_by="赵六",
            country="中国",
            state_province="广东省",
            city="广州市",
            county="天河区",
            locality="华南植物园竹园",
            decimal_latitude=23.1833,
            decimal_longitude=113.3500,
            minimum_elevation_in_meters=25,
            habitat="栽培于植物园",
            habit="竹类"
        )
    ]
    
    try:
        db.session.bulk_save_objects(sample_data)
        db.session.commit()
        print("示例数据已添加")
    except Exception as e:
        db.session.rollback()
        print(f"添加示例数据时出错: {str(e)}")
        
def import_insects_data_from_csv(csv_file):
    """从CSV文件导入昆虫数据到数据库"""
    # 尝试不同编码读取CSV文件
    encodings = ['utf-8-sig', 'gbk', 'gb2312', 'utf-8']
    rows = []
    
    for encoding in encodings:
        try:
            with open(csv_file, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file)
                rows = list(reader)
            print(f"✅ 成功使用 {encoding} 编码读取CSV文件，共 {len(rows)} 条记录")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise Exception("❌ 无法读取CSV文件，请检查编码格式")
    
    imported_count = 0
    error_count = 0
    
    for i, row in enumerate(rows):
        try:
            # 创建实例
            insect = InsectResource.from_dict(row)
            db.session.add(insect)
            imported_count += 1
            
            # 分批提交
            if imported_count % 100 == 0:
                db.session.commit()
                print(f"📊 已导入 {imported_count} 条记录")
                
        except Exception as e:
            error_count += 1
            print(f"⚠️ 第 {i+1} 行数据导入失败: {str(e)}")
            db.session.rollback()
            
    db.session.commit()
    print(f"🎉 数据导入完成！成功导入 {imported_count}/{len(rows)} 条记录")


def add_sample_insect_data():
    """添加昆虫示例数据"""
    sample_data = [
        InsectResource(
            serial_number="INS001",
            chinese_name="中华蜜蜂",
            phylum="节肢动物门",
            class_="昆虫纲",
            order="膜翅目",
            family_name="蜜蜂科",
            genus_name="蜜蜂属",
            species_name="中华蜜蜂",
            country="中国",
            province="云南省",
            locality="昆明市郊区",
            habitat="山区林地",
            collector="昆虫采集组",
            collection_date=datetime.date(2023, 6, 15)
        ),
        InsectResource(
            serial_number="INS002",
            chinese_name="七星瓢虫",
            phylum="节肢动物门",
            class_="昆虫纲",
            order="鞘翅目",
            family_name="瓢虫科",
            genus_name="瓢虫属",
            species_name="七星瓢虫",
            country="中国",
            province="四川省",
            locality="成都市农田",
            habitat="农田生态系统",
            collector="昆虫采集组",
            collection_date=datetime.date(2023, 7, 20)
        )
    ]
    
    try:
        db.session.bulk_save_objects(sample_data)
        db.session.commit()
        print("昆虫示例数据已添加")
    except Exception as e:
        db.session.rollback()
        print(f"添加昆虫示例数据时出错: {str(e)}")